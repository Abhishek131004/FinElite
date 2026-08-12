import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Advanced Credit Card Banking Dashboard",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# COLOUR PALETTES
# ============================================================

NAVY = "#172554"
BLUE = "#2563EB"
CYAN = "#0891B2"
PURPLE = "#7C3AED"
GREEN = "#059669"
ORANGE = "#EA580C"
RED = "#DC2626"
PINK = "#DB2777"

SPENDING_PALETTE = [
    "#2563EB",
    "#7C3AED",
    "#0891B2",
    "#059669",
    "#EA580C",
    "#DB2777"
]

FINANCIAL_PALETTE = [
    "#059669",
    "#0891B2",
    "#2563EB",
    "#7C3AED",
    "#EA580C"
]


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

.stApp {
    background-color: #F5F7FB;
}

.block-container {
    padding-top: 1.2rem;
    padding-bottom: 2rem;
    max-width: 1500px;
}

.dashboard-title {
    font-size: 2.4rem;
    font-weight: 800;
    color: #172554;
}

.dashboard-subtitle {
    color: #64748B;
    font-size: 1rem;
    margin-bottom: 18px;
}

.section-header {
    background: linear-gradient(
        90deg,
        #172554,
        #2563EB
    );

    color: white;
    padding: 10px 16px;
    border-radius: 10px;
    margin: 15px 0 12px 0;

    font-size: 1.05rem;
    font-weight: 700;
}

[data-testid="stMetric"] {

    background-color: white;

    border: 1px solid #E2E8F0;

    border-radius: 14px;

    padding: 14px;

    box-shadow:
        0 3px 12px rgba(15,23,42,0.06);
}

[data-testid="stMetricLabel"] {
    color: #475569;
}

[data-testid="stMetricValue"] {
    color: #172554;
}

[data-testid="stSidebar"] {
    background-color: #EEF2FF;
}

div.stButton > button {

    width: 100%;

    border-radius: 9px;

    border: 1px solid #2563EB;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data(uploaded_file=None):

    if uploaded_file is not None:

        data = pd.read_excel(
            uploaded_file
        )

    else:

        data = pd.read_excel(
            "Credir_Card_Bank(4).xlsx"
        )


    # --------------------------------------------------------
    # AGE GROUP
    # --------------------------------------------------------

    def make_age_group(age):

        if age < 20:
            return "Teen"

        elif age < 30:
            return "Young Adult"

        elif age < 50:
            return "Adult"

        elif age < 60:
            return "Middle Aged"

        else:
            return "Senior Citizen"


    data["Age_Group"] = data["Age"].apply(
        make_age_group
    )


    # --------------------------------------------------------
    # EMI GROUP
    # --------------------------------------------------------

    data["EMI_Group"] = pd.cut(
        data["EMI_Per_Month"],
        bins=5,

        labels=[
            "Very Low EMI",
            "Low EMI",
            "Medium EMI",
            "High EMI",
            "Very High EMI"
        ]
    )


    # --------------------------------------------------------
    # DTI GROUP
    # --------------------------------------------------------

    data["DTI_Group"] = pd.cut(
        data["Debt_To_Income_Ratio"],
        bins=5,

        labels=[
            "Very Low DTI",
            "Low DTI",
            "Medium DTI",
            "High DTI",
            "Very High DTI"
        ]
    )


    # --------------------------------------------------------
    # SAVINGS GROUP
    # --------------------------------------------------------

    data["Savings_Group"] = pd.cut(
        data["Savings_Balance"],
        bins=5,

        labels=[
            "Very Low Savings",
            "Low Savings",
            "Medium Savings",
            "High Savings",
            "Very High Savings"
        ]
    )


    # --------------------------------------------------------
    # INVESTMENT GROUP
    # --------------------------------------------------------

    data["Investment_Group"] = pd.cut(
        data["Investment_Value"],
        bins=5,

        labels=[
            "Very Low Investment",
            "Low Investment",
            "Medium Investment",
            "High Investment",
            "Very High Investment"
        ]
    )


    return data


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.markdown(
    "## 💳 Banking Analytics"
)

st.sidebar.caption(
    "Interactive Dashboard Controls"
)


uploaded_file = st.sidebar.file_uploader(
    "📁 Upload Excel File",
    type=["xlsx", "xls"]
)


try:

    df = load_data(
        uploaded_file
    )

except FileNotFoundError:

    st.error(
        "Excel file not found. "
        "Keep 'Credir_Card_Bank(4).xlsx' "
        "in the same folder as app.py "
        "or upload it from the sidebar."
    )

    st.stop()


except Exception as e:

    st.error(
        f"Unable to load Excel file: {e}"
    )

    st.stop()


# ============================================================
# FILTER FUNCTION
# ============================================================

def add_multiselect(
    label,
    column
):

    values = sorted(
        df[column]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    return st.sidebar.multiselect(
        label,
        values,
        default=values
    )


# ============================================================
# FILTERS
# ============================================================

st.sidebar.markdown("---")

st.sidebar.markdown(
    "### 🎯 Customer Filters"
)


employment_filter = add_multiselect(
    "Employment Type",
    "Employment_Type"
)


gender_filter = add_multiselect(
    "Gender",
    "Gender"
)


age_group_filter = add_multiselect(
    "Age Group",
    "Age_Group"
)


residential_filter = add_multiselect(
    "Residential Status",
    "Residential_Status"
)


kyc_filter = add_multiselect(
    "KYC Status",
    "KYC_Status"
)


fraud_filter = add_multiselect(
    "Fraud Flag",
    "Fraud_Flag"
)


# ============================================================
# AGE SLIDER
# ============================================================

min_age = int(
    df["Age"].min()
)

max_age = int(
    df["Age"].max()
)


age_range = st.sidebar.slider(

    "Age Range",

    min_value=min_age,

    max_value=max_age,

    value=(
        min_age,
        max_age
    )
)


# ============================================================
# SPENDING SLIDER
# ============================================================

min_spending = float(
    df["Avg_Monthly_Spending"].min()
)

max_spending = float(
    df["Avg_Monthly_Spending"].max()
)


spending_range = st.sidebar.slider(

    "Monthly Spending Range",

    min_value=min_spending,

    max_value=max_spending,

    value=(
        min_spending,
        max_spending
    )
)


# ============================================================
# CREDIT SCORE SLIDER
# ============================================================

min_score = int(
    df["Credit_Score"].min()
)

max_score = int(
    df["Credit_Score"].max()
)


credit_score_range = st.sidebar.slider(

    "Credit Score Range",

    min_value=min_score,

    max_value=max_score,

    value=(
        min_score,
        max_score
    )
)


# ============================================================
# RESET
# ============================================================

st.sidebar.markdown("---")


if st.sidebar.button(
    "🔄 Reset All Filters"
):

    st.rerun()


# ============================================================
# APPLY FILTERS
# ============================================================

filtered_df = df[

    df["Employment_Type"]
    .astype(str)
    .isin(employment_filter)

    &

    df["Gender"]
    .astype(str)
    .isin(gender_filter)

    &

    df["Age_Group"]
    .astype(str)
    .isin(age_group_filter)

    &

    df["Residential_Status"]
    .astype(str)
    .isin(residential_filter)

    &

    df["KYC_Status"]
    .astype(str)
    .isin(kyc_filter)

    &

    df["Fraud_Flag"]
    .astype(str)
    .isin(fraud_filter)

    &

    df["Age"].between(
        age_range[0],
        age_range[1]
    )

    &

    df["Avg_Monthly_Spending"].between(
        spending_range[0],
        spending_range[1]
    )

    &

    df["Credit_Score"].between(
        credit_score_range[0],
        credit_score_range[1]
    )

].copy()


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="dashboard-title">'
    '💳 Advanced Credit Card Banking Analytics'
    '</div>',
    unsafe_allow_html=True
)


st.markdown(
    '<div class="dashboard-subtitle">'
    'Customer spending • transactions • credit health • financial behaviour'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# EMPTY DATA CHECK
# ============================================================

if filtered_df.empty:

    st.warning(
        "⚠️ No customers match the selected filters."
    )

    st.stop()


# ============================================================
# CURRENCY FORMAT
# ============================================================

def currency(value):

    if value >= 1e7:

        return (
            f"₹{value / 1e7:.2f} Cr"
        )

    elif value >= 1e5:

        return (
            f"₹{value / 1e5:.2f} L"
        )

    else:

        return (
            f"₹{value:,.0f}"
        )


# ============================================================
# EXECUTIVE OVERVIEW
# ============================================================

st.markdown(
    '<div class="section-header">'
    '📊 Executive Overview'
    '</div>',
    unsafe_allow_html=True
)


k1, k2, k3, k4, k5, k6 = st.columns(6)


k1.metric(
    "👥 Customers",
    f"{len(filtered_df):,}"
)


k2.metric(
    "💰 Avg Spending",
    currency(
        filtered_df[
            "Avg_Monthly_Spending"
        ].mean()
    )
)


k3.metric(
    "🔄 Avg Transactions",
    f"{filtered_df['Avg_Monthly_Transactions'].mean():,.0f}"
)


k4.metric(
    "⭐ Avg Credit Score",
    f"{filtered_df['Credit_Score'].mean():,.0f}"
)


k5.metric(
    "💳 Avg Utilization",
    f"{filtered_df['Credit_Utilization'].mean():.1f}%"
)


k6.metric(
    "🏦 Credit Limit",
    currency(
        filtered_df[
            "Credit_Limit"
        ].sum()
    )
)


# ============================================================
# TWO PAGES
# ============================================================

page1, page2 = st.tabs([

    "📈 PAGE 1 — CUSTOMER & SPENDING",

    "💰 PAGE 2 — FINANCIAL ANALYSIS"

])


# ============================================================
# PAGE 1
# ============================================================

with page1:

    st.markdown(
        '<div class="section-header">'
        '📈 Customer Spending & Behaviour'
        '</div>',
        unsafe_allow_html=True
    )


    # ========================================================
    # DYNAMIC SPENDING ANALYSIS
    # ========================================================

    c1, c2 = st.columns(2)


    with c1:

        analysis_dimension = st.selectbox(

            "📊 Compare Spending By",

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


    with c2:

        chart_type = st.selectbox(

            "📈 Select Chart Type",

            [
                "Bar Chart",
                "Box Plot",
                "Violin Plot"
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


    selected_dimension = (
        dimension_map[
            analysis_dimension
        ]
    )


    # ========================================================
    # SUMMARY
    # ========================================================

    spending_summary = (

        filtered_df

        .groupby(
            selected_dimension,
            observed=True
        )

        .agg(

            Average_Spending=(
                "Avg_Monthly_Spending",
                "mean"
            ),

            Average_Transactions=(
                "Avg_Monthly_Transactions",
                "mean"
            ),

            Customers=(
                "Customer_ID",
                "count"
            )

        )

        .reset_index()

    )


    # ========================================================
    # DYNAMIC CHART
    # ========================================================

    if chart_type == "Bar Chart":

        fig = px.bar(

            spending_summary,

            x=selected_dimension,

            y="Average_Spending",

            color=selected_dimension,

            color_discrete_sequence=
            SPENDING_PALETTE,

            hover_data=[
                "Customers",
                "Average_Transactions"
            ],

            title=
            f"Average Monthly Spending by "
            f"{analysis_dimension}"

        )


    elif chart_type == "Box Plot":

        fig = px.box(

            filtered_df,

            x=selected_dimension,

            y="Avg_Monthly_Spending",

            color=selected_dimension,

            color_discrete_sequence=
            SPENDING_PALETTE,

            points="outliers",

            title=
            f"Spending Distribution by "
            f"{analysis_dimension}"

        )


    else:

        fig = px.violin(

            filtered_df,

            x=selected_dimension,

            y="Avg_Monthly_Spending",

            color=selected_dimension,

            color_discrete_sequence=
            SPENDING_PALETTE,

            box=True,

            points=False,

            title=
            f"Spending Pattern by "
            f"{analysis_dimension}"

        )


    fig.update_layout(

        height=450,

        template="plotly_white",

        showlegend=False,

        hovermode="x unified"

    )


    st.plotly_chart(

        fig,

        use_container_width=True

    )


    # ========================================================
    # SPENDING DISTRIBUTION
    # ========================================================

    c1, c2 = st.columns(2)


    with c1:

        fig = px.histogram(

            filtered_df,

            x="Avg_Monthly_Spending",

            nbins=30,

            marginal="box",

            color_discrete_sequence=[
                BLUE
            ],

            title=
            "💰 Monthly Spending Distribution",

            labels={
                "Avg_Monthly_Spending":
                "Monthly Spending (₹)"
            }

        )


        fig.update_layout(

            height=420,

            template="plotly_white"

        )


        st.plotly_chart(

            fig,

            use_container_width=True

        )


    # ========================================================
    # AGE GROUP
    # ========================================================

    with c2:

        age_spending = (

            filtered_df

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
                    "Customer_ID",
                    "count"
                )

            )

            .reset_index()

        )


        fig = px.bar(

            age_spending,

            x="Age_Group",

            y="Average_Spending",

            color="Average_Spending",

            color_continuous_scale=[

                "#DBEAFE",

                "#2563EB",

                "#172554"

            ],

            hover_data=[
                "Customers"
            ],

            title=
            "👥 Average Spending by Age Group"

        )


        fig.update_layout(

            height=420,

            template="plotly_white",

            coloraxis_showscale=False

        )


        st.plotly_chart(

            fig,

            use_container_width=True

        )


    # ========================================================
    # INCOME VS SPENDING
    # ========================================================

    st.markdown(
        '<div class="section-header">'
        '💵 Income & Spending Relationship'
        '</div>',
        unsafe_allow_html=True
    )


    income_metric = st.selectbox(

        "Select Income Metric",

        [
            "Annual Income",
            "Monthly Income"
        ]

    )


    income_column = (

        "Annual_Income"

        if income_metric ==
        "Annual Income"

        else

        "Monthly_Income"

    )


    fig = px.scatter(

        filtered_df,

        x=income_column,

        y="Avg_Monthly_Spending",

        color="Credit_Score",

        size="Credit_Limit",

        color_continuous_scale=[

            "#FEF3C7",

            "#F97316",

            "#DC2626"

        ],

        hover_name="Customer_ID",

        hover_data=[

            "Age",

            "Gender",

            "Occupation",

            "Employment_Type",

            "Avg_Monthly_Transactions"

        ],

        title=
        f"{income_metric} vs Monthly Spending"

    )


    fig.update_layout(

        height=500,

        template="plotly_white"

    )


    st.plotly_chart(

        fig,

        use_container_width=True

    )


    # ========================================================
    # TRANSACTIONS + TOP CUSTOMERS
    # ========================================================

    c1, c2 = st.columns(2)


    with c1:

        transaction_data = (

            filtered_df

            .groupby(
                "Employment_Type"
            )

            ["Avg_Monthly_Transactions"]

            .mean()

            .reset_index()

        )


        fig = px.bar(

            transaction_data,

            x="Employment_Type",

            y="Avg_Monthly_Transactions",

            color="Employment_Type",

            color_discrete_sequence=[

                "#0891B2",

                "#2563EB",

                "#7C3AED",

                "#059669"

            ],

            title=
            "🔄 Transactions by Employment Type"

        )


        fig.update_layout(

            height=400,

            template="plotly_white",

            showlegend=False

        )


        st.plotly_chart(

            fig,

            use_container_width=True

        )


    with c2:

        top_customers = (

            filtered_df

            .nlargest(
                10,
                "Avg_Monthly_Spending"
            )

            .sort_values(
                "Avg_Monthly_Spending"
            )

        )


        fig = px.bar(

            top_customers,

            x="Avg_Monthly_Spending",

            y="Customer_ID",

            orientation="h",

            color=
            "Avg_Monthly_Spending",

            color_continuous_scale=[

                "#FBCFE8",

                "#DB2777",

                "#831843"

            ],

            title=
            "🔥 Top 10 Spending Customers"

        )


        fig.update_layout(

            height=400,

            template="plotly_white",

            coloraxis_showscale=False

        )


        st.plotly_chart(

            fig,

            use_container_width=True

        )


# ============================================================
# PAGE 2
# ============================================================

with page2:

    st.markdown(
        '<div class="section-header">'
        '💰 Financial Health & Credit Analysis'
        '</div>',
        unsafe_allow_html=True
    )


    # ========================================================
    # FINANCIAL KPI
    # ========================================================

    f1, f2, f3, f4, f5 = st.columns(5)


    f1.metric(

        "💵 Avg EMI",

        currency(
            filtered_df[
                "EMI_Per_Month"
            ].mean()
        )

    )


    f2.metric(

        "📉 Avg DTI",

        f"{filtered_df['Debt_To_Income_Ratio'].mean():.2f}"

    )


    f3.metric(

        "🏦 Avg Savings",

        currency(
            filtered_df[
                "Savings_Balance"
            ].mean()
        )

    )


    f4.metric(

        "📈 Avg Investment",

        currency(
            filtered_df[
                "Investment_Value"
            ].mean()
        )

    )


    f5.metric(

        "💳 Avg Credit Limit",

        currency(
            filtered_df[
                "Credit_Limit"
            ].mean()
        )

    )


    # ========================================================
    # FINANCIAL SELECTOR
    # ========================================================

    st.markdown(
        '<div class="section-header">'
        '🔍 Interactive Financial Analysis'
        '</div>',
        unsafe_allow_html=True
    )


    financial_dimension = st.selectbox(

        "Choose Financial Factor",

        [
            "EMI",
            "Debt-to-Income Ratio",
            "Savings",
            "Investment",
            "Credit Utilization"
        ]

    )


    financial_map = {

        "EMI": (
            "EMI_Per_Month",
            "EMI_Group"
        ),

        "Debt-to-Income Ratio": (
            "Debt_To_Income_Ratio",
            "DTI_Group"
        ),

        "Savings": (
            "Savings_Balance",
            "Savings_Group"
        ),

        "Investment": (
            "Investment_Value",
            "Investment_Group"
        ),

        "Credit Utilization": (
            "Credit_Utilization",
            None
        )

    }


    numeric_column, group_column = (
        financial_map[
            financial_dimension
        ]
    )


    # ========================================================
    # FINANCIAL CHART
    # ========================================================

    if group_column is not None:

        financial_data = (

            filtered_df

            .groupby(
                group_column,
                observed=True
            )

            .agg(

                Average_Spending=(
                    "Avg_Monthly_Spending",
                    "mean"
                ),

                Customers=(
                    "Customer_ID",
                    "count"
                ),

                Average_Credit_Score=(
                    "Credit_Score",
                    "mean"
                )

            )

            .reset_index()

        )


        fig = px.bar(

            financial_data,

            x=group_column,

            y="Average_Spending",

            color=group_column,

            color_discrete_sequence=
            FINANCIAL_PALETTE,

            hover_data=[

                "Customers",

                "Average_Credit_Score"

            ],

            title=
            f"Spending Behaviour by "
            f"{financial_dimension}"

        )


    else:

        fig = px.histogram(

            filtered_df,

            x=numeric_column,

            nbins=25,

            marginal="box",

            color_discrete_sequence=[
                PURPLE
            ],

            title=
            "Credit Utilization Distribution"

        )


    fig.update_layout(

        height=450,

        template="plotly_white",

        showlegend=False

    )


    st.plotly_chart(

        fig,

        use_container_width=True

    )


    # ========================================================
    # CREDIT ANALYSIS
    # ========================================================

    c1, c2 = st.columns(2)


    with c1:

        fig = px.scatter(

            filtered_df,

            x="Credit_Limit",

            y="Credit_Utilization",

            size="Avg_Monthly_Spending",

            color="Credit_Score",

            color_continuous_scale=[

                "#DCFCE7",

                "#059669",

                "#064E3B"

            ],

            hover_name="Customer_ID",

            hover_data=[

                "Age",

                "Employment_Type",

                "Avg_Monthly_Spending",

                "Avg_Monthly_Transactions"

            ],

            title=
            "💳 Credit Limit vs Credit Utilization"

        )


        fig.update_layout(

            height=470,

            template="plotly_white"

        )


        st.plotly_chart(

            fig,

            use_container_width=True

        )


    # ========================================================
    # CREDIT SCORE
    # ========================================================

    with c2:

        temp = filtered_df.copy()


        temp["Credit_Band"] = pd.cut(

            temp["Credit_Score"],

            bins=[
                0,
                580,
                670,
                740,
                800,
                900
            ],

            labels=[
                "Poor",
                "Fair",
                "Good",
                "Very Good",
                "Excellent"
            ]

        )


        credit_score_data = (

            temp

            .groupby(
                "Credit_Band",
                observed=True
            )

            .agg(

                Customers=(
                    "Customer_ID",
                    "count"
                ),

                Avg_Spending=(
                    "Avg_Monthly_Spending",
                    "mean"
                ),

                Avg_Utilization=(
                    "Credit_Utilization",
                    "mean"
                )

            )

            .reset_index()

        )


        fig = px.bar(

            credit_score_data,

            x="Credit_Band",

            y="Customers",

            color="Avg_Utilization",

            color_continuous_scale=[

                "#DCFCE7",

                "#FACC15",

                "#F97316",

                "#DC2626"

            ],

            hover_data=[

                "Avg_Spending",

                "Avg_Utilization"

            ],

            title=
            "⭐ Credit Score Distribution"

        )


        fig.update_layout(

            height=470,

            template="plotly_white"

        )


        st.plotly_chart(

            fig,

            use_container_width=True

        )


    # ========================================================
    # SAVINGS VS INVESTMENT
    # ========================================================

    st.markdown(
        '<div class="section-header">'
        '📊 Savings, Investment & Financial Strength'
        '</div>',
        unsafe_allow_html=True
    )


    fig = px.scatter(

        filtered_df,

        x="Savings_Balance",

        y="Investment_Value",

        size="Annual_Income",

        color="Debt_To_Income_Ratio",

        color_continuous_scale=[

            "#DBEAFE",

            "#7C3AED",

            "#4C1D95"

        ],

        hover_name="Customer_ID",

        hover_data=[

            "Age",

            "Credit_Score",

            "EMI_Per_Month",

            "Credit_Limit"

        ],

        title=
        "Savings Balance vs Investment Value"

    )


    fig.update_layout(

        height=500,

        template="plotly_white"

    )


    st.plotly_chart(

        fig,

        use_container_width=True

    )


    # ========================================================
    # FINANCIAL COMPARISON
    # ========================================================

    c1, c2 = st.columns(2)


    with c1:

        financial_comparison = pd.DataFrame({

            "Metric": [

                "Monthly Income",

                "EMI",

                "Savings",

                "Investment",

                "Monthly Spending"

            ],

            "Value": [

                filtered_df[
                    "Monthly_Income"
                ].mean(),

                filtered_df[
                    "EMI_Per_Month"
                ].mean(),

                filtered_df[
                    "Savings_Balance"
                ].mean(),

                filtered_df[
                    "Investment_Value"
                ].mean(),

                filtered_df[
                    "Avg_Monthly_Spending"
                ].mean()

            ]

        })


        fig = px.bar(

            financial_comparison,

            x="Metric",

            y="Value",

            color="Metric",

            color_discrete_sequence=[

                "#2563EB",

                "#DC2626",

                "#059669",

                "#7C3AED",

                "#EA580C"

            ],

            title=
            "💰 Financial Metric Comparison"

        )


        fig.update_layout(

            height=450,

            template="plotly_white",

            showlegend=False

        )


        st.plotly_chart(

            fig,

            use_container_width=True

        )


    # ========================================================
    # EMPLOYMENT FINANCIAL ANALYSIS
    # ========================================================

    with c2:

        employment_financial = (

            filtered_df

            .groupby(
                "Employment_Type"
            )

            .agg(

                Spending=(
                    "Avg_Monthly_Spending",
                    "mean"
                ),

                Savings=(
                    "Savings_Balance",
                    "mean"
                ),

                Investment=(
                    "Investment_Value",
                    "mean"
                )

            )

            .reset_index()

        )


        fig = go.Figure()


        fig.add_trace(

            go.Bar(

                x=
                employment_financial[
                    "Employment_Type"
                ],

                y=
                employment_financial[
                    "Spending"
                ],

                name="Spending",

                marker_color=BLUE

            )

        )


        fig.add_trace(

            go.Bar(

                x=
                employment_financial[
                    "Employment_Type"
                ],

                y=
                employment_financial[
                    "Savings"
                ],

                name="Savings",

                marker_color=GREEN

            )

        )


        fig.add_trace(

            go.Bar(

                x=
                employment_financial[
                    "Employment_Type"
                ],

                y=
                employment_financial[
                    "Investment"
                ],

                name="Investment",

                marker_color=PURPLE

            )

        )


        fig.update_layout(

            barmode="group",

            height=450,

            template="plotly_white",

            title=
            "🏢 Financial Behaviour by Employment Type"

        )


        st.plotly_chart(

            fig,

            use_container_width=True

        )


    # ========================================================
    # AUTOMATIC INSIGHTS
    # ========================================================

    st.markdown(
        '<div class="section-header">'
        '💡 Automatic Dashboard Insights'
        '</div>',
        unsafe_allow_html=True
    )


    highest_spending_age = (

        filtered_df

        .groupby(
            "Age_Group",
            observed=True
        )["Avg_Monthly_Spending"]

        .mean()

        .idxmax()

    )


    highest_spending_employment = (

        filtered_df

        .groupby(
            "Employment_Type"
        )["Avg_Monthly_Spending"]

        .mean()

        .idxmax()

    )


    highest_credit_score_group = (

        filtered_df

        .groupby(
            "Employment_Type"
        )["Credit_Score"]

        .mean()

        .idxmax()

    )


    high_utilization_count = (

        filtered_df[
            "Credit_Utilization"
        ] >= 70

    ).sum()


    i1, i2, i3, i4 = st.columns(4)


    i1.info(
        f"👥 Highest spending age group\n\n"
        f"**{highest_spending_age}**"
    )


    i2.info(
        f"💼 Highest spending employment type\n\n"
        f"**{highest_spending_employment}**"
    )


    i3.success(
        f"⭐ Highest average credit score\n\n"
        f"**{highest_credit_score_group}**"
    )


    i4.warning(
        f"⚠️ Customers with utilization ≥ 70%\n\n"
        f"**{high_utilization_count:,}**"
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "💳 Advanced Credit Card Banking Analytics | "
    "Python • Pandas • Plotly • Streamlit"
)
