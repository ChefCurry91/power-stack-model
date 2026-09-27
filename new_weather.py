import openmeteo_requests
import pandas as pd
import requests_cache
from retry_requests import retry




def _build_weather_df(response):
    # Build a weather DataFrame using one object response Open-Meteo.
    hourly = response.Hourly()
    hourly_time = pd.date_range(
        start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
        end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
        freq=pd.Timedelta(seconds=hourly.Interval()),
        inclusive="left"
    )
    weather_df = pd.DataFrame({
        "time": hourly_time,
        "wind_speed_100m": hourly.Variables(0).ValuesAsNumpy(),
        "irradiance": hourly.Variables(1).ValuesAsNumpy(),
        "temperature": hourly.Variables(2).ValuesAsNumpy()
    })
    weather_df["time"] = weather_df["time"].dt.tz_convert("Europe/Berlin")
    return weather_df






# Function fetch_weather_batch(), only accepts two coordinate strings,  built from geo_clustering.py's
# output: cluster_installations() + aggregate_clusters() produce a DataFrame 
# with one row per cluster (mean latitude, mean longitude, total capacity)

# => lat_string = ",".join(str(x) for x in clusters_25["latitude"].tolist())

def fetch_weather_batch(latitudes, longitudes):
   # latitudes, longitudes: comma-separated coordinate strings.  Returns a list of weather DataFrames, 
   # in the same order as the given coordinates.

    # Example: params = {"latitude": "51.6,48.24,52.85", ...} becomes, in the final request URL:
    # https://api.open-meteo.com/v1/forecast?latitude=51.6,48.24,52.85&longitude=...
    # The Open-Meteo server itself parses this comma-separated format and understands it as
    # 3 distinct points, not one strange value. It treats each (latitude, longitude) pair at
    # the same position as one separate location, and returns one response object per point,
    # in the same order — hence responses[0], responses[1], responses[2].




    cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitudes,
        "longitude": longitudes,
        "hourly": "wind_speed_100m,shortwave_radiation,temperature_2m",
    }
    responses = openmeteo.weather_api(url, params=params)

    # traverse responses, et pour chacun, on construi une DataFrame météo

    return [_build_weather_df(response) for response in responses]

#  it returns a LIST of DataFrames — the lenght of the list depends on number of cluster. 
#  each index represents a cluster with 168 rows an (one per hour) 
#  and contains those columns: time, wind_speed_100m, irradiance, temperature.

