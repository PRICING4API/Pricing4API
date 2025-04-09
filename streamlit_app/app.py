import streamlit as st
from Pricing4API.basic.bounded_rate import Rate, Quota, BoundedRate
from Pricing4API.ancillary.time_unit import TimeDuration, TimeUnit
from Pricing4API.utils import parse_time_string_to_duration  # Importar la función correcta

def main():
    st.title("Capacity Simulation App")

    # User inputs for Rate
    st.sidebar.header("Rate Configuration")
    consumption_unit = st.sidebar.number_input("Consumption Unit", min_value=1, value=10)
    consumption_period = st.sidebar.text_input("Consumption Period", value="1s")

    # User inputs for Quota
    st.sidebar.header("Quota Configuration")
    quota_unit = st.sidebar.number_input("Quota Unit", min_value=1, value=100)
    quota_period = st.sidebar.text_input("Quota Period", value="1min")

    # Create Rate and Quota objects
    rate = Rate(consumption_unit, consumption_period)
    quota = Quota(quota_unit, quota_period)

    # Create BoundedRate object
    bounded_rate = BoundedRate(rate, quota)

    # User input for time interval
    st.sidebar.header("Simulation Configuration")
    time_interval = st.sidebar.text_input("Time Interval", value="5min")

    # Convert time interval to TimeDuration using the correct function
    time_duration = parse_time_string_to_duration(time_interval)

    # Display capacity curves
    st.header("Capacity Curves")
    fig = bounded_rate.show_capacity(time_duration, return_fig=True)
    st.plotly_chart(fig)

    # Display quota exhaustion threshold
    st.header("Quota Exhaustion Threshold")
    thresholds = bounded_rate.quota_exhaustion_threshold()
    st.write(thresholds)

if __name__ == "__main__":
    main()