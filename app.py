import os
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# =============================================================================
# 1. PAGE CONFIGURATION & CUSTOM CLASSY UI
# =============================================================================
st.set_page_config(
    page_title="Risk Analytics & Simulation Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling: Animated Modern Gradient Background, Glassmorphism, and Cards
st.markdown(
    """
    <style>
    /* Animated Gradient Background */
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
        font-size: 0.85rem;
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
    .badge-warning { background-color: rgba(245, 158, 11, 0.2); color: #fbbf24; }

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

    /* Alert Banner Style */
    .alert-box {
        background: rgba(239, 68, 68, 0.15);
        border: 1px solid rgba(239, 68, 68, 0.4);
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 20px;
        color: #fca5a5;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""",
    unsafe_allow_html=True,
)


# =============================================================================
# 2. DATA LOADING & PREPARATION
# =============================================================================
@st.cache_data
def load_and_preprocess_data():
    file_path = "../DataSets/Credir_Card_Bank.xlsx"

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
    st.error(f"❌ Failed to load dataset. Error: {e}")
    st.stop()


# =============================================================================
# 3. SIDEBAR FILTERS & INTERACTIVE SIMULATOR
# =============================================================================
st.sidebar.markdown("### 🎛️ Dashboard Controls")
st.sidebar.markdown("---")

# Filter 1: Risk Category
risk_options = df["High_Risk_Flag"].unique().tolist()
selected_risk = st.sidebar.multiselect(
    "Risk Profile", options=risk_options, default=risk_options
)

# Filter 2: Age Group
age_options = [str(x) for x in df["Age_Group"].cat.categories.tolist()]
selected_age_groups = st.sidebar.multiselect(
    "Age Groups", options=age_options, default=age_options
)

# Filter 3: Threshold Sliders
st.sidebar.markdown("---")
st.sidebar.markdown("### ⚙️ Threshold Controls")
credit_score_min = st.sidebar.slider(
    "Min Credit Score",
    min_value=int(df["Credit_Score"].min()),
    max_value=int(df["Credit_Score"].max()),
    value=int(df["Credit_Score"].min()),
)

utilization_max = st.sidebar.slider(
    "Max Credit Utilization (%)",
    min_value=0,
    max_value=100,
    value=100,
)

# Filter Application
filtered_df = df[
    (df["High_Risk_Flag"].isin(selected_risk))
    & (df["Age_Group"].astype(str).isin(selected_age_groups))
    & (filtered_df_score := df["Credit_Score"] >= credit_score_min)
    & (df["Credit_Utilization"] <= utilization_max)
]

# -----------------------------------------------------------------------------
# SIDEBAR: WHAT-IF RISK CALCULATOR (COOL ADDITION #1)
# -----------------------------------------------------------------------------
st.sidebar.markdown("---")
st.sidebar.markdown("### 🔮 Real-Time Risk Simulator")
st.sidebar.caption("Input applicant parameters to assess risk:")

sim_score = st.sidebar.slider("Credit Score", 300, 850, 580)
sim_util = st.sidebar.slider("Credit Utilization (%)", 0, 100, 80)
sim_missed = st.sidebar.slider("Missed Payments Count", 0, 10, 3)

# Calculate simulated risk
is_sim_high_risk = (sim_score < 600) or (sim_util > 75) or (sim_missed >= 3)
sim_score_val = (
    (850 - sim_score) * 0.4 + (sim_util * 0.4) + (sim_missed * 10)
)
sim_score_val = min(100, max(0, sim_score_val))

if is_sim_high_risk:
    st.sidebar.error(f"⚠️ **HIGH RISK APPLICANT**\n\nRisk Score: {sim_score_val:.1f}/100")
else:
    st.sidebar.success(f"✅ **LOW/STANDARD RISK**\n\nRisk Score: {sim_score_val:.1f}/100")


# =============================================================================
# 4. DASHBOARD HEADER & KPI CARDS
# =============================================================================
st.markdown('<div class="header-title">Risk Analytics & Decision Intelligence</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="header-subtitle">Real-time risk monitoring, credit profiling, and multi-dimensional default drivers analysis.</div>',
    unsafe_allow_html=True,
)

# Anomaly Alert Box (COOL ADDITION #2)
extreme_outliers = filtered_df[
    (filtered_df["Credit_Score"] < 580) & (filtered_df["Credit_Utilization"] > 80)
]
if not extreme_outliers.empty:
    st.markdown(
        f"""
        <div class="alert-box">
            🚨 <b>CRITICAL RISK ALERT:</b> Found <b>{len(extreme_outliers)} customers</b> with extreme risk signals 
            (Credit Score < 580 and Utilization > 80%). Immediate audit recommended!
        </div>
    """,
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
        f"""<div class="kpi-card"><div class="kpi-title">Total Portfolio</div><div class="kpi-value">{total_cust:,}</div><div class="kpi-badge badge-info">Active Customers</div></div>""",
        unsafe_allow_html=True,
    )

with kpi2:
    st.markdown(
        f"""<div class="kpi-card"><div class="kpi-title">Total Defaulters</div><div class="kpi-value">{total_defaults:,}</div><div class="kpi-badge badge-danger">Class Flag = 1</div></div>""",
        unsafe_allow_html=True,
    )

with kpi3:
    st.markdown(
        f"""<div class="kpi-card"><div class="kpi-title">Default Rate</div><div class="kpi-value">{overall_default_rate:.2f}%</div><div class="kpi-badge badge-danger">Portfolio Avg</div></div>""",
        unsafe_allow_html=True,
    )

with kpi4:
    st.markdown(
        f"""<div class="kpi-card"><div class="kpi-title">Avg Late Payments</div><div class="kpi-value">{avg_late:.2f}</div><div class="kpi-badge badge-warning">Delinquency Count</div></div>""",
        unsafe_allow_html=True,
    )

with kpi5:
    st.markdown(
        f"""<div class="kpi-card"><div class="kpi-title">High Risk Segment</div><div class="kpi-value">{high_risk_count:,}</div><div class="kpi-badge badge-danger">{(high_risk_count/max(1, total_cust)*100):.1f}% Exposure</div></div>""",
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)


# =============================================================================
# 5. VISUALIZATIONS (PLOTLY GRID + BUBBLE CHART)
# =============================================================================
PLOTLY_THEME = "plotly_dark"
COLOR_ACCENT = "#38bdf8"
COLOR_DANGER = "#f87171"
COLOR_TEAL = "#2dd4bf"
COLOR_PURPLE = "#c084fc"

# Row 1 Charts
r1_col1, r1_col2, r1_col3 = st.columns(3)

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
        st.info("Occupation field unavailable.")
    st.markdown("</div>", unsafe_allow_html=True)

# Row 2 Charts
r2_col1, r2_col2 = st.columns([1, 2])

# COOL ADDITION #3: Interactive Multi-Dimensional Risk Scatter Plot
with r2_col1:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.subheader("4. Risk Correlations")
    numeric_df = filtered_df.select_dtypes(include=[np.number])
    if "default_payment_next_month" in numeric_df.columns and len(filtered_df) > 1:
        corr_ranked = (
            numeric_df.corr()["default_payment_next_month"]
            .drop(["default_payment_next_month", "Number_of_Defaults"], errors="ignore")
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
            height=360,
        )
        st.plotly_chart(fig5, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with r2_col2:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.subheader("5. Credit Utilization Distribution by Default Status")
    
    if not filtered_df.empty:
        filtered_df["Status_Label"] = filtered_df["default_payment_next_month"].map(
            {0: "Non-Defaulters (0)", 1: "Defaulters (1)"}
        )
        fig_box = px.box(
            filtered_df,
            x="Status_Label",
            y="Credit_Utilization",
            color="Status_Label",
            points="outliers",
            color_discrete_map={
                "Non-Defaulters (0)": "#38bdf8",
                "Defaulters (1)": "#f87171",
            },
            template=PLOTLY_THEME,
        )
        fig_box.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=30, b=10),
            height=360,
            showlegend=False,
            xaxis_title="Default Status",
            yaxis_title="Credit Utilization (%)",
        )
        st.plotly_chart(fig_box, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
