# Enhanced Z1-Freezer.py with User-Adjustable Threshold Configuration
import streamlit as st
import numpy as np
import pandas as pd
import altair as alt
import time
from datetime import datetime, timedelta

# === THRESHOLD CONFIGURATION SYSTEM ===
def setup_threshold_configuration(zone_id="Z1-Freezer"):
    """Setup user-adjustable threshold configuration in sidebar"""
    
    # Default optimal ranges for each zone
    default_ranges = {
        'Z1-Freezer': {'temp_min': -22, 'temp_max': -18, 'humidity_min': 50, 'humidity_max': 70},
        'Z2-Chiller': {'temp_min': 2, 'temp_max': 4, 'humidity_min': 70, 'humidity_max': 80},
        'Z3-Produce': {'temp_min': 8, 'temp_max': 12, 'humidity_min': 80, 'humidity_max': 95},
        'Z4-Pharma': {'temp_min': -5, 'temp_max': -2, 'humidity_min': 50, 'humidity_max': 60}
    }
    
    defaults = default_ranges.get(zone_id, {'temp_min': -22, 'temp_max': -18, 'humidity_min': 50, 'humidity_max': 70})
    
    with st.sidebar:
        st.markdown("---")
        st.header("⚙️ Threshold Configuration")
        st.markdown("**Customize monitoring parameters for optimal performance**")
        
        # Temperature threshold sliders
        st.subheader("🌡️ Temperature Thresholds")
        
        # Create wider range for sliders based on zone type
        if zone_id == 'Z1-Freezer':
            slider_min, slider_max = -30, -10
        elif zone_id == 'Z2-Chiller':
            slider_min, slider_max = -5, 10
        elif zone_id == 'Z3-Produce':
            slider_min, slider_max = 0, 20
        elif zone_id == 'Z4-Pharma':
            slider_min, slider_max = -10, 5
        else:
            slider_min, slider_max = -30, 20
        
        # Temperature range slider
        temp_range = st.slider(
            "Optimal Temperature Range (°C)",
            min_value=float(slider_min),
            max_value=float(slider_max),
            value=(float(defaults['temp_min']), float(defaults['temp_max'])),
            step=0.5,
            key=f"temp_range_{zone_id}",
            help="Set the optimal temperature range for this zone"
        )
        
        # Warning buffer slider
        warning_buffer = st.slider(
            "Warning Buffer (±°C)",
            min_value=0.5,
            max_value=5.0,
            value=2.0,
            step=0.5,
            key=f"warning_buffer_{zone_id}",
            help="Temperature deviation before triggering warnings"
        )
        
        # Humidity thresholds (if applicable)
        st.subheader("💧 Humidity Thresholds")
        
        humidity_range = st.slider(
            "Optimal Humidity Range (%)",
            min_value=0,
            max_value=100,
            value=(defaults['humidity_min'], defaults['humidity_max']),
            step=5,
            key=f"humidity_range_{zone_id}",
            help="Set the optimal humidity range for this zone"
        )
        
        # Alert sensitivity
        st.subheader("🚨 Alert Configuration")
        
        alert_sensitivity = st.selectbox(
            "Alert Sensitivity",
            options=["Low", "Medium", "High", "Critical"],
            index=1,  # Default to Medium
            key=f"alert_sensitivity_{zone_id}",
            help="Controls how quickly alerts are triggered"
        )
        
        # Data quality requirements
        data_quality_threshold = st.slider(
            "Data Quality Threshold (%)",
            min_value=80,
            max_value=100,
            value=95,
            step=1,
            key=f"data_quality_{zone_id}",
            help="Minimum data quality required for optimal performance"
        )
        
        # Configuration summary
        st.markdown("---")
        st.markdown("**📊 Current Configuration:**")
        st.markdown(f"""
        • **Temperature:** {temp_range[0]:.1f}°C to {temp_range[1]:.1f}°C  
        • **Warning Buffer:** ±{warning_buffer:.1f}°C  
        • **Humidity:** {humidity_range[0]}% to {humidity_range[1]}%  
        • **Alert Sensitivity:** {alert_sensitivity}  
        • **Data Quality:** {data_quality_threshold}%  
        """)
        
        # Reset to defaults button
        if st.button("🔄 Reset to Defaults", use_container_width=True):
            # This would reset session state values
            st.rerun()
        
        # Save configuration button
        if st.button("💾 Save Configuration", use_container_width=True, type="primary"):
            st.success("✅ Configuration saved!")
            # In a real app, this would save to database or config file
    
    # Return current configuration
    return {
        'temp_min': temp_range[0],
        'temp_max': temp_range[1],
        'warning_buffer': warning_buffer,
        'humidity_min': humidity_range[0],
        'humidity_max': humidity_range[1],
        'alert_sensitivity': alert_sensitivity,
        'data_quality_threshold': data_quality_threshold
    }

def apply_custom_alert_logic(df, config):
    """Apply custom alert logic based on user configuration"""
    
    if df.empty:
        return df
    
    # Create a copy to avoid modifying original data
    enhanced_df = df.copy()
    
    # Apply custom temperature thresholds
    temp_min = config['temp_min']
    temp_max = config['temp_max']
    warning_buffer = config['warning_buffer']
    
    # Calculate alert levels based on temperature
    def calculate_alert_status(temp, humidity=None):
        # Critical: way outside optimal range
        if temp < (temp_min - warning_buffer * 2) or temp > (temp_max + warning_buffer * 2):
            return 'critical'
        
        # Alert: outside optimal range but within warning buffer
        elif temp < (temp_min - warning_buffer) or temp > (temp_max + warning_buffer):
            return 'alert'
        
        # Warning: outside optimal range but within warning buffer
        elif temp < temp_min or temp > temp_max:
            return 'warning'
        
        # Normal: within optimal range
        else:
            return 'normal'
    
    # Apply custom alert logic
    enhanced_df['custom_alert_status'] = enhanced_df.apply(
        lambda row: calculate_alert_status(row['temperature'], row.get('humidity')), 
        axis=1
    )
    
    # Update original alert_status based on custom logic and sensitivity
    sensitivity_mapping = {
        'Low': ['critical'],
        'Medium': ['critical', 'alert'],
        'High': ['critical', 'alert', 'warning'],
        'Critical': ['critical', 'alert', 'warning']  # Most sensitive
    }
    
    alert_triggers = sensitivity_mapping.get(config['alert_sensitivity'], ['critical', 'alert'])
    
    enhanced_df['alert_status'] = enhanced_df['custom_alert_status'].apply(
        lambda status: 'alert' if status in alert_triggers else 'normal'
    )
    
    return enhanced_df

def get_zone_status_color_custom(temperature, alert_count, config):
    """Determine zone status using custom thresholds"""
    
    temp_min = config['temp_min']
    temp_max = config['temp_max']
    warning_buffer = config['warning_buffer']
    
    # Determine status based on custom thresholds
    if temp_min <= temperature <= temp_max and alert_count == 0:
        status = "optimal"
        bg_color = "linear-gradient(135deg, #d4edda 0%, #c3e6cb 50%, #b3d7c1 100%)"
        border_color = "#28a745"
        text_color = "#155724"
        status_emoji = "🟢"
        status_text = "Optimal"
    elif (temp_min - warning_buffer <= temperature <= temp_max + warning_buffer) and alert_count <= 2:
        status = "warning"
        bg_color = "linear-gradient(135deg, #fff3cd 0%, #ffeaa7 50%, #fdcb6e 100%)"
        border_color = "#ffc107"
        text_color = "#856404"
        status_emoji = "🟡"
        status_text = "Warning"
    else:
        status = "critical"
        bg_color = "linear-gradient(135deg, #f8d7da 0%, #f5b7b1 50%, #e74c3c 100%)"
        border_color = "#dc3545"
        text_color = "#721c24"
        status_emoji = "🔴"
        status_text = "Critical"
    
    return {
        'status': status,
        'bg_color': bg_color,
        'border_color': border_color,
        'text_color': text_color,
        'status_emoji': status_emoji,
        'status_text': status_text
    }

def display_threshold_aware_metrics(df, zone_id="Z1-Freezer", config=None):
    """Display metrics panel that adapts to custom thresholds"""
    
    zone_data = df[df['zone_id'] == zone_id].sort_values('timestamp') if 'zone_id' in df.columns else df.sort_values('timestamp')
    
    if len(zone_data) < 2:
        st.warning("⚠️ Insufficient data for trend analysis")
        return zone_data
    
    # Apply custom alert logic
    if config:
        zone_data = apply_custom_alert_logic(zone_data, config)
    
    current = zone_data.iloc[-1]
    previous = zone_data.iloc[-2]
    
    # Ensure we have temperature column
    if 'temperature' not in current:
        if 'value' in current:
            current['temperature'] = current['value']
            previous['temperature'] = previous['value']
        else:
            st.error("No temperature data found")
            return zone_data
    
    # Calculate metrics
    temp_change = current['temperature'] - previous['temperature']
    recent_alerts = len(zone_data.tail(12)[zone_data.tail(12)['alert_status'] == 'alert']) if len(zone_data) >= 12 else len(zone_data[zone_data['alert_status'] == 'alert'])
    
    # Get dynamic status colors using custom thresholds
    if config:
        status_info = get_zone_status_color_custom(current['temperature'], recent_alerts, config)
    else:
        # Fallback to default logic
        status_info = {
            'status': 'normal',
            'bg_color': 'linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%)',
            'border_color': '#28a745',
            'text_color': '#155724',
            'status_emoji': '🟢',
            'status_text': 'Normal'
        }
    
    # Display configuration-aware status banner
    config_text = ""
    if config:
        config_text = f" • Target: {config['temp_min']:.1f}°C to {config['temp_max']:.1f}°C"
    
    st.markdown(f"""
    <div style="background: {status_info['bg_color']}; padding: 20px; border-radius: 15px; border-left: 6px solid {status_info['border_color']}; box-shadow: 0 4px 8px rgba(0,0,0,0.15); margin-bottom: 20px;">
        <div style="display: flex; align-items: center; justify-content: space-between;">
            <div>
                <h3 style="margin: 0; color: {status_info['text_color']};">
                    {status_info['status_emoji']} Zone Status: {status_info['status_text']}
                </h3>
                <p style="margin: 5px 0 0 0; color: {status_info['text_color']}; opacity: 0.8;">
                    Current: {current['temperature']:.1f}°C{config_text} • {recent_alerts} active alerts
                </p>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 24px;">{status_info['status_emoji']}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Enhanced metrics with threshold awareness
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Temperature metric with custom threshold awareness
        temp_status = "🎯" if config and config['temp_min'] <= current['temperature'] <= config['temp_max'] else "⚠️"
        
        st.metric(
            f"🌡️ Current Temperature {temp_status}",
            f"{current['temperature']:.1f}°C",
            delta=f"{temp_change:+.1f}°C" if abs(temp_change) > 0.01 else None,
            delta_color="inverse" if temp_change > 0 else "normal"
        )
        
        # Show threshold info
        if config:
            st.caption(f"Target: {config['temp_min']:.1f}°C to {config['temp_max']:.1f}°C")
    
    with col2:
        humidity_val = current.get('humidity', np.nan)
        if pd.notna(humidity_val):
            # Humidity status with custom thresholds
            if config and config['humidity_min'] <= humidity_val <= config['humidity_max']:
                humidity_status = "✅"
                humidity_delta = "Optimal"
            else:
                humidity_status = "⚠️"
                humidity_delta = "Check Range"
            
            st.metric(f"💧 Humidity {humidity_status}", f"{humidity_val:.1f}%", delta=humidity_delta)
            
            if config:
                st.caption(f"Target: {config['humidity_min']}% to {config['humidity_max']}%")
        else:
            st.metric("💧 Current Humidity", "N/A")
    
    with col3:
        # Alert metric with sensitivity awareness
        if recent_alerts == 0:
            st.metric("🚨 Recent Alerts", recent_alerts, delta="All Clear! 🎉")
        elif recent_alerts <= 2:
            st.metric("🚨 Recent Alerts", recent_alerts, delta="Minor Issues ⚠️", delta_color="inverse")
        else:
            st.metric("🚨 Recent Alerts", recent_alerts, delta="Attention Needed! 🔴", delta_color="inverse")
        
        if config:
            st.caption(f"Sensitivity: {config['alert_sensitivity']}")
    
    with col4:
        # Compliance with custom thresholds
        total_readings = len(zone_data.tail(50))
        if config:
            # Calculate compliance based on custom thresholds
            in_range = len(zone_data.tail(50)[
                (zone_data.tail(50)['temperature'] >= config['temp_min']) & 
                (zone_data.tail(50)['temperature'] <= config['temp_max'])
            ])
            compliance = (in_range / total_readings * 100) if total_readings > 0 else 0
        else:
            alert_readings = len(zone_data.tail(50)[zone_data.tail(50)['alert_status'] == 'alert'])
            compliance = ((total_readings - alert_readings) / total_readings * 100) if total_readings > 0 else 0
        
        if compliance >= config.get('data_quality_threshold', 95) if config else 95:
            st.metric("✅ Compliance Score", f"{compliance:.1f}%", delta="Excellent 🏆")
        elif compliance >= 85:
            st.metric("✅ Compliance Score", f"{compliance:.1f}%", delta="Good 👍", delta_color="off")
        else:
            st.metric("✅ Compliance Score", f"{compliance:.1f}%", delta="Needs Work 📈", delta_color="inverse")
        
        if config:
            st.caption(f"Target: {config.get('data_quality_threshold', 95)}%+")
    
    return zone_data

# === ENHANCED AUTO-REFRESH WITH CONFIGURATION ===
def setup_enhanced_auto_refresh():
    """Enhanced auto-refresh with better status indicators"""
    
    with st.sidebar:
        st.markdown("---")
        st.header("🔄 Live Monitoring Controls")
        
        current_time = datetime.now()
        st.markdown("""
        <div style="background: linear-gradient(90deg, #e8f5e8, #d4edda); padding: 10px; border-radius: 8px; margin-bottom: 10px;">
            <div style="display: flex; align-items: center;">
                <div style="width: 10px; height: 10px; background: #28a745; border-radius: 50%; margin-right: 8px;"></div>
                <strong>System Status: Online</strong>
            </div>
            <small>Last sync: Just now</small>
        </div>
        """, unsafe_allow_html=True)
        
        auto_refresh = st.toggle("🔴 Enable Live Mode", value=False, key="auto_refresh_toggle")
        
        if auto_refresh:
            refresh_interval = st.selectbox(
                "📡 Update frequency:",
                options=[3, 5, 10, 30, 60],
                format_func=lambda x: f"Every {x} seconds",
                index=1,
                key="refresh_interval"
            )
            
            if 'last_refresh' not in st.session_state:
                st.session_state.last_refresh = time.time()
            
            time_since_refresh = time.time() - st.session_state.last_refresh
            
            if time_since_refresh >= refresh_interval:
                st.session_state.last_refresh = time.time()
                if 'refresh_count' not in st.session_state:
                    st.session_state.refresh_count = 1
                else:
                    st.session_state.refresh_count += 1
                st.rerun()
            
            remaining = refresh_interval - int(time_since_refresh)
            progress = min(time_since_refresh / refresh_interval, 1.0)
            
            st.markdown(f"""
            <div style="background: #f8f9fa; padding: 10px; border-radius: 8px; margin: 10px 0;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">
                    <small><strong>Next update:</strong></small>
                    <small style="color: #007bff;"><strong>{remaining}s</strong></small>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.progress(progress)
            
            if 'refresh_count' in st.session_state:
                st.caption(f"🔄 Updates: {st.session_state.refresh_count} | ⚡ Frequency: {refresh_interval}s")
        
        if st.button("🔄 Manual Refresh", use_container_width=True, type="secondary"):
            st.session_state.last_refresh = time.time()
            if 'refresh_count' in st.session_state:
                st.session_state.refresh_count += 1
            else:
                st.session_state.refresh_count = 1
            st.rerun()

# === DATA LOADING FUNCTIONS ===
@st.cache_data(ttl=30)
def load_data(file_path):
    try:
        df = pd.read_csv(file_path)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        if 'temperature' not in df.columns and 'value' in df.columns:
            df['temperature'] = df['value']
        return df
    except FileNotFoundError:
        st.error(f"Data file '{file_path}' not found!")
        return pd.DataFrame()

@st.cache_data
def get_forecasted_temp(zone_id):
    return {'forecasted_temp': [-19.415, -19.175, -18.875, -21.825, -22.238, -22.295, -21.62, -20.65, -19.98, -19.513]}

# === MAIN PAGE CONTENT ===

st.set_page_config(page_title="Z1-Freezer Dashboard", layout="wide", page_icon="🧊")

# Setup threshold configuration FIRST
user_config = setup_threshold_configuration("Z1-Freezer")

# Setup enhanced auto-refresh
setup_enhanced_auto_refresh()

# Header
st.title("🧊 Z1-Freezer Monitoring Dashboard")
st.markdown("**Real-time temperature and humidity monitoring with customizable thresholds**")
st.write("---")

# Load data
df_trends = load_data('simulated_warehouse_data_30min_demo.csv')

if df_trends.empty:
    st.error("Unable to load data. Please check if 'simulated_warehouse_data_30min_demo.csv' exists.")
    st.stop()

# Handle missing humidity data
if 'humidity' in df_trends.columns:
    df_trends['humidity'] = df_trends['humidity'].apply(lambda x: x if not pd.isna(x) else np.nan)

# Display Threshold-Aware Metrics Panel
zone_data = display_threshold_aware_metrics(df_trends, "Z1-Freezer", user_config)

st.write("---")

# Enhanced Historical Trends Chart with Custom Thresholds
st.header("📈 Real-Time Temperature Trends")

chart_data = zone_data.tail(100) if 'zone_id' in zone_data.columns else zone_data.tail(100)

if not chart_data.empty:
    current_temp = chart_data.iloc[-1]['temperature']
    recent_alerts = len(chart_data[chart_data['alert_status'] == 'alert']) if 'alert_status' in chart_data.columns else 0
    status_info = get_zone_status_color_custom(current_temp, recent_alerts, user_config)
    
    # Create chart with custom threshold bands
    base = alt.Chart(chart_data).encode(
        x=alt.X('timestamp:T', axis=alt.Axis(title='Time', labelAngle=-45)),
        tooltip=[
            alt.Tooltip('timestamp:T', title='Timestamp'),
            alt.Tooltip('temperature:Q', title='Temperature (°C)', format='.2f')
        ]
    )
    
    # Temperature line with dynamic color
    temp_line = base.mark_line(
        color=status_info['border_color'], 
        strokeWidth=4,
        point=alt.OverlayMarkDef(color=status_info['border_color'], size=50)
    ).encode(
        y=alt.Y('temperature:Q', 
               axis=alt.Axis(title='Temperature (°C)', titleColor=status_info['border_color']),
               scale=alt.Scale(domain=[-25, -15]))
    )
    
    # Add custom threshold bands
    optimal_band = alt.Chart(pd.DataFrame({
        'y_min': [user_config['temp_min']],
        'y_max': [user_config['temp_max']]
    })).mark_rect(opacity=0.3, color='green').encode(
        y=alt.value(user_config['temp_min']),
        y2=alt.value(user_config['temp_max'])
    )
    
    # Warning bands
    warning_min = user_config['temp_min'] - user_config['warning_buffer']
    warning_max = user_config['temp_max'] + user_config['warning_buffer']
    
    warning_band_low = alt.Chart(pd.DataFrame({'y': [warning_min]})).mark_rect(
        opacity=0.2, color='orange'
    ).encode(
        y=alt.value(warning_min),
        y2=alt.value(user_config['temp_min'])
    )
    
    warning_band_high = alt.Chart(pd.DataFrame({'y': [warning_max]})).mark_rect(
        opacity=0.2, color='orange'
    ).encode(
        y=alt.value(user_config['temp_max']),
        y2=alt.value(warning_max)
    )
    
    combined_chart = (optimal_band + warning_band_low + warning_band_high + temp_line).interactive().properties(height=400)
    st.altair_chart(combined_chart, use_container_width=True)
    
    # Chart status indicator with custom thresholds
    st.markdown(f"""
    <div style="text-align: center; padding: 10px; background: {status_info['bg_color']}; border-radius: 8px; margin-top: 10px;">
        <small><strong>Chart Status:</strong> {status_info['status_emoji']} {status_info['status_text']} • 
        Green: Optimal ({user_config['temp_min']:.1f}°C to {user_config['temp_max']:.1f}°C) • 
        Orange: Warning (±{user_config['warning_buffer']:.1f}°C buffer)</small>
    </div>
    """, unsafe_allow_html=True)

# Temperature Forecast Section (keeping existing)
st.header("🔮 Temperature Forecast")
st.markdown("**10-step temperature prediction for Z1-Freezer:**")

forecast_data = get_forecasted_temp("Z1-Freezer")
df_forecast = pd.DataFrame(forecast_data, index=range(1, 11))
df_forecast.index.name = "Step"

col1, col2 = st.columns([3, 1])

with col1:
    st.dataframe(df_forecast.style.format({'forecasted_temp': '{:.2f}°C'}), use_container_width=True)

with col2:
    avg_forecast = df_forecast['forecasted_temp'].mean()
    forecast_range = df_forecast['forecasted_temp'].max() - df_forecast['forecasted_temp'].min()
    
    st.metric("Avg Forecast", f"{avg_forecast:.1f}°C")
    st.metric("Range", f"±{forecast_range/2:.1f}°C")
    
    # Forecast compliance with custom thresholds
    forecast_compliance = len(df_forecast[
        (df_forecast['forecasted_temp'] >= user_config['temp_min']) & 
        (df_forecast['forecasted_temp'] <= user_config['temp_max'])
    ]) / len(df_forecast) * 100
    
    st.metric("Forecast Compliance", f"{forecast_compliance:.0f}%")

# Enhanced Alerts Log Section
st.header("🚨 Alert Management")

df_alerts = zone_data[zone_data['alert_status'] == 'alert'] if 'alert_status' in zone_data.columns else pd.DataFrame()

if not df_alerts.empty:
    alert_count = len(df_alerts)
    st.markdown(f"""
    <div style="background: #fff3cd; padding: 15px; border-radius: 10px; margin-bottom: 15px;">
        <h4 style="margin: 0;">🚨 {alert_count} Active Alerts</h4>
        <p style="margin: 5px 0 0 0;">Based on current threshold configuration (Sensitivity: {user_config['alert_sensitivity']})</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.dataframe(df_alerts.tail(10), use_container_width=True)
else:
    st.markdown("""
    <div style="background: linear-gradient(90deg, #d4edda, #c3e6cb); padding: 20px; border-radius: 10px; text-align: center;">
        <h3 style="margin: 0; color: #155724;">🎉 All Systems Normal</h3>
        <p style="margin: 5px 0 0 0; color: #155724;">No alerts with current threshold settings</p>
    </div>
    """, unsafe_allow_html=True)

# Enhanced Navigation
st.write("---")
st.markdown("### 🧭 Navigation")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🏠 System Overview", use_container_width=True, type="primary"):
        st.switch_page("pages/overview.py")

with col2:
    if st.button("🔧 Zone Selection", use_container_width=True):
        st.switch_page("app.py")

with col3:
    zone_data_csv = zone_data.to_csv(index=False)
    st.download_button(
        "📥 Export Data",
        data=zone_data_csv,
        file_name=f"Z1-Freezer_custom_config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
        use_container_width=True
    )

# Footer with configuration info
st.write("---")
st.markdown(f"""
<div style="text-align: center; color: #666; padding: 15px; background: #f8f9fa; border-radius: 10px;">
    <p><strong>🧊 Z1-Freezer Monitoring System</strong> | Custom Configuration Active</p>
    <small>Thresholds: {user_config['temp_min']:.1f}°C to {user_config['temp_max']:.1f}°C | 
    Sensitivity: {user_config['alert_sensitivity']} | 
    Last update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</small>
</div>
""", unsafe_allow_html=True)
