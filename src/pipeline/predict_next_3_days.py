"""
Predict next 3 days (72 hours) AQI
Loads best model from MongoDB registry and generates forecast
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
import joblib
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.append(str(Path(__file__).resolve().parents[2]))

from src.database.mongo_db import MongoDB


def load_best_model_from_registry():
    """Load best model info from MongoDB registry."""
    
    print("Loading best model from registry...")
    
    mongo = MongoDB()
    mongo.connect()
    
    collection = mongo.get_collection("model_registry")
    registry = collection.find_one()
    
    mongo.close()
    
    if not registry:
        print("Error: No model registry found!")
        return None, None
    
    best_model_name = registry['best_model']
    best_model_path = registry['best_model_path']
    
    print(f"Best model: {best_model_name} (R² = {registry['models'][best_model_name]['r2']})\n")
    
    # Load model from disk
    model_file = Path(__file__).resolve().parents[2] / best_model_path
    model = joblib.load(model_file)
    
    return model, best_model_name


def get_latest_data_from_mongodb():
    """Get latest data point for lag features."""
    
    print("Loading latest data from MongoDB...")
    
    mongo = MongoDB()
    mongo.connect()
    
    collection = mongo.get_collection("aqi_features")
    # Get last 24 hours for lag features
    latest_data = list(collection.find().sort("timestamp", -1).limit(24))
    
    mongo.close()
    
    df = pd.DataFrame(latest_data)
    df = df.drop('_id', axis=1)
    
    print(f"Loaded {len(df)} recent records\n")
    return df


def generate_forecast_features(latest_df, hours_ahead=72):
    """Generate features for next 72 hours."""
    
    print(f"Generating forecast for next {hours_ahead} hours...\n")
    
    # Get last timestamp
    latest_df['timestamp'] = pd.to_datetime(latest_df['timestamp'])
    last_timestamp = latest_df['timestamp'].max()
    
    # Generate future timestamps
    future_timestamps = [last_timestamp + timedelta(hours=i+1) for i in range(hours_ahead)]
    
    # Create forecast dataframe
    forecast_data = []
    
    for ts in future_timestamps:
        # Time features
        hour = ts.hour
        day_of_week = ts.dayofweek
        month = ts.month
        hour_sin = np.sin(2 * np.pi * hour / 24)
        hour_cos = np.cos(2 * np.pi * hour / 24)
        
        # For simplicity, use average values from latest data
        # In production, you'd use weather forecast API
        avg_pm10 = latest_df['pm10'].mean()
        avg_pm25 = latest_df['pm2_5'].mean()
        avg_co = latest_df['carbon_monoxide'].mean()
        avg_no2 = latest_df['nitrogen_dioxide'].mean()
        avg_so2 = latest_df['sulphur_dioxide'].mean()
        avg_o3 = latest_df['ozone'].mean()
        avg_temp = latest_df['temperature_2m'].mean()
        avg_humidity = latest_df['relative_humidity_2m'].mean()
        avg_wind_speed = latest_df['wind_speed_10m'].mean()
        avg_wind_dir = latest_df['wind_direction_10m'].mean()
        avg_precip = latest_df['precipitation'].mean()
        avg_cloud = latest_df['cloud_cover'].mean()
        
        # Lag features (use last known AQI)
        aqi_lag_1 = latest_df['aqi'].iloc[0]  # Most recent
        aqi_lag_24 = latest_df['aqi'].iloc[-1] if len(latest_df) >= 24 else latest_df['aqi'].iloc[0]
        
        forecast_data.append({
            'timestamp': ts,
            'pm10': avg_pm10,
            'pm2_5': avg_pm25,
            'carbon_monoxide': avg_co,
            'nitrogen_dioxide': avg_no2,
            'sulphur_dioxide': avg_so2,
            'ozone': avg_o3,
            'temperature_2m': avg_temp,
            'relative_humidity_2m': avg_humidity,
            'wind_speed_10m': avg_wind_speed,
            'wind_direction_10m': avg_wind_dir,
            'precipitation': avg_precip,
            'cloud_cover': avg_cloud,
            'hour': hour,
            'day_of_week': day_of_week,
            'month': month,
            'hour_sin': hour_sin,
            'hour_cos': hour_cos,
            'aqi_lag_1': aqi_lag_1,
            'aqi_lag_24': aqi_lag_24
        })
    
    return pd.DataFrame(forecast_data)


def make_predictions(model, forecast_df):
    """Make AQI predictions."""
    
    features = [
        "pm10", "pm2_5", "carbon_monoxide", "nitrogen_dioxide",
        "sulphur_dioxide", "ozone", "temperature_2m", "relative_humidity_2m",
        "wind_speed_10m", "wind_direction_10m", "precipitation", "cloud_cover",
        "hour", "day_of_week", "month", "hour_sin", "hour_cos",
        "aqi_lag_1", "aqi_lag_24"
    ]
    
    X = forecast_df[features]
    predictions = model.predict(X)
    
    forecast_df['predicted_aqi'] = predictions.round().astype(int)
    
    return forecast_df


def save_predictions_to_mongodb(forecast_df, model_name):
    """Save predictions to MongoDB."""
    
    print("Saving predictions to MongoDB...")
    
    mongo = MongoDB()
    mongo.connect()
    
    collection = mongo.get_collection("predictions")
    
    # Clear old predictions
    collection.delete_many({})
    
    # Prepare prediction documents
    predictions = []
    prediction_date = datetime.utcnow().isoformat()
    
    for _, row in forecast_df.iterrows():
        predictions.append({
            'timestamp': row['timestamp'].isoformat(),
            'predicted_aqi': int(row['predicted_aqi']),
            'model_used': model_name,
            'prediction_date': prediction_date
        })
    
    collection.insert_many(predictions)
    
    print(f"Saved {len(predictions)} predictions\n")
    
    mongo.close()


def display_summary(forecast_df):
    """Display prediction summary."""
    
    print("Prediction Summary:\n")
    
    # Group by day
    forecast_df['date'] = forecast_df['timestamp'].dt.date
    daily_avg = forecast_df.groupby('date')['predicted_aqi'].agg(['mean', 'min', 'max'])
    
    for date, row in daily_avg.iterrows():
        print(f"{date}:")
        print(f"  Avg AQI: {row['mean']:.0f}")
        print(f"  Range: {row['min']:.0f} - {row['max']:.0f}\n")


def main():
    """Main prediction pipeline."""
    
    print("3-Day AQI Prediction Pipeline\n")
    
    # Load best model
    model, model_name = load_best_model_from_registry()
    if model is None:
        return
    
    # Get latest data
    latest_df = get_latest_data_from_mongodb()
    
    # Generate forecast features
    forecast_df = generate_forecast_features(latest_df, hours_ahead=72)
    
    # Make predictions
    forecast_df = make_predictions(model, forecast_df)
    
    # Display summary
    display_summary(forecast_df)
    
    # Save to MongoDB
    save_predictions_to_mongodb(forecast_df, model_name)
    
    print("Prediction complete!")


if __name__ == "__main__":
    main()
