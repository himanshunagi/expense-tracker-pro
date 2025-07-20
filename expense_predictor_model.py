import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
import os
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class ExpensePredictor:
    def __init__(self):
        self.model = RandomForestRegressor(
            n_estimators=100,
            random_state=42,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2
        )
        self.category_encoder = LabelEncoder()
        self.feature_columns = [
            'month', 'weekday', 'is_weekend', 'quarter', 'day_of_month',
            'is_month_start', 'is_month_end', 'category_encoded'
        ]
        self.is_fitted = False
        
    def create_features(self, df):
        """Create features for the model"""
        df = df.copy()
        
        # Ensure date is datetime
        df['date'] = pd.to_datetime(df['date'])
        
        # Time-based features
        df['month'] = df['date'].dt.month
        df['weekday'] = df['date'].dt.weekday
        df['is_weekend'] = df['weekday'].isin([5, 6]).astype(int)
        df['quarter'] = df['date'].dt.quarter
        df['day_of_month'] = df['date'].dt.day
        df['is_month_start'] = (df['day_of_month'] <= 7).astype(int)
        df['is_month_end'] = (df['day_of_month'] >= 24).astype(int)
        
        # Category encoding
        if not self.is_fitted:
            df['category_encoded'] = self.category_encoder.fit_transform(df['category'])
        else:
            # Handle new categories during prediction
            known_categories = set(self.category_encoder.classes_)
            df['category_encoded'] = df['category'].apply(
                lambda x: self.category_encoder.transform([x])[0] if x in known_categories else -1
            )
        
        return df
    
    def prepare_data(self, data):
        """Prepare data for training"""
        df = pd.DataFrame(data)
        
        if df.empty:
            return None, None
        
        # Handle different data formats
        if 'total_expense' in df.columns and 'total_income' in df.columns:
            # Create separate rows for income and expense
            expense_data = df[df['total_expense'] > 0].copy()
            income_data = df[df['total_income'] > 0].copy()
            
            if not expense_data.empty:
                expense_data['amount'] = expense_data['total_expense']
                expense_data['transaction_type'] = 'expense'
            
            if not income_data.empty:
                income_data['amount'] = income_data['total_income']
                income_data['transaction_type'] = 'income'
            
            # Combine
            all_data = []
            if not expense_data.empty:
                all_data.append(expense_data[['date', 'category', 'amount', 'transaction_type']])
            if not income_data.empty:
                all_data.append(income_data[['date', 'category', 'amount', 'transaction_type']])
            
            if all_data:
                df = pd.concat(all_data, ignore_index=True)
            else:
                return None, None
        
        # Ensure required columns exist
        required_cols = ['date', 'category', 'amount']
        if not all(col in df.columns for col in required_cols):
            return None, None
        
        # Remove zero amounts
        df = df[df['amount'] > 0]
        
        if df.empty:
            return None, None
        
        # Create features
        df = self.create_features(df)
        
        # Prepare X and y
        X = df[self.feature_columns]
        y = df['amount']
        
        return X, y
    
    def train(self, data):
        """Train the model"""
        X, y = self.prepare_data(data)
        
        if X is None or y is None:
            return False, "No valid data for training"
        
        if len(X) < 10:
            return False, "Insufficient data for training (minimum 10 samples required)"
        
        try:
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Train model
            self.model.fit(X_train, y_train)
            self.is_fitted = True
            
            # Calculate metrics
            y_pred = self.model.predict(X_test)
            mae = mean_absolute_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            return True, f"Model trained successfully. MAE: {mae:.2f}, R²: {r2:.3f}"
            
        except Exception as e:
            return False, f"Training failed: {str(e)}"
    
    def predict_category(self, category, transaction_type='expense', target_month=None):
        """Predict amount for a specific category"""
        if not self.is_fitted:
            return 0, 0
        
        if target_month is None:
            target_month = datetime.now().month
        
        try:
            # Check if category exists
            if category not in self.category_encoder.classes_:
                return 0, 0
            
            # Create prediction features
            prediction_data = pd.DataFrame({
                'date': [datetime.now()],
                'category': [category],
                'amount': [100],  # Dummy value
                'transaction_type': [transaction_type]
            })
            
            # Create features
            prediction_data = self.create_features(prediction_data)
            prediction_data['month'] = target_month
            
            # Make prediction
            X_pred = prediction_data[self.feature_columns]
            prediction = self.model.predict(X_pred)[0]
            
            # Calculate confidence based on feature importance
            feature_importance = self.model.feature_importances_
            confidence = min(95, max(50, np.mean(feature_importance) * 100))
            
            return max(0, prediction), confidence
            
        except Exception as e:
            return 0, 0
    
    def predict_next_month(self, categories):
        """Predict amounts for multiple categories for next month"""
        if not self.is_fitted:
            return []
        
        next_month = datetime.now().month + 1 if datetime.now().month < 12 else 1
        predictions = []
        
        for category in categories:
            # Predict for both expense and income
            expense_pred, expense_conf = self.predict_category(category, 'expense', next_month)
            income_pred, income_conf = self.predict_category(category, 'income', next_month)
            
            if expense_pred > 0 or income_pred > 0:
                predictions.append({
                    'category': category,
                    'predicted_expense': expense_pred,
                    'predicted_income': income_pred,
                    'expense_confidence': expense_conf,
                    'income_confidence': income_conf,
                    'transaction_type': 'expense' if expense_pred > income_pred else 'income'
                })
        
        return predictions
    
    def save_model(self, filepath):
        """Save the trained model"""
        if not self.is_fitted:
            return False, "Model not trained yet"
        
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Save model and encoders
            model_data = {
                'model': self.model,
                'category_encoder': self.category_encoder,
                'feature_columns': self.feature_columns,
                'is_fitted': self.is_fitted
            }
            
            joblib.dump(model_data, filepath)
            return True, f"Model saved to {filepath}"
            
        except Exception as e:
            return False, f"Failed to save model: {str(e)}"
    
    def load_model(self, filepath):
        """Load a trained model"""
        try:
            if not os.path.exists(filepath):
                return False, "Model file not found"
            
            model_data = joblib.load(filepath)
            
            self.model = model_data['model']
            self.category_encoder = model_data['category_encoder']
            self.feature_columns = model_data['feature_columns']
            self.is_fitted = model_data['is_fitted']
            
            return True, "Model loaded successfully"
            
        except Exception as e:
            return False, f"Failed to load model: {str(e)}"

def create_sample_model():
    """Create a sample model with dummy data for deployment"""
    predictor = ExpensePredictor()
    
    # Sample data for training
    sample_data = []
    categories = [
        "Salary", "Family Support", "Loan Taken", "Debt Payment", "Food", 
        "Miscellaneous Spending", "Cashback", "Subscription", "Petrol", 
        "Recharge", "Other Income", "Festival Expense", "Outing with Friends",
        "Charity", "Face & Hair Product", "Utility", "Groceries", "Cloths",
        "Entertainment", "Bank charge", "Travel", "Saving/Investment"
    ]
    
    # Generate sample data for the last 6 months
    start_date = datetime.now() - timedelta(days=180)
    
    for i in range(500):  # 500 sample transactions
        date = start_date + timedelta(days=np.random.randint(0, 180))
        category = np.random.choice(categories)
        
        # Generate realistic amounts based on category
        if category in ["Salary", "Family Support"]:
            amount = np.random.uniform(20000, 80000)
            transaction_type = "income"
        elif category in ["Debt Payment", "Saving/Investment"]:
            amount = np.random.uniform(5000, 25000)
            transaction_type = "expense"
        elif category in ["Food", "Groceries", "Utility"]:
            amount = np.random.uniform(100, 3000)
            transaction_type = "expense"
        else:
            amount = np.random.uniform(50, 5000)
            transaction_type = "expense"
        
        sample_data.append({
            'date': date.strftime('%Y-%m-%d'),
            'category': category,
            'total_expense': amount if transaction_type == 'expense' else 0,
            'total_income': amount if transaction_type == 'income' else 0,
            'transaction_type': transaction_type
        })
    
    # Train model
    success, message = predictor.train(sample_data)
    
    if success:
        # Save model
        model_dir = "model"
        os.makedirs(model_dir, exist_ok=True)
        save_success, save_message = predictor.save_model(f"{model_dir}/expense_predictor.joblib")
        
        if save_success:
            print(f"Sample model created and saved successfully!")
            print(f"Training: {message}")
            print(f"Saving: {save_message}")
            return True
        else:
            print(f"Failed to save model: {save_message}")
            return False
    else:
        print(f"Failed to train model: {message}")
        return False

if __name__ == "__main__":
    # Create sample model for deployment
    create_sample_model()
