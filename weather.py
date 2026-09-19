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
        "hourly": "wind_speed_100m,shortwave_radiation,temperature_2m",
        # This string lists which variables to fetch, in order. Each one is later retrieved
        # by POSITION (not by name) via hourly.Variables(i).ValuesAsNumpy(): 
        #  Variables(0) -> wind_speed_100m   (1st in the list above)
        #  Variables(1) -> shortwave_radiation (2nd)
        #  Variables(2) -> temperature_2m (3rd)
        
        # If you reorder or add variables here, update the Variables(i) calls below to match,
        # or the wrong data will silently get labeled with the wrong name.
    }
    responses = openmeteo.weather_api(url, params=params)
    response = responses[0]
    hourly = response.Hourly()
    # It gives access to:
    #   - time info: hourly.Time(), hourly.TimeEnd(), hourly.Interval() (start, end, step in seconds)
    #   - the actual weather series: hourly.Variables(i).ValuesAsNumpy(), one per variable
    #     requested in params["hourly"] above, matched by position (0, 1, 2, ...)
    # hourly is an entry point object


    # hourly.Time() returns timestamp first point of entire serie
    # hourly. TimeEnd() return timestamp last point of entire serie
    # hourly.Interval() define the interval between each data point
    

    hourly_time = pd.date_range(
        start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
        end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
        freq=pd.Timedelta(seconds=hourly.Interval()),
        inclusive="left"
    )

    hourly_wind_speed_100m = hourly.Variables(0).ValuesAsNumpy()
    # Returns the full 168-hour (7-day) wind speed series, one value per hour,
    # in chronological order starting from today 00:00 (see note on fetch_weather above)
    hourly_irradiance = hourly.Variables(1).ValuesAsNumpy()
    hourly_temperature_m2 = hourly.Variables(2).ValuesAsNumpy()

    # return a data frame
    weather_df = pd.DataFrame({
        "time": hourly_time,
        "wind_speed_100m": hourly_wind_speed_100m,
        "irradiance": hourly_irradiance,
        "temperature": hourly_temperature_m2
    })

    # convert UTC into Europe Berlin format 
    weather_df["time"] = weather_df["time"].dt.tz_convert("Europe/Berlin")

    return weather_df


