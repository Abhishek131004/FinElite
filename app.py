import os
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# =============================================================================
# 1. PAGE CONFIGURATION & CUSTOM CLASSY UI (GRADIENT & GLASSMORPHISM)
# =============================================================================
st.set_page_config(
    page_title="Risk Analytics Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling: Animated Modern Gradient Background, Glassmorphism, and Cards
st.markdown(
    """
    <style>
    /* Animated Gradient Background for Main Page */
    .stApp {
        background: linear-gradient(-45deg, #0f172a, #1e1b4b, #111827, #0f172a);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
        color: #f3f4f6;
    }

    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* Sidebar Customization */
    section[data-testid="stSidebar"] {
        background: rgba(15, 23, 42, 0.85) !important;
        backdrop-filter: blur(12px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* Glassmorphism KPI Container */
    .kpi-card {
        background: rgba(30, 41, 59, 0.65);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .kpi-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 24px rgba(0, 0, 0, 0.4);
        border: 1px solid rgba(99, 102, 241, 0.4);
    }

    .kpi-title {
        font-size: 0.9rem;
        font-weight: 500;
        color: #9ca3af;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .kpi-value {
        font-size: 2rem;
        font-weight: 700;
        margin-top: 8px;
        background: linear-gradient(135deg, #60a5fa, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .kpi-badge {
        font-size: 0.8rem;
        padding: 4px 8px;
        border-radius: 12px;
        margin-top: 8px;
        display: inline-block;
    }

    .badge-danger { background-color: rgba(239, 68, 68, 0.2); color: #f87171; }
    .badge-info { background-color: rgba(59, 130, 246, 0.2); color: #60a5fa; }

    /* Chart Container Cards */
    .chart-container {
        background: rgba(30, 41, 59, 0.5);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 16px;
        margin-bottom: 20px;
    }

    /* Custom Header Styling */
    .header-title {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #38bdf8, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }

    .header-subtitle {
        font-size: 1rem;
        color: #94a3b8;
        margin-bottom: 25px;
    }

    /* Hide Default Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""",
    unsafe_allow_html=True,
)


# =============================================================================
# 2. DATA LOADING & PREPARATION (CACHED)
# =============================================================================
@st.cache_data
def load_and_preprocess_data():
    file_path = "../DataSets/Credir_Card_Bank.xlsx"

    # Fallback to current folder if relative path fails
    if not os.path.exists(file_path):
        file_path = "Credir_Card_Bank.xlsx"

    df = pd.read_excel(file_path)

    # 1. Target Variable Definition
    df["default_payment_next_month"] = (df["Number_of_Defaults"] > 0).astype(int)

    # 2. Age Binning
    df["Age_Group"] = pd.cut(
        df["Age"],
        bins=[18, 25, 35, 50, 65, 100],
        labels=["18-25", "26-35", "36-50", "51-65", "65+"],
    )

    # 3. High Risk Condition Logic
    high_risk_condition = (
        (df["Credit_Score"] < 600)
        | (df["Credit_Utilization"] > 75)
        | (df["Missed_Payments"] >= 3)
    )
    df["High_Risk_Flag"] = np.where(high_risk_condition, "High Risk", "Standard")

    return df


try:
    df = load_and_preprocess_data()
except Exception as e:
    st.error(
        f"❌ Failed to load dataset! Please verify `Credir_Card_Bank.xlsx` exists in `../DataSets/` or the root folder.\n\nError: {e}"
    )
    st.stop()


# =============================================================================
# 3. SIDEBAR FILTERS & CONTROLS
# =============================================================================
st.sidebar.markdown("### 🎛️ Control Panel")
st.sidebar.markdown("---")

# Filter 1: High-Risk Flag
risk_options = df["High_Risk_Flag"].unique().tolist()
selected_risk = st.sidebar.multiselect(
    "Risk Profile", options=risk_options, default=risk_options
)

# Filter 2: Age Group
age_options = [str(x) for x in df["Age_Group"].cat.categories.tolist()]
selected_age_groups = st.sidebar.multiselect(
    "Age Group Bins", options=age_options, default=age_options
)

# Filter 3: Occupation (if exists)
if "Occupation" in df.columns:
    occ_options = df["Occupation"].dropna().unique().tolist()
    selected_occ = st.sidebar.multiselect(
        "Occupation Category", options=occ_options, default=occ_options
    )
else:
    selected_occ = None

# Filter 4: Interactive Threshold Sliders
st.sidebar.markdown("---")
st.sidebar.markdown("### ⚙️ Risk Threshold Overrides")
credit_score_min = st.sidebar.slider(
    "Credit Score Cutoff",
    min_value=int(df["Credit_Score"].min()),
    max_value=int(df["Credit_Score"].max()),
    value=600,
)

utilization_max = st.sidebar.slider(
    "Max Credit Utilization (%)",
    min_value=0,
    max_value=100,
    value=75,
)

# Apply All Filters Dynamically
filtered_df = df[
    (df["High_Risk_Flag"].isin(selected_risk))
    & (df["Age_Group"].astype(str).isin(selected_age_groups))
]

if selected_occ and "Occupation" in filtered_df.columns:
    filtered_df = filtered_df[filtered_df["Occupation"].isin(selected_occ)]

# Re-apply threshold slider logic dynamically for filtering
filtered_df = filtered_df[
    (filtered_df["Credit_Score"] >= credit_score_min)
    & (filtered_df["Credit_Utilization"] <= utilization_max)
]


# =============================================================================
# 4. DASHBOARD HEADER & EXECUTIVE METRICS
# =============================================================================
st.markdown('<div class="header-title">Risk Analytics & Default Dashboard</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="header-subtitle">Real-time risk monitoring, credit profiling, and multi-dimensional default drivers analysis.</div>',
    unsafe_allow_html=True,
)

# Executive KPI Cards Row
kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

total_cust = len(filtered_df)
total_defaults = filtered_df["default_payment_next_month"].sum()
overall_default_rate = (total_defaults / total_cust * 100) if total_cust > 0 else 0
avg_late = filtered_df["Late_Payment_Count"].mean() if "Late_Payment_Count" in filtered_df.columns else 0
high_risk_count = (filtered_df["High_Risk_Flag"] == "High Risk").sum()

with kpi1:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Total Portfolio</div>
            <div class="kpi-value">{total_cust:,}</div>
            <div class="kpi-badge badge-info">Filtered Subset</div>
        </div>
    """,
        unsafe_allow_html=True,
    )

with kpi2:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Total Defaulters</div>
            <div class="kpi-value">{total_defaults:,}</div>
            <div class="kpi-badge badge-danger">Class Flag = 1</div>
        </div>
    """,
        unsafe_allow_html=True,
    )

with kpi3:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Default Rate</div>
            <div class="kpi-value">{overall_default_rate:.2f}%</div>
            <div class="kpi-badge badge-danger">Average Benchmark</div>
        </div>
    """,
        unsafe_allow_html=True,
    )

with kpi4:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Avg Late Payments</div>
            <div class="kpi-value">{avg_late:.2f}</div>
            <div class="kpi-badge badge-info">Per Customer</div>
        </div>
    """,
        unsafe_allow_html=True,
    )

with kpi5:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">High Risk Segment</div>
            <div class="kpi-value">{high_risk_count:,}</div>
            <div class="kpi-badge badge-danger">{(high_risk_count/total_cust*100):.1f}% Exposure</div>
        </div>
    """,
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)


# =============================================================================
# 5. INTERACTIVE PLOTLY VISUALIZATIONS (GRID LAYOUT)
# =============================================================================
# Universal Plotly Dark/Neon Transparent Theme Settings
PLOTLY_THEME = "plotly_dark"
COLOR_ACCENT = "#38bdf8"
COLOR_DANGER = "#f87171"
COLOR_TEAL = "#2dd4bf"
COLOR_PURPLE = "#c084fc"

r1_col1, r1_col2, r1_col3 = st.columns(3)

# -----------------------------------------------------------------------------
# Subplot 1: Overall Default Distribution
# -----------------------------------------------------------------------------
with r1_col1:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.subheader("1. Default Class Distribution (%)")
    
    default_counts = (
        filtered_df["default_payment_next_month"]
        .value_counts(normalize=True)
        .reset_index()
    )
    default_counts.columns = ["Status", "Percentage"]
    default_counts["Percentage"] *= 100
    default_counts["Status_Label"] = default_counts["Status"].map(
        {0: "Non-Defaulters (0)", 1: "Defaulters (1)"}
    )

    fig1 = px.bar(
        default_counts,
        x="Status_Label",
        y="Percentage",
        text=default_counts["Percentage"].apply(lambda x: f"{x:.2f}%"),
        color="Status_Label",
        color_discrete_map={
            "Non-Defaulters (0)": COLOR_ACCENT,
            "Defaulters (1)": COLOR_DANGER,
        },
        template=PLOTLY_THEME,
    )
    fig1.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        margin=dict(l=10, r=10, t=30, b=10),
        height=320,
    )
    st.plotly_chart(fig1, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Subplot 2: Default Rate (%) Across Age Groups
# -----------------------------------------------------------------------------
with r1_col2:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.subheader("2. Default Rate by Age Group")

    risk_age = (
        filtered_df.groupby("Age_Group", observed=False)["default_payment_next_month"]
        .mean()
        .reset_index()
    )
    risk_age["Default Rate (%)"] = risk_age["default_payment_next_month"] * 100

    fig2 = px.bar(
        risk_age,
        x="Age_Group",
        y="Default Rate (%)",
        text=risk_age["Default Rate (%)"].apply(lambda x: f"{x:.2f}%"),
        color_discrete_sequence=[COLOR_TEAL],
        template=PLOTLY_THEME,
    )
    fig2.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=30, b=10),
        height=320,
    )
    st.plotly_chart(fig2, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Subplot 3: Default Rate (%) Across Occupations
# -----------------------------------------------------------------------------
with r1_col3:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.subheader("3. Default Rate by Occupation")

    if "Occupation" in filtered_df.columns and not filtered_df.empty:
        occ_risk = (
            filtered_df.groupby("Occupation")["default_payment_next_month"]
            .mean()
            .reset_index()
        )
        occ_risk["Default Rate (%)"] = occ_risk["default_payment_next_month"] * 100
        occ_risk = occ_risk.sort_values(by="Default Rate (%)", ascending=True)

        fig3 = px.bar(
            occ_risk,
            y="Occupation",
            x="Default Rate (%)",
            orientation="h",
            text=occ_risk["Default Rate (%)"].apply(lambda x: f"{x:.2f}%"),
            color_discrete_sequence=[COLOR_PURPLE],
            template=PLOTLY_THEME,
        )
        fig3.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=30, b=10),
            height=320,
        )
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("Occupation field unavailable or empty in current filter selection.")
    st.markdown("</div>", unsafe_allow_html=True)


r2_col1, r2_col2, r2_col3 = st.columns(3)

# -----------------------------------------------------------------------------
# Subplot 4: Distribution of Missed Payments per Customer
# -----------------------------------------------------------------------------
with r2_col1:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.subheader("4. Missed Payments Volume")

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
            color_discrete_sequence=["#38bdf8"],
            template=PLOTLY_THEME,
        )
        fig4.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=30, b=10),
            height=320,
        )
        st.plotly_chart(fig4, use_container_width=True)
    else:
        st.info("Missed_Payments attribute unavailable.")
    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Subplot 5: Feature Correlations with Default Status
# -----------------------------------------------------------------------------
with r2_col2:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.subheader("5. Default Correlation Rankings")

    numeric_df = filtered_df.select_dtypes(include=[np.number])
    if "default_payment_next_month" in numeric_df.columns and len(filtered_df) > 1:
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
            color="Correlation",
            color_continuous_scale="rdbu_r",
            template=PLOTLY_THEME,
        )
        fig5.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            coloraxis_showscale=False,
            margin=dict(l=10, r=10, t=30, b=10),
            height=320,
        )
        st.plotly_chart(fig5, use_container_width=True)
    else:
        st.info("Insufficient numeric variance to calculate correlations.")
    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Subplot 6: Late Payment Count Distribution Trend
# -----------------------------------------------------------------------------
with r2_col3:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.subheader("6. Late Payment Distribution Trend")

    if "Late_Payment_Count" in filtered_df.columns:
        late_payment_dist = (
            filtered_df["Late_Payment_Count"].value_counts().reset_index()
        )
        late_payment_dist.columns = ["Late Payment Count", "Customer Count"]
        late_payment_dist = late_payment_dist.sort_values(by="Late Payment Count")

        fig6 = px.line(
            late_payment_dist,
            x="Late Payment Count",
            y="Customer Count",
            markers=True,
            line_shape="spline",
            color_discrete_sequence=["#fb923c"],
            template=PLOTLY_THEME,
        )
        fig6.update_traces(line=dict(width=3), marker=dict(size=8))
        fig6.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=30, b=10),
            height=320,
        )
        st.plotly_chart(fig6, use_container_width=True)
    else:
        st.info("Late_Payment_Count attribute unavailable.")
    st.markdown("</div>", unsafe_allow_html=True)


# =============================================================================
# 6. FILTERED DATASET INSPECTION & DOWNLOAD
# =============================================================================
st.markdown("<br>", unsafe_allow_html=True)

with st.expander("📋 View & Export Filtered Portfolio Data"):
    st.markdown("#### High-Risk Filtered Customer Table")
    st.dataframe(filtered_df, use_container_width=True)

    # Download Filtered Dataset
    csv_bytes = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Filtered Data as CSV",
        data=csv_bytes,
        file_name="risk_analytics_filtered_data.csv",
        mime="text/csv",
    )
