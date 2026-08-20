import os
import secrets
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px

from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

# ============================================================
# 1. PAGE CONFIG & CUSTOM CSS
# ============================================================
st.set_page_config(
    page_title="FinElite : Fast ML Dashboard",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
.stApp { background: #f5f7fb; color: #374151; }
.block-container { max-width: 1650px; width: 100%; padding: 1.8rem 2rem 2rem 2rem !important; }
section[data-testid="stSidebar"] { background: #ffffff !important; border-right: 1px solid #e5e7eb; }
section[data-testid="stSidebar"] * { color: #374151 !important; }
.dashboard-title { font-size: 2.2rem; font-weight: 800; color: #2563eb; margin-bottom: 4px; }
.dashboard-subtitle { color: #6b7280; font-size: 1rem; margin-bottom: 20px; }
.section-title { background: linear-gradient(90deg, #1e40af, #2563eb); padding: 10px 16px; border-radius: 10px; color: white; font-weight: 700; margin: 20px 0 14px 0; }
.kpi-card { background: #ffffff; border: 1px solid #e5e7eb; border-radius: 12px; padding: 14px; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,.05); }
.kpi-title { color: #6b7280; font-size: 0.75rem; text-transform: uppercase; font-weight: 600; }
.kpi-value { color: #2563eb; font-size: 1.4rem; font-weight: 800; margin-top: 4px; }
.login-wrapper { max-width: 480px; margin: 4vh auto; background: #ffffff; border: 1px solid #e5e7eb; border-radius: 16px; padding: 30px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); }
.login-title { text-align: center; font-size: 1.8rem; font-weight: 800; color: #2563eb; }
.login-subtitle { text-align: center; color: #6b7280; margin-bottom: 16px; font-size: 0.9rem; }
.captcha-display { background: #eff6ff; border: 1px dashed #3b82f6; border-radius: 8px; padding: 8px; text-align: center; color: #1e40af; font-size: 1rem; font-weight: 800; margin: 10px 0; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# 2. LOGIN & AUTHENTICATION SYSTEM
# ============================================================
LOGIN_USERNAME = "admin"
LOGIN_PASSWORD = "Admin@123"

def generate_captcha():
    a = secrets.randbelow(9) + 1
    b = secrets.randbelow(9) + 1
    op = secrets.choice(["+", "-"])
    if op == "-" and b > a:
        a, b = b, a
    ans = a + b if op == "+" else a - b
    return f"{a} {op} {b} = ?", ans

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "captcha_question" not in st.session_state:
    q, ans = generate_captcha()
    st.session_state.captcha_question = q
    st.session_state.captcha_answer = ans

if not st.session_state.authenticated:
    st.markdown("""
        <div class="login-wrapper">
            <div style="text-align:center;font-size:3rem;margin-bottom:8px;">💳</div>
            <div class="login-title">FinElite Portal</div>
            <div class="login-subtitle">High-Speed AI Credit Analytics Dashboard</div>
        </div>
    """, unsafe_allow_html=True)
    
    _, login_col, _ = st.columns([1, 1.8, 1])
    with login_col:
        username = st.text_input("👤 Username", placeholder="admin", key="login_username")
        password = st.text_input("🔒 Password", type="password", placeholder="Admin@123", key="login_password")
        st.markdown(f'<div class="captcha-display">🧩 CAPTCHA: {st.session_state.captcha_question}</div>', unsafe_allow_html=True)
        captcha_input = st.text_input("Answer CAPTCHA", placeholder="Enter result", key="login_captcha")

        if st.button("🔓 Sign In", type="primary", use_container_width=True):
            try:
                captcha_ok = int(captcha_input.strip()) == int(st.session_state.captcha_answer)
            except (ValueError, AttributeError):
                captcha_ok = False

            if username == LOGIN_USERNAME and password == LOGIN_PASSWORD and captcha_ok:
                st.session_state.authenticated = True
                st.session_state.auth_error = ""
                st.rerun()
            else:
                st.session_state.auth_error = "❌ Invalid credentials or CAPTCHA."
                st.session_state.captcha_question, st.session_state.captcha_answer = generate_captcha()
                st.rerun()

        if st.session_state.get("auth_error"):
            st.error(st.session_state.auth_error)
    st.stop()

with st.sidebar:
    st.markdown("### 🔐 Session")
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.captcha_question, st.session_state.captcha_answer = generate_captcha()
        st.rerun()
    st.markdown("---")

# ============================================================
# 3. MOCK DATA GENERATOR & LOADERS
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

@st.cache_data
def load_data(uploaded_file=None):
    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file)
    else:
        paths = ["Credir_Card_Bank.xlsx", "Credir_Card_Bank(4).xlsx"]
        path = next((p for p in paths if os.path.exists(p)), None)
        df = pd.read_excel(path) if path else generate_mock_data()

    df.columns = df.columns.astype(str).str.strip().str.replace(" ", "_", regex=False)
    
    if "Age" in df.columns:
        df["Age_Group"] = pd.cut(df["Age"], bins=[18, 25, 35, 50, 65, 100], labels=["18-25", "26-35", "36-50", "51-65", "65+"], include_lowest=True)
    if "Credit_Score" in df.columns:
        df["Credit_Band"] = df["Credit_Score"].apply(lambda x: "Poor" if x<580 else ("Fair" if x<670 else ("Good" if x<740 else ("Very Good" if x<800 else "Excellent"))))
    if "Number_of_Defaults" in df.columns:
        df["default_payment_next_month"] = (df["Number_of_Defaults"] > 0).astype(int)

    return df

# ============================================================
# 4. ULTRA-FAST SINGLE-PASS ML PIPELINE
# ============================================================
@st.cache_resource(show_spinner=False)
def train_ml_models_fast(df_data):
    df_ml = df_data.copy().drop(columns=["Customer_ID", "PAN_Verified"], errors='ignore').dropna()
    
    cat_cols = df_ml.select_dtypes(include=['object', 'category']).columns.tolist()
    df_ml = pd.get_dummies(df_ml, columns=cat_cols, drop_first=True, dtype=float)

    X = df_ml.drop(['Credit_Limit'], axis=1).values
    y = df_ml['Credit_Limit'].values

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Fast models configuration with optimized tree bounds
    configs = {
        "Linear Regression": (LinearRegression(), {}),
        "Decision Tree": (DecisionTreeRegressor(random_state=42), {'max_depth': [3, 6]}),
        "Random Forest": (RandomForestRegressor(n_estimators=30, random_state=42, n_jobs=-1), {'max_depth': [4, 8]}),
        "XGBoost": (XGBRegressor(n_estimators=30, learning_rate=0.1, random_state=42, n_jobs=-1, eval_metric='rmse'), {'max_depth': [3, 5]})
    }

    results = []
    best_params = {}

    for name, (base_model, param_grid) in configs.items():
        if param_grid:
            grid = GridSearchCV(base_model, param_grid, scoring='r2', cv=3, n_jobs=-1, refit=True)
            grid.fit(X_train, y_train)
            model = grid.best_estimator_
            cv_score = grid.best_score_
            best_params[name] = grid.best_params_
        else:
            model = base_model.fit(X_train, y_train)
            cv_score = cross_val_score(model, X_train, y_train, cv=3, scoring='r2').mean()

        y_pred = model.predict(X_test)
        r2 = r2_score(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))

        results.append({
            "Algorithm": name,
            "Test R² Score (%)": r2 * 100,
            "3-Fold CV R²": cv_score,
            "MAE": mae,
            "RMSE": rmse
        })

    return pd.DataFrame(results), best_params

# ============================================================
# 5. SIDEBAR FILTERS & DATA LOAD
# ============================================================
st.sidebar.title("🎛️ Control Panel")
uploaded_file = st.sidebar.file_uploader("📁 Upload Excel Dataset", type=["xlsx", "xls"])

df_raw = load_data(uploaded_file)
df = df_raw.copy()

st.sidebar.subheader("🎯 Customer Filters")
if "Gender" in df.columns:
    genders = st.sidebar.multiselect("Gender", df["Gender"].dropna().unique(), default=df["Gender"].dropna().unique())
    df = df[df["Gender"].isin(genders)]

if "Employment_Type" in df.columns:
    emp = st.sidebar.multiselect("Employment Type", df["Employment_Type"].dropna().unique(), default=df["Employment_Type"].dropna().unique())
    df = df[df["Employment_Type"].isin(emp)]

if "Age" in df.columns:
    min_a, max_a = int(df_raw["Age"].min()), int(df_raw["Age"].max())
    age_range = st.sidebar.slider("Age Range", min_a, max_a, (min_a, max_a))
    df = df[df["Age"].between(age_range[0], age_range[1])]

# ============================================================
# 6. MAIN DASHBOARD CONTENT
# ============================================================
st.markdown('<div class="dashboard-title">💳 FinElite Analytics Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="dashboard-subtitle">Real-time Credit Data Analytics & High-Speed ML Engine</div>', unsafe_allow_html=True)

# KPI Section
c1, c2, c3, c4 = st.columns(4)
c1.markdown(f'<div class="kpi-card"><div class="kpi-title">Total Customers</div><div class="kpi-value">{len(df):,}</div></div>', unsafe_allow_html=True)
c2.markdown(f'<div class="kpi-card"><div class="kpi-title">Avg Annual Income</div><div class="kpi-value">₹{df["Annual_Income"].mean():,.0f}</div></div>', unsafe_allow_html=True)
c3.markdown(f'<div class="kpi-card"><div class="kpi-title">Avg Credit Score</div><div class="kpi-value">{df["Credit_Score"].mean():.0f}</div></div>', unsafe_allow_html=True)
c4.markdown(f'<div class="kpi-card"><div class="kpi-title">Avg Monthly Spend</div><div class="kpi-value">₹{df["Avg_Monthly_Spending"].mean():,.0f}</div></div>', unsafe_allow_html=True)

# EDA Visualizations
st.markdown('<div class="section-title">📊 Exploratory Data Analysis</div>', unsafe_allow_html=True)
col_a, col_b = st.columns(2)

with col_a:
    chart_dim = st.selectbox("Compare Spending By", ["Age_Group", "Employment_Type", "Residential_Status", "Credit_Band"], index=0)
    if chart_dim in df.columns:
        fig_bar = px.histogram(df, x=chart_dim, y="Avg_Monthly_Spending", histfunc="avg", title=f"Average Monthly Spending by {chart_dim.replace('_', ' ')}")
        fig_bar.update_layout(template="plotly_white", margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_bar, use_container_width=True)

with col_b:
    fig_scatter = px.scatter(df, x="Annual_Income", y="Credit_Limit", color="Credit_Band" if "Credit_Band" in df else None, title="Income vs Credit Limit Allocation")
    fig_scatter.update_layout(template="plotly_white", margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig_scatter, use_container_width=True)

# ============================================================
# 7. FAST MACHINE LEARNING ENGINE
# ============================================================
st.markdown('<div class="section-title">🤖 Machine Learning Engine (Lightning Speed)</div>', unsafe_allow_html=True)

if st.button("🚀 Train & Evaluate ML Models", type="primary"):
    with st.spinner("Executing streamlined single-pass ML pipeline..."):
        metrics_df, best_parameters = train_ml_models_fast(df)
        
        st.success("✅ Models Trained in Seconds!")

        st.markdown("### 📊 Model Performance Metrics")
        st.dataframe(metrics_df.style.format({
            "Test R² Score (%)": "{:.2f}%",
            "3-Fold CV R²": "{:.4f}",
            "MAE": "₹{:,.2f}",
            "RMSE": "₹{:,.2f}"
        }), use_container_width=True)

        st.markdown("### ⚙️ Optimal Hyperparameters")
        p1, p2, p3 = st.columns(3)
        p1.json({"Decision Tree": best_parameters.get("Decision Tree", {})})
        p2.json({"Random Forest": best_parameters.get("Random Forest", {})})
        p3.json({"XGBoost": best_parameters.get("XGBoost", {})})

st.divider()
st.caption("💳 FinElite Dashboard • Streamlit • Scikit-Learn • XGBoost • Plotly")
