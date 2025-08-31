import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
from datetime import datetime, timedelta

@st.cache_data
def load_all_zones_data():
    """Load data for all zones"""
    try:
        df = pd.read_csv('simulated_warehouse_data_30min_demo.csv')
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        if 'temperature' not in df.columns and 'value' in df.columns:
            df['temperature'] = df['value']
        return df
    except FileNotFoundError:
        st.error("Data file not found. Please ensure 'simulated_warehouse_data_30min_demo.csv' exists.")
        return pd.DataFrame()

def setup_date_range_filtering():
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
    if df.empty or start_date is None or end_date is None:
        return df
    start_datetime = pd.to_datetime(start_date)
    end_datetime = pd.to_datetime(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
    filtered_df = df[
        (df['timestamp'] >= start_datetime) & 
        (df['timestamp'] <= end_datetime)
    ].copy()
    return filtered_df

# ...Keep rest of your functions (performance, historical, etc.) unchanged, then add cost functions...

def calculate_zone_performance_score(df, zone_id):
    # --- As in the previous provided code, unchanged ---
    zone_data = df[df['zone_id'] == zone_id]
    if zone_data.empty:
        return None
    zone_ranges = {
        'Z1-Freezer': {'temp_min': -22, 'temp_max': -18, 'humidity_min': 50, 'humidity_max': 70},
        'Z2-Chiller': {'temp_min': 2, 'temp_max': 4, 'humidity_min': 70, 'humidity_max': 80},
        'Z3-Produce': {'temp_min': 8, 'temp_max': 12, 'humidity_min': 80, 'humidity_max': 95},
        'Z4-Pharma': {'temp_min': -5, 'temp_max': -2, 'humidity_min': 50, 'humidity_max': 60}
    }
    optimal_range = zone_ranges.get(zone_id, {'temp_min': 0, 'temp_max': 5, 'humidity_min': 50, 'humidity_max': 80})
    recent_data = zone_data.tail(50)
    temp_readings = recent_data['temperature']
    temp_std = temp_readings.std()
    in_range_temps = len(temp_readings[
        (temp_readings >= optimal_range['temp_min']) & 
        (temp_readings <= optimal_range['temp_max'])
    ])
    temp_compliance = (in_range_temps / len(temp_readings)) * 100
    if temp_std <= 0.5:
        stability_score = 40
    elif temp_std <= 1.0:
        stability_score = 35
    elif temp_std <= 2.0:
        stability_score = 25
    else:
        stability_score = 15
    temp_score = stability_score * (temp_compliance / 100)
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
    missing_data_penalty = 0
    if 'humidity' in recent_data.columns:
        missing_humidity = recent_data['humidity'].isna().sum()
        missing_data_penalty = min((missing_humidity / len(recent_data)) * 20, 10)
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
    temp_variance = temp_readings.var()
    if temp_variance <= 1.0:
        efficiency_score = 10
    elif temp_variance <= 4.0:
        efficiency_score = 7
    elif temp_variance <= 9.0:
        efficiency_score = 4
    else:
        efficiency_score = 1
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


def get_score_color_and_status(score):
    """Return color scheme and status based on performance score"""
    if score >= 90:
        return {
            'status': 'Excellent', 'emoji': '🏆', 'color': '#28a745',
            'bg_color': 'linear-gradient(135deg, #d4edda 0%, #c3cb 100%)',
            'border_color': '#28a745'
        }
    elif score >= 75:
        return {
            'status': 'Good', 'emoji': '✅', 'color': '#28a745',
            'bg_color': 'linear-gradient(135deg, #d1ecf1 0%, #bee3f1 100%)',
            'border_color': '#17a2b8'
        }
    elif score >= 60:
        return {
            'status': 'Fair', 'emoji': '⚠️', 'color': '#ffc107',
            'bg_color': 'linear-gradient(135deg, #fff3cd 0%, #ffe7a3 100%)',
            'border_color': '#ffc107'
        }
    elif score >= 40:
        return {
            'status': 'Poor', 'emoji': '⚠️', 'color': '#fd7e14',
            'bg_color': 'linear-gradient(135deg, #ffe1cb 0%, #ffcda3 100%)',
            'border_color': '#fd7e14'
        }
    else:
        return {
            'status': 'Critical', 'emoji': '🔴', 'color': '#dc3545',
            'bg_color': 'linear-gradient(135deg, #f8d7da 0%, #f5b0a7 100%)',
            'border_color': '#dc3545'
        }

def get_zone_summary(df, zone_id):
    """Get summary stats for a zone with performance score"""
    zone_data = df[df['zone_id'] == zone_id]
    if zone_data.empty:
        return None
    latest = zone_data.iloc[-1]
    avg_temp = zone_data['temperature'].mean()
    temp_std = zone_data['temperature'].std()
    alert_count = len(zone_data[zone_data['alert_status'] == 'alert'])
    total_points = len(zone_data)
    if len(zone_data) >= 10:
        recent_avg = zone_data.tail(5)['temperature'].mean()
        previous_avg = zone_data.tail(10).head(5)['temperature'].mean()
        temp_trend = recent_avg - previous_avg
    else:
        temp_trend = 0
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
        'zone_status': 'excellent' if performance_score >= 90 else 'good' if performance_score >= 75 else 'fair' if performance_score >= 60 else 'poor' if performance_score >= 40 else 'critical'
    }

def create_performance_dashboard(df, zones):
    """Create comprehensive performance dashboard"""
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
    avg_score = np.mean([scores['total_score'] for scores in zone_scores.values()])
    score_info = get_score_color_and_status(avg_score)
    st.markdown(f"""
    <div style="background: {score_info['bg_color']}; padding: 20px; border-radius: 15px; border-left: 6px solid {score_info['border_color']}; box-shadow: 0 4px 8px rgba(0,0,0,0.15); margin-bottom: 30px;">
        <div style="display: flex; align-items: center; justify-content: space-between;">
            <div>
                <h3 style="margin: 0; color: {score_info['color']};">
                    {score_info['emoji']} System Performance: {score_info['status']}
                </h3>
                <p style="margin: 5px 0 0 0; color: {score_info['color']}; opacity: 0.9;">
                    Average Score: {avg_score:.1f}/100 • {len([s for s in zone_scores.values() if s['total_score'] >= 75])}/{len(zones)} zones performing well
                </p>
            </div>
            <div style="text-align: right; font-size: 36px; color: {score_info['color']};">
                {avg_score:.0f}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.subheader("📊 Individual Zone Performance")
    sorted_zones = sorted(zone_scores.items(), key=lambda x: x[1]['total_score'], reverse=True)
    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)
    columns = [col1, col2, col3, col4]
    zone_icons = {'Z1-Freezer': '🧊', 'Z2-Chiller': '❄️', 'Z3-Produce': '🥬', 'Z4-Pharma': '💊'}
    for i, (zone, score_data) in enumerate(sorted_zones[:4]):
        score_info = get_score_color_and_status(score_data['total_score'])
        with columns[i]:
            st.markdown(f"""
            <div style="background: {score_info['bg_color']}; padding: 20px; border-radius: 12px; border-left: 5px solid {score_info['border_color']}; box-shadow: 0 3px 6px rgba(0,0,0,0.1); margin-bottom: 15px;">
                <div style="display: flex; align-items: center; justify-content: between;">
                    <div style="flex-grow: 1;">
                        <h4 style="margin: 0; color: {score_info['color']};">
                            {zone_icons.get(zone, '📊')} {zone}
                        </h4>
                        <div style="font-size: 24px; font-weight: bold; color: {score_info['color']}; margin: 10px 0;">
                            {score_data['total_score']:.1f}/100
                        </div>
                        <p style="margin: 0; color: {score_info['color']}; opacity: 0.8; font-size: 14px;">
                            {score_info['status']} Performance
                        </p>
                    </div>
                    <div style="font-size: 32px; opacity: 0.7;">
                        {score_info['emoji']}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            with st.expander(f"📋 {zone} Score Breakdown"):
                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric("🌡️ Temperature", f"{score_data['temperature_score']:.1f}/40")
                    st.metric("🚨 Alerts", f"{score_data['alert_score']:.1f}/30")
                with col_b:
                    st.metric("📊 Data Quality", f"{score_data['data_quality_score']:.1f}/20") 
                    st.metric("⚡ Efficiency", f"{score_data['efficiency_score']:.1f}/10")
                st.markdown("**📈 Key Insights:**")
                st.write(f"• Temperature Compliance: {score_data['temp_compliance']:.1f}%")
                st.write(f"• Alert Rate: {score_data['alert_rate']:.1f}%")
                st.write(f"• Temperature Stability: ±{score_data['temp_stability']:.2f}°C")
                st.write(f"• Data Freshness: {score_data['data_freshness_minutes']:.1f} minutes ago")
            if st.button(f"📋 View {zone} Details", key=f"perf_btn_{zone}", use_container_width=True):
                st.switch_page(f"pages/{zone}.py")

def create_historical_analysis_dashboard(df, zones, start_date, end_date, options):
    """Create historical analysis dashboard with date filtering"""
    st.header("📊 Historical Analysis Dashboard")
    if start_date and end_date:
        date_range = (end_date - start_date).days + 1
        total_available = options.get('total_days_available', 1) if options else 1
        if total_available == 1:
            st.markdown(f"**📅 Single Day Analysis - {start_date.strftime('%B %d, %Y')}**")
        else:
            st.markdown(f"**📅 Analyzing {date_range} days of data from {start_date.strftime('%B %d, %Y')} to {end_date.strftime('%B %d, %Y')}**")
    if start_date and end_date:
        filtered_df = filter_data_by_date_range(df, start_date, end_date)
    else:
        filtered_df = df.copy()
    if filtered_df.empty:
        st.warning("⚠️ No data available for the selected date range.")
        return
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        total_readings = len(filtered_df)
        st.metric("📊 Total Readings", f"{total_readings:,}")
    with col2:
        total_alerts = len(filtered_df[filtered_df['alert_status'] == 'alert'])
        alert_rate = (total_alerts / total_readings * 100) if total_readings > 0 else 0
        st.metric("🚨 Total Alerts", total_alerts, delta=f"{alert_rate:.1f}% rate")
    with col3:
        avg_temp = filtered_df['temperature'].mean()
        temp_std = filtered_df['temperature'].std()
        st.metric("🌡️ Average Temperature", f"{avg_temp:.1f}°C", delta=f"±{temp_std:.1f}°C std")
    with col4:
        if 'humidity' in filtered_df.columns and filtered_df['humidity'].notna().any():
            avg_humidity = filtered_df['humidity'].mean()
            st.metric("💧 Average Humidity", f"{avg_humidity:.1f}%")
        else:
            st.metric("💧 Average Humidity", "N/A")
    st.subheader("📈 Temperature Trends Over Selected Period")
    total_available = options.get('total_days_available', 1) if options else 1
    if total_available == 1:
        chart_data = filtered_df
        chart_title = f"Hourly Temperature Trends - {start_date.strftime('%B %d, %Y')}"
    elif options and options['show_daily_averages'] and len(filtered_df) > 24:
        filtered_df['date'] = filtered_df['timestamp'].dt.date
        daily_averages = filtered_df.groupby(['date', 'zone_id']).agg({
            'temperature': 'mean',
            'alert_status': lambda x: (x == 'alert').sum()
        }).reset_index()
        daily_averages['timestamp'] = pd.to_datetime(daily_averages['date'])
        chart_data = daily_averages
        chart_title = "Daily Average Temperature Trends"
    else:
        chart_data = filtered_df
        chart_title = "Detailed Temperature Trends"
    trend_chart = alt.Chart(chart_data).mark_line(strokeWidth=2, point=True).encode(
        x=alt.X('timestamp:T', title='Date/Time'),
        y=alt.Y('temperature:Q', title='Temperature (°C)'),
        color=alt.Color(
            'zone_id:N',
            scale=alt.Scale(range=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']),
            title='Storage Zone',
            legend=alt.Legend(orient="top")
        ),
        tooltip=[
            alt.Tooltip('timestamp:T', title='Time'),
            alt.Tooltip('zone_id:N', title='Zone'),
            alt.Tooltip('temperature:Q', title='Temperature (°C)', format='.1f')
        ]
    ).properties(
        height=400,
        title=chart_title
    ).interactive()
    st.altair_chart(trend_chart, use_container_width=True)
    if options and options.get('compare_periods', False) and start_date and end_date and total_available >= 2:
        st.subheader("🔍 Period Comparison Analysis")
        period_length = (end_date - start_date).days + 1
        previous_end = start_date - timedelta(days=1)
        previous_start = previous_end - timedelta(days=period_length-1)
        previous_df = filter_data_by_date_range(df, previous_start, previous_end)
        if not previous_df.empty:
            col1, col2, col3 = st.columns(3)
            with col1:
                current_avg_temp = filtered_df['temperature'].mean()
                previous_avg_temp = previous_df['temperature'].mean()
                temp_change = current_avg_temp - previous_avg_temp
                st.metric("📊 Average Temperature", f"{current_avg_temp:.1f}°C", delta=f"{temp_change:+.1f}°C vs previous period")
            with col2:
                current_alerts = len(filtered_df[filtered_df['alert_status'] == 'alert'])
                previous_alerts = len(previous_df[previous_df['alert_status'] == 'alert'])
                alert_change = current_alerts - previous_alerts
                st.metric("🚨 Alert Count", current_alerts, delta=f"{alert_change:+d} vs previous period", delta_color="inverse")
            with col3:
                current_std = filtered_df['temperature'].std()
                previous_std = previous_df['temperature'].std()
                stability_change = current_std - previous_std
                st.metric("🎯 Temperature Stability", f"±{current_std:.1f}°C", delta=f"{stability_change:+.2f}°C vs previous period", delta_color="inverse")
            st.info(f"📅 Compared with period: {previous_start.strftime('%B %d')} - {previous_end.strftime('%B %d, %Y')}")
        else:
            st.warning("⚠️ Insufficient data for previous period comparison.")
    st.subheader("🏭 Zone-Specific Historical Performance")
    zone_performance = []
    for zone in zones:
        zone_data = filtered_df[filtered_df['zone_id'] == zone]
        if not zone_data.empty:
            avg_temp = zone_data['temperature'].mean()
            temp_std = zone_data['temperature'].std()
            alert_count = len(zone_data[zone_data['alert_status'] == 'alert'])
            alert_rate = (alert_count / len(zone_data) * 100) if len(zone_data) > 0 else 0
            zone_performance.append({
                'Zone': zone,
                'Avg Temperature': f"{avg_temp:.1f}°C",
                'Stability (±)': f"{temp_std:.2f}°C",
                'Total Alerts': alert_count,
                'Alert Rate': f"{alert_rate:.1f}%",
                'Data Points': len(zone_data)
            })
    if zone_performance:
        performance_df = pd.DataFrame(zone_performance)
        st.dataframe(performance_df, use_container_width=True, hide_index=True)
        if options and options.get('export_filtered', False):
            st.subheader("📥 Export Filtered Data")
            col1, col2, col3 = st.columns(3)
            with col1:
                filtered_csv = filtered_df.to_csv(index=False)
                st.download_button(
                    "📊 Export All Filtered Data",
                    data=filtered_csv,
                    file_name=f"warehouse_data_{start_date}_{end_date}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            with col2:
                alerts_only = filtered_df[filtered_df['alert_status'] == 'alert']
                if not alerts_only.empty:
                    alerts_csv = alerts_only.to_csv(index=False)
                    st.download_button(
                        "🚨 Export Alerts Only",
                        data=alerts_csv,
                        file_name=f"alerts_{start_date}_{end_date}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                else:
                    st.button("🚨 No Alerts to Export", disabled=True, use_container_width=True)
            with col3:
                if zone_performance:
                    performance_csv = pd.DataFrame(zone_performance).to_csv(index=False)
                    st.download_button(
                        "📈 Export Performance Summary",
                        data=performance_csv,
                        file_name=f"performance_summary_{start_date}_{end_date}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
    else:
        st.warning("⚠️ No zone performance data available for selected period.")

# --- Cost analytics and dashboard goes here. Use exactly as in previous assistant message! ---
def calculate_cost_impact_metrics(df, zones):
    """Calculate cost impact metrics for business intelligence"""
    
    # Cost parameters (configurable by warehouse type)
    cost_config = {
        'energy_cost_per_kwh': 0.12,  # $0.12 per kWh
        'product_loss_per_alert': {
            'Z1-Freezer': 150,    # $150 average loss per alert (frozen goods)
            'Z2-Chiller': 75,     # $75 average loss per alert (chilled goods) 
            'Z3-Produce': 200,    # $200 average loss per alert (fresh produce)
            'Z4-Pharma': 2500     # $2500 average loss per alert (pharmaceuticals)
        },
        'maintenance_cost_multiplier': 1.2,  # 20% higher maintenance for poor performance
        'energy_waste_per_degree': 5,  # 5% energy waste per degree deviation
        'insurance_premium_impact': 0.05  # 5% insurance premium impact per major incident
    }
    
    cost_analysis = {}
    total_system_cost = 0
    total_potential_savings = 0
    
    for zone in zones:
        zone_data = df[df['zone_id'] == zone]
        if zone_data.empty:
            continue
        performance_data = calculate_zone_performance_score(df, zone)
        if not performance_data:
            continue
        zone_cost_analysis = {}
        # 1. Product Loss Costs (from alerts)
        alert_count = len(zone_data[zone_data['alert_status'] == 'alert'])
        product_loss_cost = alert_count * cost_config['product_loss_per_alert'][zone]
        zone_cost_analysis['product_loss_cost'] = product_loss_cost
        # 2. Energy Efficiency Costs
        optimal_ranges = {
            'Z1-Freezer': -20,  'Z2-Chiller': 3,  'Z3-Produce': 10,  'Z4-Pharma': -3.5
        }
        optimal_temp = optimal_ranges.get(zone, 0)
        avg_temp = zone_data['temperature'].mean()
        temp_deviation = abs(avg_temp - optimal_temp)
        base_energy_cost = 800  # $800 base monthly energy cost per zone
        energy_waste_percentage = min(temp_deviation * cost_config['energy_waste_per_degree'], 50) / 100
        energy_waste_cost = base_energy_cost * energy_waste_percentage
        zone_cost_analysis['energy_waste_cost'] = energy_waste_cost
        # 3. Maintenance Cost Impact
        performance_score = performance_data['total_score']
        if performance_score < 75:
            maintenance_multiplier = cost_config['maintenance_cost_multiplier'] * (100 - performance_score) / 100
            base_maintenance_cost = 200  # $200 base monthly maintenance per zone
            excess_maintenance_cost = base_maintenance_cost * (maintenance_multiplier - 1)
        else:
            excess_maintenance_cost = 0
        zone_cost_analysis['excess_maintenance_cost'] = excess_maintenance_cost
        # 4. Compliance and Risk Costs
        alert_rate = performance_data['alert_rate']
        if alert_rate > 10:  # High alert rate
            compliance_risk_cost = 500
        elif alert_rate > 5:
            compliance_risk_cost = 200
        else:
            compliance_risk_cost = 0
        zone_cost_analysis['compliance_risk_cost'] = compliance_risk_cost
        # 5. Calculate Potential Savings
        potential_product_loss_reduction = product_loss_cost * 0.8  # 80% reduction in alerts
        potential_energy_savings = energy_waste_cost * 0.7  # 70% energy efficiency improvement
        potential_maintenance_savings = excess_maintenance_cost * 0.6  # 60% maintenance reduction
        zone_potential_savings = (potential_product_loss_reduction +
                                potential_energy_savings +
                                potential_maintenance_savings)
        zone_cost_analysis['potential_monthly_savings'] = zone_potential_savings
        zone_total_cost = (product_loss_cost + energy_waste_cost +
                          excess_maintenance_cost + compliance_risk_cost)
        zone_cost_analysis['total_monthly_cost'] = zone_total_cost
        zone_cost_analysis['performance_score'] = performance_score
        cost_analysis[zone] = zone_cost_analysis
        total_system_cost += zone_total_cost
        total_potential_savings += zone_potential_savings
    cost_analysis['system_totals'] = {
        'total_monthly_cost': total_system_cost,
        'total_potential_savings': total_potential_savings,
        'annual_cost_impact': total_system_cost * 12,
        'annual_savings_potential': total_potential_savings * 12,
        'roi_percentage': (total_potential_savings / max(total_system_cost, 1)) * 100
    }
    return cost_analysis

def create_cost_impact_dashboard(df, zones):
    st.header("💰 Cost Impact Analytics")
    st.markdown("**Transform operational data into business intelligence and financial insights**")
    # Calculate cost metrics
    cost_analysis = calculate_cost_impact_metrics(df, zones)
    if not cost_analysis:
        st.warning("No cost analysis data available")
        return
    system_totals = cost_analysis.get('system_totals', {})
    # Executive Summary - Key Financial Metrics
    st.subheader("📊 Executive Financial Summary")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        monthly_cost = system_totals.get('total_monthly_cost', 0)
        st.metric(
            "💸 Monthly Cost Impact",
            f"${monthly_cost:,.0f}",
            help="Total monthly cost from inefficiencies and alerts"
        )
    with col2:
        potential_savings = system_totals.get('total_potential_savings', 0)
        st.metric(
            "💡 Savings Potential", 
            f"${potential_savings:,.0f}/month",
            delta=f"${potential_savings * 12:,.0f}/year",
            help="Potential monthly savings through optimization"
        )
    with col3:
        roi_percentage = system_totals.get('roi_percentage', 0)
        st.metric(
            "📈 Optimization ROI",
            f"{roi_percentage:.1f}%",
            delta="Monthly return" if roi_percentage > 0 else None,
            help="Return on investment for system optimization"
        )
    with col4:
        annual_impact = system_totals.get('annual_cost_impact', 0)
        st.metric(
            "📅 Annual Impact",
            f"${annual_impact:,.0f}",
            delta=f"${annual_impact - (monthly_cost * 12):+,.0f} vs baseline",
            delta_color="inverse",
            help="Total annual financial impact"
        )
    # Cost Breakdown Analysis
    st.subheader("🔍 Cost Breakdown Analysis")
    cost_breakdown_data = []
    for zone in zones:
        if zone in cost_analysis:
            zone_data = cost_analysis[zone]
            cost_breakdown_data.extend([
                {'Zone': zone, 'Cost Type': 'Product Loss', 'Amount': zone_data['product_loss_cost']},
                {'Zone': zone, 'Cost Type': 'Energy Waste', 'Amount': zone_data['energy_waste_cost']},
                {'Zone': zone, 'Cost Type': 'Excess Maintenance', 'Amount': zone_data['excess_maintenance_cost']},
                {'Zone': zone, 'Cost Type': 'Compliance Risk', 'Amount': zone_data['compliance_risk_cost']}
            ])
    if cost_breakdown_data:
        cost_df = pd.DataFrame(cost_breakdown_data)
        cost_chart = alt.Chart(cost_df).mark_bar().encode(
            x=alt.X('Zone:N', title='Storage Zone'),
            y=alt.Y('Amount:Q', title='Monthly Cost ($)'),
            color=alt.Color(
                'Cost Type:N',
                scale=alt.Scale(range=['#e74c3c', '#f39c12', '#9b59b6', '#34495e']),
                title='Cost Category'
            ),
            tooltip=[
                alt.Tooltip('Zone:N', title='Zone'),
                alt.Tooltip('Cost Type:N', title='Cost Type'),
                alt.Tooltip('Amount:Q', title='Monthly Cost ($)', format='$,.0f')
            ]
        ).properties(
            height=350,
            title="Monthly Cost Breakdown by Zone and Category"
        ).interactive()
        st.altair_chart(cost_chart, use_container_width=True)
    # Zone-specific cost analysis
    st.subheader("🏭 Zone-Specific Cost Analysis")
    zone_cost_summary = []
    for zone in zones:
        if zone in cost_analysis:
            zone_data = cost_analysis[zone]
            zone_cost_summary.append({
                'Zone': zone,
                'Performance Score': f"{zone_data['performance_score']:.1f}/100",
                'Monthly Cost': f"${zone_data['total_monthly_cost']:.0f}",
                'Savings Potential': f"${zone_data['potential_monthly_savings']:.0f}",
                'Annual Impact': f"${zone_data['total_monthly_cost'] * 12:,.0f}",
                'ROI Opportunity': f"{(zone_data['potential_monthly_savings'] / max(zone_data['total_monthly_cost'], 1)) * 100:.1f}%"
            })
    if zone_cost_summary:
        cost_summary_df = pd.DataFrame(zone_cost_summary)
        st.dataframe(cost_summary_df, use_container_width=True, hide_index=True)
    # Business Intelligence Insights
    st.subheader("💡 Business Intelligence Insights")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**🎯 Optimization Priorities:**")
        zone_costs = [(zone, cost_analysis[zone]['total_monthly_cost']) 
                      for zone in zones if zone in cost_analysis]
        zone_costs.sort(key=lambda x: x[1], reverse=True)
        if zone_costs:
            highest_cost_zone = zone_costs[0]
            st.markdown(f"• **Priority 1:** {highest_cost_zone[0]} (${highest_cost_zone[1]:.0f}/month)")
            if len(zone_costs) > 1:
                second_cost_zone = zone_costs[1]
                st.markdown(f"• **Priority 2:** {second_cost_zone[0]} (${second_cost_zone[1]:.0f}/month)")
    with col2:
        st.markdown("**📈 Savings Opportunities:**")
        zone_savings = [(zone, cost_analysis[zone]['potential_monthly_savings']) 
                       for zone in zones if zone in cost_analysis]
        zone_savings.sort(key=lambda x: x[1], reverse=True)
        if zone_savings:
            highest_savings_zone = zone_savings[0]
            st.markdown(f"• **Quick Win:** {highest_savings_zone[0]} (${highest_savings_zone[1]:.0f}/month)")
            total_quick_wins = sum([savings for _, savings in zone_savings[:2]])
            st.markdown(f"• **Combined Impact:** ${total_quick_wins:.0f}/month (${total_quick_wins * 12:.0f}/year)")
    st.subheader("📊 Cost-Performance Correlation")
    correlation_data = []
    for zone in zones:
        if zone in cost_analysis:
            zone_data = cost_analysis[zone]
            correlation_data.append({
                'Zone': zone,
                'Performance Score': zone_data['performance_score'],
                'Monthly Cost': zone_data['total_monthly_cost'],
                'Zone Type': zone.split('-')[1] if '-' in zone else zone
            })
    if correlation_data:
        correlation_df = pd.DataFrame(correlation_data)
        scatter_chart = alt.Chart(correlation_df).mark_circle(size=100).encode(
            x=alt.X('Performance Score:Q', title='Performance Score', scale=alt.Scale(domain=[0, 100])),
            y=alt.Y('Monthly Cost:Q', title='Monthly Cost ($)'),
            color=alt.Color(
                'Zone Type:N',
                scale=alt.Scale(range=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']),
                title='Zone Type'
            ),
            tooltip=[
                alt.Tooltip('Zone:N', title='Zone'),
                alt.Tooltip('Performance Score:Q', title='Performance Score', format='.1f'),
                alt.Tooltip('Monthly Cost:Q', title='Monthly Cost ($)', format='$,.0f')
            ]
        ).properties(
            height=300,
            title="Cost vs Performance Correlation (Lower-left is optimal)"
        ).interactive()
        st.altair_chart(scatter_chart, use_container_width=True)
    st.subheader("🎯 Recommended Actions")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        **🔧 Immediate Actions:**
        • Review high-cost zone configurations
        • Implement threshold optimizations  
        • Schedule maintenance for poor performers
        • Monitor alert patterns for trends
        """)
    with col2:
        st.markdown("""
        **📊 Medium-term Improvements:**
        • Invest in predictive maintenance
        • Upgrade inefficient equipment
        • Implement energy optimization
        • Staff training on best practices
        """)
    with col3:
        st.markdown("""
        **🎯 Strategic Initiatives:**
        • Budget allocation optimization
        • ROI tracking implementation
        • Performance benchmarking
        • Continuous improvement program
        """)
    st.subheader("📥 Export Cost Analysis")
    if cost_analysis:
        cost_report_data = []
        for zone in zones:
            if zone in cost_analysis:
                zone_data = cost_analysis[zone]
                cost_report_data.append({
                    'Zone': zone,
                    'Performance_Score': zone_data['performance_score'],
                    'Product_Loss_Cost': zone_data['product_loss_cost'],
                    'Energy_Waste_Cost': zone_data['energy_waste_cost'],
                    'Excess_Maintenance_Cost': zone_data['excess_maintenance_cost'],
                    'Compliance_Risk_Cost': zone_data['compliance_risk_cost'],
                    'Total_Monthly_Cost': zone_data['total_monthly_cost'],
                    'Potential_Monthly_Savings': zone_data['potential_monthly_savings'],
                    'Annual_Cost_Impact': zone_data['total_monthly_cost'] * 12,
                    'Annual_Savings_Potential': zone_data['potential_monthly_savings'] * 12,
                    'ROI_Percentage': (zone_data['potential_monthly_savings'] / max(zone_data['total_monthly_cost'], 1)) * 100
                })
        if cost_report_data:
            cost_report_df = pd.DataFrame(cost_report_data)
            cost_report_csv = cost_report_df.to_csv(index=False)
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    "💰 Download Cost Analysis Report",
                    data=cost_report_csv,
                    file_name=f"cost_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True,
                    type="primary"
                )
            with col2:
                executive_summary = f"""
Executive Cost Analysis Summary
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

FINANCIAL IMPACT:
• Monthly Cost Impact: ${system_totals.get('total_monthly_cost', 0):,.0f}
• Annual Cost Impact: ${system_totals.get('annual_cost_impact', 0):,.0f}
• Potential Monthly Savings: ${system_totals.get('total_potential_savings', 0):,.0f}
• Potential Annual Savings: ${system_totals.get('annual_savings_potential', 0):,.0f}
• Optimization ROI: {system_totals.get('roi_percentage', 0):.1f}%

ZONE BREAKDOWN:
{chr(10).join([f"• {zone}: ${cost_analysis[zone]['total_monthly_cost']:.0f}/month (Score: {cost_analysis[zone]['performance_score']:.1f})" for zone in zones if zone in cost_analysis])}

RECOMMENDATIONS:
• Focus on highest-cost zones first
• Implement threshold optimizations
• Monitor ROI from improvements
• Regular cost-performance reviews
                """
                st.download_button(
                    "📋 Executive Summary",
                    data=executive_summary,
                    file_name=f"executive_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )




# === MAIN PAGE CONTENT ===

st.set_page_config(page_title="System Overview", layout="wide")

start_date, end_date, filter_options = setup_date_range_filtering()

col1, col2 = st.columns([3, 1])
with col1:
    st.title("🏠 Warehouse System Overview")
    if start_date and end_date:
        date_range = (end_date - start_date).days + 1
        st.markdown(f"**Real-time monitoring with advanced analytics** | 📅 Showing {date_range} days of data")
    else:
        st.markdown("**Real-time monitoring with advanced analytics**")
with col2:
    current_time = datetime.now()
    st.success("🟢 **LIVE**")
    st.caption(f"Updated: {current_time.strftime('%H:%M:%S')}")

st.write("---")

df = load_all_zones_data()
if df.empty:
    st.stop()
if start_date and end_date:
    filtered_df = filter_data_by_date_range(df, start_date, end_date)
    if filtered_df.empty:
        st.error(f"⚠️ No data found for the selected date range: {start_date} to {end_date}")
        st.info("💡 Try selecting a different date range or reset to all data.")
        st.stop()
else:
    filtered_df = df.copy()

zones = ['Z1-Freezer', 'Z2-Chiller', 'Z3-Produce', 'Z4-Pharma']
zone_icons = ['🧊', '❄️', '🥬', '💊']

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Active Zones", f"{len([zone for zone in zones if not filtered_df[filtered_df['zone_id']==zone].empty])}/{len(zones)}")
with col2:
    total_alerts = len(filtered_df[filtered_df['alert_status'] == 'alert'])
    if total_alerts == 0:
        st.metric("Total Alerts", total_alerts, delta="All Clear! 🎉")
    else:
        st.metric("Total Alerts", total_alerts, delta="Needs Attention ⚠️", delta_color="inverse")
with col3:
    avg_system_temp = filtered_df.groupby('zone_id')['temperature'].mean().mean()
    st.metric("Avg System Temp", f"{avg_system_temp:.1f}°C")
with col4:
    update_time = filtered_df['timestamp'].max()
    st.metric("Last Update", update_time.strftime("%H:%M:%S") if pd.notna(update_time) else "N/A")

st.write("---")

if start_date and end_date and filter_options:
    create_historical_analysis_dashboard(filtered_df, zones, start_date, end_date, filter_options)
    st.write("---")

create_performance_dashboard(filtered_df, zones)
st.write("---")

create_cost_impact_dashboard(filtered_df, zones)
st.write("---")

st.header("📊 Zone Status Overview")
col1, col2 = st.columns(2)
col3, col4 = st.columns(2)
columns = [col1, col2, col3, col4]
for i, zone in enumerate(zones):
    with columns[i]:
        summary = get_zone_summary(filtered_df, zone)
        if summary:
            score_info = get_score_color_and_status(summary['performance_score'])
            st.markdown(f"""
            <div style="background: {score_info['bg_color']}; padding: 15px; border-radius: 10px; border-left: 5px solid {score_info['border_color']}; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <h4>{zone_icons[i]} {zone}</h4>
                <p><strong>Performance:</strong> {score_info['emoji']} {summary['performance_score']:.1f}/100 ({score_info['status']})</p>
            </div>
            """, unsafe_allow_html=True)
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("Current Temp", f"{summary['latest_temp']:.1f}°C",
                          delta=f"{summary['temp_trend']:+.1f}°C" if abs(summary['temp_trend']) > 0.01 else None)
                if pd.notna(summary['latest_humidity']):
                    st.metric("Humidity", f"{summary['latest_humidity']:.1f}%")
                else:
                    st.metric("Humidity", "N/A")
            with col_b:
                st.metric("Avg Temp", f"{summary['avg_temp']:.1f}°C")
                st.metric("Alert Rate", f"{summary['alert_rate']:.1f}%")
            st.caption(f"📊 Data points: {summary['data_points']} | ⏰ Updated: {summary['timestamp'].strftime('%H:%M:%S')}")
            button_type = "secondary" if summary['zone_status'] in ['excellent', 'good'] else "primary"
            if st.button(f"📋 View Details", key=f"btn_{zone}", use_container_width=True, type=button_type):
                st.switch_page(f"pages/{zone}.py")
        else:
            st.warning(f"⚠️ No data available for {zone}")

st.write("---")
st.markdown("**🔗 Quick Navigation**")
nav_cols = st.columns(4)
for i, zone in enumerate(zones):
    with nav_cols[i]:
        if st.button(f"{zone_icons[i]} {zone}", key=f"nav_{zone}", use_container_width=True):
            st.switch_page(f"pages/{zone}.py")
st.write("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <p>🏭 <strong>Warehouse Cold Storage Monitoring System</strong> | Advanced Historical + Financial Analytics</p>
    <p>✨ Date filtering • 📊 Period comparison • 💰 Cost analytics • <br> Trend analysis • 📥 Filtered exports</p>
</div>
""", unsafe_allow_html=True)


      
