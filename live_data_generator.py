import pandas as pd
import numpy as np
import datetime
import time
import os

# Define the temperature and humidity ranges for each zone
ZONE_RANGES = {
    'Z1-Freezer': {'temp_min': -22, 'temp_max': -18, 'humidity_min': 50, 'humidity_max': 70},
    'Z2-Chiller': {'temp_min': 2, 'temp_max': 4, 'humidity_min': 70, 'humidity_max': 80},
    'Z3-Produce': {'temp_min': 8, 'temp_max': 12, 'humidity_min': 80, 'humidity_max': 95},
    'Z4-Pharma': {'temp_min': -5, 'temp_max': -2, 'humidity_min': 50, 'humidity_max': 60}
}

FILE_PATH = 'simulated_warehouse_data_30min_demo.csv'

def get_latest_data():
    """Reads the last row of the CSV to get the latest sensor values."""
    if os.path.exists(FILE_PATH) and os.path.getsize(FILE_PATH) > 0:
        try:
            return pd.read_csv(FILE_PATH).iloc[-1]
        except pd.errors.EmptyDataError:
            return None
    return None

def generate_data():
    """Generates new data points for all zones."""
    data_points = []
    violation_chance = 0.1  # 10% chance to generate values outside range

    for zone_id, ranges in ZONE_RANGES.items():

        def simulate_value(min_val, max_val):
            if np.random.rand() < violation_chance:
                # Generate a value outside the range (up to 3 degrees/humidity units beyond limits)
                outside_amount = np.random.uniform(0.1, 3.0)
                if np.random.rand() < 0.5:
                    return round(min_val - outside_amount, 2)
                else:
                    return round(max_val + outside_amount, 2)
            else:
                # Generate value within the range
                return round(np.random.uniform(min_val, max_val), 2)

        temp = simulate_value(ranges['temp_min'], ranges['temp_max'])
        humidity = simulate_value(ranges['humidity_min'], ranges['humidity_max'])

        # Determine alert status
        alert_status = 'normal'
        if temp < ranges['temp_min'] or temp > ranges['temp_max']:
            alert_status = 'alert'
        if humidity < ranges['humidity_min'] or humidity > ranges['humidity_max']:
            alert_status = 'alert'

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Record temperature data point
        data_points.append({
            'timestamp': timestamp,
            'zone_id': zone_id,
            'metric': 'temperature',
            'value': temp,
            'threshold': f"{ranges['temp_min']} to {ranges['temp_max']} °C",
            'alert_status': alert_status
        })

        # Record humidity data point
        data_points.append({
            'timestamp': timestamp,
            'zone_id': zone_id,
            'metric': 'humidity',
            'value': humidity,
            'threshold': f"{ranges['humidity_min']} to {ranges['humidity_max']}%",
            'alert_status': alert_status
        })

    return data_points

def main():
    """Main loop to continuously generate and append data."""
    if not os.path.exists(FILE_PATH):
        header = ['timestamp', 'zone_id', 'metric', 'value', 'threshold', 'alert_status']
        with open(FILE_PATH, 'w') as f:
            f.write(','.join(header) + '\n')

    while True:
        new_data = generate_data()
        df = pd.DataFrame(new_data)
        df.to_csv(FILE_PATH, mode='a', header=False, index=False)
        print(f"Generated data batch at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        time.sleep(2)  # Wait 2 seconds before next data generation

if __name__ == "__main__":
    main()

