"""
Creating time-based, lag, and interaction features for AQI prediction
"""

import pandas as pd
import numpy as np
from pathlib import Path


def create_time_features(df):
    """Create time-based features from timestamp."""
    df = df.copy()
    
    # Extract basic time features
    df['hour'] = df['timestamp'].dt.hour
    df['day_of_week'] = df['timestamp'].dt.dayofweek
    df['month'] = df['timestamp'].dt.month
    df['day_of_month'] = df['timestamp'].dt.day
    
    # Cyclical encoding for hour (0-23)
    df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
    df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
    
    # Cyclical encoding for month (1-12)
    df['month_sin'] = np.sin(2 * np.pi * (df['month'] - 1) / 12)
    df['month_cos'] = np.cos(2 * np.pi * (df['month'] - 1) / 12)
    
    # Weekend indicator
    df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
    
    return df


def create_lag_features(df):
    """Create lag features for AQI."""
    df = df.copy()
    
    # Sort by timestamp to ensure correct lag calculation
    df = df.sort_values('timestamp').reset_index(drop=True)
    
    # Lag features (past values)
    df['aqi_lag_1'] = df['aqi'].shift(1)    # 1 hour ago
    df['aqi_lag_24'] = df['aqi'].shift(24)  # 24 hours ago
    df['aqi_lag_168'] = df['aqi'].shift(168)  # 1 week ago
    
    # Rolling features (moving averages and std)
    df['aqi_rolling_mean_24h'] = df['aqi'].rolling(window=24, min_periods=1).mean()
    df['aqi_rolling_std_24h'] = df['aqi'].rolling(window=24, min_periods=1).std()
    
    return df


def create_interaction_features(df):
    """Create interaction features between weather variables."""
    df = df.copy()
    
    # Temperature-Humidity interaction
    df['temp_humidity_interaction'] = df['temperature_2m'] * df['relative_humidity_2m']
    
    # Wind magnitude (combining speed and direction)
    df['wind_x'] = df['wind_speed_10m'] * np.cos(np.radians(df['wind_direction_10m']))
    df['wind_y'] = df['wind_speed_10m'] * np.sin(np.radians(df['wind_direction_10m']))
    
    return df


def select_final_features(df):
    """Select final feature set for modeling."""
    
    # Define feature columns
    feature_cols = [
        # Pollutants (6)
        "pm10", "pm2_5", "carbon_monoxide", "nitrogen_dioxide",
        "sulphur_dioxide", "ozone",
        
        # Weather (6) - Exclude surface_pressure (high VIF)
        "temperature_2m", "relative_humidity_2m",
        "wind_speed_10m", "wind_direction_10m", 
        "precipitation", "cloud_cover",
        
        # Time features (5)
        "hour", "day_of_week", "month",
        "hour_sin", "hour_cos",
        
        # Lag features (2)
        "aqi_lag_1", "aqi_lag_24"
    ]
    
    # Target variable
    target_col = "aqi"
    
    # Metadata columns to keep
    metadata_cols = ["timestamp", "city", "latitude", "longitude"]
    
    # Select columns
    all_cols = metadata_cols + feature_cols + [target_col]
    
    # Keep only columns that exist
    available_cols = [col for col in all_cols if col in df.columns]
    
    return df[available_cols], feature_cols


def main():
    """Main function to engineer features and save processed data."""
    
    print("Feature Engineering Pipeline")
    print("-" * 50)
    
    # Paths
    processed_dir = Path(__file__).resolve().parents[2] / "data" / "processed"
    input_file = processed_dir / "aqi_data.csv"
    output_file = processed_dir / "processed_aqi.csv"
    
    # Load data
    print(f"Loading data from: {input_file}")
    df = pd.read_csv(input_file)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    print(f"Loaded {len(df)} rows")
    
    # Create features
    print("\nCreating time features...")
    df = create_time_features(df)
    
    print("Creating lag features...")
    df = create_lag_features(df)
    
    print("Creating interaction features...")
    df = create_interaction_features(df)
    
    # Select final features
    print("\nSelecting final features...")
    df_final, feature_cols = select_final_features(df)
    
    # Remove rows with NaN (from lag features)
    initial_rows = len(df_final)
    df_final = df_final.dropna()
    removed_rows = initial_rows - len(df_final)
    print(f"Removed {removed_rows} rows with missing values (from lag features)")
    
    # Save processed data
    df_final.to_csv(output_file, index=False)
    
    # Summary
    print(f"\nData saved to: {output_file}")
    print(f"Final rows: {len(df_final)}")
    print(f"Final columns: {len(df_final.columns)}")
    print(f"Features for modeling: {len(feature_cols)}")
    
    print(f"\nFeature list ({len(feature_cols)} features):")
    for i, feat in enumerate(feature_cols, 1):
        print(f"  {i:2d}. {feat}")
    



if __name__ == "__main__":
    main()
