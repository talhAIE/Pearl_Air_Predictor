"""
AQI Predictor Dashboard
Simple Streamlit dashboard showing current AQI and 3-day forecast
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
from pathlib import Path
import subprocess

# Add parent directory to path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.database.mongo_db import MongoDB


# Page config
st.set_page_config(
    page_title="AQI Predictor",
    page_icon="🌍",
    layout="wide"
)

# Simple flag: on Streamlit Cloud we expect MONGODB_URI to be in st.secrets,
# while local runs typically use .env instead.
RUNNING_IN_CLOUD = "MONGODB_URI" in st.secrets


def get_aqi_category(aqi):
    """Get AQI category and color."""
    if aqi <= 50:
        return "Good", "#00E400"
    elif aqi <= 100:
        return "Moderate", "#FFFF00"
    elif aqi <= 150:
        return "Unhealthy for Sensitive Groups", "#FF7E00"
    elif aqi <= 200:
        return "Unhealthy", "#FF0000"
    elif aqi <= 300:
        return "Very Unhealthy", "#8F3F97"
    else:
        return "Hazardous", "#7E0023"


def refresh_predictions():
    """Run prediction pipeline to generate fresh predictions."""
    try:
        with st.spinner("Generating fresh predictions... This may take a minute."):
            result = subprocess.run(
                ["python", "src/pipeline/predict_next_3_days.py"],
                capture_output=True,
                text=True,
                timeout=120
            )
            if result.returncode == 0:
                st.success("✅ Predictions updated successfully!")
                st.rerun()
            else:
                st.error(f"❌ Error: {result.stderr}")
    except subprocess.TimeoutExpired:
        st.error("❌ Prediction timed out. Please try again.")
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")


def collect_fresh_data():
    """Run data collection pipeline to fetch latest AQI data."""
    try:
        with st.spinner("Collecting fresh AQI data from API... This may take a moment."):
            result = subprocess.run(
                ["python", "src/pipeline/collect_and_store_features.py"],
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode == 0:
                st.success("✅ Fresh data collected successfully!")
                st.rerun()
            else:
                st.error(f"❌ Error: {result.stderr}")
    except subprocess.TimeoutExpired:
        st.error("❌ Data collection timed out. Please try again.")
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")



def load_model_registry():
    """Load model comparison from MongoDB."""
    mongo = MongoDB()
    mongo.connect()
    
    collection = mongo.get_collection("model_registry")
    registry = collection.find_one()
    
    mongo.close()
    
    return registry


def load_predictions():
    """Load 3-day predictions from MongoDB."""
    mongo = MongoDB()
    mongo.connect()
    
    collection = mongo.get_collection("predictions")
    predictions = list(collection.find())
    
    mongo.close()
    
    df = pd.DataFrame(predictions)
    if not df.empty:
        df = df.drop('_id', axis=1)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    return df


def load_latest_aqi():
    """Load latest actual AQI from features."""
    mongo = MongoDB()
    mongo.connect()
    
    collection = mongo.get_collection("aqi_features")
    latest = collection.find_one(sort=[("timestamp", -1)])
    
    mongo.close()
    
    return latest


# Main Dashboard
st.title("Pearls AQI Monitor")
st.caption("Clean 3‑day AQI outlook for Islamabad, powered by Muhammad Talha.")

# Sidebar – simplified, project-specific copy
st.sidebar.title("Pearls AQI")
st.sidebar.markdown(
    """
    Track **current air quality** and a **72‑hour forecast** for Islamabad.
    """
)

# Sidebar actions
st.sidebar.markdown("### Actions")
if RUNNING_IN_CLOUD:
    st.sidebar.write(
        "On Streamlit Cloud, data and forecasts are refreshed automatically "
        "by GitHub Actions.\n\n"
        "Use these buttons only when running the app locally."
    )
else:
    if st.sidebar.button("Collect fresh data", use_container_width=True):
        collect_fresh_data()
    st.sidebar.caption("Fetch latest hour from OpenMeteo into MongoDB.")

    if st.sidebar.button("Regenerate 3‑day forecast", use_container_width=True):
        refresh_predictions()
    st.sidebar.caption("Run prediction pipeline with the latest best model.")

# Load data
registry = load_model_registry()
predictions_df = load_predictions()
latest_data = load_latest_aqi()

# --- Top section: current AQI + model snapshot ---
current_col, model_col = st.columns([2, 1])

with current_col:
    st.subheader("Current air quality")

    # Default values
    current_aqi = None
    category = None

    if not predictions_df.empty:
        # Use first prediction as current estimate
        first_prediction = predictions_df.iloc[0]
        current_aqi = int(first_prediction["predicted_aqi"])
        category, _ = get_aqi_category(current_aqi)

        st.metric("AQI (estimated)", current_aqi, category)

        if "prediction_date" in first_prediction:
            pred_date = pd.to_datetime(first_prediction["prediction_date"])
            from datetime import timedelta

            pred_date_pk = pred_date + timedelta(hours=5)
            st.caption(f"Predictions generated: {pred_date_pk.strftime('%b %d, %H:%M')} PKT")
    elif latest_data:
        current_aqi = int(latest_data["aqi"])
        category, _ = get_aqi_category(current_aqi)
        ts = pd.to_datetime(latest_data["timestamp"])
        st.metric("AQI (measured)", current_aqi, category)
        st.caption(f"Last measurement: {ts.strftime('%Y-%m-%d %H:%M')}")
    else:
        st.info("No AQI data found yet. Run the pipelines to populate MongoDB.")

with model_col:
    st.subheader("Model snapshot")
    if registry:
        best_name = registry["best_model"]
        best_metrics = registry["models"][best_name]
        st.metric("Best model", best_name.upper())
        st.metric("R² score", best_metrics["r2"])
        st.caption("Model is retrained daily from the latest features.")
    else:
        st.info("No model registry found. Train a model first.")

# --- Forecast section ---
st.markdown("---")
st.subheader("3‑day forecast")

if not predictions_df.empty:
    fig = px.line(
        predictions_df,
        x="timestamp",
        y="predicted_aqi",
        labels={"predicted_aqi": "Predicted AQI", "timestamp": "Time"},
    )

    # AQI zones
    fig.add_hrect(y0=0, y1=50, fillcolor="green", opacity=0.08, line_width=0)
    fig.add_hrect(y0=50, y1=100, fillcolor="yellow", opacity=0.08, line_width=0)
    fig.add_hrect(y0=100, y1=150, fillcolor="orange", opacity=0.08, line_width=0)
    fig.add_hrect(y0=150, y1=200, fillcolor="red", opacity=0.08, line_width=0)

    # Make the forecast line stand out
    fig.update_traces(
        line=dict(color="#4ade80", width=3),
        hovertemplate="%{x|%b %d, %H:%M}<br>AQI: %{y}<extra></extra>",
    )

    # Clean layout: tighter margins, subtle grid
    fig.update_layout(
        height=360,
        showlegend=False,
        margin=dict(l=40, r=20, t=10, b=40),
        yaxis=dict(title="Predicted AQI", gridcolor="rgba(255,255,255,0.05)"),
        xaxis=dict(title="Time", showgrid=False),
    )

    st.plotly_chart(fig, use_container_width=True)

    with st.expander("Daily summary", expanded=True):
        predictions_df["date"] = predictions_df["timestamp"].dt.date
        daily_summary = (
            predictions_df.groupby("date")["predicted_aqi"].agg(["mean", "min", "max"]).reset_index()
        )
        daily_summary.columns = ["Date", "Avg AQI", "Min AQI", "Max AQI"]
        daily_summary["Avg AQI"] = daily_summary["Avg AQI"].round(0).astype(int)
        daily_summary["Min AQI"] = daily_summary["Min AQI"].round(0).astype(int)
        daily_summary["Max AQI"] = daily_summary["Max AQI"].round(0).astype(int)

        st.dataframe(daily_summary, use_container_width=True, hide_index=True)

        overall_min = predictions_df["predicted_aqi"].min()
        overall_max = predictions_df["predicted_aqi"].max()
        st.caption(f"Overall forecast range: {int(overall_min)}–{int(overall_max)} AQI")
else:
    st.info("No predictions available. Generate a 3‑day forecast from the sidebar.")

# --- Model comparison (optional details) ---
st.markdown("---")
with st.expander("Model comparison (details)", expanded=False):
    if registry:
        models_data = registry["models"]
        comparison_df = pd.DataFrame(
            {
                "Model": ["Random Forest", "XGBoost", "LightGBM"],
                "R²": [
                    models_data["random_forest"]["r2"],
                    models_data["xgboost"]["r2"],
                    models_data["lightgbm"]["r2"],
                ],
                "RMSE": [
                    models_data["random_forest"]["rmse"],
                    models_data["xgboost"]["rmse"],
                    models_data["lightgbm"]["rmse"],
                ],
                "MAE": [
                    models_data["random_forest"]["mae"],
                    models_data["xgboost"]["mae"],
                    models_data["lightgbm"]["mae"],
                ],
            }
        )

        best_idx = comparison_df["R²"].idxmax()
        st.dataframe(comparison_df, use_container_width=True, hide_index=True)
        st.caption(
            f"Best model: {comparison_df.loc[best_idx, 'Model']} "
            f"(R²={comparison_df.loc[best_idx, 'R²']}, "
            f"RMSE={comparison_df.loc[best_idx, 'RMSE']}, "
            f"MAE={comparison_df.loc[best_idx, 'MAE']})"
        )
    else:
        st.info("Model metrics will appear here after the first training run.")

# Footer
st.markdown("---")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
