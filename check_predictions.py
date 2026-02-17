from src.database.mongo_db import MongoDB
import pandas as pd

mongo = MongoDB()
mongo.connect()

coll = mongo.get_collection('predictions')
preds = list(coll.find().sort('timestamp', 1))
df = pd.DataFrame(preds)

print(f'Total predictions: {len(df)}')
print(f'\nFirst 10:')
print(df[['timestamp', 'predicted_aqi']].head(10))
print(f'\nLast 10:')
print(df[['timestamp', 'predicted_aqi']].tail(10))
print(f'\nUnique values: {df["predicted_aqi"].nunique()}')
print(f'\nValue counts:')
print(df['predicted_aqi'].value_counts().head(20))
print(f'\nStats:')
print(df['predicted_aqi'].describe())

mongo.close()
