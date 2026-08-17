import os
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

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
.chart-card {
    background: #ffffff;
    border: 1px solid #374151;
    border-radius: 14px;
    padding: 10px 14px 4px 14px;
    margin-bottom: 12px;
}
.insight-card {
    background: #ffffff;
    border-left: 4px solid #16a34a;
    border-radius: 8px;
    padding: 12px 16px;
    margin: 7px 0;
}
.risk-card {
    background: #ffffff;
    border-left: 4px solid #ea580c;
    border-radius: 8px;
    padding: 12px 16px;
    margin: 7px 0;
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

/* Keep the complete login screen visible without manual scrolling */
body:has(.login-wrapper) {
    overflow: hidden !important;
}

div[data-testid="stAppViewContainer"] {
    min-height: 100vh !important;
}

div[data-testid="stAppViewContainer"] > section:first-child {
    min-height: 100vh !important;
}

.login-wrapper + * {
    margin-top: 0 !important;
}
.login-title { text-align:center; font-size:2.2rem; font-weight:800; color:#2563eb; line-height:1.25; margin-bottom:8px; }
.login-subtitle { text-align:center; color:#6b7280; margin-bottom:25px; }
.login-icon { text-align:center; font-size:3.2rem; margin-bottom:5px; }
.captcha-display { background:#f8fafc; border:1px dashed #3b82f6; border-radius:10px; padding:13px; text-align:center; color:#1e40af; font-size:1.2rem; font-weight:800; letter-spacing:2px; margin:8px 0 10px 0; }


@media (max-width: 1100px) {
    .kpi-title { font-size: .58rem; }
    .kpi-value { font-size: 1.15rem; }
}
@media (max-width: 700px) {
    .kpi-card { padding: 10px 4px; min-height: 100px; }
    .kpi-title { font-size: .55rem; }
    .kpi-value { font-size: 1rem; }
}


/* Professional Light Banking UI */
div[data-baseweb="input"] > div,
div[data-baseweb="select"] > div,
div[data-baseweb="textarea"] > div {
    background-color: #ffffff !important;
    border-color: #d1d5db !important;
}

input, textarea {
    color: #1f2937 !important;
}

.stButton > button {
    border-radius: 9px !important;
    border: 1px solid #d1d5db !important;
}

.stButton > button[kind="primary"] {
    background: #2563eb !important;
    color: #ffffff !important;
    border-color: #2563eb !important;
}

section[data-testid="stSidebar"] {
    box-shadow: 2px 0 12px rgba(15, 23, 42, 0.05);
}

.stSlider [data-baseweb="slider"] {
    color: #2563eb !important;
}


@media (max-height: 800px) {
    .login-wrapper {
        margin-top: 0.5vh;
        padding: 14px 24px 12px 24px;
    }
    .login-title { font-size: 1.75rem; }
    .login-icon { font-size: 2.3rem; }
    .login-subtitle { margin-bottom: 8px; }
}

</style>
""", unsafe_allow_html=True)

# Keep login page positioned at the top on first load
st.markdown("\n<script>\n(function () {\n    function keepLoginAtTop() {\n        const login = document.querySelector('.login-wrapper');\n        if (login) {\n            window.scrollTo(0, 0);\n            document.documentElement.scrollTop = 0;\n            document.body.scrollTop = 0;\n        }\n    }\n    keepLoginAtTop();\n    setTimeout(keepLoginAtTop, 100);\n    setTimeout(keepLoginAtTop, 400);\n})();\n</script>\n", unsafe_allow_html=True)


# ============================================================
# 🔐 LOGIN SYSTEM
# ============================================================
LOGIN_USERNAME = "admin"
LOGIN_PASSWORD = "Admin@123"

def generate_captcha():
    import secrets
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
# DATA LOADING
# ============================================================
@st.cache_data
def load_data(uploaded_file=None):
    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file)
    else:
        paths = [
            "Credir_Card_Bank.xlsx",
            "Credir_Card_Bank(4).xlsx",
            "../DataSets/Credir_Card_Bank.xlsx"
        ]
        path = next((p for p in paths if os.path.exists(p)), None)
        if path is None:
            raise FileNotFoundError(
                "Credir_Card_Bank.xlsx not found. Upload the Excel file from the sidebar."
            )
        df = pd.read_excel(path)

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

    # Age group
    if "Age" in df.columns:
        df["Age_Group"] = pd.cut(
            df["Age"],
            bins=[18, 25, 35, 50, 65, 100],
            labels=["18-25", "26-35", "36-50", "51-65", "65+"],
            include_lowest=True
        )

    # Credit band
    if "Credit_Score" in df.columns:
        def credit_band(x):
            if x < 580: return "Poor"
            if x < 670: return "Fair"
            if x < 740: return "Good"
            if x < 800: return "Very Good"
            return "Excellent"
        df["Credit_Band"] = df["Credit_Score"].apply(credit_band)

    # Default target
    if "Number_of_Defaults" in df.columns:
        df["default_payment_next_month"] = (
            df["Number_of_Defaults"] > 0
        ).astype(int)

    # High-risk flag used by the risk dashboard
    required = {"Credit_Score", "Credit_Utilization", "Missed_Payments"}
    if required.issubset(df.columns):
        high_risk = (
            (df["Credit_Score"] < 600)
            | (df["Credit_Utilization"] > 75)
            | (df["Missed_Payments"] >= 3)
        )
        df["High_Risk_Flag"] = np.where(high_risk, "High Risk", "Standard")

    # Custom risk indicator from the financial-risk dashboard
    risk_cols = {
        "Debt_To_Income_Ratio", "Credit_Utilization",
        "Missed_Payments", "Late_Payment_Count", "Number_of_Defaults"
    }
    if risk_cols.issubset(df.columns):
        df["Risk_Indicator"] = (
            df["Debt_To_Income_Ratio"] * 35
            + (df["Credit_Utilization"] / 100) * 25
            + df["Missed_Payments"] * 4
            + df["Late_Payment_Count"] * 1.5
            + df["Number_of_Defaults"] * 12
        )
        df["Risk_Level"] = pd.cut(
            df["Risk_Indicator"],
            bins=[-np.inf, 25, 50, np.inf],
            labels=["Lower", "Moderate", "Higher"]
        )

    return df

# ============================================================
# SIDEBAR
# ============================================================
st.sidebar.title("🎛️ Banking Control Center")
st.sidebar.caption("")
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

if "Age" in df.columns:
    age_range = st.sidebar.slider(
        "👥 Age Range", int(df.Age.min()), int(df.Age.max()),
        (int(df.Age.min()), int(df.Age.max()))
    )
else:
    age_range = None

if "Annual_Income" in df.columns:
    income_range = st.sidebar.slider(
        "💰 Annual Income",
        float(df.Annual_Income.min()),
        float(df.Annual_Income.max()),
        (float(df.Annual_Income.min()), float(df.Annual_Income.max())),
        format="₹%.0f"
    )
else:
    income_range = None

if "Credit_Score" in df.columns:
    score_range = st.sidebar.slider(
        "⭐ Credit Score",
        int(df.Credit_Score.min()), int(df.Credit_Score.max()),
        (int(df.Credit_Score.min()), int(df.Credit_Score.max()))
    )
else:
    score_range = None

if "Credit_Utilization" in df.columns:
    utilization_max = st.sidebar.slider(
        "💳 Max Credit Utilization (%)", 0, 100, 100
    )
else:
    utilization_max = 100

risk_segment = st.sidebar.radio(
    "🛡️ Risk Segment",
    ["All Customers", "High Risk Only", "Standard Risk Only"],
    index=0
)

require_kyc = st.sidebar.checkbox("🔒 KYC Complete Only", False)

st.sidebar.markdown("---")
st.sidebar.subheader("🔮 Applicant Risk Simulator")
sim_score = st.sidebar.slider("Applicant Credit Score", 300, 850, 580)
sim_util = st.sidebar.slider("Applicant Utilization (%)", 0, 100, 80)
sim_missed = st.sidebar.slider("Applicant Missed Payments", 0, 10, 3)
sim_high = (sim_score < 600) or (sim_util > 75) or (sim_missed >= 3)
sim_risk_score = min(
    100, max(0, (850 - sim_score) * 0.4 + sim_util * 0.4 + sim_missed * 10)
)
if sim_high:
    st.sidebar.error(f"⚠️ HIGH RISK\nScore: {sim_risk_score:.1f}/100")
else:
    st.sidebar.success(f"✅ STANDARD RISK\nScore: {sim_risk_score:.1f}/100")

# ============================================================
# APPLY FILTERS
# ============================================================
f = df.copy()

def apply_multi(data, col, selected):
    if selected is not None and selected:
        return data[data[col].astype(str).isin(selected)]
    return data

for col, selected in [
    ("Gender", gender),
    ("Employment_Type", employment),
    ("Residential_Status", residential),
    ("KYC_Status", kyc),
    ("Fraud_Flag", fraud)
]:
    if col in f.columns:
        f = apply_multi(f, col, selected)

if age_range and "Age" in f.columns:
    f = f[f.Age.between(age_range[0], age_range[1])]
if income_range and "Annual_Income" in f.columns:
    f = f[f.Annual_Income.between(income_range[0], income_range[1])]
if score_range and "Credit_Score" in f.columns:
    f = f[f.Credit_Score.between(score_range[0], score_range[1])]
if "Credit_Utilization" in f.columns:
    f = f[f.Credit_Utilization <= utilization_max]
if require_kyc and "KYC_Status" in f.columns:
    f = f[f.KYC_Status == "Complete"]
if risk_segment == "High Risk Only" and "High_Risk_Flag" in f.columns:
    f = f[f.High_Risk_Flag == "High Risk"]
elif risk_segment == "Standard Risk Only" and "High_Risk_Flag" in f.columns:
    f = f[f.High_Risk_Flag == "Standard"]

st.sidebar.info(f"Showing **{len(f):,}** of **{len(df):,}** customers")

if f.empty:
    st.warning("⚠️ No customers match the selected filters. Please widen the filters.")
    st.stop()

# ============================================================
# HELPERS
# ============================================================
def money(x):
    x = float(x)
    if abs(x) >= 1e7:
        return f"₹{x/1e7:.2f} Cr"
    if abs(x) >= 1e5:
        return f"₹{x/1e5:.2f} L"
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
# HEADER
# ============================================================
st.markdown(
    '<div class="dashboard-title">💳 FinElite : Your Credit Game Changer</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="dashboard-subtitle">'
    'An AI Powered Credit Card Financial Dashboard'
    '</div>',
    unsafe_allow_html=True
)

# ============================================================
# KPI ROW
# ============================================================
total_customers = len(f)
avg_spending = f["Avg_Monthly_Spending"].mean() if "Avg_Monthly_Spending" in f else 0
avg_income = f["Annual_Income"].mean() if "Annual_Income" in f else 0
avg_score = f["Credit_Score"].mean() if "Credit_Score" in f else 0
avg_util = f["Credit_Utilization"].mean() if "Credit_Utilization" in f else 0
default_rate = (
    f["default_payment_next_month"].mean() * 100
    if "default_payment_next_month" in f else 0
)
high_risk_count = (
    (f["High_Risk_Flag"] == "High Risk").sum()
    if "High_Risk_Flag" in f else 0
)

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
        st.markdown(
            f'<div class="kpi-card"><div class="kpi-title">{title}</div>'
            f'<div class="kpi-value">{value}</div></div>',
            unsafe_allow_html=True
        )

# ============================================================
# ROW 1 — SPENDING / CUSTOMER BEHAVIOUR
# ============================================================
st.markdown('<div class="section-title">📊 Customer Spending & Behaviour</div>', unsafe_allow_html=True)

c1, c2 = st.columns([1, 1])
with c1:
    dim_label = st.selectbox(
        "Compare Spending By",
        ["Age Group", "Gender", "Employment Type", "Occupation",
         "Residential Status", "KYC Status", "Fraud Flag"]
    )
with c2:
    chart_type = st.selectbox(
        "Chart Type",
        ["Bar Chart", "Box Plot", "Violin Plot"]
    )

dim_map = {
    "Age Group": "Age_Group",
    "Gender": "Gender",
    "Employment Type": "Employment_Type",
    "Occupation": "Occupation",
    "Residential Status": "Residential_Status",
    "KYC Status": "KYC_Status",
    "Fraud Flag": "Fraud_Flag"
}
dim = dim_map[dim_label]

if dim in f.columns and "Avg_Monthly_Spending" in f.columns:
    if chart_type == "Bar Chart":
        s = f.groupby(dim, observed=True).agg(
            Average_Spending=("Avg_Monthly_Spending", "mean"),
            Customers=("Avg_Monthly_Spending", "size")
        ).reset_index()
        fig = px.bar(
            s, x=dim, y="Average_Spending", color=dim,
            text_auto=".2s", title=f"Average Monthly Spending by {dim_label}"
        )
        fig.update_layout(showlegend=False)
    elif chart_type == "Box Plot":
        fig = px.box(
            f, x=dim, y="Avg_Monthly_Spending", color=dim,
            points="outliers", title=f"Spending Distribution by {dim_label}"
        )
        fig.update_layout(showlegend=False)
    else:
        fig = px.violin(
            f, x=dim, y="Avg_Monthly_Spending", color=dim,
            box=True, title=f"Spending Pattern by {dim_label}"
        )
        fig.update_layout(showlegend=False)
    chart(fig, 420)

c1, c2, c3 = st.columns(3)

with c1:
    if "Avg_Monthly_Spending" in f.columns:
        fig = px.histogram(
            f, x="Avg_Monthly_Spending", nbins=30,
            marginal="box", title="💰 Monthly Spending Distribution"
        )
        chart(fig, 360)

with c2:
    if {"Age_Group", "Avg_Monthly_Spending"}.issubset(f.columns):
        age_spend = f.groupby("Age_Group", observed=True)["Avg_Monthly_Spending"].mean().reset_index()
        fig = px.bar(
            age_spend, x="Age_Group", y="Avg_Monthly_Spending",
            color="Avg_Monthly_Spending", title="👥 Average Spending by Age Group"
        )
        chart(fig, 360)

with c3:
    if {"Annual_Income", "Avg_Monthly_Spending"}.issubset(f.columns):
        fig = px.scatter(
            f, x="Annual_Income", y="Avg_Monthly_Spending",
            color="Credit_Score" if "Credit_Score" in f.columns else None,
            size="Credit_Limit" if "Credit_Limit" in f.columns else None,
            title="💵 Income vs Monthly Spending"
        )
        chart(fig, 360)

# ============================================================
# ROW 2 — FINANCIAL BEHAVIOUR
# ============================================================
st.markdown('<div class="section-title">💰 Financial Behaviour & Customer Position</div>', unsafe_allow_html=True)

metric_options = [
    c for c in ["Savings_Balance", "Investment_Value",
                "Avg_Monthly_Spending", "EMI_Per_Month"]
    if c in f.columns
]
c1, c2 = st.columns(2)

with c1:
    if "Annual_Income" in f.columns and metric_options:
        selected_metric = st.selectbox(
            "Select Financial Metric",
            metric_options,
            format_func=lambda x: x.replace("_", " ")
        )
        fig = px.scatter(
            f, x="Annual_Income", y=selected_metric,
            color="Employment_Type" if "Employment_Type" in f.columns else None,
            size="Credit_Limit" if "Credit_Limit" in f.columns else None,
            title=f"Annual Income vs {selected_metric.replace('_',' ')}"
        )
        chart(fig, 390)

with c2:
    if "Occupation" in f.columns and metric_options:
        occ = (
            f.groupby("Occupation")[selected_metric]
            .mean().sort_values(ascending=False).head(10)
            .sort_values().reset_index()
        )
        fig = px.bar(
            occ, x=selected_metric, y="Occupation",
            orientation="h", text_auto=".2s",
            title=f"Top 10 Occupations by {selected_metric.replace('_',' ')}"
        )
        chart(fig, 390)

c1, c2 = st.columns(2)

with c1:
    required = {"Avg_Monthly_Transactions", "Avg_Monthly_Spending"}
    if required.issubset(f.columns):
        fig = px.scatter(
            f, x="Avg_Monthly_Transactions", y="Avg_Monthly_Spending",
            size="Credit_Limit" if "Credit_Limit" in f.columns else None,
            color="Credit_Utilization" if "Credit_Utilization" in f.columns else None,
            title="🔄 Transactions vs Spending"
        )
        chart(fig, 380)

with c2:
    if "Employment_Type" in f.columns:
        cols_available = [
            c for c in ["Avg_Monthly_Spending", "Savings_Balance", "Investment_Value"]
            if c in f.columns
        ]
        if cols_available:
            emp = f.groupby("Employment_Type")[cols_available].mean().reset_index()
            fig = go.Figure()
            for col in cols_available:
                fig.add_trace(go.Bar(
                    x=emp["Employment_Type"], y=emp[col],
                    name=col.replace("_", " ")
                ))
            fig.update_layout(
                barmode="group",
                title="🏢 Financial Behaviour by Employment Type"
            )
            chart(fig, 380)

# ============================================================
# ROW 3 — CREDIT & RISK
# ============================================================
st.markdown('<div class="section-title">🛡️ Credit Health, Default & Risk Analytics</div>', unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)

with c1:
    if "default_payment_next_month" in f.columns:
        d = f["default_payment_next_month"].value_counts(normalize=True).reset_index()
        d.columns = ["Status", "Percentage"]
        d["Percentage"] *= 100
        d["Status"] = d["Status"].map({0: "Non-Defaulters", 1: "Defaulters"})
        fig = px.bar(
            d, x="Status", y="Percentage", text_auto=".2f",
            color="Status",
            color_discrete_map={"Non-Defaulters": "#38bdf8", "Defaulters": "#f87171"},
            title="Default Class Distribution (%)"
        )
        chart(fig, 350)

with c2:
    if {"Age_Group", "default_payment_next_month"}.issubset(f.columns):
        r = f.groupby("Age_Group", observed=False)["default_payment_next_month"].mean().reset_index()
        r["Default Rate (%)"] = r["default_payment_next_month"] * 100
        fig = px.bar(
            r, x="Age_Group", y="Default Rate (%)",
            text_auto=".2f", title="Default Rate by Age Group"
        )
        chart(fig, 350)

with c3:
    if {"Occupation", "default_payment_next_month"}.issubset(f.columns):
        r = f.groupby("Occupation")["default_payment_next_month"].mean().reset_index()
        r["Default Rate (%)"] = r["default_payment_next_month"] * 100
        r = r.sort_values("Default Rate (%)").tail(10)
        fig = px.bar(
            r, x="Default Rate (%)", y="Occupation",
            orientation="h", text_auto=".2f",
            title="Top Occupations by Default Rate"
        )
        chart(fig, 350)

c1, c2 = st.columns(2)

with c1:
    if "default_payment_next_month" in f.columns and len(f) > 5:
        numeric = f.select_dtypes(include=[np.number])
        corr = (
            numeric.corr()["default_payment_next_month"]
            .drop(["default_payment_next_month", "Number_of_Defaults"], errors="ignore")
            .sort_values()
            .reset_index()
        )
        corr.columns = ["Feature", "Correlation"]
        fig = px.bar(
            corr, x="Correlation", y="Feature",
            orientation="h", color="Correlation",
            color_continuous_scale="rdbu_r",
            title="Risk Feature Correlations"
        )
        chart(fig, 410)

with c2:
    if {"Credit_Utilization", "default_payment_next_month"}.issubset(f.columns):
        temp = f.copy()
        temp["Status"] = temp["default_payment_next_month"].map(
            {0: "Non-Defaulters", 1: "Defaulters"}
        )
        fig = px.box(
            temp, x="Status", y="Credit_Utilization",
            color="Status", points="outliers",
            color_discrete_map={"Non-Defaulters": "#38bdf8", "Defaulters": "#f87171"},
            title="Credit Utilization by Default Status"
        )
        chart(fig, 410)

# More risk analysis
c1, c2 = st.columns(2)

with c1:
    if {"Debt_To_Income_Ratio", "Credit_Score"}.issubset(f.columns):
        fig = px.scatter(
            f, x="Debt_To_Income_Ratio", y="Credit_Score",
            size="Credit_Limit" if "Credit_Limit" in f.columns else None,
            color="Risk_Level" if "Risk_Level" in f.columns else None,
            title="DTI Ratio vs Credit Score"
        )
        chart(fig, 390)

with c2:
    if {"Credit_Utilization", "Risk_Level"}.issubset(f.columns):
        fig = px.histogram(
            f, x="Credit_Utilization",
            color="Risk_Level", marginal="box",
            title="Credit Utilization Distribution"
        )
        fig.add_vline(
            x=75, line_dash="dash",
            annotation_text="75% Reference"
        )
        chart(fig, 390)

c1, c2 = st.columns(2)

with c1:
    if {"Employment_Type", "Debt_To_Income_Ratio"}.issubset(f.columns):
        dti = (
            f.groupby("Employment_Type")["Debt_To_Income_Ratio"]
            .mean().sort_values().reset_index()
        )
        fig = px.bar(
            dti, x="Debt_To_Income_Ratio", y="Employment_Type",
            orientation="h", text_auto=".2f",
            title="Average DTI by Employment Type"
        )
        chart(fig, 370)

with c2:
    if {"Occupation", "Credit_Utilization"}.issubset(f.columns):
        util = (
            f.groupby("Occupation")["Credit_Utilization"]
            .mean().sort_values(ascending=False).head(10)
            .sort_values().reset_index()
        )
        fig = px.bar(
            util, x="Credit_Utilization", y="Occupation",
            orientation="h", text_auto=".1f",
            title="Top 10 Occupations by Credit Utilization"
        )
        chart(fig, 370)

if "Risk_Level" in f.columns:
    risk = (
        f["Risk_Level"].value_counts()
        .reindex(["Lower", "Moderate", "Higher"], fill_value=0)
        .reset_index()
    )
    risk.columns = ["Risk_Level", "Customers"]
    fig = px.bar(
        risk, x="Risk_Level", y="Customers",
        color="Risk_Level", text_auto=True,
        title="Overall Customer Risk Distribution"
    )
    chart(fig, 360)
    st.caption(
        "Risk Indicator is a custom analytical measure based on DTI, credit utilization, "
        "missed payments, late payments and defaults. It is not an official bank credit-risk score."
    )

# ============================================================
# AUTOMATIC INSIGHTS
# ============================================================
st.markdown('<div class="section-title">💡 Automatic Business Insights</div>', unsafe_allow_html=True)

insights = []
risks = []

if {"Age_Group", "Avg_Monthly_Spending"}.issubset(f.columns):
    x = f.groupby("Age_Group", observed=True)["Avg_Monthly_Spending"].mean()
    if not x.empty:
        insights.append(f"Highest average spending age group: <b>{x.idxmax()}</b> ({money(x.max())}/month).")

if {"Employment_Type", "Avg_Monthly_Spending"}.issubset(f.columns):
    x = f.groupby("Employment_Type")["Avg_Monthly_Spending"].mean()
    if not x.empty:
        insights.append(f"Highest average spending employment type: <b>{x.idxmax()}</b> ({money(x.max())}/month).")

if {"Employment_Type", "Credit_Score"}.issubset(f.columns):
    x = f.groupby("Employment_Type")["Credit_Score"].mean()
    if not x.empty:
        insights.append(f"Highest average credit score by employment type: <b>{x.idxmax()}</b> ({x.max():.0f}).")

if "Credit_Utilization" in f.columns:
    high_util = int((f["Credit_Utilization"] >= 70).sum())
    risks.append(f"Customers with credit utilization ≥ 70%: <b>{high_util:,}</b>.")

if "Debt_To_Income_Ratio" in f.columns:
    risks.append(f"Average DTI ratio of selected customers: <b>{f['Debt_To_Income_Ratio'].mean():.2f}</b>.")

if "High_Risk_Flag" in f.columns:
    risks.append(f"High-risk customers in the selected cohort: <b>{high_risk_count:,}</b>.")

ic1, ic2 = st.columns(2)
with ic1:
    for x in insights:
        st.markdown(f'<div class="insight-card">💡 {x}</div>', unsafe_allow_html=True)
with ic2:
    for x in risks:
        st.markdown(f'<div class="risk-card">⚠️ {x}</div>', unsafe_allow_html=True)

# ============================================================
# FOOTER
# ============================================================
st.divider()
st.caption(
    "💳 FinElite : Your Credit Game Changer"
    "Python • Pandas • NumPy • Plotly • Streamlit"
)
