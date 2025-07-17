import streamlit as st
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
import numpy as np

# Set page configuration
st.set_page_config(
    page_title="ExpenseTracker Pro - Smart Personal Finance Manager",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Session state initialization
if "selected_period" not in st.session_state:
    st.session_state.selected_period = "Month"
if "period_offset" not in st.session_state:
    st.session_state.period_offset = 0
if "active_tab" not in st.session_state:
    st.session_state.active_tab = None
if "expenses_data" not in st.session_state:
    st.session_state.expenses_data = {}
if "cash_expenses_data" not in st.session_state:
    st.session_state.cash_expenses_data = {}
if "fixed_expenses" not in st.session_state:
    st.session_state.fixed_expenses = []
if "demo_data_loaded" not in st.session_state:
    st.session_state.demo_data_loaded = False

# Categories
categories = ["Salary", "Family Support", "Loan Taken", "Debt Payment", "Food", "Miscellaneous Spending",
              "Cashback", "Subscription", "Petrol", "Recharge", "Other Income", "Festival Expense",
              "Outing with Friends", "Charity", "Face & Hair Product", "Utility", "Groceries", "Cloths",
              "Entertainment", "Bank charge", "Travel", "Saving/Investment", "Reversed Income"]

def load_demo_data():
    """Load demo data when the app first starts"""
    if not st.session_state.demo_data_loaded:
        # Sample bank expenses
        st.session_state.expenses_data = {
            "2024-12-01": [
                {"description": "Monthly Salary", "income": 75000, "expense": 0, "category": "Salary"},
                {"description": "Rent Payment", "income": 0, "expense": 25000, "category": "Utility"},
                {"description": "Groceries", "income": 0, "expense": 3500, "category": "Groceries"}
            ],
            "2024-12-02": [
                {"description": "Lunch", "income": 0, "expense": 450, "category": "Food"},
                {"description": "Petrol", "income": 0, "expense": 2000, "category": "Petrol"}
            ],
            "2024-12-03": [
                {"description": "Netflix", "income": 0, "expense": 649, "category": "Subscription"},
                {"description": "Freelance Work", "income": 15000, "expense": 0, "category": "Other Income"}
            ]
        }
        
        # Sample cash expenses
        st.session_state.cash_expenses_data = {
            "2024-12-01": [
                {"description": "Street Food", "income": 0, "expense": 120, "category": "Food"},
                {"description": "Auto Rickshaw", "income": 0, "expense": 80, "category": "Travel"}
            ],
            "2024-12-02": [
                {"description": "Tea/Coffee", "income": 0, "expense": 40, "category": "Food"},
                {"description": "Parking", "income": 0, "expense": 20, "category": "Miscellaneous Spending"}
            ]
        }
        
        # Sample fixed expenses
        st.session_state.fixed_expenses = [
            {"description": "Monthly Salary", "income": 75000, "expense": 0, "category": "Salary", "date": "2024-12-25", "end_date": "2025-12-31"},
            {"description": "House Rent", "income": 0, "expense": 25000, "category": "Utility", "date": "2024-12-01", "end_date": "2025-12-31"},
            {"description": "Internet Bill", "income": 0, "expense": 999, "category": "Utility", "date": "2024-12-05", "end_date": "2025-12-31"},
            {"description": "Netflix Subscription", "income": 0, "expense": 649, "category": "Subscription", "date": "2024-12-15", "end_date": "2025-12-31"}
        ]
        
        st.session_state.demo_data_loaded = True

def set_period(period):
    st.session_state.selected_period = period
    st.session_state.period_offset = 0

def set_active_tab(tab_name):
    st.session_state.active_tab = tab_name

def get_period_data():
    """Calculate data for the current period"""
    load_demo_data()
    
    # Calculate totals from stored data
    total_bank_income = 0
    total_bank_expense = 0
    total_cash_income = 0
    total_cash_expense = 0
    
    # Sum up all bank transactions
    for date, transactions in st.session_state.expenses_data.items():
        for transaction in transactions:
            total_bank_income += transaction.get("income", 0)
            total_bank_expense += transaction.get("expense", 0)
    
    # Sum up all cash transactions
    for date, transactions in st.session_state.cash_expenses_data.items():
        for transaction in transactions:
            total_cash_income += transaction.get("income", 0)
            total_cash_expense += transaction.get("expense", 0)
    
    total_income = total_bank_income + total_cash_income
    total_expense = total_bank_expense + total_cash_expense
    
    return {
        "income": total_income,
        "expense": total_expense,
        "savings": total_income - total_expense,
        "bank_income": total_bank_income,
        "bank_expense": total_bank_expense,
        "cash_income": total_cash_income,
        "cash_expense": total_cash_expense
    }

def get_upcoming_data():
    """Get upcoming bills and income"""
    load_demo_data()
    
    upcoming_bills = [
        {"description": "House Rent", "date": "2024-12-25", "expense": 25000},
        {"description": "Internet Bill", "date": "2024-12-28", "expense": 999},
        {"description": "Netflix", "date": "2024-12-30", "expense": 649}
    ]
    
    upcoming_income = [
        {"description": "Monthly Salary", "date": "2024-12-25", "income": 75000},
        {"description": "Freelance Project", "date": "2024-12-28", "income": 15000}
    ]
    
    return upcoming_bills, upcoming_income

# Enhanced CSS Styling
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Segoe+UI:wght@300;400;500;600;700&display=swap');

* {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

/* Main App Background */
.stApp {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    color: #333;
}

.block-container {
    max-width: 1200px !important;
    margin: 0 auto !important;
    padding: 2rem 1rem 2rem 1rem !important;
}

/* Header Styling */
.header {
    text-align: center;
    margin-bottom: 2rem;
    color: white;
    padding: 2rem 0 1rem 0;
}

.header h1 {
    font-size: 2.5rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    color: white;
}

.header p {
    font-size: 1.2rem;
    opacity: 0.9;
    color: white;
}

/* Balance Cards Section */
.balance-section {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1.5rem;
    margin-bottom: 2rem;
}

.balance-card {
    background: white;
    border-radius: 15px;
    padding: 1.5rem;
    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    transition: all 0.3s ease;
}

.balance-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 25px rgba(0,0,0,0.15);
}

.balance-card h3 {
    color: #667eea;
    margin-bottom: 1rem;
    font-size: 1.2rem;
    font-weight: 600;
}

.balance-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.75rem;
    padding: 0.5rem 0;
    border-bottom: 1px solid #f0f0f0;
}

.balance-row:last-child {
    border-bottom: none;
    font-weight: bold;
    margin-top: 0.75rem;
    padding-top: 1rem;
    border-top: 2px solid #667eea;
}

.balance-label {
    font-weight: 600;
    color: #555;
}

.balance-amount {
    font-weight: bold;
}

.income { color: #2ecc71; }
.expense { color: #e74c3c; }
.balance { color: #667eea; }
.pending { color: #f39c12; }

/* Enhanced Buttons */
.stButton > button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    color: white !important;
    border: none !important;
    padding: 0.75rem 2rem !important;
    border-radius: 10px !important;
    font-size: 16px !important;
    font-weight: 600 !important;
    cursor: pointer !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4) !important;
}

/* Demo Notice */
.demo-notice {
    background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);
    color: white;
    padding: 1rem;
    border-radius: 10px;
    margin-bottom: 2rem;
    text-align: center;
    font-weight: 600;
}

/* Form Styling */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stSelectbox > div > div,
.stDateInput > div > div > input {
    background: white !important;
    border: 2px solid #e1e5e9 !important;
    border-radius: 10px !important;
    padding: 0.75rem !important;
    font-size: 16px !important;
    color: #333 !important;
}

.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus,
.stSelectbox > div > div:focus-within,
.stDateInput > div > div > input:focus {
    outline: none !important;
    border-color: #667eea !important;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
}

/* Animation */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

.animate-fade-in {
    animation: fadeIn 0.6s ease-out;
}

/* Responsive */
@media (max-width: 768px) {
    .balance-section { grid-template-columns: 1fr; }
    .header h1 { font-size: 2rem; }
}

/* Hide Streamlit elements */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
.stDeployButton { display: none; }
</style>
""", unsafe_allow_html=True)

# Header Section
st.markdown("""
<div class="header animate-fade-in">
    <h1>💰 ExpenseTracker Pro</h1>
    <p>Your Complete Personal Finance Manager - Live Demo</p>
</div>
""", unsafe_allow_html=True)

# Demo Notice
st.markdown("""
<div class="demo-notice animate-fade-in">
    🚀 <strong>Live Demo:</strong> This is a fully functional demo! Add your own expenses and see them reflected in real-time. Your data is stored in this session only.
</div>
""", unsafe_allow_html=True)

# Tab Navigation
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    if st.button("💳 Bank Expenses", key="tab_add_expense", use_container_width=True):
        set_active_tab("add_expense")
        st.rerun()

with col2:
    if st.button("💵 Cash Expenses", key="tab_cash_expenses", use_container_width=True):
        set_active_tab("cash_expenses")
        st.rerun()

with col3:
    if st.button("🔄 Fixed Costs", key="tab_fixed_costs", use_container_width=True):
        set_active_tab("fixed_costs")
        st.rerun()

with col4:
    if st.button("📊 Analytics", key="tab_analytics", use_container_width=True):
        set_active_tab("analytics")
        st.rerun()

with col5:
    if st.button("🤖 Predictions", key="tab_prediction", use_container_width=True):
        set_active_tab("prediction")
        st.rerun()

# Home button
if st.session_state.active_tab is not None:
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🏠 Back to Home", key="back_home", use_container_width=True):
            set_active_tab(None)
            st.rerun()

st.markdown("---")

# Dashboard
def show_dashboard():
    """Display the main dashboard"""
    load_demo_data()
    period_data = get_period_data()
    
    income = period_data.get("income", 0)
    expense = period_data.get("expense", 0)
    savings = period_data.get("savings", 0)
    bank_income = period_data.get("bank_income", 0)
    bank_expense = period_data.get("bank_expense", 0)
    cash_income = period_data.get("cash_income", 0)
    cash_expense = period_data.get("cash_expense", 0)
    
    bank_balance = bank_income - bank_expense
    cash_balance = cash_income - cash_expense
    
    # Balance Cards
    st.markdown('<div class="balance-section">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="balance-card animate-fade-in">
            <h3>💳 Bank Account</h3>
            <div class="balance-row">
                <span class="balance-label">Total Income:</span>
                <span class="balance-amount income">₹{bank_income:,.0f}</span>
            </div>
            <div class="balance-row">
                <span class="balance-label">Total Expenses:</span>
                <span class="balance-amount expense">₹{bank_expense:,.0f}</span>
            </div>
            <div class="balance-row">
                <span class="balance-label">Current Balance:</span>
                <span class="balance-amount balance">₹{bank_balance:,.0f}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="balance-card animate-fade-in">
            <h3>💵 Cash</h3>
            <div class="balance-row">
                <span class="balance-label">Total Income:</span>
                <span class="balance-amount income">₹{cash_income:,.0f}</span>
            </div>
            <div class="balance-row">
                <span class="balance-label">Total Expenses:</span>
                <span class="balance-amount expense">₹{cash_expense:,.0f}</span>
            </div>
            <div class="balance-row">
                <span class="balance-label">Current Balance:</span>
                <span class="balance-amount balance">₹{cash_balance:,.0f}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        next_income = income * 1.05
        next_expense = expense * 1.02
        next_balance = next_income - next_expense
        
        st.markdown(f"""
        <div class="balance-card animate-fade-in">
            <h3>📊 Next Month Projection</h3>
            <div class="balance-row">
                <span class="balance-label">Expected Income:</span>
                <span class="balance-amount income">₹{next_income:,.0f}</span>
            </div>
            <div class="balance-row">
                <span class="balance-label">Expected Expenses:</span>
                <span class="balance-amount expense">₹{next_expense:,.0f}</span>
            </div>
            <div class="balance-row">
                <span class="balance-label">Projected Balance:</span>
                <span class="balance-amount pending">₹{next_balance:,.0f}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Simplified Bank Expenses Tab
def show_bank_expenses():
    st.markdown("## 💳 Bank Expenses")
    st.markdown("Add your bank transactions here. Data is stored in this session only.")
    
    with st.form("bank_expense_form"):
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            description = st.text_input("Description", placeholder="Enter description...")
        with col2:
            income = st.number_input("Income (₹)", min_value=0.0, step=100.0)
        with col3:
            expense = st.number_input("Expense (₹)", min_value=0.0, step=100.0)
        with col4:
            category = st.selectbox("Category", categories)
        
        date = st.date_input("Date", datetime.today())
        
        if st.form_submit_button("💾 Add Transaction"):
            if description and category and (income > 0 or expense > 0):
                date_str = date.strftime("%Y-%m-%d")
                if date_str not in st.session_state.expenses_data:
                    st.session_state.expenses_data[date_str] = []
                
                st.session_state.expenses_data[date_str].append({
                    "description": description,
                    "income": income,
                    "expense": expense,
                    "category": category
                })
                st.success("✅ Transaction added successfully!")
                st.rerun()
            else:
                st.error("Please fill all fields and enter an amount!")

# Simplified Cash Expenses Tab
def show_cash_expenses():
    st.markdown("## 💵 Cash Expenses")
    st.markdown("Add your cash transactions here. Data is stored in this session only.")
    
    with st.form("cash_expense_form"):
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            description = st.text_input("Description", placeholder="Enter description...")
        with col2:
            income = st.number_input("Income (₹)", min_value=0.0, step=10.0)
        with col3:
            expense = st.number_input("Expense (₹)", min_value=0.0, step=10.0)
        with col4:
            category = st.selectbox("Category", categories)
        
        date = st.date_input("Date", datetime.today())
        
        if st.form_submit_button("💾 Add Cash Transaction"):
            if description and category and (income > 0 or expense > 0):
                date_str = date.strftime("%Y-%m-%d")
                if date_str not in st.session_state.cash_expenses_data:
                    st.session_state.cash_expenses_data[date_str] = []
                
                st.session_state.cash_expenses_data[date_str].append({
                    "description": description,
                    "income": income,
                    "expense": expense,
                    "category": category
                })
                st.success("✅ Cash transaction added successfully!")
                st.rerun()
            else:
                st.error("Please fill all fields and enter an amount!")

# Simplified Analytics Tab
def show_analytics():
    st.markdown("## 📊 Analytics")
    load_demo_data()
    
    # Combine all data
    all_data = []
    for date, transactions in st.session_state.expenses_data.items():
        for transaction in transactions:
            all_data.append({**transaction, "type": "Bank", "date": date})
    
    for date, transactions in st.session_state.cash_expenses_data.items():
        for transaction in transactions:
            all_data.append({**transaction, "type": "Cash", "date": date})
    
    if all_data:
        df = pd.DataFrame(all_data)
        
        # Summary
        total_income = df['income'].sum()
        total_expense = df['expense'].sum()
        net_balance = total_income - total_expense
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Income", f"₹{total_income:,.0f}")
        with col2:
            st.metric("Total Expense", f"₹{total_expense:,.0f}")
        with col3:
            st.metric("Net Balance", f"₹{net_balance:,.0f}")
        
        # Category wise chart
        category_data = df.groupby('category').agg({
            'income': 'sum',
            'expense': 'sum'
        }).reset_index()
        
        if not category_data.empty:
            fig = px.bar(category_data, x='category', y=['income', 'expense'], 
                        title='Category-wise Income vs Expense')
            st.plotly_chart(fig, use_container_width=True)
        
        # Transaction table
        st.subheader("All Transactions")
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No data available. Add some transactions to see analytics!")

# Display content based on active tab
if st.session_state.active_tab is None:
    show_dashboard()
elif st.session_state.active_tab == "add_expense":
    show_bank_expenses()
elif st.session_state.active_tab == "cash_expenses":
    show_cash_expenses()
elif st.session_state.active_tab == "fixed_costs":
    st.markdown("## 🔄 Fixed Costs")
    st.info("Fixed costs feature - Add recurring expenses and income here!")
    st.markdown("This feature allows you to set up recurring monthly expenses like rent, salary, subscriptions, etc.")
elif st.session_state.active_tab == "analytics":
    show_analytics()
elif st.session_state.active_tab == "prediction":
    st.markdown("## 🤖 Predictions")
    st.info("AI-powered expense predictions coming soon!")
    st.markdown("This feature will analyze your spending patterns to predict future expenses.")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: white; padding: 2rem;">
    <p>💰 ExpenseTracker Pro - Your Complete Finance Manager</p>
    <p style="opacity: 0.8;">Live Demo | Add data and see real-time updates</p>
</div>
""", unsafe_allow_html=True)