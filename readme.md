# Pearls AQI Predictor

Simple end‑to‑end project to **predict the Air Quality Index (AQI) for Islamabad for the next 3 days** using Python, machine learning, MongoDB and Streamlit.

---

## 🔗 Live demo

- **My deployed dashboard**  
  `https://pearlairpredictor-iv38jgdt9fsg2lctbjm7q8.streamlit.app/`

---

## 💡 What this project does

- Collects hourly air quality + weather data from **OpenMeteo**.
- Stores cleaned features in **MongoDB Atlas**.
- Trains 3 models (**Random Forest, XGBoost, LightGBM**) and picks the best one.
- Generates a **72‑hour AQI forecast** every day.
- Shows current AQI, forecast and model metrics on a **Streamlit dashboard**.

---

## 🧰 Tech stack

- **Language**: Python 3.12  
- **ML**: scikit‑learn, XGBoost, LightGBM  
- **Data**: pandas, numpy  
- **Database**: MongoDB Atlas  
- **UI**: Streamlit  
- **Automation**: GitHub Actions  

---

## 📁 Main structure

```text
Pearls-AQI-Predictor/
├── app.py                     # Streamlit dashboard
├── src/
│   ├── data/
│   │   └── data_collector.py  # Download historical raw data
│   ├── features/
│   │   ├── calculate_aqi.py   # Turn pollutants into AQI
│   │   └── feature_engineering.py
│   ├── database/
│   │   └── mongo_db.py        # MongoDB helper
│   ├── models/                # Offline experiments
│   └── pipeline/
│       ├── collect_and_store_features.py  # Hourly feature write to MongoDB
│       ├── train_and_register_model.py    # Daily training + model registry
│       ├── predict_next_3_days.py         # Daily 3‑day forecast
│       └── upload_historical_data.py      # One‑time bootstrap
├── .github/workflows/         # GitHub Actions (hourly + daily jobs)
├── data/                      # Local CSVs (for bootstrapping)
└── requirements.txt
```

---

## 🚀 Run it locally

1. **Clone and enter the project**

```bash
git clone https://github.com/<your-username>/Pearls-AQI-Predictor.git
cd Pearls-AQI-Predictor
```

2. **Create virtual environment and install packages**

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS / Linux

pip install -r requirements.txt
```

3. **Add MongoDB settings**

Create a `.env` file in the project root:

```env
MONGODB_URI=your_mongodb_connection_string
MONGODB_DATABASE=aqi_predictor
```

4. **(Optional but recommended) Load historical data once**

```bash
python src/data/data_collector.py          # fetch raw data from OpenMeteo
python src/features/calculate_aqi.py       # compute AQI values
python src/features/feature_engineering.py # make features
python src/pipeline/upload_historical_data.py
```

5. **Train model + create first forecast**

```bash
python src/pipeline/train_and_register_model.py
python src/pipeline/predict_next_3_days.py
```

6. **Start the dashboard**

```bash
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

---

## ⚙️ GitHub Actions (optional)

If you push this repo to GitHub and set up Actions:

1. Add repository secrets:

- `MONGODB_URI`
- `MONGODB_DATABASE` (for example `aqi_predictor`)

2. The workflows in `.github/workflows/` will then:

- Run **hourly** to collect new features.
- Run **daily** to retrain models and pick the best.
- Run **daily** to generate the next 72 hours of predictions.

---

## 👤 Author

Project customized and deployed by **Muhammad Talha**.  
Based on an internship project originally built at Pearls Organization.

---

## 📄 License

This project is released under the **MIT License**.

