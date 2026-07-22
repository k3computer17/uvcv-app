import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- 1. рдкреЗрдЬ рдПрд╡рдВ рдереАрдо рд╕реЗрдЯрд┐рдВрдЧреНрд╕ (NIKA рдХрд▓рд░ рдмреИрдХрдЧреНрд░рд╛рдЙрдВрдб) ---
st.set_page_config(page_title="NIKA - Tax & Client Ledger System", layout="wide")

# NIKA Custom CSS Styling (рд░рдВрдЧреАрди рдмреИрдХрдЧреНрд░рд╛рдЙрдВрдб)
st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #1e1e2f 0%, #2a2a40 100%);
        color: #ffffff;
    }
    .stAppHeader {
        background-color: rgba(0,0,0,0);
    }
    h1, h2, h3 {
        color: #00d4ff !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .stButton>button {
        background: linear-gradient(90deg, #00d4ff 0%, #005bea 100%);
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 24px;
        font-weight: bold;
        font-size: 16px;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #005bea 0%, #00d4ff 100%);
        color: white;
    }
    div[data-testid="stMetricValue"] {
        color: #00ff88 !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("ЁЯПв NIKA - рдХреНрд▓рд╛рдЗрдВрдЯ рдбреЗрдЯрд╛рдмреЗрд╕ рдПрд╡рдВ рдПрдбрд╡рд╛рдВрд╕реНрдб рдЦрд╛рддрд╛ рдкреНрд░рдгрд╛рд▓реА")

# --- 2. SQLite рдбреЗрдЯрд╛рдмреЗрд╕ рд╕реЗрдЯрдЕрдк ---
conn = sqlite3.connect('nika_clients.db', check_same_thread=False)
c = conn.cursor()

# 1. рдХреНрд▓рд╛рдЗрдВрдЯреНрд╕ рдореБрдЦреНрдп рдорд╛рд╕реНрдЯрд░ рдЯреЗрдмрд▓
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

# 2. рдкреЗрдореЗрдВрдЯ рдЯреНрд░рд╛рдВрдЬреЗрдХреНрд╢рди (рд▓реЗрдЬрд╝рд░) рдЯреЗрдмрд▓
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

# --- 3. рдиреЗрд╡рд┐рдЧреЗрд╢рди рдореЗрдиреВ ---
menu = [
    "тЮХ рдирдпрд╛ рдХреНрд▓рд╛рдЗрдВрдЯ рдЬреЛрдбрд╝реЗрдВ", 
    "ЁЯТ╡ рдирдпрд╛ рдкреЗрдореЗрдВрдЯ рдкреНрд░рд╛рдкреНрдд рдХрд░реЗрдВ",
    "ЁЯФН рдХреНрд▓рд╛рдЗрдВрдЯ рд▓реЗрдЬрд╝рд░ рдПрд╡рдВ рд╣рд┐рд╕рд╛рдм-рдХрд┐рддрд╛рдм", 
    "ЁЯУК рд╕рдВрдкреВрд░реНрдг рд╡рд┐рддреНрддреАрдп рд░рд┐рдкреЛрд░реНрдЯ", 
    "ЁЯЧСя╕П рдбрд┐рд▓реАрдЯ рдкреНрд░рд╡рд┐рд╖реНрдЯрд┐"
]
choice = st.sidebar.radio("NIKA рдореЗрдиреВ рдЪреБрдиреЗрдВ", menu)

# --- 1. рдирдпрд╛ рдХреНрд▓рд╛рдЗрдВрдЯ рдЬреЛрдбрд╝реЗрдВ ---
if choice == "тЮХ рдирдпрд╛ рдХреНрд▓рд╛рдЗрдВрдЯ рдЬреЛрдбрд╝реЗрдВ":
    st.subheader("ЁЯУЭ рдирдП рдХреНрд▓рд╛рдЗрдВрдЯ рдХрд╛ рдкреНрд░реЛрдлрд╝рд╛рдЗрд▓ рдПрд╡рдВ рд╡рд╛рд░реНрд╖рд┐рдХ рдлрд╝реАрд╕ рджрд░реНрдЬ рдХрд░реЗрдВ")
    
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("рдХреНрд▓рд╛рдЗрдВрдЯ рдХрд╛ рдирд╛рдо *")
        father_name = st.text_input("рдкрд┐рддрд╛ рдХрд╛ рдирд╛рдо")
        mobile = st.text_input("рдореЛрдмрд╛рдЗрд▓ рдирдВрдмрд░")
        pan_number = st.text_input("рдкреИрди рдХрд╛рд░реНрдб рдирдВрдмрд░ (PAN Card)")
        gst_number = st.text_input("GSTIN / рдЬреАрдПрд╕рдЯреА рдирдВрдмрд░")
        address = st.text_area("рдкреВрд░рд╛ рдкрддрд╛")

    with col2:
        annual_fee = st.number_input("рд╡рд╛рд░реНрд╖рд┐рдХ рддрдп рдлрд╝реАрд╕ (Annual Agreed Fee тВ╣) *", min_value=0.0, step=500.0)
        return_type = st.selectbox("рд░рд┐рдЯрд░реНрди рдХрд╛ рдкреНрд░рдХрд╛рд░ (Return Type):", [
            "Income Tax Return (ITR)", 
            "GST Return (GSTR-1 / 3B)", 
            "Both (ITR + GST)", 
            "Accounting / Consultancy"
        ])
        income_tax_status = st.selectbox("Income Tax рд░рд┐рдЯрд░реНрди рд╕реНрдЯреЗрдЯрд╕:", ["Pending (рд▓рдВрдмрд┐рдд)", "Filed (рдлрд╛рдЗрд▓ рд╣реЛ рдЧрдпрд╛)", "Not Applicable"])
        gst_status = st.selectbox("GST рд░рд┐рдЯрд░реНрди рд╕реНрдЯреЗрдЯрд╕:", ["Pending (рд▓рдВрдмрд┐рдд)", "Filed (рдлрд╛рдЗрд▓ рд╣реЛ рдЧрдпрд╛)", "Not Applicable"])

    st.markdown("---")
    if st.button("ЁЯТ╛ рдХреНрд▓рд╛рдЗрдВрдЯ рдкреНрд░реЛрдлрд╝рд╛рдЗрд▓ рд╕реЗрд╡ рдХрд░реЗрдВ"):
        if name.strip() == "":
            st.error("рдХреГрдкрдпрд╛ рдХреНрд▓рд╛рдЗрдВрдЯ рдХрд╛ рдирд╛рдо рджрд░реНрдЬ рдХрд░реЗрдВ!")
        else:
            today_date = datetime.now().strftime("%Y-%m-%d")
            c.execute('''
                INSERT INTO clients 
                (name, father_name, pan_number, gst_number, mobile, address, annual_fee, return_type, income_tax_status, gst_status, created_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (name.strip(), father_name, pan_number.strip().upper(), gst_number.strip().upper(), mobile, address, annual_fee, return_type, income_tax_status, gst_status, today_date))
            conn.commit()
            st.success(f"тЬЕ рдХреНрд▓рд╛рдЗрдВрдЯ '{name}' рдХреА рдкреНрд░реЛрдлрд╝рд╛рдЗрд▓ тВ╣{annual_fee:,.2f} рд╡рд╛рд░реНрд╖рд┐рдХ рдлрд╝реАрд╕ рдХреЗ рд╕рд╛рде рд╕реЗрд╡ рд╣реЛ рдЧрдИ рд╣реИ!")
            st.rerun()

# --- 2. рдирдпрд╛ рдкреЗрдореЗрдВрдЯ рдЬрдорд╛ рдХрд░реЗрдВ ---
elif choice == "ЁЯТ╡ рдирдпрд╛ рдкреЗрдореЗрдВрдЯ рдкреНрд░рд╛рдкреНрдд рдХрд░реЗрдВ":
    st.subheader("ЁЯТ╡ рдХреНрд▓рд╛рдЗрдВрдЯ рд╕реЗ рдлрд╝реАрд╕/рдкреЗрдореЗрдВрдЯ рдкреНрд░рд╛рдкреНрдд рдХрд░реЗрдВ")
    
    c.execute("SELECT id, name, pan_number, annual_fee FROM clients ORDER BY name ASC")
    client_rows = c.fetchall()
    
    if not client_rows:
        st.warning("рдбреЗрдЯрд╛рдмреЗрд╕ рдореЗрдВ рдХреЛрдИ рдХреНрд▓рд╛рдЗрдВрдЯ рдирд╣реАрдВ рдорд┐рд▓рд╛ред рдкрд╣рд▓реЗ 'рдирдпрд╛ рдХреНрд▓рд╛рдЗрдВрдЯ рдЬреЛрдбрд╝реЗрдВ' рд╡рд┐рдХрд▓реНрдк рд╕реЗ рдХреНрд▓рд╛рдЗрдВрдЯ рдмрдирд╛рдПрдБред")
    else:
        client_dict = {f"{row[1]} | PAN: {row[2]} (рд╡рд╛рд░реНрд╖рд┐рдХ рдлреАрд╕: тВ╣{row[3]:,.2f})": row[0] for row in client_rows}
        selected_client_str = st.selectbox("рдХреНрд▓рд╛рдЗрдВрдЯ рдЪреБрдиреЗрдВ:", list(client_dict.keys()))
        selected_client_id = client_dict[selected_client_str]
        
        # рд╡рд░реНрддрдорд╛рди рдмрдХрд╛рдпрд╛ рдХреА рдЧрдгрдирд╛ рдХрд░реЗрдВ
        c.execute("SELECT annual_fee FROM clients WHERE id = ?", (selected_client_id,))
        total_annual_fee = c.fetchone()[0]
        
        c.execute("SELECT SUM(amount_paid) FROM payments WHERE client_id = ?", (selected_client_id,))
        paid_res = c.fetchone()[0]
        total_paid = paid_res if paid_res else 0.0
        current_balance = total_annual_fee - total_paid
        
        st.info(f"ЁЯУМ **рд╡рд╛рд░реНрд╖рд┐рдХ рдлрд╝реАрд╕:** тВ╣{total_annual_fee:,.2f} | **рдЕрдм рддрдХ рдкреНрд░рд╛рдкреНрдд:** тВ╣{total_paid:,.2f} | **рд╡рд░реНрддрдорд╛рди рдмрдХрд╛рдпрд╛:** тВ╣{current_balance:,.2f}")
        
        col1, col2 = st.columns(2)
        with col1:
            payment_amount = st.number_input("рдкреНрд░рд╛рдкреНрдд рдХреА рдЧрдИ рд░рд╛рд╢рд┐ (тВ╣) *", min_value=0.0, step=100.0)
            payment_date = st.date_input("рднреБрдЧрддрд╛рди рдХреА рддрд╛рд░реАрдЦ", datetime.now()).strftime("%Y-%m-%d")
        
        with col2:
            payment_mode = st.selectbox("рднреБрдЧрддрд╛рди рдХрд╛ рдорд╛рдзреНрдпрдо (Payment Mode):", ["Cash (рдирдХрдж)", "Online / UPI", "Net Banking / Cheque"])
            remarks = st.text_input("рд╡рд┐рд╡рд░рдг / рдкрд╛рд╡рддреА рд╕рдВрдЦреНрдпрд╛ (Remarks)")

        st.markdown("---")
        if st.button("тЬЕ рдЬрдорд╛ рдкреНрд░рд╡рд┐рд╖реНрдЯрд┐ рд╕реБрд░рдХреНрд╖рд┐рдд рдХрд░реЗрдВ"):
            if payment_amount <= 0:
                st.error("рдХреГрдкрдпрд╛ рдкреНрд░рд╛рдкреНрдд рд░рд╛рд╢рд┐ рджрд░реНрдЬ рдХрд░реЗрдВ!")
            else:
                c.execute('''
                    INSERT INTO payments (client_id, payment_date, amount_paid, payment_mode, remarks)
                    VALUES (?, ?, ?, ?, ?)
                ''', (selected_client_id, payment_date, payment_amount, payment_mode, remarks))
                conn.commit()
                st.success("тЬЕ рдЬрдорд╛ рдкреНрд░рд╡рд┐рд╖реНрдЯрд┐ рд╕рдлрд▓рддрд╛ рдкреВрд░реНрд╡рдХ рд╕реЗрд╡ рд╣реЛ рдЧрдИ рд╣реИ!")
                st.rerun()

# --- 3. рдХреНрд▓рд╛рдЗрдВрдЯ рд▓реЗрдЬрд╝рд░ рдПрд╡рдВ рд╣рд┐рд╕рд╛рдм-рдХрд┐рддрд╛рдм ---
elif choice == "ЁЯФН рдХреНрд▓рд╛рдЗрдВрдЯ рд▓реЗрдЬрд╝рд░ рдПрд╡рдВ рд╣рд┐рд╕рд╛рдм-рдХрд┐рддрд╛рдм":
    st.subheader("ЁЯФН рдХреНрд▓рд╛рдЗрдВрдЯ рдХрд╛ рдкреВрд░рд╛ рд╣рд┐рд╕рд╛рдм рдПрд╡рдВ рд▓реЗрдЬрд╝рд░ рд╕реНрдЯреЗрдЯрдореЗрдВрдЯ (Statement)")
    
    c.execute("SELECT id, name, pan_number, mobile FROM clients ORDER BY name ASC")
    client_list = c.fetchall()
    
    if client_list:
        client_options = {f"{c_row[1]} | PAN: {c_row[2]} | рдореЛ: {c_row[3]}": c_row[0] for c_row in client_list}
        selected_client_label = st.selectbox("рдХреНрд▓рд╛рдЗрдВрдЯ рдЦреЛрдЬреЗрдВ рдпрд╛ рдЪреБрдиреЗрдВ:", list(client_options.keys()))
        client_id = client_options[selected_client_label]
        
        # рдХреНрд▓рд╛рдЗрдВрдЯ рд╡рд┐рд╡рд░рдг рдкреНрд░рд╛рдкреНрдд рдХрд░реЗрдВ
        c.execute("SELECT * FROM clients WHERE id = ?", (client_id,))
        client_info = c.fetchone()
        
        annual_fee = client_info[7]
        
        # рднреБрдЧрддрд╛рди рдЗрддрд┐рд╣рд╛рд╕ рдкреНрд░рд╛рдкреНрдд рдХрд░реЗрдВ
        df_payments = pd.read_sql_query('''
            SELECT payment_date as 'рддрд╛рд░реАрдЦ', amount_paid as 'рдкреНрд░рд╛рдкреНрдд рд░рд╛рд╢рд┐ (тВ╣)', payment_mode as 'рдорд╛рдзреНрдпрдо', remarks as 'рд╡рд┐рд╡рд░рдг'
            FROM payments WHERE client_id = ? ORDER BY id ASC
        ''', conn, params=(client_id,))
        
        total_paid = df_payments['рдкреНрд░рд╛рдкреНрдд рд░рд╛рд╢рд┐ (тВ╣)'].sum() if not df_payments.empty else 0.0
        remaining_balance = annual_fee - total_paid
        
        st.markdown("---")
        # рд▓реЗрдЬрд╝рд░ рдХрд╛ summary рдХрд╛рд░реНрдб
        m1, m2, m3 = st.columns(3)
        m1.metric("рдХреБрд▓ рд╡рд╛рд░реНрд╖рд┐рдХ рддрдп рдлрд╝реАрд╕", f"тВ╣{annual_fee:,.2f}")
        m2.metric("рдЕрдм рддрдХ рдХреБрд▓ рдкреНрд░рд╛рдкреНрдд рднреБрдЧрддрд╛рди", f"тВ╣{total_paid:,.2f}")
        
        if remaining_balance > 0:
            m3.metric("рдХреБрд▓ рдмрдХрд╛рдпрд╛ (Remaining Due)", f"тВ╣{remaining_balance:,.2f}")
        elif remaining_balance < 0:
            m3.metric("рдЕрдЧреНрд░рд┐рдо рдЬрдорд╛ (Advance Paid)", f"тВ╣{abs(remaining_balance):,.2f}")
        else:
            m3.metric("рдЦрд╛рддрд╛ рдЪреБрдХрддрд╛ (Nil Balance)", "тВ╣0.00")

        st.markdown("---")
        st.markdown(f"### ЁЯУЛ {client_info[1]} рдХрд╛ рдЬрдорд╛ рднреБрдЧрддрд╛рди рдЗрддрд┐рд╣рд╛рд╕ (Receipts):")
        
        if not df_payments.empty:
            st.dataframe(df_payments, use_container_width=True)
        else:
            st.warning("рдЗрд╕ рдХреНрд▓рд╛рдЗрдВрдЯ рджреНрд╡рд╛рд░рд╛ рдЕрднреА рддрдХ рдХреЛрдИ рднреБрдЧрддрд╛рди рдЬрдорд╛ рдирд╣реАрдВ рдХрд┐рдпрд╛ рдЧрдпрд╛ рд╣реИред")
            
        # рдХреНрд▓рд╛рдЗрдВрдЯ рд╕реНрдЯреЗрдЯрд╕ рдЕрдкрдбреЗрдЯ рдлрд╝реЙрд░реНрдо
        with st.expander("ЁЯУЭ рдХреНрд▓рд╛рдЗрдВрдЯ рдХреЗ рд░рд┐рдЯрд░реНрди рд╕реНрдЯреЗрдЯрд╕ рдпрд╛ рд╡рд╛рд░реНрд╖рд┐рдХ рдлрд╝реАрд╕ рдореЗрдВ рд╕рдВрд╢реЛрдзрди рдХрд░реЗрдВ"):
            with st.form("update_client_form"):
                new_annual_fee = st.number_input("рд╡рд╛рд░реНрд╖рд┐рдХ рдлреАрд╕ рдЕрдкрдбреЗрдЯ рдХрд░реЗрдВ", value=annual_fee)
                new_itr_status = st.selectbox("ITR рд╕реНрдЯреЗрдЯрд╕", ["Pending (рд▓рдВрдмрд┐рдд)", "Filed (рдлрд╛рдЗрд▓ рд╣реЛ рдЧрдпрд╛)", "Not Applicable"])
                new_gst_status = st.selectbox("GST рд╕реНрдЯреЗрдЯрд╕", ["Pending (рд▓рдВрдмрд┐рдд)", "Filed (рдлрд╛рдЗрд▓ рд╣реЛ рдЧрдпрд╛)", "Not Applicable"])
                
                if st.form_submit_button("рдЕрдкрдбреЗрдЯ рд╕реБрд░рдХреНрд╖рд┐рдд рдХрд░реЗрдВ"):
                    c.execute("UPDATE clients SET annual_fee = ?, income_tax_status = ?, gst_status = ? WHERE id = ?",
                              (new_annual_fee, new_itr_status, new_gst_status, client_id))
                    conn.commit()
                    st.success("рд╡рд┐рд╡рд░рдг рдЕрдкрдбреЗрдЯ рдХрд░ рджрд┐рдпрд╛ рдЧрдпрд╛ рд╣реИ!")
                    st.rerun()

# --- 4. рд╕рдВрдкреВрд░реНрдг рд╡рд┐рддреНрддреАрдп рд░рд┐рдкреЛрд░реНрдЯ ---
elif choice == "ЁЯУК рд╕рдВрдкреВрд░реНрдг рд╡рд┐рддреНрддреАрдп рд░рд┐рдкреЛрд░реНрдЯ":
    st.subheader("ЁЯУК NIKA рдУрд╡рд░рдСрд▓ рдмрд┐рдЬрд╝рдиреЗрд╕ рдбреИрд╢рдмреЛрд░реНрдб")
    
    df_clients = pd.read_sql_query("SELECT * FROM clients", conn)
    
    if df_clients.empty:
        st.info("рдбреЗрдЯрд╛рдмреЗрд╕ рдореЗрдВ рдХреЛрдИ рдХреНрд▓рд╛рдЗрдВрдЯ рджрд░реНрдЬ рдирд╣реАрдВ рд╣реИред")
    else:
        total_agreed = df_clients['annual_fee'].sum()
        total_collected = pd.read_sql_query("SELECT SUM(amount_paid) FROM payments", conn).iloc[0, 0]
        total_collected = total_collected if total_collected else 0.0
        total_outstanding = total_agreed - total_collected
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("рдХреБрд▓ рдХреНрд▓рд╛рдЗрдВрдЯреНрд╕", len(df_clients))
        c2.metric("рдХреБрд▓ рддрдп рд╡рд╛рд░реНрд╖рд┐рдХ рдлрд╝реАрд╕", f"тВ╣{total_agreed:,.2f}")
        c3.metric("рдХреБрд▓ рдкреНрд░рд╛рдкреНрдд рд░рд╛рд╢рд┐", f"тВ╣{total_collected:,.2f}")
        c4.metric("рдХреБрд▓ рдмрд╛рдЬрд╝рд╛рд░ рдореЗрдВ рдмрдХрд╛рдпрд╛", f"тВ╣{total_outstanding:,.2f}")
        
        st.markdown("---")
        st.markdown("### ЁЯУЛ рд╕рднреА рдХреНрд▓рд╛рдЗрдВрдЯреНрд╕ рдХрд╛ рдмрдХрд╛рдпрд╛ рд╡рд┐рд╡рд░рдг (Master Ledger)")
        
        master_df = pd.read_sql_query('''
            SELECT 
                c.id as 'ID',
                c.name as 'рдирд╛рдо',
                c.mobile as 'рдореЛрдмрд╛рдЗрд▓',
                c.pan_number as 'PAN',
                c.annual_fee as 'рддрдп рдлрд╝реАрд╕ (тВ╣)',
                COALESCE(SUM(p.amount_paid), 0) as 'рдкреНрд░рд╛рдкреНрдд рдлрд╝реАрд╕ (тВ╣)',
                (c.annual_fee - COALESCE(SUM(p.amount_paid), 0)) as 'рдмрдХрд╛рдпрд╛ рдлрд╝реАрд╕ (тВ╣)',
                c.income_tax_status as 'ITR рд╕реНрдЯреЗрдЯрд╕',
                c.gst_status as 'GST рд╕реНрдЯреЗрдЯрд╕'
            FROM clients c
            LEFT JOIN payments p ON c.id = p.client_id
            GROUP BY c.id
        ''', conn)
        
        st.dataframe(master_df, use_container_width=True)

# --- 5. рдбрд┐рд▓реАрдЯ рдкреНрд░рд╡рд┐рд╖реНрдЯрд┐ ---
elif choice == "ЁЯЧСя╕П рдбрд┐рд▓реАрдЯ рдкреНрд░рд╡рд┐рд╖реНрдЯрд┐":
    st.subheader("ЁЯЧСя╕П рдХреНрд▓рд╛рдЗрдВрдЯ рдЕрдерд╡рд╛ рдкреЗрдореЗрдВрдЯ рдкреНрд░рд╡рд┐рд╖реНрдЯрд┐ рд╣рдЯрд╛рдПрдБ")
    
    del_choice = st.radio("рдХреНрдпрд╛ рдбрд┐рд▓реАрдЯ рдХрд░рдирд╛ рдЪрд╛рд╣рддреЗ рд╣реИрдВ?", ["рдкреВрд░рд╛ рдХреНрд▓рд╛рдЗрдВрдЯ рдкреНрд░реЛрдлрд╝рд╛рдЗрд▓", "рдХреЗрд╡рд▓ рдПрдХ рдЧрд▓рдд рдкреЗрдореЗрдВрдЯ рдПрдВрдЯреНрд░реА"])
    
    if del_choice == "рдкреВрд░рд╛ рдХреНрд▓рд╛рдЗрдВрдЯ рдкреНрд░реЛрдлрд╝рд╛рдЗрд▓":
        c.execute("SELECT id, name, pan_number FROM clients")
        recs = c.fetchall()
        if recs:
            opts = {f"ID: {r[0]} | {r[1]} | PAN: {r[2]}": r[0] for r in recs}
            sel = st.selectbox("рдХреНрд▓рд╛рдЗрдВрдЯ рдЪреБрдиреЗрдВ:", list(opts.keys()))
            if st.button("тЭМ рдХреНрд▓рд╛рдЗрдВрдЯ рдФрд░ рдЙрд╕рдХрд╛ рдкреВрд░рд╛ рд░рд┐рдХреЙрд░реНрдб рд╣рдЯрд╛рдПрдВ"):
                cid = opts[sel]
                c.execute("DELETE FROM payments WHERE client_id = ?", (cid,))
                c.execute("DELETE FROM clients WHERE id = ?", (cid,))
                conn.commit()
                st.success("рд░рд┐рдХреЙрд░реНрдб рд╣рдЯрд╛ рджрд┐рдпрд╛ рдЧрдпрд╛!")
                st.rerun()
    else:
        df_p = pd.read_sql_query('''
            SELECT p.id as 'Payment ID', c.name as 'рдирд╛рдо', p.payment_date as 'рддрд╛рд░реАрдЦ', p.amount_paid as 'рд░рд╛рд╢рд┐ (тВ╣)'
            FROM payments p JOIN clients c ON p.client_id = c.id ORDER BY p.id DESC
        ''', conn)
        if not df_p.empty:
            st.dataframe(df_p, use_container_width=True)
            p_id = st.number_input("рд╣рдЯрд╛рдиреЗ рдХреЗ рд▓рд┐рдП Payment ID рджрд░реНрдЬ рдХрд░реЗрдВ:", min_value=1, step=1)
            if st.button("тЭМ рдпрд╣ рднреБрдЧрддрд╛рди рдкреНрд░рд╡рд┐рд╖реНрдЯрд┐ рд╣рдЯрд╛рдПрдВ"):
                c.execute("DELETE FROM payments WHERE id = ?", (p_id,))
                conn.commit()
                st.success("рднреБрдЧрддрд╛рди рд░рд┐рдХреЙрд░реНрдб рд╣рдЯрд╛ рджрд┐рдпрд╛ рдЧрдпрд╛!")
                st.rerun()
