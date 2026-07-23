import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import urllib.parse

# Page Configuration
st.set_page_config(page_title="NIKA - Tax & Financial Year System", layout="wide")

# Custom CSS Styling (Includes Print Styles for A4 Output)
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

    /* Print View Customization */
    @media print {
        [data-testid="stSidebar"] {
            display: none;
        }
        .stButton {
            display: none;
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

st.title("🏢 NIKA - Client Management, WhatsApp & Financials System")

# Database Connection Helper
def get_db_connection():
    return sqlite3.connect('nika_clients_v2.db')

# Database Initialization
def init_db():
    with get_db_connection() as conn:
        c = conn.cursor()
        
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

FY_LIST = [
    "2020-2021", "2021-2022", "2022-2023", "2023-2024", 
    "2024-2025", "2025-2026", "2026-2027", "2027-2028", 
    "2028-2029", "2029-2030", "2030-2031"
]

menu = [
    "➕ Add New Client", 
    "✏️ Edit Client Profile",
    "📅 Add / Update Financial Year Fee",
    "💵 Receive Payment",
    "🔍 Client Ledger & Credentials", 
    "📑 Balance Sheet & Financial Statements", 
    "📊 Overall Business Report", 
    "🗑️ Delete Entry"
]
choice = st.sidebar.radio("NIKA Menu", menu)

if "num_gst_fields" not in st.session_state:
    st.session_state.num_gst_fields = 1

def create_whatsapp_link(client_mobile, message):
    if not client_mobile:
        return None
    clean_mobile = "".join(filter(str.isdigit, str(client_mobile)))
    if len(clean_mobile) == 10:
        clean_mobile = "91" + clean_mobile
    encoded_msg = urllib.parse.quote(message)
    return f"https://api.whatsapp.com/send?phone={clean_mobile}&text={encoded_msg}"

MY_CONTACT = "8358013017"

# --- [OTHER MENU OPTIONS REMAIN THE SAME] ---

# 6. FEATURE: Balance Sheet, Automatic Computation & Print/PDF Download
if choice == "📑 Balance Sheet & Financial Statements":
    st.subheader("📑 Client Financial Statements, Computation & Print")
    
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT id, name, father_name, pan_number, mobile, address FROM clients ORDER BY name ASC")
        client_rows = c.fetchall()
        
    if not client_rows:
        st.warning("No clients registered.")
    else:
        client_dict = {f"{r[1]} | PAN: {r[3]}": r for r in client_rows}
        selected_client_str = st.selectbox("Select Client:", list(client_dict.keys()))
        selected_client_info = client_dict[selected_client_str]
        selected_client_id = selected_client_info[0]
        selected_fy = st.selectbox("Select Financial Year:", FY_LIST, index=6)
        
        # Calculate Assessment Year
        start_year = int(selected_fy.split('-')[0])
        ay_str = f"{start_year + 1}-{start_year + 2}"
        
        # Fetch Existing Data if available
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM financial_statements WHERE client_id = ? AND financial_year = ?", (selected_client_id, selected_fy))
            fs = c.fetchone()
            
        # Defaults
        gross_turnover = fs[3] if fs and len(fs) > 3 else 0.0
        gross_profit = fs[4] if fs and len(fs) > 4 else 0.0
        net_profit = fs[5] if fs and len(fs) > 5 else 0.0
        op_capital = fs[6] if fs and len(fs) > 6 else 0.0
        cap_add = fs[7] if fs and len(fs) > 7 else 0.0
        drawings = fs[8] if fs and len(fs) > 8 else 0.0
        tot_assets = fs[10] if fs and len(fs) > 10 else 0.0
        tot_liab = fs[11] if fs and len(fs) > 11 else 0.0
        
        inc_sal = fs[12] if fs and len(fs) > 12 else 0.0
        grs_rent = fs[13] if fs and len(fs) > 13 else 0.0
        inc_cg = fs[14] if fs and len(fs) > 14 else 0.0
        inc_os = fs[15] if fs and len(fs) > 15 else 0.0
        exempt_inc = fs[16] if fs and len(fs) > 16 else 0.0
        ded_80c = fs[17] if fs and len(fs) > 17 else 0.0
        ded_80d = fs[18] if fs and len(fs) > 18 else 0.0
        other_ded = fs[19] if fs and len(fs) > 19 else 0.0

        t1, t2, t3, t4, t5 = st.tabs([
            "💰 Profit & Loss Account", 
            "🏦 Capital Account", 
            "🏛️ Balance Sheet Summary", 
            "🧮 Automatic Tax Computation",
            "🖨️ Printable Preview & PDF"
        ])
        
        with t1:
            st.write("#### Profit & Loss Statement Summary")
            col_p1, col_p2, col_p3 = st.columns(3)
            with col_p1:
                gross_turnover = st.number_input("Gross Sales / Turnover (₹)", min_value=0.0, value=float(gross_turnover), step=1000.0)
            with col_p2:
                gross_profit = st.number_input("Gross Profit (₹)", min_value=0.0, value=float(gross_profit), step=1000.0)
            with col_p3:
                net_profit = st.number_input("Net Profit / PGBP Income (₹)", min_value=0.0, value=float(net_profit), step=1000.0)

        with t2:
            st.write("#### Capital Account Computation")
            col_c1, col_c2, col_c3 = st.columns(3)
            with col_c1:
                op_capital = st.number_input("Opening Capital (₹)", min_value=0.0, value=float(op_capital), step=1000.0)
            with col_c2:
                cap_add = st.number_input("Capital Addition (₹)", min_value=0.0, value=float(cap_add), step=1000.0)
            with col_c3:
                drawings = st.number_input("Drawings / Personal Expense (₹)", min_value=0.0, value=float(drawings), step=1000.0)
                
            closing_capital = op_capital + cap_add + net_profit - drawings
            st.success(f"🧮 **Calculated Closing Capital:** ₹{closing_capital:,.2f}")

        with t3:
            st.write("#### Balance Sheet Totals")
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                tot_assets = st.number_input("Total Assets (₹)", min_value=0.0, value=float(tot_assets), step=1000.0)
            with col_b2:
                tot_liab = st.number_input("Total Liabilities (Excl. Capital) (₹)", min_value=0.0, value=float(tot_liab), step=1000.0)

        with t4:
            st.markdown("### 🧮 Automatic Computation of Taxable Income")
            c_col1, c_col2 = st.columns(2)

            with c_col1:
                st.markdown("##### 📥 Heads of Income")
                income_salary = st.number_input("1. Income from Salary (₹)", min_value=0.0, value=float(inc_sal), step=1000.0)
                
                # House Property Auto Calculation
                gross_rent = st.number_input("2. Gross Rent Received (₹)", min_value=0.0, value=float(grs_rent), step=1000.0)
                std_deduction_hp = gross_rent * 0.30
                net_house_property = max(0.0, gross_rent - std_deduction_hp)
                st.caption(f"ℹ️ Less 30% Standard Deduction: ₹{std_deduction_hp:,.2f} | Net HP Income: ₹{net_house_property:,.2f}")
                
                st.info(f"3. Business Net Profit (PGBP): **₹{net_profit:,.2f}**")
                
                income_capital_gains = st.number_input("4. Capital Gains (₹)", min_value=0.0, value=float(inc_cg), step=1000.0)
                income_other_sources = st.number_input("5. Income from Other Sources (₹)", min_value=0.0, value=float(inc_os), step=1000.0)

            with c_col2:
                st.markdown("##### 📉 Deductions & Exemptions")
                deduction_80c = st.number_input("Section 80C Deductions (₹)", min_value=0.0, max_value=150000.0, value=float(ded_80c), step=1000.0)
                deduction_80d = st.number_input("Section 80D Deductions (₹)", min_value=0.0, value=float(ded_80d), step=1000.0)
                deduction_other = st.number_input("Other Deductions (80TTA, etc.) (₹)", min_value=0.0, value=float(other_ded), step=1000.0)
                exempt_income = st.number_input("Exempt Income (Agricultural etc.) (₹)", min_value=0.0, value=float(exempt_inc), step=1000.0)

            # AUTOMATIC CALCULATION LOGIC
            gross_total_income = (income_salary + net_house_property + net_profit + income_capital_gains + income_other_sources) - exempt_income
            total_deductions = deduction_80c + deduction_80d + deduction_other
            taxable_income = max(0.0, gross_total_income - total_deductions)
            taxable_income_rounded = round(taxable_income, -1)  # u/s 288A

            st.markdown("---")
            st.markdown("#### 📊 Final Calculated Result Summary")
            res_c1, res_c2 = st.columns(2)
            with res_c1:
                st.metric("Gross Total Income (GTI)", f"₹{gross_total_income:,.2f}")
            with res_c2:
                st.metric("Net Taxable Income (u/s 288A)", f"₹{taxable_income_rounded:,.2f}")

        # TAB 5: PRINTABLE PREVIEW & DOWNLOAD
        with t5:
            st.markdown("### 🖨️ Printable Income Statement & Balance Sheet")
            
            # HTML Template for Printing
            html_printable = f"""
            <div class="printable-card">
                <h2 style="text-align:center; margin-bottom:5px; color:#1a237e;">COMPUTATION OF TOTAL INCOME</h2>
                <h4 style="text-align:center; margin-top:0px;">ASSESSMENT YEAR: {ay_str} | FINANCIAL YEAR: {selected_fy}</h4>
                <hr>
                <table style="width:100%; font-size: 14px;">
                    <tr><td><b>NAME OF ASSESSEE:</b> {selected_client_info[1]}</td><td><b>PAN NUMBER:</b> {selected_client_info[3]}</td></tr>
                    <tr><td><b>FATHER'S NAME:</b> {selected_client_info[2] if selected_client_info[2] else 'N/A'}</td><td><b>MOBILE:</b> {selected_client_info[4]}</td></tr>
                    <tr><td colspan="2"><b>ADDRESS:</b> {selected_client_info[5] if selected_client_info[5] else 'N/A'}</td></tr>
                </table>
                <hr>
                <h4 style="background-color:#1a237e; color:white; padding:5px;">1. STATEMENT OF COMPUTATION OF INCOME</h4>
                <table class="print-table">
                    <tr><th>Particulars</th><th style="text-align:right;">Amount (₹)</th></tr>
                    <tr><td>Income from Salary</td><td style="text-align:right;">{income_salary:,.2f}</td></tr>
                    <tr><td>Income from House Property (Arrears/Rent Less 30% Deduction)</td><td style="text-align:right;">{net_house_property:,.2f}</td></tr>
                    <tr><td>Profits & Gains from Business or Profession (PGBP)</td><td style="text-align:right;">{net_profit:,.2f}</td></tr>
                    <tr><td>Capital Gains (Short Term / Long Term)</td><td style="text-align:right;">{income_capital_gains:,.2f}</td></tr>
                    <tr><td>Income from Other Sources / Bank Interest</td><td style="text-align:right;">{income_other_sources:,.2f}</td></tr>
                    <tr style="font-weight:bold; background-color:#f2f2f2;"><td>GROSS TOTAL INCOME (GTI)</td><td style="text-align:right;">₹{gross_total_income:,.2f}</td></tr>
                    <tr><td>Less: Chapter VI-A Deductions (80C, 80D, etc.)</td><td style="text-align:right;">(-) {total_deductions:,.2f}</td></tr>
                    <tr style="font-weight:bold; font-size:16px; background-color:#e8eaf6;"><td>TOTAL TAXABLE INCOME (ROUNDED OFF U/S 288A)</td><td style="text-align:right;">₹{taxable_income_rounded:,.2f}</td></tr>
                </table>

                <h4 style="background-color:#1a237e; color:white; padding:5px; margin-top:20px;">2. CAPITAL ACCOUNT & BALANCE SHEET SUMMARY</h4>
                <table class="print-table">
                    <tr><th>Capital Account Particulars</th><th style="text-align:right;">Amount (₹)</th><th>Balance Sheet Particulars</th><th style="text-align:right;">Amount (₹)</th></tr>
                    <tr><td>Opening Capital</td><td style="text-align:right;">{op_capital:,.2f}</td><td>Total Assets</td><td style="text-align:right;">{tot_assets:,.2f}</td></tr>
                    <tr><td>Add: Capital Introduction</td><td style="text-align:right;">{cap_add:,.2f}</td><td>Total Liabilities (Excl. Capital)</td><td style="text-align:right;">{tot_liab:,.2f}</td></tr>
                    <tr><td>Add: Net Profit</td><td style="text-align:right;">{net_profit:,.2f}</td><td colspan="2" rowspan="2"></td></tr>
                    <tr><td>Less: Personal Drawings</td><td style="text-align:right;">(-) {drawings:,.2f}</td></tr>
                    <tr style="font-weight:bold; background-color:#f2f2f2;"><td>CLOSING CAPITAL BALANCE</td><td style="text-align:right;">₹{closing_capital:,.2f}</td><td colspan="2"></td></tr>
                </table>
            </div>
            """
            
            # Display Printable Card Preview
            st.markdown(html_printable, unsafe_allow_html=True)
            
            st.markdown("---")
            st.markdown("### 🖨️ Action Menu:")
            
            p_col1, p_col2 = st.columns(2)
            with p_col1:
                st.info("💡 **Print / Save PDF करने का तरीका:** अपने कीबोर्ड पर `Ctrl + P` दबाएं और Destination में 'Save as PDF' चुनें।")
            with p_col2:
                # HTML Download Button
                st.download_button(
                    label="📥 Download Printable HTML File",
                    data=html_printable,
                    file_name=f"Computation_{selected_client_info[1]}_{selected_fy}.html",
                    mime="text/html"
                )

        st.markdown("---")
        if st.button("💾 Save Complete Financial Statements Data"):
            today_str = datetime.now().strftime("%Y-%m-%d %H:%M")
            with get_db_connection() as conn:
                c = conn.cursor()
                c.execute('''
                    INSERT INTO financial_statements (
                        client_id, financial_year, gross_turnover, gross_profit, net_profit, 
                        opening_capital, capital_addition, drawings, closing_capital, 
                        total_assets, total_liabilities, income_salary, gross_rent, 
                        income_capital_gains, income_other_sources, exempt_income, 
                        deductions_80c, deductions_80d, other_deductions, 
                        gross_total_income, taxable_income, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(client_id, financial_year) DO UPDATE SET
                        gross_turnover=excluded.gross_turnover,
                        gross_profit=excluded.gross_profit,
                        net_profit=excluded.net_profit,
                        opening_capital=excluded.opening_capital,
                        capital_addition=excluded.capital_addition,
                        drawings=excluded.drawings,
                        closing_capital=excluded.closing_capital,
                        total_assets=excluded.total_assets,
                        total_liabilities=excluded.total_liabilities,
                        income_salary=excluded.income_salary,
                        gross_rent=excluded.gross_rent,
                        income_capital_gains=excluded.income_capital_gains,
                        income_other_sources=excluded.income_other_sources,
                        exempt_income=excluded.exempt_income,
                        deductions_80c=excluded.deductions_80c,
                        deductions_80d=excluded.deductions_80d,
                        other_deductions=excluded.other_deductions,
                        gross_total_income=excluded.gross_total_income,
                        taxable_income=excluded.taxable_income,
                        created_at=excluded.created_at
                ''', (
                    selected_client_id, selected_fy, gross_turnover, gross_profit, net_profit,
                    op_capital, cap_add, drawings, closing_capital, tot_assets, tot_liab,
                    income_salary, gross_rent, income_capital_gains, income_other_sources,
                    exempt_income, deduction_80c, deduction_80d, deduction_other,
                    gross_total_income, taxable_income_rounded, today_str
                ))
                conn.commit()
            st.success("✅ Financial Statement & Computation saved successfully!")
