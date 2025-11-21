import os
import requests

OWM_URL = "https://api.openweathermap.org/data/2.5/weather"

def get_weather_by_coords(lat, lon, api_key=None):
    api_key = api_key or os.environ.get("OPENWEATHER_API_KEY")
    if not api_key:
        raise RuntimeError("OpenWeatherMap API key required")
    params = {"lat": lat, "lon": lon, "appid": api_key, "units": "metric"}
    r = requests.get(OWM_URL, params=params, timeout=10)
    r.raise_for_status()
    j = r.json()
    return {
        "temp_c": j.get("main", {}).get("temp"),
        "pressure_hpa": j.get("main", {}).get("pressure"),
        "humidity": j.get("main", {}).get("humidity"),
        "wind_speed_mps": j.get("wind", {}).get("speed"),
        "weather_main": j.get("weather", [{}])[0].get("main"),
        "weather_desc": j.get("weather", [{}])[0].get("description")
    }

AIRPORT_COORDS = {
    "JFK": (40.6413, -73.7781),
    "LAX": (33.9416, -118.4085),
    "SFO": (37.6213, -122.3790),
    "ORD": (41.9742, -87.9073),
    "ATL": (33.6407, -84.4277),
}

def get_weather_by_airport(iata, api_key=None):
    if iata in AIRPORT_COORDS:
        lat, lon = AIRPORT_COORDS[iata]
        return get_weather_by_coords(lat, lon, api_key=api_key)
    else:
        raise KeyError(f"Airport coords for {iata} not found. Add to AIRPORT_COORDS or provide lat/lon.")
