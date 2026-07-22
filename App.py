import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import urllib.parse

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

st.title("🏢 NIKA - Client Management & WhatsApp Reminder System")

# Database Setup
conn = sqlite3.connect('nika_clients_v2.db', check_same_thread=False)
c = conn.cursor()

# Migration: Check and rename columns if needed
c.execute("PRAGMA table_info(clients)")
columns = [col[1] for col in c.fetchall()]

if 'itr_username' not in columns and 'portal_username' in columns:
    c.execute("ALTER TABLE clients RENAME COLUMN portal_username TO itr_username")
if 'itr_password' not in columns and 'portal_password' in columns:
    c.execute("ALTER TABLE clients RENAME COLUMN portal_password TO itr_password")

# 1. Clients Master Table
c.execute('''
    CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        father_name TEXT,
        pan_number TEXT,
        mobile TEXT,
        address TEXT,
        itr_username TEXT,
        itr_password TEXT,
        created_date TEXT
    )
''')

# 2. Client GST Table
c.execute('''
    CREATE TABLE IF NOT EXISTS client_gst (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER,
        gst_number TEXT,
        gst_username TEXT,
        gst_password TEXT,
        trade_name TEXT,
        FOREIGN KEY(client_id) REFERENCES clients(id)
    )
''')

# 3. Client Years Table
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

# 4. Payments Table
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

# Financial Years List
FY_LIST = [
    "2020-2021", "2021-2022", "2022-2023", "2023-2024", 
    "2024-2025", "2025-2026", "2026-2027", "2027-2028", 
    "2028-2029", "2029-2030", "2030-2031"
]

# Sidebar Navigation
menu = [
    "➕ Add New Client", 
    "✏️ Edit Client Profile",
    "📅 Add / Update Financial Year Fee",
    "💵 Receive Payment",
    "🔍 Client Ledger & Credentials", 
    "📊 Overall Business Report", 
    "🗑️ Delete Entry"
]
choice = st.sidebar.radio("NIKA Menu", menu)

if "num_gst_fields" not in st.session_state:
    st.session_state.num_gst_fields = 1

# Helper function for Universal WhatsApp Link
def create_whatsapp_link(client_mobile, message):
    if not client_mobile:
        return None
    clean_mobile = "".join(filter(str.isdigit, str(client_mobile)))
    if len(clean_mobile) == 10:
        clean_mobile = "91" + clean_mobile
    encoded_msg = urllib.parse.quote(message)
    return f"https://api.whatsapp.com/send?phone={clean_mobile}&text={encoded_msg}"

MY_CONTACT = "8358013017"

# 1. Add New Client Profile
if choice == "➕ Add New Client":
    st.subheader("📝 Register New Client Profile")
    
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Client Full Name *")
        father_name = st.text_input("Father's Name")
        mobile = st.text_input("Mobile Number")
        address = st.text_area("Address")
    
    with col2:
        pan_number = st.text_input("PAN Card Number")
        st.markdown("🔐 **Income Tax (ITR) Portal Credentials:**")
        itr_username = st.text_input("ITR Portal User ID / PAN")
        itr_password = st.text_input("ITR Portal Password", type="password")

    st.markdown("---")
    st.markdown("### 🏬 GST Details")
    
    # Checkbox option to enable/disable GST details input
    enable_gst = st.checkbox("Does this client have GST Registration? (Enable GST Input)", value=False)
    
    gst_data = []
    if enable_gst:
        st.info("💡 GST Details enabled. Enter the registration details below:")
        for i in range(st.session_state.num_gst_fields):
            st.markdown(f"**GST Registration #{i+1}:**")
            gc1, gc2, gc3, gc4 = st.columns(4)
            with gc1:
                g_num = st.text_input(f"GSTIN / GST Number #{i+1}", key=f"gst_num_{i}")
            with gc2:
                g_user = st.text_input(f"GST User ID #{i+1}", key=f"gst_user_{i}")
            with gc3:
                g_pass = st.text_input(f"GST Password #{i+1}", key=f"gst_pass_{i}", type="password")
            with gc4:
                g_trade = st.text_input(f"Trade/Firm Name #{i+1}", key=f"gst_trade_{i}")
            
            if g_num.strip():
                gst_data.append({
                    "gst_number": g_num.strip().upper(),
                    "gst_username": g_user.strip(),
                    "gst_password": g_pass.strip(),
                    "trade_name": g_trade.strip()
                })
        
        b_col1, _ = st.columns([1, 4])
        with b_col1:
            if st.button("➕ Add Another GST Number"):
                st.session_state.num_gst_fields += 1
                st.rerun()

    st.markdown("---")
    st.markdown("### 📅 Financial Year Setup")
    col3, col4 = st.columns(2)
    with col3:
        fin_year = st.selectbox("Select Financial Year (FY):", FY_LIST, index=6)
        annual_fee = st.number_input("Agreed Annual Fee (₹) *", min_value=0.0, step=500.0)
    
    with col4:
        return_type = st.selectbox("Return Type:", [
            "Income Tax Return (ITR)", 
            "GST Return (GSTR-1 / 3B)", 
            "Both (ITR + GST)", 
            "Accounting / Consultancy"
        ])
        income_tax_status = st.selectbox("Income Tax Status:", ["Pending", "Filed", "Not Applicable"])
        gst_status = st.selectbox("GST Return Status:", ["Pending", "Filed", "Not Applicable"] if enable_gst else ["Not Applicable", "Pending", "Filed"])

    if st.button("💾 Save Client Profile"):
        if name.strip() == "":
            st.error("Please enter Client Name!")
        else:
            today_date = datetime.now().strftime("%Y-%m-%d")
            c.execute('''
                INSERT INTO clients (name, father_name, pan_number, mobile, address, itr_username, itr_password, created_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (name.strip(), father_name, pan_number.strip().upper(), mobile, address, itr_username, itr_password, today_date))
            
            client_id = c.lastrowid
            
            if enable_gst:
                for gst_item in gst_data:
                    c.execute('''
                        INSERT INTO client_gst (client_id, gst_number, gst_username, gst_password, trade_name)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (client_id, gst_item["gst_number"], gst_item["gst_username"], gst_item["gst_password"], gst_item["trade_name"]))

            c.execute('''
                INSERT INTO client_years (client_id, financial_year, annual_fee, return_type, income_tax_status, gst_status)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (client_id, fin_year, annual_fee, return_type, income_tax_status, gst_status))
            
            conn.commit()
            st.session_state.num_gst_fields = 1
            st.success(f"✅ Client '{name}' saved successfully!")
            st.rerun()

# 2. Edit Client Profile
elif choice == "✏️ Edit Client Profile":
    st.subheader("✏️ Edit Client Details & Credentials")
    
    c.execute("SELECT id, name, pan_number, mobile FROM clients ORDER BY name ASC")
    client_rows = c.fetchall()
    
    if not client_rows:
        st.warning("No clients found.")
    else:
        client_dict = {f"{row[1]} | PAN: {row[2]} | Mob: {row[3]}": row[0] for row in client_rows}
        selected_client_str = st.selectbox("Select Client to Edit:", list(client_dict.keys()))
        selected_client_id = client_dict[selected_client_str]
        
        c.execute("SELECT * FROM clients WHERE id = ?", (selected_client_id,))
        c_info = c.fetchone()
        
        st.markdown("### 👤 Basic Profile & ITR Credentials")
        col1, col2 = st.columns(2)
        with col1:
            edit_name = st.text_input("Client Full Name *", value=c_info[1] if c_info[1] else "")
            edit_father = st.text_input("Father's Name", value=c_info[2] if c_info[2] else "")
            edit_mobile = st.text_input("Mobile Number", value=c_info[4] if c_info[4] else "")
            edit_address = st.text_area("Address", value=c_info[5] if c_info[5] else "")
        
        with col2:
            edit_pan = st.text_input("PAN Card Number", value=c_info[3] if c_info[3] else "")
            st.markdown("🔐 **ITR Credentials:**")
            edit_itr_user = st.text_input("ITR Portal User ID", value=c_info[6] if c_info[6] else "")
            edit_itr_pass = st.text_input("ITR Portal Password", value=c_info[7] if c_info[7] else "")
        
        if st.button("💾 Update Basic Details"):
            c.execute('''
                UPDATE clients 
                SET name = ?, father_name = ?, pan_number = ?, mobile = ?, address = ?, itr_username = ?, itr_password = ?
                WHERE id = ?
            ''', (edit_name.strip(), edit_father, edit_pan.strip().upper(), edit_mobile, edit_address, edit_itr_user, edit_itr_pass, selected_client_id))
            conn.commit()
            st.success("✅ Basic Profile & ITR Details updated successfully!")
            st.rerun()

        st.markdown("---")
        st.markdown("### 🏬 Manage GST Details")
        
        c.execute("SELECT id, gst_number, gst_username, gst_password, trade_name FROM client_gst WHERE client_id = ?", (selected_client_id,))
        gst_records = c.fetchall()
        
        has_existing_gst = len(gst_records) > 0
        enable_gst_edit = st.checkbox("Enable/Manage GST Registration for this client", value=has_existing_gst)
        
        if enable_gst_edit:
            if gst_records:
                for g_rec in gst_records:
                    g_id, g_num, g_user, g_pass, g_trade = g_rec
                    with st.expander(f"✏️ Edit GST: {g_num} ({g_trade if g_trade else 'No Trade Name'})"):
                        e_g1, e_g2, e_g3, e_g4 = st.columns(4)
                        with e_g1:
                            up_g_num = st.text_input("GSTIN", value=g_num if g_num else "", key=f"e_gnum_{g_id}")
                        with e_g2:
                            up_g_user = st.text_input("User ID", value=g_user if g_user else "", key=f"e_guser_{g_id}")
                        with e_g3:
                            up_g_pass = st.text_input("Password", value=g_pass if g_pass else "", key=f"e_gpass_{g_id}")
                        with e_g4:
                            up_g_trade = st.text_input("Trade Name", value=g_trade if g_trade else "", key=f"e_gtrade_{g_id}")
                        
                        b1, b2 = st.columns([1, 1])
                        with b1:
                            if st.button("Save GST Changes", key=f"save_g_{g_id}"):
                                c.execute('''
                                    UPDATE client_gst 
                                    SET gst_number = ?, gst_username = ?, gst_password = ?, trade_name = ?
                                    WHERE id = ?
                                ''', (up_g_num.strip().upper(), up_g_user, up_g_pass, up_g_trade, g_id))
                                conn.commit()
                                st.success("GST details updated!")
                                st.rerun()
                        with b2:
                            if st.button("❌ Remove GST", key=f"del_g_{g_id}"):
                                c.execute("DELETE FROM client_gst WHERE id = ?", (g_id,))
                                conn.commit()
                                st.success("GST entry removed!")
                                st.rerun()
            
            st.markdown("➕ **Add New GST Entry:**")
            a_col1, a_col2, a_col3, a_col4 = st.columns(4)
            with a_col1:
                new_gnum = st.text_input("New GSTIN", key="new_add_gnum")
            with a_col2:
                new_guser = st.text_input("New GST User ID", key="new_add_guser")
            with a_col3:
                new_gpass = st.text_input("New GST Password", key="new_add_gpass")
            with a_col4:
                new_gtrd = st.text_input("New Trade Name", key="new_add_gtrd")
                
            if st.button("💾 Save New GST Number"):
                if new_gnum.strip():
                    c.execute('''
                        INSERT INTO client_gst (client_id, gst_number, gst_username, gst_password, trade_name)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (selected_client_id, new_gnum.strip().upper(), new_guser, new_gpass, new_gtrd))
                    conn.commit()
                    st.success("New GST Registration added!")
                    st.rerun()
                else:
                    st.error("Please enter a GSTIN!")

# 3. Add / Update Financial Year Fee
elif choice == "📅 Add / Update Financial Year Fee":
    st.subheader("📅 Manage Year-wise Fee & Return Status")
    
    c.execute("SELECT id, name, pan_number, mobile FROM clients ORDER BY name ASC")
    client_rows = c.fetchall()
    
    if not client_rows:
        st.warning("No clients found.")
    else:
        client_dict = {f"{row[1]} | PAN: {row[2]}": (row[0], row[1], row[3]) for row in client_rows}
        selected_client_str = st.selectbox("Select Client:", list(client_dict.keys()))
        selected_client_id, client_name, client_mobile = client_dict[selected_client_str]
        
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

            # Auto WhatsApp Confirmation Link for Return Filing Status
            if income_tax_status == "Filed" or gst_status == "Filed":
                msg_filed = f"नमस्ते {client_name} जी,\n\nआपका वित्तीय वर्ष {fin_year} का रिटर्न सफलतापूर्वक फाइल (Filed) कर दिया गया है।\n\nNIKA Tax Services की सेवाओं का उपयोग करने के लिए धन्यवाद!\n\nसंपर्क: {MY_CONTACT}"
                url_filed = create_whatsapp_link(client_mobile, msg_filed)
                if url_filed:
                    st.info("📲 क्लाइंट को रिटर्न फाइलिंग की व्हाट्सएप सूचना भेजें:")
                    st.link_button("💬 Send Return Filed Confirmation on WhatsApp", url_filed, use_container_width=True)

# 4. Receive Payment
elif choice == "💵 Receive Payment":
    st.subheader("💵 Receive Fee Payment")
    
    c.execute("SELECT id, name, pan_number, mobile FROM clients ORDER BY name ASC")
    client_rows = c.fetchall()
    
    if not client_rows:
        st.warning("No clients found.")
    else:
        client_dict = {f"{row[1]} | PAN: {row[2]}": (row[0], row[1], row[3]) for row in client_rows}
        selected_client_str = st.selectbox("Select Client:", list(client_dict.keys()))
        selected_client_id, client_name, client_mobile = client_dict[selected_client_str]
        
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
                
                new_balance = current_balance - payment_amount
                st.success(f"✅ ₹{payment_amount:,.2f} Payment recorded successfully!")

                # Auto WhatsApp Payment Receipt Link
                msg_receipt = f"नमस्ते {client_name} जी,\n\nवित्तीय वर्ष {fin_year} के लिए आपका ₹{payment_amount:,.2f} का पेमेंट प्राप्त हो गया है।\n\n📌 **पेमेंट मोड:** {payment_mode}\n📌 **बकाया राशि (Remaining Due):** ₹{new_balance:,.2f}\n\nधन्यवाद!\n- NIKA Tax Services\nसंपर्क: {MY_CONTACT}"
                url_receipt = create_whatsapp_link(client_mobile, msg_receipt)
                
                if url_receipt:
                    st.info("📲 क्लाइंट को पेमेंट रसीद व्हाट्सएप पर भेजने के लिए नीचे क्लिक करें:")
                    st.link_button("💬 Send Payment Receipt on WhatsApp", url_receipt, use_container_width=True)

# 5. Client Ledger, Credentials & WhatsApp Reminders
elif choice == "🔍 Client Ledger & Credentials":
    st.subheader("🔍 Client Statement & Quick WhatsApp Reminders")
    
    c.execute("SELECT id, name, pan_number, mobile, itr_username, itr_password FROM clients ORDER BY name ASC")
    client_list = c.fetchall()
    
    if client_list:
        client_options = {f"{c_row[1]} | PAN: {c_row[2]} | Mob: {c_row[3] if c_row[3] else 'N/A'}": c_row[0] for c_row in client_list}
        selected_client_label = st.selectbox("Search / Select Client:", list(client_options.keys()))
        client_id = client_options[selected_client_label]
        
        c.execute("SELECT name, mobile, itr_username, itr_password FROM clients WHERE id = ?", (client_id,))
        c_info = c.fetchone()
        
        client_name = c_info[0] if c_info[0] else "Client"
        client_mobile = c_info[1] if c_info[1] else ""
        itr_user = c_info[2] if c_info[2] else "N/A"
        itr_pass = c_info[3] if c_info[3] else "N/A"
        
        st.success(f"🔑 **ITR User ID:** `{itr_user}` | 🔒 **ITR Password:** `{itr_pass}`")
        
        c.execute("SELECT gst_number, gst_username, gst_password, trade_name FROM client_gst WHERE client_id = ?", (client_id,))
        gst_records = c.fetchall()
        
        if gst_records:
            st.markdown("### 🏬 GST Credentials:")
            for g_rec in gst_records:
                st.info(f"📌 **Trade Name:** {g_rec[3] if g_rec[3] else 'N/A'} | **GSTIN:** `{g_rec[0]}`\n\n🔑 **User ID:** `{g_rec[1]}` | 🔒 **Password:** `{g_rec[2]}`")

        fin_year = st.selectbox("Select Financial Year:", FY_LIST, index=6)
        
        c.execute("SELECT annual_fee, income_tax_status, gst_status FROM client_years WHERE client_id = ? AND financial_year = ?", (client_id, fin_year))
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
        m1.metric(f"FY {fin_year} Fee", f"₹{annual_fee:,.2f}")
        m2.metric("Total Received", f"₹{total_paid:,.2f}")
        m3.metric("Remaining Due", f"₹{remaining_balance:,.2f}" if remaining_balance > 0 else "₹0.00")

        # Ready-made WhatsApp Options Section
        st.markdown("---")
        st.markdown("### 📲 Choose Reminder Option to Send on WhatsApp:")
        
        if not client_mobile or str(client_mobile).strip() == "":
            st.error("⚠️ Client Mobile Number is missing! Please edit client profile to add mobile number.")
        else:
            r1, r2 = st.columns(2)
            
            with r1:
                # Option 1: Payment Due Message
                msg_pay = f"नमस्ते {client_name} जी,\n\nआपका वित्तीय वर्ष {fin_year} का टैक्स/अकाउंटिंग फ़ीस में ₹{remaining_balance:,.2f} का भुगतान अभी तक नहीं हुआ है।\n\nकृपया जल्द से जल्द भुगतान करने का कष्ट करें।\n\nसंपर्क: {MY_CONTACT}\nधन्यवाद!\n- NIKA Tax Services"
                url_pay = create_whatsapp_link(client_mobile, msg_pay)
                st.markdown("#### Option 1: Payment Reminder")
                st.caption(f"**मैसेज Preview:** ₹{remaining_balance:,.2f} का भुगतान नहीं हुआ है...")
                st.link_button("💬 1. Send Payment Pending Warning", url_pay, use_container_width=True)

                st.markdown("---")

                # Option 3: Both Payment & Return Message
                msg_both = f"नमस्ते {client_name} जी,\n\nआपका वित्तीय वर्ष {fin_year} का टैक्स रिटर्न भी नहीं भरा गया है और ₹{remaining_balance:,.2f} का पेमेंट भी बकाया है।\n\nकृपया डॉक्युमेंट्स भेजकर भुगतान पूर्ण करें।\n\nसंपर्क: {MY_CONTACT}\nधन्यवाद!\n- NIKA Tax Services"
                url_both = create_whatsapp_link(client_mobile, msg_both)
                st.markdown("#### Option 3: Both Payment & Return Pending")
                st.caption(f"**मैसेज Preview:** रिटर्न नहीं भरा है और ₹{remaining_balance:,.2f} पेमेंट भी बकाया है...")
                st.link_button("⚠️ 3. Send Payment + Return Both Pending", url_both, use_container_width=True)

            with r2:
                # Option 2: Return Pending Message
                msg_ret = f"नमस्ते {client_name} जी,\n\nआपका वित्तीय वर्ष {fin_year} का टैक्स/GST रिटर्न अभी तक नहीं भरा गया है क्योंकि आपके दस्तावेज़ (Documents) पेंडिंग हैं।\n\nकृपया जल्द से जल्द दस्तावेज़ भेजने का कष्ट करें।\n\nसंपर्क: {MY_CONTACT}\nधन्यवाद!\n- NIKA Tax Services"
                url_ret = create_whatsapp_link(client_mobile, msg_ret)
                st.markdown("#### Option 2: Return Documents Pending")
                st.caption("**मैसेज Preview:** आपका रिटर्न अभी तक नहीं भरा गया है...")
                st.link_button("📄 2. Send Return/Docs Pending Warning", url_ret, use_container_width=True)

                st.markdown("---")

                # Option 4: Custom Message Input
                st.markdown("#### Option 4: Write Custom Message")
                custom_txt = st.text_input("लिखें जो मैसेज आप भेजना चाहते हैं:", value=f"नमस्ते {client_name} जी, ")
                url_custom = create_whatsapp_link(client_mobile, custom_txt)
                st.link_button("✏️ 4. Send Custom Message", url_custom, use_container_width=True)

        st.markdown("---")
        st.markdown(f"### 📋 Payment History for FY {fin_year}:")
        if not df_payments.empty:
            st.dataframe(df_payments, use_container_width=True)
        else:
            st.warning("No payments recorded for this financial year yet.")

# 6. Overall Business Report
elif choice == "📊 Overall Business Report":
    st.subheader("📊 NIKA Business Financial Dashboard")
    
    selected_fy = st.selectbox("Filter Report by Financial Year:", FY_LIST, index=6)
    
    master_df = pd.read_sql_query('''
        SELECT 
            c.id as 'ID',
            c.name as 'Name',
            c.mobile as 'Mobile',
            c.pan_number as 'PAN',
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
        st.markdown(f"### 📋 Master Client Ledger (FY {selected_fy})")
        st.dataframe(master_df, use_container_width=True)

# 7. Delete Entry
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
                c.execute("DELETE FROM client_gst WHERE client_id = ?", (cid,))
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
