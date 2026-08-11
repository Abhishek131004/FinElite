import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ---------------------------------------------------------
# 1. PAGE CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(
    page_title="Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# 2. CUSTOM GLASSMORPHISM & GRADIENT STYLING (CSS)
# ---------------------------------------------------------
st.markdown("""
<style>
    /* Main Background Gradient */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
        color: #f8fafc;
        font-family: 'Inter', sans-serif;
    }

    /* Glassmorphism Containers */
    div[data-testid="stMetricValue"], 
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.04);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 18px 22px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }

    div[data-testid="stMetric"]:hover {
        transform: translateY(-3px);
        border-color: rgba(99, 102, 241, 0.4);
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: rgba(15, 23, 42, 0.75);
        backdrop-filter: blur(16px);
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }

    /* Custom Headers */
    .dashboard-header {
        font-size: 2.25rem;
        font-weight: 700;
        background: linear-gradient(90deg, #818cf8 0%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.25rem;
    }
    
    .dashboard-subtle {
        color: #94a3b8;
        font-size: 0.95rem;
        margin-bottom: 1.5rem;
    }

    /* Styled Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 10px;
        color: #94a3b8;
        border: 1px solid rgba(255, 255, 255, 0.05);
        padding: 8px 16px;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%) !important;
        color: #ffffff !important;
        border: none !important;
    }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# 3. MOCK DATA GENERATION (Replace with your actual dataset)
# ---------------------------------------------------------
@st.cache_data
def load_data():
    dates = pd.date_range(start="2026-01-01", periods=180, freq="D")
    categories = ["Tech", "Apparel", "Services", "Logistics"]
    data = []
    
    for date in dates:
        for cat in categories:
            revenue = np.random.randint(1000, 5000)
            conversion = round(np.random.uniform(1.5, 5.0), 2)
            users = np.random.randint(100, 1000)
            data.append([date, cat, revenue, conversion, users])
            
    df = pd.DataFrame(data, columns=["Date", "Category", "Revenue", "ConversionRate", "Users"])
    return df

df = load_data()


# ---------------------------------------------------------
# 4. SIDEBAR - INTERACTIVE FILTERS
# ---------------------------------------------------------
st.sidebar.markdown("### 🎛️ Control Panel")

# Date Filter
min_date, max_date = df["Date"].min().date(), df["Date"].max().date()
date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Multi-select Category Filter
all_categories = df["Category"].unique().tolist()
selected_categories = st.sidebar.multiselect(
    "Filter Categories",
    options=all_categories,
    default=all_categories
)

# Apply Filters
if len(date_range) == 2:
    start_d, end_d = date_range
    filtered_df = df[(df["Date"].dt.date >= start_d) & 
                     (df["Date"].dt.date <= end_d) & 
                     (df["Category"].isin(selected_categories))]
else:
    filtered_df = df[df["Category"].isin(selected_categories)]


# ---------------------------------------------------------
# 5. MAIN HEADER SECTION
# ---------------------------------------------------------
st.markdown('<div class="dashboard-header">Executive Performance Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="dashboard-subtle">Real-time metrics, interactive filtering, and exploratory analytics</div>', unsafe_allow_html=True)


# ---------------------------------------------------------
# 6. KPI METRICS CARDS
# ---------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)

total_revenue = filtered_df["Revenue"].sum()
total_users = filtered_df["Users"].sum()
avg_conversion = filtered_df["ConversionRate"].mean() if not filtered_df.empty else 0.0
avg_ticket = (total_revenue / total_users) if total_users > 0 else 0.0

col1.metric("Total Revenue", f"${total_revenue:,.0f}", delta="8.4%")
col2.metric("Active Users", f"{total_users:,.0f}", delta="12.1%")
col3.metric("Avg. Conversion", f"{avg_conversion:.2f}%", delta="-0.3%")
col4.metric("Avg. Ticket Size", f"${avg_ticket:.2f}", delta="4.2%")

st.markdown("<br>", unsafe_allow_html=True)


# ---------------------------------------------------------
# 7. INTERACTIVE VISUALIZATIONS (TABS)
# ---------------------------------------------------------
tab1, tab2 = st.tabs(["📈 Market Trends", "🔍 Data Explorer"])

with tab1:
    chart_col1, chart_col2 = st.columns([2, 1])

    with chart_col1:
        st.markdown("##### Revenue Performance Over Time")
        
        # Interactive Plotly Line Chart
        trend_data = filtered_df.groupby(["Date", "Category"])["Revenue"].sum().reset_index()
        fig_line = px.line(
            trend_data,
            x="Date",
            y="Revenue",
            color="Category",
            color_discrete_sequence=["#818cf8", "#c084fc", "#38bdf8", "#f43f5e"]
        )
        
        fig_line.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#94a3b8"),
            xaxis=dict(showgrid=False),
            yaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
            hovermode="x unified",
            margin=dict(l=20, r=20, t=30, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_line, use_container_width=True)

    with chart_col2:
        st.markdown("##### Category Revenue Share")
        
        # Interactive Plotly Donut Chart
        share_data = filtered_df.groupby("Category")["Revenue"].sum().reset_index()
        fig_donut = px.pie(
            share_data,
            values="Revenue",
            names="Category",
            hole=0.6,
            color_discrete_sequence=["#818cf8", "#c084fc", "#38bdf8", "#f43f5e"]
        )
        
        fig_donut.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#94a3b8"),
            margin=dict(l=20, r=20, t=30, b=20),
            showlegend=False
        )
        fig_donut.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_donut, use_container_width=True)

with tab2:
    st.markdown("##### Detailed Dataset Inspection")
    
    # Dynamic Dataframe Display with Download Action
    st.dataframe(
        filtered_df,
        use_container_width=True,
        column_config={
            "Revenue": st.column_config.NumberColumn(format="$%d"),
            "ConversionRate": st.column_config.NumberColumn(format="%.2f%%"),
            "Date": st.column_config.DateColumn(format="YYYY-MM-DD")
        }
    )
    
    # Download Button
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Export Filtered Data as CSV",
        data=csv,
        file_name="filtered_analytics_data.csv",
        mime="text/csv",
    )
