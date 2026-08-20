import os
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px

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
section[data-testid="stSidebar"] { background: #ffffff !important; border-right: 1px solid #e5e7eb; }
section[data-testid="stSidebar"] * { color: #374151 !important; }
.dashboard-title { font-size: clamp(1.7rem, 2.8vw, 2.45rem); font-weight: 800; color: #2563eb; margin-bottom: 10px; }
.dashboard-subtitle { color: #6b7280; font-size: 1rem; margin-bottom: 24px; }
.section-title { background: linear-gradient(90deg, #1e40af, #2563eb); padding: 10px 16px; border-radius: 10px; color: white; font-weight: 700; margin: 18px 0 12px 0; }
.kpi-card { background: #ffffff; border: 1px solid #e5e7eb; border-radius: 14px; padding: 12px 6px; text-align: center; box-shadow: 0 4px 14px rgba(0,0,0,.1); }
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
LOGIN_USERNAME = os.environ.get("FINELITE_USERNAME", "admin")
LOGIN_PASSWORD = os.environ.get("FINELITE_PASSWORD", "Admin@123")


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
        '<div class="login-wrapper"><div style="text-align:center;font-size:2.7rem;">💳</div>'
        '<div class="login-title">Welcome to FinElite</div>'
        '<div class="login-subtitle">Your Credit Game Changer</div></div>',
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
@st.cache_data(show_spinner="📥 Loading and preparing data...")
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
        df["Age_Group"] = pd.cut(
            df["Age"], bins=[18, 25, 35, 50, 65, 100],
            labels=["18-25", "26-35", "36-50", "51-65", "65+"], include_lowest=True
        )

    if "Credit_Score" in df.columns:
        df["Credit_Band"] = df["Credit_Score"].apply(
            lambda x: "Poor" if pd.notna(x) and x < 580 else (
                "Fair" if pd.notna(x) and x < 670 else (
                    "Good" if pd.notna(x) and x < 740 else (
                        "Very Good" if pd.notna(x) and x < 800 else (
                            "Excellent" if pd.notna(x) else np.nan
                        )
                    )
                )
            )
        )

    if "Number_of_Defaults" in df.columns:
        df["default_payment_next_month"] = (df["Number_of_Defaults"] > 0).astype(int)

    if {"Credit_Score", "Credit_Utilization", "Missed_Payments"}.issubset(df.columns):
        high_risk = (df["Credit_Score"] < 600) | (df["Credit_Utilization"] > 75) | (df["Missed_Payments"] >= 3)
        df["High_Risk_Flag"] = np.where(high_risk, "High Risk", "Standard")

    return df


def safe_metric(df, col, fmt, prefix=""):
    """Format a KPI value without crashing on missing columns or empty/NaN data."""
    if col not in df.columns or df[col].dropna().empty:
        return "N/A"
    val = df[col].mean()
    if pd.isna(val):
        return "N/A"
    return f"{prefix}{val:{fmt}}"


# ============================================================
# CACHED ML PIPELINE FUNCTION (heavy libs imported lazily so the
# app itself starts fast; sklearn/xgboost only load the first
# time the pipeline actually runs, and the result is cached).
# ============================================================
@st.cache_data(show_spinner=False)
def run_ml_pipeline(df_input):
    from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
    from sklearn.linear_model import LinearRegression
    from sklearn.tree import DecisionTreeRegressor
    from sklearn.ensemble import RandomForestRegressor
    from xgboost import XGBRegressor
    from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

    df_ml = df_input.copy().drop(
        columns=["Customer_ID", "Monthly_Income", "PAN_Verified", "KYC_Status"], errors="ignore"
    ).dropna()

    if "Credit_Limit" not in df_ml.columns:
        raise ValueError("The dataset has no 'Credit_Limit' column, which the model needs as its target.")
    if len(df_ml) < 20:
        raise ValueError(
            f"Only {len(df_ml)} complete rows remain after dropping missing values — "
            "that's not enough to train a reliable model. Please upload a fuller dataset."
        )

    cat_cols = df_ml.select_dtypes(include=["object", "category"]).columns.tolist()
    df_ml = pd.get_dummies(df_ml, columns=cat_cols, drop_first=True, dtype=float)

    x = df_ml.drop(["Credit_Limit"], axis=1).values
    y = df_ml["Credit_Limit"].values

    xtrain, xtest, ytrain, ytest = train_test_split(x, y, test_size=0.2, random_state=42)

    # NOTE: inner estimators use n_jobs=1 while GridSearchCV uses n_jobs=-1.
    # Nesting n_jobs=-1 inside n_jobs=-1 causes CPU oversubscription and,
    # in some hosted/cloud environments, hangs or worker-process errors.

    # 1. Linear Regression (no hyperparameters to tune)
    model_linear = LinearRegression().fit(xtrain, ytrain)
    yp_linear = model_linear.predict(xtest)
    lr_cv = cross_val_score(LinearRegression(), x, y, cv=3, scoring="r2").mean()

    # 2. Decision Tree
    dt_grid = GridSearchCV(
        DecisionTreeRegressor(random_state=42),
        {"max_depth": [5, 10, None], "min_samples_split": [2, 5]},
        scoring="r2", cv=3, n_jobs=-1
    )
    dt_grid.fit(xtrain, ytrain)
    yp_dt = dt_grid.best_estimator_.predict(xtest)
    dt_cv = dt_grid.cv_results_["mean_test_score"][dt_grid.best_index_]

    # 3. Random Forest
    rf_grid = GridSearchCV(
        RandomForestRegressor(random_state=42, n_jobs=1),
        {"n_estimators": [50, 100], "max_depth": [10, None]},
        scoring="r2", cv=3, n_jobs=-1
    )
    rf_grid.fit(xtrain, ytrain)
    yp_rf = rf_grid.best_estimator_.predict(xtest)
    rf_cv = rf_grid.cv_results_["mean_test_score"][rf_grid.best_index_]

    # 4. XGBoost
    xgb_grid = GridSearchCV(
        XGBRegressor(objective="reg:squarederror", random_state=42, n_jobs=1),
        {"n_estimators": [50, 100], "learning_rate": [0.05, 0.1]},
        scoring="r2", cv=3, n_jobs=-1
    )
    xgb_grid.fit(xtrain, ytrain)
    yp_xgb = xgb_grid.best_estimator_.predict(xtest)
    xgb_cv = xgb_grid.cv_results_["mean_test_score"][xgb_grid.best_index_]

    metrics = pd.DataFrame({
        "Algorithm": ["Linear Regression", "Decision Tree", "Random Forest", "XGBoost"],
        "Test R² Score (%)": [
            r2_score(ytest, yp_linear) * 100,
            r2_score(ytest, yp_dt) * 100,
            r2_score(ytest, yp_rf) * 100,
            r2_score(ytest, yp_xgb) * 100,
        ],
        "3-Fold CV Mean R²": [lr_cv, dt_cv, rf_cv, xgb_cv],
        "GridSearch Best R² Score": [
            r2_score(ytest, yp_linear), dt_grid.best_score_, rf_grid.best_score_, xgb_grid.best_score_
        ],
        "MAE": [
            mean_absolute_error(ytest, yp_linear), mean_absolute_error(ytest, yp_dt),
            mean_absolute_error(ytest, yp_rf), mean_absolute_error(ytest, yp_xgb)
        ],
        "RMSE": [
            np.sqrt(mean_squared_error(ytest, yp_linear)), np.sqrt(mean_squared_error(ytest, yp_dt)),
            np.sqrt(mean_squared_error(ytest, yp_rf)), np.sqrt(mean_squared_error(ytest, yp_xgb))
        ]
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

if df.empty:
    st.warning("⚠️ The loaded file has no rows. Please upload a valid dataset.")
    st.stop()

# Dashboard Header
st.markdown('<div class="dashboard-title">💳 FinElite : Your Credit Game Changer</div>', unsafe_allow_html=True)
st.markdown('<div class="dashboard-subtitle">An AI Powered Credit Card Financial Dashboard & Fast ML Pipeline</div>', unsafe_allow_html=True)

# KPIs
kpis = [
    ("👥 Total Customers", f"{len(df):,}"),
    ("💰 Avg Spending", safe_metric(df, "Avg_Monthly_Spending", ",.0f", "₹")),
    ("📈 Avg Income", safe_metric(df, "Annual_Income", ",.0f", "₹")),
    ("⭐ Avg Credit Score", safe_metric(df, "Credit_Score", ".0f")),
]
cols = st.columns(len(kpis))
for col, (title, val) in zip(cols, kpis):
    col.markdown(
        f'<div class="kpi-card"><div class="kpi-title">{title}</div><div class="kpi-value">{val}</div></div>',
        unsafe_allow_html=True
    )

# EDA
st.markdown('<div class="section-title">📊 Exploratory Data Analysis</div>', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1:
    if "Avg_Monthly_Spending" in df.columns and df["Avg_Monthly_Spending"].notna().any():
        st.plotly_chart(px.histogram(df, x="Avg_Monthly_Spending", title="💰 Monthly Spending Distribution"), use_container_width=True)
    else:
        st.info("No 'Avg_Monthly_Spending' data available to plot.")
with c2:
    if {"Annual_Income", "Avg_Monthly_Spending"}.issubset(df.columns) and df[["Annual_Income", "Avg_Monthly_Spending"]].notna().any().all():
        st.plotly_chart(px.scatter(df, x="Annual_Income", y="Avg_Monthly_Spending", title="💵 Income vs Spending"), use_container_width=True)
    else:
        st.info("No 'Annual_Income' / 'Avg_Monthly_Spending' data available to plot.")

# ML Pipeline
st.markdown('<div class="section-title">🤖 Optimized Machine Learning Pipeline</div>', unsafe_allow_html=True)

if st.button("🚀 Run ML Model Training (Fast Mode)", type="primary"):
    with st.spinner("Training models with parallel processing and caching..."):
        try:
            metrics_df, best_params = run_ml_pipeline(df)
        except Exception as e:
            st.error(f"❌ Model training failed: {e}")
        else:
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
