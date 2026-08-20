import os
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
.stApp { background: #f5f7fb; color: #374151; }
.block-container { max-width: 1650px; width: 100%; padding: 1.8rem 2rem 2rem 2rem !important; }
section[data-testid="stSidebar"] { background: #ffffff !important; border-right: 1px solid #374151; }
section[data-testid="stSidebar"] * { color: #374151 !important; }
.dashboard-title { font-size: clamp(1.7rem, 2.8vw, 2.45rem); font-weight: 800; color: #2563eb; margin-bottom: 10px; }
.dashboard-subtitle { color: #6b7280; font-size: 1rem; margin-bottom: 24px; }
.section-title { background: linear-gradient(90deg, #1e40af, #2563eb); padding: 10px 16px; border-radius: 10px; color: white; font-weight: 700; margin: 18px 0 12px 0; }
.kpi-card { background: #ffffff; border: 1px solid #374151; border-radius: 14px; padding: 12px 6px; text-align: center; box-shadow: 0 4px 14px rgba(0,0,0,.1); }
.kpi-title { color: #6b7280; font-size: .65rem; text-transform: uppercase; }
.kpi-value { color: #2563eb; font-size: 1.35rem; font-weight: 750; margin-top: 5px; }
.login-wrapper { max-width: 560px; margin: 1.5vh auto 0 auto; background: #ffffff; border: 1px solid #e5e7eb; border-radius: 18px; padding: 20px 30px; box-shadow: 0 12px 35px rgba(15, 23, 42, 0.08); }
.login-title { text-align: center; font-size: 2rem; font-weight: 800; color: #2563eb; }
.login-subtitle { text-align: center; color: #6b7280; margin-bottom: 12px; }
.captcha-display { background: #f8fafc; border: 1px dashed #3b82f6; border-radius: 10px; padding: 9px; text-align: center; color: #1e40af; font-size: 1.05rem; font-weight: 800; }
</style>
""", unsafe_allow_html=True)

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
    st.markdown('<div class="login-wrapper"><div style="text-align:center;font-size:2.7rem;">💳</div><div class="login-title">Welcome to FinElite</div><div class="login-subtitle">Your Credit Game Changer</div></div>', unsafe_allow_html=True)
    _, login_col, _ = st.columns([1, 2, 1])
    with login_col:
        st.markdown("### 🔐 Login")
        username = st.text_input("👤 Username", placeholder="Enter username", key="login_username")
        password = st.text_input("🔒 Password", type="password", placeholder="Enter password", key="login_password")
        st.markdown(f'<div class="captcha-display">🧩 CAPTCHA&nbsp;&nbsp; {st.session_state.captcha_question}</div>', unsafe_allow_html=True)
        captcha = st.text_input("Enter CAPTCHA Answer", placeholder="Enter answer", key="login_captcha")

        if st.button("🔓 Login to Dashboard", type="primary", use_container_width=True):
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
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.auth_error = ""
        q, ans = generate_captcha()
        st.session_state.captcha_question = q
        st.session_state.captcha_answer = ans
        st.rerun()
    st.markdown("---")

# ============================================================
# DATA LOADING & INITIAL PREPROCESSING
# ============================================================
@st.cache_data
def load_data(uploaded_file=None):
    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file)
    else:
        paths = ["Credir_Card_Bank.xlsx", "Credir_Card_Bank(4).xlsx", "../Datasets/Credir_Card_Bank.xlsx"]
        path = next((p for p in paths if os.path.exists(p)), None)
        if path is None:
            raise FileNotFoundError("Credir_Card_Bank.xlsx not found. Upload the Excel file from the sidebar.")
        df = pd.read_excel(path)

    df.columns = df.columns.astype(str).str.strip().str.replace(" ", "_", regex=False)

    numeric_cols = [
        "Age", "Monthly_Income", "Annual_Income", "Credit_Score", "Years_With_Bank", 
        "Existing_Credit_Cards", "Existing_Credit_Limit", "Loan_Count", "EMI_Per_Month", 
        "Debt_To_Income_Ratio", "Savings_Balance", "Investment_Value", "Avg_Monthly_Transactions", 
        "Avg_Monthly_Spending", "Credit_Utilization", "Credit_History_Years", "Missed_Payments", 
        "Late_Payment_Count", "Number_of_Defaults", "Credit_Limit"
    ]
    for c in numeric_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    if "Age" in df.columns:
        df["Age_Group"] = pd.cut(df["Age"], bins=[18, 25, 35, 50, 65, 100], labels=["18-25", "26-35", "36-50", "51-65", "65+"], include_lowest=True)

    if "Credit_Score" in df.columns:
        df["Credit_Band"] = df["Credit_Score"].apply(lambda x: "Poor" if x<580 else ("Fair" if x<670 else ("Good" if x<740 else ("Very Good" if x<800 else "Excellent"))))

    if "Number_of_Defaults" in df.columns:
        df["default_payment_next_month"] = (df["Number_of_Defaults"] > 0).astype(int)

    if {"Credit_Score", "Credit_Utilization", "Missed_Payments"}.issubset(df.columns):
        high_risk = (df["Credit_Score"] < 600) | (df["Credit_Utilization"] > 75) | (df["Missed_Payments"] >= 3)
        df["High_Risk_Flag"] = np.where(high_risk, "High Risk", "Standard")

    return df

# ============================================================
# CACHED ML PIPELINE FUNCTION (FAST EXECUTION)
# ============================================================
@st.cache_resource(show_spinner=False)
def run_ml_pipeline(df_input):
    df_ml = df_input.copy().drop(columns=["Customer_ID", "Monthly_Income", "PAN_Verified", "KYC_Status"], errors='ignore').dropna()
    
    cat_cols = df_ml.select_dtypes(include=['object', 'category']).columns.tolist()
    df_ml = pd.get_dummies(df_ml, columns=cat_cols, drop_first=True, dtype=float)

    x = df_ml.drop(['Credit_Limit'], axis=1).values
    y = df_ml['Credit_Limit'].values

    xtrain, xtest, ytrain, ytest = train_test_split(x, y, test_size=0.2, random_state=42)

    # 1. Linear Regression
    modellinear = LinearRegression().fit(xtrain, ytrain)
    yplinear = modellinear.predict(xtest)
    sc = cross_val_score(LinearRegression(), x, y, cv=3, scoring='r2')

    # 2. Decision Tree
    modeldr = DecisionTreeRegressor(random_state=42).fit(xtrain, ytrain)
    ypdr = modeldr.predict(xtest)
    sc1 = cross_val_score(DecisionTreeRegressor(random_state=42), x, y, cv=3, scoring='r2')

    dt_grid = GridSearchCV(DecisionTreeRegressor(random_state=42), {'max_depth': [5, 10, None], 'min_samples_split': [2, 5]}, scoring='r2', cv=3, n_jobs=-1)
    dt_grid.fit(xtrain, ytrain)

    # 3. Random Forest
    modelrf = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1).fit(xtrain, ytrain)
    yprf = modelrf.predict(xtest)
    sc2 = cross_val_score(RandomForestRegressor(n_estimators=50, random_state=42, n_jobs=-1), x, y, cv=3, scoring='r2')

    rf_grid = GridSearchCV(RandomForestRegressor(random_state=42, n_jobs=-1), {'n_estimators': [50, 100], 'max_depth': [10, None]}, scoring='r2', cv=3, n_jobs=-1)
    rf_grid.fit(xtrain, ytrain)

    # 4. XGBoost
    modelxgbr = XGBRegressor(n_estimators=100, random_state=42, n_jobs=-1).fit(xtrain, ytrain)
    ypxgbr = modelxgbr.predict(xtest)
    sc3 = cross_val_score(XGBRegressor(n_estimators=50, random_state=42, n_jobs=-1), x, y, cv=3, scoring='r2')

    xgb_grid = GridSearchCV(XGBRegressor(objective='reg:squarederror', random_state=42, n_jobs=-1), {'n_estimators': [50, 100], 'learning_rate': [0.05, 0.1]}, scoring='r2', cv=3, n_jobs=-1)
    xgb_grid.fit(xtrain, ytrain)

    metrics = pd.DataFrame({
        "Algorithm": ["Linear Regression", "Decision Tree", "Random Forest", "XGBoost"],
        "Test R² Score (%)": [r2_score(ytest, yplinear) * 100, r2_score(ytest, ypdr) * 100, r2_score(ytest, yprf) * 100, r2_score(ytest, ypxgbr) * 100],
        "3-Fold CV Mean R²": [sc.mean(), sc1.mean(), sc2.mean(), sc3.mean()],
        "GridSearch Best R² Score": [r2_score(ytest, yplinear), dt_grid.best_score_, rf_grid.best_score_, xgb_grid.best_score_],
        "MAE": [mean_absolute_error(ytest, yplinear), mean_absolute_error(ytest, ypdr), mean_absolute_error(ytest, yprf), mean_absolute_error(ytest, ypxgbr)],
        "RMSE": [np.sqrt(mean_squared_error(ytest, yplinear)), np.sqrt(mean_squared_error(ytest, ypdr)), np.sqrt(mean_squared_error(ytest, yprf)), np.sqrt(mean_squared_error(ytest, ypxgbr))]
    })

    best_params = {
        "Decision Tree": dt_grid.best_params_,
        "Random Forest": rf_grid.best_params_,
        "XGBoost": xgb_grid.best_params_
    }

    return metrics, best_params

# ============================================================
# APP LAYOUT & FILTERS
# ============================================================
st.sidebar.title("🎛️ Control Center")
uploaded_file = st.sidebar.file_uploader("📁 Upload Credit Card Excel", type=["xlsx", "xls"])

try:
    df = load_data(uploaded_file)
except Exception as e:
    st.error(f"❌ {e}")
    st.stop()

# Dashboard Header
st.markdown('<div class="dashboard-title">💳 FinElite : Your Credit Game Changer</div>', unsafe_allow_html=True)
st.markdown('<div class="dashboard-subtitle">An AI Powered Credit Card Financial Dashboard & Fast ML Pipeline</div>', unsafe_allow_html=True)

# KPIs
kpis = [
    ("👥 Total Customers", f"{len(df):,}"),
    ("💰 Avg Spending", f"₹{df['Avg_Monthly_Spending'].mean():,.0f}" if 'Avg_Monthly_Spending' in df else "N/A"),
    ("📈 Avg Income", f"₹{df['Annual_Income'].mean():,.0f}" if 'Annual_Income' in df else "N/A"),
    ("⭐ Avg Credit Score", f"{df['Credit_Score'].mean():.0f}" if 'Credit_Score' in df else "N/A")
]
cols = st.columns(len(kpis))
for col, (title, val) in zip(cols, kpis):
    col.markdown(f'<div class="kpi-card"><div class="kpi-title">{title}</div><div class="kpi-value">{val}</div></div>', unsafe_allow_html=True)

# EDA
st.markdown('<div class="section-title">📊 Exploratory Data Analysis</div>', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1:
    if "Avg_Monthly_Spending" in df.columns:
        st.plotly_chart(px.histogram(df, x="Avg_Monthly_Spending", title="💰 Monthly Spending Distribution"), use_container_width=True)
with c2:
    if {"Annual_Income", "Avg_Monthly_Spending"}.issubset(df.columns):
        st.plotly_chart(px.scatter(df, x="Annual_Income", y="Avg_Monthly_Spending", title="💵 Income vs Spending"), use_container_width=True)

# ML Pipeline
st.markdown('<div class="section-title">🤖 Optimized Machine Learning Pipeline</div>', unsafe_allow_html=True)

if st.button("🚀 Run ML Model Training (Fast Mode)", type="primary"):
    with st.spinner("Training models with parallel processing and caching..."):
        metrics_df, best_params = run_ml_pipeline(df)
        st.success("✅ Execution Complete!")

        st.markdown("### 📊 Model Performance Comparison")
        st.dataframe(metrics_df.style.format({
            "Test R² Score (%)": "{:.2f}%",
            "3-Fold CV Mean R²": "{:.4f}",
            "GridSearch Best R² Score": "{:.4f}",
            "MAE": "{:,.2f}",
            "RMSE": "{:,.2f}"
        }), use_container_width=True)

        st.markdown("### ⚙️ Optimal Hyperparameters Found")
        col_a, col_b, col_c = st.columns(3)
        col_a.json(best_params["Decision Tree"])
        col_b.json(best_params["Random Forest"])
        col_c.json(best_params["XGBoost"])
