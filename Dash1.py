import streamlit as st
import pandas as pd
import plotly.express as px

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Credit Card Banking Dashboard",
    page_icon="💳",
    layout="wide"
)

# ============================================================
# CSS
# ============================================================

st.markdown("""
<style>

.block-container {
    padding-top: 1rem;
}

.title {
    font-size: 35px;
    font-weight: 800;
}

.subtitle {
    color: #6b7280;
    margin-bottom: 20px;
}

[data-testid="stMetric"] {
    background-color: white;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 12px;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data():

    df = pd.read_excel("Credir_Card_Bank.xlsx")

    # Age Group
    def age_group(age):

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

    df["Age_Group"] = df["Age"].apply(age_group)

    return df


df = load_data()


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="title">💳 Credit Card Banking Analytics Dashboard</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Interactive customer spending, transaction and financial analysis'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR FILTERS
# ============================================================

st.sidebar.header("🎯 Dashboard Filters")


# Employment

employment_options = sorted(
    df["Employment_Type"].dropna().unique()
)

employment = st.sidebar.multiselect(
    "Employment Type",
    employment_options,
    default=employment_options
)


# Gender

gender_options = sorted(
    df["Gender"].dropna().unique()
)

gender = st.sidebar.multiselect(
    "Gender",
    gender_options,
    default=gender_options
)


# Age Group

age_options = sorted(
    df["Age_Group"].dropna().unique()
)

age_group = st.sidebar.multiselect(
    "Age Group",
    age_options,
    default=age_options
)


# Occupation

occupation_options = sorted(
    df["Occupation"].dropna().unique()
)

occupation = st.sidebar.multiselect(
    "Occupation",
    occupation_options,
    default=occupation_options
)


# Residential Status

residential_options = sorted(
    df["Residential_Status"].dropna().unique()
)

residential = st.sidebar.multiselect(
    "Residential Status",
    residential_options,
    default=residential_options
)


# KYC

kyc_options = sorted(
    df["KYC_Status"].dropna().unique()
)

kyc = st.sidebar.multiselect(
    "KYC Status",
    kyc_options,
    default=kyc_options
)


# Fraud

fraud_options = sorted(
    df["Fraud_Flag"].dropna().unique()
)

fraud = st.sidebar.multiselect(
    "Fraud Flag",
    fraud_options,
    default=fraud_options
)


# Age Range

min_age = int(df["Age"].min())
max_age = int(df["Age"].max())

age_range = st.sidebar.slider(
    "Age Range",
    min_age,
    max_age,
    (min_age, max_age)
)


# ============================================================
# APPLY FILTERS
# ============================================================

filtered_df = df[
    (df["Employment_Type"].isin(employment))
    &
    (df["Gender"].isin(gender))
    &
    (df["Age_Group"].isin(age_group))
    &
    (df["Occupation"].isin(occupation))
    &
    (df["Residential_Status"].isin(residential))
    &
    (df["KYC_Status"].isin(kyc))
    &
    (df["Fraud_Flag"].isin(fraud))
    &
    (df["Age"].between(age_range[0], age_range[1]))
].copy()


if filtered_df.empty:

    st.warning(
        "⚠️ No data available for selected filters."
    )

    st.stop()


# ============================================================
# TWO PAGES
# ============================================================

page1, page2 = st.tabs(
    [
        "📊 PAGE 1 — CUSTOMER & SPENDING",
        "💰 PAGE 2 — FINANCIAL ANALYSIS"
    ]
)


# ============================================================
# PAGE 1
# ============================================================

with page1:

    st.subheader("📊 Customer & Spending Analysis")


    # --------------------------------------------------------
    # KPI
    # --------------------------------------------------------

    col1, col2, col3, col4, col5 = st.columns(5)


    col1.metric(
        "👥 Customers",
        f"{len(filtered_df):,}"
    )


    col2.metric(
        "💰 Avg Spending",
        f"₹{filtered_df['Avg_Monthly_Spending'].mean():,.0f}"
    )


    col3.metric(
        "🔄 Avg Transactions",
        f"{filtered_df['Avg_Monthly_Transactions'].mean():,.0f}"
    )


    col4.metric(
        "⭐ Avg Credit Score",
        f"{filtered_df['Credit_Score'].mean():,.0f}"
    )


    col5.metric(
        "💳 Credit Utilization",
        f"{filtered_df['Credit_Utilization'].mean():.1f}%"
    )


    st.divider()


    # --------------------------------------------------------
    # ROW 1
    # --------------------------------------------------------

    col1, col2 = st.columns(2)


    # Spending Distribution

    with col1:

        fig = px.histogram(
            filtered_df,
            x="Avg_Monthly_Spending",
            nbins=25,
            marginal="box",
            title="Monthly Spending Distribution"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    # Age Group

    with col2:

        age_spending = (
            filtered_df
            .groupby(
                "Age_Group",
                observed=True
            )["Avg_Monthly_Spending"]
            .mean()
            .reset_index()
        )

        fig = px.bar(
            age_spending,
            x="Age_Group",
            y="Avg_Monthly_Spending",
            title="Average Spending by Age Group"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    # --------------------------------------------------------
    # ROW 2
    # --------------------------------------------------------

    col1, col2 = st.columns(2)


    # Occupation

    with col1:

        occupation_spending = (
            filtered_df
            .groupby("Occupation")
            ["Avg_Monthly_Spending"]
            .mean()
            .sort_values()
            .reset_index()
        )

        fig = px.bar(
            occupation_spending,
            x="Avg_Monthly_Spending",
            y="Occupation",
            orientation="h",
            title="Average Spending by Occupation"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    # Employment

    with col2:

        employment_spending = (
            filtered_df
            .groupby("Employment_Type")
            ["Avg_Monthly_Spending"]
            .mean()
            .reset_index()
        )

        fig = px.bar(
            employment_spending,
            x="Employment_Type",
            y="Avg_Monthly_Spending",
            title="Average Spending by Employment Type"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    # --------------------------------------------------------
    # ROW 3
    # --------------------------------------------------------

    col1, col2 = st.columns(2)


    # Gender

    with col1:

        gender_spending = (
            filtered_df
            .groupby("Gender")
            ["Avg_Monthly_Spending"]
            .mean()
            .reset_index()
        )

        fig = px.bar(
            gender_spending,
            x="Gender",
            y="Avg_Monthly_Spending",
            title="Average Spending by Gender"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    # Income vs Spending

    with col2:

        fig = px.scatter(
            filtered_df,
            x="Annual_Income",
            y="Avg_Monthly_Spending",
            color="Credit_Score",
            size="Credit_Limit",
            hover_data=[
                "Customer_ID",
                "Age",
                "Gender",
                "Occupation"
            ],
            title="Annual Income vs Monthly Spending"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


# ============================================================
# PAGE 2
# ============================================================

with page2:

    st.subheader("💰 Financial Behaviour Analysis")


    # --------------------------------------------------------
    # KPI
    # --------------------------------------------------------

    col1, col2, col3, col4, col5 = st.columns(5)


    col1.metric(
        "💵 Avg EMI",
        f"₹{filtered_df['EMI_Per_Month'].mean():,.0f}"
    )


    col2.metric(
        "📉 Avg DTI",
        f"{filtered_df['Debt_To_Income_Ratio'].mean():.2f}"
    )


    col3.metric(
        "🏦 Avg Savings",
        f"₹{filtered_df['Savings_Balance'].mean():,.0f}"
    )


    col4.metric(
        "📈 Avg Investment",
        f"₹{filtered_df['Investment_Value'].mean():,.0f}"
    )


    col5.metric(
        "💳 Total Credit Limit",
        f"₹{filtered_df['Credit_Limit'].sum()/10000000:.2f} Cr"
    )


    st.divider()


    # --------------------------------------------------------
    # CREATE FINANCIAL GROUPS
    # --------------------------------------------------------

    filtered_df["EMI_Group"] = pd.cut(
        filtered_df["EMI_Per_Month"],
        bins=5,
        labels=[
            "Very Low",
            "Low",
            "Medium",
            "High",
            "Very High"
        ]
    )


    filtered_df["DTI_Group"] = pd.cut(
        filtered_df["Debt_To_Income_Ratio"],
        bins=5,
        labels=[
            "Very Low",
            "Low",
            "Medium",
            "High",
            "Very High"
        ]
    )


    filtered_df["Savings_Group"] = pd.cut(
        filtered_df["Savings_Balance"],
        bins=5,
        labels=[
            "Very Low",
            "Low",
            "Medium",
            "High",
            "Very High"
        ]
    )


    filtered_df["Investment_Group"] = pd.cut(
        filtered_df["Investment_Value"],
        bins=5,
        labels=[
            "Very Low",
            "Low",
            "Medium",
            "High",
            "Very High"
        ]
    )


    # --------------------------------------------------------
    # ROW 1
    # --------------------------------------------------------

    col1, col2 = st.columns(2)


    # EMI

    with col1:

        emi_data = (
            filtered_df
            .groupby(
                "EMI_Group",
                observed=True
            )["Avg_Monthly_Spending"]
            .mean()
            .reset_index()
        )

        fig = px.bar(
            emi_data,
            x="EMI_Group",
            y="Avg_Monthly_Spending",
            title="Spending by EMI Group"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    # DTI

    with col2:

        dti_data = (
            filtered_df
            .groupby(
                "DTI_Group",
                observed=True
            )["Avg_Monthly_Spending"]
            .mean()
            .reset_index()
        )

        fig = px.line(
            dti_data,
            x="DTI_Group",
            y="Avg_Monthly_Spending",
            markers=True,
            title="Spending by Debt-to-Income Group"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    # --------------------------------------------------------
    # ROW 2
    # --------------------------------------------------------

    col1, col2 = st.columns(2)


    # Savings

    with col1:

        savings_data = (
            filtered_df
            .groupby(
                "Savings_Group",
                observed=True
            )["Avg_Monthly_Spending"]
            .mean()
            .reset_index()
        )

        fig = px.bar(
            savings_data,
            x="Savings_Group",
            y="Avg_Monthly_Spending",
            title="Spending by Savings Group"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    # Investment

    with col2:

        investment_data = (
            filtered_df
            .groupby(
                "Investment_Group",
                observed=True
            )["Avg_Monthly_Spending"]
            .mean()
            .reset_index()
        )

        fig = px.bar(
            investment_data,
            x="Investment_Group",
            y="Avg_Monthly_Spending",
            title="Spending by Investment Group"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    # --------------------------------------------------------
    # ROW 3
    # --------------------------------------------------------

    col1, col2 = st.columns(2)


    # Credit Utilization

    with col1:

        fig = px.scatter(
            filtered_df,
            x="Credit_Limit",
            y="Credit_Utilization",
            size="Avg_Monthly_Spending",
            color="Credit_Score",
            hover_data=[
                "Customer_ID",
                "Age"
            ],
            title="Credit Limit vs Credit Utilization"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    # Transactions

    with col2:

        transaction_data = (
            filtered_df
            .groupby("Employment_Type")
            ["Avg_Monthly_Transactions"]
            .mean()
            .reset_index()
        )

        fig = px.bar(
            transaction_data,
            x="Employment_Type",
            y="Avg_Monthly_Transactions",
            title="Average Transactions by Employment Type"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Credit Card Banking Analytics Dashboard | "
    "Python • Pandas • Plotly • Streamlit"
)
