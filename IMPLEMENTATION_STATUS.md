## Pearls AQI Predictor – Implementation Status

This file compares the **original project brief & meeting notes** with the **actual implementation** in this repository.

In short: **the core end‑to‑end AQI system is complete and production‑ready**, but some of the advanced / optional items from the brief (deep learning, SHAP/LIME explanations, explicit alerting, etc.) are **not implemented**.

---

### 1. High‑Level Status

- **Core goal (3‑day AQI prediction in a serverless pipeline)**: ✅ Implemented
- **Automated feature + training + prediction pipelines**: ✅ Implemented with GitHub Actions
- **Serverless-style architecture** (no long‑running servers you manage): ✅ Implemented using:
  - GitHub Actions (hourly + daily jobs)
  - MongoDB Atlas (cloud DB acting as feature store + registry)
  - Streamlit Cloud / local Streamlit app for the UI
- **Feature store + model registry**: ✅ Implemented in MongoDB
- **Web dashboard for 3‑day forecast + metrics**: ✅ Implemented with Streamlit
- **Multiple ML models & automatic best‑model selection**: ✅ Implemented (RF, XGBoost, LightGBM)
- **Advanced analytics (SHAP/LIME, deep learning, alerting, multi‑model serving)**: ❌ Not implemented
- **Use of Hopsworks / Vertex AI**: ❌ Replaced by MongoDB Atlas (allowed per “Hopswork use or MongoDB” note)

---

### 2. Mapping to Original Requirements

#### 2.1 Feature Pipeline

**Spec requirement**

- Fetch raw weather + pollutant data from AQICN/OpenWeather (or similar)
- Compute:
  - Time‑based features: hour, day, month
  - Derived features like AQI change rate
- Store processed features in a **feature store** (Hopsworks / Vertex AI suggested)
- Historical backfill to create a multi‑month training set

**Implementation in this repo**

- ✅ **Data source**: Uses **OpenMeteo** (air‑quality + weather APIs) instead of AQICN/OpenWeather  
  - Implemented in:
    - `src/data/data_collector.py` (historical)
    - `src/pipeline/collect_and_store_features.py` (hourly live pipeline)
- ✅ **Time‑based features**:
  - `hour`, `day_of_week`, `month`, `hour_sin`, `hour_cos`
- ✅ **Lag / derived features**:
  - `aqi_lag_1`, `aqi_lag_24`
  - Interaction features are mentioned in docs and used in offline experiments
- ⚠️ **AQI change rate feature**:
  - Not explicitly present as a dedicated `aqi_change_rate` column in the production pipeline.
  - Lag features cover similar information but the exact “change rate” feature is missing in the online scripts.
- ✅ **Historical backfill**:
  - `data/processed/processed_aqi.csv` holds ~1 year of processed rows.
  - `src/pipeline/upload_historical_data.py` uploads this to MongoDB.
  - From then on, **live data** comes from the API into MongoDB directly.
- ✅ **Feature store**:
  - Implemented using **MongoDB Atlas**, collection `aqi_features`.
  - This satisfies the “Hopswork use or MongoDB” flexibility from the notes.

**Verdict**: **Feature pipeline is complete**, with a small deviation:
- Uses **OpenMeteo + MongoDB** instead of AQICN/OpenWeather + Hopsworks/Vertex.
- Does **not** explicitly expose an “AQI change rate” column in the production scripts.

---

#### 2.2 Training Pipeline

**Spec requirement**

- Fetch historical features + targets from the feature store
- Train a variety of ML models:
  - scikit‑learn (Random Forest, Ridge Regression)
  - TensorFlow / PyTorch (deep learning)
- Evaluate with **RMSE, MAE, R²**
- Store trained models in a **model registry**
- Automatically select the best model

**Implementation in this repo**

- ✅ **Data source**:
  - Training pipeline reads from MongoDB `aqi_features`:
    - `src/pipeline/train_and_register_model.py`
- ✅ **Models implemented**:
  - `RandomForestRegressor`
  - `XGBRegressor`
  - `LGBMRegressor`
- ❌ **Ridge Regression**: **Not implemented**
- ❌ **TensorFlow / PyTorch deep models**: **Not implemented**
- ✅ **Metrics**:
  - Computes `MAE`, `RMSE`, `R²` for each model.
- ✅ **Best‑model selection**:
  - Chooses the model with highest R².
  - Saves only `models/best_model_<name>.pkl`.
- ✅ **Model registry**:
  - MongoDB collection `model_registry` with:
    - All model metrics
    - `best_model`
    - `best_model_path`
    - `is_latest` flag and baseline vs daily runs
  - Maintains **baseline + last 5 daily** training runs.

**Verdict**: **Training pipeline is functionally complete and robust**, but:
- **Deep learning (TensorFlow/PyTorch)** and **Ridge Regression** from the brief are **not implemented**.

---

#### 2.3 Automated CI/CD Pipeline (Serverless Processing)

**Spec requirement**

- Hourly feature pipeline
- Daily training pipeline
- Daily prediction pipeline
- Serverless execution (e.g., GitHub Actions, Airflow)

**Implementation in this repo**

- ✅ **GitHub Actions workflows** in `.github/workflows/`:
  - `hourly_data_collection.yml` → runs `collect_and_store_features.py` hourly
  - `daily_model_training.yml` → runs `train_and_register_model.py` daily at 02:00 UTC
  - `daily_predictions.yml` → runs `predict_next_3_days.py` daily at 03:00 UTC
- ✅ All workflows:
  - Use `ubuntu-latest`
  - Install dependencies via `pip install -r requirements.txt`
  - Take `MONGODB_URI` and `MONGODB_DATABASE` from **GitHub Secrets**

**Verdict**: **CI/CD pipeline is fully implemented and matches the spec** using GitHub Actions as the serverless orchestrator.

---

#### 2.4 Web Application Dashboard

**Spec requirement**

- Web app (Streamlit/Gradio + Flask/FastAPI) that:
  - Loads models and features from the feature store
  - Computes predictions for the next 3 days
  - Shows interactive charts and metrics
  - Uses latest model from the model registry

**Implementation in this repo**

- ✅ **Framework**: Streamlit (`app.py`)
- ✅ **Data source**:
  - Reads from MongoDB via `MongoDB` helper:
    - `aqi_features` for latest actual AQI
    - `predictions` for 72‑hour forecast
    - `model_registry` for metrics + current best model
- ✅ **Predictions for 3 days**:
  - 72‑hour forecast is generated by `src/pipeline/predict_next_3_days.py`:
    - Uses `model_registry` → loads best model
    - Generates 72 future feature rows
    - Writes results to `predictions` collection
- ✅ **UI behaviour**:
  - Shows **Current AQI** (estimated from latest prediction, or measured fallback)
  - Shows **3‑day forecast** as interactive Plotly line chart with AQI zones
  - Shows **daily summary** (Avg / Min / Max)
  - Shows **model comparison** (RF, XGBoost, LightGBM with metrics)
  - Sidebar buttons:
    - “Collect Fresh Data” → runs `collect_and_store_features.py`
    - “Regenerate Predictions” → runs `predict_next_3_days.py`
- ⚠️ **Where predictions are computed**:
  - In the spec, the web app itself “loads the model and features from the feature store and computes predictions”.
  - Here, **predictions are computed in a separate script** (pipeline) and stored in MongoDB; the UI reads and displays them.
  - The **manual buttons** basically trigger that pipeline locally using `subprocess`, which still respects the **model registry**.

**Verdict**: **Dashboard requirements are effectively met**, with a slightly different architecture:
- Inference runs via **pipeline scripts + MongoDB storage**, not directly inline inside Streamlit.

---

#### 2.5 Advanced Analytics & Extras

**Spec requirement**

- EDA and trend analysis
- SHAP or LIME for feature importance explanations
- Alerts for hazardous AQI levels
- Support for multiple forecasting model families, including deep learning
- Separate SHAP inference script

**Implementation in this repo**

- ✅ **EDA**:
  - Jupyter notebooks under `notebooks/` (EDA, feature selection, etc.).
- ❌ **SHAP / LIME**:
  - No SHAP or LIME code or dependencies present.
  - No separate SHAP inference script.
- ❌ **Automatic alerts**:
  - Dashboard visualizes severity via color and category names.
  - There is **no active alerting mechanism** (e.g., email, SMS, push notifications).
- ❌ **Deep learning / statistical time‑series models**:
  - Only tree‑based ML models are implemented (RF, XGBoost, LightGBM).

**Verdict**: **Advanced analytics section is partially complete** (EDA only).  
SHAP/LIME, explicit alerting, and deep learning models are **not implemented**.

---

#### 2.6 “No CSV, Only Feature Store” Note

**Spec / meeting note**

- “Feature store implementation should be unique data – **no CSV file**, get data from API and maintain data into feature store.”

**Implementation in this repo**

- ✅ **Runtime behaviour**:
  - Hourly/live data pipeline uses **only the API + MongoDB** (`aqi_features`), no CSVs.
- ⚠️ **One‑time historical backfill**:
  - Uses `data/processed/processed_aqi.csv` as a bootstrap dataset.
  - Then that CSV is uploaded to MongoDB via `upload_historical_data.py` and can be ignored afterwards.

**Verdict**: For **ongoing production**, the system **does respect** the “no CSV” idea (MongoDB is the source of truth).  
There is still **one historical CSV** used only for initial backfill.

---

### 3. Overall Conclusion

- The repository **fully delivers an end‑to‑end, automated, serverless AQI prediction system** with:
  - Hourly feature pipeline
  - Daily training + automatic best‑model selection
  - Daily 72‑hour predictions
  - MongoDB‑based feature store and model registry
  - Streamlit dashboard for real‑time visualization
- Compared to the **original extended brief**, the following are **missing or intentionally simplified**:
  - No **TensorFlow/PyTorch** or **Ridge Regression** models
  - No **SHAP/LIME** explanations or SHAP‑specific inference script
  - No explicit **alerting system** (email/SMS/webhook) for hazardous AQI
  - Feature store is **MongoDB**, not Hopsworks/Vertex AI (accepted by later notes)
  - “AQI change rate” is not a separate feature in the production scripts (lags are used instead)

From a practical, production standpoint, the **core implementation is complete**.  
To match every line of the original brief, the missing advanced items listed above would be the next steps.

