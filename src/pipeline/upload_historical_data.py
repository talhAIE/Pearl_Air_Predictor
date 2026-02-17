"""
Upload Historical Features to MongoDB
One-time script to populate MongoDB with existing processed data
"""

import pandas as pd
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).resolve().parents[2]))

from src.database.mongo_db import MongoDB


def upload_historical_data():
    """Upload processed features to MongoDB."""
    
    print("Uploading Historical Data to MongoDB\n")
    
    # Load processed data with features
    data_file = Path(__file__).resolve().parents[2] / "data" / "processed" / "processed_aqi.csv"
    
    if not data_file.exists():
        print(f"Error: {data_file} not found!")
        print("Run feature_engineering.py first")
        return False
    
    print(f"Loading data from: {data_file.name}")
    df = pd.read_csv(data_file)
    print(f"Loaded {len(df)} rows\n")
    
    # Connect to MongoDB
    mongo = MongoDB()
    if not mongo.connect():
        return False
    
    collection = mongo.get_collection("aqi_features")
    
    # Clear existing data (optional - remove if you want to append)
    print("Clearing existing data...")
    collection.delete_many({})
    
    # Convert DataFrame to list of dictionaries
    print("Converting data...")
    records = df.to_dict('records')
    
    # Upload to MongoDB
    print(f"Uploading {len(records)} records to MongoDB...")
    collection.insert_many(records)
    
    print(f"\nSuccess! Uploaded {len(records)} rows to 'aqi_features' collection")
    
    # Verify
    count = collection.count_documents({})
    print(f"Verified: {count} documents in MongoDB\n")
    
    mongo.close()
    return True


if __name__ == "__main__":
    success = upload_historical_data()
    sys.exit(0 if success else 1)
