import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os


# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Credit Card Banking Analytics",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# LOGIN CREDENTIALS
# ============================================================
USERNAME = "admin"
PASSWORD = "admin123"


# ============================================================
# SESSION STATE
# ============================================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""


# ============================================================
# PROFESSIONAL LIGHT COLOR SYSTEM
# ============================================================
COLORS = {
    "navy": "#253B5B",
    "blue": "#6C9EF8",
    "light_blue": "#DCEBFF",
    "purple": "#A78BFA",
    "light_purple": "#EEE7FF",
    "teal": "#63C7C5",
    "light_teal": "#DDF5F2",
    "green": "#7BCFA6",
    "light_green": "#E5F7EE",
    "yellow": "#F4D58D",
    "light_yellow": "#FFF5D8",
    "orange": "#F2B880",
    "light_orange": "#FFF0E3",
    "pink": "#E5A6C8",
    "light_pink": "#FBEAF3",
    "red": "#E79A9A",
    "light_red": "#FFF0F0",
    "bg": "#F6F8FC",
    "card": "#FFFFFF",
    "text": "#26364D",
    "muted": "#718096",
    "border": "#DDE5F0"
}


PALETTE = [
    "#8DB7F7",
    "#B09AF5",
    "#70C9C5",
    "#8ED5AF",
    "#F2D48B",
    "#F2B487",
    "#DFA8C8",
    "#AEBCE8"
]


RISK_COLORS = {
    "Lower": "#8FD1A9",
    "Moderate": "#F1CF7D",
    "Higher": "#E59A9A"
}


# ============================================================
# MAIN DASHBOARD CSS
# ============================================================
st.markdown(
    f"""
<style>

.stApp {{
    background: {COLORS["bg"]};
}}

.block-container {{
    padding-top: 1rem;
    padding-bottom: 2rem;
    max-width: 1550px;
}}

section[data-testid="stSidebar"] {{
    background: linear-gradient(
        180deg,
        #EAF1FB 0%,
        #F3F0FC 100%
    );
    border-right: 1px solid {COLORS["border"]};
}}

.dashboard-title {{
    font-size: 2.35rem;
    font-weight: 800;
    color: {COLORS["navy"]};
    margin-bottom: 2px;
}}

.dashboard-subtitle {{
    color: {COLORS["muted"]};
    font-size: 1rem;
    margin-bottom: 16px;
}}

.section-header {{
    background: linear-gradient(
        90deg,
        #DCE9FA,
        #EEE9FC
    );
    color: {COLORS["navy"]};
    padding: 10px 16px;
    border-radius: 11px;
    margin: 16px 0 12px 0;
    font-size: 1.05rem;
    font-weight: 750;
    border: 1px solid #DDE5F2;
}}

.filter-title {{
    background: linear-gradient(
        90deg,
        #DCEBFF,
        #EEE7FF
    );
    color: #30486B;
    padding: 8px 11px;
    border-radius: 9px;
    font-weight: 750;
    margin: 10px 0 8px 0;
}}

[data-testid="stMetric"] {{
    background: white;
    border: 1px solid {COLORS["border"]};
    border-radius: 14px;
    padding: 13px;
    box-shadow: 0 3px 12px rgba(37,59,91,0.055);
}}

[data-testid="stMetricLabel"] {{
    color: {COLORS["muted"]};
}}

[data-testid="stMetricValue"] {{
    color: {COLORS["navy"]};
}}

div[data-baseweb="select"] > div {{
    background: #FFFFFF;
    border-color: #C9D6EA;
    border-radius: 9px;
}}

div[data-baseweb="select"] > div:hover {{
    border-color: #9EB6DC;
}}

div[data-testid="stSlider"] {{
    padding-bottom: 5px;
}}

div.stButton > button {{
    border-radius: 9px;
    border: 1px solid #B8C9E3;
    background: #FFFFFF;
    color: #30486B;
}}

div.stButton > button:hover {{
    border-color: #7D9CCB;
    background: #F2F6FC;
}}

.insight {{
    background: {COLORS["light_green"]};
    border-left: 4px solid {COLORS["green"]};
    padding: 11px 14px;
    border-radius: 8px;
    margin: 7px 0;
    color: #365447;
}}

.risk {{
    background: {COLORS["light_red"]};
    border-left: 4px solid {COLORS["red"]};
    padding: 11px 14px;
    border-radius: 8px;
    margin: 7px 0;
    color: #654646;
}}

.info-box {{
    background: {COLORS["light_blue"]};
    border-left: 4px solid {COLORS["blue"]};
    padding: 11px 14px;
    border-radius: 8px;
    color: #38506F;
}}

.stTabs [data-baseweb="tab-list"] {{
    gap: 7px;
}}

.stTabs [data-baseweb="tab"] {{
    border-radius: 9px;
    padding: 8px 13px;
}}

.sidebar-note {{
    background: rgba(255,255,255,.72);
    padding: 10px;
    border-radius: 10px;
    border: 1px solid #DDE5F0;
    color: #5E6D83;
    font-size: 0.82rem;
}}

</style>
""",
    unsafe_allow_html=True
)


# ============================================================
# LOGIN PAGE CSS
# ============================================================
st.markdown(
    """
<style>

.login-background {
    min-height: 82vh;
    display: flex;
    justify-content: center;
    align-items: center;
}

.login-logo {
    width: 82px;
    height: 82px;
    margin: 0 auto 18px auto;
    border-radius: 22px;
    background: linear-gradient(
        135deg,
        #6C9EF8,
        #A78BFA
    );
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 40px;
    box-shadow: 0 8px 22px rgba(108,158,248,0.25);
}

.login-title {
    font-size: 30px;
    font-weight: 800;
    color: #253B5B;
    text-align: center;
    margin-bottom: 5px;
}

.login-subtitle {
    text-align: center;
    color: #718096;
    font-size: 14px;
    margin-bottom: 25px;
}

.login-security {
    background: #EEF5FF;
    border-left: 4px solid #6C9EF8;
    padding: 12px;
    border-radius: 9px;
    margin-top: 18px;
    color: #405775;
    font-size: 13px;
}

.login-footer {
    text-align: center;
    color: #9AA6B8;
    font-size: 12px;
    margin-top: 20px;
}

</style>
""",
    unsafe_allow_html=True
)


# ============================================================
# LOGIN PAGE FUNCTION
# ============================================================
def login_page():

    st.markdown(
        "<div style='height:35px;'></div>",
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns([1, 1.15, 1])

    with col2:

        st.markdown(
            """
            <div class="login-logo">
                💳
            </div>

            <div class="login-title">
                Banking Analytics
            </div>

            <div class="login-subtitle">
                Credit Card Customer Intelligence Portal
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            """
            <div style="
                background:white;
                padding:30px;
                border-radius:20px;
                border:1px solid #DDE5F0;
                box-shadow:0 10px 35px rgba(37,59,91,0.10);
            ">
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            """
            <h3 style="
                text-align:center;
                color:#253B5B;
                margin-bottom:5px;
            ">
                🔐 Secure Login
            </h3>

            <p style="
                text-align:center;
                color:#718096;
                font-size:14px;
                margin-bottom:22px;
            ">
                Sign in to access your analytics dashboard
            </p>
            """,
            unsafe_allow_html=True
        )

        username = st.text_input(
            "👤 Username",
            placeholder="Enter username",
            key="login_username"
        )

        password = st.text_input(
            "🔑 Password",
            placeholder="Enter password",
            type="password",
            key="login_password"
        )

        remember = st.checkbox(
            "Remember this session",
            value=True
        )

        login_button = st.button(
            "🚀 Login to Dashboard",
            use_container_width=True
        )

        if login_button:

            if username.strip() == "" or password.strip() == "":
                st.warning(
                    "⚠️ Please enter both username and password."
                )

            elif (
                username == USERNAME
                and password == PASSWORD
            ):

                st.session_state.logged_in = True
                st.session_state.username = username

                st.success(
                    "✅ Login successful! Opening dashboard..."
                )

                st.rerun()

            else:
                st.error(
                    "❌ Incorrect username or password."
                )

        st.markdown(
            """
            <div class="login-security">
                🔒 <b>Secure Access</b><br>
                Your dashboard is available only after successful authentication.
            </div>

            <div style="
                text-align:center;
                margin-top:18px;
                color:#718096;
                font-size:12px;
                line-height:1.7;
            ">
                <b>Demo Credentials</b><br>
                Username: <b>admin</b><br>
                Password: <b>admin123</b>
            </div>

            <div class="login-footer">
                💳 Credit Card Banking Analytics<br>
                Built with Streamlit • Pandas • Plotly
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )


# ============================================================
# SHOW LOGIN PAGE BEFORE DASHBOARD
# ============================================================
if not st.session_state.logged_in:
    login_page()
    st.stop()


# ============================================================
# LOAD DATA
# ============================================================
@st.cache_data
def load_data(uploaded_file):

    if uploaded_file is not None:

        df = pd.read_excel(uploaded_file)

    else:

        possible_files = [
            "Credir_Card_Bank.xlsx",
            "Credir_Card_Bank(4).xlsx",
            "Credit_Card_Bank.xlsx"
        ]

        found = next(
            (
                f for f in possible_files
                if os.path.exists(f)
            ),
            None
        )

        if found is None:
            return None

        df = pd.read_excel(found)

    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.replace(
            " ",
            "_",
            regex=False
        )
    )

    numeric_columns = [
        "Age",
        "Monthly_Income",
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
        "Number_of_Defaults",
        "Credit_Limit"
    ]

    for col in numeric_columns:

        if col in df.columns:

            df[col] = pd.to_numeric(
                df[col],
                errors="coerce"
            )

    # --------------------------------------------------------
    # AGE GROUP
    # --------------------------------------------------------
    if "Age" in df.columns:

        df["Age_Group"] = pd.cut(
            df["Age"],
            bins=[
                0,
                20,
                30,
                50,
                60,
                np.inf
            ],
            labels=[
                "Teen",
                "Young Adult",
                "Adult",
                "Middle Aged",
                "Senior Citizen"
            ]
        )

    # --------------------------------------------------------
    # FINANCIAL GROUPS
    # --------------------------------------------------------
    for col, name, labels in [

        (
            "EMI_Per_Month",
            "EMI_Group",
            [
                "Very Low EMI",
                "Low EMI",
                "Medium EMI",
                "High EMI",
                "Very High EMI"
            ]
        ),

        (
            "Debt_To_Income_Ratio",
            "DTI_Group",
            [
                "Very Low DTI",
                "Low DTI",
                "Medium DTI",
                "High DTI",
                "Very High DTI"
            ]
        ),

        (
            "Savings_Balance",
            "Savings_Group",
            [
                "Very Low Savings",
                "Low Savings",
                "Medium Savings",
                "High Savings",
                "Very High Savings"
            ]
        ),

        (
            "Investment_Value",
            "Investment_Group",
            [
                "Very Low Investment",
                "Low Investment",
                "Medium Investment",
                "High Investment",
                "Very High Investment"
            ]
        )

    ]:

        if col in df.columns:

            try:

                df[name] = pd.qcut(
                    df[col],
                    q=5,
                    labels=labels,
                    duplicates="drop"
                )

            except Exception:

                try:

                    df[name] = pd.cut(
                        df[col],
                        bins=5,
                        labels=labels
                    )

                except Exception:

                    pass

    # --------------------------------------------------------
    # CREDIT BAND
    # --------------------------------------------------------
    if "Credit_Score" in df.columns:

        df["Credit_Band"] = pd.cut(
            df["Credit_Score"],
            bins=[
                0,
                580,
                670,
                740,
                800,
                np.inf
            ],
            labels=[
                "Poor",
                "Fair",
                "Good",
                "Very Good",
                "Excellent"
            ]
        )

    # --------------------------------------------------------
    # DEFAULT FLAG
    # --------------------------------------------------------
    if "Number_of_Defaults" in df.columns:

        df["default_payment_next_month"] = (
            df["Number_of_Defaults"] > 0
        ).astype(int)

    # --------------------------------------------------------
    # HIGH RISK FLAG
    # --------------------------------------------------------
    if all(
        c in df.columns
        for c in [
            "Credit_Score",
            "Credit_Utilization",
            "Missed_Payments"
        ]
    ):

        high_risk = (
            (df["Credit_Score"] < 600)
            |
            (df["Credit_Utilization"] > 75)
            |
            (df["Missed_Payments"] >= 3)
        )

        df["High_Risk_Flag"] = np.where(
            high_risk,
            "High Risk",
            "Standard"
        )

    # --------------------------------------------------------
    # RISK INDICATOR
    # --------------------------------------------------------
    risk_cols = [
        "Debt_To_Income_Ratio",
        "Credit_Utilization",
        "Missed_Payments",
        "Late_Payment_Count",
        "Number_of_Defaults"
    ]

    if all(
        c in df.columns
        for c in risk_cols
    ):

        df["Risk_Indicator"] = (
            df["Debt_To_Income_Ratio"] * 35
            +
            (df["Credit_Utilization"] / 100) * 25
            +
            df["Missed_Payments"] * 4
            +
            df["Late_Payment_Count"] * 1.5
            +
            df["Number_of_Defaults"] * 12
        )

        df["Risk_Level"] = pd.cut(
            df["Risk_Indicator"],
            bins=[
                -np.inf,
                25,
                50,
                np.inf
            ],
            labels=[
                "Lower",
                "Moderate",
                "Higher"
            ]
        )

    return df


# ============================================================
# HELPER FUNCTIONS
# ============================================================
def currency(v):

    if pd.isna(v):
        return "₹0"

    v = float(v)

    if abs(v) >= 1e7:
        return f"₹{v/1e7:.2f} Cr"

    if abs(v) >= 1e5:
        return f"₹{v/1e5:.2f} L"

    return f"₹{v:,.0f}"


def style_fig(
    fig,
    height=420
):

    fig.update_layout(

        template="plotly_white",

        height=height,

        paper_bgcolor="rgba(0,0,0,0)",

        plot_bgcolor="#FFFFFF",

        font=dict(
            color=COLORS["text"]
        ),

        title_font=dict(
            color=COLORS["navy"],
            size=17
        ),

        legend_title_text="",

        margin=dict(
            l=20,
            r=20,
            t=55,
            b=25
        ),

        hoverlabel=dict(
            bgcolor="white",
            font_color=COLORS["text"]
        ),

        transition_duration=350
    )

    fig.update_xaxes(
        showgrid=True,
        gridcolor="#EEF2F7",
        zeroline=False
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor="#EEF2F7",
        zeroline=False
    )

    return fig


def show_chart(fig):

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "displayModeBar": True,
            "displaylogo": False,
            "scrollZoom": True,
            "responsive": True
        }
    )


def dropdown(
    label,
    column,
    data,
    all_label="All"
):

    if column not in data.columns:
        return all_label

    options = sorted(
        data[column]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    return st.sidebar.selectbox(
        label,
        [all_label] + options,
        index=0
    )


def apply_dropdown(
    data,
    column,
    value
):

    if (
        value != "All"
        and column in data.columns
    ):

        return data[
            data[column]
            .astype(str)
            == value
        ]

    return data


# ============================================================
# SIDEBAR
# ============================================================
st.sidebar.markdown(
    "## 💳 Banking Analytics"
)

st.sidebar.caption(
    "Interactive Credit Card Customer Intelligence"
)


# ============================================================
# LOGOUT
# ============================================================
st.sidebar.markdown("---")

st.sidebar.success(
    f"👋 Welcome, {st.session_state.username}"
)

if st.sidebar.button(
    "🚪 Logout",
    use_container_width=True
):

    st.session_state.logged_in = False
    st.session_state.username = ""

    st.rerun()


# ============================================================
# FILE UPLOAD
# ============================================================
uploaded_file = st.sidebar.file_uploader(
    "📁 Upload Credit Card Excel File",
    type=["xlsx", "xls"]
)


df = load_data(uploaded_file)


if df is None:

    st.error(
        "Excel file not found. Upload your "
        "credit-card dataset from the sidebar "
        "or keep the Excel file in the same "
        "folder as app.py."
    )

    st.stop()


# ============================================================
# RESET BUTTON
# ============================================================
if st.sidebar.button(
    "🔄 Reset All Filters",
    use_container_width=True
):

    for key in [
        "gender_filter",
        "employment_filter",
        "residential_filter",
        "kyc_filter",
        "fraud_filter",
        "age_group_filter",
        "risk_filter",
        "band_filter"
    ]:

        st.session_state.pop(
            key,
            None
        )

    st.rerun()


# ============================================================
# CUSTOMER FILTERS
# ============================================================
st.sidebar.markdown(
    '<div class="filter-title">'
    '🎯 Customer Filters'
    '</div>',
    unsafe_allow_html=True
)


gender = dropdown(
    "👤 Gender",
    "Gender",
    df
)

employment = dropdown(
    "💼 Employment Type",
    "Employment_Type",
    df
)

residential = dropdown(
    "🏠 Residential Status",
    "Residential_Status",
    df
)

kyc = dropdown(
    "🪪 KYC Status",
    "KYC_Status",
    df
)

fraud = dropdown(
    "🚨 Fraud Flag",
    "Fraud_Flag",
    df
)

age_group = dropdown(
    "🎂 Age Group",
    "Age_Group",
    df
)


# ============================================================
# AGE RANGE
# ============================================================
if "Age" in df.columns:

    age_range = st.sidebar.slider(
        "🎂 Age Range",
        int(df["Age"].min()),
        int(df["Age"].max()),
        (
            int(df["Age"].min()),
            int(df["Age"].max())
        )
    )

else:

    age_range = None


# ============================================================
# CREDIT SCORE
# ============================================================
if "Credit_Score" in df.columns:

    score_range = st.sidebar.slider(
        "⭐ Credit Score",
        int(df["Credit_Score"].min()),
        int(df["Credit_Score"].max()),
        (
            int(df["Credit_Score"].min()),
            int(df["Credit_Score"].max())
        )
    )

else:

    score_range = None


# ============================================================
# SPENDING
# ============================================================
if "Avg_Monthly_Spending" in df.columns:

    spending_range = st.sidebar.slider(
        "💰 Monthly Spending",
        float(df["Avg_Monthly_Spending"].min()),
        float(df["Avg_Monthly_Spending"].max()),
        (
            float(df["Avg_Monthly_Spending"].min()),
            float(df["Avg_Monthly_Spending"].max())
        )
    )

else:

    spending_range = None


# ============================================================
# RISK FILTERS
# ============================================================
st.sidebar.markdown(
    '<div class="filter-title">'
    '🛡️ Risk Filters'
    '</div>',
    unsafe_allow_html=True
)


risk_segment = st.sidebar.selectbox(
    "Risk Segment",
    [
        "All Customers",
        "High Risk Only",
        "Standard Risk Only"
    ]
)


risk_level_filter = dropdown(
    "Risk Level",
    "Risk_Level",
    df
)


credit_band_filter = dropdown(
    "Credit Band",
    "Credit_Band",
    df
)


# ============================================================
# UTILIZATION
# ============================================================
if "Credit_Utilization" in df.columns:

    utilization_max = st.sidebar.slider(
        "💳 Max Credit Utilization (%)",
        0,
        100,
        100
    )

else:

    utilization_max = 100


# ============================================================
# KYC / PAN
# ============================================================
require_kyc = st.sidebar.checkbox(
    "✅ KYC Complete Only",
    False
)

require_pan = st.sidebar.checkbox(
    "✅ PAN Verified Only",
    False
)


# ============================================================
# SIDEBAR NOTE
# ============================================================
st.sidebar.markdown("---")

st.sidebar.markdown(
    '<div class="sidebar-note">'
    '💡 <b>Tip:</b> Use one dropdown at a time '
    'to understand how each customer segment '
    'changes spending, financial health and risk.'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# APPLY FILTERS
# ============================================================
filtered = df.copy()


filtered = apply_dropdown(
    filtered,
    "Gender",
    gender
)

filtered = apply_dropdown(
    filtered,
    "Employment_Type",
    employment
)

filtered = apply_dropdown(
    filtered,
    "Residential_Status",
    residential
)

filtered = apply_dropdown(
    filtered,
    "KYC_Status",
    kyc
)

filtered = apply_dropdown(
    filtered,
    "Fraud_Flag",
    fraud
)

filtered = apply_dropdown(
    filtered,
    "Age_Group",
    age_group
)

filtered = apply_dropdown(
    filtered,
    "Risk_Level",
    risk_level_filter
)

filtered = apply_dropdown(
    filtered,
    "Credit_Band",
    credit_band_filter
)


# ============================================================
# AGE RANGE FILTER
# ============================================================
if (
    age_range
    and "Age" in filtered.columns
):

    filtered = filtered[
        filtered["Age"].between(
            *age_range
        )
    ]


# ============================================================
# CREDIT SCORE FILTER
# ============================================================
if (
    score_range
    and "Credit_Score" in filtered.columns
):

    filtered = filtered[
        filtered["Credit_Score"].between(
            *score_range
        )
    ]


# ============================================================
# SPENDING FILTER
# ============================================================
if (
    spending_range
    and "Avg_Monthly_Spending" in filtered.columns
):

    filtered = filtered[
        filtered["Avg_Monthly_Spending"].between(
            *spending_range
        )
    ]


# ============================================================
# RISK SEGMENT
# ============================================================
if (
    risk_segment == "High Risk Only"
    and "High_Risk_Flag" in filtered.columns
):

    filtered = filtered[
        filtered["High_Risk_Flag"]
        == "High Risk"
    ]

elif (
    risk_segment == "Standard Risk Only"
    and "High_Risk_Flag" in filtered.columns
):

    filtered = filtered[
        filtered["High_Risk_Flag"]
        == "Standard"
    ]


# ============================================================
# UTILIZATION FILTER
# ============================================================
if "Credit_Utilization" in filtered.columns:

    filtered = filtered[
        filtered["Credit_Utilization"]
        <= utilization_max
    ]


# ============================================================
# KYC FILTER
# ============================================================
if (
    require_kyc
    and "KYC_Status" in filtered.columns
):

    filtered = filtered[
        filtered["KYC_Status"]
        .astype(str)
        .str.lower()
        .isin(
            [
                "complete",
                "completed",
                "yes",
                "verified"
            ]
        )
    ]


# ============================================================
# PAN FILTER
# ============================================================
if (
    require_pan
    and "PAN_Verified" in filtered.columns
):

    filtered = filtered[
        filtered["PAN_Verified"]
        .astype(str)
        .str.lower()
        .isin(
            [
                "yes",
                "verified",
                "true"
            ]
        )
    ]


# ============================================================
# HEADER
# ============================================================
st.markdown(
    '<div class="dashboard-title">'
    '💳 Credit Card Banking Analytics'
    '</div>',
    unsafe_allow_html=True
)


st.markdown(
    '<div class="dashboard-subtitle">'
    'Customer spending • financial health • '
    'credit performance • default & risk intelligence'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# EMPTY FILTER RESULT
# ============================================================
if filtered.empty:

    st.warning(
        "No customers match the selected filters. "
        "Please widen the filters."
    )

    st.stop()


# ============================================================
# ACTIVE FILTER SUMMARY
# ============================================================
active_filters = []


for label, value in [

    ("Gender", gender),
    ("Employment", employment),
    ("Residential", residential),
    ("KYC", kyc),
    ("Fraud", fraud),
    ("Age Group", age_group),
    ("Risk Level", risk_level_filter),
    ("Credit Band", credit_band_filter)

]:

    if value != "All":

        active_filters.append(
            f"{label}: {value}"
        )


if active_filters:

    st.info(
        "🔎 Active filters: "
        + " | ".join(active_filters)
    )

else:

    st.caption(
        "🔎 Showing the complete customer portfolio."
    )


# ============================================================
# KPI ROW
# ============================================================
st.markdown(
    '<div class="section-header">'
    '📊 Executive Portfolio Overview'
    '</div>',
    unsafe_allow_html=True
)


total_customers = len(filtered)


avg_income = (
    filtered["Annual_Income"].mean()
    if "Annual_Income" in filtered
    else 0
)


avg_spending = (
    filtered["Avg_Monthly_Spending"].mean()
    if "Avg_Monthly_Spending" in filtered
    else 0
)


avg_score = (
    filtered["Credit_Score"].mean()
    if "Credit_Score" in filtered
    else 0
)


avg_util = (
    filtered["Credit_Utilization"].mean()
    if "Credit_Utilization" in filtered
    else 0
)


total_savings = (
    filtered["Savings_Balance"].sum()
    if "Savings_Balance" in filtered
    else 0
)


total_investment = (
    filtered["Investment_Value"].sum()
    if "Investment_Value" in filtered
    else 0
)


default_count = (
    filtered["default_payment_next_month"].sum()
    if "default_payment_next_month" in filtered
    else 0
)


default_rate = (
    default_count / total_customers * 100
    if total_customers
    else 0
)


high_risk_count = (

    (
        filtered["High_Risk_Flag"]
        == "High Risk"
    ).sum()

    if "High_Risk_Flag" in filtered

    else 0
)


k1, k2, k3, k4, k5, k6 = st.columns(6)


k1.metric(
    "👥 Customers",
    f"{total_customers:,}"
)


k2.metric(
    "💰 Avg Spending",
    currency(avg_spending)
)


k3.metric(
    "⭐ Avg Credit Score",
    f"{avg_score:,.0f}"
)


k4.metric(
    "📈 Avg Utilization",
    f"{avg_util:.1f}%"
)


k5.metric(
    "⚠️ Default Rate",
    f"{default_rate:.2f}%"
)


k6.metric(
    "🛡️ High Risk",
    f"{high_risk_count:,}"
)


st.caption(
    f"Showing {len(filtered):,} of "
    f"{len(df):,} customers after filters."
)


# ============================================================
# TABS
# ============================================================
tabs = st.tabs(
    [
        "🏠 Overview",
        "💳 Spending",
        "💰 Financial Health",
        "🛡️ Credit & Risk",
        "📋 Customer Explorer"
    ]
)


# ============================================================
# TAB 1 - OVERVIEW
# ============================================================
with tabs[0]:

    st.markdown(
        '<div class="section-header">'
        '🏦 Financial Position'
        '</div>',
        unsafe_allow_html=True
    )

    c1, c2 = st.columns(2)


    with c1:

        if all(
            c in filtered.columns
            for c in [
                "Annual_Income",
                "Savings_Balance"
            ]
        ):

            fig = px.scatter(
                filtered,
                x="Annual_Income",
                y="Savings_Balance",
                size=(
                    "Credit_Limit"
                    if "Credit_Limit"
                    in filtered
                    else None
                ),
                color=(
                    "Credit_Band"
                    if "Credit_Band"
                    in filtered
                    else None
                ),
                color_discrete_sequence=PALETTE,
                hover_name=(
                    "Customer_ID"
                    if "Customer_ID"
                    in filtered
                    else None
                ),
                hover_data=[
                    c
                    for c in [
                        "Credit_Score",
                        "Employment_Type"
                    ]
                    if c in filtered
                ]
            )

            fig.update_layout(
                title="Annual Income vs Savings Balance"
            )

            show_chart(
                style_fig(
                    fig,
                    430
                )
            )


    with c2:

        if all(
            c in filtered.columns
            for c in [
                "Annual_Income",
                "Investment_Value"
            ]
        ):

            fig = px.scatter(
                filtered,
                x="Annual_Income",
                y="Investment_Value",
                size=(
                    "Credit_Limit"
                    if "Credit_Limit"
                    in filtered
                    else None
                ),
                color=(
                    "Employment_Type"
                    if "Employment_Type"
                    in filtered
                    else None
                ),
                color_discrete_sequence=PALETTE,
                hover_name=(
                    "Customer_ID"
                    if "Customer_ID"
                    in filtered
                    else None
                )
            )

            fig.update_layout(
                title="Annual Income vs Investment Value"
            )

            show_chart(
                style_fig(
                    fig,
                    430
                )
            )


    st.markdown(
        '<div class="section-header">'
        '📌 Portfolio Insights'
        '</div>',
        unsafe_allow_html=True
    )


    col1, col2 = st.columns(2)


    with col1:

        st.markdown(
            f"""
            <div class="insight">
                <b>Income & savings:</b>
                Average annual income is
                <b>{currency(avg_income)}</b>
                and total savings are
                <b>{currency(total_savings)}</b>.
            </div>
            """,
            unsafe_allow_html=True
        )


        st.markdown(
            f"""
            <div class="insight">
                <b>Investment:</b>
                Total investments are
                <b>{currency(total_investment)}</b>.
            </div>
            """,
            unsafe_allow_html=True
        )


    with col2:

        st.markdown(
            f"""
            <div class="risk">
                <b>Risk watch:</b>
                <b>{high_risk_count:,}</b>
                customers are high risk
                under the dashboard rule.
            </div>
            """,
            unsafe_allow_html=True
        )


        st.markdown(
            f"""
            <div class="risk">
                <b>Default exposure:</b>
                Default rate is
                <b>{default_rate:.2f}%</b>.
            </div>
            """,
            unsafe_allow_html=True
        )


# ============================================================
# TAB 2 - SPENDING
# ============================================================
with tabs[1]:

    st.markdown(
        '<div class="section-header">'
        '📈 Customer Spending & Behaviour'
        '</div>',
        unsafe_allow_html=True
    )


    c1, c2, c3 = st.columns(3)


    dimension_label = c1.selectbox(
        "Compare Spending By",
        [
            "Age Group",
            "Gender",
            "Employment Type",
            "Occupation",
            "Residential Status",
            "KYC Status",
            "Fraud Flag"
        ]
    )


    chart_type = c2.selectbox(
        "Chart Type",
        [
            "Bar Chart",
            "Box Plot",
            "Violin Plot"
        ]
    )


    spending_metric = c3.selectbox(
        "Spending Metric",
        [
            "Avg_Monthly_Spending",
            "Avg_Monthly_Transactions"
        ]
    )


    dimension_map = {

        "Age Group":
            "Age_Group",

        "Gender":
            "Gender",

        "Employment Type":
            "Employment_Type",

        "Occupation":
            "Occupation",

        "Residential Status":
            "Residential_Status",

        "KYC Status":
            "KYC_Status",

        "Fraud Flag":
            "Fraud_Flag"
    }


    dim = dimension_map[
        dimension_label
    ]


    if (
        dim in filtered.columns
        and spending_metric
        in filtered.columns
    ):

        summary = (
            filtered
            .groupby(
                dim,
                observed=True
            )[spending_metric]
            .mean()
            .reset_index()
            .sort_values(
                spending_metric,
                ascending=False
            )
        )


        if chart_type == "Bar Chart":

            fig = px.bar(
                summary,
                x=dim,
                y=spending_metric,
                color=dim,
                color_discrete_sequence=PALETTE,
                text_auto=".2s"
            )

        elif chart_type == "Box Plot":

            fig = px.box(
                filtered,
                x=dim,
                y=spending_metric,
                color=dim,
                color_discrete_sequence=PALETTE,
                points="outliers"
            )

        else:

            fig = px.violin(
                filtered,
                x=dim,
                y=spending_metric,
                color=dim,
                color_discrete_sequence=PALETTE,
                box=True,
                points=False
            )


        fig.update_layout(
            title=(
                f"{spending_metric.replace('_', ' ')} "
                f"by {dimension_label}"
            ),
            showlegend=False
        )


        show_chart(
            style_fig(
                fig,
                450
            )
        )


    c1, c2 = st.columns(2)


    with c1:

        fig = px.histogram(
            filtered,
            x="Avg_Monthly_Spending",
            nbins=30,
            marginal="box",
            color_discrete_sequence=[
                COLORS["blue"]
            ]
        )

        fig.update_layout(
            title="💰 Monthly Spending Distribution"
        )

        show_chart(
            style_fig(
                fig,
                410
            )
        )


    with c2:

        if "Age_Group" in filtered.columns:

            age_spending = (
                filtered
                .groupby(
                    "Age_Group",
                    observed=True
                )
                .agg(
                    Average_Spending=(
                        "Avg_Monthly_Spending",
                        "mean"
                    ),
                    Customers=(
                        "Age_Group",
                        "size"
                    )
                )
                .reset_index()
            )


            fig = px.bar(
                age_spending,
                x="Age_Group",
                y="Average_Spending",
                color="Age_Group",
                color_discrete_sequence=PALETTE,
                text_auto=".2s",
                hover_data=["Customers"]
            )


            fig.update_layout(
                title="👥 Average Spending by Age Group",
                showlegend=False
            )


            show_chart(
                style_fig(
                    fig,
                    410
                )
            )


    st.markdown(
        '<div class="section-header">'
        '💵 Income vs Spending'
        '</div>',
        unsafe_allow_html=True
    )


    income_choice = st.radio(
        "Income Metric",
        [
            "Annual Income",
            "Monthly Income"
        ],
        horizontal=True
    )


    income_col = (
        "Annual_Income"
        if income_choice
        == "Annual Income"
        else "Monthly_Income"
    )


    if income_col in filtered.columns:

        fig = px.scatter(
            filtered,
            x=income_col,
            y="Avg_Monthly_Spending",
            color=(
                "Credit_Score"
                if "Credit_Score"
                in filtered
                else None
            ),
            size=(
                "Credit_Limit"
                if "Credit_Limit"
                in filtered
                else None
            ),
            color_continuous_scale=[
                "#DDEBFF",
                "#8DB7F7",
                "#557FD0"
            ],
            hover_name=(
                "Customer_ID"
                if "Customer_ID"
                in filtered
                else None
            )
        )


        fig.update_layout(
            title=(
                f"{income_choice} "
                "vs Monthly Spending"
            )
        )


        show_chart(
            style_fig(
                fig,
                470
            )
        )


# ============================================================
# TAB 3 - FINANCIAL HEALTH
# ============================================================
with tabs[2]:

    st.markdown(
        '<div class="section-header">'
        '💰 Financial Health & Behaviour'
        '</div>',
        unsafe_allow_html=True
    )


    f1, f2, f3, f4, f5 = st.columns(5)


    f1.metric(
        "💵 Avg EMI",
        currency(
            filtered["EMI_Per_Month"].mean()
        )
        if "EMI_Per_Month"
        in filtered
        else "N/A"
    )


    f2.metric(
        "📉 Avg DTI",
        (
            f'{filtered["Debt_To_Income_Ratio"].mean():.2f}'
        )
        if "Debt_To_Income_Ratio"
        in filtered
        else "N/A"
    )


    f3.metric(
        "🏦 Avg Savings",
        currency(
            filtered["Savings_Balance"].mean()
        )
        if "Savings_Balance"
        in filtered
        else "N/A"
    )


    f4.metric(
        "📈 Avg Investment",
        currency(
            filtered["Investment_Value"].mean()
        )
        if "Investment_Value"
        in filtered
        else "N/A"
    )


    f5.metric(
        "💳 Avg Credit Limit",
        currency(
            filtered["Credit_Limit"].mean()
        )
        if "Credit_Limit"
        in filtered
        else "N/A"
    )


    financial_metric = st.selectbox(
        "Choose Financial Metric for Comparison",
        [
            "Savings_Balance",
            "Investment_Value",
            "Avg_Monthly_Spending",
            "EMI_Per_Month"
        ]
    )


    c1, c2 = st.columns(2)


    with c1:

        if (
            "Annual_Income"
            in filtered.columns
            and financial_metric
            in filtered.columns
        ):

            fig = px.scatter(
                filtered,
                x="Annual_Income",
                y=financial_metric,
                color=(
                    "Employment_Type"
                    if "Employment_Type"
                    in filtered
                    else None
                ),
                color_discrete_sequence=PALETTE,
                hover_name=(
                    "Customer_ID"
                    if "Customer_ID"
                    in filtered
                    else None
                )
            )


            fig.update_layout(
                title=(
                    "Annual Income vs "
                    + financial_metric.replace(
                        "_",
                        " "
                    )
                )
            )


            show_chart(
                style_fig(
                    fig,
                    430
                )
            )


    with c2:

        if (
            "Occupation"
            in filtered.columns
            and financial_metric
            in filtered.columns
        ):

            occupation_metric = (

                filtered
                .groupby("Occupation")[
                    financial_metric
                ]
                .mean()
                .nlargest(10)
                .sort_values()
                .reset_index()
            )


            fig = px.bar(
                occupation_metric,
                x=financial_metric,
                y="Occupation",
                orientation="h",
                color=financial_metric,
                color_continuous_scale=[
                    "#E7F6F3",
                    "#63C7C5",
                    "#398F8C"
                ],
                text_auto=".2s"
            )


            fig.update_layout(
                title=(
                    "Top Occupations by "
                    + financial_metric.replace(
                        "_",
                        " "
                    )
                ),
                coloraxis_showscale=False
            )


            show_chart(
                style_fig(
                    fig,
                    430
                )
            )


    c1, c2 = st.columns(2)


    with c1:

        if all(
            c in filtered.columns
            for c in [
                "Avg_Monthly_Transactions",
                "Avg_Monthly_Spending"
            ]
        ):

            fig = px.scatter(
                filtered,
                x="Avg_Monthly_Transactions",
                y="Avg_Monthly_Spending",
                size=(
                    "Credit_Limit"
                    if "Credit_Limit"
                    in filtered
                    else None
                ),
                color=(
                    "Credit_Utilization"
                    if "Credit_Utilization"
                    in filtered
                    else None
                ),
                color_continuous_scale=[
                    "#E6F4FF",
                    "#8DB7F7",
                    "#557FD0"
                ],
                hover_name=(
                    "Customer_ID"
                    if "Customer_ID"
                    in filtered
                    else None
                )
            )


            fig.update_layout(
                title=(
                    "Transactions vs "
                    "Monthly Spending"
                )
            )


            show_chart(
                style_fig(
                    fig,
                    430
                )
            )


    with c2:

        if "EMI_Per_Month" in filtered.columns:

            fig = px.histogram(
                filtered,
                x="EMI_Per_Month",
                nbins=30,
                marginal="box",
                color_discrete_sequence=[
                    COLORS["purple"]
                ]
            )


            fig.update_layout(
                title="Monthly EMI Distribution"
            )


            show_chart(
                style_fig(
                    fig,
                    430
                )
            )


# ============================================================
# TAB 4 - CREDIT & RISK
# ============================================================
with tabs[3]:

    st.markdown(
        '<div class="section-header">'
        '🛡️ Credit Performance & Risk Intelligence'
        '</div>',
        unsafe_allow_html=True
    )


    r1, r2, r3, r4 = st.columns(4)


    higher = (
        (filtered["Risk_Level"] == "Higher").sum()
        if "Risk_Level"
        in filtered
        else 0
    )


    moderate = (
        (filtered["Risk_Level"] == "Moderate").sum()
        if "Risk_Level"
        in filtered
        else 0
    )


    defaults = (
        filtered["Number_of_Defaults"].sum()
        if "Number_of_Defaults"
        in filtered
        else 0
    )


    missed = (
        filtered["Missed_Payments"].sum()
        if "Missed_Payments"
        in filtered
        else 0
    )


    r1.metric(
        "🔴 Higher Risk",
        f"{higher:,}"
    )


    r2.metric(
        "🟡 Moderate Risk",
        f"{moderate:,}"
    )


    r3.metric(
        "⚠️ Defaults",
        f"{int(defaults):,}"
    )


    r4.metric(
        "⏰ Missed Payments",
        f"{int(missed):,}"
    )


    c1, c2 = st.columns(2)


    with c1:

        if (
            "default_payment_next_month"
            in filtered.columns
        ):

            counts = (
                filtered[
                    "default_payment_next_month"
                ]
                .value_counts(
                    normalize=True
                )
                .reindex(
                    [0, 1],
                    fill_value=0
                )
                .reset_index()
            )


            counts.columns = [
                "Status",
                "Percentage"
            ]


            counts["Percentage"] *= 100


            counts["Status"] = (
                counts["Status"]
                .map(
                    {
                        0: "Non-Defaulters",
                        1: "Defaulters"
                    }
                )
            )


            fig = px.bar(
                counts,
                x="Status",
                y="Percentage",
                color="Status",
                color_discrete_map={
                    "Non-Defaulters":
                        "#A9D8EA",
                    "Defaulters":
                        "#E59A9A"
                },
                text=counts[
                    "Percentage"
                ].map(
                    lambda x:
                    f"{x:.2f}%"
                )
            )


            fig.update_layout(
                title="Default Class Distribution",
                showlegend=False
            )


            show_chart(
                style_fig(
                    fig,
                    390
                )
            )


    with c2:

        if (
            "Age_Group"
            in filtered.columns
            and "default_payment_next_month"
            in filtered.columns
        ):

            risk_age = (

                filtered
                .groupby(
                    "Age_Group",
                    observed=False
                )[
                    "default_payment_next_month"
                ]
                .mean()
                .reset_index()
            )


            risk_age[
                "Default Rate (%)"
            ] = (
                risk_age[
                    "default_payment_next_month"
                ] * 100
            )


            fig = px.bar(
                risk_age,
                x="Age_Group",
                y="Default Rate (%)",
                color="Age_Group",
                color_discrete_sequence=PALETTE,
                text=risk_age[
                    "Default Rate (%)"
                ].map(
                    lambda x:
                    f"{x:.2f}%"
                )
            )


            fig.update_layout(
                title="Default Rate by Age Group",
                showlegend=False
            )


            show_chart(
                style_fig(
                    fig,
                    390
                )
            )


    c1, c2 = st.columns(2)


    with c1:

        if (
            "Occupation"
            in filtered.columns
            and "default_payment_next_month"
            in filtered.columns
        ):

            occ = (

                filtered
                .groupby(
                    "Occupation"
                )[
                    "default_payment_next_month"
                ]
                .mean()
                .mul(100)
                .sort_values()
                .reset_index()
            )


            occ.columns = [
                "Occupation",
                "Default Rate (%)"
            ]


            fig = px.bar(
                occ,
                y="Occupation",
                x="Default Rate (%)",
                orientation="h",
                color="Default Rate (%)",
                color_continuous_scale=[
                    "#E9F0FF",
                    "#B3A2E8",
                    "#9A84EA"
                ],
                text=occ[
                    "Default Rate (%)"
                ].map(
                    lambda x:
                    f"{x:.2f}%"
                )
            )


            fig.update_layout(
                title="Default Rate by Occupation",
                coloraxis_showscale=False
            )


            show_chart(
                style_fig(
                    fig,
                    430
                )
            )


    with c2:

        if "Credit_Utilization" in filtered.columns:

            temp = filtered.copy()


            if (
                "default_payment_next_month"
                in temp.columns
            ):

                temp["Status_Label"] = (
                    temp[
                        "default_payment_next_month"
                    ]
                    .map(
                        {
                            0: "Non-Defaulters",
                            1: "Defaulters"
                        }
                    )
                )


                fig = px.box(
                    temp,
                    x="Status_Label",
                    y="Credit_Utilization",
                    color="Status_Label",
                    color_discrete_map={
                        "Non-Defaulters":
                            "#A9D8EA",
                        "Defaulters":
                            "#E59A9A"
                    },
                    points="outliers"
                )


                fig.update_layout(
                    title=(
                        "Credit Utilization "
                        "by Default Status"
                    ),
                    showlegend=False
                )

            else:

                fig = px.histogram(
                    temp,
                    x="Credit_Utilization",
                    nbins=30,
                    marginal="box",
                    color_discrete_sequence=[
                        COLORS["purple"]
                    ]
                )


                fig.update_layout(
                    title=(
                        "Credit Utilization Distribution"
                    )
                )


            fig.add_vline(
                x=75,
                line_dash="dash",
                line_color="#D88989",
                annotation_text="75% reference"
            )


            show_chart(
                style_fig(
                    fig,
                    430
                )
            )


    # ========================================================
    # INTERACTIVE RISK ANALYSIS
    # ========================================================
    st.markdown(
        '<div class="section-header">'
        '🎛️ Interactive Risk Analysis'
        '</div>',
        unsafe_allow_html=True
    )


    risk_metric = st.selectbox(
        "Choose Risk Metric",
        [
            "Credit Score",
            "Credit Utilization",
            "Debt To Income Ratio",
            "Missed Payments",
            "Late Payment Count"
        ]
    )


    risk_map = {

        "Credit Score":
            "Credit_Score",

        "Credit Utilization":
            "Credit_Utilization",

        "Debt To Income Ratio":
            "Debt_To_Income_Ratio",

        "Missed Payments":
            "Missed_Payments",

        "Late Payment Count":
            "Late_Payment_Count"
    }


    selected_risk_col = risk_map[
        risk_metric
    ]


    if (
        selected_risk_col
        in filtered.columns
        and "Risk_Level"
        in filtered.columns
    ):

        risk_summary = (

            filtered
            .groupby(
                "Risk_Level",
                observed=False
            )[selected_risk_col]
            .mean()
            .reindex(
                [
                    "Lower",
                    "Moderate",
                    "Higher"
                ]
            )
            .reset_index()
        )


        fig = px.bar(
            risk_summary,
            x="Risk_Level",
            y=selected_risk_col,
            color="Risk_Level",
            color_discrete_map=RISK_COLORS,
            text_auto=".2f"
        )


        fig.update_layout(
            title=(
                f"Average {risk_metric} "
                "by Risk Level"
            ),
            showlegend=False
        )


        show_chart(
            style_fig(
                fig,
                420
            )
        )


    if "Risk_Level" in filtered.columns:

        risk_data = (

            filtered["Risk_Level"]
            .value_counts()
            .reindex(
                [
                    "Lower",
                    "Moderate",
                    "Higher"
                ],
                fill_value=0
            )
            .reset_index()
        )


        risk_data.columns = [
            "Risk_Level",
            "Customers"
        ]


        fig = px.bar(
            risk_data,
            x="Risk_Level",
            y="Customers",
            color="Risk_Level",
            color_discrete_map=RISK_COLORS,
            text_auto=True
        )


        fig.update_layout(
            title="Customer Risk Distribution",
            showlegend=False
        )


        show_chart(
            style_fig(
                fig,
                410
            )
        )


        st.caption(
            "Risk Indicator is a custom analytical "
            "measure using DTI, credit utilization, "
            "missed payments, late payments and "
            "defaults. It is not an official bank "
            "credit-risk score."
        )


# ============================================================
# TAB 5 - CUSTOMER EXPLORER
# ============================================================
with tabs[4]:

    st.markdown(
        '<div class="section-header">'
        '🔎 Interactive Customer Explorer'
        '</div>',
        unsafe_allow_html=True
    )


    c1, c2 = st.columns([2, 1])


    with c1:

        search = st.text_input(
            "🔍 Search Customer ID",
            placeholder="Type Customer ID..."
        )


    with c2:

        rows_to_show = st.selectbox(
            "Rows to Display",
            [
                10,
                25,
                50,
                100,
                250,
                500
            ]
        )


    explorer = filtered.copy()


    if (
        search
        and "Customer_ID"
        in explorer.columns
    ):

        explorer = explorer[
            explorer[
                "Customer_ID"
            ]
            .astype(str)
            .str.contains(
                search,
                case=False,
                na=False
            )
        ]


    available_columns = [

        c for c in [

            "Customer_ID",
            "Age",
            "Gender",
            "Occupation",
            "Employment_Type",
            "Annual_Income",
            "Credit_Score",
            "Credit_Limit",
            "Credit_Utilization",
            "Avg_Monthly_Spending",
            "Avg_Monthly_Transactions",
            "EMI_Per_Month",
            "Debt_To_Income_Ratio",
            "Savings_Balance",
            "Investment_Value",
            "Missed_Payments",
            "Late_Payment_Count",
            "Number_of_Defaults",
            "Risk_Level",
            "High_Risk_Flag"

        ]

        if c in explorer.columns
    ]


    selected_columns = st.multiselect(
        "Select columns to display",
        available_columns,
        default=available_columns[:10]
    )


    st.write(
        f"**{len(explorer):,} customers found**"
    )


    if selected_columns:

        st.dataframe(
            explorer[
                selected_columns
            ].head(rows_to_show),
            use_container_width=True,
            height=520
        )


    csv = explorer.to_csv(
        index=False
    ).encode("utf-8")


    st.download_button(
        "⬇️ Download Filtered Customer Data",
        data=csv,
        file_name=(
            "filtered_credit_card_customers.csv"
        ),
        mime="text/csv",
        use_container_width=True
    )


# ============================================================
# FOOTER
# ============================================================
st.sidebar.markdown("---")

st.sidebar.caption(
    "Built with Streamlit • Pandas • Plotly • NumPy"
)

st.sidebar.caption(
    "💙 Professional Light Banking Analytics Dashboard"
)
