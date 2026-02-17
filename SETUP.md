## Pearls AQI Predictor – Complete Setup Guide

This guide explains how to set up and run **Pearls AQI Predictor** on **your own accounts and machine**, starting from a fresh clone.

You will:
- Run the project **locally** (pipelines + dashboard).
- Set up **MongoDB Atlas** as feature store + model registry.
- Configure **GitHub Actions** so the pipelines run automatically (serverless).
- (Optional) Deploy the dashboard to **Streamlit Cloud**.

---

### 1. Prerequisites

- **Python**: 3.12 (3.10+ should work, but 3.12 is used in CI).
- **GitHub account**: to host the repo and run GitHub Actions.
- **MongoDB Atlas account**: free tier is enough.
- **(Optional) Streamlit Cloud account**: for hosted dashboard.
- **OS**: Windows, macOS, or Linux with internet access.

---

### 2. Clone the Repository to Your Machine

If you don’t already have it locally:

```bash
git clone https://github.com/<your-username>/Pearls-AQI-Predictor.git
cd Pearls-AQI-Predictor
```

> If you cloned directly from your friend’s repo, you can keep that, or fork it into your own GitHub account first and then clone your fork.

---

### 3. Create a Python Virtual Environment

From the project root (`Pearls-AQI-Predictor`):

#### On Windows (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

#### On macOS / Linux

```bash
python -m venv .venv
source .venv/bin/activate
```

You should now see `(.venv)` or similar in your terminal prompt.

---

### 4. Install Python Dependencies

With the virtual environment active:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This installs all required packages: `pandas`, `numpy`, `scikit-learn`, `xgboost`, `lightgbm`, `pymongo`, `streamlit`, etc.

---

### 5. Set Up MongoDB Atlas (Feature Store + Model Registry)

MongoDB Atlas will store:
- Engineered features (`aqi_features` collection).
- Model registry (`model_registry` collection).
- 72‑hour predictions (`predictions` collection).

#### 5.1 Create a MongoDB Atlas Cluster

1. Go to [https://www.mongodb.com/atlas](https://www.mongodb.com/atlas) and sign in.
2. Create a **new project** (e.g., `PearlsAQI`).
3. Create a **free cluster** (e.g., `M0` tier, AWS/Azure/GCP, any region close to you).

#### 5.2 Create a Database User

1. In Atlas, go to **Database → Database Access**.
2. Click **Add New Database User**.
3. Choose:
   - Authentication: **Password**.
   - Username: e.g., `aqi_user`.
   - Password: a strong password (save it somewhere secure).
4. Give the user **Read and write to any database** (or at least to the `aqi_predictor` database).

#### 5.3 Allow Your IP

1. In Atlas, go to **Network Access**.
2. Click **Add IP Address**.
3. Option 1: Add your current IP.
4. Option 2: For development only, you can add `0.0.0.0/0` (allow from anywhere) – less secure, don’t use in production.

#### 5.4 Get the Connection String

1. In Atlas, go to **Database → Connect → Connect your application**.
2. Choose **Driver: Python**, Version: latest.
3. Copy the connection string, it looks like:

   ```text
   mongodb+srv://aqi_user:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
   ```

4. Replace `<password>` with the actual password of `aqi_user`.

You’ll use this in `.env` and GitHub Secrets.

---

### 6. Configure Local Environment Variables (`.env`)

In the project root, create a file named `.env` (or edit the existing one) with:

```env
MONGODB_URI=mongodb+srv://aqi_user:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
MONGODB_DATABASE=aqi_predictor
```

Notes:
- Replace the URI with your actual connection string.
- `MONGODB_DATABASE` can be any name (e.g., `aqi_predictor`); it will be created automatically when data is first stored.

The `MongoDB` helper in `src/database/mongo_db.py` will read these values.

---

### 7. (Optional but Recommended) Upload Historical Data Once

If `data/processed/processed_aqi.csv` exists (it should be in the repo), you can backfill one year of historical data into MongoDB.

With your virtual environment active and `.env` configured:

```bash
python src/pipeline/upload_historical_data.py
```

This will:
- Read the CSV.
- Insert all rows into the `aqi_features` collection in your MongoDB database.

You only need to do this **once** for your own cluster.

---

### 8. Run Pipelines Manually (Local Testing)

To confirm everything works end‑to‑end, run each pipeline once.

> Make sure your virtual environment is active and `.env` is correctly set.

#### 8.1 Collect One Hour of Fresh Data

```bash
python src/pipeline/collect_and_store_features.py
```

What it does:
- Calls OpenMeteo APIs for Islamabad (pollutants + weather).
- Calculates AQI, time features, lag features.
- Inserts **one new row** into `aqi_features` in MongoDB (if timestamp isn’t a duplicate).

#### 8.2 Train Models and Register Best Model

```bash
python src/pipeline/train_and_register_model.py
```

What it does:
- Reads all rows from `aqi_features`.
- Trains Random Forest, XGBoost, LightGBM.
- Evaluates each model (MAE, RMSE, R²).
- Saves best model to `models/best_model_<name>.pkl`.
- Inserts a record into `model_registry` collection (and maintains history).

#### 8.3 Generate 3‑Day (72‑Hour) Predictions

```bash
python src/pipeline/predict_next_3_days.py
``>

What it does:
- Loads the best model from `models/best_model_<name>.pkl` based on `model_registry`.
- Uses last 24 hours from `aqi_features` to build 72 future feature rows.
- Predicts AQI for each of the next 72 hours.
- Writes them to the `predictions` collection in MongoDB (clearing old ones first).

#### 8.4 (Optional) Inspect Predictions

```bash
python check_predictions.py
```

This script prints a summary of the stored predictions.

---

### 9. Run the Streamlit Dashboard Locally

From the project root, with the virtual environment active:

```bash
streamlit run app.py
```

Streamlit will print a local URL, typically:

```text
http://localhost:8501
```

Open that URL in your browser. The dashboard will:
- Show **Current AQI** (estimated from the first prediction or measured AQI).
- Show **3‑day forecast** as an interactive chart.
- Show **daily summary** (average / min / max).
- Show **model comparison** (Random Forest, XGBoost, LightGBM).

#### Sidebar Actions

In the left sidebar:
- **📡 Collect Fresh Data**:
  - Runs `src/pipeline/collect_and_store_features.py` locally via `subprocess`.
  - Inserts latest hour into `aqi_features`.
- **🔄 Regenerate Predictions**:
  - Runs `src/pipeline/predict_next_3_days.py` locally.
  - Refreshes the 72‑hour predictions in MongoDB.

---

### 10. Configure GitHub Actions (Serverless Automation)

To run the pipelines automatically on your own GitHub repo:

#### 10.1 Push the Code to Your GitHub Repository

If you cloned your friend’s repo directly and want your own remote:

```bash
git remote remove origin
git remote add origin https://github.com/<your-username>/Pearls-AQI-Predictor.git
git push -u origin main
```

Or simply fork your friend’s repo on GitHub and then clone your fork.

#### 10.2 Add GitHub Secrets

On your GitHub repository:

1. Go to **Settings → Secrets and variables → Actions**.
2. Click **New repository secret** for each:

   - `MONGODB_URI`  
     Value: same as in your local `.env`.

   - `MONGODB_DATABASE`  
     Value: `aqi_predictor` (or whatever DB name you use).

#### 10.3 Ensure Workflows are Enabled

The repo already includes these workflow files in `.github/workflows/`:

- `hourly_data_collection.yml`
- `daily_model_training.yml`
- `daily_predictions.yml`

By default, GitHub will:

- Run **hourly data collection**:
  - Cron: `0 * * * *`
  - Job: `python src/pipeline/collect_and_store_features.py`
- Run **daily model training**:
  - Cron: `0 2 * * *` (02:00 UTC)
  - Job: `python src/pipeline/train_and_register_model.py`
- Run **daily predictions**:
  - Cron: `0 3 * * *` (03:00 UTC)
  - Job: `python src/pipeline/predict_next_3_days.py`

You can also trigger each workflow manually from the **Actions** tab (using the “Run workflow” button).

> After these are running, your MongoDB feature store, model registry, and predictions will be updated automatically – no server for you to manage.

---

### 11. (Optional) Deploy the Dashboard to Streamlit Cloud

If you want a public dashboard without hosting anything yourself:

#### 11.1 Push Code to GitHub

Make sure the latest version of this repo is pushed to GitHub under your account.

#### 11.2 Create a Streamlit Cloud App

1. Go to [https://streamlit.io/cloud](https://streamlit.io/cloud) and log in with GitHub.
2. Click **New app**.
3. Select your repo and branch (e.g., `main`).
4. Set the **main file** to `app.py`.

#### 11.3 Configure Secrets in Streamlit Cloud

In the Streamlit app settings → **Secrets**:

```toml
MONGODB_URI = "mongodb+srv://aqi_user:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
MONGODB_DATABASE = "aqi_predictor"
```

The `MongoDB` helper will read from `st.secrets` when running in Streamlit Cloud.

Streamlit will then:
- Connect to your MongoDB Atlas cluster.
- Read from `aqi_features`, `model_registry`, `predictions`.
- Show the same dashboard you see locally – but hosted.

> Tip: For the “Collect Fresh Data” and “Regenerate Predictions” buttons, the pipelines are designed primarily for local execution. In production, rely on **GitHub Actions** to keep data and predictions fresh, and treat the cloud dashboard as **read‑only**.

---

### 12. Quick Checklist

- [ ] Python installed and virtual environment created.
- [ ] `pip install -r requirements.txt` completed.
- [ ] MongoDB Atlas cluster created and reachable.
- [ ] `.env` configured with `MONGODB_URI` and `MONGODB_DATABASE`.
- [ ] `upload_historical_data.py` run at least once (optional but recommended).
- [ ] `collect_and_store_features.py`, `train_and_register_model.py`, `predict_next_3_days.py` all run successfully.
- [ ] `streamlit run app.py` opens the dashboard locally.
- [ ] GitHub repository set up, with `MONGODB_URI` and `MONGODB_DATABASE` secrets.
- [ ] GitHub Actions workflows running on schedule.
- [ ] (Optional) Streamlit Cloud app connected to your repo and MongoDB.

Once all boxes are checked, the system is fully running on **your own assets** – your GitHub, your MongoDB, and your local or cloud dashboard. 🎯

