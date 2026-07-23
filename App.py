import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# Page Configuration
st.set_page_config(page_title="NIKA & Shri Charbhuja Accountancy System", layout="wide")

# Custom CSS Styling (Includes Print Styles)
st.markdown("""
    <style>
    .main {
        background-color: #f4f6f9;
        font-family: 'Segoe UI', sans-serif;
    }
    h1, h2, h3 {
        color: #1a237e !important;
    }
    .main-header {
        text-align: center;
        color: #1a237e;
        border-bottom: 2px solid #1a237e;
        padding-bottom: 10px;
        margin-bottom: 20px;
    }
    .sub-header {
        text-align: center;
        color: #333;
        font-weight: 600;
        margin-bottom: 15px;
    }
    .section-title {
        background-color: #f0f4f8;
        padding: 8px 12px;
        border-left: 5px solid #1a237e;
        font-weight: bold;
        margin-top: 15px;
        margin-bottom: 10px;
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

    @media print {
        [data-testid="stSidebar"], .stButton, .no-print {
            display: none !important;
        }
        .main {
            background-color: white !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

st.title("🏢 Shri Charbhuja Accountancy & NIKA Tax System")

# Helper for Database Connection
def get_db_connection():
    return sqlite3.connect('nika_clients_v2.db')

# Database Initialization
def init_db():
    with get_db_connection() as conn:
        c = conn.cursor()
        
        # 1. Clients Table
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
                dob TEXT,
                gender TEXT,
                email TEXT,
                bank_name TEXT,
                ifsc_code TEXT,
                bank_account TEXT,
                created_date TEXT
            )
        ''')

        # 2. Client Years Table
        c.execute('''
            CREATE TABLE IF NOT EXISTS client_years (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER,
                financial_year TEXT,
                annual_fee REAL DEFAULT 0,
                return_type TEXT,
                income_tax_status TEXT,
                gst_status TEXT,
                itr_ack_no TEXT,
                itr_filing_date TEXT,
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

        # 4. Dynamic Financial Statements Table
        c.execute('''
            CREATE TABLE IF NOT EXISTS financial_statements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER,
                financial_year TEXT,
                opening_stock REAL DEFAULT 0,
                purchases REAL DEFAULT 0,
                indirect_exp REAL DEFAULT 0,
                sales_goods REAL DEFAULT 0,
                other_income REAL DEFAULT 0,
                closing_stock REAL DEFAULT 0,
                opening_capital REAL DEFAULT 0,
                drawings REAL DEFAULT 0,
                loans_liability REAL DEFAULT 0,
                fixed_assets REAL DEFAULT 0,
                loans_advances REAL DEFAULT 0,
                sundry_debtors REAL DEFAULT 0,
                cash_in_hand REAL DEFAULT 0,
                created_at TEXT,
                FOREIGN KEY(client_id) REFERENCES clients(id)
            )
        ''')
        conn.commit()

init_db()

FY_LIST = [
    "2020-2021", "2021-2022", "2022-2023", "2023-2024", 
    "2024-2025", "2025-2026", "2026-2027", "2027-2028"
]

menu = [
    "➕ Register Client", 
    "✏️ Edit Client Profile",
    "📅 FY Fee & Acknowledgement",
    "💵 Receive Payment",
    "🔍 Client Ledger & Credentials", 
    "📑 Computation & Financial Statements", 
    "📊 Overall Business Report"
]
choice = st.sidebar.radio("NIKA Menu", menu)

# -----------------------------------------------------------------------------
# 1. REGISTER CLIENT
# -----------------------------------------------------------------------------
if choice == "➕ Register Client":
    st.subheader("📝 Register New Client Profile")
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Client Full Name *")
        father_name = st.text_input("Father's Name")
        dob = st.text_input("Date of Birth (DD/MM/YYYY)")
        gender = st.selectbox("Gender", ["MALE", "FEMALE", "OTHER"])
        mobile = st.text_input("Mobile Number")
        email = st.text_input("Email Address")
        address = st.text_area("Address")
    
    with col2:
        pan_number = st.text_input("PAN Card Number")
        st.markdown("🔐 **ITR & Bank Details:**")
        itr_username = st.text_input("ITR Portal User ID / PAN")
        itr_password = st.text_input("ITR Portal Password", type="password")
        bank_name = st.text_input("Bank Name")
        ifsc_code = st.text_input("IFSC Code")
        bank_account = st.text_input("Account Number")

    st.markdown("---")
    st.markdown("### 📅 Initial Financial Year Setup")
    col3, col4 = st.columns(2)
    with col3:
        fin_year = st.selectbox("Financial Year (FY):", FY_LIST, index=4)
        annual_fee = st.number_input("Agreed Annual Fee (₹) *", min_value=0.0, value=1500.0, step=500.0)
    
    with col4:
        return_type = st.selectbox("Return Type:", ["Income Tax Return (ITR)", "GST Return", "Both (ITR + GST)"])
        income_tax_status = st.selectbox("ITR Status:", ["Filed", "Pending", "Not Applicable"])

    if st.button("💾 Save Client Profile"):
        if name.strip() == "":
            st.error("Please enter Client Name!")
        else:
            today_date = datetime.now().strftime("%Y-%m-%d")
            with get_db_connection() as conn:
                c = conn.cursor()
                c.execute('''
                    INSERT INTO clients (name, father_name, pan_number, mobile, address, itr_username, itr_password, dob, gender, email, bank_name, ifsc_code, bank_account, created_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (name.strip(), father_name, pan_number.strip().upper(), mobile, address, itr_username, itr_password, dob, gender, email, bank_name, ifsc_code, bank_account, today_date))
                client_id = c.lastrowid
                
                c.execute('''
                    INSERT INTO client_years (client_id, financial_year, annual_fee, return_type, income_tax_status, gst_status)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (client_id, fin_year, annual_fee, return_type, income_tax_status, "Not Applicable"))
                conn.commit()

            st.success(f"✅ Client '{name}' saved successfully!")
            st.rerun()

# -----------------------------------------------------------------------------
# 2. EDIT CLIENT PROFILE
# -----------------------------------------------------------------------------
elif choice == "✏️ Edit Client Profile":
    st.subheader("✏️ Edit Client Profile & Credentials")
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT id, name, pan_number, mobile FROM clients ORDER BY name ASC")
        client_rows = c.fetchall()
    
    if client_rows:
        client_dict = {f"{row[1]} | PAN: {row[2]}": row[0] for row in client_rows}
        selected_client_str = st.selectbox("Select Client:", list(client_dict.keys()))
        selected_client_id = client_dict[selected_client_str]
        
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM clients WHERE id = ?", (selected_client_id,))
            c_info = c.fetchone()
        
        col1, col2 = st.columns(2)
        with col1:
            edit_name = st.text_input("Name", value=c_info[1] or "")
            edit_father = st.text_input("Father Name", value=c_info[2] or "")
            edit_dob = st.text_input("DOB", value=c_info[8] or "")
            edit_mobile = st.text_input("Mobile", value=c_info[4] or "")
            edit_email = st.text_input("Email", value=c_info[10] or "")
            edit_address = st.text_area("Address", value=c_info[5] or "")
        
        with col2:
            edit_pan = st.text_input("PAN", value=c_info[3] or "")
            edit_itr_user = st.text_input("ITR User ID", value=c_info[6] or "")
            edit_itr_pass = st.text_input("ITR Password", value=c_info[7] or "")
            edit_bank = st.text_input("Bank Name", value=c_info[11] or "")
            edit_ifsc = st.text_input("IFSC", value=c_info[12] or "")
            edit_account = st.text_input("Account No", value=c_info[13] or "")

        if st.button("💾 Update Client Profile"):
            with get_db_connection() as conn:
                c = conn.cursor()
                c.execute('''
                    UPDATE clients 
                    SET name = ?, father_name = ?, pan_number = ?, mobile = ?, address = ?, 
                        itr_username = ?, itr_password = ?, dob = ?, email = ?, bank_name = ?, ifsc_code = ?, bank_account = ?
                    WHERE id = ?
                ''', (edit_name, edit_father, edit_pan, edit_mobile, edit_address, edit_itr_user, edit_itr_pass, edit_dob, edit_email, edit_bank, edit_ifsc, edit_account, selected_client_id))
                conn.commit()
            st.success("✅ Profile updated successfully!")

# -----------------------------------------------------------------------------
# 3. FY FEE & ACKNOWLEDGEMENT
# -----------------------------------------------------------------------------
elif choice == "📅 FY Fee & Acknowledgement":
    st.subheader("📅 Manage Annual Fee, Status & Acknowledgement Details")
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT id, name, pan_number FROM clients ORDER BY name ASC")
        client_rows = c.fetchall()
    
    if client_rows:
        client_dict = {f"{row[1]} | PAN: {row[2]}": row[0] for row in client_rows}
        selected_client_str = st.selectbox("Select Client:", list(client_dict.keys()))
        selected_client_id = client_dict[selected_client_str]
        
        fin_year = st.selectbox("Select Financial Year:", FY_LIST, index=4)
        
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM client_years WHERE client_id = ? AND financial_year = ?", (selected_client_id, fin_year))
            existing_rec = c.fetchone()
        
        default_fee = existing_rec[3] if existing_rec else 0.0
        default_ack = existing_rec[7] if existing_rec and len(existing_rec) > 7 and existing_rec[7] else ""
        default_date = existing_rec[8] if existing_rec and len(existing_rec) > 8 and existing_rec[8] else ""

        col1, col2 = st.columns(2)
        with col1:
            annual_fee = st.number_input(f"Annual Fee for FY {fin_year} (₹):", min_value=0.0, value=float(default_fee), step=500.0)
            itr_ack_no = st.text_input("e-Filing Acknowledgement Number:", value=default_ack)

        with col2:
            income_tax_status = st.selectbox("ITR Status:", ["Filed", "Pending", "Not Applicable"])
            itr_filing_date = st.text_input("ITR Filing Date:", value=default_date)

        if st.button("💾 Save / Update Acknowledgement Details"):
            with get_db_connection() as conn:
                c = conn.cursor()
                if existing_rec:
                    c.execute('''
                        UPDATE client_years 
                        SET annual_fee = ?, income_tax_status = ?, itr_ack_no = ?, itr_filing_date = ?
                        WHERE client_id = ? AND financial_year = ?
                    ''', (annual_fee, income_tax_status, itr_ack_no, itr_filing_date, selected_client_id, fin_year))
                else:
                    c.execute('''
                        INSERT INTO client_years (client_id, financial_year, annual_fee, return_type, income_tax_status, itr_ack_no, itr_filing_date)
                        VALUES (?, ?, ?, 'Income Tax Return (ITR)', ?, ?, ?)
                    ''', (selected_client_id, fin_year, annual_fee, income_tax_status, itr_ack_no, itr_filing_date))
                conn.commit()
            st.success("✅ Saved Acknowledgement & Fee Details!")

# -----------------------------------------------------------------------------
# 4. RECEIVE PAYMENT
# -----------------------------------------------------------------------------
elif choice == "💵 Receive Payment":
    st.subheader("💵 Receive Fee Payment")
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT id, name, pan_number FROM clients ORDER BY name ASC")
        client_rows = c.fetchall()
    
    if client_rows:
        client_dict = {f"{row[1]} | PAN: {row[2]}": row[0] for row in client_rows}
        selected_client_str = st.selectbox("Select Client:", list(client_dict.keys()))
        selected_client_id = client_dict[selected_client_str]
        fin_year = st.selectbox("Select Financial Year:", FY_LIST, index=4)
        
        col1, col2 = st.columns(2)
        with col1:
            payment_amount = st.number_input("Amount Received (₹) *", min_value=0.0, step=100.0)
            payment_date = st.date_input("Payment Date", datetime.now()).strftime("%Y-%m-%d")
        with col2:
            payment_mode = st.selectbox("Payment Mode:", ["Cash", "Online / UPI", "Bank Transfer"])
            remarks = st.text_input("Remarks")

        if st.button("✅ Save Payment Entry"):
            if payment_amount > 0:
                with get_db_connection() as conn:
                    c = conn.cursor()
                    c.execute('''
                        INSERT INTO payments (client_id, financial_year, payment_date, amount_paid, payment_mode, remarks)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (selected_client_id, fin_year, payment_date, payment_amount, payment_mode, remarks))
                    conn.commit()
                st.success("✅ Payment Recorded Successfully!")

# -----------------------------------------------------------------------------
# 5. LEDGER & CREDENTIALS
# -----------------------------------------------------------------------------
elif choice == "🔍 Client Ledger & Credentials":
    st.subheader("🔍 Client Statement & Ledger")
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT id, name, pan_number FROM clients ORDER BY name ASC")
        client_list = c.fetchall()
    
    if client_list:
        client_options = {f"{c_row[1]} | PAN: {c_row[2]}": c_row[0] for c_row in client_list}
        selected_client_label = st.selectbox("Select Client:", list(client_options.keys()))
        client_id = client_options[selected_client_label]
        fin_year = st.selectbox("Select Financial Year:", FY_LIST, index=4)
        
        with get_db_connection() as conn:
            df_payments = pd.read_sql_query('''
                SELECT payment_date as 'Date', amount_paid as 'Amount Paid (₹)', payment_mode as 'Mode', remarks as 'Remarks'
                FROM payments WHERE client_id = ? AND financial_year = ? ORDER BY id ASC
            ''', conn, params=(client_id, fin_year))
        
        st.dataframe(df_payments, use_container_width=True)

# -----------------------------------------------------------------------------
# 6. COMPUTATION & DYNAMIC FINANCIAL STATEMENTS
# -----------------------------------------------------------------------------
elif choice == "📑 Computation & Financial Statements":
    st.markdown("<h2 class='main-header'>Shri Charbhuja Accountancy, Alirajpur</h2>", unsafe_allow_html=True)
    
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT id, name, father_name, pan_number, mobile, address, dob, gender, email, bank_name, ifsc_code, bank_account FROM clients ORDER BY name ASC")
        client_rows = c.fetchall()
        
    if client_rows:
        client_dict = {f"{r[1]} | PAN: {r[3]}": r for r in client_rows}
        selected_client_str = st.selectbox("Select Client for Computation:", list(client_dict.keys()))
        c_info = client_dict[selected_client_str]
        selected_client_id = c_info[0]
        selected_fy = st.selectbox("Select Financial Year:", FY_LIST, index=4)
        
        # Calculate AY
        start_year = int(selected_fy.split('-')[0])
        ay_str = f"{start_year + 1} - {start_year + 2}"

        # Fetch Acknowledgement details
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT itr_ack_no, itr_filing_date FROM client_years WHERE client_id = ? AND financial_year = ?", (selected_client_id, selected_fy))
            cy_data = c.fetchone()
            itr_ack = cy_data[0] if cy_data and cy_data[0] else "N/A"
            itr_date = cy_data[1] if cy_data and cy_data[1] else "N/A"

            # Fetch Financial Data
            c.execute("SELECT * FROM financial_statements WHERE client_id = ? AND financial_year = ?", (selected_client_id, selected_fy))
            fin_data = c.fetchone()

        # Load Existing Data or Default values
        f_op_stock = fin_data[3] if fin_data else 342520.0
        f_purchases = fin_data[4] if fin_data else 10697958.0
        f_indirect_exp = fin_data[5] if fin_data else 241100.0
        f_sales_goods = fin_data[6] if fin_data else 7569600.0
        f_other_income = fin_data[7] if fin_data else 4585200.0
        f_cl_stock = fin_data[8] if fin_data else 310500.0
        f_op_capital = fin_data[9] if fin_data else 4130028.0
        f_drawings = fin_data[10] if fin_data else 50500.0
        f_loans_liab = fin_data[11] if fin_data else 452010.0
        f_fixed_assets = fin_data[12] if fin_data else 1696580.0
        f_loans_adv = fin_data[13] if fin_data else 1963200.0
        f_debtors = fin_data[14] if fin_data else 1527780.0
        f_cash = fin_data[15] if fin_data else 217200.0

        # Form to Update Financial Data Dynamically
        with st.expander("⚙️ Click to Edit/Enter Financial Values for this Client"):
            with st.form("fin_data_form"):
                st.markdown("### 📊 Trading / P&L Values")
                f_c1, f_c2 = st.columns(2)
                with f_c1:
                    in_op_stock = st.number_input("Opening Stock (₹):", value=float(f_op_stock))
                    in_purchases = st.number_input("Purchases (₹):", value=float(f_purchases))
                    in_indirect_exp = st.number_input("Indirect Expenses (₹):", value=float(f_indirect_exp))
                with f_c2:
                    in_sales_goods = st.number_input("Goods Sales (₹):", value=float(f_sales_goods))
                    in_other_income = st.number_input("Other Income (₹):", value=float(f_other_income))
                    in_cl_stock = st.number_input("Closing Stock (₹):", value=float(f_cl_stock))
                
                st.markdown("### ⚖️ Capital & Balance Sheet Values")
                f_c3, f_c4 = st.columns(2)
                with f_c3:
                    in_op_capital = st.number_input("Opening Capital (₹):", value=float(f_op_capital))
                    in_drawings = st.number_input("Home Expenses / Drawings (₹):", value=float(f_drawings))
                    in_loans_liab = st.number_input("Loans Liability (₹):", value=float(f_loans_liab))
                with f_c4:
                    in_fixed_assets = st.number_input("Fixed Assets / Home A/c (₹):", value=float(f_fixed_assets))
                    in_loans_adv = st.number_input("Loans & Advances Asset (₹):", value=float(f_loans_adv))
                    in_debtors = st.number_input("Sundry Debtors (₹):", value=float(f_debtors))
                    in_cash = st.number_input("Cash in Hand (₹):", value=float(f_cash))

                if st.form_submit_button("💾 Save Financial Data"):
                    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    with get_db_connection() as conn:
                        c = conn.cursor()
                        # Select check to avoid SQLite ON CONFLICT UPSERT issues
                        c.execute(
                            "SELECT id FROM financial_statements WHERE client_id = ? AND financial_year = ?", 
                            (selected_client_id, selected_fy)
                        )
                        existing_fs = c.fetchone()
                        
                        if existing_fs:
                            c.execute('''
                                UPDATE financial_statements SET
                                    opening_stock = ?,
                                    purchases = ?,
                                    indirect_exp = ?,
                                    sales_goods = ?,
                                    other_income = ?,
                                    closing_stock = ?,
                                    opening_capital = ?,
                                    drawings = ?,
                                    loans_liability = ?,
                                    fixed_assets = ?,
                                    loans_advances = ?,
                                    sundry_debtors = ?,
                                    cash_in_hand = ?,
                                    created_at = ?
                                WHERE client_id = ? AND financial_year = ?
                            ''', (
                                in_op_stock, in_purchases, in_indirect_exp, in_sales_goods, in_other_income, in_cl_stock,
                                in_op_capital, in_drawings, in_loans_liab, in_fixed_assets, in_loans_adv, in_debtors, in_cash,
                                now_str, selected_client_id, selected_fy
                            ))
                        else:
                            c.execute('''
                                INSERT INTO financial_statements (
                                    client_id, financial_year, opening_stock, purchases, indirect_exp, sales_goods, other_income, closing_stock,
                                    opening_capital, drawings, loans_liability, fixed_assets, loans_advances, sundry_debtors, cash_in_hand, created_at
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            ''', (
                                selected_client_id, selected_fy, in_op_stock, in_purchases, in_indirect_exp, in_sales_goods, in_other_income, in_cl_stock,
                                in_op_capital, in_drawings, in_loans_liab, in_fixed_assets, in_loans_adv, in_debtors, in_cash, now_str
                            ))
                        conn.commit()
                    st.success("✅ Financial data saved successfully!")
                    st.rerun()

        # Dynamic Calculations
        net_profit = (f_sales_goods + f_other_income + f_cl_stock) - (f_op_stock + f_purchases + f_indirect_exp)
        closing_capital = (f_op_capital + net_profit) - f_drawings
        total_liabilities = closing_capital + f_loans_liab
        total_assets = f_fixed_assets + f_cl_stock + f_loans_adv + f_debtors + f_cash

        tab1, tab2, tab3, tab4 = st.tabs([
            "📄 Income Tax Computation", 
            "📊 Profit & Loss A/c", 
            "📒 Capital Account", 
            "⚖️ Balance Sheet"
        ])

        # -----------------------------------------------------------------------------
        # TAB 1: COMPUTATION
        # -----------------------------------------------------------------------------
        with tab1:
            st.markdown("<h3 class='sub-header'>COMPUTATION OF TOTAL INCOME & TAX STATEMENT</h3>", unsafe_allow_html=True)
            st.caption(f"Assessment Year: {ay_str} | Financial Year: {selected_fy}")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Assessee Details:**")
                st.write(f"**Name:** {c_info[1] or ''}")
                st.write(f"**Father's Name:** {c_info[2] or ''}")
                st.write(f"**PAN No.:** {c_info[3] or ''}")
                st.write(f"**DOB / Gender:** {c_info[6] or ''} | {c_info[7] or ''}")
                st.write(f"**Address:** {c_info[5] or ''}")
            
            with col2:
                st.markdown("**Filing & Bank Details:**")
                st.write(f"**Email:** {c_info[8] or ''}")
                st.write(f"**Bank:** {c_info[9] or ''}")
                st.write(f"**A/c No.:** {c_info[11] or ''}")
                st.write(f"**IFSC:** {c_info[10] or ''}")
                st.write(f"**Acknowledgement:** {itr_ack} (Filed: {itr_date})")

            st.markdown("<div class='section-title'>1. Income Calculation</div>", unsafe_allow_html=True)
            
            inc_data = {
                "Head of Income": ["Profits and Gains from Business & Profession", "Income from Other Sources (Misc Income)"],
                "Amount (₹)": [f"{net_profit:,.2f}", f"{f_other_income:,.2f}"]
            }
            st.table(pd.DataFrame(inc_data))
            
            gti = net_profit + f_other_income
            st.metric(label="Gross Total Income (GTI)", value=f"₹ {gti:,.2f}")
            st.metric(label="Total Taxable Income (u/s 288A)", value=f"₹ {net_profit:,.2f}")

            st.markdown("<div class='section-title'>2. Tax Computation</div>", unsafe_allow_html=True)
            
            tax_val = max(0.0, (net_profit - 250000.0) * 0.05) if net_profit > 250000 else 0.0
            rebate = tax_val if net_profit <= 500000 else 0.0
            net_tax = tax_val - rebate

            tax_data = {
                "Tax Particulars": ["Tax on ₹ 2,50,000", f"Tax on Balance @ 5%", "Gross Tax Liability", "Less: Rebate u/s 87A", "Net Tax Payable", "Late Fee u/s 234F Paid"],
                "Amount (₹)": ["0.00", f"{tax_val:,.2f}", f"{tax_val:,.2f}", f"-{rebate:,.2f}", f"{net_tax:,.2f}", "5,000.00"]
            }
            st.table(pd.DataFrame(tax_data))

        # -----------------------------------------------------------------------------
        # TAB 2: PROFIT & LOSS ACCOUNT
        # -----------------------------------------------------------------------------
        with tab2:
            st.markdown(f"<h3 class='sub-header'>{c_info[1]}</h3>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align: center; color: gray;'>Profit & Loss Account for FY {selected_fy}</p>", unsafe_allow_html=True)
            
            col_exp, col_inc = st.columns(2)
            tot_exp = f_op_stock + f_purchases + f_indirect_exp + net_profit
            tot_inc = f_sales_goods + f_other_income + f_cl_stock

            with col_exp:
                st.markdown("<div class='section-title'>Debit (Expenses & Purchases)</div>", unsafe_allow_html=True)
                pnl_debit = {
                    "Particulars": ["To Opening Stock", "To Purchase Accounts", "To Indirect Expenses", "To Net Profit"],
                    "Amount (₹)": [f"{f_op_stock:,.2f}", f"{f_purchases:,.2f}", f"{f_indirect_exp:,.2f}", f"{net_profit:,.2f}"]
                }
                st.table(pd.DataFrame(pnl_debit))
                st.markdown(f"**Total Debit:** `₹ {tot_exp:,.2f}`")

            with col_inc:
                st.markdown("<div class='section-title'>Credit (Incomes & Sales)</div>", unsafe_allow_html=True)
                pnl_credit = {
                    "Particulars": ["By Sales Accounts (Goods)", "By Other Income", "By Closing Stock", ""],
                    "Amount (₹)": [f"{f_sales_goods:,.2f}", f"{f_other_income:,.2f}", f"{f_cl_stock:,.2f}", ""]
                }
                st.table(pd.DataFrame(pnl_credit))
                st.markdown(f"**Total Credit:** `₹ {tot_inc:,.2f}`")

        # -----------------------------------------------------------------------------
        # TAB 3: CAPITAL ACCOUNT
        # -----------------------------------------------------------------------------
        with tab3:
            st.markdown("<h3 class='sub-header'>CAPITAL ACCOUNT STATEMENT</h3>", unsafe_allow_html=True)
            
            cap_ledger = {
                "Date": ["01-04-2020", "31-03-2021", "31-03-2021", "31-03-2021"],
                "Particulars": ["By Opening Balance", "By Profit & Loss A/c (Net Profit)", "To Home Expenses (Drawings)", "To Closing Balance (Net Capital)"],
                "Debit (₹)": ["-", "-", f"{f_drawings:,.2f}", f"{closing_capital:,.2f}"],
                "Credit (₹)": [f"{f_op_capital:,.2f}", f"{net_profit:,.2f}", "-", "-"]
            }
            st.table(pd.DataFrame(cap_ledger))

        # -----------------------------------------------------------------------------
        # TAB 4: BALANCE SHEET
        # -----------------------------------------------------------------------------
        with tab4:
            st.markdown(f"<h3 class='sub-header'>{c_info[1]}</h3>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align: center; color: gray;'>Balance Sheet for FY {selected_fy}</p>", unsafe_allow_html=True)
            
            col_liab, col_asset = st.columns(2)
            
            with col_liab:
                st.markdown("<div class='section-title'>Liabilities</div>", unsafe_allow_html=True)
                bs_liab = {
                    "Liabilities Head": ["Capital Account (Net Balance)", "Loans & Liabilities"],
                    "Amount (₹)": [f"{closing_capital:,.2f}", f"{f_loans_liab:,.2f}"]
                }
                st.table(pd.DataFrame(bs_liab))
                st.markdown(f"**Total Liabilities:** `₹ {total_liabilities:,.2f}`")

            with col_asset:
                st.markdown("<div class='section-title'>Assets</div>", unsafe_allow_html=True)
                bs_assets = {
                    "Assets Head": ["Fixed Assets / Home A/c", "Closing Stock", "Loans & Advances (Asset)", "Sundry Debtors", "Cash-in-Hand"],
                    "Amount (₹)": [f"{f_fixed_assets:,.2f}", f"{f_cl_stock:,.2f}", f"{f_loans_adv:,.2f}", f"{f_debtors:,.2f}", f"{f_cash:,.2f}"]
                }
                st.table(pd.DataFrame(bs_assets))
                st.markdown(f"**Total Assets:** `₹ {total_assets:,.2f}`")

# -----------------------------------------------------------------------------
# 7. OVERALL BUSINESS REPORT
# -----------------------------------------------------------------------------
elif choice == "📊 Overall Business Report":
    st.subheader("📊 NIKA Business Financial Dashboard")
    selected_fy = st.selectbox("Filter Report by Financial Year:", FY_LIST, index=4)
    
    with get_db_connection() as conn:
        master_df = pd.read_sql_query('''
            SELECT 
                c.id as 'ID',
                c.name as 'Name',
                c.mobile as 'Mobile',
                c.pan_number as 'PAN',
                COALESCE(cy.annual_fee, 0) as 'Annual Fee (₹)',
                COALESCE(p.total_paid, 0) as 'Received (₹)',
                (COALESCE(cy.annual_fee, 0) - COALESCE(p.total_paid, 0)) as 'Due (₹)'
            FROM clients c
            LEFT JOIN client_years cy ON c.id = cy.client_id AND cy.financial_year = ?
            LEFT JOIN (
                SELECT client_id, SUM(amount_paid) as total_paid 
                FROM payments 
                WHERE financial_year = ? 
                GROUP BY client_id
            ) p ON c.id = p.client_id
            ORDER BY c.name ASC
        ''', conn, params=(selected_fy, selected_fy))
    
    if not master_df.empty:
        st.dataframe(master_df, use_container_width=True)
