import os
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sb
import plotly.express as px
import plotly.graph_objects as go

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Financial Performance Analysis",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main > div {
        padding-top: 1rem;
    }

    .block-container {
        padding-left: 2rem;
        padding-right: 2rem;
    }

    .metric-card {
        background: linear-gradient(
            135deg,
            rgba(49,51,63,.96),
            rgba(31,34,45,.96)
        );
        padding: 16px 18px;
        border-radius: 14px;
        border: 1px solid rgba(255,255,255,.08);
        box-shadow: 0 4px 18px rgba(0,0,0,.15);
    }

    .insight {
        padding: 14px 18px;
        border-left: 4px solid #4CAF50;
        background: rgba(76,175,80,.08);
        border-radius: 8px;
        margin: 8px 0;
    }

    .risk {
        padding: 14px 18px;
        border-left: 4px solid #FF7043;
        background: rgba(255,112,67,.08);
        border-radius: 8px;
        margin: 8px 0;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data():

    data = pd.read_excel("Credir_Card_Bank.xlsx")

    # Clean column names
    data.columns = (
        data.columns
        .str.strip()
        .str.replace(" ", "_", regex=False)
    )

    # Numeric columns
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

    for column in numeric_columns:

        if column in data.columns:

            data[column] = pd.to_numeric(
                data[column],
                errors="coerce"
            )

    return data


# Load the confirmed dataset
df = load_data()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("Credit Card Bank")

st.sidebar.markdown(
    "### Dashboard Controls"
)

# ============================================================
# SIDEBAR FILTERS
# ============================================================

st.sidebar.subheader("Filters")


def get_options(column):

    if column in df.columns:

        return sorted(
            df[column]
            .dropna()
            .unique()
            .tolist()
        )

    return []


# Gender

if "Gender" in df.columns:

    gender_options = get_options("Gender")

    gender = st.sidebar.multiselect(
        "Gender",
        gender_options,
        default=gender_options
    )

else:

    gender = []


# Employment

if "Employment_Type" in df.columns:

    employment_options = get_options(
        "Employment_Type"
    )

    employment = st.sidebar.multiselect(
        "Employment Type",
        employment_options,
        default=employment_options
    )

else:

    employment = []


# Residential status

if "Residential_Status" in df.columns:

    residential_options = get_options(
        "Residential_Status"
    )

    residential = st.sidebar.multiselect(
        "Residential Status",
        residential_options,
        default=residential_options
    )

else:

    residential = []


# KYC

if "KYC_Status" in df.columns:

    kyc_options = get_options(
        "KYC_Status"
    )

    kyc = st.sidebar.multiselect(
        "KYC Status",
        kyc_options,
        default=kyc_options
    )

else:

    kyc = []


# Fraud flag

if "Fraud_Flag" in df.columns:

    fraud_options = get_options(
        "Fraud_Flag"
    )

    fraud = st.sidebar.multiselect(
        "Fraud Flag",
        fraud_options,
        default=fraud_options
    )

else:

    fraud = []


# ============================================================
# AGE FILTER
# ============================================================

if "Age" in df.columns:

    min_age = int(df["Age"].min())
    max_age = int(df["Age"].max())

    age_range = st.sidebar.slider(
        "Age",
        min_age,
        max_age,
        (min_age, max_age)
    )

else:

    age_range = None


# ============================================================
# CREDIT SCORE FILTER
# ============================================================

if "Credit_Score" in df.columns:

    min_score = int(
        df["Credit_Score"].min()
    )

    max_score = int(
        df["Credit_Score"].max()
    )

    score_range = st.sidebar.slider(
        "Credit Score",
        min_score,
        max_score,
        (min_score, max_score)
    )

else:

    score_range = None


# ============================================================
# INCOME FILTER
# ============================================================

if "Annual_Income" in df.columns:

    min_income = float(
        df["Annual_Income"].min()
    )

    max_income = float(
        df["Annual_Income"].max()
    )

    income_range = st.sidebar.slider(
        "Annual Income",
        min_income,
        max_income,
        (min_income, max_income),
        format="₹%.0f"
    )

else:

    income_range = None


# ============================================================
# APPLY FILTERS
# ============================================================

filtered_df = df.copy()


if gender and "Gender" in filtered_df.columns:

    filtered_df = filtered_df[
        filtered_df["Gender"].isin(gender)
    ]


if employment and "Employment_Type" in filtered_df.columns:

    filtered_df = filtered_df[
        filtered_df["Employment_Type"].isin(
            employment
        )
    ]


if residential and "Residential_Status" in filtered_df.columns:

    filtered_df = filtered_df[
        filtered_df["Residential_Status"].isin(
            residential
        )
    ]


if kyc and "KYC_Status" in filtered_df.columns:

    filtered_df = filtered_df[
        filtered_df["KYC_Status"].isin(kyc)
    ]


if fraud and "Fraud_Flag" in filtered_df.columns:

    filtered_df = filtered_df[
        filtered_df["Fraud_Flag"].isin(fraud)
    ]


if age_range and "Age" in filtered_df.columns:

    filtered_df = filtered_df[
        filtered_df["Age"].between(
            age_range[0],
            age_range[1]
        )
    ]


if score_range and "Credit_Score" in filtered_df.columns:

    filtered_df = filtered_df[
        filtered_df["Credit_Score"].between(
            score_range[0],
            score_range[1]
        )
    ]


if income_range and "Annual_Income" in filtered_df.columns:

    filtered_df = filtered_df[
        filtered_df["Annual_Income"].between(
            income_range[0],
            income_range[1]
        )
    ]


st.sidebar.markdown("---")

st.sidebar.info(
    f"Showing **{len(filtered_df):,}** "
    f"of **{len(df):,}** customers"
)


# ============================================================
# CREDIT SCORE CATEGORY
# ============================================================

def credit_category(score):

    if score < 580:

        return "Poor"

    elif score < 670:

        return "Fair"

    elif score < 740:

        return "Good"

    elif score < 800:

        return "Very Good"

    else:

        return "Excellent"


if "Credit_Score" in filtered_df.columns:

    filtered_df["Credit_Band"] = (
        filtered_df["Credit_Score"]
        .apply(credit_category)
    )


# ============================================================
# CUSTOM RISK INDICATOR
# ============================================================

risk_columns = [
    "Debt_To_Income_Ratio",
    "Credit_Utilization",
    "Missed_Payments",
    "Late_Payment_Count",
    "Number_of_Defaults"
]

if all(
    column in filtered_df.columns
    for column in risk_columns
):

    filtered_df["Risk_Indicator"] = (

        filtered_df["Debt_To_Income_Ratio"] * 35

        +

        (
            filtered_df["Credit_Utilization"] /
            100
        ) * 25

        +

        filtered_df["Missed_Payments"] * 4

        +

        filtered_df["Late_Payment_Count"] * 1.5

        +

        filtered_df["Number_of_Defaults"] * 12
    )

    filtered_df["Risk_Level"] = pd.cut(

        filtered_df["Risk_Indicator"],

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


# ============================================================
# HEADER
# ============================================================

st.title(
    "Financial Performance Analysis"
)

st.caption(
    "Interactive financial analysis dashboard "
    "using customer credit, income, spending, "
    "loan and risk data."
)


# ============================================================
# TABS
# ============================================================

tabs = st.tabs(
    [
        "Executive Overview",
        "Financial Behavior",
        "Credit & Risk"
    ]
)


# ============================================================
# TAB 1 — EXECUTIVE OVERVIEW
# ============================================================

with tabs[0]:

    st.header(
        "Executive Overview"
    )

    # KPI calculations

    total_customers = len(filtered_df)

    avg_income = (
        filtered_df["Annual_Income"].mean()
        if "Annual_Income" in filtered_df
        else 0
    )

    avg_credit_score = (
        filtered_df["Credit_Score"].mean()
        if "Credit_Score" in filtered_df
        else 0
    )

    avg_credit_limit = (
        filtered_df["Credit_Limit"].mean()
        if "Credit_Limit" in filtered_df
        else 0
    )

    avg_utilization = (
        filtered_df["Credit_Utilization"].mean()
        if "Credit_Utilization" in filtered_df
        else 0
    )

    total_savings = (
        filtered_df["Savings_Balance"].sum()
        if "Savings_Balance" in filtered_df
        else 0
    )

    total_investment = (
        filtered_df["Investment_Value"].sum()
        if "Investment_Value" in filtered_df
        else 0
    )

    avg_dti = (
        filtered_df["Debt_To_Income_Ratio"].mean()
        if "Debt_To_Income_Ratio" in filtered_df
        else 0
    )


    # KPI row 1

    col1, col2, col3, col4 = st.columns(4)


    col1.metric(
        "Customers",
        f"{total_customers:,}"
    )


    col2.metric(
        "Avg Annual Income",
        f"₹{avg_income:,.0f}"
    )


    col3.metric(
        "Avg Credit Score",
        f"{avg_credit_score:,.0f}"
    )


    col4.metric(
        "Avg Credit Limit",
        f"₹{avg_credit_limit:,.0f}"
    )


    # KPI row 2

    col1, col2, col3, col4 = st.columns(4)


    col1.metric(
        "Avg Credit Utilization",
        f"{avg_utilization:.1f}%"
    )


    col2.metric(
        "Total Savings",
        f"₹{total_savings:,.0f}"
    )


    col3.metric(
        "Total Investments",
        f"₹{total_investment:,.0f}"
    )


    col4.metric(
        "Avg DTI Ratio",
        f"{avg_dti:.2f}"
    )


    st.markdown("---")

    st.subheader(
        "Financial Position"
    )


    col1, col2 = st.columns(2)


       # Income vs savings

    with col1:

        if all(
            c in filtered_df.columns
            for c in [
                "Annual_Income",
                "Savings_Balance"
            ]
        ):

            fig = px.scatter(

                filtered_df,

                x="Annual_Income",

                y="Savings_Balance",

                size="Credit_Limit"
                if "Credit_Limit"
                in filtered_df.columns
                else None,

                color="Credit_Band"
                if "Credit_Band"
                in filtered_df.columns
                else None,

                hover_data=[
                    c for c in [
                        "Customer_ID",
                        "Credit_Score",
                        "Employment_Type"
                    ]
                    if c in filtered_df.columns
                ],

                title="Annual Income vs Savings Balance"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )


    # Income vs investments

    with col2:

        if all(
            c in filtered_df.columns
            for c in [
                "Annual_Income",
                "Investment_Value"
            ]
        ):

            fig = px.scatter(

                filtered_df,

                x="Annual_Income",

                y="Investment_Value",

                size="Credit_Limit"
                if "Credit_Limit"
                in filtered_df.columns
                else None,

                color="Employment_Type"
                if "Employment_Type"
                in filtered_df.columns
                else None,

                hover_data=[
                    c for c in [
                        "Customer_ID",
                        "Credit_Score"
                    ]
                    if c in filtered_df.columns
                ],

                title="Annual Income vs Investment Value"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

    
    st.subheader(
        "Business Insights"
    )


    st.markdown(
        """
        <div class="insight">
        <b>Higher-income customers</b> generally show
        stronger savings capacity and can be suitable
        candidates for premium banking products.
        </div>
        """,
        unsafe_allow_html=True
    )


    st.markdown(
        """
        <div class="insight">
        Customers with stronger investment values
        can be targeted for wealth-management and
        investment products.
        </div>
        """,
        unsafe_allow_html=True
    )


    st.markdown(
        """
        <div class="risk">
        Customers with higher EMI obligations
        may experience greater repayment pressure.
        </div>
        """,
        unsafe_allow_html=True
    )


    st.markdown(
        """
        <div class="risk">
        Higher debt-to-income ratio can indicate
        lower repayment capacity.
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# TAB 2 — FINANCIAL BEHAVIOR
# ============================================================

with tabs[1]:

    st.header(
        "Financial Behavior Analysis"
    )


    metric = st.selectbox(

        "Select financial metric",

        [
            "Savings_Balance",
            "Investment_Value",
            "Avg_Monthly_Spending",
            "EMI_Per_Month"
        ],

        format_func=lambda x: x.replace(
            "_",
            " "
        )
    )


    col1, col2 = st.columns(2)


    # Income vs selected metric

    with col1:

        if (
            "Annual_Income" in filtered_df.columns
            and metric in filtered_df.columns
        ):

            fig = px.scatter(

                filtered_df,

                x="Annual_Income",

                y=metric,

                color="Employment_Type"
                if "Employment_Type"
                in filtered_df.columns
                else None,

                hover_data=[
                    c for c in [
                        "Customer_ID",
                        "Credit_Score"
                    ]
                    if c in filtered_df.columns
                ],

                title=(
                    "Annual Income vs "
                    + metric.replace("_", " ")
                )
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )


    # Occupation metric

    with col2:

        if (
            "Occupation" in filtered_df.columns
            and metric in filtered_df.columns
        ):

            occupation_metric = (
                filtered_df
                .groupby("Occupation")[metric]
                .mean()
                .sort_values(
                    ascending=False
                )
                .head(10)
                .reset_index()
            )


            occupation_metric = (
                occupation_metric
                .sort_values(metric)
            )


            fig = px.bar(

                occupation_metric,

                x=metric,

                y="Occupation",

                orientation="h",

                text_auto=".2s",

                title=(
                    "Top Occupations by Average "
                    + metric.replace("_", " ")
                )
            )


            st.plotly_chart(
                fig,
                use_container_width=True
            )


    st.subheader(
        "Spending & Transaction Behavior"
    )


    col1, col2 = st.columns(2)


    with col1:

        required = [
            "Avg_Monthly_Transactions",
            "Avg_Monthly_Spending"
        ]

        if all(
            c in filtered_df.columns
            for c in required
        ):

            fig = px.scatter(

                filtered_df,

                x="Avg_Monthly_Transactions",

                y="Avg_Monthly_Spending",

                size="Credit_Limit"
                if "Credit_Limit"
                in filtered_df.columns
                else None,

                color="Credit_Utilization"
                if "Credit_Utilization"
                in filtered_df.columns
                else None,

                hover_data=[
                    c for c in [
                        "Customer_ID",
                        "Occupation"
                    ]
                    if c in filtered_df.columns
                ],

                title="Transactions vs Monthly Spending"
            )


            st.plotly_chart(
                fig,
                use_container_width=True
            )


    with col2:

        if "EMI_Per_Month" in filtered_df.columns:

            fig = px.histogram(

                filtered_df,

                x="EMI_Per_Month",

                nbins=30,

                title="Monthly EMI Distribution"
            )


            st.plotly_chart(
                fig,
                use_container_width=True
            )


# ============================================================
# TAB 3 — CREDIT & RISK
# ============================================================

with tabs[2]:

    st.header(
        "Credit Performance & Risk"
    )


    if "Risk_Level" in filtered_df.columns:

        higher_risk = (
            filtered_df["Risk_Level"]
            .eq("Higher")
            .sum()
        )

        moderate_risk = (
            filtered_df["Risk_Level"]
            .eq("Moderate")
            .sum()
        )

    else:

        higher_risk = 0
        moderate_risk = 0


    defaults = (

        filtered_df[
            "Number_of_Defaults"
        ].sum()

        if "Number_of_Defaults"
        in filtered_df.columns

        else 0
    )


    missed_payments = (

        filtered_df[
            "Missed_Payments"
        ].sum()

        if "Missed_Payments"
        in filtered_df.columns

        else 0
    )


    c1, c2, c3, c4 = st.columns(4)


    c1.metric(
        "Higher Risk",
        f"{higher_risk:,}"
    )


    c2.metric(
        "Moderate Risk",
        f"{moderate_risk:,}"
    )


    c3.metric(
        "Defaults",
        f"{int(defaults):,}"
    )


    c4.metric(
        "Missed Payments",
        f"{int(missed_payments):,}"
    )


    col1, col2 = st.columns(2)


    # Credit utilization

    with col1:

        if "Credit_Utilization" in filtered_df.columns:

            fig = px.histogram(

                filtered_df,

                x="Credit_Utilization",

                nbins=30,

                color="Risk_Level"
                if "Risk_Level"
                in filtered_df.columns
                else None,

                marginal="box",

                title="Credit Utilization Distribution"
            )


            fig.add_vline(
                x=75,
                line_dash="dash",
                annotation_text="75% Reference"
            )


            st.plotly_chart(
                fig,
                use_container_width=True
            )


    # DTI vs credit score

    with col2:

        required = [
            "Debt_To_Income_Ratio",
            "Credit_Score"
        ]

        if all(
            c in filtered_df.columns
            for c in required
        ):

            fig = px.scatter(

                filtered_df,

                x="Debt_To_Income_Ratio",

                y="Credit_Score",

                size="Credit_Limit"
                if "Credit_Limit"
                in filtered_df.columns
                else None,

                color="Risk_Level"
                if "Risk_Level"
                in filtered_df.columns
                else None,

                hover_data=[
                    c for c in [
                        "Customer_ID",
                        "Missed_Payments",
                        "Number_of_Defaults"
                    ]
                    if c in filtered_df.columns
                ],

                title="DTI Ratio vs Credit Score"
            )


            st.plotly_chart(
                fig,
                use_container_width=True
            )


    col1, col2 = st.columns(2)


    # DTI by employment

    with col1:

        if (
            "Employment_Type"
            in filtered_df.columns
            and
            "Debt_To_Income_Ratio"
            in filtered_df.columns
        ):

            dti_data = (

                filtered_df
                .groupby(
                    "Employment_Type"
                )["Debt_To_Income_Ratio"]
                .mean()
                .sort_values()
                .reset_index()
            )


            fig = px.bar(

                dti_data,

                x="Debt_To_Income_Ratio",

                y="Employment_Type",

                orientation="h",

                text_auto=".2f",

                title="Average DTI by Employment Type"
            )


            st.plotly_chart(
                fig,
                use_container_width=True
            )


    # Utilization by occupation

    with col2:

        if (
            "Occupation" in filtered_df.columns
            and
            "Credit_Utilization"
            in filtered_df.columns
        ):

            utilization = (

                filtered_df
                .groupby(
                    "Occupation"
                )["Credit_Utilization"]
                .mean()
                .sort_values(
                    ascending=False
                )
                .head(10)
                .reset_index()
            )


            utilization = (
                utilization
                .sort_values(
                    "Credit_Utilization"
                )
            )


            fig = px.bar(

                utilization,

                x="Credit_Utilization",

                y="Occupation",

                orientation="h",

                text_auto=".1f",

                title=(
                    "Top 10 Occupations by "
                    "Credit Utilization"
                )
            )


            st.plotly_chart(
                fig,
                use_container_width=True
            )


    # Risk distribution

    if "Risk_Level" in filtered_df.columns:

        st.subheader(
            "Risk Indicator Distribution"
        )


        risk_data = (

            filtered_df["Risk_Level"]
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

            text_auto=True,

            title="Customer Risk Distribution"
        )


        st.plotly_chart(
            fig,
            use_container_width=True
        )


        st.caption(
            "The risk indicator is a custom dashboard "
            "analytical measure based on DTI, credit "
            "utilization, missed payments, late payments "
            "and defaults. It is not an official bank "
            "credit-risk score."
        )



# ============================================================
# SIDEBAR FOOTER
# ============================================================

st.sidebar.markdown("---")

st.sidebar.caption(
    "Built with Streamlit • Pandas • Plotly • NumPy"
)
