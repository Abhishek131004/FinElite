import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

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
# PROJECT PATH
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DATA_PATH = BASE_DIR / "Credir_Card_Bank.xlsx"

TARGET = "Credit_Limit"


# ============================================================
# CONSTANTS
# ============================================================

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
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* =========================================
       GLOBAL
    ========================================= */

    .stApp {
        background: #f4f7fb;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1500px;
    }


    /* =========================================
       SIDEBAR
    ========================================= */

    section[data-testid="stSidebar"] {

        background:
        linear-gradient(
            180deg,
            #06152b 0%,
            #0b2748 100%
        );

    }


    section[data-testid="stSidebar"] * {

        color: white !important;

    }


    section[data-testid="stSidebar"] .stFileUploader {

        background: rgba(255,255,255,0.06);

        border-radius: 12px;

        padding: 10px;

    }


    /* =========================================
       MAIN HEADER
    ========================================= */

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


    /* =========================================
       DATASET BADGE
    ========================================= */

    .dataset-badge {

        background: #e8f1ff;

        color: #1259a5;

        padding: 8px 15px;

        border-radius: 20px;

        font-weight: 700;

        display: inline-block;

        margin-bottom: 20px;

    }


    /* =========================================
       METRIC CARDS
    ========================================= */

    .metric-card {

        background: white;

        padding: 22px;

        border-radius: 18px;

        border: 1px solid #e5eaf1;

        box-shadow:
        0 5px 20px
        rgba(7, 26, 51, 0.06);

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


    /* =========================================
       SECTION CARDS
    ========================================= */

    .section-card {

        background: white;

        padding: 24px;

        border-radius: 18px;

        border: 1px solid #e5eaf1;

        box-shadow:
        0 5px 20px
        rgba(7, 26, 51, 0.05);

        margin-bottom: 20px;

    }


    /* =========================================
       RISK BADGES
    ========================================= */

    .risk-low {

        display: inline-block;

        padding: 9px 20px;

        border-radius: 30px;

        background: #e7f8ef;

        color: #137a45;

        font-weight: 800;

    }


    .risk-medium {

        display: inline-block;

        padding: 9px 20px;

        border-radius: 30px;

        background: #fff4d6;

        color: #9a6700;

        font-weight: 800;

    }


    .risk-high {

        display: inline-block;

        padding: 9px 20px;

        border-radius: 30px;

        background: #ffe6e6;

        color: #b42318;

        font-weight: 800;

    }


    /* =========================================
       INFO BOX
    ========================================= */

    .info-box {

        background: #eef6ff;

        border-left: 5px solid #1976d2;

        padding: 17px;

        border-radius: 10px;

        color: #17324d;

        margin: 15px 0;

    }


    /* =========================================
       FOOTER
    ========================================= */

    .footer {

        text-align: center;

        color: #718096;

        padding: 30px;

        font-size: 13px;

    }


    /* =========================================
       BUTTON
    ========================================= */

    .stButton > button {

        border-radius: 10px;

        font-weight: 700;

        min-height: 42px;

    }


    /* =========================================
       TABS
    ========================================= */

    button[data-baseweb="tab"] {

        font-weight: 700;

        font-size: 15px;

    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# LOAD DEFAULT DATASET
# ============================================================

@st.cache_data
def load_default_data():

    if not DATA_PATH.exists():

        raise FileNotFoundError(
            f"Dataset not found: {DATA_PATH}"
        )

    df = pd.read_excel(
        DATA_PATH
    )

    return df


# ============================================================
# LOAD UPLOADED DATASET
# ============================================================

@st.cache_data
def read_uploaded_file(
    file_bytes,
    file_name
):

    if file_name.lower().endswith(
        ".csv"
    ):

        return pd.read_csv(
            BytesIO(file_bytes)
        )


    elif file_name.lower().endswith(
        (".xlsx", ".xls")
    ):

        return pd.read_excel(
            BytesIO(file_bytes)
        )


    else:

        raise ValueError(
            "Only CSV, XLS and XLSX files are supported."
        )


# ============================================================
# GET DATASET
# ============================================================

def get_dataset():

    uploaded = st.session_state.get(
        "uploaded_file"
    )


    if uploaded is not None:

        return read_uploaded_file(
            uploaded["bytes"],
            uploaded["name"]
        )


    return load_default_data()


# ============================================================
# PREPROCESS DATA
# ============================================================

@st.cache_data
def preprocess_data(df):

    data = df.copy()


    # --------------------------------------------------------
    # TARGET CHECK
    # --------------------------------------------------------

    if TARGET not in data.columns:

        raise ValueError(
            f"Target column '{TARGET}' is missing."
        )


    # --------------------------------------------------------
    # REMOVE MISSING TARGET
    # --------------------------------------------------------

    data[TARGET] = pd.to_numeric(
        data[TARGET],
        errors="coerce"
    )


    data = data.dropna(
        subset=[TARGET]
    )


    # --------------------------------------------------------
    # DROP UNNECESSARY COLUMNS
    # --------------------------------------------------------

    columns_to_drop = [

        col

        for col in DROP_COLUMNS

        if col in data.columns

    ]


    data = data.drop(
        columns=columns_to_drop,
        errors="ignore"
    )


    # --------------------------------------------------------
    # TARGET
    # --------------------------------------------------------

    y = data[TARGET].copy()


    data = data.drop(
        columns=[TARGET]
    )


    # --------------------------------------------------------
    # AUTOMATIC CATEGORICAL DETECTION
    # --------------------------------------------------------

    categorical_columns = (

        data
        .select_dtypes(
            include=[
                "object",
                "category",
                "bool"
            ]
        )
        .columns
        .tolist()

    )


    # --------------------------------------------------------
    # HANDLE CATEGORICAL MISSING VALUES
    # --------------------------------------------------------

    for col in categorical_columns:

        data[col] = (

            data[col]

            .astype(str)

            .replace(
                "nan",
                "Unknown"
            )

            .fillna(
                "Unknown"
            )

        )


    # --------------------------------------------------------
    # ONE HOT ENCODING
    # --------------------------------------------------------

    data = pd.get_dummies(
        data,
        columns=categorical_columns,
        drop_first=True
    )


    # --------------------------------------------------------
    # NUMERIC CONVERSION
    # --------------------------------------------------------

    for col in data.columns:

        data[col] = pd.to_numeric(
            data[col],
            errors="coerce"
        )


    # --------------------------------------------------------
    # MISSING NUMERIC VALUES
    # --------------------------------------------------------

    for col in data.columns:

        if data[col].isna().any():

            median = data[col].median()


            if pd.isna(median):

                median = 0


            data[col] = data[col].fillna(
                median
            )


    # --------------------------------------------------------
    # BOOL TO INT
    # --------------------------------------------------------

    for col in data.columns:

        if data[col].dtype == bool:

            data[col] = data[col].astype(
                int
            )


    return data, y


# ============================================================
# TRAIN XGBOOST MODEL
# ============================================================

@st.cache_resource
def train_model(df):

    X, y = preprocess_data(
        df
    )


    # --------------------------------------------------------
    # TRAIN TEST SPLIT
    # --------------------------------------------------------

    X_train, X_test, y_train, y_test = train_test_split(

        X,

        y,

        test_size=0.20,

        random_state=42

    )


    # --------------------------------------------------------
    # XGBOOST
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # TRAIN
    # --------------------------------------------------------

    model.fit(
        X_train,
        y_train
    )


    # --------------------------------------------------------
    # PREDICTION
    # --------------------------------------------------------

    predictions = model.predict(
        X_test
    )


    # --------------------------------------------------------
    # METRICS
    # --------------------------------------------------------

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
# DEFAULT VALUE
# ============================================================

def get_default_value(
    series
):

    if pd.api.types.is_numeric_dtype(
        series
    ):

        value = series.median()


        if pd.isna(value):

            return 0


        return float(value)


    mode = series.mode()


    if len(mode) > 0:

        return mode.iloc[0]


    return "Unknown"


# ============================================================
# BUILD APPLICANT FORM
# ============================================================

def build_input_form(
    raw_df
):

    user_data = {}


    # ========================================================
    # PERSONAL
    # ========================================================

    st.sidebar.markdown(
        "## 👤 Applicant Profile"
    )


    # ========================================================
    # NUMERIC FIELDS
    # ========================================================

    for field in NUMERIC_FIELDS:


        if field not in raw_df.columns:

            continue


        series = pd.to_numeric(

            raw_df[field],

            errors="coerce"

        ).dropna()


        if len(series) == 0:

            continue


        min_value = float(
            series.min()
        )


        max_value = float(
            series.max()
        )


        median_value = float(
            series.median()
        )


        label = field.replace(
            "_",
            " "
        )


        # ----------------------------------------------------
        # INTEGER
        # ----------------------------------------------------

        if field in INTEGER_FIELDS:

            user_data[field] = st.sidebar.number_input(

                label,

                min_value=int(
                    min_value
                ),

                max_value=int(
                    max_value
                ),

                value=int(
                    median_value
                ),

                step=1,

                key=f"input_{field}"

            )


        # ----------------------------------------------------
        # FLOAT
        # ----------------------------------------------------

        else:

            step = (

                max_value
                - min_value

            ) / 100


            if step <= 0:

                step = 1.0


            user_data[field] = st.sidebar.number_input(

                label,

                min_value=min_value,

                max_value=max_value,

                value=median_value,

                step=float(step),

                key=f"input_{field}"

            )


    # ========================================================
    # CATEGORICAL
    # ========================================================

    existing_categories = [

        col

        for col in CATEGORICAL_COLUMNS

        if col in raw_df.columns

    ]


    if existing_categories:

        st.sidebar.markdown("---")

        st.sidebar.markdown(
            "## 🏢 Applicant Details"
        )


    for col in existing_categories:


        options = (

            raw_df[col]

            .dropna()

            .astype(str)

            .unique()

            .tolist()

        )


        options = sorted(
            options
        )


        if not options:

            continue


        default = str(

            get_default_value(
                raw_df[col]
            )

        )


        if default not in options:

            default = options[0]


        user_data[col] = st.sidebar.selectbox(

            col.replace(
                "_",
                " "
            ),

            options,

            index=options.index(
                default
            ),

            key=f"input_{col}"

        )


    return user_data


# ============================================================
# PREPARE USER DATA
# ============================================================

def prepare_user_data(

    user_data,

    feature_columns

):

    user_df = pd.DataFrame(
        [user_data]
    )


    # --------------------------------------------------------
    # DROP
    # --------------------------------------------------------

    user_df = user_df.drop(

        columns=[

            col

            for col in DROP_COLUMNS

            if col in user_df.columns

        ],

        errors="ignore"

    )


    # --------------------------------------------------------
    # CATEGORICAL
    # --------------------------------------------------------

    categorical_columns = (

        user_df

        .select_dtypes(

            include=[

                "object",

                "category",

                "bool"

            ]

        )

        .columns

        .tolist()

    )


    # --------------------------------------------------------
    # ENCODE
    # --------------------------------------------------------

    user_df = pd.get_dummies(

        user_df,

        columns=categorical_columns,

        drop_first=True

    )


    # --------------------------------------------------------
    # NUMERIC
    # --------------------------------------------------------

    for col in user_df.columns:

        user_df[col] = pd.to_numeric(

            user_df[col],

            errors="coerce"

        )


    user_df = user_df.fillna(
        0
    )


    # --------------------------------------------------------
    # MATCH FEATURES
    # --------------------------------------------------------

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

def calculate_risk(
    user_data
):

    score = 0


    credit_score = user_data.get(
        "Credit_Score",
        700
    )


    utilization = user_data.get(
        "Credit_Utilization",
        30
    )


    dti = user_data.get(
        "Debt_To_Income_Ratio",
        30
    )


    missed = user_data.get(
        "Missed_Payments",
        0
    )


    defaults = user_data.get(
        "Number_of_Default",
        0
    )


    # --------------------------------------------------------
    # CREDIT SCORE
    # --------------------------------------------------------

    if credit_score >= 750:

        score += 0

    elif credit_score >= 650:

        score += 1

    elif credit_score >= 550:

        score += 2

    else:

        score += 3


    # --------------------------------------------------------
    # UTILIZATION
    # --------------------------------------------------------

    if utilization <= 30:

        score += 0

    elif utilization <= 50:

        score += 1

    elif utilization <= 75:

        score += 2

    else:

        score += 3


    # --------------------------------------------------------
    # DTI
    # --------------------------------------------------------

    if dti <= 30:

        score += 0

    elif dti <= 45:

        score += 1

    elif dti <= 60:

        score += 2

    else:

        score += 3


    # --------------------------------------------------------
    # MISSED PAYMENTS
    # --------------------------------------------------------

    if missed == 0:

        score += 0

    elif missed <= 2:

        score += 1

    elif missed <= 5:

        score += 2

    else:

        score += 3


    # --------------------------------------------------------
    # DEFAULTS
    # --------------------------------------------------------

    if defaults == 0:

        score += 0

    elif defaults <= 1:

        score += 2

    else:

        score += 3


    # --------------------------------------------------------
    # RISK
    # --------------------------------------------------------

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

def create_risk_gauge(
    risk_score
):

    percentage = min(

        100,

        (risk_score / 15) * 100

    )


    fig = go.Figure(

        go.Indicator(

            mode="gauge+number",

            value=percentage,

            title={
                "text": "Credit Risk Score"
            },

            gauge={

                "axis": {
                    "range": [0, 100]
                },

                "steps": [

                    {
                        "range": [
                            0,
                            35
                        ]
                    },

                    {
                        "range": [
                            35,
                            65
                        ]
                    },

                    {
                        "range": [
                            65,
                            100
                        ]
                    }

                ],

                "threshold": {

                    "line": {
                        "width": 4
                    },

                    "value": percentage

                }

            }

        )

    )


    fig.update_layout(

        height=320,

        margin=dict(

            l=20,

            r=20,

            t=60,

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

    importance_df = pd.DataFrame({

        "Feature":
            feature_columns,

        "Importance":
            model.feature_importances_

    })


    importance_df = (

        importance_df

        .sort_values(

            "Importance",

            ascending=False

        )

        .head(15)

    )


    importance_df["Feature"] = (

        importance_df["Feature"]

        .str.replace(

            "_",

            " ",

            regex=False

        )

    )


    fig = px.bar(

        importance_df.sort_values(
            "Importance"
        ),

        x="Importance",

        y="Feature",

        orientation="h",

        title="Top 15 Model Features"

    )


    fig.update_layout(
        height=500
    )


    return fig


# ============================================================
# SHAP
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


        shap_values = np.asarray(
            shap_values
        ).flatten()


        shap_df = pd.DataFrame({

            "Feature":
                user_df.columns,

            "SHAP":
                shap_values,

            "Value":
                user_df.iloc[0].values

        })


        shap_df["Abs_SHAP"] = (

            shap_df["SHAP"]

            .abs()

        )


        shap_df = (

            shap_df

            .sort_values(

                "Abs_SHAP",

                ascending=False

            )

            .head(12)

        )


        shap_df["Feature"] = (

            shap_df["Feature"]

            .str.replace(

                "_",

                " ",

                regex=False

            )

        )


        fig = px.bar(

            shap_df.sort_values(
                "SHAP"
            ),

            x="SHAP",

            y="Feature",

            orientation="h",

            title="How Features Influenced This Prediction"

        )


        fig.update_layout(
            height=500
        )


        return fig


    except Exception:

        return None


# ============================================================
# DATASET OVERVIEW
# ============================================================

def dataset_overview(
    df
):

    st.subheader(
        "📊 Dataset Overview"
    )


    c1, c2, c3, c4 = st.columns(4)


    with c1:

        st.metric(
            "Rows",
            f"{df.shape[0]:,}"
        )


    with c2:

        st.metric(
            "Columns",
            f"{df.shape[1]:,}"
        )


    with c3:

        st.metric(
            "Missing Values",
            f"{df.isna().sum().sum():,}"
        )


    with c4:

        numeric_count = len(

            df.select_dtypes(

                include=np.number

            ).columns

        )


        st.metric(
            "Numeric Columns",
            numeric_count
        )


# ============================================================
# DATASET EXPLORER
# ============================================================

def dataset_explorer(
    raw_df
):

    st.subheader(
        "📂 Dataset Explorer"
    )


    dataset_overview(
        raw_df
    )


    st.markdown("---")


    # ========================================================
    # PREVIEW
    # ========================================================

    st.subheader(
        "🔎 Dataset Preview"
    )


    max_rows = min(
        100,
        len(raw_df)
    )


    preview_rows = st.slider(

        "Rows to display",

        min_value=5,

        max_value=max_rows,

        value=min(
            10,
            max_rows
        )

    )


    st.dataframe(

        raw_df.head(
            preview_rows
        ),

        use_container_width=True,

        height=400

    )


    # ========================================================
    # COLUMN INFORMATION
    # ========================================================

    st.subheader(
        "🧾 Column Information"
    )


    column_info = pd.DataFrame({

        "Column":
            raw_df.columns,

        "Data Type": [

            str(dtype)

            for dtype
            in raw_df.dtypes

        ],

        "Missing Values": [

            int(
                raw_df[col].isna().sum()
            )

            for col
            in raw_df.columns

        ],

        "Unique Values": [

            int(
                raw_df[col].nunique()
            )

            for col
            in raw_df.columns

        ]

    })


    st.dataframe(

        column_info,

        use_container_width=True,

        height=350

    )


    # ========================================================
    # MISSING VALUES
    # ========================================================

    st.subheader(
        "⚠️ Missing Value Analysis"
    )


    missing_df = pd.DataFrame({

        "Column":
            raw_df.columns,

        "Missing":
            raw_df.isna().sum().values

    })


    missing_df["Percentage"] = (

        missing_df["Missing"]

        / len(raw_df)

        * 100

    )


    missing_df = (

        missing_df[

            missing_df["Missing"] > 0

        ]

        .sort_values(

            "Missing",

            ascending=False

        )

    )


    if len(missing_df) > 0:

        fig = px.bar(

            missing_df.head(20),

            x="Column",

            y="Missing",

            title="Columns With Missing Values"

        )


        fig.update_layout(

            xaxis_tickangle=-45

        )


        st.plotly_chart(

            fig,

            use_container_width=True

        )


        st.dataframe(

            missing_df,

            use_container_width=True,

            hide_index=True

        )


    else:

        st.success(
            "✅ No missing values found."
        )


    # ========================================================
    # TARGET DISTRIBUTION
    # ========================================================

    if TARGET in raw_df.columns:

        st.subheader(
            "🎯 Credit Limit Distribution"
        )


        target = pd.to_numeric(

            raw_df[TARGET],

            errors="coerce"

        ).dropna()


        fig = px.histogram(

            target,

            nbins=40,

            title="Credit Limit Distribution"

        )


        st.plotly_chart(

            fig,

            use_container_width=True

        )


    # ========================================================
    # NUMERIC CORRELATION
    # ========================================================

    numeric_df = raw_df.select_dtypes(
        include=np.number
    )


    if (

        TARGET in numeric_df.columns

        and len(numeric_df.columns) > 1

    ):

        st.subheader(
            "📈 Correlation With Credit Limit"
        )


        correlations = (

            numeric_df

            .corr()[TARGET]

            .drop(TARGET)

            .sort_values()

        )


        correlation_df = pd.DataFrame({

            "Feature":
                correlations.index,

            "Correlation":
                correlations.values

        })


        fig = px.bar(

            correlation_df,

            x="Correlation",

            y="Feature",

            orientation="h",

            title="Feature Correlation With Credit Limit"

        )


        st.plotly_chart(

            fig,

            use_container_width=True

        )


    # ========================================================
    # DOWNLOAD
    # ========================================================

    st.subheader(
        "⬇️ Download Dataset"
    )


    csv_dataset = raw_df.to_csv(
        index=False
    )


    st.download_button(

        "Download Dataset as CSV",

        data=csv_dataset,

        file_name="FinElite_Dataset.csv",

        mime="text/csv",

        use_container_width=True

    )


# ============================================================
# MAIN
# ============================================================

def main():


    # ========================================================
    # SESSION STATE
    # ========================================================

    if "uploaded_file" not in st.session_state:

        st.session_state[
            "uploaded_file"
        ] = None


    # ========================================================
    # SIDEBAR BRAND
    # ========================================================

    st.sidebar.markdown(

        """
        <div style="
            text-align:center;
            padding:15px 5px;
        ">

            <div style="
                font-size:42px;
            ">
                💳
            </div>

            <h1 style="
                color:white;
                margin-bottom:0;
            ">
                FinElite
            </h1>

            <p style="
                color:#b8c7da;
            ">
                AI Credit Intelligence
            </p>

        </div>
        """,

        unsafe_allow_html=True

    )


    # ========================================================
    # DATASET UPLOAD
    # ========================================================

    st.sidebar.markdown(
        "## 📂 Dataset"
    )


    uploaded_file = st.sidebar.file_uploader(

        "Upload Dataset",

        type=[

            "xlsx",

            "xls",

            "csv"

        ],

        help=(
            "Dataset must contain "
            "Credit_Limit as target column."
        )

    )


    if uploaded_file is not None:

        file_bytes = (
            uploaded_file.getvalue()
        )


        st.session_state[
            "uploaded_file"
        ] = {

            "name":
                uploaded_file.name,

            "bytes":
                file_bytes

        }


        st.sidebar.success(

            f"Loaded: "
            f"{uploaded_file.name}"

        )


    # ========================================================
    # LOAD DATASET
    # ========================================================

    try:

        raw_df = get_dataset()


    except Exception as e:

        st.error(
            f"❌ Dataset loading error: {e}"
        )


        st.info(

            "Make sure "

            "`Credir_Card_Bank.xlsx` "

            "is in the project root."

        )


        st.stop()


    # ========================================================
    # TARGET VALIDATION
    # ========================================================

    if TARGET not in raw_df.columns:

        st.error(

            f"❌ Target column "
            f"'{TARGET}' was not found."

        )


        st.write(
            "Available columns:"
        )


        st.write(
            list(raw_df.columns)
        )


        st.stop()


    # ========================================================
    # DATASET SIDEBAR INFO
    # ========================================================

    st.sidebar.markdown("---")


    st.sidebar.markdown(
        "### 📌 Current Dataset"
    )


    st.sidebar.write(

        f"Rows: "
        f"**{len(raw_df):,}**"

    )


    st.sidebar.write(

        f"Columns: "
        f"**{len(raw_df.columns):,}**"

    )


    st.sidebar.write(

        f"Target: "
        f"**{TARGET}**"

    )


    # ========================================================
    # TRAIN MODEL
    # ========================================================

    with st.spinner(
        "Training FinElite XGBoost model..."
    ):

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

            ) = train_model(
                raw_df
            )


        except Exception as e:

            st.error(

                f"❌ Model training failed: {e}"

            )


            st.stop()


    # ========================================================
    # SIDEBAR APPLICANT INPUT
    # ========================================================

    user_data = build_input_form(
        raw_df
    )


    # ========================================================
    # RESET
    # ========================================================

    st.sidebar.markdown("---")


    if st.sidebar.button(

        "🔄 Reset Application",

        use_container_width=True

    ):

        st.session_state.clear()

        st.rerun()


    # ========================================================
    # PREPARE USER INPUT
    # ========================================================

    user_df = prepare_user_data(

        user_data,

        X.columns

    )


    # ========================================================
    # PREDICTION
    # ========================================================

    prediction = predict_limit(

        model,

        user_df

    )


    # ========================================================
    # RISK
    # ========================================================

    (

        risk_tier,

        risk_score,

        risk_class

    ) = calculate_risk(
        user_data
    )


    # ========================================================
    # HEADER
    # ========================================================

    st.markdown(

        '<div class="main-title">'
        'FinElite'
        '</div>',

        unsafe_allow_html=True

    )


    st.markdown(

        """
        <div class="subtitle">

        AI-Powered Credit Card Limit Prediction
        & Credit Risk Intelligence

        </div>
        """,

        unsafe_allow_html=True

    )


    # ========================================================
    # DATASET BADGE
    # ========================================================

    dataset_name = (
        "Credir_Card_Bank.xlsx"
    )


    if st.session_state.get(
        "uploaded_file"
    ):

        dataset_name = (

            st.session_state[
                "uploaded_file"
            ]["name"]

        )


    st.markdown(

        f"""
        <div class="dataset-badge">

        📂 Dataset: {dataset_name}

        </div>
        """,

        unsafe_allow_html=True

    )


    # ========================================================
    # TOP METRICS
    # ========================================================

    col1, col2, col3, col4 = st.columns(4)


    # --------------------------------------------------------
    # CREDIT LIMIT
    # --------------------------------------------------------

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

                    XGBoost prediction

                </div>

            </div>
            """,

            unsafe_allow_html=True

        )


    # --------------------------------------------------------
    # RISK
    # --------------------------------------------------------

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

                    Risk Score: {risk_score}/15

                </div>

            </div>
            """,

            unsafe_allow_html=True

        )


    # --------------------------------------------------------
    # CREDIT SCORE
    # --------------------------------------------------------

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

                    Applicant profile

                </div>

            </div>
            """,

            unsafe_allow_html=True

        )


    # --------------------------------------------------------
    # UTILIZATION
    # --------------------------------------------------------

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


    st.markdown(
        "<br>",
        unsafe_allow_html=True
    )


    # ========================================================
    # TABS
    # ========================================================

    tab1, tab2, tab3, tab4 = st.tabs(

        [

            "👤 Applicant Assessment",

            "🧠 Model Insights",

            "🎯 Scenario Simulator",

            "📂 Dataset Explorer"

        ]

    )


    # ========================================================
    # TAB 1
    # ========================================================

    with tab1:

        left, right = st.columns(

            [1.3, 1]

        )


        # ====================================================
        # RECOMMENDATION
        # ====================================================

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
                    padding:25px;
                ">

                    <div style="
                        font-size:16px;
                        color:#718096;
                    ">

                        Recommended Credit Limit

                    </div>

                    <div style="
                        font-size:50px;
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


        # ====================================================
        # RISK GAUGE
        # ====================================================

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


        # ====================================================
        # FINANCIAL SUMMARY
        # ====================================================

        st.markdown(

            '<div class="section-card">',

            unsafe_allow_html=True

        )


        st.subheader(

            "Applicant Financial Summary"

        )


        summary = st.columns(4)


        summary_data = [

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


        for col, (

            title,

            value

        ) in zip(

            summary,

            summary_data

        ):


            with col:

                st.metric(

                    title,

                    value

                )


        st.markdown(

            "</div>",

            unsafe_allow_html=True

        )


        # ====================================================
        # RECOMMENDATION
        # ====================================================

        if risk_tier == "LOW":

            recommendation = (

                "Applicant demonstrates a relatively "
                "strong credit profile. The recommended "
                "credit limit can be considered subject "
                "to institutional credit policies."

            )


        elif risk_tier == "MEDIUM":

            recommendation = (

                "Applicant presents moderate credit risk. "
                "Consider income stability, existing "
                "liabilities and repayment history "
                "before approval."

            )


        else:

            recommendation = (

                "Applicant presents elevated credit risk. "
                "A conservative credit limit and "
                "additional verification may be appropriate."

            )


        st.markdown(

            f"""
            <div class="info-box">

                <b>💡 FinElite Recommendation</b>

                <br><br>

                {recommendation}

            </div>
            """,

            unsafe_allow_html=True

        )


    # ========================================================
    # TAB 2 - MODEL INSIGHTS
    # ========================================================

    with tab2:

        st.subheader(

            "🧠 Model Insights & Explainable AI"

        )


        insight1, insight2 = st.columns(2)


        # ====================================================
        # FEATURE IMPORTANCE
        # ====================================================

        with insight1:

            st.plotly_chart(

                feature_importance_chart(

                    model,

                    X.columns

                ),

                use_container_width=True

            )


        # ====================================================
        # SHAP
        # ====================================================

        with insight2:

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

                        "SHAP explanation could not "
                        "be generated."

                    )

            else:

                st.warning(

                    "SHAP is not installed."

                )

                st.code(
                    "pip install shap"
                )


        # ====================================================
        # MODEL PERFORMANCE
        # ====================================================

        st.subheader(

            "📈 Model Performance"

        )


        p1, p2, p3 = st.columns(3)


        with p1:

            st.metric(

                "R² Score",

                f"{r2 * 100:.2f}%"

            )


        with p2:

            st.metric(

                "MAE",

                f"₹{mae:,.0f}"

            )


        with p3:

            st.metric(

                "RMSE",

                f"₹{rmse:,.0f}"

            )


        st.markdown(

            f"""
            <div class="info-box">

            <b>Model:</b>
            XGBoost Regressor

            <br><br>

            <b>Training Records:</b>
            {len(X_train):,}

            <br>

            <b>Testing Records:</b>
            {len(X_test):,}

            <br><br>

            <b>R² Score:</b>
            Measures how much variation in the
            credit limit is explained by the model.

            <br><br>

            <b>MAE:</b>
            Average absolute prediction error.

            <br><br>

            <b>RMSE:</b>
            Penalizes larger prediction errors more strongly.

            </div>
            """,

            unsafe_allow_html=True

        )


    # ========================================================
    # TAB 3 - SCENARIO
    # ========================================================

    with tab3:

        st.subheader(

            "🎯 What-If Scenario Simulator"

        )


        st.write(

            "Change annual income and credit score "
            "to see how the predicted credit limit changes."

        )


        scenario_col1, scenario_col2 = st.columns(2)


        # ====================================================
        # INCOME
        # ====================================================

        with scenario_col1:

            if "Annual_Income" in raw_df.columns:

                income_series = pd.to_numeric(

                    raw_df["Annual_Income"],

                    errors="coerce"

                ).dropna()


                scenario_income = st.slider(

                    "Scenario Annual Income",

                    min_value=float(

                        income_series.min()

                    ),

                    max_value=float(

                        income_series.max()

                    ),

                    value=float(

                        user_data.get(

                            "Annual_Income",

                            income_series.median()

                        )

                    )

                )


            else:

                scenario_income = user_data.get(

                    "Annual_Income",

                    0

                )


        # ====================================================
        # CREDIT SCORE
        # ====================================================

        with scenario_col2:

            if "Credit_Score" in raw_df.columns:

                score_series = pd.to_numeric(

                    raw_df["Credit_Score"],

                    errors="coerce"

                ).dropna()


                scenario_score = st.slider(

                    "Scenario Credit Score",

                    min_value=int(

                        score_series.min()

                    ),

                    max_value=int(

                        score_series.max()

                    ),

                    value=int(

                        user_data.get(

                            "Credit_Score",

                            score_series.median()

                        )

                    )

                )


            else:

                scenario_score = user_data.get(

                    "Credit_Score",

                    0

                )


        # ====================================================
        # SCENARIO
        # ====================================================

        scenario_data = user_data.copy()


        scenario_data[
            "Annual_Income"
        ] = scenario_income


        scenario_data[
            "Credit_Score"
        ] = scenario_score


        scenario_df = prepare_user_data(

            scenario_data,

            X.columns

        )


        scenario_prediction = predict_limit(

            model,

            scenario_df

        )


        difference = (

            scenario_prediction
            - prediction

        )


        # ====================================================
        # METRICS
        # ====================================================

        s1, s2, s3 = st.columns(3)


        with s1:

            st.metric(

                "Current Limit",

                f"₹{prediction:,.0f}"

            )


        with s2:

            st.metric(

                "Scenario Limit",

                f"₹{scenario_prediction:,.0f}"

            )


        with s3:

            st.metric(

                "Change",

                f"₹{difference:,.0f}"

            )


        # ====================================================
        # CHART
        # ====================================================

        chart_df = pd.DataFrame({

            "Profile": [

                "Current",

                "Scenario"

            ],

            "Credit Limit": [

                prediction,

                scenario_prediction

            ]

        })


        fig = px.bar(

            chart_df,

            x="Profile",

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


        # ====================================================
        # INTERPRETATION
        # ====================================================

        if difference > 0:

            st.success(

                f"📈 The scenario increases "
                f"the predicted credit limit by "
                f"₹{difference:,.0f}."

            )


        elif difference < 0:

            st.warning(

                f"📉 The scenario decreases "
                f"the predicted credit limit by "
                f"₹{abs(difference):,.0f}."

            )


        else:

            st.info(

                "The scenario produces approximately "
                "the same prediction."

            )


    # ========================================================
    # TAB 4 - DATASET
    # ========================================================

    with tab4:

        dataset_explorer(
            raw_df
        )


    # ========================================================
    # REPORT
    # ========================================================

    st.markdown("---")


    st.subheader(
        "📄 Prediction Report"
    )


    report_df = pd.DataFrame({

        "Metric": [

            "Predicted Credit Limit",

            "Risk Tier",

            "Risk Score",

            "Credit Score",

            "Annual Income",

            "Existing Credit Limit",

            "Credit Utilization",

            "Debt To Income Ratio",

            "Model",

            "Dataset Rows"

        ],


        "Value": [

            f"₹{prediction:,.2f}",

            risk_tier,

            f"{risk_score}/15",

            user_data.get(

                "Credit_Score",

                "N/A"

            ),

            user_data.get(

                "Annual_Income",

                "N/A"

            ),

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

            ),

            "XGBoost Regressor",

            len(raw_df)

        ]

    })


    st.dataframe(

        report_df,

        use_container_width=True,

        hide_index=True

    )


    # ========================================================
    # DOWNLOAD REPORT
    # ========================================================

    csv_report = report_df.to_csv(

        index=False

    )


    st.download_button(

        "⬇️ Download Prediction Report",

        data=csv_report,

        file_name="FinElite_Credit_Limit_Report.csv",

        mime="text/csv",

        use_container_width=True

    )


    # ========================================================
    # FOOTER
    # ========================================================

    st.markdown(

        """
        <div class="footer">

            <b>FinElite</b>
            | AI-Powered Credit Limit Prediction

            <br>

            Machine Learning • XGBoost •
            Explainable AI • Credit Intelligence

        </div>
        """,

        unsafe_allow_html=True

    )


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":

    main()
