import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# =============================================================================
# 1. PAGE CONFIGURATION & STYLING
# =============================================================================
st.set_page_config(
    page_title="Risk Analytics Dashboard",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for polished styling
st.markdown(
    """
    <style>
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 15px;
        border-left: 5px solid #2b5c8f;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .stPlotlyChart {
        background-color: #ffffff;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
""",
    unsafe_allow_html=True,
)


# =============================================================================
# 2. DATA LOADING & CACHING
# =============================================================================
@st.cache_data
def load_data():
    file_path = "../DataSets/Credir_Card_Bank.xlsx"

    # Fallback to local directory if relative path fails
    if not os.path.exists(file_path) and os.path.exists("Credir_Card_Bank.xlsx"):
        file_path = "Credir_Card_Bank.xlsx"

    df = pd.read_excel(file_path)

    # Core transformations from initial script
    df["default_payment_next_month"] = (df["Number_of_Defaults"] > 0).astype(
        int
    )
    df["Age_Group"] = pd.cut(
        df["Age"],
        bins=[18, 25, 35, 50, 65, 100],
        labels=["18-25", "26-35", "36-50", "51-65", "65+"],
    )

    high_risk_condition = (
        (df["Credit_Score"] < 600)
        | (df["Credit_Utilization"] > 75)
        | (df["Missed_Payments"] >= 3)
    )
    df["High_Risk_Flag"] = np.where(
        high_risk_condition, "High Risk", "Standard"
    )

    return df


try:
    df = load_data()
except Exception as e:
    st.error(
        f"Unable to load dataset. Please ensure `Credir_Card_Bank.xlsx` exists in `../DataSets/` or the app root folder. Error details: {e}"
    )
    st.stop()


# =============================================================================
# 3. INTERACTIVE SIDEBAR FILTERS
# =============================================================================
st.sidebar.header("🔍 Global Dashboard Filters")

# Filter 1: Risk Category
selected_risk = st.sidebar.multiselect(
    "Risk Segment Status",
    options=df["High_Risk_Flag"].unique(),
    default=df["High_Risk_Flag"].unique(),
)

# Filter 2: Age Group
selected_age_groups = st.sidebar.multiselect(
    "Age Groups",
    options=df["Age_Group"].cat.categories.tolist(),
    default=df["Age_Group"].cat.categories.tolist(),
)

# Filter 3: Occupation (if available)
if "Occupation" in df.columns:
    occupations = df["Occupation"].dropna().unique().tolist()
    selected_occ = st.sidebar.multiselect(
        "Occupation", options=occupations, default=occupations
    )
else:
    selected_occ = None

# Apply Filters
filtered_df = df[
    (df["High_Risk_Flag"].isin(selected_risk))
    & (df["Age_Group"].isin(selected_age_groups))
]

if selected_occ and "Occupation" in filtered_df.columns:
    filtered_df = filtered_df[filtered_df["Occupation"].isin(selected_occ)]


# =============================================================================
# 4. DASHBOARD HEADER & KPI CARDS
# =============================================================================
st.title("💳 Credit Risk & Default Profiling Analytics")
st.markdown(
    "An interactive dashboard analyzing portfolio default risk, age distribution, missed payments, and driver correlation."
)
st.divider()

# Executive Summary Metric Row
col1, col2, col3, col4, col5 = st.columns(5)

total_cust = len(filtered_df)
total_defaults = filtered_df["default_payment_next_month"].sum()
overall_default_rate = (
    (total_defaults / total_cust * 100) if total_cust > 0 else 0
)
avg_late = (
    filtered_df["Late_Payment_Count"].mean()
    if "Late_Payment_Count" in filtered_df.columns
    else 0
)
high_risk_count = (filtered_df["High_Risk_Flag"] == "High Risk").sum()

col1.metric("Total Customers", f"{total_cust:,}")
col2.metric("Defaulted Customers", f"{total_defaults:,}")
col3.metric("Default Rate", f"{overall_default_rate:.2f}%")
col4.metric("Avg Late Payments", f"{avg_late:.2f}")
col5.metric(
    "High Risk Flagged",
    f"{high_risk_count:,}",
    delta=f"{(high_risk_count/total_cust*100):.1f}%" if total_cust > 0 else "0%",
    delta_color="inverse",
)

st.divider()


# =============================================================================
# 5. DASHBOARD CHARTS (2x3 GRID)
# =============================================================================

row1_col1, row1_col2, row1_col3 = st.columns(3)

# -----------------------------------------------------------------------------
# Chart 1: Default Distribution
# -----------------------------------------------------------------------------
with row1_col1:
    st.subheader("1. Default Distribution (%)")
    default_dist = (
        filtered_df["default_payment_next_month"]
        .value_counts(normalize=True)
        .reset_index()
    )
    default_dist.columns = ["Status", "Percentage"]
    default_dist["Percentage"] *= 100
    default_dist["Status_Label"] = default_dist["Status"].map(
        {0: "Non-Defaulters (0)", 1: "Defaulters (1)"}
    )

    fig1 = px.bar(
        default_dist,
        x="Status_Label",
        y="Percentage",
        text=default_dist["Percentage"].apply(lambda x: f"{x:.2f}%"),
        color="Status_Label",
        color_discrete_map={
            "Non-Defaulters (0)": "#2b5c8f",
            "Defaulters (1)": "#d95f02",
        },
    )
    fig1.update_traces(
        textposition="outside", hovertemplate="%{x}: %{y:.2f}%"
    )
    fig1.update_layout(
        xaxis_title="",
        yaxis_title="Percentage (%)",
        showlegend=False,
        height=380,
    )
    st.plotly_chart(fig1, use_container_width=True)

# -----------------------------------------------------------------------------
# Chart 2: Default Rate by Age Group
# -----------------------------------------------------------------------------
with row1_col2:
    st.subheader("2. Default Rate by Age Group")
    risk_age = (
        filtered_df.groupby("Age_Group", observed=False)[
            "default_payment_next_month"
        ]
        .mean()
        .reset_index()
    )
    risk_age["Default Rate (%)"] = risk_age["default_payment_next_month"] * 100

    fig2 = px.bar(
        risk_age,
        x="Age_Group",
        y="Default Rate (%)",
        text=risk_age["Default Rate (%)"].apply(lambda x: f"{x:.2f}%"),
        color_discrete_sequence=["teal"],
    )
    fig2.update_traces(
        textposition="outside", hovertemplate="Age %{x}: %{y:.2f}%"
    )
    fig2.update_layout(
        xaxis_title="Age Group",
        yaxis_title="Default Rate (%)",
        height=380,
    )
    st.plotly_chart(fig2, use_container_width=True)

# -----------------------------------------------------------------------------
# Chart 3: Default Rate by Occupation
# -----------------------------------------------------------------------------
with row1_col3:
    st.subheader("3. Default Rate by Occupation")
    if "Occupation" in filtered_df.columns:
        occ_risk = (
            filtered_df.groupby("Occupation")["default_payment_next_month"]
            .mean()
            .reset_index()
        )
        occ_risk["Default Rate (%)"] = (
            occ_risk["default_payment_next_month"] * 100
        )
        occ_risk = occ_risk.sort_values(by="Default Rate (%)", ascending=True)

        fig3 = px.bar(
            occ_risk,
            y="Occupation",
            x="Default Rate (%)",
            orientation="h",
            color_discrete_sequence=["teal"],
        )
        fig3.update_traces(hovertemplate="%{y}: %{x:.2f}%")
        fig3.update_layout(
            yaxis_title="Occupation",
            xaxis_title="Default Rate (%)",
            height=380,
        )
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("Occupation feature is not present in dataset.")

row2_col1, row2_col2, row2_col3 = st.columns(3)

# -----------------------------------------------------------------------------
# Chart 4: Distribution of Missed Payments
# -----------------------------------------------------------------------------
with row2_col1:
    st.subheader("4. Missed Payments Count")
    if "Missed_Payments" in filtered_df.columns:
        missed_counts = (
            filtered_df["Missed_Payments"].value_counts().reset_index()
        )
        missed_counts.columns = ["Missed Payments", "Customer Count"]
        missed_counts = missed_counts.sort_values(by="Missed Payments")

        fig4 = px.bar(
            missed_counts,
            x="Missed Payments",
            y="Customer Count",
            color_discrete_sequence=["#87ceeb"],
        )
        fig4.update_traces(
            marker_line_color="black",
            marker_line_width=1,
            hovertemplate="Missed %{x} Payments: %{y:,} Customers",
        )
        fig4.update_layout(
            xaxis_title="Number of Missed Payments",
            yaxis_title="Customer Count",
            height=380,
        )
        st.plotly_chart(fig4, use_container_width=True)
    else:
        st.info("Missed_Payments column not found.")

# -----------------------------------------------------------------------------
# Chart 5: Feature Correlations
# -----------------------------------------------------------------------------
with row2_col2:
    st.subheader("5. Feature Correlations")
    numeric_df = filtered_df.select_dtypes(include=[np.number])
    if "default_payment_next_month" in numeric_df.columns:
        corr_with_target = numeric_df.corr()["default_payment_next_month"]
        corr_ranked = (
            corr_with_target.drop(
                ["default_payment_next_month", "Number_of_Defaults"],
                errors="ignore",
            )
            .sort_values(ascending=True)
            .reset_index()
        )
        corr_ranked.columns = ["Feature", "Correlation"]

        fig5 = px.bar(
            corr_ranked,
            y="Feature",
            x="Correlation",
            orientation="h",
            color_discrete_sequence=["teal"],
        )
        fig5.add_vline(x=0, line_dash="dash", line_color="grey")
        fig5.update_traces(hovertemplate="%{y}: %{x:.4f}")
        fig5.update_layout(
            xaxis_title="Correlation Coefficient",
            yaxis_title="Feature",
            height=380,
        )
        st.plotly_chart(fig5, use_container_width=True)

# -----------------------------------------------------------------------------
# Chart 6: Late Payment Distribution Trend
# -----------------------------------------------------------------------------
with row2_col3:
    st.subheader("6. Late Payment Count Trend")
    if "Late_Payment_Count" in filtered_df.columns:
        late_dist = (
            filtered_df["Late_Payment_Count"].value_counts().reset_index()
        )
        late_dist.columns = ["Late Payment Count", "Customer Count"]
        late_dist = late_dist.sort_values(by="Late Payment Count")

        fig6 = px.line(
            late_dist,
            x="Late Payment Count",
            y="Customer Count",
            markers=True,
            color_discrete_sequence=["coral"],
        )
        fig6.update_traces(
            line=dict(width=3),
            marker=dict(size=8),
            hovertemplate="%{x} Late Payments: %{y:,} Customers",
        )
        fig6.update_layout(
            xaxis_title="Late Payment Count",
            yaxis_title="Number of Customers",
            height=380,
        )
        st.plotly_chart(fig6, use_container_width=True)
    else:
        st.info("Late_Payment_Count column not found.")


# =============================================================================
# 6. RAW DATA & EXPLORATION TABLE
# =============================================================================
with st.expander("📄 View Filtered Portfolio Data Table"):
    st.dataframe(filtered_df, use_container_width=True)
