import streamlit as st

st.subheader("🧮 Automatic Computation of Taxable Income")

# --- INPUT SECTION ---
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📥 Heads of Income")
    
    # 1. Salary Income
    income_salary = st.number_input("1. Income from Salary (₹)", min_value=0.0, step=1000.0)
    
    # 2. House Property Income (Auto-calculated after 30% Deduction)
    gross_rent = st.number_input("2. Gross Rent / Arrears Received (₹)", min_value=0.0, step=1000.0)
    std_deduction_hp = gross_rent * 0.30  # 30% Deduction u/s 24(a)
    net_house_property = max(0.0, gross_rent - std_deduction_hp)
    st.caption(f"ℹ️ Less 30% Standard Deduction: ₹{std_deduction_hp:,.2f} | Net HP Income: ₹{net_house_property:,.2f}")
    
    # 3. Business & Profession Income (PGBP)
    income_business = st.number_input("3. Net Profit / Business Income (PGBP) (₹)", min_value=0.0, step=1000.0)
    
    # 4. Capital Gains
    income_capital_gains = st.number_input("4. Capital Gains (STCG / LTCG) (₹)", min_value=0.0, step=1000.0)
    
    # 5. Income from Other Sources
    income_other_sources = st.number_input("5. Income from Other Sources (Interest/Misc) (₹)", min_value=0.0, step=1000.0)

with col2:
    st.markdown("### 📉 Deductions (Chapter VI-A)")
    
    deduction_80c = st.number_input("Section 80C (PPF, LIC, ELSS, etc.) (₹)", min_value=0.0, max_value=150000.0, step=1000.0)
    deduction_80d = st.number_input("Section 80D (Health Insurance) (₹)", min_value=0.0, step=1000.0)
    deduction_other = st.number_input("Other Deductions (80TTA, 80G, etc.) (₹)", min_value=0.0, step=1000.0)
    
    exempt_income = st.number_input("Agricultural / Exempt Income u/s 10 (₹)", min_value=0.0, step=1000.0)

# --- AUTOMATIC CALCULATION LOGIC ---

# 1. Total Gross Income Calculation
gross_total_income = (
    income_salary + 
    net_house_property + 
    income_business + 
    income_capital_gains + 
    income_other_sources
)

# 2. Total Deductions Calculation
total_deductions = deduction_80c + deduction_80d + deduction_other

# 3. Net Taxable Income Calculation
taxable_income = max(0.0, gross_total_income - total_deductions)

# 4. Section 288A Rounding Off (Nearest multiple of 10)
taxable_income_rounded = round(taxable_income, -1)

# --- DISPLAY COMPUTATION SUMMARY ---
st.markdown("---")
st.markdown("### 📊 Automatic Computation Summary")

res_col1, res_col2 = st.columns(2)

with res_col1:
    st.metric(label="Gross Total Income (GTI)", value=f"₹{gross_total_income:,.2f}")
    st.write(f"- Income from House Property (Net): ₹{net_house_property:,.2f}")
    st.write(f"- Income from Business / Profession: ₹{income_business:,.2f}")
    st.write(f"- Income from Other Sources: ₹{income_other_sources:,.2f}")

with res_col2:
    st.metric(label="Total Deductions (Chapter VI-A)", value=f"₹{total_deductions:,.2f}")
    st.metric(label="Net Taxable Income (Rounded Off u/s 288A)", value=f"₹{taxable_income_rounded:,.2f}")
