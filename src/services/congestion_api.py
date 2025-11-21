import os
import requests


AVIATIONSTACK_URL = "http://api.aviationstack.com/v1/flights"


def get_congestion_by_airport(iata, api_key=None):
  api_key = api_key or os.environ.get("AVIATIONSTACK_API_KEY")
  if not api_key:
    raise RuntimeError("AviationStack API key required - set AVIATIONSTACK_API_KEY env var")

  params = {"access_key": api_key, "arr_icao": iata, "limit": 100}
  try:
    r = requests.get(AVIATIONSTACK_URL, params=params, timeout=10)
    r.raise_for_status()
    j = r.json()
    data = j.get("data", [])
  
    return {"recent_flights_count": len(data)}
  except Exception as e:
 
    return {"recent_flights_count": None, "error": str(e)}