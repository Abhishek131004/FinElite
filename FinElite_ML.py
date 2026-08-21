import os
import secrets
import numpy as np
import pandas as pd
import seaborn as sb
import matplotlib.pyplot as plt
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="FinElite : Your Credit Game Changer",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# THEME / CSS
# ============================================================
st.markdown("""
<style>
.stApp {
    background: #f5f7fb;
    color: #374151;
}
.block-container {
    max-width: 1650px;
    width: 100%;
    padding-top: 1.8rem !important;
    padding-bottom: 2rem;
    padding-left: 2rem;
    padding-right: 2rem;
}
section[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid #374151;
}
section[data-testid="stSidebar"] * {
    color: #374151 !important;
}
.dashboard-title {
    display: block;
    width: 100%;
    box-sizing: border-box;
    font-size: clamp(1.7rem, 2.8vw, 2.45rem);
    font-weight: 800;
    color: #2563eb;
    margin: 0 0 10px 0;
    padding: 2px 0 4px 0;
    line-height: 1.35;
    white-space: normal;
    overflow: visible;
    word-break: normal;
    overflow-wrap: normal;
    text-align: left;
}
.dashboard-subtitle {
    display: block;
    width: 100%;
    box-sizing: border-box;
    color: #6b7280;
    font-size: 1rem;
    line-height: 1.5;
    margin: 0 0 24px 0;
    padding: 0;
}
.section-title {
    background: linear-gradient(90deg, #1e40af, #2563eb);
    padding: 10px 16px;
    border-radius: 10px;
    color: white;
    font-weight: 700;
    margin: 18px 0 12px 0;
}
.kpi-card {
    width: 100%;
    min-width: 0;
    min-height: 112px;
    box-sizing: border-box;
    background: #ffffff;
    border: 1px solid #374151;
    border-radius: 14px;
    padding: 12px 6px;
    text-align: center;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    overflow: hidden;
    box-shadow: 0 4px 14px rgba(0,0,0,.30);
}
.kpi-title {
    width: 100%;
    color: #6b7280;
    font-size: .62rem;
    line-height: 1.25;
    text-transform: uppercase;
    letter-spacing: .25px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.kpi-value {
    width: 100%;
    color: #2563eb;
    font-size: 1.35rem;
    line-height: 1.2;
    font-weight: 750;
    margin-top: 7px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

/* LOGIN PAGE */
.login-wrapper {
    max-width: 560px;
    margin: 1.5vh auto 0 auto;
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 18px;
    padding: 20px 30px 18px 30px;
    box-shadow: 0 12px 35px rgba(15, 23, 42, 0.08);
}
.login-title {
    text-align: center;
    font-size: 2rem;
    font-weight: 800;
    color: #2563eb;
    line-height: 1.2;
    margin-bottom: 5px;
}
.login-subtitle {
    text-align: center;
    color: #6b7280;
    margin-bottom: 12px;
}
.login-icon {
    text-align: center;
    font-size: 2.7rem;
    margin-bottom: 2px;
}
.captcha-display {
    background: #f8fafc;
    border: 1px dashed #3b82f6;
    border-radius: 10px;
    padding: 9px;
    text-align: center;
    color: #1e40af;
    font-size: 1.05rem;
    font-weight: 800;
    letter-spacing: 2px;
    margin: 6px 0 8px 0;
}
.prediction-box-high {
    background: #fef2f2;
    border: 2px solid #ef4444;
    border-radius: 14px;
    padding: 20px;
    text-align: center;
    box-shadow: 0 4px 15px rgba(239, 68, 68, 0.15);
    margin-top: 10px;
}
.prediction-box-std {
    background: #f0fdf4;
    border: 2px solid #22c55e;
    border-radius: 14px;
    padding: 20px;
    text-align: center;
    box-shadow: 0 4px 15px rgba(34, 197, 94, 0.15);
    margin-top: 10px;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# 🔐 LOGIN SYSTEM
# ============================================================
LOGIN_USERNAME = "admin"
LOGIN_PASSWORD = "Admin@123"

def generate_captcha():
    a = secrets.randbelow(9) + 1
    b = secrets.randbelow(9) + 1
    op = secrets.choice(["+", "-"])
    if op == "-" and b > a:
        a, b = b, a
    answer = a + b if op == "+" else a - b
    return f"{a} {op} {b} = ?", answer

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "captcha_question" not in st.session_state:
    q, ans = generate_captcha()
    st.session_state.captcha_question = q
    st.session_state.captcha_answer = ans

if not st.session_state.authenticated:
    st.markdown(
        '<div class="login-wrapper">'
        '<div class="login-icon">💳</div>'
        '<div class="login-title">Welcome to FinElite</div>'
        '<div class="login-subtitle">Your Credit Game Changer</div>'
        '</div>',
        unsafe_allow_html=True
    )

    _, login_col, _ = st.columns([1, 2, 1])
    with login_col:
        st.markdown("### 🔐 Login")
        username = st.text_input("👤 Username", placeholder="Enter username", key="login_username")
        password = st.text_input("🔒 Password", type="password", placeholder="Enter password", key="login_password")

        st.markdown(
            f'<div class="captcha-display">🧩 CAPTCHA&nbsp;&nbsp; {st.session_state.captcha_question}</div>',
            unsafe_allow_html=True
        )
        captcha = st.text_input("Enter CAPTCHA Answer", placeholder="Enter answer", key="login_captcha")

        if st.button("🔓 Login to Dashboard", type="primary", use_container_width=True, key="login_button"):
            try:
                captcha_ok = int(captcha.strip()) == int(st.session_state.captcha_answer)
            except (ValueError, AttributeError):
                captcha_ok = False

            if username == LOGIN_USERNAME and password == LOGIN_PASSWORD and captcha_ok:
                st.session_state.authenticated = True
                st.session_state.auth_error = ""
                st.rerun()
            else:
                st.session_state.auth_error = "❌ Invalid username, password, or CAPTCHA."
                q, ans = generate_captcha()
                st.session_state.captcha_question = q
                st.session_state.captcha_answer = ans
                st.rerun()

        if st.session_state.get("auth_error"):
            st.error(st.session_state.auth_error)

        st.caption("Authorized users only • Login required to access dashboard.")

    st.stop()

# ============================================================
# 🚪 LOGOUT
# ============================================================
with st.sidebar:
    st.markdown("### 🔐 Session")
    if st.button("🚪 Logout", use_container_width=True, key="logout_button"):
        st.session_state.authenticated = False
        st.session_state.auth_error = ""
        q, ans = generate_captcha()
        st.session_state.captcha_question = q
        st.session_state.captcha_answer = ans
        st.rerun()
    st.markdown("---")

# ============================================================
# MOCK DATA GENERATOR (FALLBACK)
# ============================================================
def generate_mock_data(n=400):
    np.random.seed(42)
    age = np.random.randint(18, 70, n)
    annual_income = np.random.uniform(200000, 2500000, n)
    credit_score = np.random.randint(300, 850, n)
    utilization = np.random.uniform(5, 95, n)
    spending = annual_income * np.random.uniform(0.1, 0.4, n) / 12
    missed_payments = np.random.choice([0, 1, 2, 3, 4], n, p=[0.7, 0.15, 0.08, 0.04, 0.03])
    late_payments = missed_payments + np.random.randint(0, 3, n)
    defaults = np.where(missed_payments > 2, 1, 0)
    
    credit_limit = (annual_income * 0.3) + (credit_score * 150) - (utilization * 200) + np.random.normal(0, 10000, n)
    credit_limit = np.maximum(10000, credit_limit)

    return pd.DataFrame({
        "Customer_ID": [f"CUST_{1000+i}" for i in range(n)],
        "Age": age,
        "Gender": np.random.choice(["Male", "Female"], n),
        "Employment_Type": np.random.choice(["Salaried", "Self-Employed", "Business"], n),
        "Occupation": np.random.choice(["IT & Tech", "Healthcare", "Finance", "Retail", "Manufacturing"], n),
        "Residential_Status": np.random.choice(["Owned", "Rented", "Mortgaged"], n),
        "KYC_Status": np.random.choice(["Complete", "Pending"], n, p=[0.9, 0.1]),
        "Fraud_Flag": np.random.choice(["No", "Yes"], n, p=[0.95, 0.05]),
        "Annual_Income": annual_income,
        "Credit_Score": credit_score,
        "Credit_Utilization": utilization,
        "Avg_Monthly_Spending": spending,
        "Missed_Payments": missed_payments,
        "Late_Payment_Count": late_payments,
        "Number_of_Defaults": defaults,
        "Credit_Limit": credit_limit
    })

# ============================================================
# DATA LOADING & INITIAL PREPROCESSING
# ============================================================
@st.cache_data
def load_data(uploaded_file=None):
    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file)
    else:
        paths = [
            "Credir_Card_Bank.xlsx",
            "Credir_Card_Bank(4).xlsx",
            "../Datasets/Credir_Card_Bank.xlsx",
            "../DataSets/Credir_Card_Bank.xlsx"
        ]
        path = next((p for p in paths if os.path.exists(p)), None)
        df = pd.read_excel(path) if path else generate_mock_data()

    df.columns = df.columns.astype(str).str.strip().str.replace(" ", "_", regex=False)

    numeric_cols = [
        "Age", "Monthly_Income", "Annual_Income", "Credit_Score",
        "Years_With_Bank", "Existing_Credit_Cards", "Existing_Credit_Limit",
        "Loan_Count", "EMI_Per_Month", "Debt_To_Income_Ratio",
        "Savings_Balance", "Investment_Value", "Avg_Monthly_Transactions",
        "Avg_Monthly_Spending", "Credit_Utilization", "Credit_History_Years",
        "Missed_Payments", "Late_Payment_Count", "Number_of_Defaults",
        "Credit_Limit"
    ]
    for c in numeric_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    if "Age" in df.columns:
        df["Age_Group"] = pd.cut(
            df["Age"],
            bins=[18, 25, 35, 50, 65, 100],
            labels=["18-25", "26-35", "36-50", "51-65", "65+"],
            include_lowest=True
        )

    if "Credit_Score" in df.columns:
        def credit_band(x):
            if x < 580: return "Poor"
            if x < 670: return "Fair"
            if x < 740: return "Good"
            if x < 800: return "Very Good"
            return "Excellent"
        df["Credit_Band"] = df["Credit_Score"].apply(credit_band)

    if "Number_of_Defaults" in df.columns:
        df["default_payment_next_month"] = (df["Number_of_Defaults"] > 0).astype(int)

    required = {"Credit_Score", "Credit_Utilization", "Missed_Payments"}
    if required.issubset(df.columns):
        high_risk = (
            (df["Credit_Score"] < 600)
            | (df["Credit_Utilization"] > 75)
            | (df["Missed_Payments"] >= 3)
        )
        df["High_Risk_Flag"] = np.where(high_risk, "High Risk", "Standard")

    return df

# ============================================================
# SIDEBAR FILTERS
# ============================================================
st.sidebar.title("🎛️ Banking Control Center")
uploaded_file = st.sidebar.file_uploader("📁 Upload Credit Card Excel", type=["xlsx", "xls"])

try:
    df = load_data(uploaded_file)
except Exception as e:
    st.error(f"❌ {e}")
    st.stop()

st.sidebar.markdown("---")
st.sidebar.subheader("🎯 Customer Filters")

def multi_filter(label, col):
    if col not in df.columns:
        return None
    opts = sorted(df[col].dropna().astype(str).unique().tolist())
    return st.sidebar.multiselect(label, opts, default=opts)

gender = multi_filter("Gender", "Gender")
employment = multi_filter("Employment Type", "Employment_Type")
residential = multi_filter("Residential Status", "Residential_Status")
kyc = multi_filter("KYC Status", "KYC_Status")
fraud = multi_filter("Fraud Flag", "Fraud_Flag")

age_range = st.sidebar.slider("👥 Age Range", int(df.Age.min()), int(df.Age.max()), (int(df.Age.min()), int(df.Age.max()))) if "Age" in df.columns else None
income_range = st.sidebar.slider("💰 Annual Income", float(df.Annual_Income.min()), float(df.Annual_Income.max()), (float(df.Annual_Income.min()), float(df.Annual_Income.max())), format="₹%.0f") if "Annual_Income" in df.columns else None
score_range = st.sidebar.slider("⭐ Credit Score", int(df.Credit_Score.min()), int(df.Credit_Score.max()), (int(df.Credit_Score.min()), int(df.Credit_Score.max()))) if "Credit_Score" in df.columns else None
utilization_max = st.sidebar.slider("💳 Max Credit Utilization (%)", 0, 100, 100) if "Credit_Utilization" in df.columns else 100

risk_segment = st.sidebar.radio("🛡️ Risk Segment", ["All Customers", "High Risk Only", "Standard Risk Only"], index=0)
require_kyc = st.sidebar.checkbox("🔒 KYC Complete Only", False)

# ============================================================
# APPLY FILTERS
# ============================================================
f = df.copy()

def apply_multi(data, col, selected):
    return data[data[col].astype(str).isin(selected)] if selected else data

for col, selected in [("Gender", gender), ("Employment_Type", employment), ("Residential_Status", residential), ("KYC_Status", kyc), ("Fraud_Flag", fraud)]:
    if col in f.columns:
        f = apply_multi(f, col, selected)

if age_range and "Age" in f.columns: f = f[f.Age.between(age_range[0], age_range[1])]
if income_range and "Annual_Income" in f.columns: f = f[f.Annual_Income.between(income_range[0], income_range[1])]
if score_range and "Credit_Score" in f.columns: f = f[f.Credit_Score.between(score_range[0], score_range[1])]
if "Credit_Utilization" in f.columns: f = f[f.Credit_Utilization <= utilization_max]
if require_kyc and "KYC_Status" in f.columns: f = f[f.KYC_Status == "Complete"]
if risk_segment == "High Risk Only" and "High_Risk_Flag" in f.columns: f = f[f.High_Risk_Flag == "High Risk"]
elif risk_segment == "Standard Risk Only" and "High_Risk_Flag" in f.columns: f = f[f.High_Risk_Flag == "Standard"]

st.sidebar.info(f"Showing **{len(f):,}** of **{len(df):,}** customers")

if f.empty:
    st.warning("⚠️ No customers match the selected filters. Please widen the filters.")
    st.stop()

# ============================================================
# HELPERS
# ============================================================
def money(x):
    x = float(x)
    if abs(x) >= 1e7: return f"₹{x/1e7:.2f} Cr"
    if abs(x) >= 1e5: return f"₹{x/1e5:.2f} L"
    return f"₹{x:,.0f}"

def chart(fig, height=380):
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(255,255,255,0)",
        plot_bgcolor="rgba(255,255,255,0)",
        font=dict(color="#374151"),
        margin=dict(l=20, r=20, t=55, b=20),
        height=height
    )
    st.plotly_chart(fig, use_container_width=True)

# ============================================================
# HEADER & KPIS
# ============================================================
st.markdown('<div class="dashboard-title">💳 FinElite : Your Credit Game Changer</div>', unsafe_allow_html=True)
st.markdown('<div class="dashboard-subtitle">An AI Powered Credit Card Financial Dashboard & ML Pipeline</div>', unsafe_allow_html=True)

total_customers = len(f)
avg_spending = f["Avg_Monthly_Spending"].mean() if "Avg_Monthly_Spending" in f else 0
avg_income = f["Annual_Income"].mean() if "Annual_Income" in f else 0
avg_score = f["Credit_Score"].mean() if "Credit_Score" in f else 0
avg_util = f["Credit_Utilization"].mean() if "Credit_Utilization" in f else 0
default_rate = (f["default_payment_next_month"].mean() * 100) if "default_payment_next_month" in f else 0
high_risk_count = (f["High_Risk_Flag"] == "High Risk").sum() if "High_Risk_Flag" in f else 0

kpis = [
    ("👥 Customers", f"{total_customers:,}"),
    ("💰 Avg Monthly Spending", money(avg_spending)),
    ("📈 Avg Annual Income", money(avg_income)),
    ("⭐ Avg Credit Score", f"{avg_score:,.0f}"),
    ("💳 Avg Utilization", f"{avg_util:.1f}%"),
    ("⚠️ Default Rate", f"{default_rate:.2f}%"),
    ("🛡️ High Risk Customers", f"{high_risk_count:,}")
]
cols = st.columns(len(kpis), gap="small")
for col, (title, value) in zip(cols, kpis):
    with col:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">{title}</div><div class="kpi-value">{value}</div></div>', unsafe_allow_html=True)

# ============================================================
# EXPLORATORY DATA ANALYSIS (EDA)
# ============================================================
st.markdown('<div class="section-title">📊 Exploratory Data Analysis & Customer Behaviour</div>', unsafe_allow_html=True)

c1, c2 = st.columns([1, 1])
with c1:
    dim_label = st.selectbox("Compare Spending By", ["Age Group", "Gender", "Employment Type", "Occupation", "Residential Status", "KYC Status", "Fraud Flag"])
with c2:
    chart_type = st.selectbox("Chart Type", ["Bar Chart", "Box Plot", "Violin Plot"])

dim_map = {"Age Group": "Age_Group", "Gender": "Gender", "Employment Type": "Employment_Type", "Occupation": "Occupation", "Residential Status": "Residential_Status", "KYC Status": "KYC_Status", "Fraud Flag": "Fraud_Flag"}
dim = dim_map[dim_label]

if dim in f.columns and "Avg_Monthly_Spending" in f.columns:
    if chart_type == "Bar Chart":
        s = f.groupby(dim, observed=True).agg(Average_Spending=("Avg_Monthly_Spending", "mean")).reset_index()
        fig = px.bar(s, x=dim, y="Average_Spending", color=dim, text_auto=".2s", title=f"Average Monthly Spending by {dim_label}")
    elif chart_type == "Box Plot":
        fig = px.box(f, x=dim, y="Avg_Monthly_Spending", color=dim, points="outliers", title=f"Spending Distribution by {dim_label}")
    else:
        fig = px.violin(f, x=dim, y="Avg_Monthly_Spending", color=dim, box=True, title=f"Spending Pattern by {dim_label}")
    chart(fig, 400)

c1, c2, c3 = st.columns(3)
with c1:
    if "Avg_Monthly_Spending" in f.columns:
        chart(px.histogram(f, x="Avg_Monthly_Spending", nbins=30, marginal="box", title="💰 Monthly Spending Distribution"), 360)
with c2:
    if {"Age_Group", "Avg_Monthly_Spending"}.issubset(f.columns):
        age_spend = f.groupby("Age_Group", observed=True)["Avg_Monthly_Spending"].mean().reset_index()
        chart(px.bar(age_spend, x="Age_Group", y="Avg_Monthly_Spending", color="Avg_Monthly_Spending", title="👥 Average Spending by Age Group"), 360)
with c3:
    if {"Annual_Income", "Avg_Monthly_Spending"}.issubset(f.columns):
        chart(px.scatter(f, x="Annual_Income", y="Avg_Monthly_Spending", color="Credit_Score" if "Credit_Score" in f.columns else None, title="💵 Income vs Monthly Spending"), 360)

# ============================================================
# 🚨 CREDIT RISK & DECISION INTELLIGENCE
# ============================================================
st.markdown('<div class="section-title">🚨 Credit Risk & Decision Intelligence</div>', unsafe_allow_html=True)
st.write("Monitor default indicators, analyze risk drivers across segments, and evaluate real-time exposure.")

# 1. Portfolio Risk Metrics
st.markdown("#### 📈 Portfolio Risk Metrics")
m1, m2, m3, m4 = st.columns(4)

def_rate_val = (f["default_payment_next_month"].mean() * 100) if "default_payment_next_month" in f else 0.0
total_defaulters = f["default_payment_next_month"].sum() if "default_payment_next_month" in f else 0
avg_late = f["Late_Payment_Count"].mean() if "Late_Payment_Count" in f else 0.0
high_risk_exposure = (f["High_Risk_Flag"] == "High Risk").sum() if "High_Risk_Flag" in f else 0

m1.metric("Default Rate", f"{def_rate_val:.2f}%")
m2.metric("Defaulter Count", f"{total_defaulters:,}")
m3.metric("Avg Late Payments", f"{avg_late:.2f}")
m4.metric("High-Risk Exposure", f"{high_risk_exposure:,}")

st.markdown("---")

# 2. Default Drivers Breakdown
st.markdown("#### 🧬 Default Drivers Breakdown")
col_drv1, col_drv2 = st.columns(2)

with col_drv1:
    if {"Age_Group", "default_payment_next_month"}.issubset(f.columns):
        age_def = f.groupby("Age_Group", observed=True)["default_payment_next_month"].mean().reset_index()
        age_def["Default Rate (%)"] = age_def["default_payment_next_month"] * 100
        fig_age_def = px.bar(
            age_def, x="Age_Group", y="Default Rate (%)",
            color="Default Rate (%)", color_continuous_scale="Reds",
            title="Default Distribution by Demographic Age Group"
        )
        chart(fig_age_def, 350)

with col_drv2:
    occ_col = "Occupation" if "Occupation" in f.columns else ("Employment_Type" if "Employment_Type" in f.columns else None)
    if occ_col and "default_payment_next_month" in f.columns:
        occ_def = f.groupby(occ_col, observed=True)["default_payment_next_month"].mean().reset_index()
        occ_def["Default Rate (%)"] = occ_def["default_payment_next_month"] * 100
        fig_occ_def = px.bar(
            occ_def, x=occ_col, y="Default Rate (%)",
            color="Default Rate (%)", color_continuous_scale="Oranges",
            title=f"Default Distribution by {occ_col} Segment"
        )
        chart(fig_occ_def, 350)

st.markdown("---")

# 3. Feature Correlation Engine
st.markdown("#### 🔍 Feature Correlation Engine")
num_df = f.select_dtypes(include=[np.number])

if "default_payment_next_month" in num_df.columns:
    corr_target = num_df.corr()["default_payment_next_month"].drop("default_payment_next_month").abs().sort_values(ascending=False).reset_index()
    corr_target.columns = ["Feature", "Absolute Correlation"]
    
    fig_corr_bar = px.bar(
        corr_target.head(8), x="Absolute Correlation", y="Feature", orientation="h",
        color="Absolute Correlation", color_continuous_scale="Viridis",
        title="Top Numerical Factors Correlated with Customer Loan Defaults"
    )
    fig_corr_bar.update_layout(yaxis={'categoryorder': 'total ascending'})
    chart(fig_corr_bar, 380)

st.markdown("---")

# 4. Underwriter Risk Simulator
st.markdown("#### ⚡ Underwriter Risk Simulator")
st.write("Real-time interactive scoring tool to instantly classify new applicants based on risk profile.")

sim_col1, sim_col2, sim_col3 = st.columns(3)

with sim_col1:
    sim_score = st.slider("Credit Score", min_value=300, max_value=850, value=650, key="sim_score")

with sim_col2:
    sim_util = st.slider("Credit Utilization (%)", min_value=0.0, max_value=100.0, value=45.0, key="sim_util")

with sim_col3:
    sim_missed = st.number_input("Missed Payments Count", min_value=0, max_value=20, value=1, key="sim_missed")

if st.button("🛡️ Simulate Underwriting Risk Assessment", type="primary", use_container_width=True):
    is_high_risk = (sim_score < 600) or (sim_util > 75.0) or (sim_missed >= 3)
    
    if is_high_risk:
        st.markdown("""
        <div class="prediction-box-high">
            <h3 style="color:#dc2626;margin:0;">Risk Classification Result</h3>
            <h1 style="color:#ef4444;font-size:2.8rem;margin:10px 0;">HIGH RISK</h1>
            <p style="color:#991b1b;margin:0;">Applicant breached risk thresholds (Low Credit Score, High Utilization, or Excessive Missed Payments).</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="prediction-box-std">
            <h3 style="color:#16a34a;margin:0;">Risk Classification Result</h3>
            <h1 style="color:#22c55e;font-size:2.8rem;margin:10px 0;">STANDARD RISK</h1>
            <p style="color:#166534;margin:0;">Applicant profile is within safe credit operational parameters.</p>
        </div>
        """, unsafe_allow_html=True)

# ============================================================
# FOOTER
# ============================================================
st.divider()
st.caption("💳 FinElite : Your Credit Game Changer | Python • Streamlit • Pandas • NumPy • Plotly • Scikit-Learn • XGBoost")
