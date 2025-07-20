#!/usr/bin/env python3
"""
Script to create the ML model for deployment
Run this script to generate the model/expense_predictor.joblib file
"""

import os
import sys
from expense_predictor_model import create_sample_model

def main():
    """Create the ML model for deployment"""
    print("🚀 Creating ML model for ExpenseTracker Pro...")
    print("=" * 50)
    
    # Create model directory
    model_dir = "model"
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)
        print(f"📁 Created directory: {model_dir}")
    
    # Create the model
    print("🤖 Training ML model with sample data...")
    success = create_sample_model()
    
    if success:
        print("✅ Model created successfully!")
        print(f"📦 Model saved to: {model_dir}/expense_predictor.joblib")
        print("\n🎉 Ready for deployment!")
        print("You can now upload your app to Streamlit Cloud.")
    else:
        print("❌ Failed to create model!")
        sys.exit(1)

if __name__ == "__main__":
    main()
