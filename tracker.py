import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os

st.set_page_config(page_title="Expense Tracker", layout="wide")

# Load or create CSV
csv_file = "expenses.csv"
columns = ["Date", "Category", "Amount", "Payment Method"]

if os.path.exists(csv_file):
    try:
        df = pd.read_csv(csv_file)
        if df.empty or list(df.columns) != columns:
            df = pd.DataFrame(columns=columns)
            df.to_csv(csv_file, index=False)
    except pd.errors.EmptyDataError:
        df = pd.DataFrame(columns=columns)
        df.to_csv(csv_file, index=False)
else:
    df = pd.DataFrame(columns=columns)
    df.to_csv(csv_file, index=False)

# Sidebar
st.sidebar.title("ExpenseTracker")
st.sidebar.caption("Smart Expense Management")
page = st.sidebar.radio("NAVIGATION", ["Dashboard", "Add Expense", "Reports"])

# Quick stats
st.sidebar.markdown("### QUICK STATS")
this_month = df[df['Date'].str.startswith(str(datetime.now().year) + '-' + str(datetime.now().month).zfill(2))]
st.sidebar.markdown(f"📈 This Month: **${this_month['Amount'].sum():.2f}**")
st.sidebar.markdown(f"📉 Total Expenses: **${df['Amount'].sum():.2f}**")

# Add Expense
if page == "Add Expense":
    st.title("➕ Add Expense")
    with st.form("expense_form"):
        amount = st.number_input("Amount", min_value=0.0, format="%.2f")
        category = st.selectbox("Category", ["Food", "Transport", "Entertainment", "Bills", "Others"])
        date = st.date_input("Date", value=datetime.today())
        payment_method = st.selectbox("Payment Method", ["Cash", "Card", "UPI", "Other"])
        submitted = st.form_submit_button("Add")
        if submitted:
            new_expense = {
                "Date": date.strftime("%Y-%m-%d"),
                "Category": category,
                "Amount": amount,
                "Payment Method": payment_method
            }
            df = pd.concat([df, pd.DataFrame([new_expense])], ignore_index=True)
            df.to_csv(csv_file, index=False)
            st.success("Expense Added!")

# Dashboard
elif page == "Dashboard":
    st.title("📊 Dashboard")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("This Month", f"${this_month['Amount'].sum():.2f}")
    col2.metric("Total Expenses", f"${df['Amount'].sum():.2f}", f"{len(df)} transactions")
    col3.metric("Average Expense", f"${df['Amount'].mean():.2f}" if not df.empty else "$0.00")
    col4.metric("Payment Methods", f"{df['Payment Method'].nunique()}" if not df.empty else "0")

    # Export button
    st.download_button("⬇️ Export CSV", data=df.to_csv(index=False), file_name="expenses.csv", mime="text/csv")

    # Monthly Spending Trend
    st.markdown("### 📈 Monthly Spending Trend")
    if not df.empty:
        df['Month'] = pd.to_datetime(df['Date']).dt.to_period('M').astype(str)
        month_group = df.groupby('Month')['Amount'].sum()
        fig, ax = plt.subplots()
        month_group.plot(kind='line', marker='o', ax=ax)
        ax.set_ylabel("Amount ($)")
        st.pyplot(fig)
    else:
        st.info("No data to display chart.")

# Reports
elif page == "Reports":
    st.title("📑 Reports")
    st.dataframe(df)

    st.markdown("### 📊 Category-wise Spending")
    if not df.empty:
        cat_group = df.groupby('Category')['Amount'].sum()
        fig, ax = plt.subplots()
        cat_group.plot(kind='bar', ax=ax)
        st.pyplot(fig)
    else:
        st.info("No data to display report.")
