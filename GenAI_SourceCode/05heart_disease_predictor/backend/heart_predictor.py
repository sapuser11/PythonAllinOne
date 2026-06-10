import pandas as pd
import numpy as np
import joblib
import os

def load_model(model_path):
    """
    Load the pre-trained model from the specified path.
    
    :param model_path: Path to the saved model file.
    :return: Loaded model object.
    """
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found at {model_path}")
    
    model = joblib.load(model_path)
    return model

def predict_heart_disease(model, feature_names, patient_data):
    
    # Convert patient data to DataFrame
    if isinstance(patient_data, dict):
        patient_df = pd.DataFrame([patient_data])
    else:
        patient_df = patient_data.copy()

    # Validate if the feature names match
    missing_cols = [col for col in feature_names if col not in patient_df.columns]
    if missing_cols:
        raise ValueError(f"Missing columns in patient data: {missing_cols}")
    
    # Extract features in the correct order
    X = patient_df[feature_names].values

    # Make predictions
    predictions = model.predict(X)
    probabilities = model.predict_proba(X)[:, 1]  # Probability of positive class

    results = []
    for i, pred in enumerate(predictions):
        result = {
            'patient_name': patient_df.iloc[i].get('name', 'Unknown'),
            'prediction': int(pred),
            'probability': float(probabilities[i]),
            'risk_level': ('Low Risk' if probabilities[i] < 0.3 
                           else 'Medium Risk' if probabilities[i] < 0.6 
                          else 'High Risk')
        }

        results.append(result)

    return results


def display_results(results):
    """
    Display the prediction results in a readable format.
    
    :param results: List of prediction results.
    """
    for result in results:
        print(f"Patient: {result['patient_name']}, "
              f"Prediction: {'Heart Disease' if result['prediction'] else 'No Heart Disease'}, "
              f"Probability: {result['probability']:.2f}, "
              f"Risk Level: {result['risk_level']}")
        
def main():
    # Load the model and feature names
    model = load_model("models/heart_disease_model.pkl")
    feature_names = pd.read_csv("models/features.csv")['feature'].tolist()
    # load new patient data
    df = pd.read_csv("./patients.csv")

    if df is not None:
        # Predict heart disease for the new patient data
        results = predict_heart_disease(model, feature_names, df)
        
        # Display the results
        display_results(results)
        
        #save in another csv file
        results_df = pd.DataFrame(results)
        results_df.to_csv("./results/predictions.csv", index=False)

if __name__ == "__main__":
    main()
