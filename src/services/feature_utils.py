import pandas as pd


def build_feature_row(base_row: dict, weather: dict=None, congestion: dict=None):

  row = base_row.copy()
  # Add weather features
  if weather:
    row.update({
    "temp_c": weather.get("temp_c"),
    "pressure_hpa": weather.get("pressure_hpa"),
    "humidity": weather.get("humidity"),
    "wind_speed_mps": weather.get("wind_speed_mps"),
    })
  else:
    row.update({"temp_c": None, "pressure_hpa": None, "humidity": None, "wind_speed_mps": None})


  # Add congestion features
  if congestion:
    row.update({"recent_flights_count": congestion.get("recent_flights_count")})
  else:
    row.update({"recent_flights_count": None})


  # Return single-row DataFrame
  return pd.DataFrame([row])