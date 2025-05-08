import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import bcrypt

# Set config first
st.set_page_config(page_title="Personal Finance Planner", layout="centered")

# ---------------------- DATABASE INITIALIZATION ----------------------

def init_user_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        username TEXT PRIMARY KEY,
                        password TEXT)''')
    conn.commit()
    conn.close()

def init_finance_db():
    conn = sqlite3.connect("finance.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT,
                        type TEXT,
                        amount REAL,
                        category TEXT,
                        date TEXT)''')
    conn.commit()
    conn.close()

# ---------------------- AUTH FUNCTIONS ----------------------

def register_user(username, password):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users WHERE username=?", (username,))
    existing = cursor.fetchone()

    if existing:
        conn.close()
        return "Username already exists! Choose a different one."

    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_pw))
    conn.commit()
    conn.close()
    return "User registered successfully!"

def authenticate_user(username, password):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE username=?", (username,))
    result = cursor.fetchone()
    conn.close()
    return result and bcrypt.checkpw(password.encode(), result[0])

# ---------------------- TRANSACTION FUNCTIONS ----------------------

def add_transaction(username, transaction_type, amount, category, date):
    conn = sqlite3.connect("finance.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO transactions (username, type, amount, category, date) VALUES (?, ?, ?, ?, ?)",
                   (username, transaction_type, amount, category, date))
    conn.commit()
    conn.close()

def fetch_transactions(username):
    conn = sqlite3.connect("finance.db")
    df = pd.read_sql_query("SELECT * FROM transactions WHERE username=?", conn, params=(username,))
    conn.close()
    return df

def visualize_expenses(username):
    df = fetch_transactions(username)
    expense_df = df[df["type"] == "Expense"]
    if expense_df.empty:
        st.info("No expense data to visualize.")
        return
    category_totals = expense_df.groupby("category")["amount"].sum()

    plt.figure(figsize=(8, 5))
    category_totals.plot(kind="bar", color="skyblue")
    plt.title("Expense Breakdown")
    plt.xlabel("Category")
    plt.ylabel("Amount")
    plt.xticks(rotation=45)
    plt.grid()
    st.pyplot(plt)

# ---------------------- STREAMLIT UI ----------------------

def finance_ui():
    st.title("💰 Personal Finance Planner")

    if "username" not in st.session_state:
        st.session_state.username = None
    if "page" not in st.session_state:
        st.session_state.page = "welcome"

    # Welcome page
    if st.session_state.page == "welcome":
        st.write("Track expenses, forecast spending, and manage budgets easily.")
        if st.button("Proceed to Login"):
            st.session_state.page = "login"
            st.rerun()

    # Login page
    elif st.session_state.page == "login":
        st.subheader("🔐 Login / Register")
        username_input = st.text_input("Username")
        password_input = st.text_input("Password", type="password")

        if st.button("Login"):
            if authenticate_user(username_input, password_input):
                st.session_state.username = username_input
                st.session_state.page = "dashboard"
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid username or password.")

        if st.button("Register"):
            if username_input and password_input:
                msg = register_user(username_input, password_input)
                st.success(msg)
            else:
                st.error("Please fill both fields.")

    # Dashboard
    elif st.session_state.page == "dashboard":
        st.subheader(f"Welcome, {st.session_state.username}!")
        st.markdown("### Add New Transaction")
        transaction_type = st.selectbox("Transaction Type", ["Income", "Expense"])
        amount = st.number_input("Amount (₹)", min_value=0.01)
        category = st.text_input("Category")
        date = st.date_input("Date")

        if st.button("Add Transaction"):
            if category.strip():
                add_transaction(st.session_state.username, transaction_type, amount, category.strip(), str(date))
                st.success("Transaction added.")
            else:
                st.error("Category cannot be empty.")

        st.markdown("### Your Transactions")
        df = fetch_transactions(st.session_state.username)
        st.dataframe(df)

        if st.button("Show Expense Breakdown"):
            visualize_expenses(st.session_state.username)

# ---------------------- MAIN ----------------------

if __name__ == "__main__":
    init_user_db()
    init_finance_db()
    finance_ui()
