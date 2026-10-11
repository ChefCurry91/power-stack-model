from dotenv import load_dotenv
import os
from entsoe import EntsoePandasClient


# Loads variables from the .env file
load_dotenv()  #

# Retrieves the API key from the environment
api_key = os.getenv("ENTSOE_API_KEY")  
client = EntsoePandasClient(api_key=api_key)  


def fetch_load_forecast(zone, start, end):
    load_forecast = client.query_load_forecast(zone, start=start, end=end)
    load_forecast_hourly = load_forecast[load_forecast.index.minute == 0]

    load_forecast_hourly = load_forecast_hourly.reset_index()
    load_forecast_hourly.columns = ["time", "demand"]
    

    return load_forecast_hourly

    # returns the demand (hour-by-hour variable) — used separately with market.clear(demand_capacity=...). 


  

def fetch_installed_capacity_zone(zone,start,end):

    installed_capacity  = client.query_installed_generation_capacity(zone,start=start, end=end)
    return installed_capacity

#   returns (fixed, a single “snapshot,” no hourly changes)—this is what should provide 
#   with the total national capacity, which you then distribute among your 25 clusters (proportionally),




def fetch_day_ahead_prices (zone, start, end):
    load_historic_data = client.query_day_ahead_prices(zone, start=start, end=end)
    load_historic_data_hourly = load_historic_data[load_historic_data.index.minute == 0]

    load_historic_price_hourly = load_historic_data_hourly.reset_index()
    load_historic_price_hourly.columns = ["time", "price"]
    

    return load_historic_price_hourly

def fetch_day_ahead_demand(zone,start,end):
    load_historic_data = client.query_load(zone, start=start, end=end)
    load_historic_data_hourly = load_historic_data[load_historic_data.index.minute == 0]

    load_historic_demand_hourly = load_historic_data_hourly.reset_index()
    load_historic_demand_hourly.columns = ["time", "demand"]

    return load_historic_demand_hourly




