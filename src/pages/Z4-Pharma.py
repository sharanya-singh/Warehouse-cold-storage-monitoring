# COMPLETE Z4-Pharma.py with Alert Display, Notifications and Regulatory Compliance
import streamlit as st
import numpy as np
import pandas as pd
import altair as alt
import time
from datetime import datetime, timedelta

st.set_page_config(page_title="Z4-Pharma Monitor", layout="wide", page_icon="💊")

# === NOTIFICATION SYSTEM ===
def show_alert_notification(alert_type, message, zone="Z4-Pharma"):
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

            oscillator.frequency.setValueAtTime(900, audioContext.currentTime);
            gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);

            oscillator.start();
            oscillator.stop(audioContext.currentTime + 0.4);
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
def setup_threshold_configuration(zone_id="Z4-Pharma"):
    """Setup user-adjustable threshold configuration in sidebar using st.session_state."""
    defaults = {
        'temp_range': (2.0, 8.0),
        'humidity_range': (50, 60),
        'warning_buffer': 1.0,
        'alert_sensitivity': "Critical",
        'regulatory_compliance': "FDA CFR 21",
        'validation_required': True,
        'continuous_monitoring': True,
        'deviation_reporting': True,
        'data_quality': 99,
        'enable_sound': True,
        'enable_popup': True,
        'enable_email_alerts': True,
        'auto_refresh_interval': 15
    }
    sensitivity_options = ["Low", "Medium", "High", "Critical"]
    regulatory_options = ["FDA CFR 21", "EU GDP Guidelines", "ICH Q1A", "WHO TRS", "Custom"]
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

        st.subheader("🌡️ Temperature Thresholds")
        st.slider(
            "Optimal Temperature Range (°C)", -10.0, 15.0, step=0.2,
            key=prefix + "temp_range",
            help="Set the optimal temperature range for pharmaceutical storage"
        )
        st.slider(
            "Warning Buffer (±°C)", 0.2, 2.0, step=0.2,
            key=prefix + "warning_buffer",
            help="Temperature deviation before triggering warnings (critical for pharma)"
        )

        st.subheader("💧 Humidity Thresholds")
        st.slider(
            "Optimal Humidity Range (%)", 0, 100, step=5,
            key=prefix + "humidity_range",
            help="Set the optimal humidity range for pharmaceutical products"
        )

        st.subheader("🚨 Alert Configuration")
        st.selectbox(
            "Alert Sensitivity", options=sensitivity_options,
            key=prefix + "alert_sensitivity",
            help="Controls how quickly alerts are triggered for pharmaceutical safety"
        )

        st.subheader("💊 Pharmaceutical Settings")
        st.selectbox(
            "Regulatory Standard", options=regulatory_options,
            key=prefix + "regulatory_compliance",
            help="Select applicable regulatory standard"
        )
        st.checkbox("Validation Required", key=prefix + "validation_required", help="Enable for GxP compliance")
        st.checkbox("Continuous Monitoring", key=prefix + "continuous_monitoring", help="24/7 continuous temperature monitoring")
        st.checkbox("Automatic Deviation Reporting", key=prefix + "deviation_reporting", help="Automatically generate deviation reports")
        st.slider(
            "Data Quality Threshold (%)", 80, 100, step=1,
            key=prefix + "data_quality",
            help="Minimum data quality required for pharmaceutical monitoring"
        )

        st.subheader("🔔 Notification Settings")
        st.checkbox("Enable Sound Alerts", key=prefix + "enable_sound", help="Play sound when critical alerts occur")
        st.checkbox("Enable Popup Notifications", key=prefix + "enable_popup", help="Show popup notifications for all alerts")
        st.checkbox("Enable Email Alerts", key=prefix + "enable_email_alerts", help="Send email notifications for critical events")

        st.subheader("🔄 Live Update Settings")
        st.slider(
            "Auto-Refresh Interval (seconds)", 10, 60,
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
        'regulatory_compliance': st.session_state[prefix + 'regulatory_compliance'],
        'validation_required': st.session_state[prefix + 'validation_required'],
        'continuous_monitoring': st.session_state[prefix + 'continuous_monitoring'],
        'deviation_reporting': st.session_state[prefix + 'deviation_reporting'],
        'enable_sound': st.session_state[prefix + 'enable_sound'],
        'enable_popup': st.session_state[prefix + 'enable_popup'],
        'enable_email_alerts': st.session_state[prefix + 'enable_email_alerts'],
        'auto_refresh_interval': st.session_state[prefix + 'auto_refresh_interval']
    }

def apply_custom_alert_logic(df, config):
    """Apply custom alert logic based on user configuration - stricter for pharma"""
    if df.empty:
        return df

    enhanced_df = df.copy()
    temp_min = config['temp_min']
    temp_max = config['temp_max']
    warning_buffer = config['warning_buffer']

    def calculate_alert_status(temp, humidity=None):
        # Pharmaceutical-grade stricter thresholds
        if temp < (temp_min - warning_buffer * 1.5) or temp > (temp_max + warning_buffer * 1.5):
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

    # Pharmaceutical sensitivity - stricter than other zones
    sensitivity_mapping = {
        'Low': ['critical'],
        'Medium': ['critical', 'alert'],
        'High': ['critical', 'alert', 'warning'],
        'Critical': ['critical', 'alert', 'warning']  # Most sensitive
    }

    alert_triggers = sensitivity_mapping.get(config['alert_sensitivity'], ['critical', 'alert', 'warning'])
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
        return df[df['zone_id'] == "Z4-Pharma"]
    except FileNotFoundError:
        st.error("📁 Data file not found. Please ensure the CSV file exists.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Error loading data: {e}")
        return pd.DataFrame()

def calculate_regulatory_compliance_score(zone_data, config):
    """Calculate regulatory compliance score for pharmaceutical storage"""
    if zone_data.empty:
        return 0

    temp_readings = zone_data['temperature']

    # Strict compliance scoring
    in_range_temps = len(temp_readings[
        (temp_readings >= config['temp_min']) & 
        (temp_readings <= config['temp_max'])
    ])
    compliance_rate = (in_range_temps / len(temp_readings)) * 100

    # Deviations impact compliance heavily
    critical_deviations = len(temp_readings[
        (temp_readings < config['temp_min'] - config['warning_buffer']) |
        (temp_readings > config['temp_max'] + config['warning_buffer'])
    ])

    # Penalize any critical deviations severely
    deviation_penalty = min(critical_deviations * 10, 50)  # Up to 50% penalty

    final_score = max(0, compliance_rate - deviation_penalty)
    return final_score

def display_threshold_aware_metrics(df, zone_id="Z4-Pharma", config=None):
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

        if alert_temp < config['temp_min'] - config['warning_buffer'] * 1.5:
            show_alert_notification("critical", f"PHARMACEUTICAL CRITICAL: Temperature too low: {alert_temp:.1f}°C - Product integrity at risk!", zone_id)
        elif alert_temp > config['temp_max'] + config['warning_buffer'] * 1.5:
            show_alert_notification("critical", f"PHARMACEUTICAL CRITICAL: Temperature too high: {alert_temp:.1f}°C - Product degradation risk!", zone_id)
        elif alert_temp < config['temp_min'] or alert_temp > config['temp_max']:
            show_alert_notification("alert", f"PHARMACEUTICAL ALERT: Temperature deviation: {alert_temp:.1f}°C - Immediate action required!", zone_id)

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
                <p style="margin: 0;">Pharmaceutical Grade Monitoring</p>
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
        if config:
            compliance_score = calculate_regulatory_compliance_score(zone_data.tail(100), config)
            st.metric("📋 Compliance", f"{compliance_score:.0f}%")
        else:
            data_age = (datetime.now() - current['timestamp']).total_seconds() / 60
            st.metric("🕐 Data Age", f"{data_age:.1f} min")

    return zone_data

def display_regulatory_compliance(zone_data, config):
    """Display regulatory compliance dashboard"""
    st.header("📋 Regulatory Compliance Dashboard")

    compliance_score = calculate_regulatory_compliance_score(zone_data, config)
    temp_readings = zone_data['temperature']

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("🏛️ Regulatory Standard", config.get('regulatory_compliance', 'FDA CFR 21'))
        if config.get('validation_required', True):
            st.success("✅ Validation Required")
        else:
            st.info("ℹ️ Validation Optional")

    with col2:
        st.metric("📊 Compliance Score", f"{compliance_score:.1f}%")
        if compliance_score >= 99:
            st.success("Excellent compliance")
        elif compliance_score >= 95:
            st.warning("Good compliance")
        else:
            st.error("Poor compliance")

    with col3:
        deviations = len(temp_readings[
            (temp_readings < config['temp_min']) |
            (temp_readings > config['temp_max'])
        ])
        st.metric("⚠️ Total Deviations", deviations)

        if deviations == 0:
            st.success("No deviations")
        elif deviations <= 5:
            st.warning("Few deviations")
        else:
            st.error("Multiple deviations")

    with col4:
        critical_deviations = len(temp_readings[
            (temp_readings < config['temp_min'] - config['warning_buffer']) |
            (temp_readings > config['temp_max'] + config['warning_buffer'])
        ])
        st.metric("🚨 Critical Deviations", critical_deviations)

        if critical_deviations == 0:
            st.success("No critical events")
        else:
            st.error("Critical events detected!")

    # Compliance timeline
    st.subheader("📈 Compliance Timeline")

    # Calculate hourly compliance
    zone_data_hourly = zone_data.set_index('timestamp').resample('1H').agg({
        'temperature': ['mean', 'min', 'max', 'count']
    }).reset_index()

    zone_data_hourly.columns = ['timestamp', 'temp_mean', 'temp_min', 'temp_max', 'reading_count']

    # Calculate compliance for each hour
    zone_data_hourly['compliant'] = (
        (zone_data_hourly['temp_min'] >= config['temp_min']) &
        (zone_data_hourly['temp_max'] <= config['temp_max'])
    ).astype(int) * 100

    if not zone_data_hourly.empty:
        compliance_chart = alt.Chart(zone_data_hourly).mark_bar().encode(
            x=alt.X('timestamp:T', title='Time'),
            y=alt.Y('compliant:Q', title='Compliance (%)'),
            color=alt.Color('compliant:Q', 
                           scale=alt.Scale(domain=[0, 100], range=['red', 'green']),
                           legend=None),
            tooltip=['timestamp:T', 'compliant:Q', 'temp_mean:Q']
        ).properties(
            height=300,
            title='Hourly Compliance Status'
        )

        st.altair_chart(compliance_chart, use_container_width=True)

    # Generate deviation report if enabled
    if config.get('deviation_reporting', True) and deviations > 0:
        st.subheader("📝 Automated Deviation Report")

        deviation_data = zone_data[
            (zone_data['temperature'] < config['temp_min']) |
            (zone_data['temperature'] > config['temp_max'])
        ]

        if not deviation_data.empty:
            st.error(f"🚨 {len(deviation_data)} temperature deviations detected!")

            deviation_summary = deviation_data[['timestamp', 'temperature']].copy()
            deviation_summary['deviation_type'] = deviation_summary['temperature'].apply(
                lambda temp: 'BELOW MINIMUM' if temp < config['temp_min'] else 'ABOVE MAXIMUM'
            )
            deviation_summary['deviation_magnitude'] = deviation_summary.apply(
                lambda row: abs(row['temperature'] - config['temp_min']) if row['temperature'] < config['temp_min']
                           else abs(row['temperature'] - config['temp_max']), axis=1
            )

            st.dataframe(
                deviation_summary.head(10),
                use_container_width=True,
                hide_index=True,
                column_config={
                    "timestamp": "Deviation Time",
                    "temperature": st.column_config.NumberColumn("Temperature (°C)", format="%.2f"),
                    "deviation_type": "Deviation Type",
                    "deviation_magnitude": st.column_config.NumberColumn("Magnitude (°C)", format="%.2f")
                }
            )

def display_alert_history(zone_data, config):
    """Display detailed alert history with regulatory context"""
    st.header("🚨 Alert History & Regulatory Impact")

    # Get all alerts
    alerts = zone_data[zone_data['alert_status'] == 'alert']

    if alerts.empty:
        st.success("✅ No alerts recorded - pharmaceutical storage operating within compliance!")
        return

    # Alert summary with regulatory context
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_alerts = len(alerts)
        st.metric("📊 Total Alerts", total_alerts)

    with col2:
        recent_alerts = len(alerts.tail(24))  # Last 24 readings
        st.metric("⏰ Recent (24h)", recent_alerts)

    with col3:
        # Regulatory impact assessment
        high_impact_alerts = len(alerts[
            (alerts['temperature'] < config['temp_min'] - config['warning_buffer']) |
            (alerts['temperature'] > config['temp_max'] + config['warning_buffer'])
        ])
        st.metric("⚠️ Regulatory Impact", high_impact_alerts)

    with col4:
        alert_rate = (len(alerts) / len(zone_data) * 100) if len(zone_data) > 0 else 0
        st.metric("📈 Alert Rate", f"{alert_rate:.1f}%")

    # Recent alerts table with regulatory severity
    st.subheader("📋 Recent Alert Events")

    recent_alerts = alerts.tail(10)
    if not recent_alerts.empty:
        alert_display = recent_alerts[['timestamp', 'temperature', 'humidity', 'alert_status']].copy()
        alert_display['timestamp'] = alert_display['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
        alert_display['regulatory_severity'] = alert_display['temperature'].apply(
            lambda temp: 'CRITICAL REGULATORY BREACH' if temp < config['temp_min'] - config['warning_buffer'] * 1.5 or 
                                                        temp > config['temp_max'] + config['warning_buffer'] * 1.5
                         else 'HIGH REGULATORY RISK' if temp < config['temp_min'] - config['warning_buffer'] or 
                                                       temp > config['temp_max'] + config['warning_buffer']
                         else 'MODERATE RISK'
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
                "regulatory_severity": "Regulatory Impact"
            }
        )

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
        # Call the existing display functions
        zone_data = display_threshold_aware_metrics(df_processed, "Z4-Pharma", config)

        if not zone_data.empty:
            display_regulatory_compliance(zone_data, config)
            display_alert_history(zone_data, config)

            # Temperature monitoring with compliance zones
            st.header("📊 Temperature Monitoring with Compliance Zones")
            chart_data = zone_data.tail(100)
            temp_chart = alt.Chart(chart_data).mark_line(point=True, color='purple', strokeWidth=2).encode(
                x=alt.X('timestamp:T', title='Time'), y=alt.Y('temperature:Q', title='Temperature (°C)'),
                tooltip=['timestamp:T', 'temperature:Q', 'alert_status:N']
            )
            compliance_band = alt.Chart(pd.DataFrame({'temp_min': [config['temp_min']], 'temp_max': [config['temp_max']]})).mark_rect(opacity=0.2, color='green').encode(
                y='temp_min:Q', y2='temp_max:Q'
            )
            st.altair_chart(compliance_band + temp_chart, use_container_width=True)

            # Recent data table
            st.header("📊 Recent Readings")
            recent_data = zone_data.tail(15)[['timestamp', 'temperature', 'humidity', 'alert_status']].copy()
            recent_data['timestamp'] = recent_data['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
            st.dataframe(recent_data, use_container_width=True, hide_index=True, column_config={
                "timestamp": "Timestamp", "temperature": st.column_config.NumberColumn("Temperature (°C)", format="%.3f"),
                "humidity": st.column_config.NumberColumn("Humidity (%)", format="%.1f"), "alert_status": "Status"
            })

# === MAIN APPLICATION LOGIC ===
st.title("💊 Z4-Pharma Live Monitor")
st.markdown("**Real-time monitoring for pharmaceutical storage**")

user_config = setup_threshold_configuration()
auto_refresh = st.toggle("🔄 Auto-Refresh Dashboard", value=True)
placeholder = st.empty()

if auto_refresh:
    while True:
        st.cache_data.clear()
        draw_dashboard(placeholder, user_config)
        with st.empty():
            for seconds in range(user_config['auto_refresh_interval'], 0, -1):
                st.markdown(f"**Next refresh in {seconds} seconds...**")
                time.sleep(1)
            st.markdown("**Refreshing data...**")
else:
    st.cache_data.clear()
    draw_dashboard(placeholder, user_config)
    st.warning("Auto-refresh is off. Toggle it on to see live updates.")
