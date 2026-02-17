"""
Experiment 3: Manual Parameter Optimization
Using best parameters from Experiment 2 with slight adjustments
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
    print(f"Loaded {len(df)} rows\n")
    return df


def prepare_data(df):
    """Prepare features and target."""
    
    features = [
        "pm10", "pm2_5", "carbon_monoxide", "nitrogen_dioxide",
        "sulphur_dioxide", "ozone", "temperature_2m", "relative_humidity_2m",
        "wind_speed_10m", "wind_direction_10m", "precipitation", "cloud_cover",
        "hour", "day_of_week", "month", "hour_sin", "hour_cos",
        "aqi_lag_1", "aqi_lag_24"
    ]
    
    X = df[features]
    y = df["aqi"]
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, shuffle=False
    )
    
    print(f"Train: {len(X_train)}, Test: {len(X_test)}\n")
    return X_train, X_test, y_train, y_test, features


def train_models(X_train, y_train):
    """Train models with optimized parameters."""
    
    print("Training models with optimized parameters...\n")
    
    # Random Forest - improved from Exp 2
    print("[1/3] Random Forest...")
    rf = RandomForestRegressor(
        n_estimators=300,
        max_depth=25,
        min_samples_split=5,
        min_samples_leaf=4,
        random_state=42,
        n_jobs=-1
    )
    rf.fit(X_train, y_train)
    
    # XGBoost - improved from Exp 2
    print("[2/3] XGBoost...")
    xgb_model = xgb.XGBRegressor(
        n_estimators=300,
        max_depth=8,
        learning_rate=0.05,
        subsample=0.9,
        colsample_bytree=0.9,
        random_state=42,
        n_jobs=-1
    )
    xgb_model.fit(X_train, y_train)
    
    # LightGBM - best from Exp 2 with minor tweaks
    print("[3/3] LightGBM...")
    lgb_model = lgb.LGBMRegressor(
        n_estimators=400,
        max_depth=12,
        learning_rate=0.05,
        num_leaves=50,
        subsample=0.9,
        colsample_bytree=0.9,
        min_child_samples=25,
        random_state=42,
        n_jobs=-1,
        verbose=-1
    )
    lgb_model.fit(X_train, y_train)
    
    print()
    return {
        "Random Forest": rf,
        "XGBoost": xgb_model,
        "LightGBM": lgb_model
    }


def evaluate_models(models, X_test, y_test):
    """Evaluate all models."""
    
    print("Evaluating models...\n")
    results = {}
    
    for name, model in models.items():
        y_pred = model.predict(X_test)
        
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)
        
        results[name] = {
            "MAE": round(mae, 2),
            "RMSE": round(rmse, 2),
            "R2": round(r2, 4)
        }
        
        print(f"{name}:")
        print(f"  R²:   {r2:.4f}")
        print(f"  RMSE: {rmse:.2f}")
        print(f"  MAE:  {mae:.2f}\n")
    
    return results


def save_results(models, results, features):
    """Save models and results."""
    
    models_dir = Path(__file__).resolve().parents[2] / "models"
    models_dir.mkdir(exist_ok=True)
    
    # Save models
    for name, model in models.items():
        filename = name.lower().replace(" ", "_") + "_exp3.pkl"
        joblib.dump(model, models_dir / filename)
    
    # Save results
    with open(models_dir / "experiment_3_results.json", 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Saved to: {models_dir}\n")


def main():
    """Main training pipeline."""
    
    print("Experiment 3: Manual Parameter Optimization\n")
    
    # Load and prepare data
    df = load_data()
    X_train, X_test, y_train, y_test, features = prepare_data(df)
    
    # Train models
    models = train_models(X_train, y_train)
    
    # Evaluate models
    results = evaluate_models(models, X_test, y_test)
    
    # Select best model
    best_model = max(results.items(), key=lambda x: x[1]['R2'])
    print(f"Best Model: {best_model[0]} (R² = {best_model[1]['R2']:.4f})\n")
    
    # Save results
    save_results(models, results, features)


if __name__ == "__main__":
    main()
