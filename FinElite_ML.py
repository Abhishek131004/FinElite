import os
import secrets
import numpy as np
import pandas as pd
import seaborn as sb
import matplotlib.pyplot as plt
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

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
.prediction-box {
    background: #ffffff;
    border: 2px solid #2563eb;
    border-radius: 14px;
    padding: 20px;
    text-align: center;
    box-shadow: 0 4px 15px rgba(37, 99, 235, 0.15);
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
    defaults = np.where(missed_payments > 2, 1, 0)
    
    credit_limit = (annual_income * 0.3) + (credit_score * 150) - (utilization * 200) + np.random.normal(0, 10000, n)
    credit_limit = np.maximum(10000, credit_limit)

    return pd.DataFrame({
        "Customer_ID": [f"CUST_{1000+i}" for i in range(n)],
        "Age": age,
        "Gender": np.random.choice(["Male", "Female"], n),
        "Employment_Type": np.random.choice(["Salaried", "Self-Employed", "Business"], n),
        "Residential_Status": np.random.choice(["Owned", "Rented", "Mortgaged"], n),
        "KYC_Status": np.random.choice(["Complete", "Pending"], n, p=[0.9, 0.1]),
        "Fraud_Flag": np.random.choice(["No", "Yes"], n, p=[0.95, 0.05]),
        "Annual_Income": annual_income,
        "Credit_Score": credit_score,
        "Credit_Utilization": utilization,
        "Avg_Monthly_Spending": spending,
        "Missed_Payments": missed_payments,
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
# EDA CORRELATION HEATMAP
# ============================================================
st.markdown("#### 🔍 Feature Correlation Matrix")
num_df = f.select_dtypes(include=[np.number])
if not num_df.empty:
    corr_matrix = num_df.corr(numeric_only=True)
    fig_corr = px.imshow(
        corr_matrix, text_auto=".2f", aspect="auto",
        color_continuous_scale="RdBu_r", title="Correlation Heatmap (Numeric Features)"
    )
    chart(fig_corr, 500)

# ============================================================
# 🤖 FAST MODEL TRAINING PIPELINE
# ============================================================
@st.cache_resource(show_spinner=False)
def train_and_cache_models(data_frame):
    df_ml = data_frame.copy()
    df_ml = df_ml.drop(columns=["Customer_ID", "Monthly_Income", "PAN_Verified", "KYC_Status", "Age_Group", "Credit_Band", "High_Risk_Flag"], errors='ignore').dropna()
    
    cat_cols = df_ml.select_dtypes(include=['object', 'category']).columns.tolist()
    df_ml = pd.get_dummies(df_ml, columns=cat_cols, drop_first=True, dtype=float)

    X = df_ml.drop(['Credit_Limit'], axis=1)
    y = df_ml['Credit_Limit']

    X_train, X_test, y_train, y_test = train_test_split(X.values, y.values, test_size=0.2, random_state=42)

    configs = {
        "Linear Regression": (LinearRegression(), {}),
        "Decision Tree": (DecisionTreeRegressor(random_state=42), {'max_depth': [3, 5, 10]}),
        "Random Forest": (RandomForestRegressor(n_estimators=50, random_state=42, n_jobs=-1), {'max_depth': [5, 10]}),
        "XGBoost": (XGBRegressor(n_estimators=50, learning_rate=0.1, random_state=42, n_jobs=-1), {'max_depth': [3, 5]})
    }

    results = []
    best_params = {}
    fitted_models = {}

    for name, (base_model, param_grid) in configs.items():
        if param_grid:
            grid = GridSearchCV(base_model, param_grid, scoring='r2', cv=3, n_jobs=-1, refit=True)
            grid.fit(X_train, y_train)
            best_model = grid.best_estimator_
            best_score = grid.best_score_
            best_params[name] = grid.best_params_
        else:
            best_model = base_model.fit(X_train, y_train)
            best_score = cross_val_score(best_model, X_train, y_train, cv=3, scoring='r2').mean()

        y_pred = best_model.predict(X_test)
        r2 = r2_score(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))

        fitted_models[name] = best_model
        results.append({
            "Algorithm": name,
            "Test R² Score (%)": r2 * 100,
            "3-Fold CV R²": best_score,
            "MAE": mae,
            "RMSE": rmse
        })

    return pd.DataFrame(results), best_params, fitted_models, X.columns.tolist()

# ============================================================
# 🤖 MACHINE LEARNING DASHBOARD & PREDICTION PIPELINE
# ============================================================
st.markdown('<div class="section-title">🤖 Machine Learning Models & Credit Limit Prediction</div>', unsafe_allow_html=True)

if "models_trained" not in st.session_state:
    st.session_state.models_trained = False

if st.button("🚀 Run ML Model Training & Hyperparameter Tuning", type="primary"):
    with st.spinner("Executing Data Preprocessing, Model Training & Optimization..."):
        metrics_df, best_parameters, fitted_models, feature_columns = train_and_cache_models(df)
        st.session_state.metrics_df = metrics_df
        st.session_state.best_parameters = best_parameters
        st.session_state.fitted_models = fitted_models
        st.session_state.feature_columns = feature_columns
        st.session_state.models_trained = True
        st.success("✅ Training & Evaluation Finished!")

if st.session_state.models_trained:
    st.markdown("### 📊 Model Performance Comparison")
    st.dataframe(st.session_state.metrics_df.style.format({
        "Test R² Score (%)": "{:.2f}%",
        "3-Fold CV R²": "{:.4f}",
        "MAE": "₹{:,.2f}",
        "RMSE": "₹{:,.2f}"
    }), use_container_width=True)

    st.markdown("### ⚙️ Optimal Hyperparameters Found")
    col_a, col_b, col_c = st.columns(3)
    col_a.json({"Decision Tree": st.session_state.best_parameters.get("Decision Tree", {})})
    col_b.json({"Random Forest": st.session_state.best_parameters.get("Random Forest", {})})
    col_c.json({"XGBoost": st.session_state.best_parameters.get("XGBoost", {})})

    # ============================================================
    # 🎯 REAL-TIME USER PREDICTION DASHBOARD
    # ============================================================
    st.markdown('<div class="section-title">🎯 Real-Time Credit Limit Predictor</div>', unsafe_allow_html=True)
    st.write("Select custom customer profile parameters to compute estimated credit limits instantly.")

    pred_col1, pred_col2, pred_col3 = st.columns(3)

    with pred_col1:
        input_age = st.number_input("Age", min_value=18, max_value=100, value=30)
        input_income = st.number_input("Annual Income (₹)", min_value=50000.0, max_value=10000000.0, value=600000.0, step=25000.0)
        input_score = st.slider("Credit Score", min_value=300, max_value=850, value=720)
        input_util = st.slider("Credit Utilization (%)", min_value=0.0, max_value=100.0, value=25.0)

    with pred_col2:
        input_gender = st.selectbox("Gender", df["Gender"].dropna().unique() if "Gender" in df else ["Male", "Female"])
        input_emp = st.selectbox("Employment Type", df["Employment_Type"].dropna().unique() if "Employment_Type" in df else ["Salaried", "Self-Employed", "Business"])
        input_res = st.selectbox("Residential Status", df["Residential_Status"].dropna().unique() if "Residential_Status" in df else ["Owned", "Rented", "Mortgaged"])
        input_spending = st.number_input("Avg Monthly Spending (₹)", min_value=0.0, max_value=500000.0, value=25000.0, step=5000.0)

    with pred_col3:
        input_missed = st.number_input("Missed Payments", min_value=0, max_value=20, value=0)
        input_defaults = st.number_input("Number of Defaults", min_value=0, max_value=10, value=0)
        selected_algo = st.selectbox("Select Trained Model for Inference", list(st.session_state.fitted_models.keys()), index=3)

    if st.button("🔮 Predict Credit Limit", type="primary", use_container_width=True):
        # Prepare Input Data Match Trained Feature Space
        input_dict = {
            "Age": input_age,
            "Annual_Income": input_income,
            "Credit_Score": input_score,
            "Credit_Utilization": input_util,
            "Avg_Monthly_Spending": input_spending,
            "Missed_Payments": input_missed,
            "Number_of_Defaults": input_defaults,
            "default_payment_next_month": 1 if input_defaults > 0 else 0,
            f"Gender_{input_gender}": 1.0,
            f"Employment_Type_{input_emp}": 1.0,
            f"Residential_Status_{input_res}": 1.0
        }

        # Align with original feature schema
        input_df = pd.DataFrame([input_dict])
        for col in st.session_state.feature_columns:
            if col not in input_df.columns:
                input_df[col] = 0.0

        input_df = input_df[st.session_state.feature_columns]

        # Execute Prediction
        model_to_use = st.session_state.fitted_models[selected_algo]
        predicted_limit = model_to_use.predict(input_df.values)[0]
        predicted_limit = max(10000.0, float(predicted_limit))

        st.markdown(f"""
        <div class="prediction-box">
            <h3 style="color:#6b7280;margin:0;">Estimated Credit Limit ({selected_algo})</h3>
            <h1 style="color:#2563eb;font-size:2.8rem;margin:10px 0;">{money(predicted_limit)}</h1>
            <p style="color:#374151;margin:0;">Calculated based on real-time parameter configuration.</p>
        </div>
        """, unsafe_allow_html=True)

# ============================================================
# FOOTER
# ============================================================
st.divider()
st.caption("💳 FinElite : Your Credit Game Changer | Python • Streamlit • Pandas • NumPy • Plotly • Scikit-Learn • XGBoost")
