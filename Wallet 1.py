import streamlit as st
import pandas as pd

# Load your CSV data
@st.cache_data
def load_data():
    # Replace 'your_data.csv' with your actual CSV file path
    return pd.read_csv(r"C:\Users\sugan\Desktop\random_wallet_transactions.csv")

transactions_df = load_data()

# Streamlit App Layout
st.title("Wallet Details Page")

# Select Wallet
wallets = transactions_df['Sender Wallet'].tolist() + transactions_df['Receiver Wallet'].tolist()
wallets = sorted(set(wallets))  # Unique and sorted wallet addresses
selected_wallet = st.selectbox("Select Wallet", wallets)

if selected_wallet:
    # Wallet Overview
    st.header("Wallet Overview")
    wallet_transactions = transactions_df[
        (transactions_df['Sender Wallet'] == selected_wallet) | 
        (transactions_df['Receiver Wallet'] == selected_wallet)
    ]
    total_transactions = len(wallet_transactions)
    total_amount_transacted = wallet_transactions['Amount Transacted'].sum()
    risk_score = wallet_transactions['Risk Score'].mode()[0] if not wallet_transactions.empty else "Unknown"
    owner = "Not Linked to KYC"  # Placeholder, update if KYC data is available

    st.write(f"**Wallet Address:** {selected_wallet}")
    st.write(f"**Owner:** {owner}")
    st.write(f"**Risk Score:** {risk_score}")
    st.write(f"**Total Transactions:** {total_transactions}")
    st.write(f"**Total Amount Transacted:** ${total_amount_transacted:.2f}")

    # Transaction History
    st.header("Transaction History")
    st.write(wallet_transactions[['Transaction ID', 'Sender Wallet', 'Receiver Wallet', 'Amount Transacted', 'Timestamp', 'Risk Score']])

    # Export Options: CSV
    st.download_button(
        label="Download CSV",
        data=wallet_transactions.to_csv(index=False).encode('utf-8'),
        file_name=f"{selected_wallet}_transactions.csv",
        mime='text/csv'
    )
