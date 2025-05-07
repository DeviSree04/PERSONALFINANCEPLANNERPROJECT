import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import bcrypt
import os
from sklearn.linear_model import LinearRegression
import numpy as np

# ---------------------- Database Initialization ----------------------

def init_user_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT
        )
    ''')
    conn.commit()
    conn.close()
    print("User DB initialized")

def init_finance_db():
    conn = sqlite3.connect("finance.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            type TEXT,
            amount REAL,
            category TEXT,
            date TEXT
        )
    ''')
    conn.commit()
    conn.close()
    print("Finance DB initialized")

# ---------------------- User Management ----------------------

def register_user(username, password):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users WHERE username=?", (username,))
    existing_user = cursor.fetchone()

    if existing_user:
        conn.close()
        return "Username already exists! Choose a different one."

    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
    conn.commit()
    conn.close()
    return "User registered successfully!"

def authenticate_user(username, password):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE username=?", (username,))
    result = cursor.fetchone()
    conn.close()

    if result:
        return bcrypt.checkpw(password.encode(), result[0])
    return False

# ---------------------- Finance Management ----------------------

def add_transaction(username, transaction_type, amount, category, date):
    st.write("Debug - Adding transaction:")
    st.write(f"Username: {username}, Type: {transaction_type}, Amount: {amount}, Category: {category}, Date: {date}")

    if not all([username, transaction_type, amount, category, date]):
        st.error("Please fill in all transaction fields.")
        return

    conn = sqlite3.connect("finance.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO transactions (username, type, amount, category, date) VALUES (?, ?, ?, ?, ?)",
        (username, transaction_type, amount, category, date)
    )
    conn.commit()
    conn.close()

def fetch_transactions(username):
    conn = sqlite3.connect("finance.db")
    df = pd.read_sql_query("SELECT * FROM transactions WHERE username=?", conn, params=(username,))
    conn.close()
    return df

# ---------------------- Visualization ----------------------

def visualize_expenses(username):
    df = fetch_transactions(username)
    expense_df = df[df["type"] == "Expense"]

    if expense_df.empty:
        st.info("No expenses to show.")
        return

    category_totals = expense_df.groupby("category")["amount"].sum()
    plt.figure(figsize=(8, 5))
    category_totals.plot(kind="bar", color="skyblue")
    plt.xlabel("Category")
    plt.ylabel("Amount Spent")
    plt.title("Expense Breakdown")
    plt.xticks(rotation=45)
    plt.grid(True)
    st.pyplot(plt)

# ---------------------- Streamlit UI ----------------------

def finance_ui():
    st.set_page_config(page_title="Personal Finance Planner", layout="centered")
    st.title("💰 Personal Finance Planner")

    if "username" not in st.session_state:
        st.session_state["username"] = None
    if "page" not in st.session_state:
        st.session_state["page"] = "welcome"

    # Welcome
    if st.session_state["page"] == "welcome":
        st.write("Track expenses, forecast spending, and manage budgets easily.")
        if st.button("Proceed to Login"):
            st.session_state["page"] = "login"
            st.rerun()

    # Login/Register
    elif st.session_state["page"] == "login":
        st.subheader("🔐 Login / Register")
        username_input = st.text_input("Username", key="login_username")
        password_input = st.text_input("Password", type="password", key="login_password")

        if st.button("Login"):
            if authenticate_user(username_input, password_input):
                st.session_state["username"] = username_input
                st.session_state["page"] = "dashboard"
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid username or password.")

        if st.button("Register"):
            if username_input and password_input:
                msg = register_user(username_input, password_input)
                st.success(msg)
            else:
                st.error("Please enter both username and password.")

    # Dashboard
    elif st.session_state["page"] == "dashboard":
        st.write(f"🎉 Welcome, *{st.session_state['username']}*")

        # Transaction Form
        st.subheader("Enter Transaction")
        transaction_type = st.selectbox("Type", ["Income", "Expense"])
        amount = st.number_input("Amount (₹)", min_value=1.0)
        category = st.text_input("Category (e.g., Rent, Food, Travel)")
        date = st.date_input("Date")

        if st.button("Add Transaction"):
            add_transaction(st.session_state["username"], transaction_type, amount, category, str(date))
            st.success("Transaction added successfully!")

        # Transactions List
        st.subheader("Your Transactions")
        df = fetch_transactions(st.session_state["username"])
        st.dataframe(df)

        # Visualization
        if st.button("Show Expense Breakdown"):
            visualize_expenses(st.session_state["username"])

        if st.button("Logout"):
            st.session_state.clear()
            st.rerun()

# ---------------------- Main ----------------------

if _name_ == "_main_":
    st.write("Current working directory:", os.getcwd())
    st.write("User DB Path:", os.path.abspath("users.db"))
    st.write("Finance DB Path:", os.path.abspath("finance.db"))

    init_user_db()
    init_finance_db()
    finance_ui()
