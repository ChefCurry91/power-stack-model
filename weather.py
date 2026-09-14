import openmeteo_requests

import pandas as pd
import requests_cache
from retry_requests import retry

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

# Test retrieval of hourly wind speed data from Open-Meteo
url = "https://api.open-meteo.com/v1/forecast"
params = {
    "latitude": 52.52,
    "longitude": 13.41,
    "hourly": "wind_speed_100m"
}
responses = openmeteo.weather_api(url, params = params)

response = responses[0]
hourly = response.Hourly()
hourly_wind_speed_100m = hourly.Variables(0).ValuesAsNumpy()
print(hourly_wind_speed_100m)
