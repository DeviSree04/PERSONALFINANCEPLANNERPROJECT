import sqlite3
import streamlit as st

def main():
    # This must be the first Streamlit call
    st.set_page_config(page_title="Test Transactions", layout="centered")
    
    st.title("Test: Add Transaction to DB")
    
    username = st.text_input("Username")
    transaction_type = st.selectbox("Transaction Type", ["Income", "Expense"])
    amount = st.number_input("Amount (₹)", min_value=0.01)
    category = st.text_input("Category")
    date = st.date_input("Date")

    if st.button("Add Transaction"):
        if username and category:
            add_transaction(username, transaction_type, amount, category.strip(), str(date))
        else:
            st.error("Username and Category are required.")
# Initialize finance database with transactions table
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

# Add a new transaction and print debug information
def add_transaction(username, transaction_type, amount, category, date):
    try:
        conn = sqlite3.connect("finance.db")
        cursor = conn.cursor()
        st.write("Inserting:", username, transaction_type, amount, category, date)  # Debug log
        cursor.execute(
            "INSERT INTO transactions (username, type, amount, category, date) VALUES (?, ?, ?, ?, ?)",
            (username, transaction_type, amount, category, date)
        )
        conn.commit()
        st.success("Transaction added successfully!")
    except Exception as e:
        st.error(f"Error adding transaction: {e}")
    finally:
        conn.close()

# Streamlit UI
def main():
    st.set_page_config(page_title="Test Transactions", layout="centered")
    st.title("Test: Add Transaction to DB")

    username = st.text_input("Username")
    transaction_type = st.selectbox("Transaction Type", ["Income", "Expense"])
    amount = st.number_input("Amount (₹)", min_value=0.01)
    category = st.text_input("Category")
    date = st.date_input("Date")

    if st.button("Add Transaction"):
        if username and category:
            add_transaction(username, transaction_type, amount, category.strip(), str(date))
        else:
            st.error("Username and Category are required.")

if __name__ == "_main_":
    init_finance_db()
    main()
