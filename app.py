# Updated app.py with System Overview
import streamlit as st

st.set_page_config(
    page_title="Warehouse Cold Storage Monitoring",
    layout="wide",
    page_icon="❄️"
)

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
        st.switch_page("pages/overview.py")

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
    st.caption("Chilled products • 2°C to 4°C")
    if st.button("Monitor Z2-Chiller", use_container_width=True):
        st.switch_page("pages/Z2-Chiller.py")

with col3:
    st.markdown("### 🥬 Z3-Produce")
    st.caption("Fresh produce • 8°C to 12°C")
    if st.button("Monitor Z3-Produce", use_container_width=True):
        st.switch_page("pages/Z3-Produce.py")

with col4:
    st.markdown("### 💊 Z4-Pharma")
    st.caption("Pharmaceutical storage • -5°C to -2°C")
    if st.button("Monitor Z4-Pharma", use_container_width=True):
        st.switch_page("pages/Z4-Pharma.py")

# Quick system status
st.write("---")
st.header("⚡ Quick System Status")

try:
    import pandas as pd
    
    # Try to load data for quick status
    df = pd.read_csv('simulated_warehouse_data_30min_demo.csv')
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Calculate quick stats
    zones = ['Z1-Freezer', 'Z2-Chiller', 'Z3-Produce', 'Z4-Pharma']
    total_alerts = len(df[df['alert_status'] == 'alert'])
    active_zones = len([zone for zone in zones if not df[df['zone_id'] == zone].empty])
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

except FileNotFoundError:
    st.info("💡 **Tip:** Start the data generator to see live system status")
    st.code("python live_data_generator.py", language="bash")

except Exception as e:
    st.warning("⚠️ Unable to load system status")

# Footer
st.write("---")
st.markdown("""
**🛠️ System Features:**
- ✅ Real-time temperature and humidity monitoring
- ✅ Automated alert generation and tracking  
- ✅ Historical trend analysis and forecasting
- ✅ Data export and reporting capabilities
- ✅ Multi-zone comparative analysis
""")

st.caption("💡 **New in this version:** Auto-refresh, enhanced metrics, system overview, and CSV export functionality!")
