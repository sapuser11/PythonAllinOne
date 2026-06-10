from fastapi import FastAPI, HTTPException  
from pydantic import BaseModel
import joblib
import os
from pathlib import Path
import pandas as pd
import numpy as np
from fastapi.responses import RedirectResponse

##Initialize a microservice - web service
app = FastAPI(title="Heart Disease Predictor", version="1.0")

#Global variables
model = None
feature_names = None

def load_model_if_needed():
    global model
    global feature_names

    try:
        if model is not None:
            return True
            
        possible_paths = [
            ('model/heart_disease_model.pkl',
            'model/features.csv'),
            (Path(__file__).parent / "model" / "heart_disease_model.pkl",
            Path(__file__).parent / "model" / "features.csv")
        ]
        for model_path, features_path in possible_paths:
            if Path(model_path).exists() and Path(features_path).exists():
                model = joblib.load(model_path)
                feature_names = pd.read_csv(features_path)['feature'].tolist()
                print(f"✅ Model loaded from {model_path}")
                return True
        else:
            raise FileNotFoundError("❌ Model file not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading model: {str(e)}")


class PatientData(BaseModel):
    name: str
    age: int
    weight: int
    bloodSugar: int
    bloodPressure: int
    smoker: int
    chronic_disease: int
    diabetic: int
    alcoholic: int

@app.post("/predict")
async def predict_heart_disease(data: PatientData):
    try:
        if not load_model_if_needed():
            raise HTTPException(status_code=500, detail="Model not loaded.")

        # Prepare input data
        patient_dict = data.model_dump()
        input_data = pd.DataFrame([patient_dict])
        
        #get feature columns in the same order as the model was trained
        missing_cols = [col for col in feature_names if col not in input_data.columns]
        if missing_cols:
            raise HTTPException(status_code=400, detail=f"Missing features: {', '.join(missing_cols)}") 
        
        X = input_data[feature_names].values

        # Make prediction
        prediction = model.predict(X)
        probability = model.predict_proba(X)[:, 1]

        return {
            "patient_name": data.name,
            "probability": float(probability[0]),
            "patient_age": data.age,
            "risk_level": "Low Risk" if probability[0] < 0.3 else
                          "Medium Risk" if probability[0] < 0.7 else
                          "High Risk",
            "final_observation" : "Heart Disease" if prediction[0] == 1 else "No Heart Disease"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during prediction: {str(e)}")
    
@app.get("/")
async def redirect_to_docs():
    return RedirectResponse(url="/docs")


if __name__ == "__main__":
    import uvicorn
    print("Run using http://localhost:8000/predict, press Ctrl+C to stop the server")
    uvicorn.run(app, host="0.0.0.0", port=8000)