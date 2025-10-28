import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# ----------------------------
# PAGE CONFIG
# ----------------------------
st.set_page_config(
    page_title="Customer Intelligence Dashboard",
    page_icon="📊",
    layout="wide"
)

# ----------------------------
# LOAD DATA
# ----------------------------
@st.cache_data
def load_data():
    df = pd.read_excel("ML_Testing.xlsx")
    df['Date'] = pd.to_datetime(df['Date'])
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.month_name()
    df['Day_Name'] = df['Date'].dt.day_name()
    return df

df = load_data()

# ----------------------------
# SIDEBAR FILTERS
# ----------------------------
st.sidebar.header("🔍 Filter Data")
selected_year = st.sidebar.multiselect(
    "Select Year:",
    options=sorted(df["Year"].unique()),
    default=sorted(df["Year"].unique())
)
selected_segment = st.sidebar.multiselect(
    "Select Customer Segment:",
    options=df["customer_segment"].unique(),
    default=df["customer_segment"].unique()[:3]
)
selected_industry = st.sidebar.multiselect(
    "Select Industry Type:",
    options=df["businessindustrytype"].unique(),
    default=df["businessindustrytype"].unique()[:5]
)

# Apply filters dynamically
filtered_df = df.query("Year == @selected_year and customer_segment == @selected_segment and businessindustrytype == @selected_industry")

# ----------------------------
# DASHBOARD HEADER
# ----------------------------
st.title("📊 Customer Intelligence Dashboard")
st.markdown("Analyze customer behavior, spending trends, and segment performance interactively.")

# ----------------------------
# KPI METRICS
# ----------------------------
total_sales = filtered_df["Amount"].sum()
total_customers = filtered_df["customer_segment"].nunique()
avg_transaction = filtered_df["Amount"].mean()

col1, col2, col3 = st.columns(3)
col1.metric("💰 Total Revenue", f"${total_sales:,.0f}")
col2.metric("👥 Active Segments", f"{total_customers}")
col3.metric("🧾 Avg Transaction", f"${avg_transaction:,.2f}")

# ----------------------------
# VISUALIZATIONS
# ----------------------------

# 1️⃣ Sales by Customer Segment
sales_by_segment = filtered_df.groupby("customer_segment")["Amount"].sum().reset_index()
fig_segment = px.bar(
    sales_by_segment,
    x="customer_segment",
    y="Amount",
    color="customer_segment",
    title="Revenue by Customer Segment",
    text_auto=".2s"
)

# 2️⃣ Sales by Day Name
sales_by_day = filtered_df.groupby("Day_Name")["Amount"].sum().reset_index()
day_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
sales_by_day["Day_Name"] = pd.Categorical(sales_by_day["Day_Name"], categories=day_order, ordered=True)
sales_by_day = sales_by_day.sort_values("Day_Name")
fig_day = px.line(
    sales_by_day,
    x="Day_Name",
    y="Amount",
    title="Weekly Sales Pattern"
)

# 3️⃣ Industry Contribution
industry_sales = filtered_df.groupby("businessindustrytype")["Amount"].sum().reset_index()
fig_industry = px.pie(
    industry_sales,
    values="Amount",
    names="businessindustrytype",
    title="Revenue Share by Industry"
)

a, b, c = st.columns(3)
a.plotly_chart(fig_segment, use_container_width=True)
b.plotly_chart(fig_day, use_container_width=True)
c.plotly_chart(fig_industry, use_container_width=True)

# ----------------------------
# DYNAMIC DATA TABLE
# ----------------------------
st.subheader("📋 Dynamic Data Table")
st.caption("This table updates automatically based on your selected filters.")

st.dataframe(
    filtered_df[["Date", "customer_segment", "businessindustrytype", "Amount", "Year", "Month"]],
    use_container_width=True
)

# ----------------------------
# BONUS: Monthly Trend
# ----------------------------
monthly_trend = filtered_df.groupby("Month")["Amount"].sum().reset_index()
month_order = [
    "January","February","March","April","May","June",
    "July","August","September","October","November","December"
]
monthly_trend["Month"] = pd.Categorical(monthly_trend["Month"], categories=month_order, ordered=True)
monthly_trend = monthly_trend.sort_values("Month")

fig_month = px.area(
    monthly_trend,
    x="Month",
    y="Amount",
    title="Monthly Revenue Trend",
    line_group=None,
    markers=True
)
st.plotly_chart(fig_month, use_container_width=True)

# ----------------------------
# INSIGHT SECTION
# ----------------------------
st.markdown("### 💡 Insight Summary")
st.write(f"""
- **Total revenue:** ${total_sales:,.0f} across {len(selected_year)} year(s).
- **Top-performing segment:** {sales_by_segment.sort_values('Amount', ascending=False).iloc[0,0]}.
- **Most active day:** {sales_by_day.sort_values('Amount', ascending=False).iloc[0,0]}.
- **Leading industry:** {industry_sales.sort_values('Amount', ascending=False).iloc[0,0]}.
""")
