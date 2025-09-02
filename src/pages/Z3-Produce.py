# COMPLETE Z3-Produce.py with Alert Display and Notifications
import streamlit as st
import numpy as np
import pandas as pd
import altair as alt
import time
from datetime import datetime, timedelta

st.set_page_config(page_title="Z3-Produce Monitor", layout="wide", page_icon="🥬")

# --- Initialize Session State ---
if 'acknowledged_alerts' not in st.session_state:
    st.session_state.acknowledged_alerts = {
        'Z1-Freezer': None, 'Z2-Chiller': None, 'Z3-Produce': None, 'Z4-Pharma': None
    }

# === NOTIFICATION SYSTEM ===
def show_alert_notification(alert_type, message, zone="Z3-Produce"):
    """Display alert notifications with sound and visual alerts"""
    if alert_type == "critical":
        st.error(f"🚨 **CRITICAL ALERT - {zone}**: {message}")
        st.markdown("""
        <script>
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();

            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);

            oscillator.frequency.setValueAtTime(700, audioContext.currentTime);
            gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);

            oscillator.start();
            oscillator.stop(audioContext.currentTime + 0.25);
        </script>
        """, unsafe_allow_html=True)
    elif alert_type == "warning":
        st.warning(f"⚠️ **WARNING - {zone}**: {message}")
    elif alert_type == "alert":
        st.error(f"🔔 **ALERT - {zone}**: {message}")

# === DARK BACKGROUND FUNCTIONS FOR WHITE TEXT ===
def get_zone_status_color_custom(temperature, alert_count, config):
    """Determine zone status using DARK custom thresholds for WHITE TEXT"""
    temp_min = config['temp_min']
    temp_max = config['temp_max']
    warning_buffer = config['warning_buffer']

    if temp_min <= temperature <= temp_max and alert_count == 0:
        return {
            'status': 'optimal',
            'bg_color': 'linear-gradient(135deg, #1b5e20 0%, #2e7d32 50%, #388e3c 100%)',  # Dark green
            'border_color': '#4caf50',
            'text_color': '#ffffff',  # WHITE TEXT
            'status_emoji': '🟢',
            'status_text': 'Optimal'
        }
    elif (temp_min - warning_buffer <= temperature <= temp_max + warning_buffer) and alert_count <= 2:
        return {
            'status': 'warning',
            'bg_color': 'linear-gradient(135deg, #e65100 0%, #f57c00 50%, #ff9800 100%)',  # Dark orange
            'border_color': '#ffc107',
            'text_color': '#ffffff',  # WHITE TEXT
            'status_emoji': '🟡',
            'status_text': 'Warning'
        }
    else:
        return {
            'status': 'critical',
            'bg_color': 'linear-gradient(135deg, #b71c1c 0%, #c62828 50%, #d32f2f 100%)',  # Dark red
            'border_color': '#f44336',
            'text_color': '#ffffff',  # WHITE TEXT
            'status_emoji': '🔴',
            'status_text': 'Critical'
        }

# === THRESHOLD CONFIGURATION SYSTEM ===
def setup_threshold_configuration(zone_id="Z3-Produce"):
    """Setup user-adjustable threshold configuration in sidebar using st.session_state."""
    defaults = {
        'temp_range': (5.0, 10.0), 'humidity_range': (80, 95),
        'warning_buffer': 2.0, 'alert_sensitivity': "High", 'produce_type': "Mixed Vegetables",
        'freshness_monitoring': True, 'data_quality': 98, 'enable_sound': True,
        'enable_popup': True, 'auto_refresh_interval': 10
    }
    sensitivity_options = ["Low", "Medium", "High", "Critical"]
    produce_options = ["Mixed Vegetables", "Leafy Greens", "Root Vegetables", "Fruits", "Herbs"]
    prefix = f"{zone_id}_"

    # Initialize session state if it's empty for this zone
    if prefix + 'initialized' not in st.session_state:
        st.session_state[prefix + 'initialized'] = True
        for key, value in defaults.items():
            st.session_state[prefix + key] = value

    with st.sidebar:
        st.markdown("---")
        st.header("⚙️ Threshold Configuration")
        st.markdown("**Your changes will be saved automatically.**")

        st.slider(
            "Optimal Temperature Range (°C)", 0.0, 20.0,
            value=(st.session_state.get(prefix + 'temp_range', (5.0, 10.0))), # Corrected line
            step=0.5,
            key=prefix + "temp_range",
            help="Set the optimal temperature range for fresh produce storage"
        )

        st.slider(
            "Warning Buffer (±°C)", 0.5, 4.0, step=0.5,
            key=prefix + "warning_buffer",
            help="Temperature deviation before triggering warnings"
        )

        st.subheader("💧 Humidity Thresholds")
        st.slider(
            "Optimal Humidity Range (%)",
            0, 100,
            value=(st.session_state.get(prefix + 'humidity_range', (80, 95))), # Corrected line
            step=5,
            key=prefix + "humidity_range",
            help="Set the optimal humidity range for fresh produce"
        )

        st.subheader("🚨 Alert Configuration")
        st.selectbox(
            "Alert Sensitivity", options=sensitivity_options,
            key=prefix + "alert_sensitivity",
            help="Controls how quickly alerts are triggered for produce freshness"
        )

        st.subheader("🥬 Produce Settings")
        st.selectbox(
            "Primary Produce Type", options=produce_options,
            key=prefix + "produce_type",
            help="Select the primary type of produce stored"
        )
        st.checkbox(
            "Enable Freshness Scoring", key=prefix + "freshness_monitoring",
            help="Calculate produce freshness scores"
        )
        st.slider(
            "Data Quality Threshold (%)", 80, 100, step=1,
            key=prefix + "data_quality",
            help="Minimum data quality required for produce monitoring"
        )

        st.subheader("🔔 Notification Settings")
        st.checkbox(
            "Enable Sound Alerts", key=prefix + "enable_sound",
            help="Play sound when critical alerts occur"
        )
        st.checkbox(
            "Enable Popup Notifications", key=prefix + "enable_popup",
            help="Show popup notifications for all alerts"
        )

        st.subheader("🔄 Live Update Settings")
        st.slider(
            "Auto-Refresh Interval (seconds)", 5, 60,
            key=prefix + "auto_refresh_interval",
            step=5,
            help="Set how often the dashboard updates automatically."
        )

        st.markdown("---")
        if st.button("🔄 Reset to Defaults", use_container_width=True):
            for key, value in defaults.items():
                st.session_state[prefix + key] = value
            st.rerun()

        if st.button("💾 Save Configuration", use_container_width=True, type="primary"):
            st.success("✅ Configuration saved in session!")

    return {
        'temp_min': st.session_state[prefix + 'temp_range'][0],
        'temp_max': st.session_state[prefix + 'temp_range'][1],
        'warning_buffer': st.session_state[prefix + 'warning_buffer'],
        'humidity_min': st.session_state[prefix + 'humidity_range'][0],
        'humidity_max': st.session_state[prefix + 'humidity_range'][1],
        'alert_sensitivity': st.session_state[prefix + 'alert_sensitivity'],
        'data_quality_threshold': st.session_state[prefix + 'data_quality'],
        'produce_type': st.session_state[prefix + 'produce_type'],
        'freshness_monitoring': st.session_state[prefix + 'freshness_monitoring'],
        'enable_sound': st.session_state[prefix + 'enable_sound'],
        'enable_popup': st.session_state[prefix + 'enable_popup'],
        'auto_refresh_interval': st.session_state[prefix + 'auto_refresh_interval']
    }

def apply_custom_alert_logic(df, config):
    """Apply custom alert logic based on user configuration"""
    if df.empty:
        return df

    enhanced_df = df.copy()
    temp_min = config['temp_min']
    temp_max = config['temp_max']
    warning_buffer = config['warning_buffer']

    def calculate_alert_status(temp, humidity=None):
        if temp < (temp_min - warning_buffer * 2) or temp > (temp_max + warning_buffer * 2):
            return 'critical'
        elif temp < (temp_min - warning_buffer) or temp > (temp_max + warning_buffer):
            return 'alert'
        elif temp < temp_min or temp > temp_max:
            return 'warning'
        else:
            return 'normal'

    enhanced_df['custom_alert_status'] = enhanced_df.apply(
        lambda row: calculate_alert_status(row['temperature'], row.get('humidity')),
        axis=1
    )

    sensitivity_mapping = {
        'Low': ['critical'],
        'Medium': ['critical', 'alert'],
        'High': ['critical', 'alert', 'warning'],
        'Critical': ['critical', 'alert', 'warning']
    }

    alert_triggers = sensitivity_mapping.get(config['alert_sensitivity'], ['critical', 'alert'])
    enhanced_df['alert_status'] = enhanced_df['custom_alert_status'].apply(
        lambda status: 'alert' if status in alert_triggers else 'normal'
    )

    return enhanced_df

@st.cache_data
def load_zone_data():
    """Load data with proper error handling"""
    try:
        df = pd.read_csv('simulated_warehouse_data_30min_demo.csv', na_values=['NaN', '', 'nan'])
        df = df.dropna()  # Clean data
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df[df['zone_id'] == "Z3-Produce"]
    except FileNotFoundError:
        st.error("📁 Data file not found. Please ensure the CSV file exists.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Error loading data: {e}")
        return pd.DataFrame()

def calculate_freshness_score(zone_data, config):
    """Calculate produce freshness score based on temperature stability"""
    if zone_data.empty:
        return 0

    temp_readings = zone_data['temperature']
    humidity_readings = zone_data.get('humidity', pd.Series([85] * len(zone_data)))

    # Temperature score (50% of total)
    temp_optimal = len(temp_readings[
        (temp_readings >= config['temp_min']) & 
        (temp_readings <= config['temp_max'])
    ]) / len(temp_readings)

    # Temperature stability (25% of total)
    temp_stability = 1 / (1 + temp_readings.std())

    # Humidity score (25% of total)
    humidity_optimal = len(humidity_readings[
        (humidity_readings >= config['humidity_min']) & 
        (humidity_readings <= config['humidity_max'])
    ]) / len(humidity_readings)

    # Combined freshness score
    freshness_score = (temp_optimal * 0.5 + temp_stability * 0.25 + humidity_optimal * 0.25) * 100

    return min(100, max(0, freshness_score))

def display_threshold_aware_metrics(df, zone_id="Z3-Produce", config=None, active_alert_count=0):
    """Display metrics panel with DARK backgrounds and alert notifications"""
    zone_data = df[df['zone_id'] == zone_id].sort_values('timestamp') if 'zone_id' in df.columns else df.sort_values('timestamp')

    if len(zone_data) < 2:
        st.warning("⚠️ Insufficient data for trend analysis")
        return zone_data

    if config:
        zone_data = apply_custom_alert_logic(zone_data, config)

    current = zone_data.iloc[-1]
    previous = zone_data.iloc[-2]

    if 'temperature' not in current:
        if 'value' in current:
            current['temperature'] = current['value']
            previous['temperature'] = previous['value']
        else:
            st.error("No temperature data found")
            return zone_data

    temp_change = current['temperature'] - previous['temperature']

    if config:
        status_info = get_zone_status_color_custom(current['temperature'], active_alert_count, config)
    else:
        status_info = {
            'status': 'normal',
            'bg_color': 'linear-gradient(135deg, #1b5e20 0%, #2e7d32 100%)',
            'border_color': '#4caf50',
            'text_color': '#ffffff',
            'status_emoji': '🟢',
            'status_text': 'Normal'
        }

    # CHECK FOR ACTIVE ALERTS AND SHOW NOTIFICATIONS
    current_alerts = zone_data[zone_data['alert_status'] == 'alert'].tail(5)
    if not current_alerts.empty and config and config.get('enable_popup', True):
        latest_alert = current_alerts.iloc[-1]
        alert_temp = latest_alert['temperature']

        if alert_temp < config['temp_min'] - config['warning_buffer'] * 2:
            show_alert_notification("critical", f"Temperature critically low - produce may freeze: {alert_temp:.1f}°C", zone_id)
        elif alert_temp > config['temp_max'] + config['warning_buffer'] * 2:
            show_alert_notification("critical", f"Temperature critically high - produce freshness at risk: {alert_temp:.1f}°C", zone_id)
        elif alert_temp < config['temp_min'] or alert_temp > config['temp_max']:
            show_alert_notification("alert", f"Temperature affecting produce quality: {alert_temp:.1f}°C", zone_id)

    config_text = ""
    if config:
        config_text = f" • Target: {config['temp_min']:.1f}°C to {config['temp_max']:.1f}°C"

    # Status banner with DARK background and WHITE text
    st.markdown(f"""
    <div style="
        background: {status_info['bg_color']};
        border: 3px solid {status_info['border_color']};
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        color: {status_info['text_color']};
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
    ">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h2 style="margin: 0; color: {status_info['text_color']};">{status_info['status_emoji']} {status_info['status_text']}</h2>
                <h3 style="margin: 5px 0; color: {status_info['text_color']};">Current: {current['temperature']:.1f}°C{config_text}</h3>
                <p style="margin: 0; color: {status_info['text_color']};">{active_alert_count} active alerts</p>
            </div>
            <div style="text-align: right; color: {status_info['text_color']};">
                <h4 style="margin: 0;">{status_info['status_text']}</h4>
                <p style="margin: 0;">Fresh Produce Monitoring</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Current metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        trend_indicator = "🔼" if temp_change > 0.1 else "🔽" if temp_change < -0.1 else "➡️"
        st.metric(
            "🌡️ Temperature",
            f"{current['temperature']:.1f}°C",
            f"{temp_change:+.1f}°C {trend_indicator}"
        )

    with col2:
        humidity_val = current.get('humidity', 0)
        if pd.notna(humidity_val):
            st.metric("💧 Humidity", f"{humidity_val:.1f}%")
        else:
            st.metric("💧 Humidity", "N/A")

    with col3:
        st.metric("🚨 Recent Alerts", f"{active_alert_count}")

    with col4:
        if config and config.get('freshness_monitoring', True):
            freshness = calculate_freshness_score(zone_data.tail(50), config)
            st.metric("🥬 Freshness Score", f"{freshness:.0f}/100")
        else:
            data_age = (datetime.now() - current['timestamp']).total_seconds() / 60
            st.metric("🕐 Data Age", f"{data_age:.1f} min")

    return zone_data

def display_produce_analysis(zone_data, config):
    """Display produce-specific analysis"""
    st.header("🥬 Produce Quality Analysis")

    if not config.get('freshness_monitoring', True):
        st.info("Freshness monitoring is disabled. Enable it in the sidebar configuration.")
        return

    # Calculate freshness metrics
    freshness_score = calculate_freshness_score(zone_data, config)
    temp_stability = zone_data['temperature'].std()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("🌟 Overall Freshness", f"{freshness_score:.0f}/100")
        if freshness_score >= 90:
            st.success("Excellent quality")
        elif freshness_score >= 75:
            st.info("Good quality")
        elif freshness_score >= 60:
            st.warning("Fair quality")
        else:
            st.error("Poor quality")

    with col2:
        # Estimate shelf life impact
        if freshness_score >= 90:
            shelf_impact = "Optimal"
            color = "success"
        elif freshness_score >= 75:
            shelf_impact = "Good"
            color = "info"
        elif freshness_score >= 60:
            shelf_impact = "Reduced"
            color = "warning"
        else:
            shelf_impact = "Poor"
            color = "error"

        st.metric("📅 Shelf Life", shelf_impact)
        getattr(st, color)(f"Storage conditions: {shelf_impact}")

    with col3:
        # Temperature consistency
        consistency = "Excellent" if temp_stability <= 0.5 else "Good" if temp_stability <= 1.0 else "Fair" if temp_stability <= 2.0 else "Poor"
        st.metric("🎯 Consistency", consistency)
        st.info(f"Std Dev: ±{temp_stability:.2f}°C")

    with col4:
        # Produce type specific info
        produce_info = {
            "Mixed Vegetables": {"optimal_days": "7-14", "temp_sensitive": "Medium"},
            "Leafy Greens": {"optimal_days": "5-7", "temp_sensitive": "High"},
            "Root Vegetables": {"optimal_days": "14-30", "temp_sensitive": "Low"},
            "Fruits": {"optimal_days": "7-21", "temp_sensitive": "Medium"},
            "Herbs": {"optimal_days": "3-7", "temp_sensitive": "Very High"}
        }

        produce_type = config.get('produce_type', 'Mixed Vegetables')
        info = produce_info.get(produce_type, produce_info['Mixed Vegetables'])

        st.metric("📦 Produce Type", produce_type)
        st.info(f"Expected shelf life: {info['optimal_days']} days")

def display_alert_history(zone_data, config):
    """Display detailed alert history with notifications"""
    st.header("🚨 Alert History & Analysis")

    # Get all alerts
    alerts = zone_data[zone_data['alert_status'] == 'alert']

    if alerts.empty:
        st.success("✅ No alerts recorded - produce storage operating optimally!")
        return

    # Alert summary
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_alerts = len(alerts)
        st.metric("📊 Total Alerts", total_alerts)

    with col2:
        recent_alerts = len(alerts.tail(24))  # Last 24 readings
        st.metric("⏰ Recent (24h)", recent_alerts)

    with col3:
        # Quality impact assessment
        high_impact_alerts = len(alerts[
            (alerts['temperature'] < config['temp_min'] - 1) |
            (alerts['temperature'] > config['temp_max'] + 1)
        ])
        st.metric("⚠️ Quality Impact", high_impact_alerts)

    with col4:
        alert_rate = (len(alerts) / len(zone_data) * 100) if len(zone_data) > 0 else 0
        st.metric("📈 Alert Rate", f"{alert_rate:.1f}%")

    # Recent alerts table with produce-specific context
    st.subheader("📋 Recent Alert Events")

    recent_alerts = alerts.tail(10)
    if not recent_alerts.empty:
        alert_display = recent_alerts[['timestamp', 'temperature', 'humidity', 'alert_status']].copy()
        alert_display['timestamp'] = alert_display['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
        alert_display['quality_impact'] = alert_display['temperature'].apply(
            lambda temp: 'HIGH IMPACT' if temp < config['temp_min'] - 2 or temp > config['temp_max'] + 2
                         else 'MEDIUM IMPACT' if temp < config['temp_min'] - 1 or temp > config['temp_max'] + 1
                         else 'LOW IMPACT'
        )

        st.dataframe(
            alert_display,
            use_container_width=True,
            hide_index=True,
            column_config={
                "timestamp": "Timestamp",
                "temperature": st.column_config.NumberColumn("Temperature (°C)", format="%.2f"),
                "humidity": st.column_config.NumberColumn("Humidity (%)", format="%.1f"),
                "alert_status": "Status",
                "quality_impact": "Quality Impact"
            }
        )

def draw_dashboard(placeholder, config):
    """Draws the entire dashboard inside a placeholder."""
    # Load and process data
    df_original = load_zone_data()
    if df_original.empty:
        placeholder.warning("⚠️ No data available.")
        return

    zone_id = "Z3-Produce"
    df_processed = apply_custom_alert_logic(df_original, config)
    
    acknowledged_ts = st.session_state.acknowledged_alerts.get(zone_id)
    unacknowledged_data = df_processed[df_processed['timestamp'] > acknowledged_ts] if acknowledged_ts else df_processed

    active_alerts_df = unacknowledged_data[unacknowledged_data['alert_status'] == 'alert']
    active_alert_count = len(active_alerts_df)

    # Use the placeholder's container to draw the content
    with placeholder.container():
        # Display acknowledgement button if there are active alerts
        if active_alert_count > 0:
            st.error(f"🚨 **{active_alert_count} unacknowledged alerts!**")
            if st.button(f"✅ Acknowledge & Clear Alerts for {zone_id}"):
                st.session_state.acknowledged_alerts[zone_id] = active_alerts_df['timestamp'].max()
                st.rerun()

        # Call the existing display functions
        zone_data = display_threshold_aware_metrics(df_processed, zone_id, config, active_alert_count=active_alert_count)

        if not zone_data.empty:
            display_produce_analysis(zone_data, config)
            display_alert_history(zone_data, config)

            # Environmental monitoring charts
            st.header("📊 Environmental Monitoring")
            chart_data = zone_data.tail(100)
            temp_chart = alt.Chart(chart_data).mark_line(point=True, color='green', strokeWidth=2).encode(
                x=alt.X('timestamp:T', title='Time'), y=alt.Y('temperature:Q', title='Temperature (°C)'),
                tooltip=['timestamp:T', 'temperature:Q', 'alert_status:N']
            )
            humidity_chart = alt.Chart(chart_data).mark_line(point=True, color='blue', strokeWidth=2).encode(
                x=alt.X('timestamp:T', title='Time'), y=alt.Y('humidity:Q', title='Humidity (%)'),
                tooltip=['timestamp:T', 'humidity:Q']
            )
            st.subheader("🌡️ Temperature Trend")
            st.altair_chart(temp_chart, use_container_width=True)
            st.subheader("💧 Humidity Trend")
            st.altair_chart(humidity_chart, use_container_width=True)

            # Recent data table
            st.header("📊 Recent Readings")
            recent_data = zone_data.tail(15)[['timestamp', 'temperature', 'humidity', 'alert_status']].copy()
            recent_data['timestamp'] = recent_data['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
            st.dataframe(recent_data, use_container_width=True, hide_index=True, column_config={
                "timestamp": "Timestamp", "temperature": st.column_config.NumberColumn("Temperature (°C)", format="%.2f"),
                "humidity": st.column_config.NumberColumn("Humidity (%)", format="%.1f"), "alert_status": "Status"
            })

# === MAIN APPLICATION LOGIC ===
st.title("🥬 Z3-Produce Live Monitor")
st.markdown("**Real-time monitoring for fresh produce storage with quality analysis and alerts**")

user_config = setup_threshold_configuration()
auto_refresh = st.toggle("🔄 Auto-Refresh Dashboard", value=True)
placeholder = st.empty()

if auto_refresh:
    timer_placeholder = st.empty()
    while True:
        st.cache_data.clear()
        draw_dashboard(placeholder, user_config)
        for seconds in range(user_config['auto_refresh_interval'], 0, -1):
            timer_placeholder.markdown(f"**Next refresh in {seconds} seconds...**")
            time.sleep(1)
        timer_placeholder.empty()
else:
    st.cache_data.clear()
    draw_dashboard(placeholder, user_config)
    st.warning("Auto-refresh is off.")