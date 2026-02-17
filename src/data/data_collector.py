import os
import pandas as pd
import requests
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

CITY = os.getenv("CITY_NAME", "Islamabad")
LAT = float(os.getenv("CITY_LATITUDE", "33.6996"))
LON = float(os.getenv("CITY_LONGITUDE", "73.0362"))

START_DATE = "2024-12-24"
END_DATE = "2025-12-24"

OUTPUT_DIR = Path(__file__).resolve().parents[2] / "data" / "raw"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

AIR_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
WEATHER_URL = "https://archive-api.open-meteo.com/v1/archive"

AIR_PARAMS = ["pm10", "pm2_5", "carbon_monoxide", "nitrogen_dioxide", "sulphur_dioxide", "ozone"]
WEATHER_PARAMS = ["temperature_2m", "relative_humidity_2m", "surface_pressure", "wind_speed_10m", 
                  "wind_direction_10m", "precipitation", "cloud_cover"]


def fetch_api(url, params):
    """Fetch API data and return DataFrame."""
    try:
        resp = requests.get(url, params=params, timeout=120)
        resp.raise_for_status()
        data = resp.json().get("hourly", {})
        if "time" not in data:
            return pd.DataFrame()
        df = pd.DataFrame(data)
        df["timestamp"] = pd.to_datetime(df["time"])
        df.drop(columns=["time"], inplace=True)
        return df
    except Exception:
        return pd.DataFrame()


# Main Function
def main():
    print(f"Fetching AQI and weather data for {CITY} ({LAT}, {LON})")
    print(f"Date range: {START_DATE} to {END_DATE}")

    # Air Quality Data
    air_df = fetch_api(AIR_URL, {
        "latitude": LAT,
        "longitude": LON,
        "start_date": START_DATE,
        "end_date": END_DATE,
        "hourly": ",".join(AIR_PARAMS),
        "timezone": "Asia/Karachi"
    })

    # Weather Data
    weather_df = fetch_api(WEATHER_URL, {
        "latitude": LAT,
        "longitude": LON,
        "start_date": START_DATE,
        "end_date": END_DATE,
        "hourly": ",".join(WEATHER_PARAMS),
        "timezone": "Asia/Karachi"
    })

    if air_df.empty or weather_df.empty:
        print("Failed to fetch data. Check your internet or API.")
        return

    # Merge air and weather data
    df = pd.merge(air_df, weather_df, on="timestamp", how="inner")
    df["city"] = CITY
    df["latitude"] = LAT
    df["longitude"] = LON

    # Drop duplicates and missing values
    df.drop_duplicates(subset=["timestamp"], inplace=True)
    df.dropna(subset=["pm2_5", "pm10"], inplace=True)

    # Save data
    filename = OUTPUT_DIR / f"raw_data_{CITY.lower()}_{START_DATE.replace('-', '')}-{END_DATE.replace('-', '')}.csv"
    df.to_csv(filename, index=False)

    print(f"\nData saved to: {filename}")
    print(f"Rows: {len(df)}, Columns: {len(df.columns)}")
    print(f"Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
    print(f"\nNext step: Explore data in Jupyter notebook")


if __name__ == "__main__":
    main()
