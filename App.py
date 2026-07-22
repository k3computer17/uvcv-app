import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# Page Configuration
st.set_page_config(page_title="NIKA - Tax & Client Ledger", layout="wide")

# Custom CSS Styling
st.markdown("""
    <style>
    .main {
        background-color: #f4f6f9;
        font-family: 'Segoe UI', sans-serif;
    }
    h1, h2, h3 {
        color: #1a237e !important;
    }
    .stButton>button {
        background: linear-gradient(90deg, #1e88e5 0%, #1565c0 100%);
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 24px;
        font-weight: bold;
        font-size: 16px;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #1565c0 0%, #1e88e5 100%);
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🏢 NIKA - Client Database & Ledger System")

# Database Setup
conn = sqlite3.connect('nika_clients.db', check_same_thread=False)
c = conn.cursor()

# Create Tables
c.execute('''
    CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        father_name TEXT,
        pan_number TEXT,
        gst_number TEXT,
        mobile TEXT,
        address TEXT,
        annual_fee REAL DEFAULT 0,
        return_type TEXT,
        income_tax_status TEXT,
        gst_status TEXT,
        created_date TEXT
    )
''')

c.execute('''
    CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER,
        payment_date TEXT,
        amount_paid REAL,
        payment_mode TEXT,
        remarks TEXT,
        FOREIGN KEY(client_id) REFERENCES clients(id)
    )
''')
conn.commit()

# Sidebar Navigation
menu = [
    "➕ Add New Client", 
    "💵 Receive Payment",
    "🔍 Client Ledger & History", 
    "📊 Overall Business Report", 
    "🗑️ Delete Entry"
]
choice = st.sidebar.radio("NIKA Menu", menu)

# 1. Add New Client
if choice == "➕ Add New Client":
    st.subheader("📝 Register New Client Profile & Annual Fee")
    
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Client Full Name *")
        father_name = st.text_input("Father's Name")
        mobile = st.text_input("Mobile Number")
        pan_number = st.text_input("PAN Card Number")
        gst_number = st.text_input("GSTIN / GST Number")
        address = st.text_area("Address")

    with col2:
        annual_fee = st.number_input("Agreed Annual Fee (₹) *", min_value=0.0, step=500.0)
        return_type = st.selectbox("Return Type:", [
            "Income Tax Return (ITR)", 
            "GST Return (GSTR-1 / 3B)", 
            "Both (ITR + GST)", 
            "Accounting / Consultancy"
        ])
        income_tax_status = st.selectbox("Income Tax Status:", ["Pending", "Filed", "Not Applicable"])
        gst_status = st.selectbox("GST Return Status:", ["Pending", "Filed", "Not Applicable"])

    st.markdown("---")
    if st.button("💾 Save Client Profile"):
        if name.strip() == "":
            st.error("Please enter Client Name!")
        else:
            today_date = datetime.now().strftime("%Y-%m-%d")
            c.execute('''
                INSERT INTO clients 
                (name, father_name, pan_number, gst_number, mobile, address, annual_fee, return_type, income_tax_status, gst_status, created_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (name.strip(), father_name, pan_number.strip().upper(), gst_number.strip().upper(), mobile, address, annual_fee, return_type, income_tax_status, gst_status, today_date))
            conn.commit()
            st.success(f"✅ Client '{name}' saved successfully with Annual Fee ₹{annual_fee:,.2f}!")
            st.rerun()

# 2. Receive Payment
elif choice == "💵 Receive Payment":
    st.subheader("💵 Receive Fee Payment from Client")
    
    c.execute("SELECT id, name, pan_number, annual_fee FROM clients ORDER BY name ASC")
    client_rows = c.fetchall()
    
    if not client_rows:
        st.warning("No clients found. Please add a client first.")
    else:
        client_dict = {f"{row[1]} | PAN: {row[2]} (Fee: ₹{row[3]:,.2f})": row[0] for row in client_rows}
        selected_client_str = st.selectbox("Select Client:", list(client_dict.keys()))
        selected_client_id = client_dict[selected_client_str]
        
        c.execute("SELECT annual_fee FROM clients WHERE id = ?", (selected_client_id,))
        total_annual_fee = c.fetchone()[0]
        
        c.execute("SELECT SUM(amount_paid) FROM payments WHERE client_id = ?", (selected_client_id,))
        paid_res = c.fetchone()[0]
        total_paid = paid_res if paid_res else 0.0
        current_balance = total_annual_fee - total_paid
        
        st.info(f"📌 **Annual Fee:** ₹{total_annual_fee:,.2f} | **Total Paid:** ₹{total_paid:,.2f} | **Current Due:** ₹{current_balance:,.2f}")
        
        col1, col2 = st.columns(2)
        with col1:
            payment_amount = st.number_input("Amount Received (₹) *", min_value=0.0, step=100.0)
            payment_date = st.date_input("Payment Date", datetime.now()).strftime("%Y-%m-%d")
        
        with col2:
            payment_mode = st.selectbox("Payment Mode:", ["Cash", "Online / UPI", "Net Banking / Cheque"])
            remarks = st.text_input("Remarks / Receipt No.")

        st.markdown("---")
        if st.button("✅ Save Payment Entry"):
            if payment_amount <= 0:
                st.error("Please enter a valid amount!")
            else:
                c.execute('''
                    INSERT INTO payments (client_id, payment_date, amount_paid, payment_mode, remarks)
                    VALUES (?, ?, ?, ?, ?)
                ''', (selected_client_id, payment_date, payment_amount, payment_mode, remarks))
                conn.commit()
                st.success("✅ Payment recorded successfully!")
                st.rerun()

# 3. Client Ledger & History
elif choice == "🔍 Client Ledger & History":
    st.subheader("🔍 Client Statement & Ledger")
    
    c.execute("SELECT id, name, pan_number, mobile FROM clients ORDER BY name ASC")
    client_list = c.fetchall()
    
    if client_list:
        client_options = {f"{c_row[1]} | PAN: {c_row[2]} | Mob: {c_row[3]}": c_row[0] for c_row in client_list}
        selected_client_label = st.selectbox("Search / Select Client:", list(client_options.keys()))
        client_id = client_options[selected_client_label]
        
        c.execute("SELECT * FROM clients WHERE id = ?", (client_id,))
        client_info = c.fetchone()
        annual_fee = client_info[7]
        
        df_payments = pd.read_sql_query('''
            SELECT payment_date as 'Date', amount_paid as 'Amount Paid (₹)', payment_mode as 'Mode', remarks as 'Remarks'
            FROM payments WHERE client_id = ? ORDER BY id ASC
        ''', conn, params=(client_id,))
        
        total_paid = df_payments['Amount Paid (₹)'].sum() if not df_payments.empty else 0.0
        remaining_balance = annual_fee - total_paid
        
        st.markdown("---")
        m1, m2, m3 = st.columns(3)
        m1.metric("Agreed Annual Fee", f"₹{annual_fee:,.2f}")
        m2.metric("Total Received", f"₹{total_paid:,.2f}")
        
        if remaining_balance > 0:
            m3.metric("Remaining Due", f"₹{remaining_balance:,.2f}")
        elif remaining_balance < 0:
            m3.metric("Advance Received", f"₹{abs(remaining_balance):,.2f}")
        else:
            m3.metric("Balance Clear", "₹0.00")

        st.markdown("---")
        st.markdown(f"### 📋 Payment Receipts History for {client_info[1]}:")
        
        if not df_payments.empty:
            st.dataframe(df_payments, use_container_width=True)
        else:
            st.warning("No payments recorded for this client yet.")

# 4. Overall Business Report
elif choice == "📊 Overall Business Report":
    st.subheader("📊 NIKA Business Financial Dashboard")
    
    df_clients = pd.read_sql_query("SELECT * FROM clients", conn)
    
    if df_clients.empty:
        st.info("No clients in database.")
    else:
        total_agreed = df_clients['annual_fee'].sum()
        total_collected = pd.read_sql_query("SELECT SUM(amount_paid) FROM payments", conn).iloc[0, 0]
        total_collected = total_collected if total_collected else 0.0
        total_outstanding = total_agreed - total_collected
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Clients", len(df_clients))
        c2.metric("Total Annual Agreed", f"₹{total_agreed:,.2f}")
        c3.metric("Total Collected", f"₹{total_collected:,.2f}")
        c4.metric("Total Outstanding", f"₹{total_outstanding:,.2f}")
        
        st.markdown("---")
        st.markdown("### 📋 Master Client Ledger")
        
        master_df = pd.read_sql_query('''
            SELECT 
                c.id as 'ID',
                c.name as 'Name',
                c.mobile as 'Mobile',
                c.pan_number as 'PAN',
                c.annual_fee as 'Annual Fee (₹)',
                COALESCE(SUM(p.amount_paid), 0) as 'Received (₹)',
                (c.annual_fee - COALESCE(SUM(p.amount_paid), 0)) as 'Due (₹)',
                c.income_tax_status as 'ITR Status',
                c.gst_status as 'GST Status'
            FROM clients c
            LEFT JOIN payments p ON c.id = p.client_id
            GROUP BY c.id
        ''', conn)
        
        st.dataframe(master_df, use_container_width=True)

# 5. Delete Entry
elif choice == "🗑️ Delete Entry":
    st.subheader("🗑️ Delete Client or Payment Entry")
    
    del_choice = st.radio("Select What to Delete:", ["Complete Client Profile", "Only Single Payment Entry"])
    
    if del_choice == "Complete Client Profile":
        c.execute("SELECT id, name, pan_number FROM clients")
        recs = c.fetchall()
        if recs:
            opts = {f"ID: {r[0]} | {r[1]} | PAN: {r[2]}": r[0] for r in recs}
            sel = st.selectbox("Select Client:", list(opts.keys()))
            if st.button("❌ Delete Client & All Records"):
                cid = opts[sel]
                c.execute("DELETE FROM payments WHERE client_id = ?", (cid,))
                c.execute("DELETE FROM clients WHERE id = ?", (cid,))
                conn.commit()
                st.success("Record deleted successfully!")
                st.rerun()
    else:
        df_p = pd.read_sql_query('''
            SELECT p.id as 'Payment ID', c.name as 'Name', p.payment_date as 'Date', p.amount_paid as 'Amount (₹)'
            FROM payments p JOIN clients c ON p.client_id = c.id ORDER BY p.id DESC
        ''', conn)
        if not df_p.empty:
            st.dataframe(df_p, use_container_width=True)
            p_id = st.number_input("Enter Payment ID to Delete:", min_value=1, step=1)
            if st.button("❌ Delete This Payment Entry"):
                c.execute("DELETE FROM payments WHERE id = ?", (p_id,))
                conn.commit()
                st.success("Payment record deleted!")
                st.rerun()
