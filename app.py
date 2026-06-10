
import streamlit as st
import pandas as pd
import plotly.express as px

# Page config
st.set_page_config(page_title="Nassau Candy Logistics Dashboard", layout="wide")

# Load dataset
df = pd.read_csv("/content/nassau_candy_final_clean_dataset.csv")

df["Order Date"] = pd.to_datetime(
    df["Order Date"],
    dayfirst=True
)

df["Ship Date Corrected"] = pd.to_datetime(
    df["Ship Date Corrected"],
    dayfirst=True
)

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

state = st.sidebar.multiselect(
    "Select State",
    options=sorted(df["State/Province"].unique()),
    default=sorted(df["State/Province"].unique())
)

st.sidebar.subheader("Select Date Range")

date_range = st.sidebar.date_input(
    "Order Date Range",
    value=(
        df["Order Date"].min(),
        df["Order Date"].max()
    )
)


# Filter data

filtered_df = df[
    (df["Region"].isin(region)) &
    (df["Ship Mode"].isin(ship_mode)) &
    (df["State/Province"].isin(state))
]

#if len(date_range) == 2:
  #start_date, end_date = date_range

    #filtered_df = filtered_df[
      #  (filtered_df["Order Date"] >= pd.to_datetime(start_date)) &
       # (filtered_df["Order Date"] <= pd.to_datetime(end_date))


# ==================================
# DASHBOARD TABS
# ==================================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Overview",
    "🚚 Route Analysis",
    "📍 Bottlenecks",
    "🚛 Ship Mode",
    "💡 Recommendations"
])

with tab1:

    st.header("📊 Logistics Performance Overview")

    # KPI Section
    avg_lead = round(filtered_df["Shipping Lead Time"].mean(), 2)
    total_orders = filtered_df["Order ID"].nunique()
    avg_sales = round(filtered_df["Sales"].sum(), 2)
    avg_profit = round(filtered_df["Gross Profit"].sum(), 2)
    delay_freq = round(
          (
           filtered_df["Delay Flag"]
            .eq("Delayed")
            .mean()
          ) * 100,
               2
         )

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Average Lead Time", avg_lead)
    col2.metric("Total Orders", total_orders)
    col3.metric("Total Sales", f"${avg_sales:,.0f}")
    col4.metric("Total Profit", f"${avg_profit:,.0f}")
    col5.metric(
    "Delay Frequency %",
    f"{delay_freq}%"
   )

    st.markdown("---")

    # Chart 1
    st.subheader("Average Shipping Lead Time by Region")

    region_chart = (
        filtered_df.groupby("Region")["Shipping Lead Time"]
        .mean()
        .reset_index()
    )

    fig1 = px.bar(
        region_chart,
        x="Region",
        y="Shipping Lead Time",
        color="Shipping Lead Time"
    )

    st.plotly_chart(fig1, use_container_width=True, key="overview_region")

    # Chart 2
    st.subheader("Delay Status Distribution")

    fig2 = px.pie(
        filtered_df,
        names="Delay Status",
        hole=0.5
    )

    st.plotly_chart(fig2, use_container_width=True,key="overview_Delay_Status")

    # Chart 3
    st.subheader("Shipment Volume by Region")

    region_volume = (
        filtered_df.groupby("Region")["Order ID"]
        .count()
        .reset_index()
    )

    fig3 = px.bar(
        region_volume,
        x="Region",
        y="Order ID",
        color="Order ID"
    )

    st.plotly_chart(fig3, use_container_width=True, key="overview_ship_region")

    # Chart 4
    st.subheader("Sales by Region")

    sales_region = (
        filtered_df.groupby("Region")["Sales"]
        .sum()
        .reset_index()
    )

    fig4 = px.pie(
        sales_region,
        names="Region",
        values="Sales"
    )

    st.plotly_chart(fig4, use_container_width=True,key="overview_sale_region")

with tab2:

    st.header("🚚 Route Efficiency Analysis")

    # Route Summary

    route_summary = (
        filtered_df.groupby("Factory-to-State Route")
        .agg({
            "Shipping Lead Time": "mean",
            "Order ID": "count",
            "Route Efficiency Score": "mean"
        })
        .reset_index()
    )

    route_summary.columns = [
        "Route",
        "Average Lead Time",
        "Route Volume",
        "Route Efficiency Score"
    ]



    # Top 10 Efficient Routes

    st.subheader("🏆 Top 10 Most Efficient Routes")

    top_routes = (
        route_summary
        .sort_values("Average Lead Time")
        .head(10)
    )

    fig_top = px.bar(
        top_routes,
        x="Average Lead Time",
        y="Route",
        orientation="h",
        color="Average Lead Time"
    )

    st.plotly_chart(fig_top, use_container_width=True,key="Route_Top10")

    # Bottom 10 Routes

    st.subheader("⚠️ Bottom 10 Least Efficient Routes")

    bottom_routes = (
        route_summary
        .sort_values("Average Lead Time", ascending=False)
        .head(10)
    )

    fig_bottom = px.bar(
        bottom_routes,
        x="Average Lead Time",
        y="Route",
        orientation="h",
        color="Average Lead Time"
    )

    st.plotly_chart(fig_bottom, use_container_width=True,key="Route_bott10")

    # Route Volume

    st.subheader("📦 Route Shipment Volume")

    volume_routes = (
        route_summary
        .sort_values("Route Volume", ascending=False)
        .head(10)
    )

    fig_volume = px.bar(
        volume_routes,
        x="Route Volume",
        y="Route",
        orientation="h",
        color="Route Volume"
    )

    st.plotly_chart(fig_volume, use_container_width=True, key="Route_shipment")

    # Route Efficiency Score

    st.subheader("📈 Route Efficiency Score")

    fig_score = px.scatter(
        route_summary,
        x="Route Volume",
        y="Average Lead Time",
        size="Route Efficiency Score",
        hover_name="Route"
    )

    st.plotly_chart(fig_score, use_container_width=True,key="Route_Effi_score")

    st.subheader("📊 Routes with Highest Lead Time Variability")

    route_variability = (
       filtered_df.groupby("Factory-to-State Route")
       ["Shipping Lead Time"]
       .std()
       .reset_index()
       .sort_values(
         by="Shipping Lead Time",
         ascending=False
     )
    .head(10)
    )

    fig_var = px.bar(
       route_variability,
       x="Shipping Lead Time",
       y="Factory-to-State Route",
       orientation="h",
       color="Shipping Lead Time"
      )

    st.plotly_chart(
      fig_var,
      use_container_width=True, key="Route_LTime_Variability"
     )

    # Detailed Route Table

    st.subheader("📋 Route Leaderboard")

    st.dataframe(
        route_summary.sort_values(
            "Average Lead Time"
        )
    )

with tab3:

    st.header("📍 Geographic Bottleneck Analysis")

    st.subheader("🗺️ Factory Shipping Network")

    factory_coords = pd.DataFrame({
         "Factory": [
             "Lot's O' Nuts",
             "Wicked Choccy's",
             "Sugar Shack",
             "Secret Factory",
             "The Other Factory"
         ],
          "Latitude": [
             32.881893,
             32.076176,
             48.119140,
             41.446333,
             35.117500
         ],
         "Longitude": [
             -111.768036,
             -81.088371,
             -96.181150,
             -90.565487,
             -89.971107
         ]
      })

    fig_map = px.scatter_mapbox(
         factory_coords,
          lat="Latitude",
          lon="Longitude",
           hover_name="Factory",
           zoom=3,
           height=500
    )

    fig_map.update_layout(
          mapbox_style="open-street-map"
     )

    st.plotly_chart(
       fig_map,
      use_container_width=True,key="Bottleneck_factory"
    )

    # Lead Time Threshold

    st.subheader("Lead Time Threshold Filter")

    lead_threshold = st.slider(
        "Select Minimum Shipping Lead Time",
        int(filtered_df["Shipping Lead Time"].min()),
        int(filtered_df["Shipping Lead Time"].max()),
        int(filtered_df["Shipping Lead Time"].mean())
    )

    threshold_df = filtered_df[
        filtered_df["Shipping Lead Time"] >= lead_threshold
    ]

    st.write(
        "Filtered Shipments:",
        threshold_df.shape[0]
    )

    # Top Bottleneck States

    st.subheader("🚨 Top Bottleneck States")

    state_delay = (
        threshold_df.groupby("State/Province")
        ["Shipping Lead Time"]
        .mean()
        .reset_index()
        .sort_values(
            by="Shipping Lead Time",
            ascending=False
        )
        .head(10)
    )

    fig_state = px.bar(
        state_delay,
        x="Shipping Lead Time",
        y="State/Province",
        orientation="h",
        color="Shipping Lead Time"
    )

    st.plotly_chart(
        fig_state,
        use_container_width=True, key="Bottleneck_Top_s"
    )

    # Region Performance

    st.subheader("🌎 Region Performance")

    region_delay = (
        filtered_df.groupby("Region")
        ["Shipping Lead Time"]
        .mean()
        .reset_index()
    )

    fig_region = px.bar(
        region_delay,
        x="Region",
        y="Shipping Lead Time",
        color="Shipping Lead Time"
    )

    st.plotly_chart(
        fig_region,
        use_container_width=True, key="Bottleneck_region"
    )

    # Shipment Volume

    st.subheader("📦 Shipment Volume by Region")

    region_volume = (
        filtered_df.groupby("Region")
        ["Order ID"]
        .count()
        .reset_index()
    )

    fig_volume = px.pie(
        region_volume,
        names="Region",
        values="Order ID",
        hole=0.5
    )

    st.plotly_chart(
        fig_volume,
        use_container_width=True, key="Bottleneck_ship_reg"
    )

    # State Leaderboard

    st.subheader("📋 State Performance Ranking")

    state_table = (
        filtered_df.groupby("State/Province")
        .agg({
            "Shipping Lead Time": "mean",
            "Order ID": "count"
        })
        .reset_index()
    )

    state_table.columns = [
        "State",
        "Average Lead Time",
        "Shipment Volume"
    ]

    st.dataframe(
        state_table.sort_values(
            "Average Lead Time",
            ascending=False
        )
    )

with tab4:

    st.header("🚛 Ship Mode Performance Analysis")

    # Lead Time by Ship Mode

    st.subheader("Average Lead Time by Ship Mode")

    ship_mode_lead = (
        filtered_df.groupby("Ship Mode")
        ["Shipping Lead Time"]
        .mean()
        .reset_index()
    )

    fig_ship1 = px.bar(
        ship_mode_lead,
        x="Ship Mode",
        y="Shipping Lead Time",
        color="Shipping Lead Time"
    )

    st.plotly_chart(
        fig_ship1,
        use_container_width=True,key="shipM_averageL"
    )

    # Shipment Volume

    st.subheader("Shipment Volume by Ship Mode")

    ship_volume = (
        filtered_df.groupby("Ship Mode")
        ["Order ID"]
        .count()
        .reset_index()
    )

    fig_ship2 = px.pie(
        ship_volume,
        names="Ship Mode",
        values="Order ID",
        hole=0.5
    )

    st.plotly_chart(
        fig_ship2,
        use_container_width=True,key="shipM_volume"
    )

    # Sales Performance

    st.subheader("Sales by Ship Mode")

    ship_sales = (
        filtered_df.groupby("Ship Mode")
        ["Sales"]
        .sum()
        .reset_index()
    )

    fig_ship3 = px.bar(
        ship_sales,
        x="Ship Mode",
        y="Sales",
        color="Sales"
    )

    st.plotly_chart(
        fig_ship3,
        use_container_width=True, key="shipM_sale"
    )

    # Profit Performance

    st.subheader("Gross Profit by Ship Mode")

    ship_profit = (
        filtered_df.groupby("Ship Mode")
        ["Gross Profit"]
        .sum()
        .reset_index()
    )

    fig_ship4 = px.bar(
        ship_profit,
        x="Ship Mode",
        y="Gross Profit",
        color="Gross Profit"
    )

    st.plotly_chart(
        fig_ship4,
        use_container_width=True,key="shipM_gross"
     )

    st.subheader("💰 Cost vs Lead Time Tradeoff")

    cost_tradeoff = (
       filtered_df.groupby("Ship Mode")
       .agg({
            "Cost": "mean",
            "Shipping Lead Time": "mean"
        })
        .reset_index()
     )

    fig_tradeoff = px.scatter(
       cost_tradeoff,
       x="Cost",
       y="Shipping Lead Time",
       size="Shipping Lead Time",
       color="Ship Mode",
       hover_name="Ship Mode"
    )

    st.plotly_chart(
        fig_tradeoff,
        use_container_width=True, key="shipM_costvs_lead"
    )
    # Ship Mode Leaderboard

    st.subheader("Ship Mode Performance Table")

    ship_table = (
        filtered_df.groupby("Ship Mode")
        .agg({
            "Shipping Lead Time": "mean",
            "Sales": "sum",
            "Gross Profit": "sum",
            "Order ID": "count"
        })
        .reset_index()
    )

    ship_table.columns = [
        "Ship Mode",
        "Average Lead Time",
        "Total Sales",
        "Total Profit",
        "Shipment Volume"
    ]

    st.dataframe(ship_table)

with tab5:

    st.header("💡 Executive Insights & Recommendations")

    # Executive Summary

    st.subheader("Executive Summary")

    st.info(
        """
        This dashboard analyzes shipping efficiency,
        route performance, bottlenecks, and ship mode
        effectiveness across Nassau Candy Distributor's
        logistics network.

        The analysis helps identify operational
        inefficiencies and supports data-driven
        logistics optimization.
        """
    )

    # Key Findings

    st.subheader("Key Findings")

    avg_lead = round(
        filtered_df["Shipping Lead Time"].mean(), 2
    )

    total_shipments = filtered_df["Order ID"].count()

    total_sales = round(
        filtered_df["Sales"].sum(), 2
    )

    total_profit = round(
        filtered_df["Gross Profit"].sum(), 2
    )

    st.success(
        f"""
        • Total Shipments Analyzed: {total_shipments}

        • Average Shipping Lead Time: {avg_lead}

        • Total Sales: ${total_sales:,.0f}

        • Total Gross Profit: ${total_profit:,.0f}
        """
    )

    # Recommendations

    st.subheader("Strategic Recommendations")

    st.warning(
        """
        1. Prioritize optimization of routes with
           consistently high lead times.

        2. Closely monitor bottleneck states and
           regions with poor shipping performance.

        3. Improve shipment planning in
           congestion-prone regions.

        4. Increase utilization of efficient
           shipping methods where feasible.

        5. Implement predictive logistics monitoring
           to proactively identify delays.

        6. Continuously track Route Efficiency
           Scores for performance benchmarking.
        """
    )

    # Business Impact

    st.subheader("Expected Business Impact")

    st.write(
        """
        • Improved customer satisfaction

        • Reduced delivery delays

        • Better route planning

        • Improved logistics scalability

        • Enhanced operational visibility

        • Data-driven decision making
        """
    )

    # Download Data

    st.subheader("Download Filtered Dataset")

    csv = filtered_df.to_csv(index=False)

    st.download_button(
        label="📥 Download Filtered Data",
        data=csv,
        file_name="nassau_filtered_data.csv",
        mime="text/csv"
    )
