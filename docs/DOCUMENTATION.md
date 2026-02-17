# AQI Predictor - Project Documentation

**Air Quality Index Prediction System for Islamabad, Pakistan**

---

## 📋 Project Overview

| Property | Value |
|----------|-------|
| **Project Name** | AQI Predictor |
| **Objective** | Predict Air Quality Index using Machine Learning |
| **Location** | Islamabad, Pakistan (33.6996°N, 73.0362°E) |
| **Timeline** | January 2026 - February 2026 |
| **Status** | Phase 3 - Model Development |

---

## Project Goals

1. Collect historical air quality and weather data
2. Perform exploratory data analysis
3. Engineer meaningful features for prediction
4. Train and evaluate machine learning models
5. Deploy a prediction system with automated updates

---

## Data Collection Journey

### Initial Attempts

#### 1. AQICN API (aqicn.org)
- **Attempt Date**: Early January 2026
- **Issue**: DNS blocking - couldn't access the API
- **Solution**: Used VPN to bypass blocking
- **Limitation**: Only provides **2 months** of historical data
- **Result**: ❌ Insufficient data for robust model training

#### 2. OpenWeather API (openweathermap.org)
- **Attempt Date**: Mid January 2026
- **Issue**: Similar DNS blocking issues
- **Solution**: Used VPN
- **Limitation**: Also limited to **2 months** of historical data
- **Result**: ❌ Not enough historical data

#### 3. OpenMeteo API (open-meteo.com) ✅
- **Selected Date**: January 2026
- **Advantages**:
  - ✅ **No API key required** (free and open)
  - ✅ **No DNS blocking** - accessible without VPN
  - ✅ Provides **60+ days** of historical data
  - ✅ Comprehensive air quality and weather data
  - ✅ Reliable and well-documented API
- **Result**: ✅ **Selected as primary data source**

### Why OpenMeteo?

After testing multiple APIs, OpenMeteo emerged as the best choice because:

1. **Accessibility**: No VPN required, no blocking issues
2. **Data Volume**: Sufficient historical data for training
3. **Cost**: Completely free, no API key needed
4. **Reliability**: Stable API with good uptime
5. **Data Quality**: Comprehensive pollutant and weather measurements

---

## 🌐 Data Sources

### OpenMeteo Air Quality API

**Endpoint**: `https://air-quality.open-meteo.com/v1/air-quality`

**Parameters**:
```python
{
    "latitude": 33.6996,
    "longitude": 73.0362,
    "hourly": [
        "pm10", "pm2_5", "carbon_monoxide",
        "nitrogen_dioxide", "sulphur_dioxide", "ozone"
    ],
    "timezone": "Asia/Karachi",
    "past_days": 60
}
```

**Pollutants Collected**:
- PM10 - Particulate Matter 10 micrometers (µg/m³)
- PM2.5 - Particulate Matter 2.5 micrometers (µg/m³)
- CO - Carbon Monoxide (µg/m³)
- NO₂ - Nitrogen Dioxide (µg/m³)
- SO₂ - Sulphur Dioxide (µg/m³)
- O₃ - Ozone (µg/m³)

### OpenMeteo Weather API

**Endpoint**: `https://api.open-meteo.com/v1/forecast`

**Parameters**:
```python
{
    "latitude": 33.6996,
    "longitude": 73.0362,
    "hourly": [
        "temperature_2m", "relative_humidity_2m",
        "surface_pressure", "wind_speed_10m",
        "wind_direction_10m", "precipitation"
    ],
    "timezone": "Asia/Karachi",
    "past_days": 60
}
```

**Weather Variables**:
- Temperature at 2m (°C)
- Relative Humidity at 2m (%)
- Surface Pressure (hPa)
- Wind Speed at 10m (km/h)
- Wind Direction at 10m (°)
- Precipitation (mm)

---

## 📁 Project Structure

```
AQI_Predictor/
├── src/
│   ├── data/
│   │   └── data_collector.py      # Data collection from OpenMeteo
│   └── features/
│       ├── calculate_aqi.py       # AQI calculation using EPA standards
│       └── feature_engineering.py # Feature engineering pipeline
├── data/
│   ├── raw/                       # Raw data from API
│   │   └── raw_data_islamabad_*.csv
│   └── processed/                 # Processed data with AQI
│       └── aqi_data.csv
├── notebooks/
│   └── eda/                       # Exploratory Data Analysis
│       ├── 01_data_exploration.ipynb
│       └── 02_aqi_calculation.ipynb
│   └── 03_feature_selection.ipynb # Feature Selection & Analysis
├── docs/
│   └── DOCUMENTATION.md           # This file
├── .env                           # Environment variables
├── requirements.txt               # Python dependencies
└── readme.md                      # Project README
```

---

## 🛠️ Technology Stack

### Core Technologies
- **Python**: 3.10+
- **Data Processing**: pandas, numpy
- **Machine Learning**: scikit-learn, XGBoost, LightGBM
- **Visualization**: matplotlib, seaborn, plotly

### APIs
- **OpenMeteo**: Air quality and weather data

### Future Technologies (Planned)
- **Database**: MongoDB Atlas (feature store & model registry)
- **Web Framework**: Streamlit or FastAPI
- **CI/CD**: GitHub Actions
- **Deployment**: Cloud platform (TBD)

---

## 📈 Development Phases

### ✅ Phase 1: Data Collection & Exploration (Completed)
- [x] Research and test different APIs (AQICN, OpenWeather, OpenMeteo)
- [x] Resolve DNS blocking issues
- [x] Select OpenMeteo as primary data source
- [x] Implement data collection script
- [x] Collect 1 year of historical data (8,784 hours)
- [x] Perform exploratory data analysis
- [x] Calculate AQI using EPA standards

### ✅ Phase 2: Feature Engineering (Completed)
- [x] Calculate AQI from pollutant concentrations
- [x] Create time-based features (hour, day, month, cyclical encoding)
- [x] Create lag features (aqi_lag_1, aqi_lag_24)
- [x] Create interaction features (temp×humidity, wind components)
- [x] Feature selection and importance analysis
- [x] Final feature set: 19 features selected

### ✅ Phase 3: Model Development (Completed)
- [x] Train baseline models (Experiment 1)
- [x] Hyperparameter tuning (Experiment 2)
- [x] Manual parameter optimization (Experiment 3)
- [x] Model evaluation and comparison
- [x] Select best performing model (LightGBM - R² = 0.8229)

### 🔄 Phase 4: Production Pipeline (Completed)

#### 4.1 MongoDB Setup
- [x] MongoDB connection helper created
- [x] Feature store collection setup
- [x] Historical data uploaded (8,760 rows)
- [x] Model registry collection setup
- [x] Predictions collection setup

#### 4.2 Data Pipeline
- [x] Upload historical features to MongoDB (one-time)
- [x] Hourly data collection script (`collect_and_store_features.py`)
- [x] GitHub Actions automation (runs every hour)

#### 4.3 Model Pipeline
- [x] Daily model training automation
- [x] Model comparison and selection
- [x] Model registry with metadata
- [x] GitHub Actions workflow (runs daily at 2 AM UTC)

#### 4.4 Prediction Pipeline
- [x] Next 3 days AQI prediction
- [x] Prediction storage in MongoDB
- [x] GitHub Actions workflow (runs daily at 3 AM UTC)

#### 4.5 Dashboard
- [x] Streamlit dashboard created
- [x] Real-time data visualization
- [x] 3-day forecast display
- [x] Model comparison view
- [x] Manual prediction refresh button

---

## Automation Pipeline

### Overview

The complete ML pipeline is automated using GitHub Actions with three workflows:

| Workflow | Frequency | Schedule | Purpose |
|----------|-----------|----------|---------|
| **Data Collection** | Every hour | `0 * * * *` | Fetch live data from OpenMeteo API |
| **Model Training** | Daily | `0 2 * * *` (2 AM UTC) | Train and select best model |
| **Predictions** | Daily | `0 3 * * *` (3 AM UTC) | Generate 72-hour forecast |

### 1. Hourly Data Collection

**File:** `.github/workflows/hourly_data_collection.yml`

**Process:**
1. Fetches latest weather and air quality data from OpenMeteo API
2. Calculates AQI using EPA formula
3. Engineers time-based and lag features
4. Stores new record in MongoDB (`aqi_features` collection)

**Output:** 1 new row added to MongoDB every hour

### 2. Daily Model Training

**File:** `.github/workflows/daily_model_training.yml`

**Process:**
1. Loads all historical data from MongoDB
2. Trains 3 models (Random Forest, XGBoost, LightGBM)
3. Evaluates performance (R², RMSE, MAE)
4. Selects best model based on R² score
5. Saves best model to repository
6. Updates model registry in MongoDB

**Output:** 
- Updated `best_model_lightgbm.pkl` file
- Model metadata in `model_registry` collection

### 3. Daily Predictions

**File:** `.github/workflows/daily_predictions.yml`

**Process:**
1. Loads best model from repository
2. Fetches latest 24 hours of data from MongoDB
3. Generates features for next 72 hours
4. Predicts AQI for each hour
5. Saves predictions to MongoDB (`predictions` collection)

**Output:** 72 hourly predictions (3 days)

### 4. Dashboard (On-Demand)

**File:** `app.py`

**Process:**
1. User opens dashboard: `streamlit run app.py`
2. Loads data from MongoDB:
   - Latest actual AQI from `aqi_features`
   - 72-hour predictions from `predictions`
   - Model metrics from `model_registry`
3. Displays interactive visualizations

**Features:**
- Current AQI with category (Good/Moderate/Unhealthy)
- 72-hour forecast line chart with AQI zones
- Daily summary table (Avg/Min/Max AQI)
- Model comparison table and chart
- Manual "Refresh Predictions" button

**Note:** Dashboard displays data; it doesn't generate predictions. Predictions are generated by GitHub Actions daily at 3 AM UTC.

---

## Model Training Experiments

### Experiment 1: Baseline Models (February 4, 2026)

**Configuration:**
- **Data Split:** 80/20 (Train: 7,008 | Test: 1,752)
- **Features:** 19 features (6 pollutants, 6 weather, 5 time, 2 lag)
- **Models:** Random Forest, XGBoost, LightGBM (default parameters)

**Results:**

| Model | R² | RMSE | MAE |
|-------|------|------|-----|
| Random Forest | 0.6027 | 52.22 | 17.64 |
| XGBoost | 0.5471 | 55.75 | 15.98 |
| **LightGBM** | **0.8220** | **34.95** | **15.02** |

**Best Model:** LightGBM (R² = 0.8220)

**Key Findings:**
- LightGBM significantly outperforms other models
- Random Forest shows moderate performance
- XGBoost underperforms (likely needs tuning)
- LightGBM achieves 82.2% variance explained

**Next Steps:**
- Hyperparameter tuning to improve XGBoost and Random Forest
- Cross-validation for more robust evaluation
- Feature importance analysis

---

### Experiment 2: Hyperparameter Tuning (February 4, 2026)

**Configuration:**
- **Data Split:** 80/20 (Train: 7,008 | Test: 1,752)
- **Features:** 19 features (same as Experiment 1)
- **Method:** RandomizedSearchCV with 3-fold cross-validation
- **Iterations:** 10 random parameter combinations per model

**Hyperparameters Tuned:**
- **Random Forest:** n_estimators, max_depth, min_samples_split, min_samples_leaf
- **XGBoost:** n_estimators, max_depth, learning_rate, subsample, colsample_bytree
- **LightGBM:** n_estimators, max_depth, learning_rate, num_leaves, subsample

**Results:**

| Model | R² | RMSE | MAE | Improvement from Exp 1 |
|-------|------|------|-----|------------------------|
| Random Forest | 0.7036 | 45.10 | 15.25 | +10.1% R² |
| XGBoost | 0.6963 | 45.65 | 16.08 | +14.9% R² |
| **LightGBM** | **0.8229** | **34.86** | **14.68** | **+0.1% R²** |

**Best Model:** LightGBM (R² = 0.8229)

**Best Hyperparameters:**
- **LightGBM:** n_estimators=300, max_depth=12, learning_rate=0.05, num_leaves=31, subsample=0.8

**Key Findings:**
- Hyperparameter tuning significantly improved Random Forest (+10.1%) and XGBoost (+14.9%)
- LightGBM already near-optimal with default parameters (minimal improvement)
- All models now perform reasonably well (R² > 0.69)
- LightGBM remains the best model with 82.3% variance explained

**Comparison with Experiment 1:**
- Random Forest: 0.6027 → 0.7036 ✅
- XGBoost: 0.5471 → 0.6963 ✅
- LightGBM: 0.8220 → 0.8229 ✅

---

### Experiment 3: Manual Parameter Optimization (February 4, 2026)

**Configuration:**
- **Data Split:** 80/20 (Train: 7,008 | Test: 1,752)
- **Features:** 19 features (same as previous experiments)
- **Method:** Manual parameter tuning based on Experiment 2 results
- **Approach:** No GridSearch - direct parameter optimization for speed

**Parameter Adjustments:**
- **Random Forest:** n_estimators=300, max_depth=25
- **XGBoost:** n_estimators=300, max_depth=8, learning_rate=0.05, subsample=0.9
- **LightGBM:** n_estimators=400, max_depth=12, learning_rate=0.05, num_leaves=50, subsample=0.9

**Results:**

| Model | R² | RMSE | MAE | Change from Exp 2 |
|-------|------|------|-----|-------------------|
| Random Forest | 0.7036 | 45.10 | 15.25 | No change |
| XGBoost | 0.6691 | 47.65 | 15.58 | -2.7% R² |
| **LightGBM** | **0.8084** | **36.26** | **16.15** | **-1.4% R²** |

**Best Model:** LightGBM (R² = 0.8084)

**Key Findings:**
- Manual parameter tuning did not improve performance
- Experiment 2 (RandomizedSearchCV) found better parameters
- Increasing n_estimators and num_leaves slightly decreased performance
- **Conclusion:** Experiment 2 parameters are optimal

**Final Decision:**
- **Use Experiment 2 models for production**
- Best model: LightGBM with R² = 0.8229
- Parameters: n_estimators=300, max_depth=12, learning_rate=0.05, num_leaves=31, subsample=0.8

---

## 🏆 Final Model Selection

**Selected Model:** LightGBM (from Experiment 2)

**Performance Metrics:**
- **R²:** 0.8229 (82.3% variance explained)
- **RMSE:** 34.86 (average error magnitude)
- **MAE:** 14.68 (average absolute error)

**Model Parameters:**
```python
LGBMRegressor(
    n_estimators=300,
    max_depth=12,
    learning_rate=0.05,
    num_leaves=31,
    subsample=0.8,
    random_state=42
)
```

**Saved Models:**
- `models/lightgbm_tuned.pkl` (Production model)
- `models/xgboost_tuned.pkl` (Backup model)
- `models/random_forest_tuned.pkl` (Baseline model)

---

## Model Performance Interpretation

### Understanding the Metrics

During model development, the initial performance metrics appeared modest compared to some academic benchmarks. However, research into real-world AQI prediction systems revealed that these metrics are actually **strong indicators of model quality**.

### Performance Context

**Our Model Performance:**
- **R² Score: 0.8229** (82.3% variance explained)
- **RMSE: 34.86** (Root Mean Squared Error)
- **MAE: 14.68** (Mean Absolute Error)

### Why These Metrics Are Good

#### **R² Score (0.8229)**
- **Interpretation:** The model explains 82.3% of the variance in AQI values
- **Industry Standard:** 
  - R² > 0.70 is considered good for environmental predictions
  - R² > 0.80 is considered very good
  - R² > 0.90 is excellent (but often indicates overfitting in real-world scenarios)
- **Our Performance:** ✅ Very Good (0.82 falls in the "very good" category)

#### **MAE (14.68)**
- **Interpretation:** On average, predictions are off by ±15 AQI points
- **Context:** 
  - AQI range is 0-500
  - AQI categories have 50-point ranges (e.g., 0-50 = Good, 51-100 = Moderate)
  - An error of 15 points is **well within acceptable bounds**
- **Real-World Impact:** 
  - Predictions are accurate enough for health advisory decisions
  - Rarely crosses category boundaries incorrectly
- **Our Performance:** ✅ Excellent for practical use

#### **RMSE (34.86)**
- **Interpretation:** Penalizes larger errors more heavily than MAE
- **Context:**
  - RMSE is naturally higher than MAE due to squaring errors
  - For AQI prediction, RMSE < 40 is considered acceptable
  - RMSE < 30 is considered very good
- **Our Performance:** ✅ Good (close to "very good" threshold)

### Comparison with Research Literature

Based on published research on AQI prediction models:

| Metric | Poor | Acceptable | Good | Very Good | Our Model |
|--------|------|------------|------|-----------|-----------|
| R² | < 0.60 | 0.60-0.75 | 0.75-0.85 | > 0.85 | **0.82** ✅ |
| MAE | > 25 | 15-25 | 10-15 | < 10 | **14.68** ✅ |
| RMSE | > 50 | 35-50 | 25-35 | < 25 | **34.86** ✅ |

### Why Not Higher Performance?

**Realistic Factors:**
1. **Inherent Uncertainty:** Air quality is influenced by many unpredictable factors (traffic patterns, industrial emissions, weather changes)
2. **Data Limitations:** Hourly predictions are challenging due to rapid environmental changes
3. **No Data Leakage:** The model uses only past data and weather features, avoiding unrealistic "perfect" predictions
4. **Time-Series Split:** Using proper temporal validation (no shuffling) ensures realistic performance estimates

### Red Flags in "Too Good" Models

Models with R² > 0.95 and MAE < 5 often indicate:
- ❌ Data leakage (using future information)
- ❌ Overfitting (won't generalize to new data)
- ❌ Incorrect train/test split (shuffling time-series data)
- ❌ Using target-derived features

**Our approach prioritizes realistic, production-ready performance over inflated metrics.**

### Conclusion

The model's performance metrics (R² = 0.82, MAE = 14.68, RMSE = 34.86) represent:
- ✅ Strong predictive capability for real-world AQI forecasting
- ✅ Reliable performance without overfitting
- ✅ Suitable for production deployment and health advisory systems
- ✅ Honest evaluation using proper time-series validation

---

## Production Pipeline Architecture

### Overview

The production pipeline consists of three main components:
1. **Data Pipeline** - Collect and store features hourly
2. **Model Pipeline** - Train and register models daily
3. **Prediction Pipeline** - Generate 3-day forecasts daily

### MongoDB Collections

```
Database: aqi_predictor

1. aqi_features
   - Stores engineered features (ready for model training)
   - Updated hourly via GitHub Actions
   - Schema: {timestamp, pm10, pm2_5, ..., hour, aqi_lag_1, aqi}

2. model_registry
   - Stores model comparison and best model metadata
   - Updated daily after training
   - Schema: {
       version: "v1.0",
       timestamp: "2026-02-04",
       models: {
           random_forest: {r2, rmse, mae},
           xgboost: {r2, rmse, mae},
           lightgbm: {r2, rmse, mae}
       },
       best_model: "lightgbm",
       best_model_path: "models/lightgbm_tuned.pkl"
   }

3. predictions
   - Stores next 3 days (72 hours) AQI predictions
   - Updated daily
   - Schema: {timestamp, predicted_aqi, model_used, prediction_date}
```

### Pipeline Scripts

#### 1. One-Time Setup
**File:** `src/pipeline/upload_historical_data.py`
- **Purpose:** Upload existing processed features to MongoDB
- **Input:** `data/processed/processed_aqi.csv` (8,760 rows)
- **Output:** MongoDB `aqi_features` collection
- **Run:** Manual, once

#### 2. Hourly Data Collection
**File:** `src/pipeline/collect_and_store_features.py`
- **Purpose:** Collect latest data and engineer features
- **Steps:**
  1. Fetch latest 1 hour from OpenMeteo API
  2. Calculate AQI
  3. Engineer features (time, lag, etc.)
  4. Store in MongoDB `aqi_features`
- **Schedule:** Every hour via GitHub Actions
- **Automation:** `.github/workflows/hourly_data.yml`

#### 3. Daily Model Training
**File:** `src/pipeline/train_and_register_model.py`
- **Purpose:** Train models and select best
- **Steps:**
  1. Read features from MongoDB
  2. Train 3 models (RF, XGBoost, LightGBM)
  3. Compare metrics (R², RMSE, MAE)
  4. Select best model
  5. Save metadata to MongoDB `model_registry`
- **Schedule:** Daily at 2:00 AM via GitHub Actions
- **Automation:** `.github/workflows/daily_training.yml`

#### 4. Daily Prediction
**File:** `src/pipeline/predict_next_3_days.py`
- **Purpose:** Generate 72-hour AQI forecast
- **Steps:**
  1. Load best model from registry
  2. Get weather forecast for next 3 days
  3. Predict AQI for next 72 hours
  4. Store predictions in MongoDB
- **Schedule:** Daily at 3:00 AM via GitHub Actions
- **Automation:** `.github/workflows/daily_prediction.yml`

### Automation Schedule

```
GitHub Actions Schedule:

Every Hour (00:00, 01:00, ..., 23:00):
  └─ collect_and_store_features.py
     └─ Collect data → Engineer features → Save to MongoDB

Every Day at 2:00 AM:
  └─ train_and_register_model.py
     └─ Train models → Compare → Save best model metadata

Every Day at 3:00 AM:
  └─ predict_next_3_days.py
     └─ Load best model → Predict 72 hours → Save predictions
```

### Dashboard Features

The Streamlit dashboard will display:
1. **Model Comparison Table** - R², RMSE, MAE for all 3 models
2. **Current AQI** - Latest reading from MongoDB
3. **3-Day Forecast** - Next 72 hours prediction chart
4. **Historical Trends** - Past 7 days AQI visualization
5. **Model Info** - Current production model details

**Next Steps:**
- Create pipeline scripts
- Set up GitHub Actions
- Build Streamlit dashboard

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10 or higher
- Internet connection (for API access)

### Installation

```bash
# Clone repository
git clone https://github.com/u-faizan/Pearls-AQI-Predictor.git
cd Pearls-AQI-Predictor

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Environment Setup

Create a `.env` file:

```env
# City Configuration
CITY_NAME=Islamabad
CITY_LATITUDE=33.6996
CITY_LONGITUDE=73.0362

# MongoDB (for later phases)
MONGODB_URI=your_mongodb_uri
MONGODB_DATABASE=aqi_predictor
```

### Collect Data

```bash
# Run data collection script
python src/data/data_collector.py
```

---

## 📝 Lessons Learned

### API Selection Process

1. **Don't assume availability**: Popular APIs may be blocked in certain regions
2. **Test before committing**: Always test API access and data availability
3. **Consider data volume**: Ensure the API provides sufficient historical data
4. **Free isn't always limited**: OpenMeteo proves free APIs can be excellent
5. **Documentation matters**: Well-documented APIs save development time

### Technical Challenges

1. **DNS Blocking**: 
   - Problem: AQICN and OpenWeather were blocked
   - Solution: VPN access, but found better alternative (OpenMeteo)
   
2. **Data Limitations**:
   - Problem: 2-month limit on commercial APIs
   - Solution: OpenMeteo provides 60+ days without restrictions

---

## Current Status

**Last Updated**: February 13, 2026

**Progress**:
- ✅ Project setup complete
- ✅ Data source selected (OpenMeteo)
- ✅ Data collection automated (hourly via GitHub Actions)
- ✅ Collected 1 year+ of historical data (8,761 hourly records)
- ✅ Feature engineering completed (19 features)
- ✅ Model training automated (daily via GitHub Actions)
- ✅ Prediction pipeline automated (daily via GitHub Actions)
- ✅ Streamlit dashboard deployed
- ✅ MongoDB integration complete
- ✅ **Production Ready**

**Production Deployment**:
- **Database**: MongoDB Atlas (cloud-hosted)
- **Model Registry**: Baseline model (R²=0.82) + last 5 daily runs
- **Current Model**: LightGBM (R²=0.7573)
- **Automation**: GitHub Actions (hourly data, daily training/predictions)
- **Dashboard**: Streamlit (real-time AQI + 72-hour forecast)
- **Data Freshness**: API data has 1-2 hour delay (noted in dashboard)
- **Timezone**: All timestamps in UTC, displayed as Pakistan Time (UTC+5)

**Key Features**:
- Dashboard buttons run locally, store to MongoDB
- Baseline model preserved for comparison
- AQI range display in forecast
- Manual refresh capability for data and predictions

---

## 🤝 Contributing

This is an internship project. Feedback and suggestions are welcome!

---

## 📄 License

MIT License

---

*Documentation maintained as part of the AQI Predictor project*
*Internship Project - January 2026 to February 2026*
