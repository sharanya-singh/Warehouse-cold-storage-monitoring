# COMPLETE Z1-Freezer.py with Alert Display and Notifications
import streamlit as st
import numpy as np
import pandas as pd
import altair as alt
import time
from datetime import datetime, timedelta

st.set_page_config(page_title="Z1-Freezer Monitor", layout="wide", page_icon="🧊")

# === NOTIFICATION SYSTEM ===
def show_alert_notification(alert_type, message, zone="Z1-Freezer"):
    """Display alert notifications with sound and visual alerts"""
    if alert_type == "critical":
        st.error(f"🚨 **CRITICAL ALERT - {zone}**: {message}")
        # Add sound notification (browser will play)
        st.markdown("""
        <script>
            // Create audio context for alert sound
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();

            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);

            oscillator.frequency.setValueAtTime(800, audioContext.currentTime);
            gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);

            oscillator.start();
            oscillator.stop(audioContext.currentTime + 0.2);
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
            'bg_color': 'linear-gradient(135deg, #1b5e20 0%, #2e7d32 50%, #388e3c 100%)',
            'border_color': '#4caf50', 'text_color': '#ffffff', 'status_emoji': '🟢', 'status_text': 'Optimal'
        }
    elif (temp_min - warning_buffer <= temperature <= temp_max + warning_buffer) and alert_count <= 2:
        return {
            'status': 'warning',
            'bg_color': 'linear-gradient(135deg, #e65100 0%, #f57c00 50%, #ff9800 100%)',
            'border_color': '#ffc107', 'text_color': '#ffffff', 'status_emoji': '🟡', 'status_text': 'Warning'
        }
    else:
        return {
            'status': 'critical',
            'bg_color': 'linear-gradient(135deg, #b71c1c 0%, #c62828 50%, #d32f2f 100%)',
            'border_color': '#f44336', 'text_color': '#ffffff', 'status_emoji': '🔴', 'status_text': 'Critical'
        }

# === THRESHOLD CONFIGURATION SYSTEM ===
def setup_threshold_configuration(zone_id="Z1-Freezer"):
    """Setup user-adjustable threshold configuration in sidebar using st.session_state."""
    # Define defaults for all settings
    defaults = {
        'temp_min': -22, 'temp_max': -18, 'humidity_min': 50, 'humidity_max': 70, 
        'warning_buffer': 2.0, 'alert_sensitivity': "Medium", 'data_quality': 95,

        'enable_sound': True, 'enable_popup': True, 'auto_refresh_interval': 10
    }
    sensitivity_options = ["Low", "Medium", "High", "Critical"]

    # Initialize session state keys if they don't exist
    if f"temp_range_{zone_id}" not in st.session_state:
        st.session_state[f"temp_range_{zone_id}"] = (float(defaults['temp_min']), float(defaults['temp_max']))
    if f"warning_buffer_{zone_id}" not in st.session_state:
        st.session_state[f"warning_buffer_{zone_id}"] = defaults['warning_buffer']
    if f"humidity_range_{zone_id}" not in st.session_state:
        st.session_state[f"humidity_range_{zone_id}"] = (defaults['humidity_min'], defaults['humidity_max'])
    if f"alert_sensitivity_{zone_id}" not in st.session_state:
        st.session_state[f"alert_sensitivity_{zone_id}"] = defaults['alert_sensitivity']
    if f"data_quality_{zone_id}" not in st.session_state:
        st.session_state[f"data_quality_{zone_id}"] = defaults['data_quality']
    if f"enable_sound_{zone_id}" not in st.session_state:
        st.session_state[f"enable_sound_{zone_id}"] = defaults['enable_sound']
    if f"enable_popup_{zone_id}" not in st.session_state:
        st.session_state[f"enable_popup_{zone_id}"] = defaults['enable_popup']
    if f"auto_refresh_interval_{zone_id}" not in st.session_state:
        st.session_state[f"auto_refresh_interval_{zone_id}"] = defaults['auto_refresh_interval']

    with st.sidebar:
        st.markdown("---")
        st.header("⚙️ Threshold Configuration")
        st.markdown("**Customize monitoring parameters for optimal performance**")

        st.subheader("🌡️ Temperature Thresholds")
        st.slider(
            "Optimal Temperature Range (°C)",
            min_value=-30.0,
            max_value=-10.0,
            step=0.5,
            key=f"temp_range_{zone_id}", # Using key links this to session_state
            help="Set the optimal temperature range for frozen storage"
        )
        st.slider(
            "Warning Buffer (±°C)",
            min_value=0.5,
            max_value=5.0,
            step=0.5,
            key=f"warning_buffer_{zone_id}",
            help="Temperature deviation before triggering warnings"
        )

        st.subheader("💧 Humidity Thresholds")
        st.slider(
            "Optimal Humidity Range (%)",
            min_value=0,
            max_value=100,
            step=5,
            key=f"humidity_range_{zone_id}",
            help="Set the optimal humidity range for this zone"
        )

        st.subheader("🚨 Alert Configuration")
        st.selectbox(
            "Alert Sensitivity",
            options=sensitivity_options,
            index=sensitivity_options.index(st.session_state[f"alert_sensitivity_{zone_id}"]),
            key=f"alert_sensitivity_{zone_id}",
            help="Controls how quickly alerts are triggered"
        )

        st.slider(
            "Data Quality Threshold (%)",
            min_value=80,
            max_value=100,
            step=1,
            key=f"data_quality_{zone_id}",
            help="Minimum data quality required for optimal performance"
        )

        st.subheader("🔔 Notification Settings")
        st.checkbox(
            "Enable Sound Alerts",
            key=f"enable_sound_{zone_id}",
            help="Play sound when critical alerts occur"
        )
        st.checkbox(
            "Enable Popup Notifications",
            key=f"enable_popup_{zone_id}",
            help="Show popup notifications for all alerts"
        )
        
        st.subheader("🔄 Live Update Settings")
        st.slider(
            "Auto-Refresh Interval (seconds)", 5, 60,
            key=f"auto_refresh_interval_{zone_id}",
            step=5,
            help="Set how often the dashboard updates automatically."
        )

        st.markdown("---")
        st.markdown("**📊 Current Configuration:**")
        st.markdown(f"""
        • **Temperature:** {st.session_state[f'temp_range_{zone_id}'][0]:.1f}°C to {st.session_state[f'temp_range_{zone_id}'][1]:.1f}°C
        • **Warning Buffer:** ±{st.session_state[f'warning_buffer_{zone_id}']:.1f}°C
        • **Humidity:** {st.session_state[f'humidity_range_{zone_id}'][0]}% to {st.session_state[f'humidity_range_{zone_id}'][1]}%
        • **Alert Sensitivity:** {st.session_state[f'alert_sensitivity_{zone_id}']}
        • **Data Quality:** {st.session_state[f'data_quality_{zone_id}']}%
        • **Sound Alerts:** {"Enabled" if st.session_state[f'enable_sound_{zone_id}'] else "Disabled"}
        • **Popup Notifications:** {"Enabled" if st.session_state[f'enable_popup_{zone_id}'] else "Disabled"}
        """)

        # Reset button clears the session state keys for this zone
        if st.button("🔄 Reset to Defaults", use_container_width=True):
            keys_to_delete = [
                f"temp_range_{zone_id}", f"warning_buffer_{zone_id}", f"humidity_range_{zone_id}",
                f"alert_sensitivity_{zone_id}", f"data_quality_{zone_id}",
                f"enable_sound_{zone_id}", f"enable_popup_{zone_id}"
            ]
            for key in keys_to_delete:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

        if st.button("💾 Save Configuration", use_container_width=True, type="primary"):
            st.success("✅ Configuration saved in session!")

    # Return the configuration from session state
    return {
        'temp_min': st.session_state[f'temp_range_{zone_id}'][0],
        'temp_max': st.session_state[f'temp_range_{zone_id}'][1],
        'warning_buffer': st.session_state[f'warning_buffer_{zone_id}'],
        'humidity_min': st.session_state[f'humidity_range_{zone_id}'][0],
        'humidity_max': st.session_state[f'humidity_range_{zone_id}'][1],
        'alert_sensitivity': st.session_state[f'alert_sensitivity_{zone_id}'],
        'data_quality_threshold': st.session_state[f'data_quality_{zone_id}'],
        'enable_sound': st.session_state[f'enable_sound_{zone_id}'],
        'enable_popup': st.session_state[f'enable_popup_{zone_id}'],
        'auto_refresh_interval': st.session_state[f'auto_refresh_interval_{zone_id}']
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
        return df[df['zone_id'] == "Z1-Freezer"]
    except FileNotFoundError:
        st.error("📁 Data file not found. Please ensure 'simulated_warehouse_data_30min_demo.csv' exists.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Error loading data: {e}")
        return pd.DataFrame()

def display_threshold_aware_metrics(df, zone_id="Z1-Freezer", config=None):
    """Display metrics panel with DARK backgrounds and alert notifications"""
    zone_data = df.sort_values('timestamp')

    if len(zone_data) < 2:
        st.warning("⚠️ Insufficient data for trend analysis")
        return zone_data

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
    recent_alerts = len(zone_data.tail(12)[zone_data.tail(12)['alert_status'] == 'alert']) if len(zone_data) >= 12 else len(zone_data[zone_data['alert_status'] == 'alert'])

    if config:
        status_info = get_zone_status_color_custom(current['temperature'], recent_alerts, config)
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
            show_alert_notification("critical", f"Temperature critically low: {alert_temp:.1f}°C", zone_id)
        elif alert_temp > config['temp_max'] + config['warning_buffer'] * 2:
            show_alert_notification("critical", f"Temperature critically high: {alert_temp:.1f}°C", zone_id)
        elif alert_temp < config['temp_min'] or alert_temp > config['temp_max']:
            show_alert_notification("alert", f"Temperature out of range: {alert_temp:.1f}°C", zone_id)

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
                <p style="margin: 0; color: {status_info['text_color']};">{recent_alerts} active alerts</p>
            </div>
            <div style="text-align: right; color: {status_info['text_color']};">
                <h4 style="margin: 0;">{status_info['status_text']}</h4>
                <p style="margin: 0;">Frozen Storage Monitoring</p>
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
        st.metric("🚨 Recent Alerts", f"{recent_alerts}")

    with col4:
        data_age = (datetime.now() - current['timestamp']).total_seconds() / 60
        st.metric("🕐 Data Age", f"{data_age:.1f} min")

    return zone_data

def display_alert_history(zone_data, config):
    """Display detailed alert history with notifications"""
    st.header("🚨 Alert History & Analysis")

    # Get all alerts
    alerts = zone_data[zone_data['alert_status'] == 'alert']

    if alerts.empty:
        st.success("✅ No alerts recorded - freezer operating normally!")
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
        critical_alerts = len(alerts[
            (alerts['temperature'] < config['temp_min'] - config['warning_buffer'] * 2) |
            (alerts['temperature'] > config['temp_max'] + config['warning_buffer'] * 2)
        ])
        st.metric("🔴 Critical", critical_alerts)

    with col4:
        alert_rate = (len(alerts) / len(zone_data) * 100) if len(zone_data) > 0 else 0
        st.metric("📈 Alert Rate", f"{alert_rate:.1f}%")

    # Recent alerts table
    st.subheader("📋 Recent Alert Events")

    recent_alerts = alerts.tail(10)
    if not recent_alerts.empty:
        alert_display = recent_alerts[['timestamp', 'temperature', 'humidity', 'alert_status']].copy()
        alert_display['timestamp'] = alert_display['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
        alert_display['alert_severity'] = alert_display['temperature'].apply(
            lambda temp: 'CRITICAL' if temp < config['temp_min'] - config['warning_buffer'] * 2 or 
                                     temp > config['temp_max'] + config['warning_buffer'] * 2 
                         else 'HIGH' if temp < config['temp_min'] - config['warning_buffer'] or 
                                       temp > config['temp_max'] + config['warning_buffer']
                         else 'MEDIUM'
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
                "alert_severity": "Severity"
            }
        )

        # Alert trend chart
        st.subheader("📈 Alert Trend Analysis")

        # Create alert timeline
        alert_timeline = alerts.set_index('timestamp').resample('1H')['temperature'].count().reset_index()
        alert_timeline.columns = ['hour', 'alert_count']

        if not alert_timeline.empty:
            alert_chart = alt.Chart(alert_timeline).mark_bar(color='red').encode(
                x=alt.X('hour:T', title='Time'),
                y=alt.Y('alert_count:Q', title='Alert Count'),
                tooltip=['hour:T', 'alert_count:Q']
            ).properties(
                height=300,
                title='Hourly Alert Frequency'
            )

            st.altair_chart(alert_chart, use_container_width=True)
    else:
        st.info("No recent alerts to display")

def display_temperature_charts(zone_data, config):
    """Display temperature monitoring charts with alert zones"""
    st.header("📊 Temperature Monitoring Charts")

    # Temperature trend with alert zones
    chart_data = zone_data.tail(200)  # Last 200 readings

    # Main temperature chart
    temp_chart = alt.Chart(chart_data).mark_line(
        point=True, 
        color='blue',
        strokeWidth=2
    ).encode(
        x=alt.X('timestamp:T', title='Time'),
        y=alt.Y('temperature:Q', 
               title='Temperature (°C)',
               scale=alt.Scale(domain=[
                   config['temp_min'] - 5, 
                   config['temp_max'] + 2
               ])),
        tooltip=['timestamp:T', 'temperature:Q', 'alert_status:N']
    )

    # Optimal range band
    optimal_band = alt.Chart(pd.DataFrame({
        'temp_min': [config['temp_min']] * len(chart_data),
        'temp_max': [config['temp_max']] * len(chart_data),
        'timestamp': chart_data['timestamp']
    })).mark_area(
        opacity=0.2,
        color='green'
    ).encode(
        x='timestamp:T',
        y='temp_min:Q',
        y2='temp_max:Q'
    )

    # Warning zones
    warning_upper = alt.Chart(pd.DataFrame({
        'warn_min': [config['temp_max']] * len(chart_data),
        'warn_max': [config['temp_max'] + config['warning_buffer']] * len(chart_data),
        'timestamp': chart_data['timestamp']
    })).mark_area(
        opacity=0.1,
        color='orange'
    ).encode(
        x='timestamp:T',
        y='warn_min:Q',
        y2='warn_max:Q'
    )

    warning_lower = alt.Chart(pd.DataFrame({
        'warn_min': [config['temp_min'] - config['warning_buffer']] * len(chart_data),
        'warn_max': [config['temp_min']] * len(chart_data),
        'timestamp': chart_data['timestamp']
    })).mark_area(
        opacity=0.1,
        color='orange'
    ).encode(
        x='timestamp:T',
        y='warn_min:Q',
        y2='warn_max:Q'
    )

    # Critical zones
    critical_upper = alt.Chart(pd.DataFrame({
        'crit_min': [config['temp_max'] + config['warning_buffer']] * len(chart_data),
        'crit_max': [config['temp_max'] + 5] * len(chart_data),
        'timestamp': chart_data['timestamp']
    })).mark_area(
        opacity=0.1,
        color='red'
    ).encode(
        x='timestamp:T',
        y='crit_min:Q',
        y2='crit_max:Q'
    )

    critical_lower = alt.Chart(pd.DataFrame({
        'crit_min': [config['temp_min'] - 5] * len(chart_data),
        'crit_max': [config['temp_min'] - config['warning_buffer']] * len(chart_data),
        'timestamp': chart_data['timestamp']
    })).mark_area(
        opacity=0.1,
        color='red'
    ).encode(
        x='timestamp:T',
        y='crit_min:Q',
        y2='crit_max:Q'
    )

    # Combine all layers
    combined_chart = critical_lower + critical_upper + warning_lower + warning_upper + optimal_band + temp_chart
    st.altair_chart(combined_chart, use_container_width=True)

    # Legend
    st.markdown("""
    **Chart Legend:**
    - 🟢 **Green Zone**: Optimal temperature range
    - 🟡 **Orange Zone**: Warning temperature range  
    - 🔴 **Red Zone**: Critical temperature range
    - 🔵 **Blue Line**: Actual temperature readings
    """)

def draw_dashboard(placeholder, config):
    """Draws the entire dashboard inside a placeholder."""
    # Load and process data
    df_original = load_zone_data()
    if df_original.empty:
        with placeholder.container():
            st.warning("⚠️ No data available. Is the data generator running?")
        return

    df_processed = apply_custom_alert_logic(df_original, config)

    # Use the placeholder's container to draw the content
    with placeholder.container():
        # Call the existing display functions, but they will draw inside this container
        zone_data = display_threshold_aware_metrics(df_processed, "Z1-Freezer", config)

        if not zone_data.empty:
            display_alert_history(zone_data, config)
            display_temperature_charts(zone_data, config)

            # Recent data table
            st.header("📊 Recent Readings")
            recent_data = zone_data.tail(15)[['timestamp', 'temperature', 'humidity', 'alert_status']].copy()
            recent_data['timestamp'] = recent_data['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
            st.dataframe(
                recent_data,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "timestamp": "Timestamp",
                    "temperature": st.column_config.NumberColumn("Temperature (°C)", format="%.3f"),
                    "humidity": st.column_config.NumberColumn("Humidity (%)", format="%.1f"),
                    "alert_status": "Status"
                }
            )

# === MAIN APPLICATION LOGIC ===

st.title("🧊 Z1-Freezer Live Monitor")
st.markdown("**Real-time monitoring for frozen goods storage zone**")

# Setup sidebar and get config. This runs only once per interaction.
user_config = setup_threshold_configuration()

# Main toggle for auto-refresh
auto_refresh = st.toggle("🔄 Auto-Refresh Dashboard", value=True)

# Create a single, persistent placeholder for the entire dashboard
placeholder = st.empty()

# This is the new "real-time" loop
if auto_refresh:
    while True: # Loop indefinitely while toggle is on
        st.cache_data.clear()
        draw_dashboard(placeholder, user_config)
        
        # Wait for the configured interval, showing a countdown
        with st.empty():
            for seconds in range(user_config['auto_refresh_interval'], 0, -1):
                st.markdown(f"**Next refresh in {seconds} seconds...**")
                time.sleep(1)
            st.markdown("**Refreshing data...**")
else:
    # If auto-refresh is off, draw the dashboard once and stop
    st.cache_data.clear()
    draw_dashboard(placeholder, user_config)
    st.warning("Auto-refresh is off. Toggle it on to see live updates.")