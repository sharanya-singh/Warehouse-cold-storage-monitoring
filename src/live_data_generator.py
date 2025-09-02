import pandas as pd
import numpy as np
import datetime
import time
import os

# Define the temperature and humidity ranges for each zone
ZONE_RANGES = {
    'Z1-Freezer': {'temp_min': -22, 'temp_max': -18, 'humidity_min': 50, 'humidity_max': 70},
    'Z2-Chiller': {'temp_min': 2, 'temp_max': 5, 'humidity_min': 70, 'humidity_max': 80},
    'Z3-Produce': {'temp_min': 5, 'temp_max': 10, 'humidity_min': 80, 'humidity_max': 95},
    'Z4-Pharma': {'temp_min': 2, 'temp_max': 8, 'humidity_min': 50, 'humidity_max': 60}
}

FILE_PATH = 'simulated_warehouse_data_30min_demo.csv'
MAX_TEMP_DRIFT = 1.0  # Maximum temperature change per reading
MAX_HUMIDITY_DRIFT = 3.0  # Maximum humidity change per reading

def get_last_values():
    """Returns a dict with last valid values for each zone"""
    if not os.path.exists(FILE_PATH) or os.path.getsize(FILE_PATH) == 0:
        return {}

    try:
        # Read CSV with proper handling of missing values
        df = pd.read_csv(FILE_PATH, na_values=['NaN', '', 'nan', 'NULL', 'null'])

        # Drop rows with any missing values
        df = df.dropna()

        if df.empty:
            return {}

        last_vals = {}
        for zone_id in ZONE_RANGES.keys():
            zone_data = df[df['zone_id'] == zone_id]
            if not zone_data.empty:
                last_row = zone_data.tail(1).iloc[0]
                # Ensure values are numeric and valid
                try:
                    temp = float(last_row['temperature'])
                    humidity = float(last_row['humidity'])

                    # Validate ranges - if outside reasonable bounds, use defaults
                    zone_range = ZONE_RANGES[zone_id]
                    if temp < zone_range['temp_min'] - 10 or temp > zone_range['temp_max'] + 10:
                        temp = (zone_range['temp_min'] + zone_range['temp_max']) / 2
                    if humidity < 0 or humidity > 100:
                        humidity = (zone_range['humidity_min'] + zone_range['humidity_max']) / 2

                    last_vals[zone_id] = {
                        'temperature': temp,
                        'humidity': humidity
                    }
                except (ValueError, TypeError):
                    # If conversion fails, skip this zone (will use defaults)
                    continue

        return last_vals

    except Exception as e:
        print(f"Warning: Could not read last values: {e}")
        return {}

def generate_realistic_value(current_val, target_min, target_max, max_drift, violation_chance=0.08):
    """Generate realistic sensor values with controlled drift"""

    # Calculate target center
    target_center = (target_min + target_max) / 2

    # If we don't have a current value, start near center
    if current_val is None:
        return round(np.random.uniform(target_min, target_max), 2)

    # Add small random drift
    drift = np.random.normal(0, max_drift * 0.3)
    new_val = current_val + drift

    # Occasionally simulate equipment issues (controlled violations)
    if np.random.rand() < violation_chance:
        # Create a violation but keep it reasonable
        if np.random.rand() < 0.5:
            violation_amount = np.random.uniform(0.5, 2.0)
            new_val = target_min - violation_amount
        else:
            violation_amount = np.random.uniform(0.5, 2.0)
            new_val = target_max + violation_amount
    else:
        # Gentle pull towards optimal range if outside
        if new_val < target_min:
            new_val = target_min + np.random.uniform(0, 1.0)
        elif new_val > target_max:
            new_val = target_max - np.random.uniform(0, 1.0)

    # Ensure drift doesn't exceed maximum change
    if abs(new_val - current_val) > max_drift:
        if new_val > current_val:
            new_val = current_val + max_drift
        else:
            new_val = current_val - max_drift

    return round(new_val, 2)

def generate_data(last_values):
    """Generate new data points for all zones - NO MISSING VALUES"""
    data_points = []

    # Add small time-based variation (simulates daily temperature cycles)
    hour = datetime.datetime.now().hour
    daily_variation = np.sin((hour / 24) * 2 * np.pi) * 0.3  # ±0.3°C daily swing

    for zone_id, ranges in ZONE_RANGES.items():
        prev = last_values.get(zone_id, {})
        prev_temp = prev.get('temperature')
        prev_humidity = prev.get('humidity')

        # Generate temperature with realistic drift
        temp = generate_realistic_value(
            prev_temp,
            ranges['temp_min'],
            ranges['temp_max'],
            MAX_TEMP_DRIFT
        )

        # Add daily variation
        temp += daily_variation

        # Generate humidity with realistic drift
        # Humidity tends to be inversely related to temperature changes
        humidity_adjustment = 0
        if prev_temp is not None:
            temp_change = temp - prev_temp
            humidity_adjustment = -temp_change * 2  # Inverse relationship

        humidity = generate_realistic_value(
            prev_humidity,
            ranges['humidity_min'],
            ranges['humidity_max'],
            MAX_HUMIDITY_DRIFT
        )
        humidity += humidity_adjustment

        # Ensure humidity stays within reasonable bounds
        humidity = max(0, min(100, humidity))
        humidity = round(humidity, 2)

        # Ensure temperature is reasonable (safety bounds)
        if zone_id == 'Z1-Freezer':
            temp = max(-35, min(-10, temp))
        else:
            temp = max(-10, min(25, temp))

        temp = round(temp, 2)

        # Create timestamp
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # GUARANTEE: All values are valid numbers, no NaN or empty strings
        data_points.append({
            'timestamp': timestamp,
            'zone_id': zone_id,
            'temperature': temp,  # Always a valid float
            'humidity': humidity,  # Always a valid float
            'temp_threshold': f"{ranges['temp_min']} to {ranges['temp_max']} °C",
            'humidity_threshold': f"{ranges['humidity_min']} to {ranges['humidity_max']}%"
        })

    return data_points

def clean_existing_data():
    """Clean any existing data file of NaN values"""
    if not os.path.exists(FILE_PATH):
        return

    try:
        # Read existing data
        df = pd.read_csv(FILE_PATH, na_values=['NaN', '', 'nan', 'NULL', 'null'])

        # Count issues before cleaning
        initial_count = len(df)
        nan_count = df.isnull().sum().sum()

        if nan_count > 0:
            print(f"🧹 Cleaning {nan_count} missing values from existing data...")

            # Remove rows with any NaN values
            df_clean = df.dropna()

            # Save cleaned data
            df_clean.to_csv(FILE_PATH, index=False)

            print(f"✅ Cleaned data: {initial_count} → {len(df_clean)} rows")
        else:
            print("✅ Existing data is already clean")

    except Exception as e:
        print(f"Warning: Could not clean existing data: {e}")

def main():
    """Main loop to continuously generate clean data"""
    print("🚀 Starting FIXED data generator (NO missing values)")

    # Clean existing data first
    clean_existing_data()

    # Create file if it doesn't exist
    if not os.path.exists(FILE_PATH):
        header = ['timestamp', 'zone_id', 'temperature', 'humidity', 'temp_threshold', 'humidity_threshold']
        with open(FILE_PATH, 'w') as f:
            f.write(','.join(header) + '\n')
        print("✅ Created new clean data file")

    while True:
        try:
            # Get last valid values
            last_values = get_last_values()

            # Generate new clean data
            new_data = generate_data(last_values)

            # Verify no missing values before saving
            df = pd.DataFrame(new_data)
            if df.isnull().sum().sum() > 0:
                print("❌ ERROR: Generated data contains missing values!")
                continue

            # Save to CSV
            df.to_csv(FILE_PATH, mode='a', header=False, index=False)

            print(f"✅ Generated clean data at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

            # Show current values for monitoring
            for zone_data in new_data:
                temp = zone_data['temperature']
                humidity = zone_data['humidity']
                zone = zone_data['zone_id']
                print(f"   {zone}: {temp}°C, {humidity}%")

            time.sleep(10)

        except Exception as e:
            print(f"❌ Error in main loop: {e}")
            time.sleep(10)  # Wait longer if there's an error

if __name__ == "__main__":
    main()