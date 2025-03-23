import joblib

new_data = []

loaded_pipeline = joblib.load('pipeline.pkl')
prediction = loaded_pipeline.predict(new_data)
