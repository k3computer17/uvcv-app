import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# Page Configuration
st.set_page_config(page_title="NIKA - Tax & Financial Year System", layout="wide")

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

st.title("🏢 NIKA - Client Database & Financial Year System")

# Database Setup
conn = sqlite3.connect('nika_clients.db', check_same_thread=False)
c = conn.cursor()

# 1. Clients Master Table (With Username & Password Columns)
c.execute('''
    CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        father_name TEXT,
        pan_number TEXT,
        gst_number TEXT,
        mobile TEXT,
        address TEXT,
        portal_username TEXT,
        portal_password TEXT,
        created_date TEXT
    )
''')

# 2. Client Year-wise Fee & Return Status Table
c.execute('''
    CREATE TABLE IF NOT EXISTS client_years (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER,
        financial_year TEXT,
        annual_fee REAL DEFAULT 0,
        return_type TEXT,
        income_tax_status TEXT,
        gst_status TEXT,
        FOREIGN KEY(client_id) REFERENCES clients(id)
    )
''')

# 3. Payments Table
c.execute('''
    CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER,
        financial_year TEXT,
        payment_date TEXT,
        amount_paid REAL,
        payment_mode TEXT,
        remarks TEXT,
        FOREIGN KEY(client_id) REFERENCES clients(id)
    )
''')
conn.commit()

# 10 Financial Years List
FY_LIST = [
    "2020-2021", "2021-2022", "2022-2023", "2023-2024", 
    "2024-2025", "2025-2026", "2026-2027", "2027-2028", 
    "2028-2029", "2029-2030", "2030-2031"
]

# Sidebar Navigation
menu = [
    "➕ Add New Client", 
    "📅 Add / Update Financial Year Fee",
    "💵 Receive Payment",
    "🔍 Client Ledger & Passwords", 
    "📊 Overall Business Report", 
    "🗑️ Delete Entry"
]
choice = st.sidebar.radio("NIKA Menu", menu)

# 1. Add New Client
if choice == "➕ Add New Client":
    st.subheader("📝 Register New Client Profile & Portal Credentials")
    
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Client Full Name *")
        father_name = st.text_input("Father's Name")
        mobile = st.text_input("Mobile Number")
        address = st.text_area("Address")
    
    with col2:
        pan_number = st.text_input("PAN Card Number")
        gst_number = st.text_input("GSTIN / GST Number")
        st.markdown("---")
        st.markdown("🔐 **ITR / GST Portal Login Info:**")
        portal_username = st.text_input("Portal User Name / ID")
        portal_password = st.text_input("Portal Password", type="default")

    st.markdown("---")
    st.markdown("### 📅 Financial Year Setup")
    col3, col4 = st.columns(2)
    with col3:
        fin_year = st.selectbox("Select Financial Year (FY):", FY_LIST, index=6) # Default 2026-2027
        annual_fee = st.number_input("Agreed Annual Fee (₹) *", min_value=0.0, step=500.0)
    
    with col4:
        return_type = st.selectbox("Return Type:", [
            "Income Tax Return (ITR)", 
            "GST Return (GSTR-1 / 3B)", 
            "Both (ITR + GST)", 
            "Accounting / Consultancy"
        ])
        income_tax_status = st.selectbox("Income Tax Status:", ["Pending", "Filed", "Not Applicable"])
        gst_status = st.selectbox("GST Return Status:", ["Pending", "Filed", "Not Applicable"])

    if st.button("💾 Save Client Profile"):
        if name.strip() == "":
            st.error("Please enter Client Name!")
        else:
            today_date = datetime.now().strftime("%Y-%m-%d")
            c.execute('''
                INSERT INTO clients (name, father_name, pan_number, gst_number, mobile, address, portal_username, portal_password, created_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (name.strip(), father_name, pan_number.strip().upper(), gst_number.strip().upper(), mobile, address, portal_username, portal_password, today_date))
            
            client_id = c.lastrowid
            
            c.execute('''
                INSERT INTO client_years (client_id, financial_year, annual_fee, return_type, income_tax_status, gst_status)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (client_id, fin_year, annual_fee, return_type, income_tax_status, gst_status))
            
            conn.commit()
            st.success(f"✅ Client '{name}' saved successfully with Login details for FY {fin_year}!")
            st.rerun()

# 2. Add / Update Financial Year Fee
elif choice == "📅 Add / Update Financial Year Fee":
    st.subheader("📅 Manage Year-wise Fee & Return Status (10 Years)")
    
    c.execute("SELECT id, name, pan_number FROM clients ORDER BY name ASC")
    client_rows = c.fetchall()
    
    if not client_rows:
        st.warning("No clients found.")
    else:
        client_dict = {f"{row[1]} | PAN: {row[2]}": row[0] for row in client_rows}
        selected_client_str = st.selectbox("Select Client:", list(client_dict.keys()))
        selected_client_id = client_dict[selected_client_str]
        
        fin_year = st.selectbox("Select Financial Year:", FY_LIST, index=6)
        
        c.execute("SELECT * FROM client_years WHERE client_id = ? AND financial_year = ?", (selected_client_id, fin_year))
        existing_rec = c.fetchone()
        
        default_fee = existing_rec[3] if existing_rec else 0.0
        default_ret = existing_rec[4] if existing_rec else "Income Tax Return (ITR)"
        default_itr = existing_rec[5] if existing_rec else "Pending"
        default_gst = existing_rec[6] if existing_rec else "Pending"
        
        col1, col2 = st.columns(2)
        with col1:
            annual_fee = st.number_input(f"Annual Fee for FY {fin_year} (₹):", min_value=0.0, value=float(default_fee), step=500.0)
            return_type = st.selectbox("Return Type:", [
                "Income Tax Return (ITR)", 
                "GST Return (GSTR-1 / 3B)", 
                "Both (ITR + GST)", 
                "Accounting / Consultancy"
            ], index=0)

        with col2:
            income_tax_status = st.selectbox("ITR Status:", ["Pending", "Filed", "Not Applicable"])
            gst_status = st.selectbox("GST Status:", ["Pending", "Filed", "Not Applicable"])

        if st.button("💾 Save / Update Year Details"):
            if existing_rec:
                c.execute('''
                    UPDATE client_years 
                    SET annual_fee = ?, return_type = ?, income_tax_status = ?, gst_status = ?
                    WHERE client_id = ? AND financial_year = ?
                ''', (annual_fee, return_type, income_tax_status, gst_status, selected_client_id, fin_year))
            else:
                c.execute('''
                    INSERT INTO client_years (client_id, financial_year, annual_fee, return_type, income_tax_status, gst_status)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (selected_client_id, fin_year, annual_fee, return_type, income_tax_status, gst_status))
            
            conn.commit()
            st.success(f"✅ Fee & Status updated for FY {fin_year}!")
            st.rerun()

# 3. Receive Payment
elif choice == "💵 Receive Payment":
    st.subheader("💵 Receive Fee Payment")
    
    c.execute("SELECT id, name, pan_number FROM clients ORDER BY name ASC")
    client_rows = c.fetchall()
    
    if not client_rows:
        st.warning("No clients found.")
    else:
        client_dict = {f"{row[1]} | PAN: {row[2]}": row[0] for row in client_rows}
        selected_client_str = st.selectbox("Select Client:", list(client_dict.keys()))
        selected_client_id = client_dict[selected_client_str]
        
        fin_year = st.selectbox("Select Financial Year:", FY_LIST, index=6)
        
        c.execute("SELECT annual_fee FROM client_years WHERE client_id = ? AND financial_year = ?", (selected_client_id, fin_year))
        fee_res = c.fetchone()
        total_annual_fee = fee_res[0] if fee_res else 0.0
        
        c.execute("SELECT SUM(amount_paid) FROM payments WHERE client_id = ? AND financial_year = ?", (selected_client_id, fin_year))
        paid_res = c.fetchone()[0]
        total_paid = paid_res if paid_res else 0.0
        current_balance = total_annual_fee - total_paid
        
        st.info(f"📌 **FY {fin_year} Fee:** ₹{total_annual_fee:,.2f} | **Total Paid:** ₹{total_paid:,.2f} | **Current Due:** ₹{current_balance:,.2f}")
        
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
                    INSERT INTO payments (client_id, financial_year, payment_date, amount_paid, payment_mode, remarks)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (selected_client_id, fin_year, payment_date, payment_amount, payment_mode, remarks))
                conn.commit()
                st.success("✅ Payment recorded successfully!")
                st.rerun()

# 4. Client Ledger & Passwords
elif choice == "🔍 Client Ledger & Passwords":
    st.subheader("🔍 Client Statement & Login Credentials")
    
    c.execute("SELECT id, name, pan_number, mobile FROM clients ORDER BY name ASC")
    client_list = c.fetchall()
    
    if client_list:
        client_options = {f"{c_row[1]} | PAN: {c_row[2]} | Mob: {c_row[3]}": c_row[0] for c_row in client_list}
        selected_client_label = st.selectbox("Search / Select Client:", list(client_options.keys()))
        client_id = client_options[selected_client_label]
        
        c.execute("SELECT * FROM clients WHERE id = ?", (client_id,))
        c_info = c.fetchone()
        
        # Display Credentials Box
        st.success(f"🔑 **Portal Username:** `{c_info[7] if c_info[7] else 'N/A'}` | 🔒 **Portal Password:** `{c_info[8] if c_info[8] else 'N/A'}`")
        
        fin_year = st.selectbox("Select Financial Year:", FY_LIST, index=6)
        
        c.execute("SELECT annual_fee FROM client_years WHERE client_id = ? AND financial_year = ?", (client_id, fin_year))
        year_info = c.fetchone()
        annual_fee = year_info[0] if year_info else 0.0
        
        df_payments = pd.read_sql_query('''
            SELECT payment_date as 'Date', amount_paid as 'Amount Paid (₹)', payment_mode as 'Mode', remarks as 'Remarks'
            FROM payments WHERE client_id = ? AND financial_year = ? ORDER BY id ASC
        ''', conn, params=(client_id, fin_year))
        
        total_paid = df_payments['Amount Paid (₹)'].sum() if not df_payments.empty else 0.0
        remaining_balance = annual_fee - total_paid
        
        st.markdown("---")
        m1, m2, m3 = st.columns(3)
        m1.metric(f"FY {fin_year} Agreed Fee", f"₹{annual_fee:,.2f}")
        m2.metric("Total Received", f"₹{total_paid:,.2f}")
        
        if remaining_balance > 0:
            m3.metric("Remaining Due", f"₹{remaining_balance:,.2f}")
        elif remaining_balance < 0:
            m3.metric("Advance Received", f"₹{abs(remaining_balance):,.2f}")
        else:
            m3.metric("Balance Clear", "₹0.00")

        st.markdown("---")
        st.markdown(f"### 📋 Payment History for FY {fin_year}:")
        if not df_payments.empty:
            st.dataframe(df_payments, use_container_width=True)
        else:
            st.warning("No payments recorded for this financial year yet.")
            
        with st.expander("📝 Update Portal Username & Password"):
            with st.form("update_creds"):
                u_name = st.text_input("Username", value=c_info[7] if c_info[7] else "")
                u_pass = st.text_input("Password", value=c_info[8] if c_info[8] else "")
                if st.form_submit_button("Update Credentials"):
                    c.execute("UPDATE clients SET portal_username = ?, portal_password = ? WHERE id = ?", (u_name, u_pass, client_id))
                    conn.commit()
                    st.success("Credentials updated successfully!")
                    st.rerun()

# 5. Overall Business Report
elif choice == "📊 Overall Business Report":
    st.subheader("📊 NIKA Business Financial Dashboard")
    
    selected_fy = st.selectbox("Filter Report by Financial Year:", FY_LIST, index=6)
    
    master_df = pd.read_sql_query('''
        SELECT 
            c.id as 'ID',
            c.name as 'Name',
            c.mobile as 'Mobile',
            c.pan_number as 'PAN',
            c.portal_username as 'Portal User',
            c.portal_password as 'Portal Pass',
            COALESCE(cy.annual_fee, 0) as 'Annual Fee (₹)',
            COALESCE(SUM(p.amount_paid), 0) as 'Received (₹)',
            (COALESCE(cy.annual_fee, 0) - COALESCE(SUM(p.amount_paid), 0)) as 'Due (₹)'
        FROM clients c
        LEFT JOIN client_years cy ON c.id = cy.client_id AND cy.financial_year = ?
        LEFT JOIN payments p ON c.id = p.client_id AND p.financial_year = ?
        GROUP BY c.id
    ''', conn, params=(selected_fy, selected_fy))
    
    if master_df.empty:
        st.info("No data available.")
    else:
        total_agreed = master_df['Annual Fee (₹)'].sum()
        total_collected = master_df['Received (₹)'].sum()
        total_outstanding = master_df['Due (₹)'].sum()
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Clients", len(master_df))
        c2.metric(f"FY {selected_fy} Total Fee", f"₹{total_agreed:,.2f}")
        c3.metric("Total Collected", f"₹{total_collected:,.2f}")
        c4.metric("Total Outstanding", f"₹{total_outstanding:,.2f}")
        
        st.markdown("---")
        st.markdown(f"### 📋 Master Client Ledger & Credentials (FY {selected_fy})")
        st.dataframe(master_df, use_container_width=True)

# 6. Delete Entry
elif choice == "🗑️ Delete Entry":
    st.subheader("🗑️ Delete Record")
    
    del_choice = st.radio("Select Option:", ["Delete Single Payment Entry", "Delete Client Profile"])
    
    if del_choice == "Delete Client Profile":
        c.execute("SELECT id, name, pan_number FROM clients")
        recs = c.fetchall()
        if recs:
            opts = {f"ID: {r[0]} | {r[1]} | PAN: {r[2]}": r[0] for r in recs}
            sel = st.selectbox("Select Client:", list(opts.keys()))
            if st.button("❌ Delete Client Completely"):
                cid = opts[sel]
                c.execute("DELETE FROM payments WHERE client_id = ?", (cid,))
                c.execute("DELETE FROM client_years WHERE client_id = ?", (cid,))
                c.execute("DELETE FROM clients WHERE id = ?", (cid,))
                conn.commit()
                st.success("Client completely deleted!")
                st.rerun()
    else:
        df_p = pd.read_sql_query('''
            SELECT p.id as 'Payment ID', c.name as 'Name', p.financial_year as 'FY', p.payment_date as 'Date', p.amount_paid as 'Amount (₹)'
            FROM payments p JOIN clients c ON p.client_id = c.id ORDER BY p.id DESC
        ''', conn)
        if not df_p.empty:
            st.dataframe(df_p, use_container_width=True)
            p_id = st.number_input("Enter Payment ID to Delete:", min_value=1, step=1)
            if st.button("❌ Delete Payment"):
                c.execute("DELETE FROM payments WHERE id = ?", (p_id,))
                conn.commit()
                st.success("Payment entry deleted!")
                st.rerun()
