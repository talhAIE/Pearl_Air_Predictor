# Pearls AQI Predictor

**Automated Air Quality Index (AQI) prediction system for Islamabad, Pakistan**

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![ML](https://img.shields.io/badge/ML-LightGBM-green.svg)](https://lightgbm.readthedocs.io/)
[![MongoDB](https://img.shields.io/badge/Database-MongoDB-green.svg)](https://www.mongodb.com/)
[![Streamlit](https://img.shields.io/badge/Dashboard-Streamlit-red.svg)](https://streamlit.io/)

🌐 **[Live Dashboard](https://pearl-aqi-predictor.streamlit.app/)** - View real-time AQI predictions

## Project Overview

A complete end-to-end machine learning pipeline that:
- Collects live air quality data every hour
- Trains ML models daily to predict AQI
- Generates 72-hour forecasts automatically
- Displays predictions on an interactive dashboard

| Property | Value |
|----------|-------|
| **Location** | Islamabad, Pakistan (33.6844°N, 73.0479°E) |
| **Best Model** | LightGBM (R² = 0.8229) |
| **Prediction Horizon** | 72 hours (3 days) |
| **Data Frequency** | Hourly updates |
| **Status** | Production Ready |

---

## Features

### Automated ML Pipeline
- **Hourly Data Collection**: Fetches live weather and air quality data from OpenMeteo API
- **Daily Model Training**: Trains and compares 3 models (Random Forest, XGBoost, LightGBM)
- **Daily Predictions**: Generates 72-hour AQI forecasts
- **All automated with GitHub Actions** - No manual intervention required

### Interactive Dashboard
- Real-time current AQI with health category
- 3-day forecast visualization with AQI zones
- Model performance comparison
- Daily summary statistics
- Manual prediction refresh option

### Model Performance
- **Current Model**: LightGBM (R² = 0.7573)
- **Baseline Model**: LightGBM (R² = 0.82) - Preserved for comparison
- **RMSE**: 26.3
- **MAE**: 20.5
- **Training Data**: 8,761 hours (1 year + daily updates)
- **Features**: 19 engineered features
- **Model Registry**: Keeps baseline + last 5 daily training runs

---

## Data Pipeline

### Automation Schedule

| Component | Frequency | Time (UTC) | Purpose |
|-----------|-----------|------------|---------|
| **Data Collection** | Every hour | `0 * * * *` | Fetch live data |
| **Model Training** | Daily | `0 2 * * *` (2 AM) | Retrain models |
| **Predictions** | Daily | `0 3 * * *` (3 AM) | Generate forecast |

### Data Sources
- **Air Quality**: OpenMeteo Air Quality API (PM2.5, PM10, O₃, NO₂, SO₂, CO)
- **Weather**: OpenMeteo Weather API (Temperature, Humidity, Wind, Precipitation)
- **Storage**: MongoDB Atlas (Cloud database)

**Note:** OpenMeteo API data typically has a 1-2 hour delay. The dashboard displays model predictions as "Current AQI" for better accuracy and real-time estimates.

---

## Tech Stack

### Core Technologies
- **Language**: Python 3.12
- **ML Libraries**: scikit-learn, XGBoost, LightGBM
- **Data Processing**: pandas, numpy
- **Database**: MongoDB Atlas
- **Dashboard**: Streamlit
- **Automation**: GitHub Actions
- **Visualization**: Plotly

### Project Structure
```
AQI_Predictor/
├── .github/workflows/          # GitHub Actions automation
│   ├── hourly_data_collection.yml
│   ├── daily_model_training.yml
│   └── daily_predictions.yml
├── src/
│   ├── data/
│   │   └── data_collector.py   # Historical data collection
│   ├── database/
│   │   └── mongo_db.py         # MongoDB connection
│   ├── features/
│   │   ├── calculate_aqi.py    # AQI calculation
│   │   └── feature_engineering.py
│   ├── models/
│   │   ├── train.py            # Model training scripts
│   │   └── EXPERIMENTS_SUMMARY.md
│   └── pipeline/
│       ├── collect_and_store_features.py  # Hourly collection
│       ├── train_and_register_model.py    # Daily training
│       ├── predict_next_3_days.py         # Daily predictions
│       └── upload_historical_data.py      # One-time setup
├── models/
│   ├── best_model_lightgbm.pkl # Production model
│   └── BEST_MODEL.txt          # Model info
├── data/
│   └── processed/
│       └── processed_aqi.csv   # Historical data (8,760 rows)
├── notebooks/                  # Jupyter notebooks for EDA
├── docs/
│   └── DOCUMENTATION.md        # Complete documentation
├── app.py                      # Streamlit dashboard
└── requirements.txt
```

---

## Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/u-faizan/Pearls-AQI-Predictor.git
cd Pearls-AQI-Predictor
```

### 2. Setup Environment
```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure MongoDB
Create a `.env` file:
```env
MONGODB_URI=your_mongodb_connection_string
MONGODB_DATABASE=aqi_predictor
```

### 4. Upload Historical Data (One-time)
```bash
python src/pipeline/upload_historical_data.py
```

### 5. Run Dashboard
```bash
streamlit run app.py
```

The dashboard will open at `http://localhost:8501`

---

## Model Development

### Training Experiments

**Experiment 1: Baseline Models**
- Random Forest: R² = 0.6027
- XGBoost: R² = 0.5471
- LightGBM: R² = 0.8220 (Selected)

**Experiment 2: Hyperparameter Tuning**
- Used RandomizedSearchCV
- LightGBM: R² = 0.8229 (Improved)

**Experiment 3: Manual Optimization**
- Fine-tuned LightGBM parameters
- Final production model

See [EXPERIMENTS_SUMMARY.md](src/models/EXPERIMENTS_SUMMARY.md) for details.

### Features (19 total)
- **Pollutants (6)**: PM10, PM2.5, CO, NO₂, SO₂, O₃
- **Weather (6)**: Temperature, Humidity, Wind Speed/Direction, Precipitation, Cloud Cover
- **Time (5)**: Hour, Day of Week, Month, Hour Sin/Cos
- **Lag (2)**: AQI 1-hour ago, AQI 24-hours ago

---

## GitHub Actions Setup

### Prerequisites
1. MongoDB Atlas account (free tier works)
2. GitHub repository

### Setup Secrets
Go to: `Settings → Secrets and variables → Actions`

Add these secrets:
- `MONGODB_URI`: Your MongoDB connection string
- `MONGODB_DATABASE`: `aqi_predictor`

### Workflows
All workflows are in `.github/workflows/` and run automatically.

---

## Dashboard Features

### Current AQI Display
- **Current AQI (Estimated)**: Shows the first prediction value for most accurate real-time estimate
- **Fallback**: Uses latest measured data if predictions unavailable
- Health category (Good/Moderate/Unhealthy/etc.)
- Location and model information
- *Note: Predictions used due to 1-2 hour API data delay*

### 3-Day Forecast
- Interactive line chart with 72 hourly predictions
- Color-coded AQI zones (Good/Moderate/Unhealthy)
- Daily summary table (Average, Min, Max AQI)

### Model Comparison
- Performance metrics for all 3 models
- Highlighted best model
- Visual comparison chart

---

## Documentation

- **[Complete Documentation](docs/DOCUMENTATION.md)** - Full project details
- **[Experiments Summary](src/models/EXPERIMENTS_SUMMARY.md)** - Model training results
- **[Best Model Info](models/BEST_MODEL.txt)** - Production model details

---

## Future Enhancements

- Deploy dashboard to Streamlit Cloud
- Add email alerts for unhealthy AQI levels
- Implement ensemble models
- Add more cities
- Create REST API for predictions

---

## Contributing

This is an internship project. Feedback and suggestions are welcome.

---

## License

MIT License

---

## Author

**Faizan**  
Data Science Intern | Pearls Organization  
*January 2026 - February 2026*

---

## Acknowledgments

- **OpenMeteo** for free weather and air quality data
- **MongoDB Atlas** for cloud database hosting
- **GitHub Actions** for free CI/CD automation
- **Streamlit** for easy dashboard creation

---

**Star this repo if you find it useful!**
