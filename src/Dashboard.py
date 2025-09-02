# Updated Dashboard.py - FIXED VERSION

import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Warehouse Cold Storage Monitoring",
    layout="wide",
    page_icon="❄️"
)

# --- Alert Calculation Logic ---
# This logic is now included to dynamically check alerts for the quick status
def check_for_alerts(df, zone_id, temp_min, temp_max, humidity_min, humidity_max):
    """Checks the latest reading for a given zone against thresholds."""
    zone_data = df[df['zone_id'] == zone_id]
    if zone_data.empty:
        return "normal"
    latest_reading = zone_data.iloc[-1]
    temp = latest_reading['temperature']
    humidity = latest_reading['humidity']

    if not (temp_min <= temp <= temp_max):
        return "alert"
    if not (humidity_min <= humidity <= humidity_max):
        return "alert"
    return "normal"

# --- Main Application ---
st.title("❄️ Warehouse Cold Storage Monitoring")
st.markdown("**A real-time dashboard with predictive analytics**")
st.write("---")

# Navigation options
st.header("📊 Navigation")

# Create main navigation grid
col1, col2 = st.columns(2)

with col1:
    st.subheader("🏠 System Overview")
    st.markdown("Get a comprehensive view of all storage zones at once")
    if st.button("🔍 View System Overview", use_container_width=True, type="primary"):
        st.switch_page("pages/Overview.py")

with col2:
    st.subheader("🎯 Individual Zone Monitoring")
    st.markdown("Detailed monitoring for specific storage zones")

# Zone selection grid
st.write("**Select a storage zone to view its detailed dashboard:**")

col1, col2 = st.columns(2)
col3, col4 = st.columns(2)

with col1:
    st.markdown("### 🧊 Z1-Freezer")
    st.caption("Frozen goods storage • -22°C to -18°C")
    if st.button("Monitor Z1-Freezer", use_container_width=True):
        st.switch_page("pages/Z1-Freezer.py")

with col2:
    st.markdown("### ❄️ Z2-Chiller")
    st.caption("Chilled products • 2°C to 5°C")
    if st.button("Monitor Z2-Chiller", use_container_width=True):
        st.switch_page("pages/Z2-Chiller.py")

with col3:
    st.markdown("### 🥬 Z3-Produce")
    st.caption("Fresh produce • 5°C to 10°C")
    if st.button("Monitor Z3-Produce", use_container_width=True):
        st.switch_page("pages/Z3-Produce.py")

with col4:
    st.markdown("### 💊 Z4-Pharma")
    st.caption("Pharmaceutical storage • 2°C to 8°C")
    if st.button("Monitor Z4-Pharma", use_container_width=True):
        st.switch_page("pages/Z4-Pharma.py")

# Quick system status
st.write("---")
st.header("⚡ Quick System Status")

try:
    df = pd.read_csv('simulated_warehouse_data_30min_demo.csv', na_values=['NaN', '', 'nan'])
    df = df.dropna()
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # Default thresholds for quick status check
    default_ranges = {
        'Z1-Freezer': {'temp_min': -22, 'temp_max': -18, 'humidity_min': 50, 'humidity_max': 70},
        'Z2-Chiller': {'temp_min': 2, 'temp_max': 5, 'humidity_min': 70, 'humidity_max': 80},
        'Z3-Produce': {'temp_min': 5, 'temp_max': 10, 'humidity_min': 80, 'humidity_max': 95},
        'Z4-Pharma': {'temp_min': 2, 'temp_max': 8, 'humidity_min': 50, 'humidity_max': 60}
    }

    # Dynamically check for alerts
    zones_with_alerts = []
    for zone_id, ranges in default_ranges.items():
        if check_for_alerts(df, zone_id, ranges['temp_min'], ranges['temp_max'], ranges['humidity_min'], ranges['humidity_max']) == 'alert':
            zones_with_alerts.append(zone_id)

    total_alerts = len(zones_with_alerts)
    active_zones = len([zone for zone in default_ranges.keys() if not df[df['zone_id'] == zone].empty])
    last_update = df['timestamp'].max()

    # Display quick metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("🟢 Active Zones", f"{active_zones}/4")

    with col2:
        if total_alerts == 0:
            st.success("✅ No Active Alerts")
        else:
            st.error(f"🚨 {total_alerts} Active Alerts")

    with col3:
        if pd.notna(last_update):
            st.metric("🕐 Last Update", last_update.strftime("%H:%M:%S"))
        else:
            st.metric("🕐 Last Update", "N/A")

    # Alert notification
    if zones_with_alerts:
        st.warning(f"🚨 Critical alerts detected in: {', '.join(zones_with_alerts)}")

except FileNotFoundError:
    st.warning("📁 No data file found. Please start the data generator first.")
    st.info("**To start generating data:**\n1. Run: `python src/live_data_generator.py`\n2. Wait for data to be generated\n3. Refresh this page")
    st.stop()

except Exception as e:
    st.error(f"❌ Error loading data: {e}")
    st.info("Please check if the data file exists and has the correct format.")
    st.stop()

# === QUICK DATA PREVIEW ===
with st.expander("📊 Quick Data Preview", expanded=False):
    if 'df' in locals() and not df.empty:
        st.markdown("**Latest readings from all zones:**")
        latest_data = df.groupby('zone_id').tail(1)[['zone_id', 'timestamp', 'temperature', 'humidity']]
        st.dataframe(latest_data, use_container_width=True, hide_index=True)
    else:
        st.info("No data available for preview")