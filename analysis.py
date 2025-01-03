# analysis.py

import altair as alt
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium
import folium
from folium.plugins import MarkerCluster, HeatMap
from database.database_consumer import connect_server

# Importing the extracted queries
from modules.queries import (
    TRAFFIC_HEATMAP_BASE,
    KPIS_BASE,
    ROUTE_PERFORMANCE_BASE,
    PEAK_NONPEAK_BASE,
    ENV_IMPACT_BASE,
    CORRELATION_BASE,
    ROUTE_OPTIMIZATION_BASE,
    TRAFFIC_BY_DAY_OF_WEEK_BASE,
    SPEED_DISTRIBUTION_BASE,
    VEHICLE_COUNT_BASE,
)


@st.cache_data
def fetch_data(query, params=None):
    """
    Executes the given SQL query with optional parameters and returns a pandas DataFrame.

    :param query: SQL query string.
    :param params: Optional tuple of parameters for parameterized queries.
    :return: pandas DataFrame with query results or None if connection fails.
    """
    engine = connect_server()
    if engine is None:
        return None
    print(f"Executing Query:\n{query}")
    if params:
        print(f"With Parameters: {params}")
    return pd.read_sql(query, engine, params=params)


def build_route_query(base_query, selected_route, column="route_id"):
    """
    Appends a WHERE clause to the base query if a specific route is selected.

    :param base_query: The base SQL query string.
    :param selected_route: The route_id to filter by or "All" for no filtering.
    :param column: The column name to apply the filter on (default is "route_id").
    :return: Modified SQL query string.
    """
    if selected_route != "All":
        base_query += f" WHERE {column} = %s"
    return base_query


def display_traffic_density_heatmap(selected_route):
    """
    Displays a heatmap of traffic density based on latitude and longitude.

    :param selected_route: The route_id to filter by or "All" for no filtering.
    """
    query = TRAFFIC_HEATMAP_BASE
    query = build_route_query(query, selected_route)
    query += " GROUP BY latitude, longitude ORDER BY traffic_count DESC;"

    df = fetch_data(
        query, params=(selected_route,) if selected_route != "All" else None
    )

    if df.empty:
        st.write("No data available.")
        return

    map_center = [df["latitude"].mean(), df["longitude"].mean()]
    traffic_map = folium.Map(location=map_center, zoom_start=12)

    heat_data = [
        [row["latitude"], row["longitude"], row["traffic_count"]]
        for _, row in df.iterrows()
    ]

    HeatMap(heat_data).add_to(traffic_map)

    st_folium(traffic_map, width=800, height=600)


def display_kpis(selected_route):
    """
    Displays Key Performance Indicators (KPIs) such as average speed, highest traffic count, and busiest route.

    :param selected_route: The route_id to filter by or "All" for no filtering.
    """
    query = KPIS_BASE
    query = build_route_query(query, selected_route)
    query += " GROUP BY route_id ORDER BY traffic_count DESC LIMIT 5;"

    df = fetch_data(
        query, params=(selected_route,) if selected_route != "All" else None
    )

    if df.empty:
        st.write("No data available.")
        return

    avg_speed = df["avg_speed"].mean()
    highest_traffic = df["traffic_count"].max()
    busiest_route = df.loc[df["traffic_count"].idxmax()]["route_id"]

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Avg Speed (km/h)", value=f"{avg_speed:.2f}")
    with col2:
        st.metric(label="Highest Traffic Count", value=highest_traffic)
    with col3:
        st.metric(label="Busiest Route", value=f"Route {busiest_route}")
    st.write("---")


def analyze_route_performance(selected_route):
    """
    Analyzes and visualizes route performance based on average speed and traffic count.

    :param selected_route: The route_id to filter by or "All" for no filtering.
    """
    query = ROUTE_PERFORMANCE_BASE
    query = build_route_query(query, selected_route)
    query += " GROUP BY route_id ORDER BY traffic_count DESC;"

    df = fetch_data(
        query, params=(selected_route,) if selected_route != "All" else None
    )

    if df.empty:
        st.write("No data available for route performance.")
        return

    st.write(
        """This analysis evaluates the efficiency and reliability of each bus route by comparing average speed
            and on-time performance.
            The bar chart displays the average speed for each route,
            while the line plot overlays the percentage of on-time arrivals.
            Routes with lower speeds and punctuality rates are identified for potential optimization."""
    )

    chart = (
        alt.Chart(df)
        .mark_point()
        .encode(
            x="avg_speed:Q",
            y="traffic_count:Q",
            color="route_id:N",
            size="traffic_count:Q",
            tooltip=["route_id", "avg_speed", "traffic_count"],
        )
        .properties(title="Route Performance Analysis", width=600, height=400)
        .configure_mark(opacity=0.7, color="blue")
    )

    st.altair_chart(chart, use_container_width=True)


def analyze_peak_vs_nonpeak(selected_route):
    """
    Analyzes and visualizes traffic volume and average speed during peak and non-peak hours.

    :param selected_route: The route_id to filter by or "All" for no filtering.
    """
    query = PEAK_NONPEAK_BASE
    query = build_route_query(query, selected_route)
    query += " GROUP BY hour ORDER BY hour;"

    df = fetch_data(
        query, params=(selected_route,) if selected_route != "All" else None
    )

    if df.empty:
        st.write("No data available for peak vs non-peak analysis.")
        return

    st.write(
        """
    This analysis compares traffic volume and average speed during peak and non-peak hours.
    The line plot displays traffic count by hour, with a secondary axis for average speed.
    Peak hours generally correspond to higher traffic volume and lower average speeds.
    """
    )

    chart = (
        alt.Chart(df)
        .mark_line()
        .encode(
            x="hour:O",
            y="traffic_count:Q",
            color=alt.value("blue"),
            tooltip=["hour", "traffic_count"],
        )
        .properties(title="Traffic Volume by Hour")
    )

    chart2 = (
        alt.Chart(df)
        .mark_line()
        .encode(
            x="hour:O",
            y="avg_speed:Q",
            color=alt.value("red"),
            tooltip=["hour", "avg_speed"],
        )
        .properties(title="Average Speed by Hour")
    )

    st.altair_chart(chart + chart2, use_container_width=True)


def analyze_environmental_impact(selected_route):
    """
    Estimates the environmental impact by calculating CO2 emissions based on traffic conditions.

    :param selected_route: The route_id to filter by or "All" for no filtering.
    """
    query = ENV_IMPACT_BASE
    query = build_route_query(query, selected_route)
    query += " GROUP BY route_id ORDER BY traffic_count DESC;"

    df = fetch_data(
        query, params=(selected_route,) if selected_route != "All" else None
    )

    if df.empty:
        st.write("No data available for environmental impact analysis.")
        return

    st.write(
        """
    This analysis estimates the environmental impact by calculating CO2 emissions based on traffic conditions.
    Routes with higher traffic counts are analyzed for their estimated emissions. A bar chart visualizes estimated emissions for different routes.
    """
    )

    # Example calculation: estimated_emissions = traffic_count * (1 / avg_speed)
    df["estimated_emissions"] = df["traffic_count"] * (1 / df["avg_speed"])

    chart = (
        alt.Chart(df.head(15))
        .mark_bar()
        .encode(
            x="route_id:N",
            y="estimated_emissions:Q",
            color="route_id:N",
            tooltip=["route_id", "estimated_emissions"],
        )
        .properties(title="Estimated CO2 Emissions by Route")
    )

    st.altair_chart(chart, use_container_width=True)


def analyze_correlation(selected_route):
    """
    Examines the correlation between speed and traffic count.

    :param selected_route: The route_id to filter by or "All" for no filtering.
    """
    query = CORRELATION_BASE
    query = build_route_query(query, selected_route)
    query += " GROUP BY speed ORDER BY traffic_count DESC;"

    df = fetch_data(
        query, params=(selected_route,) if selected_route != "All" else None
    )

    if df.empty:
        st.write("No data available for correlation analysis.")
        return

    st.write(
        """
    This analysis examines the correlation between speed and traffic count. A heatmap visualizes the 
    relationship between these variables, with stronger correlations shown in darker colors.
    """
    )

    # Compute correlation matrix
    corr = df.corr()

    corr_reset = corr.reset_index().melt(id_vars="index")
    corr_reset.columns = ["variable", "index", "value"]

    heatmap = (
        alt.Chart(corr_reset)
        .mark_rect()
        .encode(
            x="index:N",
            y="variable:N",
            color="value:Q",
            tooltip=["index", "variable", "value"],
        )
        .properties(
            title="Correlation Heatmap",
            width=600,
            height=600,
        )
        .configure_mark(opacity=0.7)
    )

    st.altair_chart(heatmap, use_container_width=True)


def analyze_route_optimization(selected_route):
    """
    Suggests ways to optimize route speeds based on average speed and delay.

    :param selected_route: The route_id to filter by or "All" for no filtering.
    """
    query = ROUTE_OPTIMIZATION_BASE
    query = build_route_query(query, selected_route)
    query += " GROUP BY route_id ORDER BY avg_speed DESC;"

    df = fetch_data(
        query, params=(selected_route,) if selected_route != "All" else None
    )

    if df.empty:
        st.write("No data available for route optimization analysis.")
        return

    st.write(
        """
    This analysis suggests ways to optimize route speeds based on average speed and delay.
    Routes with lower average speeds might benefit from speed improvements.
    """
    )

    # Example calculation: suggested_speed = avg_speed + (10 - avg_speed) / 2
    df["suggested_speed"] = df["avg_speed"] + (10 - df["avg_speed"]) / 2

    chart = (
        alt.Chart(df.head(15))
        .mark_bar()
        .encode(
            x="route_id:N",
            y="suggested_speed:Q",
            color="route_id:N",
            tooltip=["route_id", "suggested_speed"],
        )
        .properties(title="Suggested Speed Increases by Route")
    )

    st.altair_chart(chart, use_container_width=True)


def display_map(selected_route):
    """
    Displays a map with markers for vehicle locations.

    :param selected_route: The route_id to filter by or "All" for no filtering.
    """
    # This query is not speed-related and remains unchanged
    query = """
    SELECT vehicle_id, route_id, latitude, longitude
    FROM vehicle_data
    WHERE latitude IS NOT NULL AND longitude IS NOT NULL
    """
    query = build_route_query(query, selected_route)
    query += " LIMIT 100;"

    df = fetch_data(
        query, params=(selected_route,) if selected_route != "All" else None
    )

    if df.empty:
        st.write("No vehicle location data available.")
        return

    map_center = [df["latitude"].mean(), df["longitude"].mean()]
    bus_map = folium.Map(location=map_center, zoom_start=12)

    marker_cluster = MarkerCluster().add_to(bus_map)

    for _, row in df.iterrows():
        folium.Marker(
            location=[row["latitude"], row["longitude"]],
            popup=f"Vehicle ID: {row['vehicle_id']} | Route ID: {row['route_id']}",
            icon=folium.Icon(color="blue", icon="bus", prefix="fa"),
        ).add_to(marker_cluster)

    st_folium(bus_map, width=800, height=600)


def analyze_traffic_by_day_of_week(selected_route):
    """
    Analyzes and visualizes traffic counts by day of the week.

    :param selected_route: The route_id to filter by or "All" for no filtering.
    """
    query = TRAFFIC_BY_DAY_OF_WEEK_BASE
    query = build_route_query(query, selected_route)
    query += " GROUP BY day_of_week ORDER BY day_of_week;"

    df = fetch_data(
        query, params=(selected_route,) if selected_route != "All" else None
    )

    if df.empty:
        st.write("No data available for traffic by day of the week.")
        return

    # Map day_of_week numbers to day names
    day_mapping = {
        0: "Sunday",
        1: "Monday",
        2: "Tuesday",
        3: "Wednesday",
        4: "Thursday",
        5: "Friday",
        6: "Saturday",
    }
    df["day_name"] = df["day_of_week"].map(day_mapping)

    st.write(
        """
    This analysis shows how traffic counts vary by day of the week. A bar chart visualizes traffic patterns
    for each day, highlighting busy periods during weekdays or weekends.
    """
    )

    chart = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X(
                "day_name:N",
                sort=[
                    "Monday",
                    "Tuesday",
                    "Wednesday",
                    "Thursday",
                    "Friday",
                    "Saturday",
                    "Sunday",
                ],
            ),
            y="traffic_count:Q",
            color="day_name:N",
            tooltip=["day_name", "traffic_count"],
        )
        .properties(title="Traffic by Day of Week")
    )

    st.altair_chart(chart, use_container_width=True)


def analyze_speed_distribution_by_route(selected_route):
    """
    Analyzes and visualizes the distribution of vehicle speeds for selected routes.

    :param selected_route: The route_id to filter by or "All" for no filtering.
    """
    query = SPEED_DISTRIBUTION_BASE
    query = build_route_query(query, selected_route)
    query += " ORDER BY speed DESC;"

    df = fetch_data(
        query, params=(selected_route,) if selected_route != "All" else None
    )

    if df.empty:
        st.write("No data available for speed distribution analysis.")
        return

    st.write(
        """
    This analysis shows the distribution of vehicle speeds for the selected route(s). It helps to understand traffic conditions such as congestion or smooth flowing traffic.
    """
    )

    chart = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x="speed:Q",
            y="count():Q",
            color="route_id:N",
            tooltip=["speed", "count()"],
        )
        .properties(title="Speed Distribution by Route")
    )

    st.altair_chart(chart, use_container_width=True)


def analyze_vehicle_count_per_route(selected_route):
    """
    Analyzes and visualizes the total count of vehicles operating on each route.

    :param selected_route: The route_id to filter by or "All" for no filtering.
    """
    query = VEHICLE_COUNT_BASE
    query = build_route_query(query, selected_route)
    query += " GROUP BY route_id ORDER BY vehicle_count DESC;"

    df = fetch_data(
        query, params=(selected_route,) if selected_route != "All" else None
    )

    if df.empty:
        st.write("No data available for vehicle count analysis.")
        return

    st.write(
        """
    This analysis provides the total count of vehicles operating on each route. It helps to understand which routes are the busiest and their operational load.
    """
    )

    chart = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x="route_id:N",
            y="vehicle_count:Q",
            color="route_id:N",
            tooltip=["route_id", "vehicle_count"],
        )
        .properties(title="Vehicle Count per Route")
    )

    st.altair_chart(chart, use_container_width=True)
