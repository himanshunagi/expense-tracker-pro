import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import calendar
import os
import json

# Import the ML model class
try:
    from expense_predictor_model import ExpensePredictor
    MODEL_AVAILABLE = True
except ImportError:
    MODEL_AVAILABLE = False
    st.warning("⚠️ ML model not available. Please ensure expense_predictor_model.py exists.")

# Page configuration
st.set_page_config(
    page_title="ExpenseTracker Pro - Smart Personal Finance Manager",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state
if "expenses" not in st.session_state:
    st.session_state.expenses = []
if "cash_expenses" not in st.session_state:
    st.session_state.cash_expenses = []
if "fixed_expenses" not in st.session_state:
    st.session_state.fixed_expenses = []
if "selected_period" not in st.session_state:
    st.session_state.selected_period = "Month"
if "period_offset" not in st.session_state:
    st.session_state.period_offset = 0
if "active_tab" not in st.session_state:
    st.session_state.active_tab = None
if "data_storage" not in st.session_state:
    st.session_state.data_storage = {
        "bank_expenses": {},
        "cash_expenses": {},
        "fixed_expenses": []
    }

# Categories
CATEGORIES = [
    "Salary", "Cashback", "Other Income", "Family Support", "Loan Taken", "Debt Payment", "Food", "Miscellaneous Spending",
    "Subscription", "Petrol", "Recharge", "Festival Expense",
    "Outing with Friends", "Charity", "Body care", "Utility", "Groceries", "Clothes",
    "Entertainment", "Bank charge", "Travel", "Saving/Investment", "Medical Expenses", "Self Care"
]

# Load ML Model
@st.cache_resource
def load_ml_model():
    """Load the ML model for predictions"""
    if not MODEL_AVAILABLE:
        return None
    
    model = ExpensePredictor()
    model_path = "model/expense_predictor.joblib"
    
    if os.path.exists(model_path):
        success, message = model.load_model(model_path)
        if success:
            return model
    
    # If model doesn't exist, create a sample one
    st.info("Creating ML model for predictions...")
    try:
        from expense_predictor_model import create_sample_model
        if create_sample_model():
            success, message = model.load_model(model_path)
            if success:
                return model
    except Exception as e:
        st.error(f"Error creating model: {e}")
    
    return None

# Utility functions
def set_active_tab(tab_name):
    st.session_state.active_tab = tab_name

def get_period_data():
    """Get data for the current period and offset"""
    today = datetime.today()
    
    if st.session_state.selected_period == "Week":
        start_date = today - timedelta(days=today.weekday()) + timedelta(weeks=st.session_state.period_offset)
        end_date = start_date + timedelta(days=6)
    elif st.session_state.selected_period == "Month":
        if st.session_state.period_offset == 0:
            start_date = today.replace(day=1)
            end_date = today
        else:
            target_month = today.month + st.session_state.period_offset
            target_year = today.year
            while target_month > 12:
                target_month -= 12
                target_year += 1
            while target_month < 1:
                target_month += 12
                target_year -= 1
            start_date = datetime(target_year, target_month, 1)
            last_day = calendar.monthrange(target_year, target_month)[1]
            end_date = datetime(target_year, target_month, last_day)
    else:  # Year
        target_year = today.year + st.session_state.period_offset
        start_date = datetime(target_year, 1, 1)
        end_date = datetime(target_year, 12, 31)
    
    # Calculate data from session state
    total_income = 0
    total_expense = 0
    
    # Online Transaction expenses (previously Bank expenses)
    for date_str, expenses in st.session_state.data_storage["bank_expenses"].items():
        try:
            expense_date = datetime.strptime(date_str, "%Y-%m-%d")
            if start_date <= expense_date <= end_date:
                total_income += sum(float(exp.get("income", 0)) for exp in expenses)
                total_expense += sum(float(exp.get("expense", 0)) for exp in expenses)
        except (ValueError, TypeError):
            continue
    
    # Cash Transaction expenses (previously Cash expenses)
    for date_str, expenses in st.session_state.data_storage["cash_expenses"].items():
        try:
            expense_date = datetime.strptime(date_str, "%Y-%m-%d")
            if start_date <= expense_date <= end_date:
                total_income += sum(float(exp.get("income", 0)) for exp in expenses)
                total_expense += sum(float(exp.get("expense", 0)) for exp in expenses)
        except (ValueError, TypeError):
            continue
    
    # Fixed expenses
    for expense in st.session_state.data_storage["fixed_expenses"]:
        try:
            exp_date = datetime.strptime(expense["date"], "%Y-%m-%d")
            if start_date <= exp_date <= end_date:
                total_income += float(expense.get("income", 0))
                total_expense += float(expense.get("expense", 0))
        except (ValueError, TypeError):
            continue
    
    return {
        "income": total_income,
        "expense": total_expense,
        "savings": total_income - total_expense,
        "bank_income": total_income * 0.8,
        "bank_expense": total_expense * 0.85,
        "cash_income": total_income * 0.2,
        "cash_expense": total_expense * 0.15
    }

# Enhanced Mobile-Friendly CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

* {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

/* Mobile-First Responsive Design */
.stApp {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    color: #333;
}

.block-container {
    max-width: 100% !important;
    padding: 1rem !important;
}

/* Mobile Header */
.header {
    text-align: center;
    margin-bottom: 1.5rem;
    color: white;
    padding: 1rem 0;
}

.header h1 {
    font-size: 1.8rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    color: white;
}

.header p {
    font-size: 1rem;
    opacity: 0.9;
    color: white;
}

/* Mobile Cards */
.balance-card {
    background: white;
    border-radius: 12px;
    padding: 1rem;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    margin-bottom: 1rem;
    transition: all 0.3s ease;
}

.balance-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(0,0,0,0.15);
}

.balance-card h3 {
    color: #667eea;
    margin-bottom: 0.75rem;
    font-size: 1rem;
    font-weight: 600;
}

.balance-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
    padding: 0.25rem 0;
    border-bottom: 1px solid #f0f0f0;
}

.balance-row:last-child {
    border-bottom: none;
    font-weight: bold;
    margin-top: 0.5rem;
    padding-top: 0.75rem;
    border-top: 2px solid #667eea;
}

.balance-label {
    font-weight: 500;
    color: #555;
    font-size: 0.9rem;
}

.balance-amount {
    font-weight: bold;
    font-size: 0.9rem;
}

/* Mobile Buttons */
.stButton > button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    color: white !important;
    border: none !important;
    padding: 0.75rem 1rem !important;
    border-radius: 8px !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    cursor: pointer !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3) !important;
    width: 100% !important;
    min-height: 44px !important;
}

.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4) !important;
}


/* Mobile Navigation */
.tab-nav {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    gap: 0.5rem;
    margin-bottom: 1rem;
}

.tab-nav button {
    padding: 0.75rem 0.5rem !important;
    font-size: 12px !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
}

/* Mobile Tables */
.stDataFrame {
    font-size: 12px !important;
    overflow-x: auto !important;
}

.stDataFrame table {
    min-width: 100% !important;
}

/* Mobile Charts */
.chart-container {
    background: white;
    border-radius: 12px;
    padding: 1rem;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    margin: 1rem 0;
}

/* Mobile Responsive Grid */
.mobile-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 1rem;
}

@media (min-width: 768px) {
    .mobile-grid {
        grid-template-columns: repeat(2, 1fr);
    }
    
    .header h1 {
        font-size: 2.5rem;
    }
    
    .balance-card {
        padding: 1.5rem;
    }
    
    .tab-nav {
        grid-template-columns: repeat(5, 1fr);
    }
}

@media (min-width: 1024px) {
    .mobile-grid {
        grid-template-columns: repeat(3, 1fr);
    }
    
    .block-container {
        max-width: 1200px !important;
        margin: 0 auto !important;
        padding: 2rem 1rem !important;
    }
}

/* Color classes */
.income { color: #2ecc71; }
.expense { color: #e74c3c; }
.balance { color: #667eea; }
.pending { color: #f39c12; }

/* Success/Error messages */
.stSuccess {
    background: #d4edda !important;
    border: 1px solid #c3e6cb !important;
    color: #155724 !important;
    border-radius: 8px !important;
    padding: 1rem !important;
    margin: 1rem 0 !important;
}

.stError {
    background: #f8d7da !important;
    border: 1px solid #f5c6cb !important;
    color: #721c24 !important;
    border-radius: 8px !important;
    padding: 1rem !important;
    margin: 1rem 0 !important;
}

.stWarning {
    background: #fff3cd !important;
    border: 1px solid #ffeeba !important;
    color: #856404 !important;
    border-radius: 8px !important;
    padding: 1rem !important;
    margin: 1rem 0 !important;
}

/* Hide Streamlit elements */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
.stDeployButton { display: none; }
header { visibility: hidden; }


/* Mobile touch targets */
@media (max-width: 768px) {
    .stButton > button {
        min-height: 48px !important;
        font-size: 16px !important;
    }
    
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div,
    .stDateInput > div > div > input {
        min-height: 48px !important;
        font-size: 16px !important;
    }
}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="header">
    <h1>💰 ExpenseTracker Pro</h1>
    <p>Smart Personal Finance Manager</p>
</div>
""", unsafe_allow_html=True)

# Tab Navigation
st.markdown('<div class="tab-nav">', unsafe_allow_html=True)
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    if st.button("💳 Online", key="tab_bank", use_container_width=True):
        set_active_tab("bank")
        st.rerun()

with col2:
    if st.button("💵 Cash", key="tab_cash", use_container_width=True):
        set_active_tab("cash")
        st.rerun()

with col3:
    if st.button("🔄 Fixed", key="tab_fixed", use_container_width=True):
        set_active_tab("fixed")
        st.rerun()

with col4:
    if st.button("📊 Analytics", key="tab_analytics", use_container_width=True):
        set_active_tab("analytics")
        st.rerun()

with col5:
    if st.button("🤖 AI", key="tab_ai", use_container_width=True):
        set_active_tab("ai")
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# Home button
if st.session_state.active_tab:
    if st.button("🏠 Home", key="home_btn"):
        set_active_tab(None)
        st.rerun()

# Main Content
def show_dashboard():
    """Main dashboard"""
    period_data = get_period_data()
    
    # Summary cards
    st.markdown('<div class="mobile-grid">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="balance-card">
            <h3>💳 Online Transaction</h3>
            <div class="balance-row">
                <span class="balance-label">Income:</span>
                <span class="balance-amount income">₹{period_data['bank_income']:,.0f}</span>
            </div>
            <div class="balance-row">
                <span class="balance-label">Expense:</span>
                <span class="balance-amount expense">₹{period_data['bank_expense']:,.0f}</span>
            </div>
            <div class="balance-row">
                <span class="balance-label">Balance:</span>
                <span class="balance-amount balance">₹{period_data['bank_income'] - period_data['bank_expense']:,.0f}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="balance-card">
            <h3>💵 Cash Transaction</h3>
            <div class="balance-row">
                <span class="balance-label">Income:</span>
                <span class="balance-amount income">₹{period_data['cash_income']:,.0f}</span>
            </div>
            <div class="balance-row">
                <span class="balance-label">Expense:</span>
                <span class="balance-amount expense">₹{period_data['cash_expense']:,.0f}</span>
            </div>
            <div class="balance-row">
                <span class="balance-label">Balance:</span>
                <span class="balance-amount balance">₹{period_data['cash_income'] - period_data['cash_expense']:,.0f}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="balance-card">
            <h3>📊 Total</h3>
            <div class="balance-row">
                <span class="balance-label">Income:</span>
                <span class="balance-amount income">₹{period_data['income']:,.0f}</span>
            </div>
            <div class="balance-row">
                <span class="balance-label">Expense:</span>
                <span class="balance-amount expense">₹{period_data['expense']:,.0f}</span>
            </div>
            <div class="balance-row">
                <span class="balance-label">Savings:</span>
                <span class="balance-amount balance">₹{period_data['savings']:,.0f}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Period selection
    st.markdown("### 📅 Period Selection")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Week", key="week_select"):
            st.session_state.selected_period = "Week"
            st.session_state.period_offset = 0
            st.rerun()
    
    with col2:
        if st.button("Month", key="month_select"):
            st.session_state.selected_period = "Month"
            st.session_state.period_offset = 0
            st.rerun()
    
    with col3:
        if st.button("Year", key="year_select"):
            st.session_state.selected_period = "Year"
            st.session_state.period_offset = 0
            st.rerun()
    
    # Period navigation
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.button("◀ Previous", key="prev_period"):
            st.session_state.period_offset -= 1
            st.rerun()
    
    with col2:
        period_text = f"{st.session_state.selected_period}"
        if st.session_state.period_offset != 0:
            period_text += f" ({st.session_state.period_offset:+d})"
        st.markdown(f"<div style='text-align: center; padding: 0.5rem; background: rgba(255,255,255,0.2); border-radius: 8px; color: white;'>{period_text}</div>", unsafe_allow_html=True)
    
    with col3:
        if st.button("Next ▶", key="next_period"):
            st.session_state.period_offset += 1
            st.rerun()

def show_bank_expenses():
    """Online Transaction expenses management"""
    st.markdown("### 💳 Online Transaction Expenses")
    
    # Date selection
    selected_date = st.date_input("Select Date", datetime.today())
    date_str = selected_date.strftime("%Y-%m-%d")
    
    # Get existing expenses for the date
    if date_str in st.session_state.data_storage["bank_expenses"]:
        current_expenses = st.session_state.data_storage["bank_expenses"][date_str]
    else:
        current_expenses = []
    
    # Add empty row if needed
    if not current_expenses or (current_expenses and current_expenses[-1].get("description", "")):
        current_expenses.append({
            "description": "",
            "income": 0.0,
            "expense": 0.0,
            "category": ""
        })
    
    # Form for adding/editing expenses
    with st.form("bank_expenses_form"):
        st.markdown("#### Add/Edit Online Transactions")
        
        new_expenses = []
        for i, exp in enumerate(current_expenses):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                desc = st.text_input(f"Description {i+1}", value=exp.get("description", ""), key=f"bank_desc_{i}")
            
            with col2:
                income = st.number_input(f"Income {i+1}", value=float(exp.get("income", 0)), min_value=0.0, key=f"bank_income_{i}")
            
            with col3:
                expense = st.number_input(f"Expense {i+1}", value=float(exp.get("expense", 0)), min_value=0.0, key=f"bank_expense_{i}")
            
            with col4:
                category_index = 0
                current_category = exp.get("category", "")
                
                # Create options with placeholder
                category_options = ["Select Category"] + CATEGORIES
                
                # Set index based on current category
                if current_category and current_category in CATEGORIES:
                    category_index = CATEGORIES.index(current_category) + 1
                
                category = st.selectbox(
                    f"Category {i+1}", 
                    category_options, 
                    index=category_index, 
                    key=f"bank_category_{i}"
                )
                
                # Convert back to actual category (empty if placeholder selected)
                if category == "Select Category":
                    category = ""
            
            if desc or income > 0 or expense > 0:
                new_expenses.append({
                    "description": desc,
                    "income": income,
                    "expense": expense,
                    "category": category
                })
        
        if st.form_submit_button("💾 Save Online Transactions"):
            valid_expenses = [exp for exp in new_expenses if exp["description"] and exp["category"]]
            
            if valid_expenses:
                st.session_state.data_storage["bank_expenses"][date_str] = valid_expenses
                st.success(f"✅ Saved {len(valid_expenses)} online transactions!")
                st.rerun()
            else:
                st.warning("⚠️ Please fill in description and category for all transactions.")
    
    # Quick actions
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🗑️ Clear All", key="clear_bank"):
            st.session_state.data_storage["bank_expenses"][date_str] = []
            st.rerun()
    
    with col2:
        if st.button("➕ Add Row", key="add_bank_row"):
            if date_str not in st.session_state.data_storage["bank_expenses"]:
                st.session_state.data_storage["bank_expenses"][date_str] = []
            st.session_state.data_storage["bank_expenses"][date_str].append({
                "description": "",
                "income": 0.0,
                "expense": 0.0,
                "category": ""
            })
            st.rerun()

def show_cash_expenses():
    """Cash Transaction expenses management"""
    st.markdown("### 💵 Cash Transaction Expenses")
    
    # Date selection
    selected_date = st.date_input("Select Date", datetime.today(), key="cash_date")
    date_str = selected_date.strftime("%Y-%m-%d")
    
    # Get existing expenses for the date
    if date_str in st.session_state.data_storage["cash_expenses"]:
        current_expenses = st.session_state.data_storage["cash_expenses"][date_str]
    else:
        current_expenses = []
    
    # Add empty row if needed
    if not current_expenses or (current_expenses and current_expenses[-1].get("description", "")):
        current_expenses.append({
            "description": "",
            "income": 0.0,
            "expense": 0.0,
            "category": ""
        })
    
    # Form for adding/editing expenses
    with st.form("cash_expenses_form"):
        st.markdown("#### Add/Edit Cash Transactions")
        
        new_expenses = []
        for i, exp in enumerate(current_expenses):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                desc = st.text_input(f"Description {i+1}", value=exp.get("description", ""), key=f"cash_desc_{i}")
            
            with col2:
                income = st.number_input(f"Income {i+1}", value=float(exp.get("income", 0)), min_value=0.0, key=f"cash_income_{i}")
            
            with col3:
                expense = st.number_input(f"Expense {i+1}", value=float(exp.get("expense", 0)), min_value=0.0, key=f"cash_expense_{i}")
            
            with col4:
                category_index = 0
                current_category = exp.get("category", "")
                
                # Create options with placeholder
                category_options = ["Select Category"] + CATEGORIES
                
                # Set index based on current category
                if current_category and current_category in CATEGORIES:
                    category_index = CATEGORIES.index(current_category) + 1
                
                category = st.selectbox(
                    f"Category {i+1}", 
                    category_options, 
                    index=category_index, 
                    key=f"cash_category_{i}"
                )
                
                # Convert back to actual category (empty if placeholder selected)
                if category == "Select Category":
                    category = ""
            
            if desc or income > 0 or expense > 0:
                new_expenses.append({
                    "description": desc,
                    "income": income,
                    "expense": expense,
                    "category": category
                })
        
        if st.form_submit_button("💾 Save Cash Transactions"):
            valid_expenses = [exp for exp in new_expenses if exp["description"] and exp["category"]]
            
            if valid_expenses:
                st.session_state.data_storage["cash_expenses"][date_str] = valid_expenses
                st.success(f"✅ Saved {len(valid_expenses)} cash transactions!")
                st.rerun()
            else:
                st.warning("⚠️ Please fill in description and category for all transactions.")
    
    # Quick actions
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🗑️ Clear All", key="clear_cash"):
            st.session_state.data_storage["cash_expenses"][date_str] = []
            st.rerun()
    
    with col2:
        if st.button("➕ Add Row", key="add_cash_row"):
            if date_str not in st.session_state.data_storage["cash_expenses"]:
                st.session_state.data_storage["cash_expenses"][date_str] = []
            st.session_state.data_storage["cash_expenses"][date_str].append({
                "description": "",
                "income": 0.0,
                "expense": 0.0,
                "category": ""
            })
            st.rerun()

def show_fixed_expenses():
    """Fixed expenses management"""
    st.markdown("### 🔄 Fixed Expenses")
    
    # Add new fixed expense
    with st.form("fixed_expense_form"):
        st.markdown("#### Add New Fixed Expense")
        
        col1, col2 = st.columns(2)
        
        with col1:
            description = st.text_input("Description")
            start_date = st.date_input("Start Date", datetime.today())
            end_date = st.date_input("End Date", datetime.today() + timedelta(days=365))
        
        with col2:
            income = st.number_input("Income Amount", min_value=0.0)
            expense = st.number_input("Expense Amount", min_value=0.0)
            category = st.selectbox("Category", CATEGORIES)
        
        if st.form_submit_button("💾 Save Fixed Expense"):
            if description and category and (income > 0 or expense > 0):
                new_fixed = {
                    "description": description,
                    "date": start_date.strftime("%Y-%m-%d"),
                    "end_date": end_date.strftime("%Y-%m-%d"),
                    "income": income,
                    "expense": expense,
                    "category": category
                }
                
                st.session_state.data_storage["fixed_expenses"].append(new_fixed)
                st.success("✅ Fixed expense added successfully!")
                st.rerun()
            else:
                st.warning("⚠️ Please fill in all required fields.")
    
    # Display existing fixed expenses
    if st.session_state.data_storage["fixed_expenses"]:
        st.markdown("#### Your Fixed Expenses")
        
        for i, expense in enumerate(st.session_state.data_storage["fixed_expenses"]):
            with st.expander(f"{expense['description']} - {expense['category']}"):
                st.write(f"**Date Range:** {expense['date']} to {expense['end_date']}")
                st.write(f"**Income:** ₹{expense['income']:,.0f}")
                st.write(f"**Expense:** ₹{expense['expense']:,.0f}")
                
                if st.button(f"🗑️ Delete", key=f"delete_fixed_{i}"):
                    st.session_state.data_storage["fixed_expenses"].pop(i)
                    st.rerun()
    else:
        st.info("No fixed expenses added yet.")

def show_analytics():
    """Analytics dashboard"""
    st.markdown("### 📊 Analytics")
    
    # Date range selection
    col1, col2 = st.columns(2)
    
    with col1:
        start_date = st.date_input("Start Date", datetime.today() - timedelta(days=30))
    
    with col2:
        end_date = st.date_input("End Date", datetime.today())
    
    # Collect data for the period
    period_data = []
    
    # Online Transaction expenses (previously Bank expenses)
    for date_str, expenses in st.session_state.data_storage["bank_expenses"].items():
        try:
            expense_date = datetime.strptime(date_str, "%Y-%m-%d")
            if start_date <= expense_date.date() <= end_date:
                for exp in expenses:
                    if exp.get("category"):  # Only include if category exists
                        period_data.append({
                            "date": date_str,
                            "category": exp["category"],
                            "income": float(exp.get("income", 0)),
                            "expense": float(exp.get("expense", 0)),
                            "type": "Online Transaction"
                        })
        except (ValueError, TypeError):
            continue
    
    # Cash Transaction expenses (previously Cash expenses)
    for date_str, expenses in st.session_state.data_storage["cash_expenses"].items():
        try:
            expense_date = datetime.strptime(date_str, "%Y-%m-%d")
            if start_date <= expense_date.date() <= end_date:
                for exp in expenses:
                    if exp.get("category"):  # Only include if category exists
                        period_data.append({
                            "date": date_str,
                            "category": exp["category"],
                            "income": float(exp.get("income", 0)),
                            "expense": float(exp.get("expense", 0)),
                            "type": "Cash Transaction"
                        })
        except (ValueError, TypeError):
            continue
    
    if period_data:
        df = pd.DataFrame(period_data)
        
        # Summary metrics
        total_income = df["income"].sum()
        total_expense = df["expense"].sum()
        net_balance = total_income - total_expense
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Income", f"₹{total_income:,.0f}")
        
        with col2:
            st.metric("Total Expense", f"₹{total_expense:,.0f}")
        
        with col3:
            st.metric("Net Balance", f"₹{net_balance:,.0f}")
        
        # Category breakdown
        if total_expense > 0:
            expense_df = df[df["expense"] > 0].groupby("category")["expense"].sum().reset_index()
            expense_df = expense_df.sort_values("expense", ascending=False)
            
            if not expense_df.empty:
                fig = px.pie(expense_df, values="expense", names="category", 
                            title="Expense Breakdown by Category")
                st.plotly_chart(fig, use_container_width=True)
        
        # Monthly trend
        df["date"] = pd.to_datetime(df["date"])
        df["month"] = df["date"].dt.to_period("M")
        monthly_df = df.groupby("month").agg({
            "income": "sum",
            "expense": "sum"
        }).reset_index()
        monthly_df["month"] = monthly_df["month"].astype(str)
        
        if not monthly_df.empty:
            fig = go.Figure()
            fig.add_trace(go.Bar(x=monthly_df["month"], y=monthly_df["income"], name="Income", marker_color="#2ecc71"))
            fig.add_trace(go.Bar(x=monthly_df["month"], y=monthly_df["expense"], name="Expense", marker_color="#e74c3c"))
            fig.update_layout(title="Monthly Income vs Expense Trend", barmode="group")
            st.plotly_chart(fig, use_container_width=True)
        
    else:
        st.info("No data available for the selected period.")

def show_ai_predictions():
    """AI predictions using ML model"""
    st.markdown("### 🤖 AI Predictions")
    
    # Load ML model
    model = load_ml_model()
    
    if model is None:
        st.error("❌ ML model not available. Please ensure the model file exists.")
        if st.button("🔄 Try to Create Model"):
            try:
                from expense_predictor_model import create_sample_model
                with st.spinner("Creating sample model..."):
                    if create_sample_model():
                        st.success("✅ Sample model created! Please refresh the page.")
                        st.rerun()
                    else:
                        st.error("❌ Failed to create sample model.")
            except Exception as e:
                st.error(f"Error: {e}")
        return
    
    # Prepare training data from current storage
    training_data = []
    
    # Online Transaction expenses (previously Bank expenses)
    for date_str, expenses in st.session_state.data_storage["bank_expenses"].items():
        for exp in expenses:
            if exp.get("category"):
                training_data.append({
                    "date": date_str,
                    "category": exp["category"],
                    "total_expense": float(exp.get("expense", 0)),
                    "total_income": float(exp.get("income", 0)),
                    "transaction_type": "expense" if exp.get("expense", 0) > 0 else "income"
                })
    
    # Cash Transaction expenses (previously Cash expenses)
    for date_str, expenses in st.session_state.data_storage["cash_expenses"].items():
        for exp in expenses:
            if exp.get("category"):
                training_data.append({
                    "date": date_str,
                    "category": exp["category"],
                    "total_expense": float(exp.get("expense", 0)),
                    "total_income": float(exp.get("income", 0)),
                    "transaction_type": "expense" if exp.get("expense", 0) > 0 else "income"
                })
    
    # Fixed expenses
    for exp in st.session_state.data_storage["fixed_expenses"]:
        training_data.append({
            "date": exp["date"],
            "category": exp["category"],
            "total_expense": float(exp.get("expense", 0)),
            "total_income": float(exp.get("income", 0)),
            "transaction_type": "expense" if exp.get("expense", 0) > 0 else "income"
        })
    
    if st.button("🚀 Generate Predictions"):
        if not training_data:
            st.warning("⚠️ No data available for predictions. Please add some transactions first.")
            return
        
        with st.spinner("Training model and generating predictions..."):
            try:
                # Retrain model with current data
                success, message = model.train(training_data)
                
                if success:
                    st.success(f"✅ {message}")
                    
                    # Generate predictions for all categories
                    unique_categories = list(set(exp["category"] for exp in training_data if exp.get("category")))
                    predictions = model.predict_next_month(unique_categories)
                    
                    if predictions:
                        # Display predictions
                        st.markdown("#### 📈 Next Month Predictions")
                        
                        pred_df = pd.DataFrame(predictions)
                        
                        # Expense predictions
                        expense_preds = pred_df[pred_df["predicted_expense"] > 0]
                        if not expense_preds.empty:
                            st.markdown("**💸 Predicted Expenses**")
                            for _, pred in expense_preds.iterrows():
                                st.write(f"**{pred['category']}:** ₹{pred['predicted_expense']:,.0f} (Confidence: {pred['expense_confidence']:.1f}%)")
                        
                        # Income predictions
                        income_preds = pred_df[pred_df["predicted_income"] > 0]
                        if not income_preds.empty:
                            st.markdown("**💰 Predicted Income**")
                            for _, pred in income_preds.iterrows():
                                st.write(f"**{pred['category']}:** ₹{pred['predicted_income']:,.0f} (Confidence: {pred['income_confidence']:.1f}%)")
                        
                        # Summary
                        total_pred_expense = pred_df["predicted_expense"].sum()
                        total_pred_income = pred_df["predicted_income"].sum()
                        pred_savings = total_pred_income - total_pred_expense
                        
                        st.markdown("#### 📊 Prediction Summary")
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Predicted Income", f"₹{total_pred_income:,.0f}")
                        
                        with col2:
                            st.metric("Predicted Expense", f"₹{total_pred_expense:,.0f}")
                        
                        with col3:
                            st.metric("Predicted Savings", f"₹{pred_savings:,.0f}")
                        
                        # Visualization
                        if total_pred_expense > 0 and not expense_preds.empty:
                            fig = px.pie(expense_preds, values="predicted_expense", names="category", 
                                        title="Predicted Expense Distribution")
                            st.plotly_chart(fig, use_container_width=True)
                    
                    else:
                        st.info("No predictions generated. Model may need more training data.")
                else:
                    st.error(f"❌ {message}")
            except Exception as e:
                st.error(f"❌ Error during prediction: {str(e)}")

# Main app logic
if st.session_state.active_tab is None:
    show_dashboard()
elif st.session_state.active_tab == "bank":
    show_bank_expenses()
elif st.session_state.active_tab == "cash":
    show_cash_expenses()
elif st.session_state.active_tab == "fixed":
    show_fixed_expenses()
elif st.session_state.active_tab == "analytics":
    show_analytics()
elif st.session_state.active_tab == "ai":
    show_ai_predictions()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: white; padding: 1rem; background: rgba(255,255,255,0.1); border-radius: 8px; margin-top: 2rem;">
    <p>💰 ExpenseTracker Pro - Your Smart Finance Manager</p>
    <p style="font-size: 0.9rem; opacity: 0.8;">Track • Analyze • Predict • Save</p>
</div>
""", unsafe_allow_html=True)