import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

from xgboost import XGBRegressor

# Optional SHAP
try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="FinElite | AI Credit Limit Prediction",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* Main background */
    .stApp {
        background: #f4f7fb;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #071a33 0%, #0b2748 100%);
    }

    section[data-testid="stSidebar"] * {
        color: white !important;
    }

    /* Header */
    .main-title {
        font-size: 38px;
        font-weight: 800;
        color: #071a33;
        margin-bottom: 2px;
    }

    .subtitle {
        color: #607089;
        font-size: 16px;
        margin-bottom: 25px;
    }

    /* Cards */
    .metric-card {
        background: white;
        padding: 22px;
        border-radius: 16px;
        border: 1px solid #e5eaf1;
        box-shadow: 0 5px 20px rgba(7, 26, 51, 0.06);
        min-height: 130px;
    }

    .metric-title {
        color: #718096;
        font-size: 14px;
        font-weight: 600;
    }

    .metric-value {
        color: #071a33;
        font-size: 30px;
        font-weight: 800;
        margin-top: 7px;
    }

    .metric-sub {
        color: #718096;
        font-size: 13px;
        margin-top: 5px;
    }

    /* Section cards */
    .section-card {
        background: white;
        padding: 24px;
        border-radius: 18px;
        border: 1px solid #e5eaf1;
        box-shadow: 0 5px 20px rgba(7, 26, 51, 0.05);
        margin-bottom: 20px;
    }

    /* Risk badges */
    .risk-low {
        display: inline-block;
        padding: 8px 18px;
        border-radius: 30px;
        background: #e7f8ef;
        color: #137a45;
        font-weight: 700;
    }

    .risk-medium {
        display: inline-block;
        padding: 8px 18px;
        border-radius: 30px;
        background: #fff4d6;
        color: #9a6700;
        font-weight: 700;
    }

    .risk-high {
        display: inline-block;
        padding: 8px 18px;
        border-radius: 30px;
        background: #ffe6e6;
        color: #b42318;
        font-weight: 700;
    }

    /* Info box */
    .info-box {
        background: #eef6ff;
        border-left: 5px solid #1976d2;
        padding: 16px;
        border-radius: 10px;
        color: #17324d;
        margin: 15px 0;
    }

    /* Footer */
    .footer {
        text-align: center;
        color: #718096;
        padding: 30px;
        font-size: 13px;
    }

    /* Buttons */
    .stButton > button {
        border-radius: 10px;
        font-weight: 700;
        border: none;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# CONSTANTS
# ============================================================

DATA_PATH = "Credir_Card_Bank.xlsx"

TARGET = "Credit_Limit"

DROP_COLUMNS = [
    "Customer_ID",
    "Monthly_Income",
    "PAN_Verified",
    "KYC_Status"
]

CATEGORICAL_COLUMNS = [
    "Gender",
    "Employment_Type",
    "Occupation",
    "Residential_Status",
    "Fraud_Flag"
]


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data():

    df = pd.read_excel(DATA_PATH)

    return df


# ============================================================
# PREPROCESS DATA
# ============================================================

@st.cache_data
def preprocess_data(df):

    data = df.copy()

    # Remove unnecessary columns only if they exist
    columns_to_drop = [
        col for col in DROP_COLUMNS
        if col in data.columns
    ]

    data = data.drop(columns=columns_to_drop)

    # Encode categorical variables
    existing_cat_cols = [
        col for col in CATEGORICAL_COLUMNS
        if col in data.columns
    ]

    data = pd.get_dummies(
        data,
        columns=existing_cat_cols,
        drop_first=True
    )

    # Make sure all data is numeric
    for col in data.columns:

        if data[col].dtype == "bool":
            data[col] = data[col].astype(int)

    return data


# ============================================================
# TRAIN XGBOOST MODEL
# ============================================================

@st.cache_resource
def train_model():

    raw_df = load_data()

    processed_df = preprocess_data(raw_df)

    X = processed_df.drop(columns=[TARGET])
    y = processed_df[TARGET]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42
    )

    model = XGBRegressor(
        objective="reg:squarederror",
        n_estimators=200,
        learning_rate=0.05,
        max_depth=5,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        n_jobs=-1
    )

    model.fit(
        X_train,
        y_train
    )

    predictions = model.predict(X_test)

    r2 = r2_score(
        y_test,
        predictions
    )

    mae = mean_absolute_error(
        y_test,
        predictions
    )

    rmse = np.sqrt(
        mean_squared_error(
            y_test,
            predictions
        )
    )

    return (
        model,
        X,
        y,
        X_train,
        X_test,
        y_train,
        y_test,
        r2,
        mae,
        rmse
    )


# ============================================================
# CREATE DEFAULT VALUES
# ============================================================

def get_default_value(series):

    if pd.api.types.is_numeric_dtype(series):

        value = series.median()

        if pd.isna(value):
            return 0

        return float(value)

    mode = series.mode()

    if len(mode) > 0:
        return mode.iloc[0]

    return "Unknown"


# ============================================================
# BUILD APPLICANT INPUT
# ============================================================

def build_input_form(raw_df):

    user_data = {}

    # --------------------------------------------------------
    # PERSONAL INFORMATION
    # --------------------------------------------------------

    st.sidebar.markdown("## 👤 Applicant Profile")

    if "Age" in raw_df.columns:

        user_data["Age"] = st.sidebar.slider(
            "Age",
            min_value=int(raw_df["Age"].min()),
            max_value=int(raw_df["Age"].max()),
            value=int(raw_df["Age"].median())
        )

    # --------------------------------------------------------
    # FINANCIAL INFORMATION
    # --------------------------------------------------------

    st.sidebar.markdown("---")
    st.sidebar.markdown("## 💰 Financial Profile")

    numeric_fields = [
        "Annual_Income",
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
        "Number_of_Default",
        "Existing_Credit_Cards",
        "Years_With_Bank"
    ]

    for field in numeric_fields:

        if field not in raw_df.columns:
            continue

        series = raw_df[field]

        min_value = float(series.min())
        max_value = float(series.max())
        median_value = float(series.median())

        # Special handling for integer-like columns
        integer_fields = [
            "Loan_Count",
            "Avg_Monthly_Transactions",
            "Credit_History_Years",
            "Missed_Payments",
            "Late_Payment_Count",
            "Number_of_Default",
            "Existing_Credit_Cards",
            "Years_With_Bank"
        ]

        if field in integer_fields:

            user_data[field] = st.sidebar.number_input(
                field.replace("_", " "),
                min_value=int(min_value),
                max_value=int(max_value),
                value=int(median_value),
                step=1
            )

        else:

            user_data[field] = st.sidebar.number_input(
                field.replace("_", " "),
                min_value=min_value,
                max_value=max_value,
                value=median_value,
                step=max((max_value - min_value) / 100, 1.0)
            )

    # --------------------------------------------------------
    # CREDIT SCORE
    # --------------------------------------------------------

    if "Credit_Score" in raw_df.columns:

        st.sidebar.markdown("---")
        st.sidebar.markdown("## 📊 Credit Profile")

        user_data["Credit_Score"] = st.sidebar.slider(
            "Credit Score",
            min_value=int(raw_df["Credit_Score"].min()),
            max_value=int(raw_df["Credit_Score"].max()),
            value=int(raw_df["Credit_Score"].median())
        )

    # --------------------------------------------------------
    # CATEGORICAL VARIABLES
    # --------------------------------------------------------

    st.sidebar.markdown("---")
    st.sidebar.markdown("## 🏢 Applicant Details")

    for col in CATEGORICAL_COLUMNS:

        if col not in raw_df.columns:
            continue

        options = sorted(
            raw_df[col]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        if len(options) == 0:
            continue

        default_value = get_default_value(
            raw_df[col]
        )

        default_value = str(default_value)

        if default_value not in options:
            default_value = options[0]

        user_data[col] = st.sidebar.selectbox(
            col.replace("_", " "),
            options,
            index=options.index(default_value)
        )

    return user_data


# ============================================================
# PREPARE USER DATA FOR MODEL
# ============================================================

def prepare_user_data(
    user_data,
    raw_df,
    feature_columns
):

    user_df = pd.DataFrame([user_data])

    # Remove columns exactly like training
    columns_to_drop = [
        col for col in DROP_COLUMNS
        if col in user_df.columns
    ]

    user_df = user_df.drop(
        columns=columns_to_drop,
        errors="ignore"
    )

    # One-hot encoding
    existing_cat_cols = [
        col for col in CATEGORICAL_COLUMNS
        if col in user_df.columns
    ]

    user_df = pd.get_dummies(
        user_df,
        columns=existing_cat_cols,
        drop_first=True
    )

    # Convert bool to integer
    for col in user_df.columns:

        if user_df[col].dtype == "bool":
            user_df[col] = user_df[col].astype(int)

    # Match training columns
    user_df = user_df.reindex(
        columns=feature_columns,
        fill_value=0
    )

    return user_df


# ============================================================
# PREDICTION
# ============================================================

def predict_limit(
    model,
    user_df
):

    prediction = model.predict(
        user_df
    )[0]

    prediction = max(
        0,
        float(prediction)
    )

    return prediction


# ============================================================
# RISK CALCULATION
# ============================================================

def calculate_risk(user_data):

    score = 0

    # Credit score
    credit_score = user_data.get(
        "Credit_Score",
        700
    )

    if credit_score >= 750:
        score += 0
    elif credit_score >= 650:
        score += 1
    elif credit_score >= 550:
        score += 2
    else:
        score += 3

    # Credit utilization
    utilization = user_data.get(
        "Credit_Utilization",
        30
    )

    if utilization <= 30:
        score += 0
    elif utilization <= 50:
        score += 1
    elif utilization <= 75:
        score += 2
    else:
        score += 3

    # DTI
    dti = user_data.get(
        "Debt_To_Income_Ratio",
        30
    )

    if dti <= 30:
        score += 0
    elif dti <= 45:
        score += 1
    elif dti <= 60:
        score += 2
    else:
        score += 3

    # Missed payments
    missed = user_data.get(
        "Missed_Payments",
        0
    )

    if missed == 0:
        score += 0
    elif missed <= 2:
        score += 1
    elif missed <= 5:
        score += 2
    else:
        score += 3

    # Defaults
    defaults = user_data.get(
        "Number_of_Default",
        0
    )

    if defaults == 0:
        score += 0
    elif defaults <= 1:
        score += 2
    else:
        score += 3

    # Final tier
    if score <= 3:

        return (
            "LOW",
            score,
            "risk-low"
        )

    elif score <= 7:

        return (
            "MEDIUM",
            score,
            "risk-medium"
        )

    else:

        return (
            "HIGH",
            score,
            "risk-high"
        )


# ============================================================
# RISK GAUGE
# ============================================================

def create_risk_gauge(risk_score):

    risk_percentage = min(
        100,
        (risk_score / 15) * 100
    )

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=risk_percentage,
            title={
                "text": "Credit Risk Score"
            },
            gauge={
                "axis": {
                    "range": [0, 100]
                },
                "bar": {
                    "thickness": 0.3
                },
                "steps": [
                    {
                        "range": [0, 35],
                    },
                    {
                        "range": [35, 65],
                    },
                    {
                        "range": [65, 100],
                    }
                ],
                "threshold": {
                    "line": {
                        "width": 4
                    },
                    "value": risk_percentage
                }
            }
        )
    )

    fig.update_layout(
        height=300,
        margin=dict(
            l=20,
            r=20,
            t=50,
            b=20
        )
    )

    return fig


# ============================================================
# FEATURE IMPORTANCE
# ============================================================

def feature_importance_chart(
    model,
    feature_columns
):

    importance = model.feature_importances_

    importance_df = pd.DataFrame({
        "Feature": feature_columns,
        "Importance": importance
    })

    importance_df = importance_df.sort_values(
        "Importance",
        ascending=False
    ).head(15)

    importance_df["Feature"] = (
        importance_df["Feature"]
        .str.replace("_", " ")
    )

    fig = px.bar(
        importance_df.sort_values(
            "Importance"
        ),
        x="Importance",
        y="Feature",
        orientation="h",
        title="Top Model Features"
    )

    fig.update_layout(
        height=500,
        margin=dict(
            l=10,
            r=20,
            t=50,
            b=20
        )
    )

    return fig


# ============================================================
# SHAP EXPLANATION
# ============================================================

def create_shap_chart(
    model,
    user_df
):

    if not SHAP_AVAILABLE:
        return None

    try:

        explainer = shap.TreeExplainer(
            model
        )

        shap_values = explainer.shap_values(
            user_df
        )

        if isinstance(shap_values, list):
            shap_values = shap_values[0]

        shap_values = np.array(
            shap_values
        ).flatten()

        values = user_df.iloc[0].values

        shap_df = pd.DataFrame({
            "Feature": user_df.columns,
            "SHAP": shap_values,
            "Value": values
        })

        shap_df["Abs_SHAP"] = (
            shap_df["SHAP"]
            .abs()
        )

        shap_df = shap_df.sort_values(
            "Abs_SHAP",
            ascending=False
        ).head(12)

        shap_df["Feature"] = (
            shap_df["Feature"]
            .str.replace("_", " ")
        )

        fig = px.bar(
            shap_df.sort_values("SHAP"),
            x="SHAP",
            y="Feature",
            orientation="h",
            title="How Features Influenced This Prediction"
        )

        fig.update_layout(
            height=500,
            margin=dict(
                l=10,
                r=20,
                t=50,
                b=20
            )
        )

        return fig

    except Exception:

        return None


# ============================================================
# MAIN APP
# ============================================================

def main():

    # --------------------------------------------------------
    # LOAD MODEL
    # --------------------------------------------------------

    try:

        (
            model,
            X,
            y,
            X_train,
            X_test,
            y_train,
            y_test,
            r2,
            mae,
            rmse
        ) = train_model()

        raw_df = load_data()

    except Exception as e:

        st.error(
            f"Unable to load/train the FinElite model: {e}"
        )

        st.info(
            "Check that the Excel file exists at "
            "`Datasets/Credir_Card_Bank.xlsx`."
        )

        st.stop()

    # --------------------------------------------------------
    # SIDEBAR
    # --------------------------------------------------------

    st.sidebar.markdown(
        """
        <div style="
            text-align:center;
            padding:10px;
            margin-bottom:15px;
        ">
            <h1 style="color:white;">
                💳 FinElite
            </h1>

            <p style="color:#b8c7da;">
                AI Credit Intelligence
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    user_data = build_input_form(
        raw_df
    )

    st.sidebar.markdown("---")

    if st.sidebar.button(
        "🔄 Reset Application",
        use_container_width=True
    ):

        st.session_state.clear()
        st.rerun()

    st.sidebar.markdown(
        """
        <div style="
            text-align:center;
            margin-top:25px;
            color:#b8c7da;
            font-size:12px;
        ">
            FinElite AI<br>
            Credit Limit Intelligence Platform
        </div>
        """,
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # PREPARE INPUT
    # --------------------------------------------------------

    user_df = prepare_user_data(
        user_data,
        raw_df,
        X.columns
    )

    prediction = predict_limit(
        model,
        user_df
    )

    risk_tier, risk_score, risk_class = calculate_risk(
        user_data
    )

    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------

    st.markdown(
        '<div class="main-title">FinElite</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="subtitle">
        AI-Powered Credit Card Limit Prediction & Credit Risk Intelligence
        </div>
        """,
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # TOP METRICS
    # --------------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">
                    RECOMMENDED CREDIT LIMIT
                </div>

                <div class="metric-value">
                    ₹{prediction:,.0f}
                </div>

                <div class="metric-sub">
                    AI model recommendation
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:

        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">
                    RISK TIER
                </div>

                <div class="metric-value">
                    {risk_tier}
                </div>

                <div class="metric-sub">
                    Risk score: {risk_score}/15
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:

        credit_score = user_data.get(
            "Credit_Score",
            0
        )

        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">
                    CREDIT SCORE
                </div>

                <div class="metric-value">
                    {credit_score}
                </div>

                <div class="metric-sub">
                    Applicant credit profile
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col4:

        utilization = user_data.get(
            "Credit_Utilization",
            0
        )

        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">
                    CREDIT UTILIZATION
                </div>

                <div class="metric-value">
                    {utilization:.1f}%
                </div>

                <div class="metric-sub">
                    Current utilization
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # --------------------------------------------------------
    # TABS
    # --------------------------------------------------------

    tab1, tab2, tab3 = st.tabs(
        [
            "👤 Applicant Assessment",
            "🧠 Model Insights & XAI",
            "🎯 Scenario Simulator"
        ]
    )

    # ========================================================
    # TAB 1
    # ========================================================

    with tab1:

        left, right = st.columns(
            [1.3, 1]
        )

        with left:

            st.markdown(
                '<div class="section-card">',
                unsafe_allow_html=True
            )

            st.subheader(
                "Credit Limit Recommendation"
            )

            st.markdown(
                f"""
                <div style="
                    text-align:center;
                    padding:20px;
                ">

                    <div style="
                        font-size:16px;
                        color:#718096;
                    ">
                        Recommended Credit Limit
                    </div>

                    <div style="
                        font-size:48px;
                        font-weight:800;
                        color:#071a33;
                    ">
                        ₹{prediction:,.0f}
                    </div>

                    <br>

                    <span class="{risk_class}">
                        {risk_tier} RISK
                    </span>

                </div>
                """,
                unsafe_allow_html=True
            )

            st.markdown(
                "</div>",
                unsafe_allow_html=True
            )

        with right:

            st.markdown(
                '<div class="section-card">',
                unsafe_allow_html=True
            )

            st.plotly_chart(
                create_risk_gauge(
                    risk_score
                ),
                use_container_width=True
            )

            st.markdown(
                "</div>",
                unsafe_allow_html=True
            )

        # ----------------------------------------------------
        # APPLICANT SUMMARY
        # ----------------------------------------------------

        st.markdown(
            '<div class="section-card">',
            unsafe_allow_html=True
        )

        st.subheader(
            "Applicant Financial Summary"
        )

        summary_columns = st.columns(4)

        metrics = [
            (
                "Annual Income",
                f"₹{user_data.get('Annual_Income', 0):,.0f}"
            ),
            (
                "Existing Limit",
                f"₹{user_data.get('Existing_Credit_Limit', 0):,.0f}"
            ),
            (
                "Monthly Spending",
                f"₹{user_data.get('Avg_Monthly_Spending', 0):,.0f}"
            ),
            (
                "DTI Ratio",
                f"{user_data.get('Debt_To_Income_Ratio', 0):.1f}%"
            )
        ]

        for column, (title, value) in zip(
            summary_columns,
            metrics
        ):

            with column:

                st.metric(
                    title,
                    value
                )

        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )

        # ----------------------------------------------------
        # RECOMMENDATION
        # ----------------------------------------------------

        if risk_tier == "LOW":

            recommendation = """
            Applicant demonstrates a relatively strong credit profile.
            The recommended credit limit can be considered for approval,
            subject to institutional credit policies.
            """

        elif risk_tier == "MEDIUM":

            recommendation = """
            Applicant presents moderate credit risk. Consider the AI
            recommendation together with income stability, existing
            liabilities and repayment history before approval.
            """

        else:

            recommendation = """
            Applicant presents elevated credit risk. A conservative
            credit limit and additional verification may be appropriate.
            """

        st.markdown(
            f"""
            <div class="info-box">
                <b>💡 FinElite Recommendation</b><br><br>
                {recommendation}
            </div>
            """,
            unsafe_allow_html=True
        )

    # ========================================================
    # TAB 2
    # ========================================================

    with tab2:

        st.subheader(
            "🧠 Model Insights & Explainable AI"
        )

        st.markdown(
            """
            FinElite uses machine learning to estimate an appropriate
            credit limit. The XAI layer helps users understand which
            variables contribute most strongly to the model's decision.
            """
        )

        insight_col1, insight_col2 = st.columns(2)

        with insight_col1:

            st.plotly_chart(
                feature_importance_chart(
                    model,
                    X.columns
                ),
                use_container_width=True
            )

        with insight_col2:

            if SHAP_AVAILABLE:

                shap_chart = create_shap_chart(
                    model,
                    user_df
                )

                if shap_chart is not None:

                    st.plotly_chart(
                        shap_chart,
                        use_container_width=True
                    )

                else:

                    st.info(
                        "SHAP explanation could not be generated "
                        "for this model."
                    )

            else:

                st.info(
                    """
                    SHAP is not installed.

                    Add `shap` to requirements.txt to enable
                    individual prediction explanations.
                    """
                )

                st.plotly_chart(
                    feature_importance_chart(
                        model,
                        X.columns
                    ),
                    use_container_width=True
                )

        # ----------------------------------------------------
        # MODEL PERFORMANCE
        # ----------------------------------------------------

        st.subheader(
            "📈 Model Performance"
        )

        performance_col1, performance_col2, performance_col3 = st.columns(3)

        with performance_col1:

            st.metric(
                "R² Score",
                f"{r2 * 100:.2f}%"
            )

        with performance_col2:

            st.metric(
                "MAE",
                f"₹{mae:,.0f}"
            )

        with performance_col3:

            st.metric(
                "RMSE",
                f"₹{rmse:,.0f}"
            )

        st.markdown(
            """
            <div class="info-box">
                <b>Model Interpretation</b><br><br>
                <b>R²:</b> Measures how much variation in credit limit
                is explained by the model.<br><br>

                <b>MAE:</b> Average absolute difference between actual
                and predicted credit limits.<br><br>

                <b>RMSE:</b> Penalizes larger prediction errors more strongly.
            </div>
            """,
            unsafe_allow_html=True
        )

    # ========================================================
    # TAB 3 - WHAT IF
    # ========================================================

    with tab3:

        st.subheader(
            "🎯 What-If Scenario Simulator"
        )

        st.markdown(
            """
            Adjust the applicant's income and credit score to see
            how the recommended credit limit changes.
            """
        )

        scenario_col1, scenario_col2 = st.columns(2)

        with scenario_col1:

            if "Annual_Income" in raw_df.columns:

                scenario_income = st.slider(
                    "Scenario Annual Income",
                    min_value=float(
                        raw_df["Annual_Income"].min()
                    ),
                    max_value=float(
                        raw_df["Annual_Income"].max()
                    ),
                    value=float(
                        user_data.get(
                            "Annual_Income",
                            raw_df["Annual_Income"].median()
                        )
                    )
                )

            else:

                scenario_income = user_data.get(
                    "Annual_Income",
                    0
                )

        with scenario_col2:

            if "Credit_Score" in raw_df.columns:

                scenario_score = st.slider(
                    "Scenario Credit Score",
                    min_value=int(
                        raw_df["Credit_Score"].min()
                    ),
                    max_value=int(
                        raw_df["Credit_Score"].max()
                    ),
                    value=int(
                        user_data.get(
                            "Credit_Score",
                            raw_df["Credit_Score"].median()
                        )
                    )
                )

            else:

                scenario_score = user_data.get(
                    "Credit_Score",
                    0
                )

        # ----------------------------------------------------
        # CREATE SCENARIO
        # ----------------------------------------------------

        scenario_data = user_data.copy()

        if "Annual_Income" in scenario_data:

            scenario_data["Annual_Income"] = (
                scenario_income
            )

        if "Credit_Score" in scenario_data:

            scenario_data["Credit_Score"] = (
                scenario_score
            )

        scenario_df = prepare_user_data(
            scenario_data,
            raw_df,
            X.columns
        )

        scenario_prediction = predict_limit(
            model,
            scenario_df
        )

        prediction_difference = (
            scenario_prediction - prediction
        )

        # ----------------------------------------------------
        # SCENARIO METRICS
        # ----------------------------------------------------

        sc1, sc2, sc3 = st.columns(3)

        with sc1:

            st.metric(
                "Current Limit",
                f"₹{prediction:,.0f}"
            )

        with sc2:

            st.metric(
                "Scenario Limit",
                f"₹{scenario_prediction:,.0f}"
            )

        with sc3:

            st.metric(
                "Change",
                f"₹{prediction_difference:,.0f}",
                delta=f"{prediction_difference:,.0f}"
            )

        # ----------------------------------------------------
        # WHAT-IF VISUAL
        # ----------------------------------------------------

        scenario_chart_df = pd.DataFrame({
            "Scenario": [
                "Current Profile",
                "What-If Scenario"
            ],
            "Credit Limit": [
                prediction,
                scenario_prediction
            ]
        })

        fig = px.bar(
            scenario_chart_df,
            x="Scenario",
            y="Credit Limit",
            text_auto=".2s",
            title="Current vs Scenario Credit Limit"
        )

        fig.update_layout(
            height=450
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        # ----------------------------------------------------
        # SCENARIO INTERPRETATION
        # ----------------------------------------------------

        if prediction_difference > 0:

            st.success(
                f"""
                Increasing the selected applicant attributes results in
                an estimated credit limit increase of
                ₹{prediction_difference:,.0f}.
                """
            )

        elif prediction_difference < 0:

            st.warning(
                f"""
                The selected scenario decreases the estimated credit limit
                by ₹{abs(prediction_difference):,.0f}.
                """
            )

        else:

            st.info(
                "The scenario produces approximately the same prediction."
            )

    # ========================================================
    # DOWNLOAD REPORT
    # ========================================================

    st.markdown("---")

    st.subheader(
        "📄 Prediction Report"
    )

    report_data = {
        "Metric": [
            "Predicted Credit Limit",
            "Risk Tier",
            "Risk Score",
            "Credit Score",
            "Annual Income",
            "Existing Credit Limit",
            "Credit Utilization",
            "Debt To Income Ratio"
        ],
        "Value": [
            f"₹{prediction:,.2f}",
            risk_tier,
            f"{risk_score}/15",
            user_data.get("Credit_Score", "N/A"),
            user_data.get("Annual_Income", "N/A"),
            user_data.get(
                "Existing_Credit_Limit",
                "N/A"
            ),
            user_data.get(
                "Credit_Utilization",
                "N/A"
            ),
            user_data.get(
                "Debt_To_Income_Ratio",
                "N/A"
            )
        ]
    }

    report_df = pd.DataFrame(
        report_data
    )

    csv_data = report_df.to_csv(
        index=False
    )

    st.download_button(
        label="⬇️ Download Prediction Report",
        data=csv_data,
        file_name="FinElite_Credit_Limit_Report.csv",
        mime="text/csv",
        use_container_width=True
    )

    # --------------------------------------------------------
    # FOOTER
    # --------------------------------------------------------

    st.markdown(
        """
        <div class="footer">
            FinElite | AI-Powered Credit Limit Prediction<br>
            Machine Learning • Explainable AI • Credit Intelligence
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()
