"""
Experiment 2: Hyperparameter Tuning
"""

import pandas as pd
import numpy as np
import json
import joblib
from pathlib import Path

from sklearn.model_selection import train_test_split, RandomizedSearchCV
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


def tune_models(X_train, y_train):
    """Tune all models with RandomizedSearchCV."""
    
    print("Tuning models ...\n")
    
    # Random Forest
    print("[1/3] Random Forest...")
    rf_params = {
        'n_estimators': [100, 200, 300],
        'max_depth': [15, 20, 25, 30],
        'min_samples_split': [2, 5, 10],
        'min_samples_leaf': [1, 2, 4]
    }
    rf_search = RandomizedSearchCV(
        RandomForestRegressor(random_state=42, n_jobs=-1),
        rf_params, n_iter=10, cv=3, scoring='r2', random_state=42, n_jobs=-1
    )
    rf_search.fit(X_train, y_train)
    print(f"  Best R²: {rf_search.best_score_:.4f}")
    
    # XGBoost
    print("\n[2/3] XGBoost...")
    xgb_params = {
        'n_estimators': [100, 200, 300],
        'max_depth': [6, 8, 10, 12],
        'learning_rate': [0.01, 0.05, 0.1],
        'subsample': [0.8, 0.9, 1.0],
        'colsample_bytree': [0.8, 0.9, 1.0]
    }
    xgb_search = RandomizedSearchCV(
        xgb.XGBRegressor(random_state=42, n_jobs=-1),
        xgb_params, n_iter=10, cv=3, scoring='r2', random_state=42, n_jobs=-1
    )
    xgb_search.fit(X_train, y_train)
    print(f"  Best R²: {xgb_search.best_score_:.4f}")
    
    # LightGBM
    print("\n[3/3] LightGBM...")
    lgb_params = {
        'n_estimators': [100, 200, 300],
        'max_depth': [8, 10, 12, 15],
        'learning_rate': [0.01, 0.05, 0.1],
        'num_leaves': [31, 50, 70],
        'subsample': [0.8, 0.9, 1.0]
    }
    lgb_search = RandomizedSearchCV(
        lgb.LGBMRegressor(random_state=42, n_jobs=-1, verbose=-1),
        lgb_params, n_iter=10, cv=3, scoring='r2', random_state=42, n_jobs=-1
    )
    lgb_search.fit(X_train, y_train)
    print(f"  Best R²: {lgb_search.best_score_:.4f}\n")
    
    return {
        "Random Forest": rf_search.best_estimator_,
        "XGBoost": xgb_search.best_estimator_,
        "LightGBM": lgb_search.best_estimator_
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
    
    # Save tuned models
    for name, model in models.items():
        filename = name.lower().replace(" ", "_") + "_tuned.pkl"
        joblib.dump(model, models_dir / filename)
    
    # Save results
    with open(models_dir / "experiment_2_results.json", 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Saved to: {models_dir}\n")


def main():
    """Main training pipeline."""
    
    print("Experiment 2: Hyperparameter Tuning\n")
    
    # Load and prepare data
    df = load_data()
    X_train, X_test, y_train, y_test, features = prepare_data(df)
    
    # Tune models
    models = tune_models(X_train, y_train)
    
    # Evaluate models
    results = evaluate_models(models, X_test, y_test)
    
    # Select best model
    best_model = max(results.items(), key=lambda x: x[1]['R2'])
    print(f"Best Model: {best_model[0]} (R² = {best_model[1]['R2']:.4f})\n")
    
    # Save results
    save_results(models, results, features)
    
    


if __name__ == "__main__":
    main()
