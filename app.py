
import streamlit as st
import pandas as pd
import plotly.express as px

# Page config
st.set_page_config(page_title="Nassau Candy Logistics Dashboard", layout="wide")

# Load dataset
df = pd.read_csv("nassau_candy_final_clean_dataset.csv")

# Title
st.title("Nassau Candy Distributor Logistics Analysis")

# Sidebar filters
st.sidebar.header("Filters")

region = st.sidebar.multiselect(
    "Select Region",
    options=df["Region"].unique(),
    default=df["Region"].unique()
)

ship_mode = st.sidebar.multiselect(
    "Select Ship Mode",
    options=df["Ship Mode"].unique(),
    default=df["Ship Mode"].unique()
)

# Filter data
filtered_df = df[
    (df["Region"].isin(region)) &
    (df["Ship Mode"].isin(ship_mode))
]

# KPI Section
avg_lead = round(filtered_df["Shipping Lead Time"].mean(), 2)
total_orders = filtered_df["Order ID"].nunique()
avg_sales = round(filtered_df["Sales"].mean(), 2)
avg_profit = round(filtered_df["Gross Profit"].mean(), 2)

col1, col2, col3, col4 = st.columns(4)

col1.metric("Average Lead Time", avg_lead)
col2.metric("Total Orders", total_orders)
col3.metric("Average Sales", avg_sales)
col4.metric("Average Profit", avg_profit)

# Chart 1
st.subheader("Average Shipping Lead Time by Region")

region_chart = filtered_df.groupby("Region")["Shipping Lead Time"].mean().reset_index()

fig1 = px.bar(
    region_chart,
    x="Region",
    y="Shipping Lead Time",
    color="Shipping Lead Time"
)

st.plotly_chart(fig1, use_container_width=True)

# Chart 2
st.subheader("Ship Mode Performance")

ship_chart = filtered_df.groupby("Ship Mode")["Shipping Lead Time"].mean().reset_index()

fig2 = px.bar(
    ship_chart,
    x="Ship Mode",
    y="Shipping Lead Time",
    color="Shipping Lead Time"
)

st.plotly_chart(fig2, use_container_width=True)

# Chart 3
st.subheader("Delay Status Distribution")

fig3 = px.pie(
    filtered_df,
    names="Delay Status",
    hole=0.5
)

st.plotly_chart(fig3, use_container_width=True)

# Detailed Table
st.subheader("Detailed Shipment Data")

display_df = filtered_df[[
    "Order ID",
    "Order Date",
    "Ship Date Corrected",
    "Ship Mode",
    "Factory",
    "Region",
    "State/Province",
    "Shipping Lead Time",
    "Delay Status",
    "Sales",
    "Gross Profit"
]]

st.dataframe(display_df)

# Route Creation
filtered_df["Factory_to_State_Route"] = (
    filtered_df["Factory"] + " to " + filtered_df["State/Province"]
)

# Top 10 Efficient Routes
st.subheader("Top 10 Most Efficient Routes")

top_routes = (
    filtered_df.groupby("Factory_to_State_Route")["Shipping Lead Time"]
    .mean()
    .reset_index()
    .sort_values(by="Shipping Lead Time", ascending=True)
    .head(10)
)

fig4 = px.bar(
    top_routes,
    x="Shipping Lead Time",
    y="Factory_to_State_Route",
    orientation="h",
    color="Shipping Lead Time"
)

st.plotly_chart(fig4, use_container_width=True)

# Bottom 10 Least Efficient Routes
st.subheader("Bottom 10 Least Efficient Routes")

bottom_routes = (
    filtered_df.groupby("Factory_to_State_Route")["Shipping Lead Time"]
    .mean()
    .reset_index()
    .sort_values(by="Shipping Lead Time", ascending=False)
    .head(10)
)

fig5 = px.bar(
    bottom_routes,
    x="Shipping Lead Time",
    y="Factory_to_State_Route",
    orientation="h",
    color="Shipping Lead Time"
)

st.plotly_chart(fig5, use_container_width=True)

# ==============================
# LEAD TIME THRESHOLD SLIDER
# ==============================

st.subheader("Lead Time Threshold Filter")

lead_threshold = st.slider(
    "Select Minimum Shipping Lead Time",
    int(filtered_df["Shipping Lead Time"].min()),
    int(filtered_df["Shipping Lead Time"].max()),
    500
)

threshold_df = filtered_df[
    filtered_df["Shipping Lead Time"] >= lead_threshold
]

st.write("Filtered Records:", threshold_df.shape[0])

# ==============================
# STATE LEVEL BOTTLENECK ANALYSIS
# ==============================

st.subheader("Top Bottleneck States")

state_delay = (
    threshold_df.groupby("State/Province")["Shipping Lead Time"]
    .mean()
    .reset_index()
    .sort_values(by="Shipping Lead Time", ascending=False)
    .head(10)
)

fig6 = px.bar(
    state_delay,
    x="Shipping Lead Time",
    y="State/Province",
    orientation="h",
    color="Shipping Lead Time"
)

st.plotly_chart(fig6, use_container_width=True)

# ==============================
# REGION SHIPMENT VOLUME
# ==============================

st.subheader("Shipment Volume by Region")

region_volume = (
    filtered_df.groupby("Region")["Order ID"]
    .count()
    .reset_index()
)

fig7 = px.pie(
    region_volume,
    names="Region",
    values="Order ID"
)

st.plotly_chart(fig7, use_container_width=True)
