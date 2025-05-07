import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import bcrypt
from sklearn.linear_model import LinearRegression
import numpy as np

# Initialize user authentication database
def init_user_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        username TEXT PRIMARY KEY,
                        password TEXT)''')
    conn.commit()
    conn.close()

# Register new users with duplicate check
def register_user(username, password):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("SELECT username FROM users WHERE username=?", (username,))
    existing_user = cursor.fetchone()

    if existing_user:
        conn.close()
        return "❌ Username already exists! Choose a different one."

    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
    conn.commit()
    conn.close()
    return "✅ User registered successfully!"

# Verify user login
def authenticate_user(username, password):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE username=?", (username,))
    result = cursor.fetchone()
    conn.close()

    if result and bcrypt.checkpw(password.encode(), result[0]):
        return True
    return False

# Initialize finance database
def init_finance_db():
    conn = sqlite3.connect("finance.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (
                        id INTEGER PRIMARY KEY,
                        username TEXT,
                        type TEXT,
                        amount REAL,
                        category TEXT,
                        date TEXT)''')
    conn.commit()
    conn.close()

# Add transactions
def add_transaction(username, transaction_type, amount, category, date):
    conn = sqlite3.connect("finance.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO transactions (username, type, amount, category, date) VALUES (?, ?, ?, ?, ?)",
                   (username, transaction_type, amount, category, date))
    conn.commit()
    conn.close()

# Fetch transactions for the logged-in user
def fetch_transactions(username):
    conn = sqlite3.connect("finance.db")
    df = pd.read_sql_query("SELECT * FROM transactions WHERE username=?", conn, params=(username,))
    conn.close()
    return df

# Bar Chart - Expense Breakdown
def visualize_expenses(username):
    df = fetch_transactions(username)
    expense_df = df[df["type"] == "Expense"]
    category_totals = expense_df.groupby("category")["amount"].sum()

    plt.figure(figsize=(8, 5))
    category_totals.plot(kind="bar", color="skyblue")
    plt.xlabel("Category")
    plt.ylabel("Amount Spent")
    plt.title("Expense Breakdown")
    plt.xticks(rotation=45)
    plt.grid()
    st.pyplot(plt)

# Pie Chart - Expense Distribution
def visualize_pie_chart(username):
    df = fetch_transactions(username)
    expense_df = df[df["type"] == "Expense"]
    category_totals = expense_df.groupby("category")["amount"].sum()

    plt.figure(figsize=(7, 7))
    plt.pie(category_totals, labels=category_totals.index, autopct="%1.1f%%",
            colors=["#ff9999", "#66b3ff", "#99ff99", "#ffcc99"])
    plt.title("Expense Distribution")
    st.pyplot(plt)

# Monthly Trends - Line Chart
def visualize_monthly_trends(username):
    df = fetch_transactions(username)
    df["date"] = pd.to_datetime(df["date"])
    expense_df = df[df["type"] == "Expense"]
    monthly_totals = expense_df.groupby(df["date"].dt.strftime("%Y-%m"))["amount"].sum()

    plt.figure(figsize=(10, 5))
    plt.plot(monthly_totals.index, monthly_totals.values, marker="o", linestyle="-", color="blue")
    plt.xlabel("Month")
    plt.ylabel("Total Expense")
    plt.title("Monthly Expense Trends")
    plt.xticks(rotation=45)
    plt.grid()
    st.pyplot(plt)

# AI-Powered Expense Prediction
def predict_future_expense(username):
    df = fetch_transactions(username)
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.month

    X = df.groupby("month")["amount"].sum().index.values.reshape(-1, 1)
    y = df.groupby("month")["amount"].sum().values

    if len(X) > 1:  # Ensure there's enough data
        model = LinearRegression()
        model.fit(X, y)
        next_month = np.array([[max(X) + 1]])
        return model.predict(next_month)[0]
    else:
        return "Not enough data for prediction"

# Streamlit UI with Improved Navigation & Session Handling
def finance_ui():
    st.title("💰 Welcome to Personal Finance Planner!")
    st.write("Track expenses, predict spending & manage budgets easily.")

    # Initialize session state properly
    if "username" not in st.session_state:
        st.session_state.username = ""

    if "page" not in st.session_state:
        st.session_state.page = "welcome"

    if st.session_state.page == "welcome":
        st.write("### Welcome to Personal Finance Planner!")
        st.write("Track expenses, forecast spending, and manage budgets easily.")
        
        if st.button("Proceed to Login"):
            st.session_state.page = "login"
            

    elif st.session_state.page == "login":
        st.write("### 🔐 Login / Register")
        username_input = st.text_input("Username", key="username")
        password_input = st.text_input("Password", type="password", key="password")

        if st.button("Login"):
            if authenticate_user(username_input, password_input):
                st.session_state.username = username_input
                st.session_state.page = "dashboard"
                st.success("Login successful! 🎉")
                
            else:
                st.error("Invalid username or password!")

        if st.button("Register"):
            if username_input and password_input:
                msg = register_user(username_input, password_input)
                st.success(msg)
            else:
                st.error("Please enter both username and password!")

    elif st.session_state.page == "dashboard":
        st.write(f"🎉 Welcome, {st.session_state.username}! You are now in the dashboard.")
        
        st.write("### Enter Your Transaction Details")
        transaction_type = st.selectbox("Transaction Type", ["Income", "Expense"])
        amount = st.number_input("Enter Amount (₹)", min_value=1.0)
        category = st.text_input("Expense Category (e.g., Food, Rent, Travel)")
        date = st.date_input("Transaction Date")

        if st.button("Add Transaction"):
            add_transaction(st.session_state.username, transaction_type, amount, category, str(date))
            st.success("✅ Transaction Added Successfully!")

        st.write("### Your Transactions")
        df = fetch_transactions(st.session_state.username)
        st.dataframe(df)

# Initialize Databases & Run App
if __name__ == "__main__":
    init_user_db()
    init_finance_db()
    finance_ui()
