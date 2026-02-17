"""
Training Random Forest, XGBoost, and LightGBM models for AQI prediction
"""

import pandas as pd
import numpy as np
import json
import joblib
from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import xgboost as xgb
import lightgbm as lgb


def load_data():
    """Load processed data."""
    processed_dir = Path(__file__).resolve().parents[2] / "data" / "processed"
    df = pd.read_csv(processed_dir / "processed_aqi.csv")
    print(f"Loaded {len(df)} rows")
    return df


def prepare_data(df):
    """Prepare features and target."""
    
    # 19 features
    features = [
        "pm10", "pm2_5", "carbon_monoxide", "nitrogen_dioxide",
        "sulphur_dioxide", "ozone", "temperature_2m", "relative_humidity_2m",
        "wind_speed_10m", "wind_direction_10m", "precipitation", "cloud_cover",
        "hour", "day_of_week", "month", "hour_sin", "hour_cos",
        "aqi_lag_1", "aqi_lag_24"
    ]
    
    X = df[features]
    y = df["aqi"]
    
    # Split: 80% train, 20% test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, shuffle=False
    )
    
    print(f"Train: {len(X_train)}, Test: {len(X_test)}")
    return X_train, X_test, y_train, y_test, features


def train_models(X_train, y_train):
    """Train all 3 models."""
    
    print("\nTraining models...")
    
    models = {
        "Random Forest": RandomForestRegressor(
            n_estimators=100, max_depth=20, random_state=42, n_jobs=-1
        ),
        "XGBoost": xgb.XGBRegressor(
            n_estimators=200, max_depth=10, learning_rate=0.1, random_state=42, n_jobs=-1
        ),
        "LightGBM": lgb.LGBMRegressor(
            n_estimators=200, max_depth=10, learning_rate=0.1, random_state=42, n_jobs=-1, verbose=-1
        )
    }
    
    for name, model in models.items():
        model.fit(X_train, y_train)
        print(f"  ✓ {name}")
    
    return models


def evaluate_models(models, X_test, y_test):
    """Evaluate all models and return metrics."""
    
    print("\nEvaluating models...")
    results = {}
    
    for name, model in models.items():
        y_pred = model.predict(X_test)
        
        results[name] = {
            "MAE": round(mean_absolute_error(y_test, y_pred), 2),
            "RMSE": round(np.sqrt(mean_squared_error(y_test, y_pred)), 2),
            "R2": round(r2_score(y_test, y_pred), 4)
        }
        
        print(f"\n{name}:")
        print(f"  R²:   {results[name]['R2']:.4f}")
        print(f"  RMSE: {results[name]['RMSE']:.2f}")
        print(f"  MAE:  {results[name]['MAE']:.2f}")
    
    return results


def select_best_model(results):
    """Select model with highest R²."""
    best_model = max(results.items(), key=lambda x: x[1]['R2'])
    return best_model[0]


def save_results(models, results, features):
    """Save models and metrics."""
    
    models_dir = Path(__file__).resolve().parents[2] / "models"
    models_dir.mkdir(exist_ok=True)
    
    # Save models
    for name, model in models.items():
        filename = name.lower().replace(" ", "_") + ".pkl"
        joblib.dump(model, models_dir / filename)
    
    # Save metrics
    with open(models_dir / "model_metrics.json", 'w') as f:
        json.dump(results, f, indent=2)
    
    # Save features
    with open(models_dir / "feature_columns.json", 'w') as f:
        json.dump(features, f, indent=2)
    
    print(f"\nSaved to: {models_dir}")


def main():
    """Main training pipeline."""
    
    print("Training AQI Prediction Models")
    print("-" * 50)
    
    # Load and prepare data
    df = load_data()
    X_train, X_test, y_train, y_test, features = prepare_data(df)
    
    # Train models
    models = train_models(X_train, y_train)
    
    # Evaluate models
    results = evaluate_models(models, X_test, y_test)
    
    # Select best model
    best_model = select_best_model(results)
    
    print("\n" + "=" * 50)
    print(f"Best Model: {best_model}")
    print(f"R²: {results[best_model]['R2']:.4f}")
    print("=" * 50)
    
    # Save everything
    save_results(models, results, features)
    
    print("\nTraining complete!")


if __name__ == "__main__":
    main()
