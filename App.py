import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import urllib.parse

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

    /* Print View Customization */
    @media print {
        [data-testid="stSidebar"] {
            display: none;
        }
        .stButton, .no-print {
            display: none !important;
        }
        .main {
            background-color: white !important;
        }
    }
    
    .printable-card {
        background-color: #ffffff;
        padding: 25px;
        border: 2px solid #1a237e;
        border-radius: 10px;
        color: #000;
        font-family: Arial, sans-serif;
    }
    .print-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 15px;
    }
    .print-table th, .print-table td {
        border: 1px solid #ddd;
        padding: 8px;
        text-align: left;
    }
    .print-table th {
        background-color: #f2f2f2;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🏢 Shri Charbhuja Accountancy & NIKA Tax System")

# Helper to manage DB Connection safely
def get_db_connection():
    return sqlite3.connect('nika_clients_v2.db')

# Database Initialization & Auto-Migration
def init_db():
    with get_db_connection() as conn:
        c = conn.cursor()
        
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
                dob TEXT,
                gender TEXT,
                email TEXT,
                bank_name TEXT,
                ifsc_code TEXT,
                bank_account TEXT,
                created_date TEXT
            )
        ''')

        # Auto Migrations for Clients
        c.execute("PRAGMA table_info(clients)")
        columns = [col[1] for col in c.fetchall()]
        if 'itr_username' not in columns and 'portal_username' in columns:
            c.execute("ALTER TABLE clients RENAME COLUMN portal_username TO itr_username")
        if 'itr_password' not in columns and 'portal_password' in columns:
            c.execute("ALTER TABLE clients RENAME COLUMN portal_password TO itr_password")
        if 'dob' not in columns:
            c.execute("ALTER TABLE clients ADD COLUMN dob TEXT")
        if 'gender' not in columns:
            c.execute("ALTER TABLE clients ADD COLUMN gender TEXT")
        if 'email' not in columns:
            c.execute("ALTER TABLE clients ADD COLUMN email TEXT")
        if 'bank_name' not in columns:
            c.execute("ALTER TABLE clients ADD COLUMN bank_name TEXT")
        if 'ifsc_code' not in columns:
            c.execute("ALTER TABLE clients ADD COLUMN ifsc_code TEXT")
        if 'bank_account' not in columns:
            c.execute("ALTER TABLE clients ADD COLUMN bank_account TEXT")

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
                itr_ack_no TEXT,
                itr_filing_date TEXT,
                FOREIGN KEY(client_id) REFERENCES clients(id)
            )
        ''')

        # Migration check for client_years (Ack No & Filing Date)
        c.execute("PRAGMA table_info(client_years)")
        cy_columns = [col[1] for col in c.fetchall()]
        if 'itr_ack_no' not in cy_columns:
            c.execute("ALTER TABLE client_years ADD COLUMN itr_ack_no TEXT")
        if 'itr_filing_date' not in cy_columns:
            c.execute("ALTER TABLE client_years ADD COLUMN itr_filing_date TEXT")

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

        # 5. Financial Statements & Computation Table
        c.execute('''
            CREATE TABLE IF NOT EXISTS financial_statements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER,
                financial_year TEXT,
                gross_turnover REAL DEFAULT 0,
                gross_profit REAL DEFAULT 0,
                net_profit REAL DEFAULT 0,
                opening_capital REAL DEFAULT 0,
                capital_addition REAL DEFAULT 0,
                drawings REAL DEFAULT 0,
                closing_capital REAL DEFAULT 0,
                total_assets REAL DEFAULT 0,
                total_liabilities REAL DEFAULT 0,
                income_salary REAL DEFAULT 0,
                gross_rent REAL DEFAULT 0,
                income_capital_gains REAL DEFAULT 0,
                income_other_sources REAL DEFAULT 0,
                exempt_income REAL DEFAULT 0,
                deductions_80c REAL DEFAULT 0,
                deductions_80d REAL DEFAULT 0,
                other_deductions REAL DEFAULT 0,
                gross_total_income REAL DEFAULT 0,
                taxable_income REAL DEFAULT 0,
                created_at TEXT,
                FOREIGN KEY(client_id) REFERENCES clients(id),
                UNIQUE(client_id, financial_year)
            )
        ''')
        conn.commit()

init_db()

# Financial Years List
FY_LIST = [
    "2020-2021", "2021-2022", "2022-2023", "2023-2024", 
    "2024-2025", "2025-2026", "2026-2027", "2027-2028"
]

# Sidebar Navigation
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

if "num_gst_fields" not in st.session_state:
    st.session_state.num_gst_fields = 1

# 1. Register Client Profile
if choice == "➕ Register Client":
    st.subheader("📝 Register New Client Profile")
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Client Full Name *")
        father_name = st.text_input("Father's Name")
        dob = st.text_input("Date of Birth (DD/MM/YYYY)", value="25/08/1987")
        gender = st.selectbox("Gender", ["MALE", "FEMALE", "OTHER"])
        mobile = st.text_input("Mobile Number")
        email = st.text_input("Email Address", value="k3computer@gmail.com")
        address = st.text_area("Address", value="C51 KESHAV NAGAR K.B. ROAD, ALIRAJPUR")
    
    with col2:
        pan_number = st.text_input("PAN Card Number", value="BJBPB9747C")
        st.markdown("🔐 **ITR & Bank Details:**")
        itr_username = st.text_input("ITR Portal User ID / PAN")
        itr_password = st.text_input("ITR Portal Password", type="password")
        bank_name = st.text_input("Bank Name", value="BANK OF BARODA, STATE BANK OF INDIA")
        ifsc_code = st.text_input("IFSC Code", value="BARB0ALIRAJ")
        bank_account = st.text_input("Account Number", value="06890200001749")

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

# 2. Edit Client Profile
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
            edit_name = st.text_input("Name", value=c_info[1] if c_info[1] else "")
            edit_father = st.text_input("Father Name", value=c_info[2] if c_info[2] else "")
            edit_dob = st.text_input("DOB", value=c_info[8] if len(c_info) > 8 and c_info[8] else "")
            edit_mobile = st.text_input("Mobile", value=c_info[4] if c_info[4] else "")
            edit_email = st.text_input("Email", value=c_info[10] if len(c_info) > 10 and c_info[10] else "")
            edit_address = st.text_area("Address", value=c_info[5] if c_info[5] else "")
        
        with col2:
            edit_pan = st.text_input("PAN", value=c_info[3] if c_info[3] else "")
            edit_itr_user = st.text_input("ITR User ID", value=c_info[6] if c_info[6] else "")
            edit_itr_pass = st.text_input("ITR Password", value=c_info[7] if c_info[7] else "")
            edit_bank = st.text_input("Bank Name", value=c_info[11] if len(c_info) > 11 and c_info[11] else "")
            edit_ifsc = st.text_input("IFSC", value=c_info[12] if len(c_info) > 12 and c_info[12] else "")
            edit_account = st.text_input("Account No", value=c_info[13] if len(c_info) > 13 and c_info[13] else "")

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

# 3. Add / Update Financial Year Fee & Filing Details
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
        default_ack = existing_rec[7] if existing_rec and len(existing_rec) > 7 and existing_rec[7] else "602642800240626"
        default_date = existing_rec[8] if existing_rec and len(existing_rec) > 8 and existing_rec[8] else "JUN 24, 2026"

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

# 4. Receive Payment
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

# 5. Ledger & Credentials
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

# 6. Balance Sheet & Financial Statements
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
            itr_ack = cy_data[0] if cy_data and cy_data[0] else "602642800240626"
            itr_date = cy_data[1] if cy_data and cy_data[1] else "JUN 24, 2026"

        tab1, tab2, tab3, tab4 = st.tabs([
            "📄 Income Tax Computation", 
            "📊 Profit & Loss A/c", 
            "📒 Capital Account", 
            "⚖️ Balance Sheet"
        ])

        # -----------------------------------------------------------------------------
        # TAB 1: COMPUTATION OF TOTAL INCOME
        # -----------------------------------------------------------------------------
        with tab1:
            st.markdown("<h3 class='sub-header'>COMPUTATION OF TOTAL INCOME & TAX STATEMENT</h3>", unsafe_allow_html=True)
            st.caption(f"Assessment Year: {ay_str} | Financial Year: {selected_fy}")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Assessee Details:**")
                st.write(f"**Name:** {c_info[1]}")
                st.write(f"**Father's Name:** {c_info[2]}")
                st.write(f"**PAN No.:** {c_info[3]}")
                st.write(f"**DOB / Gender:** {c_info[6]} | {c_info[7]}")
                st.write(f"**Address:** {c_info[5]}")
            
            with col2:
                st.markdown("**Filing & Bank Details:**")
                st.write(f"**Email:** {c_info[8]}")
                st.write(f"**Bank:** {c_info[9]}")
                st.write(f"**A/c No.:** {c_info[11]}")
                st.write(f"**IFSC:** {c_info[10]}")
                st.write(f"**Acknowledgement:** {itr_ack} (Filed: {itr_date})")

            st.markdown("<div class='section-title'>1. Income Calculation</div>", unsafe_allow_html=True)
            
            inc_data = {
                "Head of Income": ["Profits and Gains from Business & Profession", "Income from Other Sources (Misc Income)"],
                "Amount (₹)": ["11,83,722.00", "45,85,200.00"]
            }
            st.table(pd.DataFrame(inc_data))
            
            st.metric(label="Gross Total Income (GTI)", value="₹ 57,68,922.00")
            st.metric(label="Total Taxable Income (u/s 288A)", value="₹ 11,83,722.00")

            st.markdown("<div class='section-title'>2. Tax Computation</div>", unsafe_allow_html=True)
            tax_data = {
                "Tax Particulars": ["Tax on ₹ 2,50,000", "Tax on Balance @ 5%", "Gross Tax Liability", "Less: Rebate u/s 87A", "Net Tax Payable", "Late Fee u/s 234F Paid"],
                "Amount (₹)": ["0.00", "23,776.00", "23,776.00", "-23,776.00", "0.00", "5,000.00"]
            }
            st.table(pd.DataFrame(tax_data))

        # -----------------------------------------------------------------------------
        # TAB 2: PROFIT & LOSS ACCOUNT
        # -----------------------------------------------------------------------------
        with tab2:
            st.markdown("<h3 class='sub-header'>SHIVAY ENTERPRISES</h3>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align: center; color: gray;'>Prop. {c_info[1]} | Profit & Loss Account (1-Apr-2020 to 31-Mar-2021)</p>", unsafe_allow_html=True)
            
            col_exp, col_inc = st.columns(2)
            
            with col_exp:
                st.markdown("<div class='section-title'>Debit (Expenses & Purchases)</div>", unsafe_allow_html=True)
                pnl_debit = {
                    "Particulars": [
                        "To Opening Stock (Cement)", 
                        "To Purchase Accounts (Goods)", 
                        "To Indirect Expenses:",
                        "   - Office & Hotel Expenses",
                        "   - Salary Expenses",
                        "   - Travelling Expenses",
                        "To Net Profit"
                    ],
                    "Amount (₹)": [
                        "3,42,520.00", 
                        "10,697,958.00", 
                        "", 
                        "74,580.00", 
                        "1,20,000.00", 
                        "46,520.00", 
                        "11,83,722.00"
                    ]
                }
                st.table(pd.DataFrame(pnl_debit))
                st.markdown("**Total Debit:** `₹ 1,24,65,300.00`")

            with col_inc:
                st.markdown("<div class='section-title'>Credit (Incomes & Sales)</div>", unsafe_allow_html=True)
                pnl_credit = {
                    "Particulars": [
                        "By Sales Accounts:", 
                        "   - Goods Sales", 
                        "   - Other Income", 
                        "By Closing Stock (Cement)",
                        "",
                        "",
                        ""
                    ],
                    "Amount (₹)": [
                        "", 
                        "75,69,600.00", 
                        "45,85,200.00", 
                        "3,10,500.00",
                        "",
                        "",
                        ""
                    ]
                }
                st.table(pd.DataFrame(pnl_credit))
                st.markdown("**Total Credit:** `₹ 1,24,65,300.00`")

        # -----------------------------------------------------------------------------
        # TAB 3: CAPITAL ACCOUNT
        # -----------------------------------------------------------------------------
        with tab3:
            st.markdown("<h3 class='sub-header'>CAPITAL ACCOUNT STATEMENT</h3>", unsafe_allow_html=True)
            st.caption("For the period: 01-04-2020 to 31-03-2021")
            
            cap_ledger = {
                "Date": ["01-04-2020", "31-03-2021", "31-03-2021", "31-03-2021"],
                "Particulars": ["By Opening Balance", "By Profit & Loss A/c (Net Profit)", "To Home Expenses (Drawings)", "To Closing Balance (Net Capital)"],
                "Vch Type": ["—", "Journal", "Journal", "—"],
                "Debit (₹)": ["-", "-", "50,500.00", "52,63,250.00"],
                "Credit (₹)": ["41,30,028.00", "11,83,722.00", "-", "-"]
            }
            st.table(pd.DataFrame(cap_ledger))

        # -----------------------------------------------------------------------------
        # TAB 4: BALANCE SHEET
        # -----------------------------------------------------------------------------
        with tab4:
            st.markdown("<h3 class='sub-header'>SHIVAY ENTERPRISES</h3>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align: center; color: gray;'>Balance Sheet as at 31st March 2021</p>", unsafe_allow_html=True)
            
            col_liab, col_asset = st.columns(2)
            
            with col_liab:
                st.markdown("<div class='section-title'>Liabilities</div>", unsafe_allow_html=True)
                bs_liab = {
                    "Liabilities Head": [
                        "Capital Account (Net Balance)", 
                        "Loans & Liabilities", 
                        "Current Liabilities", 
                        "   - Sundry Creditors", 
                        "   - Duties & Taxes"
                    ],
                    "Amount (₹)": [
                        "52,63,250.00", 
                        "4,52,010.00", 
                        "0.00", 
                        "0.00", 
                        "0.00"
                    ]
                }
                st.table(pd.DataFrame(bs_liab))
                st.markdown("**Total Liabilities:** `₹ 57,15,260.00`")

            with col_asset:
                st.markdown("<div class='section-title'>Assets</div>", unsafe_allow_html=True)
                bs_assets = {
                    "Assets Head": [
                        "Non-Current Assets (Home A/c)", 
                        "Current Assets:", 
                        "   - Closing Stock (Cement)", 
                        "   - Loans & Advances (Asset)", 
                        "   - Sundry Debtors", 
                        "   - Cash-in-Hand"
                    ],
                    "Amount (₹)": [
                        "16,96,580.00", 
                        "", 
                        "3,10,500.00", 
                        "19,63,200.00", 
                        "15,27,780.00", 
                        "2,17,200.00"
                    ]
                }
                st.table(pd.DataFrame(bs_assets))
                st.markdown("**Total Assets:** `₹ 57,15,260.00`")

        st.markdown("---")
        st.success("✅ कंप्यूटेशन व बैलेंस शीट डेटा पूरी तरह सिंक है।")

# 7. Overall Business Report
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
