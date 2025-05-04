import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import bcrypt
from sklearn.linear_model import LinearRegression
import numpy as np

st.title("PERSONAL FINANCE PLANNER")
# Initialize user authentication database
def init_user_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        username TEXT PRIMARY KEY,
                        password TEXT)''')
    conn.commit()
    conn.close()

# Register new users
def register_user(username, password):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
    conn.commit()
    conn.close()

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
    expense_df = df[df["type"] == "expense"]
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
    expense_df = df[df["type"] == "expense"]
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
    expense_df = df[df["type"] == "expense"]
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

# Streamlit UI with Welcome Message & User Authentication
def finance_ui():
    st.title(" Welcome to Personal Finance Planner!")
    st.write("Track expenses, predict spending & manage budgets easily.")

    if "username" not in st.session_state:
        st.session_state.username = None

    if st.session_state.username:
        st.success(f"Welcome back, {st.session_state.username}! 🎉")

        # Expense Tracking UI
        st.write("### Enter Your Transaction Details")
        transaction_type = st.selectbox("Transaction Type", ["Income", "Expense"])
        amount = st.number_input("Enter Amount (₹)", min_value=1.0)
        category = st.text_input("Expense Category (e.g., Food, Rent, Travel)")
        date = st.date_input("Transaction Date")

        if st.button("Add Transaction"):
            add_transaction(st.session_state.username, transaction_type, amount, category, str(date))
            st.success("✅ Transaction Added Successfully!")

        # Display Transactions
        st.write("### Your Transactions")
        df = fetch_transactions(st.session_state.username)
        st.dataframe(df)

        # Show Expense Charts
        if st.button("Show Expense Bar Chart"):
            visualize_expenses(st.session_state.username)

        if st.button("Show Expense Pie Chart"):
            visualize_pie_chart(st.session_state.username)

        if st.button("Show Monthly Trends"):
            visualize_monthly_trends(st.session_state.username)

        # Predict Future Expense
        if st.button("Predict Next Month’s Expense"):
            prediction = predict_future_expense(st.session_state.username)
            st.success(f"Projected Expense for Next Month: ₹{prediction:.2f}" if isinstance(prediction, float) else prediction)

    else:
        st.write("### 🔐 Login / Register")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if authenticate_user(username, password):
                st.session_state.username = username
                st.success("Login successful! 🎉")
            else:
                st.error("Invalid username or password!")

        if st.button("Register"):
            if username and password:
                register_user(username, password)
                st.success("User registered! Now login.")
            else:
                st.error("Please enter both username and password.")

# Initialize Databases & Run App
if __name__ == "_main_":
    init_user_db()
    init_finance_db()
    finance_ui()