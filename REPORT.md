<div align="center">

# Air Quality Index (AQI) Forecasting System  
### End‑to‑End Machine Learning Project

---

**Submitted by**  
**Talha Abbasi**

**Organization**  
Pearls Organization

**Date**  
17 February 2026

</div>

---

## 1. Introduction

This report explains a small but complete **Air Quality Index (AQI) forecasting system** for **Islamabad, Pakistan**.  
The system collects air and weather data, trains machine learning models, makes 3‑day AQI forecasts, and shows results in a web dashboard.

The main ideas of the project are:

- use real hourly data from a public API  
- build a clear pipeline from data to prediction  
- keep everything simple so another student can understand and run it  

---

## 2. Project Summary

### 2.1 High‑level description

The project predicts AQI for the **next 72 hours** (3 days).  
It uses:

- **OpenMeteo** for air quality and weather data  
- **MongoDB Atlas** as a cloud database  
- **Random Forest, XGBoost and LightGBM** as models  
- **Streamlit** for the user interface  
- **GitHub Actions** to keep the system updated automatically  

### 2.2 System overview table

| Layer              | Main tools / files                             | Purpose                                   |
|--------------------|-----------------------------------------------|-------------------------------------------|
| Data collection    | `data_collector.py`, `collect_and_store_features.py` | Get raw and live data from OpenMeteo      |
| Feature engineering| `calculate_aqi.py`, `feature_engineering.py`  | Turn raw data into AQI and features       |
| Modeling           | `train_and_register_model.py`                 | Train 3 models and pick the best          |
| Prediction         | `predict_next_3_days.py`                      | Make 72‑hour AQI forecast                 |
| Storage            | `mongo_db.py`, MongoDB Atlas                  | Save features, models and predictions     |
| Dashboard          | `app.py` (Streamlit)                          | Show current AQI, forecast and metrics    |

---

## 3. Data Collection

### 3.1 Data source

The project uses the **OpenMeteo** APIs:

- **Air quality API**  
  - pollutants: PM2.5, PM10, CO, NO₂, SO₂, O₃  
- **Weather API**  
  - variables: temperature, humidity, wind speed, wind direction, precipitation, cloud cover  

The city is **Islamabad**. The latitude and longitude are set in environment variables but default to the known coordinates.

### 3.2 Historical data (one‑time)

File: `src/data/data_collector.py`

This script:

- reads the city name and coordinates  
- downloads around **one year of hourly data** from both APIs  
- merges air and weather data on the timestamp  
- drops rows with missing key values  
- saves the result to `data/raw/` as a CSV file  

This CSV is later converted into AQI and features.

### 3.3 Live hourly data

File: `src/pipeline/collect_and_store_features.py`

This pipeline is used after the historical load. It:

- asks OpenMeteo for the last hour of data  
- calculates AQI for that hour  
- adds time and lag features  
- writes one document into the `aqi_features` collection in MongoDB  

This script can be called locally or from GitHub Actions (hourly).

---

## 4. Feature Engineering

### 4.1 AQI calculation

File: `src/features/calculate_aqi.py`

This script:

- uses official **EPA breakpoints** for each pollutant  
- applies the AQI formula for:
  - PM2.5, PM10, O₃, NO₂, SO₂, CO  
- takes the **maximum AQI** across all pollutants as the final AQI  
- adds a simple **category** (Good, Moderate, Unhealthy, etc.)  

The output is saved as `data/processed/aqi_data.csv`.

### 4.2 Extra features for modeling

File: `src/features/feature_engineering.py`

From the AQI data, it builds:

- **time features**
  - hour of day  
  - day of week  
  - month  
  - sine and cosine of hour  
- **lag features**
  - `aqi_lag_1` (AQI 1 hour ago)  
  - `aqi_lag_24` (AQI 24 hours ago)  
- **weather interactions**
  - temperature × humidity  
  - wind x and y components  

The final cleaned table is stored as `data/processed/processed_aqi.csv` and then uploaded to MongoDB.

---

## 5. Model Training

### 5.1 Training data

File: `src/pipeline/train_and_register_model.py`

Training uses the `aqi_features` collection in MongoDB.  
The script:

- reads all rows  
- drops the MongoDB `_id` column  
- splits data into **80% train** and **20% test** (no shuffle to keep time order)  

### 5.2 Models and metrics

Three models are trained:

- Random Forest Regressor  
- XGBoost Regressor  
- LightGBM Regressor  

Each model is evaluated on the test set with:

- **R²** – how much variance is explained  
- **RMSE** – root mean squared error  
- **MAE** – mean absolute error  

Example of model scores (from one run):

| Model         | R²    | RMSE  | MAE   |
|--------------|-------|-------|-------|
| RandomForest | 0.70  | 45.10 | 15.24 |
| XGBoost      | 0.70  | 45.26 | 15.69 |
| LightGBM     | 0.82  | 34.86 | 14.68 |

LightGBM is selected as the **best model**.

### 5.3 Model registry

The script saves:

- the best model file under `models/best_model_lightgbm.pkl`  
- a registry document in MongoDB (`model_registry` collection) that stores:

  - metrics for each model  
  - name of the best model  
  - path to the best model file  
  - training time and small flags (latest, baseline)  

The registry makes it easy for the prediction step and the dashboard to know which model to use.

---

## 6. Prediction Pipeline

File: `src/pipeline/predict_next_3_days.py`

This script:

1. Loads the **best model** from the registry.  
2. Reads the latest **24 hours** from `aqi_features`.  
3. Builds features for the next **72 hours** by:
   - moving the timestamp forward one hour at a time  
   - using average values from the recent data for pollutants and weather  
   - recomputing time features and lag features  
4. Runs the model to get **predicted AQI** for each future hour.  
5. Saves all 72 predictions into the `predictions` collection with:
   - forecast timestamp  
   - predicted AQI  
   - model name  
   - prediction date  

These predictions are what the Streamlit app reads.

---

## 7. Dashboard (Streamlit)

File: `app.py`

The Streamlit app is a simple front‑end on top of MongoDB.

It shows:

- **Current AQI**  
  - uses the first prediction as “current AQI”  
  - if predictions are missing, falls back to the latest measured value  

- **3‑day forecast chart**  
  - line chart with 72 hourly points  
  - colored bands for AQI zones  
  - small table with daily averages and min / max values  

- **Model snapshot**  
  - best model name (usually LIGHTGBM)  
  - latest R² score from the registry  

The page also includes short text like **“powered by Muhammad Talha”** so it is clearly branded.

Locally, extra buttons in the sidebar can:

- collect a fresh hour of data  
- force a new 3‑day forecast  

On Streamlit Cloud these buttons are hidden, because the GitHub Actions workflows already keep the data fresh.

---

## 8. Automation with GitHub Actions

Three workflows in `.github/workflows/` keep the system up to date.

### 8.1 Workflows table

| Workflow file               | Schedule              | Main job                                      |
|----------------------------|-----------------------|-----------------------------------------------|
| `hourly_data_collection`   | Every hour            | Run `collect_and_store_features.py`           |
| `daily_model_training`     | Every day at 02:00 UTC| Run `train_and_register_model.py`             |
| `daily_predictions`        | Every day at 03:00 UTC| Run `predict_next_3_days.py`                  |

Each job:

- checks out the repo  
- sets up Python 3.12  
- installs dependencies from `requirements.txt`  
- reads MongoDB settings from GitHub secrets  
- runs the correct pipeline script  

---

## 9. Deployment Details

### 9.1 MongoDB Atlas

- Free cluster on MongoDB Atlas.  
- Database name: for example `aqi_predictor`.  
- Collections:
  - `aqi_features` – hourly feature rows  
  - `model_registry` – model metadata and best model path  
  - `predictions` – 72‑hour forecast rows  

Connection details are stored in:

- `.env` for local runs  
- `st.secrets` on Streamlit Cloud  
- GitHub Actions secrets (`MONGODB_URI`, `MONGODB_DATABASE`)  

### 9.2 Streamlit Cloud

The app is deployed on Streamlit Cloud using the GitHub repository.

- Main file: `app.py`  
- Secrets:
  - `MONGODB_URI`  
  - `MONGODB_DATABASE`  
- Live URL at the time of writing:  
  `https://pearlairpredictor-iv38jgdt9fsg2lctbjm7q8.streamlit.app/`

---

## 10. How to Run the Project

Short summary for a new user:

1. Clone the repository.  
2. Create a virtual environment and install dependencies.  
3. Add the MongoDB URI and database name to `.env`.  
4. (Optional) Run the historical scripts to load one year of data.  
5. Run the training and prediction pipelines once.  
6. Start the Streamlit app with `streamlit run app.py`.  

After that, GitHub Actions and Streamlit Cloud can keep the system running without manual work.

---

## 11. Conclusion

This project shows a **complete AQI forecasting pipeline** that is still easy to understand.  
It connects data collection, feature engineering, model training, prediction and a web UI into one flow.

The design uses simple tools that are common in data science:

- Python and pandas for data work  
- well‑known tree‑based models for prediction  
- MongoDB Atlas for storage  
- Streamlit for the dashboard  
- GitHub Actions for automation  

Future work could include:

- supporting more cities  
- adding alerts for very bad AQI days  
- explaining predictions with tools like SHAP  
- trying deep learning models if needed  


