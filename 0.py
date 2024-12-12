import streamlit as st
import json
import pandas as pd
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO

# Function to load user data from JSON file
def load_user_data():
    try:
        with open('user_data.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# Function to save user data to JSON file
def save_user_data(user_data):
    with open('user_data.json', 'w') as file:
        json.dump(user_data, file, indent=4)

# Function to load reports
def load_reports():
    try:
        with open('reports.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

# Function to save reports
def save_reports(reports):
    with open('reports.json', 'w') as file:
        json.dump(reports, file, indent=4)

# Register page
def register_user():
    st.title("🔐 Register New Account")
    username = st.text_input("Enter a username")
    password = st.text_input("Enter a password", type="password")
    confirm_password = st.text_input("Confirm your password", type="password")

    if st.button("Register"):
        user_data = load_user_data()
        if password != confirm_password:
            st.error("Passwords do not match!")
        elif username in user_data:
            st.error("Username already exists!")
        else:
            user_data[username] = password
            save_user_data(user_data)
            st.success("Account created successfully!")
            st.info("You can now log in with your credentials.")
            st.session_state.redirect_to_login = True

# Login page
def login_user():
    st.title("🔑 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if hasattr(st.session_state, "redirect_to_login") and st.session_state.redirect_to_login:
        st.success("Account created successfully. Please log in.")
        del st.session_state.redirect_to_login

    if st.button("Login"):
        user_data = load_user_data()
        if username in user_data and user_data[username] == password:
            current_time = datetime.now()
            hour = current_time.hour
            greeting = "Good Morning" if hour < 12 else "Good Afternoon" if hour < 18 else "Good Evening"
            st.success(f"{greeting}, {username}!")
            st.session_state.logged_in = True
            st.session_state.username = username
            return True, username
        else:
            st.error("Invalid username or password!")
    return False, None

# Logout page
def logout_user():
    st.session_state.logged_in = False
    del st.session_state.username
    st.success("You have been logged out.")

# Home page
def home_page():
    st.title("🏠 Blockchain Analysis Tool")
    st.markdown("""Welcome to the Blockchain Analysis Tool!
        - Explore blockchain transactions.
        - Detect fraudulent activities.
        - Analyze and visualize data like a pro.
    """)

    st.markdown("### Learn more about Blockchain:")
    video_url = "https://youtu.be/QJn28fFKUR0?si=IPPXXYeFZCQk1tB6"
    st.video(video_url)

import pandas as pd
import streamlit as st

def user_dashboard(username):
    """
    Function to handle the user dashboard with various navigation options.
    Allows the user to upload data and view blockchain analytics, visualization,
    peer-to-peer transaction data, and 3D blockchain connections.
    """
    st.sidebar.title("📊 Dashboard")
    st.sidebar.write(f"Logged in as: {username}")

    search_query = st.text_input("Search", "Enter your search query here...")
    
    if search_query:
        st.write(f"Search results for: **{search_query}**")
    
    pages = ["🏠 Home", "📤 View Data", "📈 Blockchain Analytics", "📊 Visualization", "💱 Peer-to-Peer Transaction", 
             "🌐 3D Visualization of Blockchain", "🔗 Explore through API", "👛 Wallet Details", "🧠 AI Insight", "🚪 Logout"]
    choice = st.sidebar.radio("Navigate to:", pages)

    if choice == "🏠 Home":
        home_page()
    elif choice == "📤 View Data":
        load_transaction_data()
    elif choice == "📈 Blockchain Analytics":
        blockchain_analytics()  # Placeholder for blockchain analytics function
    elif choice == "📊 Visualization":
        visualize_transactions()  # Placeholder for visualization function
    elif choice == "💱 Peer-to-Peer Transaction":
        peer_to_peer_transaction()
    elif choice == "🌐 3D Visualization of Blockchain":
        visualize_blockchain_network()
    elif choice == "🔗 Explore through API":
        explore_through_api()
    elif choice == "👛 Wallet Details":
        wallet_details()
   
    elif choice == "🚪 Logout":
        logout_user()


def load_data():
    return pd.read_csv(r"C:\Users\sugan\Desktop\random_wallet_transactions.csv")

transactions_df = load_data()

# Define wallet details functionality
def wallet_details():
    st.title("👛 Wallet Details")
    wallets = transactions_df['Sender Wallet'].tolist() + transactions_df['Receiver Wallet'].tolist()
    wallets = sorted(set(wallets))
    selected_wallet = st.selectbox("Select Wallet", wallets)
    if selected_wallet:
        wallet_transactions = transactions_df[
            (transactions_df['Sender Wallet'] == selected_wallet) | 
            (transactions_df['Receiver Wallet'] == selected_wallet)
        ]
        st.header("Wallet Overview")
        st.write(f"**Wallet Address:** {selected_wallet}")
        st.write(f"**Total Transactions:** {len(wallet_transactions)}")
        st.write(f"**Total Amount Transacted:** ${wallet_transactions['Amount Transacted'].sum():.2f}")
        st.header("Transaction History")
        st.write(wallet_transactions[['Transaction ID', 'Sender Wallet', 'Receiver Wallet', 'Amount Transacted', 'Timestamp', 'Risk Score']])
        st.download_button(
            label="Download CSV",
            data=wallet_transactions.to_csv(index=False).encode('utf-8'),
            file_name=f"{selected_wallet}_transactions.csv",
            mime='text/csv'
        )



import requests
import time
import streamlit as st
from io import BytesIO
import qrcode
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes

def generate_qr_code(data):
    """Generates and returns a QR code image in bytes for Streamlit display."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    qr_image = qr.make_image(fill_color="black", back_color="white")

    # Convert the PIL image to a bytes object
    img_buffer = BytesIO()
    qr_image.save(img_buffer, format="PNG")
    img_buffer.seek(0)
    return img_buffer

def get_block_info(hash_id):
    API_URL = f"https://blockchain.info/block/{hash_id}?format=json"
    st.info("Connecting to server...")
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        block_info = response.json()

        st.success("Block data loaded successfully!")
        block_count = block_info.get("height", "Unknown")
        st.subheader("Block Information")
        st.text(f"Hash: {block_info.get('hash')}")
        st.text(f"Height (Block Number): {block_count}")
        st.text(f"Time: {block_info.get('time')}")
        st.text(f"Block Size: {block_info.get('size')} bytes")
        st.text(f"Number of Transactions: {len(block_info.get('tx', []))}")
        st.text(f"Total Blocks in the Blockchain: {block_count + 1}")

        return block_info

    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching block data: {e}")
        return None

def get_transaction_details(tx_id):
    API_URL = f"https://blockchain.info/rawtx/{tx_id}?format=json"
    st.info("Requesting transaction details...")
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        transaction_info = response.json()
        st.success("Transaction data loaded successfully!")
        return transaction_info

    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching transaction details: {e}")
        return None

def is_mining_transaction(transaction):
    return len(transaction.get("inputs", [])) == 0

def extract_scriptsig(transaction_details):
    return [
        tx_input.get("script", "No scriptSig available")
        for tx_input in transaction_details.get("inputs", [])
    ]

def get_signer_identity(scriptsig_details):
    if scriptsig_details:
        return "Signer Identity: Decoded from ScriptSig"
    return "No identity available from ScriptSig"

def show_beneficiary_details(transaction_details):
    st.subheader("Beneficiary Details")
    if is_mining_transaction(transaction_details):
        st.write("This is a mining transaction (block reward).")
        for tx_output in transaction_details.get("out", []):
            address = tx_output.get("addr", "N/A")
            value_btc = tx_output.get("value", 0) / 1e8
            st.write(f"- **Received by**: `{address}`, **Amount**: `{value_btc} BTC`")
    else:
        st.write("This is a regular transaction.")
        st.write("**Beneficiaries (Receivers):**")
        for tx_output in transaction_details.get("out", []):
            address = tx_output.get("addr", "N/A")
            value_btc = tx_output.get("value", 0) / 1e8
            st.write(f"- **Received by**: `{address}`, **Amount**: `{value_btc} BTC`")
        
        st.write("**Sources (Senders):**")
        for tx_input in transaction_details.get("inputs", []):
            prev_out = tx_input.get("prev_out", {})
            sender_address = prev_out.get("addr", "N/A")
            st.write(f"- **Source Address**: `{sender_address}`")

    st.subheader("Witness Signatures and Addresses")
    found_witness = False
    for i, tx_input in enumerate(transaction_details.get("inputs", [])):
        if "witness" in tx_input:
            witness_data = tx_input["witness"]
            st.write(f"- **Witness Signature**: `{witness_data}`")
            found_witness = True
            
            # Add unique key to the button
            if st.button(f"Generate QR Code for Witness Signature - Input {i+1}", key=f"qr_button_{i}"):
                qr_image_bytes = generate_qr_code(witness_data)
                st.image(qr_image_bytes, caption=f"QR Code for Witness Signature - Input {i+1}")
    
    if not found_witness:
        st.write("No witness for this transaction.")
    
    scriptsig_details = extract_scriptsig(transaction_details)
    st.subheader("ScriptSig (Transaction Authorization Potential Forensics)")
    if scriptsig_details:
        for i, script in enumerate(scriptsig_details, 1):
            st.write(f"- **ScriptSig for Input {i}**: `{script}`")
    
    signer_identity = get_signer_identity(scriptsig_details)
    st.write(f"**Signer Identity**: {signer_identity}")

def visualize_transactions(block_data):
    transactions = block_data.get("tx", [])
    if not transactions:
        st.write("No transactions found in this block.")
        return

    st.subheader("Visualizing Transactions in Block")
    tx_ids = [tx.get('hash') for tx in transactions[:15]]
    selected_tx = st.selectbox("Select a transaction to explore:", tx_ids)
    
    if selected_tx:
        st.write(f"Fetching details for Transaction: `{selected_tx}`")
        transaction_details = get_transaction_details(selected_tx)
        if transaction_details:
            st.write("Transaction details fetched successfully!")
            show_beneficiary_details(transaction_details)

# Explore through API function
def  explore_through_api():
    st.title("🔗 Explore Blockchain API")
    st.markdown("""
    Here you can explore blockchain data through an API.
    Enter a Block Hash ID to view its details.
    """)

    block_hash = st.text_input("Enter Block Hash ID")

    if block_hash:
        block_data = get_block_info(block_hash)
        if block_data:
            st.subheader("Options")
            st.write("Select a transaction to view detailed information.")
            visualize_transactions(block_data)





import plotly.graph_objects as go
import numpy as np
import pandas as pd
import streamlit as st

def visualize_blockchain_network(df):
    """
    Visualizes the blockchain network in 3D with fraudulent transactions highlighted in red.
    """
    # Ensure the 'is_fraudulent' column is boolean
    if 'is_fraudulent' in df.columns:
        df['is_fraudulent'] = df['is_fraudulent'].astype(bool)  # Convert to boolean if necessary
    else:
        st.error("The 'is_fraudulent' column is missing in the data!")
        return

    # Extract relevant columns from the dataframe (assuming 'address', 'recipient' exist)
    addresses = df['address'].unique()
    recipients = df['recipient'].unique()

    # Generate random coordinates for addresses and recipients for visualization purposes
    np.random.seed(42)
    address_coordinates = np.random.rand(len(addresses), 3)  # Random 3D coordinates for addresses
    recipient_coordinates = np.random.rand(len(recipients), 3)  # Random 3D coordinates for recipients

    # Create a 3D scatter plot using Plotly
    x = np.concatenate([address_coordinates[:, 0], recipient_coordinates[:, 0]])
    y = np.concatenate([address_coordinates[:, 1], recipient_coordinates[:, 1]])
    z = np.concatenate([address_coordinates[:, 2], recipient_coordinates[:, 2]])

    # Create the 3D plot
    fig = go.Figure()

    # Plot addresses and recipients in blue
    fig.add_trace(go.Scatter3d(x=x, y=y, z=z, mode='markers',
                             marker=dict(size=8, color='blue', opacity=0.6), name="Transactions"))

    # Filter fraudulent transactions (where 'is_fraudulent' is True)
    fraudulent_transactions = df[df['is_fraudulent'] == True]
    fraud_addresses = fraudulent_transactions['address'].unique()
    fraud_recipients = fraudulent_transactions['recipient'].unique()

    # Find the coordinates of fraudulent addresses and recipients
    fraud_x = np.concatenate([address_coordinates[np.isin(addresses, fraud_addresses), 0], recipient_coordinates[np.isin(recipients, fraud_recipients), 0]])
    fraud_y = np.concatenate([address_coordinates[np.isin(addresses, fraud_addresses), 1], recipient_coordinates[np.isin(recipients, fraud_recipients), 1]])
    fraud_z = np.concatenate([address_coordinates[np.isin(addresses, fraud_addresses), 2], recipient_coordinates[np.isin(recipients, fraud_recipients), 2]])

    # Highlight fraudulent transactions in red
    fig.add_trace(go.Scatter3d(x=fraud_x, y=fraud_y, z=fraud_z, mode='markers',
                             marker=dict(size=8, color='red', opacity=0.6), name="Fraudulent Transactions"))

    # Layout configuration
    fig.update_layout(scene=dict(xaxis_title='X', yaxis_title='Y', zaxis_title='Z'),
                      title="3D Blockchain Network Visualization")

    # Display the plot in Streamlit
    st.plotly_chart(fig)





    
def peer_to_peer_transaction():
    """
    Function to handle both the transaction submission and the display of peer-to-peer transactions.
    Allows users to submit peer-to-peer transactions and also view the transaction count between addresses and recipients.
    """
    st.title("💱 Peer-to-Peer Transaction")

    # Displaying the uploaded dataset if available
    if "uploaded_df" in st.session_state and st.session_state.uploaded_df is not None:
        df = st.session_state.uploaded_df

        # Display the current peer-to-peer transaction count
        peer_count = peer_to_peer_transaction_count(df)
        st.write("Peer-to-Peer Transaction Count:")
        st.write(peer_count)

    else:
        st.warning("Please upload a transaction dataset first.")

    # Input fields for submitting a new transaction
    sender = st.text_input("Sender Address")
    receiver = st.text_input("Receiver Address")
    amount = st.number_input("Amount", min_value=0.01)
    transaction_id = st.text_input("Transaction ID")
    transaction_date = st.date_input("Transaction Date", min_value=datetime.today())

    if st.button("Submit Transaction"):
        if sender and receiver and transaction_id:
            # Creating a new transaction record
            transaction = {
                "address": sender,
                "recipient": receiver,
                "amount": amount,
                "transaction_id": transaction_id,
                "date": transaction_date.strftime("%Y-%m-%d"),
            }

            # Add the new transaction to the dataset
            new_transaction_df = pd.DataFrame([transaction])
            
            # Append the new transaction to the uploaded dataset and update the session state
            updated_df = pd.concat([df, new_transaction_df], ignore_index=True)
            st.session_state.uploaded_df = updated_df

            st.success(f"Transaction successfully recorded: {transaction}")

        else:
            st.error("Please fill in all fields.")

def peer_to_peer_transaction_count(df):
    """
    Function to count peer-to-peer transactions between addresses and recipients.
    Adds a 'type' column with the value 'P2P' to indicate peer-to-peer transactions.
    """
    # Grouping the data by 'address' and 'recipient' to count the transactions
    peer_count = df.groupby(['address', 'recipient']).size().reset_index(name='transaction_count')

    # Adding a new column 'type' to indicate peer-to-peer transactions
    peer_count['type'] = 'P2P'

    return peer_count




# Function to handle file upload for transaction data
# Path to your data file
DATA_FILE_PATH = r"C:\Users\sugan\Desktop\Apps\Block Chain_Project\Datas.csv"

def load_transaction_data():
    """
    Function to automatically load transaction data from a predefined file.
    """
    if "uploaded_df" not in st.session_state:
        st.session_state.uploaded_df = None
    
    try:
        df = pd.read_csv(DATA_FILE_PATH)
        if df.empty:
            st.error("The data file is empty. Please check the file content.")
        else:
            st.success("Data loaded successfully from file!")
            st.write("Data Preview:")
            st.write(df.head())
            st.session_state.uploaded_df = df  # Store the loaded DataFrame in session state for use elsewhere in the app
    except Exception as e:
        st.error(f"Error reading the file: {e}")
    
    return st.session_state.uploaded_df


# Blockchain Analytics Navigation
def blockchain_analytics(df):
    st.markdown("---")
    st.title("🔍 Blockchain Analytics Navigation")

    # Check if the DataFrame contains the required columns
    if "transaction_type" in df.columns:
        st.write("### Transaction Analysis by Type")
        
        # Group the data by transaction_type and count occurrences
        transaction_counts = df.groupby("transaction_type").size().reset_index(name="Count")
        
        # Display aggregated results
        st.write("Transaction Counts by Type:")
        st.write(transaction_counts)
        
        # Display the results as a bar chart
        st.bar_chart(transaction_counts.set_index("transaction_type")["Count"])
    else:
        st.warning("The uploaded dataset does not contain a 'transaction_type' column. Please verify the data.")

    # Navigation options
    analytics_options = ["📂 Overview", "📊 Data Insights", "📉 Network Analysis", "🕵️‍♂️ Transaction Monitoring", "🕵️‍♂️ Pseudonymous Addresses"]
    analytics_choice = st.selectbox("Select an analysis type:", analytics_options)

    if analytics_choice == "📂 Overview":
        st.write("### Blockchain Overview")
        st.write("Gain a high-level understanding of blockchain transactions.")
        user_reporting_and_collaboration()
    elif analytics_choice == "📊 Data Insights":
        st.write("### Data Insights")
        st.write("Explore trends, patterns, and anomalies in the data.")
        st.write("Data Statistics:")
        st.write(df.describe())
    elif analytics_choice == "📉 Network Analysis":
        st.write("### Network Analysis")
        st.write("Analyze blockchain connections and transaction networks.")
    elif analytics_choice == "🕵️‍♂️ Transaction Monitoring":
        st.write("### Transaction Monitoring")
        if "is_fraudulent" in df.columns:
            fraudulent_transactions = df[df['is_fraudulent'] == True]
            if not fraudulent_transactions.empty:
                st.write("### Fraudulent Transactions:")
                st.write(fraudulent_transactions)
            else:
                st.write("No fraudulent transactions found.")
        else:
            st.warning("The dataset does not contain an 'is_fraudulent' column. Please verify the data.")
    elif analytics_choice == "🕵️‍♂️ Pseudonymous Addresses":
        st.write("### Pseudonymous Addresses")
        if "address" in df.columns:
            unique_addresses = df['address'].unique()
            st.write(f"Unique blockchain addresses (showing pseudonymous properties):")
            st.write(unique_addresses)
            generate_pdf(unique_addresses)  # Generate PDF here
        else:
            st.warning("The dataset does not contain an 'address' column. Please verify the data.")

# Function to handle user reporting and collaboration
def user_reporting_and_collaboration():
    st.write("### User Reporting and Collaboration")
    transaction_id = st.text_input("Transaction ID")
    reported_by = st.text_input("Reported By")
    notes = st.text_area("Notes")

    if st.button("Submit Report"):
        if transaction_id and reported_by and notes:
            reports = load_reports()
            reports.append({
                "transaction_id": transaction_id,
                "reported_by": reported_by,
                "notes": notes,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            save_reports(reports)
            st.success("Report submitted successfully!")
        else:
            st.error("Please fill all the fields before submitting.")

    # Display submitted reports
    reports = load_reports()
    if reports:
        st.write("### Submitted Reports")
        st.table(reports)

# Function to generate a PDF with the unique addresses in A4 format
def generate_pdf(addresses):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    c.setFont("Helvetica", 12)
    c.drawString(30, height - 30, "Unique Blockchain Addresses (Pseudonymous Properties):")
    y_position = height - 50
    for address in addresses:
        c.drawString(30, y_position, address)
        y_position -= 20
        if y_position < 50:
            c.showPage()
            c.setFont("Helvetica", 12)
            c.drawString(30, height - 30, "Unique Blockchain Addresses (Pseudonymous Properties):")
            y_position = height - 50
    c.save()
    buffer.seek(0)
    pdf_data = buffer.read()
    st.download_button(
        label="Download Unique Addresses as PDF",
        data=pdf_data,
        file_name="unique_addresses.pdf",
        mime="application/pdf"
    )

    # Function to visualize transaction proportions and generate a report
def visualize_transaction_proportions_and_generate_report(df):
    st.title("📊 Visualization and Reporting Tools")
    
    # Visualize transaction type proportions as a pie chart
    if 'transaction_type' in df.columns:
        st.subheader("Transaction Proportions")
        transaction_counts = df['transaction_type'].value_counts().reset_index()
        transaction_counts.columns = ['transaction_type', 'count']
        import plotly.express as px
        fig = px.pie(transaction_counts, values='count', names='transaction_type', title='Transaction Type Proportions')
        st.plotly_chart(fig)
        
        # Generate PDF report
        st.subheader("Download Detailed Report")
        buffer = BytesIO()
        report = canvas.Canvas(buffer, pagesize=letter)
        report.drawString(100, 750, "Blockchain Analysis Report")
        report.drawString(100, 730, f"Total Transactions: {len(df)}")
        y_position = 700
        for index, row in transaction_counts.iterrows():
            report.drawString(100, y_position, f"{row['transaction_type']}: {row['count']} transactions")
            y_position -= 20
            if y_position < 50:  # Add a new page if needed
                report.showPage()
                y_position = 750
        report.save()
        buffer.seek(0)
        pdf_data = buffer.read()
        st.download_button(
            label="Download Report as PDF",
            data=pdf_data,
            file_name="transaction_report.pdf",
            mime="application/pdf"
        )
    else:
        st.warning("The dataset does not contain a 'transaction_type' column. Please upload a valid dataset.")


# Main application
def main():
    st.set_page_config(
        page_title="Blockchain Analysis Tool",
        page_icon="🔗",
        layout="wide",
        initial_sidebar_state="expanded"
        
    )

    menu = ["🏠 Home", "🔑 Login", "🔐 Register"]
    choice = st.sidebar.selectbox("Menu", menu)
    if "logged_in" in st.session_state and st.session_state.logged_in:
        user_dashboard(st.session_state.username)
    elif choice == "🏠 Home":
        home_page()
    elif choice == "🔑 Login":
        logged_in, username = login_user()
        if logged_in:
            user_dashboard(username)
    elif choice == "🔐 Register":
        register_user()

if __name__ == "__main__":
    if not load_user_data():
        random_users = {f"user{i}": f"password{i}" for i in range(1, 11)}
        save_user_data(random_users)
    main()
