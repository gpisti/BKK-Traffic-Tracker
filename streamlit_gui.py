import streamlit as st
from analysis import (
    display_kpis,
    analyze_route_performance,
    analyze_peak_vs_nonpeak,
    analyze_environmental_impact,
    display_map,
    analyze_correlation,
    analyze_route_optimization,
    analyze_traffic_by_day_of_week,
    analyze_speed_distribution_by_route,
    analyze_vehicle_count_per_route,
    display_traffic_density_heatmap,
    fetch_data,
)
from modules.queries import GET_DISTINCT_ROUTES


def main():
    st.title("BKK Traffic Data Dashboard")
    st.write(
        "This dashboard provides real-time insights into traffic data collected from BKK."
    )

    route_df = fetch_data(GET_DISTINCT_ROUTES)
    if route_df is None or route_df.empty:
        st.write("No routes available.")
        return

    route_ids = route_df["route_id"].tolist()
    selected_route = st.selectbox("Select a bus route", ["All"] + route_ids)

    display_kpis(selected_route)

    display_map(selected_route)

    st.subheader("Traffic Analysis")

    st.write("### Traffic Density Heatmap")
    display_traffic_density_heatmap(selected_route)

    st.write("### Route Performance Analysis")
    analyze_route_performance(selected_route)

    st.write("### Peak vs. Non-Peak Hour Analysis")
    analyze_peak_vs_nonpeak(selected_route)

    st.write("### Environmental Impact Analysis")
    analyze_environmental_impact(selected_route)

    st.write("### Correlation Analysis")
    analyze_correlation(selected_route)

    st.write("### Route Optimization Suggestions")
    analyze_route_optimization(selected_route)

    st.write("### Traffic Volume by Day of Week")
    analyze_traffic_by_day_of_week(selected_route)

    st.write("### Speed Distribution by Route")
    analyze_speed_distribution_by_route(selected_route)

    st.write("### Vehicle Count per Route")
    analyze_vehicle_count_per_route(selected_route)


if __name__ == "__main__":
    main()
