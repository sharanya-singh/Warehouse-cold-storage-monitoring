# Updated Dashboard.py - FIXED VERSION

import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="Warehouse Cold Storage Monitoring",
    layout="wide",
    page_icon="❄️"
)

# --- Initialize Persistent State for Alert Acknowledgement ---
# This will be available across all pages of the application.
if 'acknowledged_alerts' not in st.session_state:
    st.session_state.acknowledged_alerts = {
        'Z1-Freezer': None,
        'Z2-Chiller': None,
        'Z3-Produce': None,
        'Z4-Pharma': None
    }

# --- Alert Calculation Logic ---
# This logic is now included to dynamically check alerts for the quick status
def check_for_alerts(df, zone_id, temp_min, temp_max, humidity_min, humidity_max):
    """Checks the latest reading for a given zone against thresholds and acknowledgement status."""
    zone_data = df[df['zone_id'] == zone_id]
    if zone_data.empty:
        return "normal"

    latest_reading = zone_data.iloc[-1]
    temp = latest_reading['temperature']
    humidity = latest_reading['humidity']
    timestamp = latest_reading['timestamp']

    # Check if the latest reading's timestamp has been acknowledged
    acknowledged_ts = st.session_state.acknowledged_alerts.get(zone_id)
    if acknowledged_ts and timestamp <= acknowledged_ts:
        return "acknowledged"

    # If it's a new alert, flag it for either temp or humidity
    if not (temp_min <= temp <= temp_max):
        return "alert"
    if not (humidity_min <= humidity <= humidity_max):
        return "alert"
    return "normal"

# --- Main Application ---
st.title("❄️ Warehouse Cold Storage Monitoring")
st.markdown("**A real-time dashboard with predictive analytics and alert management**")
st.write("---")

# Navigation options
st.header("📊 Navigation")

# Create main navigation grid
col1, col2 = st.columns(2)

with col1:
    st.subheader("🏠 System Overview")
    st.markdown("Get a comprehensive view of all storage zones at once.")
    if st.button("🔍 View System Overview", use_container_width=True):
        st.switch_page("pages/Overview.py")

with col2:
    st.subheader("🎯 Individual Zone Monitoring")
    st.markdown("Detailed monitoring for specific storage zones.")

# Zone selection grid
st.write("**Select a storage zone to view its detailed dashboard:**")

col1, col2 = st.columns(2)
col3, col4 = st.columns(2)

with col1:
    st.markdown("### 🧊 Z1-Freezer")
    if st.button("Monitor Z1-Freezer", use_container_width=True): st.switch_page("pages/Z1-Freezer.py")

with col2:
    st.markdown("### ❄️ Z2-Chiller")
    if st.button("Monitor Z2-Chiller", use_container_width=True): st.switch_page("pages/Z2-Chiller.py")

with col3:
    st.markdown("### 🥬 Z3-Produce")
    if st.button("Monitor Z3-Produce", use_container_width=True): st.switch_page("pages/Z3-Produce.py")

with col4:
    st.markdown("### 💊 Z4-Pharma")
    if st.button("Monitor Z4-Pharma", use_container_width=True): st.switch_page("pages/Z4-Pharma.py")

# Quick system status
st.write("---")
st.header("⚡ Quick System Status")

try:
    df = pd.read_csv('simulated_warehouse_data_30min_demo.csv')
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    default_ranges = {
        'Z1-Freezer': {'temp_min': -22, 'temp_max': -18, 'humidity_min': 50, 'humidity_max': 70},
        'Z2-Chiller': {'temp_min': 2, 'temp_max': 5, 'humidity_min': 70, 'humidity_max': 80},
        'Z3-Produce': {'temp_min': 5, 'temp_max': 10, 'humidity_min': 80, 'humidity_max': 95},
        'Z4-Pharma': {'temp_min': 2, 'temp_max': 8, 'humidity_min': 50, 'humidity_max': 60}
    }

    # Dynamically check for unacknowledged alerts
    zones_with_alerts = []
    for zone_id, ranges in default_ranges.items():
        status = check_for_alerts(
            df, zone_id, 
            ranges['temp_min'], ranges['temp_max'],
            ranges['humidity_min'], ranges['humidity_max']
        )
        if status == 'alert':
            zones_with_alerts.append(zone_id)

    total_alerts = len(zones_with_alerts)
    active_zones = len(df['zone_id'].unique())
    last_update = df['timestamp'].max()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("🟢 Active Zones", f"{active_zones}/4")

    with col2:
        if total_alerts == 0:
            st.success("✅ No Active Alerts")
        else:
            st.error(f"🚨 {total_alerts} Active Alerts")

    with col3:
        st.metric("🕐 Last Update", last_update.strftime("%H:%M:%S"))

    if zones_with_alerts:
        st.warning(f"🚨 Unacknowledged alerts detected in: **{', '.join(zones_with_alerts)}**")

except FileNotFoundError:
    st.error("Data file not found. Please start `live_data_generator.py`.")
    st.stop()
except Exception as e:
    st.error(f"An error occurred: {e}")
    st.stop()