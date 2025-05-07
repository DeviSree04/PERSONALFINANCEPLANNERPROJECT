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
        return " Username already exists! Choose a different one."

    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
    conn.commit()
    conn.close()
    return "User registered successfully!"

# Verify user login
def authenticate_user(username, password):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE username=?", (username,))
    result = cursor.fetchone()
    conn.close()

    return result and bcrypt.checkpw(password.encode(), result[0])

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

# Streamlit UI
def finance_ui():
    st.title("💰 Personal Finance Planner")

    # Initialize session state properly
    if "username" not in st.session_state:
        st.session_state["username"] = None  # ✅ Use dictionary-style session state access

    if "page" not in st.session_state:
        st.session_state["page"] = "welcome"

    # Welcome Page
    if st.session_state["page"] == "welcome":
        st.write("Track expenses, forecast spending, and manage budgets easily.")
        if st.button("Proceed to Login"):
            st.session_state["page"] = "login"
            st.rerun()

    # Login / Register Page
    elif st.session_state["page"] == "login":
        st.write("### 🔐 Login / Register")
        username_input = st.text_input("Username", key="username")
        password_input = st.text_input("Password", type="password", key="password")

        if st.button("Login"):
            if authenticate_user(username_input, password_input):
                st.session_state["username"] = username_input  # ✅ Works now!
                st.session_state["page"] = "dashboard"
                st.success("Login successful! 🎉")
                st.rerun()
            else:
                st.error("Invalid username or password!")

        if st.button("Register"):
            if username_input and password_input:
                msg = register_user(username_input, password_input)
                st.success(msg)
            else:
                st.error("Please enter both username and password!")

    # Dashboard Page
    elif st.session_state["page"] == "dashboard":
        st.write(f"🎉 Welcome, {st.session_state['username']}! You are now in the dashboard.")

        # Transaction Entry
        st.write("### Enter Your Transaction Details")
        transaction_type = st.selectbox("Transaction Type", ["Income", "Expense"])
        amount = st.number_input("Enter Amount (₹)", min_value=1.0)
        category = st.text_input("Expense Category (e.g., Food, Rent, Travel)")
        date = st.date_input("Transaction Date")

        if st.button("Add Transaction"):
            add_transaction(st.session_state["username"], transaction_type, amount, category, str(date))
            st.success("✅ Transaction Added Successfully!")

        # Show Transactions
        st.write("### Your Transactions")
        df = fetch_transactions(st.session_state["username"])
        st.dataframe(df)

        # Expense Visualization
        if st.button("Show Expense Breakdown"):
            visualize_expenses(st.session_state["username"])

# Initialize Databases & Run App
if __name__ == "__main__":
    init_user_db()
    init_finance_db()
    finance_ui()
