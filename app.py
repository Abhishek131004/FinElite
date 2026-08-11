import os
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# =============================================================================
# 1. PAGE CONFIG & HIGH-CONTRAST VISIBILITY CSS
# =============================================================================
st.set_page_config(
    page_title="Risk Analytics Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS fixing text contrast for Sidebar, Labels, and Headers
st.markdown(
    """
    <style>
    /* Dark Background */
    .stApp {
        background-color: #0d1117;
        color: #f0f6fc;
    }

    /* Sidebar Background & Explicit White Text Fix */
    section[data-testid="stSidebar"] {
        background-color: #161b22 !important;
        border-right: 1px solid #30363d;
    }
    
    /* Force all Sidebar text, labels, headers, and markdown to be crisp white/light grey */
    section[data-testid="stSidebar"] * {
        color: #e6edf3 !important;
    }

    /* Fix Slider Text Labels specifically */
    div[data-baseweb="slider"] * {
        color: #f0f6fc !important;
    }

    /* KPI Cards */
    .kpi-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 18px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }

    .kpi-title {
        font-size: 0.85rem;
        font-weight: 600;
        color: #8b949e !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .kpi-value {
        font-size: 2.2rem;
        font-weight: 700;
        margin-top: 6px;
        color: #58a6ff !important;
    }

    .kpi-badge {
        font-size: 0.75rem;
        padding: 3px 8px;
        border-radius: 10px;
        margin-top: 6px;
        display: inline-block;
    }

    .badge-danger { background-color: rgba(248, 81, 73, 0.2); color: #ff7b72 !important; }
    .badge-info { background-color: rgba(56, 139, 253, 0.2); color: #58a6ff !important; }

    /* Chart Container Cards */
    .chart-container {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 20px;
    }

    /* Headers */
    .header-title {
        font-size: 2.4rem;
        font-weight: 800;
        color: #58a6ff;
        margin-bottom: 0px;
    }

    .header-subtitle {
        font-size: 1rem;
        color: #8b949e;
        margin-bottom: 20px;
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
# 3. SIDEBAR FILTERS WITH CORRECT DEFAULTS
# =============================================================================
st.sidebar.markdown("## 🎛️ Dashboard Controls")
st.sidebar.markdown("---")

# Filter 1: Risk Category
risk_options = df["High_Risk_Flag"].unique().tolist()
selected_risk = st.sidebar.multiselect(
    "Risk Profile Filter", options=risk_options, default=risk_options
)

# Filter 2: Age Group
age_options = [str(x) for x in df["Age_Group"].cat.categories.tolist()]
selected_age_groups = st.sidebar.multiselect(
    "Age Group Bins", options=age_options, default=age_options
)

# Filter 3: Sliders defaulted to FULL RANGE so data isn't hidden by default
st.sidebar.markdown("---")
st.sidebar.markdown("### ⚙️ Threshold Overrides")
credit_score_min = st.sidebar.slider(
    "Min Credit Score Cutoff",
    min_value=int(df["Credit_Score"].min()),
    max_value=int(df["Credit_Score"].max()),
    value=int(df["Credit_Score"].min()),  # Start at minimum to show ALL data
)

utilization_max = st.sidebar.slider(
    "Max Credit Utilization Cutoff (%)",
    min_value=0,
    max_value=100,
    value=100,  # Start at 100% to show ALL data
)

# Apply Filters
filtered_df = df[
    (df["High_Risk_Flag"].isin(selected_risk))
    & (df["Age_Group"].astype(str).isin(selected_age_groups))
    & (df["Credit_Score"] >= credit_score_min)
    & (df["Credit_Utilization"] <= utilization_max)
]

# Real-time Risk Simulator
st.sidebar.markdown("---")
st.sidebar.markdown("### 🔮 Real-Time Risk Simulator")
sim_score = st.sidebar.slider("Applicant Credit Score", 300, 850, 580)
sim_util = st.sidebar.slider("Credit Utilization (%)", 0, 100, 80)
sim_missed = st.sidebar.slider("Missed Payments Count", 0, 10, 3)

is_sim_high_risk = (sim_score < 600) or (sim_util > 75) or (sim_missed >= 3)
sim_score_val = min(100, max(0, (850 - sim_score) * 0.4 + (sim_util * 0.4) + (sim_missed * 10)))

if is_sim_high_risk:
    st.sidebar.error(f"⚠️ **HIGH RISK APPLICANT**\n\nCalculated Risk: {sim_score_val:.1f}/100")
else:
    st.sidebar.success(f"✅ **STANDARD RISK APPLICANT**\n\nCalculated Risk: {sim_score_val:.1f}/100")


# =============================================================================
# 4. DASHBOARD HEADER & KPI CARDS
# =============================================================================
st.markdown('<div class="header-title">Risk Analytics & Decision Intelligence</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="header-subtitle">Real-time risk monitoring, credit profiling, and multi-dimensional default drivers analysis.</div>',
    unsafe_allow_html=True,
)

# Executive KPI Row
kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

total_cust = len(filtered_df)
total_defaults = filtered_df["default_payment_next_month"].sum()
overall_default_rate = (total_defaults / total_cust * 100) if total_cust > 0 else 0
avg_late = filtered_df["Late_Payment_Count"].mean() if "Late_Payment_Count" in filtered_df.columns and total_cust > 0 else 0
high_risk_count = (filtered_df["High_Risk_Flag"] == "High Risk").sum()

with kpi1:
    st.markdown(
        f"""<div class="kpi-card"><div class="kpi-title">Total Portfolio</div><div class="kpi-value">{total_cust:,}</div><div class="kpi-badge badge-info">Filtered Subset</div></div>""",
        unsafe_allow_html=True,
    )

with kpi2:
    st.markdown(
        f"""<div class="kpi-card"><div class="kpi-title">Total Defaulters</div><div class="kpi-value">{total_defaults:,}</div><div class="kpi-badge badge-danger">Class Flag = 1</div></div>""",
        unsafe_allow_html=True,
    )

with kpi3:
    st.markdown(
        f"""<div class="kpi-card"><div class="kpi-title">Default Rate</div><div class="kpi-value">{overall_default_rate:.2f}%</div><div class="kpi-badge badge-danger">Portfolio Rate</div></div>""",
        unsafe_allow_html=True,
    )

with kpi4:
    st.markdown(
        f"""<div class="kpi-card"><div class="kpi-title">Avg Late Payments</div><div class="kpi-value">{avg_late:.2f}</div><div class="kpi-badge badge-info">Per Customer</div></div>""",
        unsafe_allow_html=True,
    )

with kpi5:
    st.markdown(
        f"""<div class="kpi-card"><div class="kpi-title">High Risk Segment</div><div class="kpi-value">{high_risk_count:,}</div><div class="kpi-badge badge-danger">{(high_risk_count/max(1, total_cust)*100):.1f}% Exposure</div></div>""",
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)


# =============================================================================
# 5. VISUALIZATIONS (PLOTLY CHARTS WITH EXPLICIT FONT COLORS)
# =============================================================================
PLOTLY_THEME = "plotly_dark"

r1_col1, r1_col2, r1_col3 = st.columns(3)

# -----------------------------------------------------------------------------
# Chart 1: Default Class Distribution
# -----------------------------------------------------------------------------
with r1_col1:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.subheader("1. Default Class Distribution (%)")
    
    if total_cust > 0:
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
                "Non-Defaulters (0)": "#38bdf8",
                "Defaulters (1)": "#f87171",
            },
            template=PLOTLY_THEME,
        )
        fig1.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e6edf3"),
            showlegend=False,
            margin=dict(l=10, r=10, t=30, b=10),
            height=320,
        )
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.warning("No data match the current filter selection.")
    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Chart 2: Default Rate (%) Across Age Groups
# -----------------------------------------------------------------------------
with r1_col2:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.subheader("2. Default Rate by Age Group")

    if total_cust > 0:
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
            color_discrete_sequence=["#2dd4bf"],
            template=PLOTLY_THEME,
        )
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e6edf3"),
            margin=dict(l=10, r=10, t=30, b=10),
            height=320,
        )
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.warning("No data match the current filter selection.")
    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Chart 3: Default Rate (%) Across Occupations
# -----------------------------------------------------------------------------
with r1_col3:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.subheader("3. Default Rate by Occupation")

    if "Occupation" in filtered_df.columns and total_cust > 0:
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
            color_discrete_sequence=["#c084fc"],
            template=PLOTLY_THEME,
        )
        fig3.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e6edf3"),
            margin=dict(l=10, r=10, t=30, b=10),
            height=320,
        )
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.warning("No data match the current filter selection.")
    st.markdown("</div>", unsafe_allow_html=True)


r2_col1, r2_col2 = st.columns([1, 1])

# -----------------------------------------------------------------------------
# Chart 4: Feature Correlations
# -----------------------------------------------------------------------------
with r2_col1:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.subheader("4. Risk Feature Correlations")

    numeric_df = filtered_df.select_dtypes(include=[np.number])
    if "default_payment_next_month" in numeric_df.columns and total_cust > 5:
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
            font=dict(color="#e6edf3"),
            coloraxis_showscale=False,
            margin=dict(l=10, r=10, t=30, b=10),
            height=360,
        )
        st.plotly_chart(fig5, use_container_width=True)
    else:
        st.info("Insufficient variance or data to compute correlation.")
    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Chart 5: Credit Utilization Boxplot by Default Status
# -----------------------------------------------------------------------------
with r2_col2:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.subheader("5. Credit Utilization by Default Status")

    if total_cust > 0:
        filtered_df_copy = filtered_df.copy()
        filtered_df_copy["Status_Label"] = filtered_df_copy[
            "default_payment_next_month"
        ].map({0: "Non-Defaulters (0)", 1: "Defaulters (1)"})

        fig_box = px.box(
            filtered_df_copy,
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
            font=dict(color="#e6edf3"),
            margin=dict(l=10, r=10, t=30, b=10),
            height=360,
            showlegend=False,
            xaxis_title="Default Status",
            yaxis_title="Credit Utilization (%)",
        )
        st.plotly_chart(fig_box, use_container_width=True)
    else:
        st.warning("No data match the current filter selection.")
    st.markdown("</div>", unsafe_allow_html=True)
