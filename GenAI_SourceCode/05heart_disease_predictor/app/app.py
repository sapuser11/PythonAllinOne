import streamlit as st
import requests
import time
import pandas as pd
import webbrowser

#API_URL = "http://localhost:8000/predict"
API_URL = "https://heart-beat-api-wise-gazelle-xs.cfapps.us10-001.hana.ondemand.com/predict"  # Replace with your actual API URL
TIMEOUT = 30  # seconds

st.title("Heart Disease Predictor")
st.write("Enter the following details to predict the risk of heart disease:")

#Input fields for user data
name = st.text_input("Name", value="Patient Name")
age = st.number_input("Age", min_value=0, max_value=120, value=30)
weight = st.number_input("Weight (kg)", min_value=0, max_value=300, value=70)
bloodSugar = st.number_input("Blood Sugar Level (mg/dL)", min_value=0, max_value=300, value=100)
bloodPressure = st.number_input("Blood Pressure (mm Hg)", min_value=0, max_value=300, value=120)
smoker = st.selectbox("Smoker", options=[0, 1])
chronic_disease = st.selectbox("Chronic Disease", options=[0, 1])
diabetic = st.selectbox("Diabetic", options=[0, 1])
alcoholic = st.selectbox("Alcoholic", options=[0, 1])

if st.button("Predict"):
    # Prepare the data for prediction
    data = {
        "name": name,
        "age": age,
        "weight": weight,
        "bloodSugar": bloodSugar,
        "bloodPressure": bloodPressure,
        "smoker": smoker,
        "chronic_disease": chronic_disease,
        "diabetic": diabetic,
        "alcoholic": alcoholic
    }
    

    with st.spinner("Making prediction..."):
        try:
            response = requests.post(API_URL, json=data, timeout=TIMEOUT)
            response.raise_for_status()
            result = response.json()
            # Display results in a table with icons
            st.markdown("### Prediction Results")
            icon_map = {
                "High Risk": "🔴",
                "Medium Risk": "🟡",
                "Low Risk": "🟢"
            }

            results_df = pd.DataFrame([
                ["👤 Patient Name", result["patient_name"]],
                ["📅 Age", result["patient_age"]],
                [f"{icon_map.get(result['risk_level'], '❓')} Risk Level", result["risk_level"]],
                ["📊 Probability", f"{result['probability']:.2%}"],
                ["🏥 Final Observation", result["final_observation"]]
            ], columns=["Parameter", "Value"])

            st.table(results_df)
        except requests.exceptions.Timeout:
            st.error("The request timed out. Please try again later.")
        except requests.exceptions.RequestException as e:
            st.error(f"An error occurred: {e}")


if __name__ == "__main__":
    st.write("Ready to make predictions!")