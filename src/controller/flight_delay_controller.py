import os
import streamlit as st
import joblib
from src.services import weather_api, congestion_api
from src.services.feature_utils import build_feature_row


MODELS_DIR = os.environ.get("MODELS_DIR", "./models")

class FlightDelayController:
    def __init__(self):
        self.models = {}
        for w in ["t-12", "t-6", "t-3", "t-1"]:
            path = os.path.join(MODELS_DIR, f"model_rf_{w}.joblib")
            if os.path.exists(path):
                try:
                    self.models[w] = joblib.load(path)
                except:
                    pass

    def run_prediction(self):
        st.title("Make a Flight Delay Prediction")
        col1, col2 = st.columns(2)
        with col1:
            year = st.number_input("Year", value=2019, step=1)
            month = st.selectbox("Month", list(range(1,13)), index=0)
            day = st.number_input("Day of month", value=1, step=1)
            dep_hour = st.number_input("Scheduled departure hour (0-23)", value=9, min_value=0, max_value=23, step=1)
        with col2:
            carrier = st.text_input("Carrier code (IATA)", value="AA")
            origin = st.text_input("Origin (IATA)", value="JFK")
            dest = st.text_input("Destination (IATA)", value="LAX")
            distance = st.number_input("Distance (miles)", value=2475)

        base = {
            "YEAR": year,
            "MONTH": month,
            "DAY_OF_MONTH": day,
            "CRS_DEP_HOUR": dep_hour,
            "UNIQUE_CARRIER": carrier,
            "ORIGIN": origin,
            "DEST": dest,
            "DISTANCE": distance
        }

        st.markdown("---")
        st.subheader("Realtime feature augmentation")
        use_real = st.checkbox("Fetch real-time weather and congestion", value=True)

        weather = None
        congestion = None

        if use_real:
            try:
                weather = weather_api.get_weather_by_airport(origin)
            except:
                pass
            try:
                congestion = congestion_api.get_congestion_by_airport(origin)
            except:
                pass

        features_df = build_feature_row(base, weather=weather, congestion=congestion)
        st.write("Features used for prediction:")
        st.dataframe(features_df)

        chosen_model = None
        for w in ["t-1","t-3","t-6","t-12"]:
            if w in self.models:
                chosen_model = (w, self.models[w])
                break

        if not chosen_model:
            st.error("No trained models found in ./models")
            return

        wname, model = chosen_model
        if st.button("Predict delay"):
            try:
                prob = float(model.predict_proba(features_df)[:,1][0])
                pred = int(model.predict(features_df)[0])
            except Exception as e:
                st.error(str(e))
                return

            st.success(f"Model ({wname}) -> Delay probability: {prob:.3f}  (delayed = {pred})")
            st.info(f"Risk Score (0-100): {int(prob*100)}")

            prompt = (
                f"Flight: {base}. Model {wname} predicted delay probability {prob:.2f}. "
                f"Provide 3 likely reasons and 2 actionable tips for the passenger."
            )
            st.markdown("LLM Explanation Prompt:")
            st.code(prompt)

    def run_monitoring(self):
        st.title("Data & Model Monitoring")
        airport = st.text_input("Airport (IATA)", value="JFK")
        if st.button("Fetch live congestion & weather"):
            try:
                w = weather_api.get_weather_by_airport(airport)
                c = congestion_api.get_congestion_by_airport(airport)
                st.write("Weather:", w)
                st.write("Congestion:", c)
            except Exception as e:
                st.error(str(e))
