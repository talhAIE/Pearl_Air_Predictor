import os
import certifi
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()


class MongoDB:
    """MongoDB connection manager"""
    
    def __init__(self):
        # try find first streamlit secrets then fallback to .env
        try:
            import streamlit as st
            self.uri = st.secrets.get("MONGODB_URI", os.getenv("MONGODB_URI"))
            self.db_name = st.secrets.get("MONGODB_DATABASE", os.getenv("MONGODB_DATABASE", "aqi_predictor"))
        except:
            # Fallback to .env
            self.uri = os.getenv("MONGODB_URI")
            self.db_name = os.getenv("MONGODB_DATABASE", "aqi_predictor")
        
        self.client = None
        self.db = None
    
    def connect(self):
        """Connect to MongoDB."""
        try:
            # Use certifi for SSL certificates and allow invalid certs for GitHub Actions
            self.client = MongoClient(
                self.uri,
                tls=True,
                tlsCAFile=certifi.where(),
                tlsAllowInvalidCertificates=True,
                serverSelectionTimeoutMS=10000
            )
            self.db = self.client[self.db_name]
            self.client.admin.command('ping')
            print(f"Connected to MongoDB: {self.db_name}")
            return True
        except Exception as e:
            print(f"MongoDB connection failed: {str(e)[:200]}")
            return False
    
    def get_collection(self, collection_name):
        """Get a collection."""
        if self.db is None:
            self.connect()
        return self.db[collection_name]
    
    def close(self):
        """Close connection."""
        if self.client:
            self.client.close()


if __name__ == "__main__":
    mongo = MongoDB()
    if mongo.connect():
        print("MongoDB is ready!")
        mongo.close()
    else:
        print("\nTroubleshooting:")
        print("1. Check MONGODB_URI in .env file")
        print("2. Install certifi: pip install certifi")
        print("3. Check MongoDB Atlas network access (allow your IP)")

