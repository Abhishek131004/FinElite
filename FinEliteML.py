import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import textwrap

from pathlib import Path
from io import BytesIO

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    r2_score,
    mean_absolute_error,
    mean_squared_error
)

from xgboost import XGBRegressor

# ============================================================
# OPTIONAL SHAP
# ============================================================
try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="FinElite | AI Credit Intelligence",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# PROJECT PATH & CONSTANTS
# ============================================================
BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "Credir_Card_Bank.xlsx"
TARGET = "Credit_Limit"

DROP_COLUMNS = [
    "Customer_ID",
    "CustomerId",
    "ID",
    "Monthly_Income",
    "PAN_Verified",
    "KYC_Status"
]

NUMERIC_FIELDS = [
    "Age",
    "Annual_Income",
    "Credit_Score",
    "Years_With_Bank",
    "Existing_Credit_Cards",
    "Existing_Credit_Limit",
    "Loan_Count",
    "EMI_Per_Month",
    "Debt_To_Income_Ratio",
    "Savings_Balance",
    "Investment_Value",
    "Avg_Monthly_Transactions",
    "Avg_Monthly_Spending",
    "Credit_Utilization",
    "Credit_History_Years",
    "Missed_Payments",
    "Late_Payment_Count",
    "Number_of_Default"
]

INTEGER_FIELDS = [
    "Age",
    "Years_With_Bank",
    "Existing_Credit_Cards",
    "Loan_Count",
    "Avg_Monthly_Transactions",
    "Credit_History_Years",
    "Missed_Payments",
    "Late_Payment_Count",
    "Number_of_Default"
]

CATEGORICAL_COLUMNS = [
    "Gender",
    "Employment_Type",
    "Occupation",
    "Residential_Status",
    "Fraud_Flag"
]

# ============================================================
# HELPER FOR SAFE HTML RENDERING
# ============================================================
def render_html(html_str: str):
    st.markdown(textwrap.dedent(html_str).strip(), unsafe_allow_html=True)

# ============================================================
# CUSTOM CSS
# ============================================================
render_html("""
    <style>
    .stApp {
        background: #f4f7fb;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1500px;
    }
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #06152b 0%, #0b2748 100%);
    }
    section[data-testid="stSidebar"] * {
        color: white !important;
    }
    section[data-testid="stSidebar"] .stFileUploader {
        background: rgba(255,255,255,0.06);
        border-radius: 12px;
        padding: 10px;
    }
    .main-title {
        font-size: 42px;
        font-weight: 800;
        color: #071a33;
        margin-bottom: 0;
    }
    .subtitle {
        color: #64748b;
        font-size: 17px;
        margin-bottom: 20px;
    }
    .dataset-badge {
        background: #e8f1ff;
        color: #1259a5;
        padding: 8px 15px;
        border-radius: 20px;
        font-weight: 700;
        display: inline-block;
        margin-bottom: 20px;
    }
    .metric-card {
        background: white;
        padding: 22px;
        border-radius: 18px;
        border: 1px solid #e5eaf1;
        box-shadow: 0 5px 20px rgba(7, 26, 51, 0.06);
        min-height: 135px;
    }
    .metric-title {
        color: #718096;
        font-size: 13px;
        font-weight: 700;
        letter-spacing: 0.5px;
    }
    .metric-value {
        color: #071a33;
        font-size: 29px;
        font-weight: 800;
        margin-top: 8px;
    }
    .metric-sub {
        color: #718096;
        font-size: 13px;
        margin-top: 6px;
    }
    .risk-low {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        background: #e7f8ef;
        color: #137a45 !important;
        font-weight: 800;
    }
    .risk-medium {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        background: #fff4d6;
        color: #9a6700 !important;
        font-weight: 800;
    }
    .risk-high {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        background: #ffe6e6;
        color: #b42318 !important;
        font-weight: 800;
    }
    .footer {
        text-align: center;
        color: #718096;
        padding: 30px;
        font-size: 13px;
    }
    .stButton > button {
        border-radius: 10px;
        font-weight: 700;
        min-height: 45px;
        width: 100%;
        background-color: #0066cc !important;
        color: white !important;
        border: none !important;
    }
    .stButton > button:hover {
        background-color: #0052a3 !important;
    }
    button[data-baseweb="tab"] {
        font-weight: 700;
        font-size: 15px;
    }
    </style>
""")

# ============================================================
# LOAD DATA FUNCTIONS
# ============================================================
@st.cache_data
def load_default_data():
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Dataset not found: {DATA_PATH}")
    return pd.read_excel(DATA_PATH)

@st.cache_data
def read_uploaded_file(file_bytes, file_name):
    if file_name.lower().endswith(".csv"):
        return pd.read_csv(BytesIO(file_bytes))
    elif file_name.lower().endswith((".xlsx", ".xls")):
        return pd.read_excel(BytesIO(file_bytes))
    else:
        raise ValueError("Only CSV, XLS and XLSX files are supported.")

def get_dataset():
    uploaded = st.session_state.get("uploaded_file")
    if uploaded is not None:
        return read_uploaded_file(uploaded["bytes"], uploaded["name"])
    return load_default_data()

# ============================================================
# PREPROCESS DATA & MODEL
# ============================================================
@st.cache_data
def preprocess_data(df):
    data = df.copy()

    if TARGET not in data.columns:
        raise ValueError(f"Target column '{TARGET}' is missing.")

    data[TARGET] = pd.to_numeric(data[TARGET], errors="coerce")
    data = data.dropna(subset=[TARGET])

    columns_to_drop = [col for col in DROP_COLUMNS if col in data.columns]
    data = data.drop(columns=columns_to_drop, errors="ignore")

    y = data[TARGET].copy()
    data = data.drop(columns=[TARGET])

    categorical_columns = data.select_dtypes(include=["object", "category", "bool"]).columns.tolist()

    for col in categorical_columns:
        data[col] = data[col].astype(str).replace("nan", "Unknown").fillna("Unknown")

    data = pd.get_dummies(data, columns=categorical_columns, drop_first=True)

    for col in data.columns:
        data[col] = pd.to_numeric(data[col], errors="coerce")

    for col in data.columns:
        if data[col].isna().any():
            median = data[col].median()
            data[col] = data[col].fillna(0 if pd.isna(median) else median)

    for col in data.columns:
        if data[col].dtype == bool:
            data[col] = data[col].astype(int)

    return data, y

@st.cache_resource
def train_model(df):
    X, y = preprocess_data(df)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42
    )

    model = XGBRegressor(
        objective="reg:squarederror",
        n_estimators=300,
        learning_rate=0.05,
        max_depth=5,
        min_child_weight=2,
        subsample=0.8,
        colsample_bytree=0.8,
        reg_alpha=0.1,
        reg_lambda=1.0,
        random_state=42,
        n_jobs=-1
    )

    model.fit(X_train, y_train)
    predictions = model.predict(X_test)

    r2 = r2_score(y_test, predictions)
    mae = mean_absolute_error(y_test, predictions)
    rmse = np.sqrt(mean_squared_error(y_test, predictions))

    return model, X, y, X_train, X_test, y_train, y_test, r2, mae, rmse

# ============================================================
# FORM BUILDER & USER PREPARATION
# ============================================================
def get_default_value(series):
    if pd.api.types.is_numeric_dtype(series):
        value = series.median()
        return 0 if pd.isna(value) else float(value)
    mode = series.mode()
    return mode.iloc[0] if len(mode) > 0 else "Unknown"

def build_input_form(raw_df):
    user_data = {}
    st.sidebar.markdown("### 👤 Applicant Profile")

    for field in NUMERIC_FIELDS:
        if field not in raw_df.columns:
            continue

        series = pd.to_numeric(raw_df[field], errors="coerce").dropna()
        if len(series) == 0:
            continue

        min_val = float(series.min())
        max_val = float(series.max())
        med_val = float(series.median())
        label = field.replace("_", " ")

        if field in INTEGER_FIELDS:
            user_data[field] = st.sidebar.number_input(
                label,
                min_value=int(min_val),
                max_value=int(max_val),
                value=int(med_val),
                step=1,
                key=f"input_{field}"
            )
        else:
            step = max((max_val - min_val) / 100, 1.0)
            user_data[field] = st.sidebar.number_input(
                label,
                min_value=min_val,
                max_value=max_val,
                value=med_val,
                step=float(step),
                key=f"input_{field}"
            )

    existing_categories = [col for col in CATEGORICAL_COLUMNS if col in raw_df.columns]
    if existing_categories:
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 🏢 Applicant Details")

        for col in existing_categories:
            options = sorted(raw_df[col].dropna().astype(str).unique().tolist())
            if not options:
                continue

            default = str(get_default_value(raw_df[col]))
            if default not in options:
                default = options[0]

            user_data[col] = st.sidebar.selectbox(
                col.replace("_", " "),
                options,
                index=options.index(default),
                key=f"input_{col}"
            )

    st.sidebar.markdown("---")
    predict_btn = st.sidebar.button("⚡ Predict Credit Limit", key="btn_predict")

    return user_data, predict_btn

def prepare_user_data(user_data, feature_columns):
    user_df = pd.DataFrame([user_data])
    user_df = user_df.drop(columns=[col for col in DROP_COLUMNS if col in user_df.columns], errors="ignore")

    categorical_columns = user_df.select_dtypes(include=["object", "category", "bool"]).columns.tolist()
    user_df = pd.get_dummies(user_df, columns=categorical_columns, drop_first=True)

    for col in user_df.columns:
        user_df[col] = pd.to_numeric(user_df[col], errors="coerce")

    user_df = user_df.fillna(0)
    return user_df.reindex(columns=feature_columns, fill_value=0)

# ============================================================
# CALCULATIONS & CHARTS
# ============================================================
def predict_limit(model, user_df):
    prediction = model.predict(user_df)[0]
    return max(0, float(prediction))

def calculate_risk(user_data):
    score = 0
    credit_score = user_data.get("Credit_Score", 700)
    utilization = user_data.get("Credit_Utilization", 30)
    dti = user_data.get("Debt_To_Income_Ratio", 30)
    missed = user_data.get("Missed_Payments", 0)
    defaults = user_data.get("Number_of_Default", 0)

    score += 0 if credit_score >= 750 else (1 if credit_score >= 650 else (2 if credit_score >= 550 else 3))
    score += 0 if utilization <= 30 else (1 if utilization <= 50 else (2 if utilization <= 75 else 3))
    score += 0 if dti <= 30 else (1 if dti <= 45 else (2 if dti <= 60 else 3))
    score += 0 if missed == 0 else (1 if missed <= 2 else (2 if missed <= 5 else 3))
    score += 0 if defaults == 0 else (2 if defaults <= 1 else 3)

    if score <= 3:
        return "LOW", score, "risk-low"
    elif score <= 7:
        return "MEDIUM", score, "risk-medium"
    else:
        return "HIGH", score, "risk-high"

def create_risk_gauge(risk_score):
    percentage = min(100, (risk_score / 15) * 100)
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=percentage,
        title={"text": "Credit Risk Score (%)"},
        gauge={
            "axis": {"range": [0, 100]},
            "steps": [
                {"range": [0, 35], "color": "#e7f8ef"},
                {"range": [35, 65], "color": "#fff4d6"},
                {"range": [65, 100], "color": "#ffe6e6"}
            ],
            "threshold": {"line": {"width": 4, "color": "black"}, "value": percentage}
        }
    ))
    fig.update_layout(height=300, margin=dict(l=20, r=20, t=50, b=20))
    return fig

def feature_importance_chart(model, feature_columns):
    importance_df = pd.DataFrame({
        "Feature": feature_columns,
        "Importance": model.feature_importances_
    }).sort_values("Importance", ascending=False).head(15)

    importance_df["Feature"] = importance_df["Feature"].str.replace("_", " ", regex=False)
    fig = px.bar(
        importance_df.sort_values("Importance"),
        x="Importance",
        y="Feature",
        orientation="h",
        title="Top 15 Model Features"
    )
    fig.update_layout(height=450)
    return fig

def create_shap_chart(model, user_df):
    if not SHAP_AVAILABLE:
        return None
    try:
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(user_df)
        shap_values = np.asarray(shap_values).flatten()

        shap_df = pd.DataFrame({
            "Feature": user_df.columns,
            "SHAP": shap_values,
            "Abs_SHAP": np.abs(shap_values)
        }).sort_values("Abs_SHAP", ascending=False).head(12)

        shap_df["Feature"] = shap_df["Feature"].str.replace("_", " ", regex=False)
        fig = px.bar(
            shap_df.sort_values("SHAP"),
            x="SHAP",
            y="Feature",
            orientation="h",
            title="Feature Impact on Current Prediction"
        )
        fig.update_layout(height=450)
        return fig
    except Exception:
        return None

# ============================================================
# DATASET EXPLORER TAB
# ============================================================
def dataset_explorer(raw_df):
    st.subheader("📊 Dataset Overview")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rows", f"{raw_df.shape[0]:,}")
    c2.metric("Columns", f"{raw_df.shape[1]:,}")
    c3.metric("Missing Values", f"{raw_df.isna().sum().sum():,}")
    c4.metric("Numeric Columns", len(raw_df.select_dtypes(include=np.number).columns))

    st.markdown("---")
    st.subheader("🔎 Dataset Preview")
    max_rows = min(100, len(raw_df))
    preview_rows = st.slider("Rows to display", 5, max_rows, min(10, max_rows))
    st.dataframe(raw_df.head(preview_rows), use_container_width=True)

    st.subheader("⚠️ Missing Value Analysis")
    missing_df = pd.DataFrame({
        "Column": raw_df.columns,
        "Missing": raw_df.isna().sum().values
    })
    missing_df = missing_df[missing_df["Missing"] > 0]

    if len(missing_df) > 0:
        fig = px.bar(missing_df, x="Column", y="Missing", title="Missing Values per Column")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.success("✅ No missing values found.")

    st.subheader("⬇️ Download Dataset")
    csv_bytes = raw_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Cleaned CSV",
        data=csv_bytes,
        file_name="credit_card_data.csv",
        mime="text/csv"
    )

# ============================================================
# MAIN APPLICATION ROUTINE
# ============================================================
def main():
    render_html("""
        <div style="text-align: center; padding: 10px 0;">
            <div style="font-size: 42px;">💳</div>
            <h1 style="color: white; margin: 0; font-size: 28px; font-weight: 800;">FinElite</h1>
            <p style="color: #b8c7da; font-size: 14px; margin-top: 4px;">AI Credit Intelligence</p>
        </div>
    """)

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📁 Dataset Source")
    uploaded_file = st.sidebar.file_uploader("Upload CSV or XLSX", type=["csv", "xlsx", "xls"])

    if uploaded_file is not None:
        st.session_state["uploaded_file"] = {
            "bytes": uploaded_file.getvalue(),
            "name": uploaded_file.name
        }

    try:
        raw_df = get_dataset()
    except Exception as e:
        st.error(f"Error loading dataset: {e}")
        st.stop()

    user_inputs, predict_clicked = build_input_form(raw_df)

    try:
        model, X, y, X_train, X_test, y_train, y_test, r2, mae, rmse = train_model(raw_df)
    except Exception as e:
        st.error(f"Error training model: {e}")
        st.stop()

    user_df = prepare_user_data(user_inputs, X.columns)
    
    # Real-time recalculation on input changes or button click
    predicted_limit = predict_limit(model, user_df)
    risk_label, risk_score, risk_class = calculate_risk(user_inputs)

    if predict_clicked:
        st.toast("⚡ Prediction updated successfully!", icon="✅")

    # Main Header
    render_html("""
        <div class="main-title">FinElite Dashboard</div>
        <div class="subtitle">AI-Powered Credit Card Limit Prediction & Credit Risk Intelligence</div>
    """)

    dataset_name = uploaded_file.name if uploaded_file else "Credir_Card_Bank.xlsx"
    render_html(f'<div class="dataset-badge">📁 Dataset: {dataset_name}</div>')

    tab1, tab2, tab3 = st.tabs(["🎯 Prediction & Risk", "🤖 Model Performance", "📊 Dataset Explorer"])

    with tab1:
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            render_html(f"""
                <div class="metric-card">
                    <div class="metric-title">RECOMMENDED CREDIT</div>
                    <div class="metric-value">₹{predicted_limit:,.0f}</div>
                    <div class="metric-sub">XGBoost prediction</div>
                </div>
            """)
        with col2:
            render_html(f"""
                <div class="metric-card">
                    <div class="metric-title">RISK TIER</div>
                    <div class="metric-value"><span class="{risk_class}">{risk_label}</span></div>
                    <div class="metric-sub">Risk Score: {risk_score}/15</div>
                </div>
            """)
        with col3:
            render_html(f"""
                <div class="metric-card">
                    <div class="metric-title">CREDIT SCORE</div>
                    <div class="metric-value">{user_inputs.get('Credit_Score', 'N/A')}</div>
                    <div class="metric-sub">Applicant profile</div>
                </div>
            """)
        with col4:
            render_html(f"""
                <div class="metric-card">
                    <div class="metric-title">CREDIT UTILIZATION</div>
                    <div class="metric-value">{user_inputs.get('Credit_Utilization', 0)}%</div>
                    <div class="metric-sub">Current utilization</div>
                </div>
            """)

        st.markdown("<br>", unsafe_allow_html=True)
        g_col1, g_col2 = st.columns([1, 1])

        with g_col1:
            st.plotly_chart(create_risk_gauge(risk_score), use_container_width=True)

        with g_col2:
            st.subheader("📋 Application Input Summary")
            st.json(user_inputs)

    with tab2:
        m1, m2, m3 = st.columns(3)
        m1.metric("R² Score", f"{r2:.4f}")
        m2.metric("MAE", f"₹{mae:,.2f}")
        m3.metric("RMSE", f"₹{rmse:,.2f}")

        st.markdown("---")
        f_col1, f_col2 = st.columns(2)

        with f_col1:
            st.plotly_chart(feature_importance_chart(model, X.columns), use_container_width=True)

        with f_col2:
            if SHAP_AVAILABLE:
                shap_fig = create_shap_chart(model, user_df)
                if shap_fig:
                    st.plotly_chart(shap_fig, use_container_width=True)
                else:
                    st.info("SHAP details not available for this record.")
            else:
                st.warning("Install `shap` library to enable explainability features.")

    with tab3:
        dataset_explorer(raw_df)

    render_html("""
        <div class="footer">
            <b>FinElite</b> | AI-Powered Credit Limit Prediction<br>
            Machine Learning • XGBoost • Explainable AI • Credit Intelligence
        </div>
    """)

if __name__ == "__main__":
    main()
