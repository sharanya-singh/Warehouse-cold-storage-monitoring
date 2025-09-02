# TRULY COMPLETE Overview.py with Dark Backgrounds and ALL Functionality
import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
from datetime import datetime, timedelta
import time

st.set_page_config(page_title="System Overview", layout="wide", page_icon="📊")

# === DARK BACKGROUND FUNCTIONS FOR WHITE TEXT ===
def get_zone_status_color(temperature, alert_count, zone_id):
    """Determine zone status color using DARK backgrounds for WHITE TEXT"""
    zone_ranges = {
        'Z1-Freezer': {'temp_min': -22, 'temp_max': -18},
        'Z2-Chiller': {'temp_min': 2, 'temp_max': 5},
        'Z3-Produce': {'temp_min': 5, 'temp_max': 10},
        'Z4-Pharma': {'temp_min': 2, 'temp_max': 8}
    }

    optimal_range = zone_ranges.get(zone_id, {'temp_min': 0, 'temp_max': 5})
    temp_min, temp_max = optimal_range['temp_min'], optimal_range['temp_max']

    if temp_min <= temperature <= temp_max and alert_count == 0:
        return {
            'status': 'optimal',
            'bg_color': 'linear-gradient(135deg, #1b5e20 0%, #2e7d32 50%, #388e3c 100%)',  # Dark green
            'border_color': '#4caf50',
            'text_color': '#ffffff',  # WHITE TEXT
            'emoji': '🟢'
        }
    elif temp_min - 2 <= temperature <= temp_max + 2 and alert_count <= 2:
        return {
            'status': 'warning',
            'bg_color': 'linear-gradient(135deg, #e65100 0%, #f57c00 50%, #ff9800 100%)',  # Dark orange
            'border_color': '#ffc107',
            'text_color': '#ffffff',  # WHITE TEXT
            'emoji': '🟡'
        }
    else:
        return {
            'status': 'critical',
            'bg_color': 'linear-gradient(135deg, #b71c1c 0%, #c62828 50%, #d32f2f 100%)',  # Dark red
            'border_color': '#f44336',
            'text_color': '#ffffff',  # WHITE TEXT
            'emoji': '🔴'
        }

def get_score_color_and_status(score):
    """Return DARK color scheme and status based on performance score"""
    if score >= 90:
        return {
            'status': 'Excellent',
            'emoji': '🏆',
            'color': '#ffffff',  # WHITE TEXT
            'bg_color': 'linear-gradient(135deg, #1b5e20 0%, #2e7d32 100%)',  # Dark green
            'border_color': '#4caf50'
        }
    elif score >= 75:
        return {
            'status': 'Good',
            'emoji': '✅',
            'color': '#ffffff',  # WHITE TEXT
            'bg_color': 'linear-gradient(135deg, #1565c0 0%, #1976d2 100%)',  # Dark blue
            'border_color': '#2196f3'
        }
    elif score >= 60:
        return {
            'status': 'Fair',
            'emoji': '⚠️',
            'color': '#ffffff',  # WHITE TEXT
            'bg_color': 'linear-gradient(135deg, #e65100 0%, #f57c00 100%)',  # Dark orange
            'border_color': '#ff9800'
        }
    elif score >= 40:
        return {
            'status': 'Poor',
            'emoji': '⚠️',
            'color': '#ffffff',  # WHITE TEXT
            'bg_color': 'linear-gradient(135deg, #d84315 0%, #ff5722 100%)',  # Dark red-orange
            'border_color': '#ff7043'
        }
    else:
        return {
            'status': 'Critical',
            'emoji': '🔴',
            'color': '#ffffff',  # WHITE TEXT
            'bg_color': 'linear-gradient(135deg, #b71c1c 0%, #c62828 100%)',  # Dark red
            'border_color': '#f44336'
        }



# === THRESHOLD CONFIGURATION SYSTEM ===
def setup_threshold_configuration(zone_id):
    """Complete threshold configuration system"""
    default_ranges = {
        'Z1-Freezer': {'temp_min': -22, 'temp_max': -18, 'humidity_min': 50, 'humidity_max': 70},
        'Z2-Chiller': {'temp_min': 2, 'temp_max': 5, 'humidity_min': 70, 'humidity_max': 80},
        'Z3-Produce': {'temp_min': 5, 'temp_max': 10, 'humidity_min': 80, 'humidity_max': 95},
        'Z4-Pharma': {'temp_min': 2, 'temp_max': 8, 'humidity_min': 50, 'humidity_max': 60}
    }

    defaults = default_ranges.get(zone_id, {'temp_min': 2, 'temp_max': 5, 'humidity_min': 70, 'humidity_max': 80})

    return {
        'temp_min': defaults['temp_min'],
        'temp_max': defaults['temp_max'],
        'warning_buffer': 1.5,
        'humidity_min': defaults['humidity_min'],
        'humidity_max': defaults['humidity_max'],
        'alert_sensitivity': "Medium",
        'data_quality_threshold': 95
    }

def apply_custom_alert_logic(df, config):
    """Apply custom alert logic based on configuration"""
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
def load_all_zones_data():
    """Load data for all zones with comprehensive error handling"""
    try:
        df = pd.read_csv('simulated_warehouse_data_30min_demo.csv', na_values=['NaN', '', 'nan', 'NULL', 'null'])
        df = df.dropna()  # Remove any rows with missing values
        df['timestamp'] = pd.to_datetime(df['timestamp'])

        if 'temperature' not in df.columns and 'value' in df.columns:
            df['temperature'] = df['value']

        return df
    except FileNotFoundError:
        st.error("📁 Data file not found. Please ensure 'simulated_warehouse_data_30min_demo.csv' exists.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Error loading data: {e}")
        return pd.DataFrame()

def setup_date_range_filtering():
    """Complete date range filtering system"""
    with st.sidebar:
        st.markdown("---")
        st.header("📅 Historical Analysis")
        st.markdown("**Analyze data trends across custom time periods**")

        df = load_all_zones_data()

        if not df.empty:
            min_date = df['timestamp'].min().date()
            max_date = df['timestamp'].max().date()
            total_days = (max_date - min_date).days + 1

            if total_days >= 7:
                default_start = (datetime.combine(max_date, datetime.min.time()) - timedelta(days=7)).date()
            elif total_days >= 3:
                default_start = (datetime.combine(max_date, datetime.min.time()) - timedelta(days=total_days-1)).date()
            else:
                default_start = min_date

            default_start = max(default_start, min_date)

            st.subheader("🚀 Quick Ranges")
            col1, col2 = st.columns(2)

            with col1:
                if st.button("📊 Last 24 Hours", use_container_width=True):
                    end_date = max_date
                    start_date = max((datetime.combine(max_date, datetime.min.time()) - timedelta(days=1)).date(), min_date)
                    st.session_state['date_start'] = start_date
                    st.session_state['date_end'] = end_date
                    st.rerun()

                if st.button("📈 Last Week", use_container_width=True):
                    end_date = max_date
                    start_date = max((datetime.combine(max_date, datetime.min.time()) - timedelta(weeks=1)).date(), min_date)
                    st.session_state['date_start'] = start_date
                    st.session_state['date_end'] = end_date
                    st.rerun()

            with col2:
                if st.button("📊 Last 3 Days", use_container_width=True):
                    end_date = max_date
                    start_date = max((datetime.combine(max_date, datetime.min.time()) - timedelta(days=3)).date(), min_date)
                    st.session_state['date_start'] = start_date
                    st.session_state['date_end'] = end_date
                    st.rerun()

                if st.button("📈 All Available", use_container_width=True):
                    st.session_state['date_start'] = min_date
                    st.session_state['date_end'] = max_date
                    st.rerun()

            st.subheader("🎯 Custom Range")

            if 'date_start' not in st.session_state:
                st.session_state['date_start'] = default_start
            if 'date_end' not in st.session_state:
                st.session_state['date_end'] = max_date

            st.session_state['date_start'] = max(st.session_state.get('date_start', default_start), min_date)
            st.session_state['date_start'] = min(st.session_state['date_start'], max_date)
            st.session_state['date_end'] = max(st.session_state.get('date_end', max_date), min_date)
            st.session_state['date_end'] = min(st.session_state['date_end'], max_date)

            start_date = st.date_input(
                "📅 Start Date",
                value=st.session_state['date_start'],
                min_value=min_date,
                max_value=max_date,
                key="date_range_start"
            )

            end_date = st.date_input(
                "📅 End Date",
                value=st.session_state['date_end'],
                min_value=min_date,
                max_value=max_date,
                key="date_range_end"
            )

            st.session_state['date_start'] = start_date
            st.session_state['date_end'] = end_date

            if start_date > end_date:
                st.error("⚠️ Start date must be before end date!")
                return None, None, None

            date_range = (end_date - start_date).days + 1

            st.markdown("---")
            st.markdown("**📊 Range Summary:**")

            if total_days == 1:
                st.info(f"💡 **Single Day Dataset** - All data from {max_date.strftime('%B %d, %Y')}")
            else:
                st.markdown(f"""
                • **Period:** {date_range} days
                • **From:** {start_date.strftime('%B %d, %Y')}
                • **To:** {end_date.strftime('%B %d, %Y')}
                • **Available:** {total_days} days total
                """)

            st.subheader("🔍 Analysis Options")

            compare_periods = st.checkbox(
                "📈 Compare with Previous Period",
                value=False,
                disabled=(total_days < 2),
                key="compare_periods",
                help="Compare current range with equivalent previous period" if total_days >= 2 else "Need at least 2 days of data for comparison"
            )

            show_daily_averages = st.checkbox(
                "📊 Show Daily Averages",
                value=(date_range > 2),
                key="show_daily_averages",
                help="Display daily average temperatures instead of raw readings"
            )

            export_filtered = st.checkbox(
                "📥 Enable Filtered Export",
                value=True,
                key="export_filtered",
                help="Export only data within selected date range"
            )

            if st.button("✅ Apply Date Filter", use_container_width=True, type="primary"):
                st.success(f"✅ Filtering data from {start_date} to {end_date}")
                st.rerun()

            if st.button("🔄 Reset to All Data", use_container_width=True):
                st.session_state['date_start'] = min_date
                st.session_state['date_end'] = max_date
                st.success("🔄 Showing all available data")
                st.rerun()

            return start_date, end_date, {
                'compare_periods': compare_periods,
                'show_daily_averages': show_daily_averages,
                'export_filtered': export_filtered,
                'total_days_available': total_days
            }
        else:
            st.warning("No data available for date filtering")
            return None, None, None

def filter_data_by_date_range(df, start_date, end_date):
    """Filter dataframe by date range"""
    if df.empty or start_date is None or end_date is None:
        return df

    start_datetime = pd.to_datetime(start_date)
    end_datetime = pd.to_datetime(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)

    filtered_df = df[
        (df['timestamp'] >= start_datetime) &
        (df['timestamp'] <= end_datetime)
    ].copy()

    return filtered_df

def calculate_zone_performance_score(df, zone_id):
    """Complete zone performance scoring algorithm"""
    zone_data = df[df['zone_id'] == zone_id]
    if zone_data.empty:
        return None

    zone_ranges = {
        'Z1-Freezer': {'temp_min': -22, 'temp_max': -18, 'humidity_min': 50, 'humidity_max': 70},
        'Z2-Chiller': {'temp_min': 2, 'temp_max': 5, 'humidity_min': 70, 'humidity_max': 80},
        'Z3-Produce': {'temp_min': 5, 'temp_max': 10, 'humidity_min': 80, 'humidity_max': 95},
        'Z4-Pharma': {'temp_min': 2, 'temp_max': 8, 'humidity_min': 50, 'humidity_max': 60}
    }

    optimal_range = zone_ranges.get(zone_id, {'temp_min': 0, 'temp_max': 5, 'humidity_min': 50, 'humidity_max': 80})
    recent_data = zone_data.tail(50)
    temp_readings = recent_data['temperature']
    temp_std = temp_readings.std()

    # Temperature compliance scoring
    in_range_temps = len(temp_readings[
        (temp_readings >= optimal_range['temp_min']) &
        (temp_readings <= optimal_range['temp_max'])
    ])
    temp_compliance = (in_range_temps / len(temp_readings)) * 100

    # Stability scoring based on standard deviation
    if temp_std <= 0.5:
        stability_score = 40
    elif temp_std <= 1.0:
        stability_score = 35
    elif temp_std <= 2.0:
        stability_score = 25
    else:
        stability_score = 15

    temp_score = stability_score * (temp_compliance / 100)

    # Alert frequency scoring
    alert_count = len(recent_data[recent_data['alert_status'] == 'alert'])
    alert_rate = (alert_count / len(recent_data)) * 100

    if alert_rate == 0:
        alert_score = 30
    elif alert_rate <= 5:
        alert_score = 25
    elif alert_rate <= 15:
        alert_score = 15
    elif alert_rate <= 30:
        alert_score = 8
    else:
        alert_score = 2

    # Data quality scoring
    missing_data_penalty = 0
    if 'humidity' in recent_data.columns:
        missing_humidity = recent_data['humidity'].isna().sum()
        missing_data_penalty = min((missing_humidity / len(recent_data)) * 20, 10)

    # Data freshness scoring
    latest_reading = recent_data.iloc[-1]['timestamp']
    time_diff = (datetime.now() - latest_reading).total_seconds() / 60

    if time_diff <= 5:
        freshness_score = 10
    elif time_diff <= 30:
        freshness_score = 7
    elif time_diff <= 60:
        freshness_score = 4
    else:
        freshness_score = 1

    data_quality_score = 20 - missing_data_penalty + freshness_score
    data_quality_score = max(0, min(20, data_quality_score))

    # Efficiency scoring based on temperature variance
    temp_variance = temp_readings.var()
    if temp_variance <= 1.0:
        efficiency_score = 10
    elif temp_variance <= 4.0:
        efficiency_score = 7
    elif temp_variance <= 9.0:
        efficiency_score = 4
    else:
        efficiency_score = 1

    # Calculate total score
    total_score = temp_score + alert_score + data_quality_score + efficiency_score
    total_score = max(0, min(100, total_score))

    return {
        'total_score': round(total_score, 1),
        'temperature_score': round(temp_score, 1),
        'alert_score': round(alert_score, 1),
        'data_quality_score': round(data_quality_score, 1),
        'efficiency_score': round(efficiency_score, 1),
        'temp_compliance': round(temp_compliance, 1),
        'alert_rate': round(alert_rate, 1),
        'temp_stability': round(temp_std, 2),
        'data_freshness_minutes': round(time_diff, 1)
    }

def get_zone_summary(df, zone_id):
    """Get comprehensive summary stats for a zone"""
    zone_data = df[df['zone_id'] == zone_id]
    if zone_data.empty:
        return None

    latest = zone_data.iloc[-1]
    avg_temp = zone_data['temperature'].mean()
    temp_std = zone_data['temperature'].std()
    alert_count = len(zone_data[zone_data['alert_status'] == 'alert'])
    total_points = len(zone_data)

    # Calculate temperature trend
    if len(zone_data) >= 10:
        recent_avg = zone_data.tail(5)['temperature'].mean()
        previous_avg = zone_data.tail(10).head(5)['temperature'].mean()
        temp_trend = recent_avg - previous_avg
    else:
        temp_trend = 0

    # Get performance score
    performance_data = calculate_zone_performance_score(df, zone_id)
    performance_score = performance_data['total_score'] if performance_data else 0

    recent_alerts = zone_data[zone_data['alert_status'] == 'alert'].tail(10)

    return {
        'latest_temp': latest['temperature'],
        'latest_humidity': latest.get('humidity', np.nan),
        'avg_temp': avg_temp,
        'temp_std': temp_std,
        'temp_trend': temp_trend,
        'alert_count': alert_count,
        'data_points': total_points,
        'alert_rate': (alert_count / total_points * 100) if total_points > 0 else 0,
        'timestamp': latest['timestamp'],
        'recent_alerts': recent_alerts,
        'performance_score': performance_score,
        'zone_status': 'excellent' if performance_score >= 90 else
                      'good' if performance_score >= 75 else
                      'fair' if performance_score >= 60 else
                      'poor' if performance_score >= 40 else 'critical'
    }

def create_performance_dashboard(df, zones):
    """Create comprehensive performance dashboard with DARK backgrounds"""
    st.header("🏆 Zone Performance Dashboard")
    st.markdown("**Comprehensive health scores based on temperature stability, alert rates, and data quality**")

    zone_scores = {}
    for zone in zones:
        score_data = calculate_zone_performance_score(df, zone)
        if score_data:
            zone_scores[zone] = score_data

    if not zone_scores:
        st.warning("No performance data available")
        return

    # Overall system performance with DARK background
    avg_score = np.mean([scores['total_score'] for scores in zone_scores.values()])
    score_info = get_score_color_and_status(avg_score)

    # Performance summary with WHITE text on DARK background
    well_performing = len([s for s in zone_scores.values() if s['total_score'] >= 75])

    st.markdown(f"""
    <div style="
        background: {score_info['bg_color']};
        border: 2px solid {score_info['border_color']};
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        text-align: center;
        color: {score_info['color']};
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
    ">
        <h3>{score_info['emoji']} System Performance: {avg_score:.1f}/100</h3>
        <p>Average Score: {avg_score:.1f}/100 • {well_performing}/{len(zones)} zones performing well</p>
        <p><strong>{score_info['status']} Performance</strong></p>
    </div>
    """, unsafe_allow_html=True)

    # Individual zone performance cards with DARK backgrounds
    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)
    cols = [col1, col2, col3, col4]

    zone_names = {
        'Z1-Freezer': '🧊 Freezer',
        'Z2-Chiller': '❄️ Chiller',
        'Z3-Produce': '🥬 Produce',
        'Z4-Pharma': '💊 Pharma'
    }

    for i, zone in enumerate(zones):
        if zone in zone_scores:
            score = zone_scores[zone]
            info = get_score_color_and_status(score['total_score'])

            with cols[i]:
                st.markdown(f"""
                <div style="
                    background: {info['bg_color']};
                    border: 2px solid {info['border_color']};
                    border-radius: 10px;
                    padding: 15px;
                    margin: 5px 0;
                    color: {info['color']};
                    box-shadow: 0 4px 8px rgba(0,0,0,0.3);
                ">
                    <h4>{info['emoji']} {zone_names.get(zone, zone)}</h4>
                    <p><strong>Performance:</strong> {score['total_score']}/100 ({info['status']})</p>
                    <p><strong>Temperature Score:</strong> {score['temperature_score']}/40</p>
                    <p><strong>Alert Score:</strong> {score['alert_score']}/30</p>
                    <p><strong>Data Quality:</strong> {score['data_quality_score']}/20</p>
                    <p><strong>Efficiency:</strong> {score['efficiency_score']}/10</p>
                </div>
                """, unsafe_allow_html=True)

def create_system_overview_charts(df):
    """Create comprehensive system overview charts"""
    if df.empty:
        return

    st.header("📊 System Analytics Dashboard")

    # Temperature trends for all zones
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🌡️ Temperature Trends (All Zones)")

        chart_data = df.tail(200)  # Last 200 readings

        temp_chart = alt.Chart(chart_data).mark_line(point=True).encode(
            x=alt.X('timestamp:T', title='Time'),
            y=alt.Y('temperature:Q', title='Temperature (°C)'),
            color=alt.Color('zone_id:N', title='Zone'),
            tooltip=['zone_id:N', 'timestamp:T', 'temperature:Q', 'alert_status:N']
        ).properties(
            width=400,
            height=300,
            title='Multi-Zone Temperature Monitoring'
        )

        st.altair_chart(temp_chart, use_container_width=True)

    with col2:
        st.subheader("🚨 Alert Distribution")

        # Alert distribution by zone
        alert_data = df[df['alert_status'] == 'alert']

        if not alert_data.empty:
            alert_counts = alert_data['zone_id'].value_counts().reset_index()
            alert_counts.columns = ['zone_id', 'alert_count']

            alert_chart = alt.Chart(alert_counts).mark_bar(color='red').encode(
                x=alt.X('zone_id:N', title='Zone'),
                y=alt.Y('alert_count:Q', title='Alert Count'),
                tooltip=['zone_id:N', 'alert_count:Q']
            ).properties(
                width=400,
                height=300,
                title='Alert Distribution by Zone'
            )

            st.altair_chart(alert_chart, use_container_width=True)
        else:
            st.success("✅ No alerts across all zones!")

def create_historical_analysis(df, start_date, end_date, options):
    """Create historical analysis dashboard"""
    st.header("📈 Historical Analysis Dashboard")

    if not df.empty and start_date and end_date:
        st.markdown(f"**Analysis Period:** {start_date} to {end_date} ({len(df):,} data points)")

        # Daily averages if requested
        if options and options.get('show_daily_averages', False):
            st.subheader("📊 Daily Temperature Averages")

            # Group by date and zone
            df['date'] = df['timestamp'].dt.date
            daily_avg = df.groupby(['date', 'zone_id'])['temperature'].mean().reset_index()
            daily_avg['date'] = pd.to_datetime(daily_avg['date'])

            daily_chart = alt.Chart(daily_avg).mark_line(point=True).encode(
                x=alt.X('date:T', title='Date'),
                y=alt.Y('temperature:Q', title='Average Temperature (°C)'),
                color=alt.Color('zone_id:N', title='Zone'),
                tooltip=['date:T', 'zone_id:N', 'temperature:Q']
            ).properties(
                height=400,
                title='Daily Average Temperatures by Zone'
            )

            st.altair_chart(daily_chart, use_container_width=True)

        # Period comparison if requested
        if options and options.get('compare_periods', False):
            st.subheader("🔄 Period Comparison")

            # Calculate period length
            period_days = (end_date - start_date).days + 1

            # Get previous period
            prev_start = start_date - timedelta(days=period_days)
            prev_end = start_date - timedelta(days=1)

            # Filter data for both periods
            current_period = df
            prev_period = filter_data_by_date_range(
                load_all_zones_data(),
                prev_start,
                prev_end
            )

            if not prev_period.empty:
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("**Current Period**")
                    current_stats = current_period.groupby('zone_id')['temperature'].agg(['mean', 'std', 'count']).round(2)
                    current_alerts = len(current_period[current_period['alert_status'] == 'alert'])
                    st.dataframe(current_stats)
                    st.metric("Total Alerts", current_alerts)

                with col2:
                    st.markdown("**Previous Period**")
                    prev_stats = prev_period.groupby('zone_id')['temperature'].agg(['mean', 'std', 'count']).round(2)
                    prev_alerts = len(prev_period[prev_period['alert_status'] == 'alert'])
                    st.dataframe(prev_stats)
                    st.metric("Total Alerts", prev_alerts, delta=current_alerts - prev_alerts)
            else:
                st.info("No data available for previous period comparison")

        # Statistical summary
        st.subheader("📊 Statistical Summary")

        summary_stats = df.groupby('zone_id').agg({
            'temperature': ['mean', 'std', 'min', 'max', 'count'],
            'humidity': ['mean', 'std'] if 'humidity' in df.columns else lambda x: None
        }).round(2)

        # Flatten column names
        summary_stats.columns = ['_'.join(col).strip() for col in summary_stats.columns]

        st.dataframe(summary_stats, use_container_width=True)

        # Alert frequency analysis
        alert_summary = df.groupby('zone_id')['alert_status'].value_counts().unstack(fill_value=0)
        if 'alert' in alert_summary.columns:
            alert_summary['alert_rate'] = (alert_summary['alert'] / (alert_summary['alert'] + alert_summary['normal']) * 100).round(1)

        st.subheader("🚨 Alert Frequency Analysis")
        st.dataframe(alert_summary, use_container_width=True)

def create_predictive_analytics(df, zones):
    """Create predictive analytics dashboard"""
    st.header("🔮 Predictive Analytics")
    st.markdown("**Temperature trend predictions and risk assessment based on historical data**")

    predictions = {}

    for zone in zones:
        zone_data = df[df['zone_id'] == zone].tail(100)  # Last 100 readings

        if len(zone_data) >= 10:
            # Simple linear trend analysis
            zone_data = zone_data.copy()
            zone_data['time_numeric'] = range(len(zone_data))

            # Calculate trend using numpy polyfit
            temp_trend = np.polyfit(zone_data['time_numeric'], zone_data['temperature'], 1)[0]

            # Predict next few readings
            next_temps = []
            current_temp = zone_data['temperature'].iloc[-1]
            for i in range(1, 13):  # Next 12 readings
                predicted_temp = current_temp + (temp_trend * i)
                next_temps.append(predicted_temp)

            # Risk assessment
            zone_ranges = {
                'Z1-Freezer': {'temp_min': -22, 'temp_max': -18},
                'Z2-Chiller': {'temp_min': 2, 'temp_max': 5},
                'Z3-Produce': {'temp_min': 5, 'temp_max': 10},
                'Z4-Pharma': {'temp_min': 2, 'temp_max': 8}
            }

            optimal_range = zone_ranges.get(zone, {'temp_min': 0, 'temp_max': 5})

            # Calculate risk score
            risk_score = 0
            for temp in next_temps[:6]:  # Next 6 readings (3 hours)
                if temp < optimal_range['temp_min'] or temp > optimal_range['temp_max']:
                    risk_score += 1

            risk_percentage = (risk_score / 6) * 100

            predictions[zone] = {
                'current_temp': current_temp,
                'trend': temp_trend,
                'next_temps': next_temps,
                'risk_score': risk_percentage,
                'risk_level': 'High' if risk_percentage > 50 else 'Medium' if risk_percentage > 20 else 'Low'
            }

    # Display predictions
    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)
    prediction_cols = [col1, col2, col3, col4]

    zone_names = {
        'Z1-Freezer': '🧊 Freezer',
        'Z2-Chiller': '❄️ Chiller',
        'Z3-Produce': '🥬 Produce',
        'Z4-Pharma': '💊 Pharma'
    }

    for i, (zone, pred) in enumerate(predictions.items()):
        with prediction_cols[i]:
            # Risk color
            risk_color = "#b71c1c" if pred['risk_level'] == 'High' else "#e65100" if pred['risk_level'] == 'Medium' else "#1b5e20"

            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, {risk_color} 0%, {risk_color}dd 100%);
                border: 2px solid #ffffff;
                border-radius: 10px;
                padding: 15px;
                margin: 5px 0;
                color: #ffffff;
                box-shadow: 0 4px 8px rgba(0,0,0,0.3);
            ">
                <h4>{zone_names.get(zone, zone)}</h4>
                <p><strong>Current:</strong> {pred['current_temp']:.1f}°C</p>
                <p><strong>Trend:</strong> {pred['trend']:+.3f}°C/reading</p>
                <p><strong>Risk Level:</strong> {pred['risk_level']}</p>
                <p><strong>Risk Score:</strong> {pred['risk_score']:.0f}%</p>
            </div>
            """, unsafe_allow_html=True)

    # Create prediction chart
    if predictions:
        st.subheader("📈 Temperature Trend Predictions")

        # Prepare data for chart
        chart_data = []

        for zone, pred in predictions.items():
            # Historical data (last 20 points)
            zone_historical = df[df['zone_id'] == zone].tail(20)

            for _, row in zone_historical.iterrows():
                chart_data.append({
                    'zone': zone,
                    'time_index': len(chart_data),
                    'temperature': row['temperature'],
                    'type': 'Historical',
                    'timestamp': row['timestamp']
                })

            # Predicted data
            base_index = len([d for d in chart_data if d['zone'] == zone])
            for i, temp in enumerate(pred['next_temps'][:6]):
                chart_data.append({
                    'zone': zone,
                    'time_index': base_index + i,
                    'temperature': temp,
                    'type': 'Predicted',
                    'timestamp': None
                })

        if chart_data:
            chart_df = pd.DataFrame(chart_data)

            prediction_chart = alt.Chart(chart_df).mark_line(point=True).encode(
                x=alt.X('time_index:Q', title='Time Index'),
                y=alt.Y('temperature:Q', title='Temperature (°C)'),
                color=alt.Color('zone:N', title='Zone'),
                strokeDash=alt.StrokeDash('type:N', title='Data Type'),
                tooltip=['zone:N', 'temperature:Q', 'type:N']
            ).properties(
                height=400,
                title='Temperature Trends and Predictions'
            )

            st.altair_chart(prediction_chart, use_container_width=True)

    # Maintenance recommendations
    st.subheader("🔧 Predictive Maintenance Recommendations")

    maintenance_recs = []

    for zone, pred in predictions.items():
        if pred['risk_level'] == 'High':
            maintenance_recs.append(f"🚨 **{zone}**: High risk detected - Schedule immediate inspection")
        elif pred['risk_level'] == 'Medium':
            maintenance_recs.append(f"⚠️ **{zone}**: Medium risk - Monitor closely and schedule preventive maintenance")

        if abs(pred['trend']) > 0.05:
            maintenance_recs.append(f"📈 **{zone}**: Significant temperature trend ({pred['trend']:+.3f}°C/reading) - Check system calibration")

    if maintenance_recs:
        for i, rec in enumerate(maintenance_recs, 1):
            st.markdown(f"{i}. {rec}")
    else:
        st.success("✅ All zones show stable trends - no immediate maintenance required!")

# === MAIN APPLICATION ===
st.title("📊 Warehouse System Overview")
st.markdown("**Advanced Cold Storage Monitoring & Analytics with Dark Theme**")

# Setup date range filtering
date_filter_result = setup_date_range_filtering()
start_date, end_date, filter_options = date_filter_result if date_filter_result else (None, None, None)

# Load data
full_df = load_all_zones_data()

if full_df.empty:
    st.warning("⚠️ No data available. Please check your data file.")
    st.stop()

# --- DYNAMICALLY APPLY ALERT LOGIC TO THE ENTIRE DATAFRAME ---
# This is the key change to make the entire page dynamic.
zones = ['Z1-Freezer', 'Z2-Chiller', 'Z3-Produce', 'Z4-Pharma']

# Apply alert logic for each zone and combine the results
processed_dfs = []
for zone_id in zones:
    zone_data = full_df[full_df['zone_id'] == zone_id].copy()
    if not zone_data.empty:
        # Get default configuration for the zone
        config = setup_threshold_configuration(zone_id)
        # Apply the alert logic to this zone's data
        processed_df = apply_custom_alert_logic(zone_data, config)
        processed_dfs.append(processed_df)

if processed_dfs:
    df = pd.concat(processed_dfs).sort_values('timestamp').reset_index(drop=True)
else:
    df = pd.DataFrame()

if df.empty:
    st.warning("⚠️ No processable data available after applying alert logic.")
    st.stop()

# Apply date filtering if specified
if start_date and end_date:
    df = filter_data_by_date_range(df, start_date, end_date)
    if df.empty:
        st.warning(f"⚠️ No data available for selected date range: {start_date} to {end_date}")
        st.stop()

# === SYSTEM STATUS OVERVIEW ===
st.header("🏢 System Status Overview")

zone_names = {
    'Z1-Freezer': '🧊 Freezer',
    'Z2-Chiller': '❄️ Chiller',
    'Z3-Produce': '🥬 Produce',
    'Z4-Pharma': '💊 Pharma'
}

# Calculate overall metrics
total_alerts = len(df[df['alert_status'] == 'alert'])
active_zones = len([zone for zone in zones if not df[df['zone_id'] == zone].empty])
last_update = df['timestamp'].max()

# Display overall metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("🟢 Active Zones", f"{active_zones}/4")

with col2:
    if total_alerts == 0:
        st.metric("🚨 Total Alerts", "0", delta="✅ All Normal")
    else:
        st.metric("🚨 Total Alerts", str(total_alerts), delta="⚠️ Action Needed")

with col3:
    if pd.notna(last_update):
        time_diff = (datetime.now() - last_update).total_seconds() / 60
        if time_diff <= 5:
            st.metric("🕐 Data Status", "Live", delta="✅ Current")
        else:
            st.metric("🕐 Data Status", f"{time_diff:.0f}min ago", delta="⚠️ Delayed")
    else:
        st.metric("🕐 Data Status", "Unknown", delta="❌ No Data")

with col4:
    if not df.empty:
        avg_temp_all = df.groupby('zone_id')['temperature'].mean().mean()
        st.metric("🌡️ Avg Temp", f"{avg_temp_all:.1f}°C")

# === ZONE STATUS CARDS WITH DARK BACKGROUNDS ===
st.header("📋 Zone Status Cards")

col1, col2 = st.columns(2)
col3, col4 = st.columns(2)
zone_cols = [col1, col2, col3, col4]

for i, zone_id in enumerate(zones):
    with zone_cols[i]:
        summary = get_zone_summary(df, zone_id)

        if summary:
            status_info = get_zone_status_color(summary['latest_temp'], summary['alert_count'], zone_id)

            # Trend arrow
            if abs(summary['temp_trend']) < 0.1:
                trend_arrow = "→"
            elif summary['temp_trend'] > 0:
                trend_arrow = "↗️"
            else:
                trend_arrow = "↘️"

            st.markdown(f"""
            <div style="
                background: {status_info['bg_color']};
                border: 2px solid {status_info['border_color']};
                border-radius: 10px;
                padding: 15px;
                margin: 5px 0;
                color: {status_info['text_color']};
                box-shadow: 0 4px 8px rgba(0,0,0,0.3);
            ">
                <h4>{status_info['emoji']} {zone_names[zone_id]}</h4>
                <p><strong>Temperature:</strong> {summary['latest_temp']:.1f}°C {trend_arrow}</p>
                <p><strong>Humidity:</strong> {summary['latest_humidity']:.1f}%</p>
                <p><strong>Alerts:</strong> {summary['alert_count']} active</p>
                <p><strong>Performance:</strong> {summary['performance_score']:.1f}/100</p>
                <p><strong>Status:</strong> {status_info['status'].title()}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.error(f"❌ No data for {zone_names[zone_id]}")

# === PERFORMANCE DASHBOARD ===
create_performance_dashboard(df, zones)

# === SYSTEM ANALYTICS ===
create_system_overview_charts(df)

# === HISTORICAL ANALYSIS ===
if start_date and end_date:
    create_historical_analysis(df, start_date, end_date, filter_options)

# === PREDICTIVE ANALYTICS ===
create_predictive_analytics(df, zones)

# === RECENT ALERTS TABLE ===
st.header("🚨 Recent Alerts & Notifications")

recent_alerts = df[df['alert_status'] == 'alert'].tail(20)

if not recent_alerts.empty:
    alert_display = recent_alerts[['timestamp', 'zone_id', 'temperature', 'humidity', 'alert_status']].copy()
    alert_display['timestamp'] = alert_display['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')

    st.dataframe(
        alert_display,
        use_container_width=True,
        hide_index=True,
        column_config={
            "timestamp": "Timestamp",
            "zone_id": "Zone",
            "temperature": st.column_config.NumberColumn("Temperature (°C)", format="%.2f"),
            "humidity": st.column_config.NumberColumn("Humidity (%)", format="%.1f"),
            "alert_status": "Status"
        }
    )
else:
    st.success("✅ No recent alerts - all zones operating normally!")

# === SYSTEM CONTROLS ===
st.header("⚙️ System Controls")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🔄 Refresh Data", type="secondary"):
        st.cache_data.clear()
        st.rerun()

with col2:
    if st.button("📊 Reset Filters", type="secondary"):
        for key in list(st.session_state.keys()):
            if key.startswith('date_'):
                del st.session_state[key]
        st.rerun()

with col3:
    auto_refresh = st.toggle("🔄 Auto Refresh", value=False)
    if auto_refresh:
        st.info("🔄 Auto refresh enabled - page will update every 30 seconds")
        time.sleep(30)
        st.rerun()

# Export functionality
if filter_options and filter_options.get('export_filtered', False):
    st.subheader("📥 Data Export")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📊 Export Current View"):
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"warehouse_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

    with col2:
        if st.button("🚨 Export Alerts Only"):
            alerts_only = df[df['alert_status'] == 'alert']
            if not alerts_only.empty:
                csv = alerts_only.to_csv(index=False)
                st.download_button(
                    label="📥 Download Alerts CSV",
                    data=csv,
                    file_name=f"warehouse_alerts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            else:
                st.info("No alerts to export")

    with col3:
        if st.button("📈 Export Performance Report"):
            # Create performance summary
            performance_data = []
            for zone in zones:
                score_data = calculate_zone_performance_score(df, zone)
                if score_data:
                    performance_data.append({
                        'zone': zone,
                        **score_data
                    })

            if performance_data:
                performance_df = pd.DataFrame(performance_data)
                csv = performance_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Performance CSV",
                    data=csv,
                    file_name=f"warehouse_performance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )

# === FOOTER ===
st.markdown("---")

# Display current filter status
if start_date and end_date:
    st.markdown(f"**📅 Filtered Data:** {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')} ({len(df):,} records)")
else:
    st.markdown(f"**📅 All Data:** {len(df):,} records")

st.markdown(
    f"**🏢 Warehouse Cold Storage Monitoring System** | "
    f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
    f"**Data Points:** {len(df):,} | "
    f"**Zones Active:** {active_zones}/4 | "
    f"**Total Alerts:** {total_alerts}"
)

st.markdown("**🎨 Dark Theme Active** | **✨ Complete Features:** Real-time monitoring • Performance scoring • Alert management • Historical filtering • Predictive analytics • Dark backgrounds for optimal readability")