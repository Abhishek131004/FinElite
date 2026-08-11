import streamlit as st
import pandas as pd
import plotly.express as px

# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Credit Card Banking Dashboard",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

.stApp {
    background-color: #f4f6f9;
}

.main-title {
    font-size: 38px;
    font-weight: 800;
    color: #1f2937;
}

.subtitle {
    color: #6b7280;
    font-size: 17px;
    margin-bottom: 25px;
}

[data-testid="stMetric"] {
    background-color: white;
    padding: 15px;
    border-radius: 12px;
    border: 1px solid #e5e7eb;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.05);
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# LOAD EXCEL DATA
# =========================================================

@st.cache_data
def load_data():

    df = pd.read_excel("Credir_Card_Bank.xlsx")

    return df


df = load_data()


# =========================================================
# TITLE
# =========================================================

st.markdown(
    '<div class="main-title">💳 Credit Card Banking Analytics Dashboard</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Interactive analysis of customer spending, transactions, credit and financial behaviour'
    '</div>',
    unsafe_allow_html=True
)


# =========================================================
# SIDEBAR FILTERS
# =========================================================

st.sidebar.title("🎯 Dashboard Filters")

st.sidebar.markdown("---")


# Employment Type

employment_options = sorted(
    df["Employment_Type"].dropna().unique()
)

selected_employment = st.sidebar.multiselect(
    "Employment Type",
    employment_options,
    default=employment_options
)


# Gender

gender_options = sorted(
    df["Gender"].dropna().unique()
)

selected_gender = st.sidebar.multiselect(
    "Gender",
    gender_options,
    default=gender_options
)


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


age_group_options = list(
    df["Age_Group"].unique()
)

selected_age_group = st.sidebar.multiselect(
    "Age Group",
    age_group_options,
    default=age_group_options
)


# Residential Status

residential_options = sorted(
    df["Residential_Status"].dropna().unique()
)

selected_residential = st.sidebar.multiselect(
    "Residential Status",
    residential_options,
    default=residential_options
)


# KYC Status

kyc_options = sorted(
    df["KYC_Status"].dropna().unique()
)

selected_kyc = st.sidebar.multiselect(
    "KYC Status",
    kyc_options,
    default=kyc_options
)


# Fraud Flag

fraud_options = sorted(
    df["Fraud_Flag"].dropna().unique()
)

selected_fraud = st.sidebar.multiselect(
    "Fraud Flag",
    fraud_options,
    default=fraud_options
)


# Age Slider

min_age = int(df["Age"].min())
max_age = int(df["Age"].max())

selected_age = st.sidebar.slider(
    "Age Range",
    min_age,
    max_age,
    (min_age, max_age)
)


# =========================================================
# FILTER DATA
# =========================================================

filtered_df = df[
    (df["Employment_Type"].isin(selected_employment))
    &
    (df["Gender"].isin(selected_gender))
    &
    (df["Age_Group"].isin(selected_age_group))
    &
    (df["Residential_Status"].isin(selected_residential))
    &
    (df["KYC_Status"].isin(selected_kyc))
    &
    (df["Fraud_Flag"].isin(selected_fraud))
    &
    (df["Age"].between(selected_age[0], selected_age[1]))
].copy()


# =========================================================
# CHECK FILTERED DATA
# =========================================================

if filtered_df.empty:

    st.warning(
        "⚠️ No records found for the selected filters."
    )

    st.stop()


# =========================================================
# KPI SECTION
# =========================================================

st.subheader("📊 Key Performance Indicators")

col1, col2, col3, col4, col5, col6 = st.columns(6)


# Total Customers

col1.metric(
    "👥 Customers",
    f"{len(filtered_df):,}"
)


# Average Spending

col2.metric(
    "💰 Avg Spending",
    f"₹{filtered_df['Avg_Monthly_Spending'].mean():,.0f}"
)


# Average Transactions

col3.metric(
    "🔄 Avg Transactions",
    f"{filtered_df['Avg_Monthly_Transactions'].mean():,.0f}"
)


# Credit Score

col4.metric(
    "⭐ Avg Credit Score",
    f"{filtered_df['Credit_Score'].mean():,.0f}"
)


# Credit Utilization

col5.metric(
    "💳 Credit Utilization",
    f"{filtered_df['Credit_Utilization'].mean():.1f}%"
)


# Credit Limit

col6.metric(
    "🏦 Credit Limit",
    f"₹{filtered_df['Credit_Limit'].sum()/10000000:.2f} Cr"
)


# =========================================================
# TABS
# =========================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "📈 Spending Analysis",
        "👥 Customer Behaviour",
        "💰 Financial Analysis",
        "⭐ Segmentation",
        "📋 Customer Data"
    ]
)


# =========================================================
# TAB 1
# SPENDING ANALYSIS
# =========================================================

with tab1:

    st.header("📈 Spending Analysis")


    # -----------------------------------------------------
    # Spending Distribution
    # -----------------------------------------------------

    col1, col2 = st.columns(2)


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


    # -----------------------------------------------------
    # Age Group Spending
    # -----------------------------------------------------

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


    # -----------------------------------------------------
    # Occupation Spending
    # -----------------------------------------------------

    col1, col2 = st.columns(2)


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


    # -----------------------------------------------------
    # Employment Spending
    # -----------------------------------------------------

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


    # -----------------------------------------------------
    # Income vs Spending
    # -----------------------------------------------------

    st.subheader("💰 Annual Income vs Monthly Spending")

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
            "Occupation",
            "Employment_Type"
        ],
        title="Income vs Spending"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# =========================================================
# TAB 2
# CUSTOMER BEHAVIOUR
# =========================================================

with tab2:

    st.header("👥 Customer Behaviour")


    col1, col2, col3 = st.columns(3)


    # Monthly Transactions

    with col1:

        fig = px.histogram(
            filtered_df,
            x="Avg_Monthly_Transactions",
            nbins=25,
            title="Monthly Transactions"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    # Gender

    with col2:

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
            title="Spending by Gender"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    # Residential Status

    with col3:

        residential_spending = (
            filtered_df
            .groupby("Residential_Status")
            ["Avg_Monthly_Spending"]
            .mean()
            .reset_index()
        )

        fig = px.bar(
            residential_spending,
            x="Residential_Status",
            y="Avg_Monthly_Spending",
            title="Spending by Residential Status"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    # -----------------------------------------------------
    # KYC / PAN / FRAUD
    # -----------------------------------------------------

    col1, col2, col3 = st.columns(3)


    with col1:

        kyc_spending = (
            filtered_df
            .groupby("KYC_Status")
            ["Avg_Monthly_Spending"]
            .mean()
            .reset_index()
        )

        fig = px.bar(
            kyc_spending,
            x="KYC_Status",
            y="Avg_Monthly_Spending",
            title="Spending by KYC Status"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    with col2:

        pan_spending = (
            filtered_df
            .groupby("PAN_Verified")
            ["Avg_Monthly_Spending"]
            .mean()
            .reset_index()
        )

        fig = px.bar(
            pan_spending,
            x="PAN_Verified",
            y="Avg_Monthly_Spending",
            title="Spending by PAN Verification"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    with col3:

        fraud_spending = (
            filtered_df
            .groupby("Fraud_Flag")
            ["Avg_Monthly_Spending"]
            .mean()
            .reset_index()
        )

        fig = px.bar(
            fraud_spending,
            x="Fraud_Flag",
            y="Avg_Monthly_Spending",
            title="Spending by Fraud Flag"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


# =========================================================
# TAB 3
# FINANCIAL ANALYSIS
# =========================================================

with tab3:

    st.header("💰 Financial Behaviour")


    # Create groups

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


    # -----------------------------------------------------
    # EMI
    # -----------------------------------------------------

    col1, col2 = st.columns(2)


    with col1:

        emi = (
            filtered_df
            .groupby(
                "EMI_Group",
                observed=True
            )["Avg_Monthly_Spending"]
            .mean()
            .reset_index()
        )

        fig = px.bar(
            emi,
            x="EMI_Group",
            y="Avg_Monthly_Spending",
            title="Spending by EMI Group"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    # -----------------------------------------------------
    # DTI
    # -----------------------------------------------------

    with col2:

        dti = (
            filtered_df
            .groupby(
                "DTI_Group",
                observed=True
            )["Avg_Monthly_Spending"]
            .mean()
            .reset_index()
        )

        fig = px.line(
            dti,
            x="DTI_Group",
            y="Avg_Monthly_Spending",
            markers=True,
            title="Spending by Debt-to-Income Ratio"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    # -----------------------------------------------------
    # Savings
    # -----------------------------------------------------

    col1, col2 = st.columns(2)


    with col1:

        savings = (
            filtered_df
            .groupby(
                "Savings_Group",
                observed=True
            )["Avg_Monthly_Spending"]
            .mean()
            .reset_index()
        )

        fig = px.bar(
            savings,
            x="Savings_Group",
            y="Avg_Monthly_Spending",
            title="Spending by Savings Balance"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    # -----------------------------------------------------
    # Investment
    # -----------------------------------------------------

    with col2:

        investment = (
            filtered_df
            .groupby(
                "Investment_Group",
                observed=True
            )["Avg_Monthly_Spending"]
            .mean()
            .reset_index()
        )

        fig = px.bar(
            investment,
            x="Investment_Group",
            y="Avg_Monthly_Spending",
            title="Spending by Investment Value"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    # -----------------------------------------------------
    # Credit Utilization
    # -----------------------------------------------------

    st.subheader("💳 Credit Utilization")

    fig = px.scatter(
        filtered_df,
        x="Credit_Limit",
        y="Credit_Utilization",
        size="Avg_Monthly_Spending",
        color="Credit_Score",
        hover_data=["Customer_ID"],
        title="Credit Limit vs Credit Utilization"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# =========================================================
# TAB 4
# CUSTOMER SEGMENTATION
# =========================================================

with tab4:

    st.header("⭐ Customer Segmentation")


    # -----------------------------------------------------
    # High Value Customers
    # -----------------------------------------------------

    income_75 = df["Annual_Income"].quantile(0.75)

    credit_limit_75 = df["Credit_Limit"].quantile(0.75)


    high_value = filtered_df[
        (filtered_df["Annual_Income"] > income_75)
        &
        (filtered_df["Credit_Limit"] > credit_limit_75)
    ]


    # -----------------------------------------------------
    # Low Engagement
    # -----------------------------------------------------

    transaction_25 = (
        df["Avg_Monthly_Transactions"]
        .quantile(0.25)
    )

    spending_25 = (
        df["Avg_Monthly_Spending"]
        .quantile(0.25)
    )


    low_engagement = filtered_df[
        (filtered_df["Avg_Monthly_Transactions"] < transaction_25)
        &
        (filtered_df["Avg_Monthly_Spending"] < spending_25)
    ]


    # -----------------------------------------------------
    # Fraud
    # -----------------------------------------------------

    fraud_customers = filtered_df[
        filtered_df["Fraud_Flag"] == "Yes"
    ]


    # KPI

    col1, col2, col3 = st.columns(3)


    col1.metric(
        "⭐ High Value Customers",
        len(high_value)
    )


    col2.metric(
        "⚠️ Low Engagement",
        len(low_engagement)
    )


    col3.metric(
        "🚨 Fraud Flagged",
        len(fraud_customers)
    )


    # -----------------------------------------------------
    # Segment Selection
    # -----------------------------------------------------

    segment = st.selectbox(
        "Select Segment",
        [
            "High Value Customers",
            "Low Engagement Customers",
            "Fraud Flagged Customers"
        ]
    )


    if segment == "High Value Customers":

        segment_df = high_value


    elif segment == "Low Engagement Customers":

        segment_df = low_engagement


    else:

        segment_df = fraud_customers


    # Display

    st.dataframe(
        segment_df,
        use_container_width=True,
        hide_index=True
    )


    # Download

    csv = segment_df.to_csv(
        index=False
    ).encode("utf-8")


    st.download_button(
        "⬇️ Download Segment",
        csv,
        "customer_segment.csv",
        "text/csv"
    )


# =========================================================
# TAB 5
# CUSTOMER DATA
# =========================================================

with tab5:

    st.header("📋 Customer Data Explorer")


    search = st.text_input(
        "🔎 Search Customer ID"
    )


    display_df = filtered_df.copy()


    if search:

        display_df = display_df[
            display_df["Customer_ID"]
            .astype(str)
            .str.contains(
                search,
                case=False,
                na=False
            )
        ]


    st.write(
        f"Showing {len(display_df):,} records"
    )


    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )


    # Download filtered data

    csv = display_df.to_csv(
        index=False
    ).encode("utf-8")


    st.download_button(
        "⬇️ Download Filtered Data",
        csv,
        "filtered_credit_card_data.csv",
        "text/csv"
    )


# =========================================================
# AUTOMATIC INSIGHTS
# =========================================================

st.divider()

st.header("💡 Business Insights")


age_analysis = (
    filtered_df
    .groupby("Age_Group")
    ["Avg_Monthly_Spending"]
    .mean()
)


occupation_analysis = (
    filtered_df
    .groupby("Occupation")
    ["Avg_Monthly_Spending"]
    .mean()
)


employment_analysis = (
    filtered_df
    .groupby("Employment_Type")
    ["Avg_Monthly_Spending"]
    .mean()
)


highest_age = age_analysis.idxmax()

highest_occupation = occupation_analysis.idxmax()

highest_employment = employment_analysis.idxmax()


col1, col2, col3 = st.columns(3)


col1.info(
    f"👥 Highest spending age group:\n\n"
    f"**{highest_age}**"
)


col2.info(
    f"💼 Highest spending occupation:\n\n"
    f"**{highest_occupation}**"
)


col3.info(
    f"🏢 Highest spending employment type:\n\n"
    f"**{highest_employment}**"
)


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "Credit Card Banking Analytics Dashboard | "
    "Python + Pandas + Plotly + Streamlit"
)
