import requests
import streamlit as st
from datetime import datetime
import pytz
from collections import defaultdict
import pandas as pd

def convert_utc_to_ist(unix_time):
    """Converts UNIX timestamp to IST (Indian Standard Time) and formats it."""
    utc_time = datetime.utcfromtimestamp(unix_time)
    ist_time_zone = pytz.timezone('Asia/Kolkata')
    ist_time = utc_time.replace(tzinfo=pytz.utc).astimezone(ist_time_zone)
    return ist_time.strftime('%Y-%m-%d %H:%M:%S %Z')

def get_block_info(hash_id):
    """Fetch block information using the block hash."""
    sanitized_hash_id = hash_id.strip()
    API_URL = f"https://blockchain.info/block/{sanitized_hash_id}?format=json"
    st.info("Connecting to server...")
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        block_info = response.json()

        st.success("Block data loaded successfully!")
        st.subheader("Block Information")
        st.text(f"Hash: {block_info.get('hash')}")
        st.text(f"Height (Block Number): {block_info.get('height', 'Unknown')}")
        st.text(f"Time: {convert_utc_to_ist(block_info.get('time', 0))}")
        st.text(f"Block Size: {block_info.get('size')} bytes")
        st.text(f"Number of Transactions: {len(block_info.get('tx', []))}")

        return block_info
    except requests.exceptions.HTTPError as e:
        st.error(f"HTTP Error: {e.response.status_code} - {e.response.reason}")
    except requests.exceptions.ConnectionError:
        st.error("Failed to connect to the API. Check your internet connection or the API URL.")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
    return None

def get_transaction_details(tx_id):
    """Fetch details of a specific transaction using its transaction hash."""
    API_URL = f"https://blockchain.info/rawtx/{tx_id}?format=json"
    st.info(f"Requesting details for transaction {tx_id}...")
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        transaction_info = response.json()
        st.success("Transaction data loaded successfully!")
        return transaction_info
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching transaction details: {e}")
        return None

def analyze_frequent_transactions(block_info):
    """Analyze transactions for frequent transactions within the same wallet over 10 minutes."""
    transactions = block_info.get('tx', [])
    addr_transactions = defaultdict(list)
    suspicious_details = []

    # Collect transactions by address and timestamp
    for tx in transactions:
        outputs = tx.get('out', [])
        inputs = tx.get('inputs', [])
        for output in outputs:
            if output.get('value', 0) > 50000000:  # Threshold for "larger amount"
                addr_transactions[output.get('addr')].append((tx.get('time'), output.get('value'), tx.get('hash')))

    # Filter for addresses with transactions more than 5 times in 10 minutes
    for addr, details in addr_transactions.items():
        times = [time for time, _, _ in details]
        if len(times) < 5:
            continue

        # Sort and check the interval
        details.sort()  # Sort by time
        for i in range(len(times) - 4):
            if (times[i + 4] - times[i]) <= 600:  # 10 minutes in seconds
                transaction_hashes = [tx_hash for _, _, tx_hash in details[i:i+5]]
                transaction_amounts = [value for _, value, _ in details[i:i+5]]
                suspicious_details.append((addr, transaction_hashes, transaction_amounts))
                break

    return suspicious_details

# Streamlit user interface for blockchain fraud detection
st.title("AI Insights in Blockchain Transactions")

# List of predefined block hashes
block_hashes = [
    "000000000000000000001b5e13e491e390f59152f6346f149ee352a4e50c2c3b",
    "0000000000000000000181ea8abf5a8d34c03767add007e6fcb75bce44492eb7",
    "00000000000000000000a3fde1d8121072dcb33b02033bbfd9db35ef7e0aa040",
    "000000000000000000001b5e13e491e390f59152f6346f149ee352a4e50c2c3b",
    "000000000000000000028a884cf974b7cc75bbea3b06120aa313f6bea6443691",
    "000000000000000000028a884cf974b7cc75bbea3b06120aa313f6bea6443691",
    "000000000000000000021a36e537753b01c4a169974e8b8fcb693802b418380a",
    "00000000000000000000964b4c20beecd20302d03e8708d0e0054d814c024d5b",
    "00000000000000000000c03c39cc2926713fd189f9632dfd261ea9c44363dfa4"
]

# Interface to allow selecting or entering a block hash
st.subheader("Enter or select a Block Hash ID:")
block_hash_input = st.text_input("Enter a block hash or choose from below", key="hash_input")
if not block_hash_input:
    block_hash_input = st.selectbox("Or choose from commonly used hashes:", block_hashes)

if block_hash_input:
    st.subheader("Analyzing Transactions for Frequent Large Transfers")
    block_info = get_block_info(block_hash_input)
    if block_info:
        suspicious_transactions = analyze_frequent_transactions(block_info)
        if suspicious_transactions:
            suspicious_data = []
            for addr, hashes, amounts in suspicious_transactions:
                for tx_hash, amount in zip(hashes, amounts):
                    # Convert amount from Satoshis to Bitcoin
                    amount_btc = amount / 100000000.0
                    transaction_details = get_transaction_details(tx_hash)
                    if transaction_details:
                        inputs = transaction_details.get('inputs', [])
                        outputs = transaction_details.get('out', [])
                        sender = ', '.join([inp['prev_out']['addr'] for inp in inputs if 'prev_out' in inp])
                        receiver = ', '.join([out['addr'] for out in outputs if 'addr' in out])
                        suspicious_data.append({
                            "Transaction Hash": tx_hash,
                            "Amount (BTC)": f"{amount_btc:.8f} BTC",  # Format as Bitcoin
                            "Sender": sender,
                            "Receiver": receiver,
                            "Address Involved": addr
                        })
            
            # Display the table with suspicious transactions
            if suspicious_data:
                df = pd.DataFrame(suspicious_data)
                st.table(df)  # Display as a table
                st.write(f"Total suspicious transactions: {len(suspicious_data)}")
            else:
                st.write("No suspicious transactions found.")
        else:
            st.write("No frequent large transactions detected.")
