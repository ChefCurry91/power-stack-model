from dotenv import load_dotenv
import os
from entsoe import EntsoePandasClient
import pandas as pd

# Loads variables from the .env file
load_dotenv()  #

# Retrieves the API key from the environment
api_key = os.getenv("ENTSOE_API_KEY")  
client = EntsoePandasClient(api_key=api_key)  


def fetch_load_forecast(zone, start, end):
    load_forecast = client.query_load_forecast(zone, start=start, end=end)
    load_forecast_hourly = load_forecast[load_forecast.index.minute == 0]

    return load_forecast_hourly

