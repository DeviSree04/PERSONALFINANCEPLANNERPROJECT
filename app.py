import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from sklearn.linear_model import LinearRegression
import numpy as np

# Initialize database
def init_db():
    conn = sqlite3.connect("finance.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (
                        id INTEGER PRIMARY KEY,
                        type TEXT,
                        amount REAL,
                        category TEXT,
                        date TEXT)''')
    conn.commit()
    conn.close()

# Function to add transactions
def add_transaction(transaction_type, amount, category, date):
    conn = sqlite3.connect("finance.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO transactions (type, amount, category, date) VALUES (?, ?, ?, ?)",
                   (transaction_type, amount, category, date))
    conn.commit()
    conn.close()

# Function to fetch transactions
def fetch_transactions():
    conn = sqlite3.connect("finance.db")
    df = pd.read_sql_query("SELECT * FROM transactions", conn)
    conn.close()
    return df

# Bar Chart - Expense Breakdown
def visualize_expenses():
    df = fetch_transactions()
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
def visualize_pie_chart():
    df = fetch_transactions()
    expense_df = df[df["type"] == "expense"]
    category_totals = expense_df.groupby("category")["amount"].sum()

    plt.figure(figsize=(7, 7))
    plt.pie(category_totals, labels=category_totals.index, autopct="%1.1f%%",
            colors=["#ff9999", "#66b3ff", "#99ff99", "#ffcc99"])
    plt.title("Expense Distribution")
    st.pyplot(plt)

# Line Chart - Monthly Expense Trends
def visualize_monthly_trends():
    df = fetch_transactions()
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
def predict_future_expense():
    df = fetch_transactions()
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.month

    # Prepare Data
    X = df.groupby("month")["amount"].sum().index.values.reshape(-1, 1)
    y = df.groupby("month")["amount"].sum().values

    model = LinearRegression()
    model.fit(X, y)

    # Predict next month's expense
    next_month = np.array([[max(X) + 1]])
    predicted_expense = model.predict(next_month)[0]
    
    return predicted_expense

# Budget Advisory System
def budget_advice():
    df = fetch_transactions()
    total_expense = df[df["type"] == "expense"]["amount"].sum()

    if total_expense > 5000:  # Example threshold
        return "⚠ You are overspending! Try reducing expenses in food & entertainment."
    else:
        return "✅ Your spending is under control. Keep saving!"

# Streamlit UI
def finance_ui():
    st.title("📊 Personal Finance Planner")
    st.write("Track, analyze, and manage your expenses efficiently.")

    # User Input Form
    type_input = st.selectbox("Transaction Type", ["income", "expense"])
    amount_input = st.number_input("Amount", min_value=1.0)
    category_input = st.text_input("Category")
    date_input = st.date_input("Date")

    if st.button("Add Transaction"):
        add_transaction(type_input, amount_input, category_input, str(date_input))
        st.success("Transaction Added!")

    # Display Transactions
    df = fetch_transactions()
    st.write("### Transactions Data")
    st.dataframe(df)

    # Budget Advisory System
    if st.button("Get Budget Advice"):
        advice = budget_advice()
        st.warning(advice) if "⚠" in advice else st.success(advice)

    # Expense Charts
    if st.button("Show Expense Bar Chart"):
        visualize_expenses()

    if st.button("Show Expense Pie Chart"):
        visualize_pie_chart()

    if st.button("Show Monthly Trends"):
        visualize_monthly_trends()

    # Predict Future Expenses
    if st.button("Predict Next Month’s Expense"):
        prediction = predict_future_expense()
        st.success(f"Projected Expense for Next Month: ₹{prediction:.2f}")

    # Filter Transactions by Month
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.strftime("%Y-%m")
    selected_month = st.selectbox("Choose Month:", df["month"].unique())

    filtered_df = df[df["month"] == selected_month]
    st.write(f"### Transactions for {selected_month}")
    st.dataframe(filtered_df)

# Initialize Database and Run App
if __name__ == "_main_":
    init_db()
    finance_ui()