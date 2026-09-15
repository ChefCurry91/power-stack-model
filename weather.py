import openmeteo_requests
import pandas as pd
import requests_cache
from retry_requests import retry



def fetch_weather(latitude, longitude):
    cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "wind_speed_100m,shortwave_radiation"
    }
    responses = openmeteo.weather_api(url, params=params)
    response = responses[0]
    hourly = response.Hourly()

    hourly_wind_speed_100m = hourly.Variables(0).ValuesAsNumpy()
    hourly_irradiance = hourly.Variables(1).ValuesAsNumpy()

    return hourly_wind_speed_100m, hourly_irradiance


#wind_speed_list, irradiance_list = fetch_weather(52.52, 13.41)

#print('hello')
#print(wind_speed_list)
#print(irradiance_list)