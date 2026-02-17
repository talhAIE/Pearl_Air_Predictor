"""
AQI Calculation Script
Calculates Air Quality Index from pollutant concentrations using EPA standards
"""

import pandas as pd
import numpy as np
from pathlib import Path


# EPA AQI Breakpoints
# Format: (C_low, C_high, I_low, I_high)

PM25_BREAKPOINTS = [
    (0.0, 12.0, 0, 50),
    (12.1, 35.4, 51, 100),
    (35.5, 55.4, 101, 150),
    (55.5, 150.4, 151, 200),
    (150.5, 250.4, 201, 300),
    (250.5, 500.4, 301, 500)
]

PM10_BREAKPOINTS = [
    (0, 54, 0, 50),
    (55, 154, 51, 100),
    (155, 254, 101, 150),
    (255, 354, 151, 200),
    (355, 424, 201, 300),
    (425, 604, 301, 500)
]

O3_BREAKPOINTS = [
    (0, 54, 0, 50),
    (55, 70, 51, 100),
    (71, 85, 101, 150),
    (86, 105, 151, 200),
    (106, 200, 201, 300)
]

NO2_BREAKPOINTS = [
    (0, 53, 0, 50),
    (54, 100, 51, 100),
    (101, 360, 101, 150),
    (361, 649, 151, 200),
    (650, 1249, 201, 300),
    (1250, 2049, 301, 500)
]

SO2_BREAKPOINTS = [
    (0, 35, 0, 50),
    (36, 75, 51, 100),
    (76, 185, 101, 150),
    (186, 304, 151, 200),
    (305, 604, 201, 300),
    (605, 1004, 301, 500)
]

CO_BREAKPOINTS = [
    (0, 4.4, 0, 50),
    (4.5, 9.4, 51, 100),
    (9.5, 12.4, 101, 150),
    (12.5, 15.4, 151, 200),
    (15.5, 30.4, 201, 300),
    (30.5, 50.4, 301, 500)
]


def calculate_aqi_single(concentration, breakpoints):
    """
    Calculate AQI for a single pollutant using EPA formula.
    
    Args:
        concentration: Pollutant concentration
        breakpoints: List of (C_low, C_high, I_low, I_high) tuples
        
    Returns:
        AQI value (int)
    """
    if pd.isna(concentration) or concentration < 0:
        return np.nan
    
    # Find the appropriate breakpoint
    for c_low, c_high, i_low, i_high in breakpoints:
        if c_low <= concentration <= c_high:
            # EPA AQI formula
            aqi = ((i_high - i_low) / (c_high - c_low)) * (concentration - c_low) + i_low
            return round(aqi)
    
    # If concentration exceeds all breakpoints, return max AQI
    return 500


def calculate_aqi_pm25(pm25):
    """Calculate AQI from PM2.5 concentration."""
    return calculate_aqi_single(pm25, PM25_BREAKPOINTS)


def calculate_aqi_pm10(pm10):
    """Calculate AQI from PM10 concentration."""
    return calculate_aqi_single(pm10, PM10_BREAKPOINTS)


def calculate_aqi_o3(o3):
    """Calculate AQI from Ozone concentration."""
    return calculate_aqi_single(o3, O3_BREAKPOINTS)


def calculate_aqi_no2(no2):
    """Calculate AQI from NO2 concentration."""
    return calculate_aqi_single(no2, NO2_BREAKPOINTS)


def calculate_aqi_so2(so2):
    """Calculate AQI from SO2 concentration."""
    return calculate_aqi_single(so2, SO2_BREAKPOINTS)


def calculate_aqi_co(co):
    """Calculate AQI from CO concentration (convert to ppm)."""
    # CO is in µg/m³, convert to ppm: ppm = µg/m³ / 1145
    co_ppm = co / 1145.0 if not pd.isna(co) else np.nan
    return calculate_aqi_single(co_ppm, CO_BREAKPOINTS)


def get_aqi_category(aqi):
    """Get AQI category name from AQI value."""
    if pd.isna(aqi):
        return "Unknown"
    elif aqi <= 50:
        return "Good"
    elif aqi <= 100:
        return "Moderate"
    elif aqi <= 150:
        return "Unhealthy for Sensitive Groups"
    elif aqi <= 200:
        return "Unhealthy"
    elif aqi <= 300:
        return "Very Unhealthy"
    else:
        return "Hazardous"


def main():
    """Main function to calculate AQI and save processed data."""
    
    print("Calculating AQI from pollutant data...")
    
    # Paths
    raw_dir = Path(__file__).resolve().parents[2] / "data" / "raw"
    processed_dir = Path(__file__).resolve().parents[2] / "data" / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)
    
    # Find the most recent raw data file
    raw_files = list(raw_dir.glob("raw_data_*.csv"))
    if not raw_files:
        print("Error: No raw data files found in data/raw/")
        return
    
    latest_file = max(raw_files, key=lambda p: p.stat().st_mtime)
    print(f"Loading data from: {latest_file.name}")
    
    # Load data
    df = pd.read_csv(latest_file)
    print(f"Loaded {len(df)} rows")
    
    # Calculate AQI for each pollutant
    print("\nCalculating AQI for each pollutant...")
    df['aqi_pm25'] = df['pm2_5'].apply(calculate_aqi_pm25)
    df['aqi_pm10'] = df['pm10'].apply(calculate_aqi_pm10)
    df['aqi_o3'] = df['ozone'].apply(calculate_aqi_o3)
    df['aqi_no2'] = df['nitrogen_dioxide'].apply(calculate_aqi_no2)
    df['aqi_so2'] = df['sulphur_dioxide'].apply(calculate_aqi_so2)
    df['aqi_co'] = df['carbon_monoxide'].apply(calculate_aqi_co)
    
    # Calculate overall AQI (maximum of all pollutants)
    aqi_columns = ['aqi_pm25', 'aqi_pm10', 'aqi_o3', 'aqi_no2', 'aqi_so2', 'aqi_co']
    df['aqi'] = df[aqi_columns].max(axis=1)
    
    # Add AQI category
    df['aqi_category'] = df['aqi'].apply(get_aqi_category)
    
    # Save processed data
    output_file = processed_dir / "aqi_data.csv"
    df.to_csv(output_file, index=False)
    
    # Summary
    print(f"\nData saved to: {output_file}")
    print(f"Total rows: {len(df)}, Columns: {len(df.columns)}")
    
    print("\nAQI Statistics:")
    print(f"  Mean: {df['aqi'].mean():.1f}")
    print(f"  Min: {df['aqi'].min():.0f}")
    print(f"  Max: {df['aqi'].max():.0f}")
    
    print("\nAQI Categories:")
    for category, count in df['aqi_category'].value_counts().sort_index().items():
        print(f"  {category}: {count}")
    
    print("\nDominant Pollutant:")
    dominant = df[aqi_columns].idxmax(axis=1).value_counts()
    for pollutant, count in dominant.items():
        pollutant_name = pollutant.replace('aqi_', '').upper()
        percentage = (count / len(df)) * 100
        print(f"  {pollutant_name}: {percentage:.1f}%")
    
    


if __name__ == "__main__":
    main()
