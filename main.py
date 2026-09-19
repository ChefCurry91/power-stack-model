from plant import Plant,Gas, Nuclear, Wind, Solar
from market import Market
from datetime import datetime
from weather import fetch_weather
import pandas as pd
from entsoe_data import fetch_load_forecast


# initialize instance Gaz

gaz = Gas(
    name="CCGT_gaz", 
    capacity_mw=13000, 
    country="Germany",
    fuel_price=30, 
    efficiency=0.5, 
    emission_factor=0.2,
    )

# initialize instance Nuclear

nuclear = Nuclear(
        name="Benznau_nuclear",
        capacity_mw = 30000,
        country="Switzerland",
        fuel_price = 20,
        efficiency = 1,
        emission_factor = 0
    )


# initialize instance Wind

wind = Wind(name = 'Wind_farm_1', capacity_mw=22000, country="Germany")

# initialize instance Solar

solar = Solar(name='Park_1',capacity_mw=20000, country="Germany")



# initialize instance Wind

list_plants = [gaz, nuclear, solar, wind]
market = Market(list_plants)


def build_forecast_dataset(start_time_forecasting, end_time_forecasting, zone_forecasting, latitude, longitude):
    # Fetch electricity demand forecast for the given zone and time window
    list_demand_electricity_next_24_hours = fetch_load_forecast(zone_forecasting, start_time_forecasting, end_time_forecasting)

    # Turn the timestamp index into a plain "time" column, so it can be merged with weather data
    demand_df = list_demand_electricity_next_24_hours.reset_index()
    # Rename columns to "time"/"demand" for clarity and to match weather_df's column name
    demand_df.columns = ["time", "demand"]

    # Fetch the full 168h weather forecast, then keep only the requested window
    weather_df = fetch_weather(latitude, longitude)
    weather_next_24h = weather_df[(weather_df["time"] >= start_time_forecasting) & (weather_df["time"] < end_time_forecasting)]

    # Combine both sources on matching timestamps (drops hours missing from either side)
    combined_df = pd.merge(weather_next_24h, demand_df, on="time", how="inner")

    return combined_df


# Convert current time into a pandas Timestamp with timezone, required by fetch_load_forecast().
# Window is 22h (not 24h): ENTSO-E's day-ahead load forecast has a limited horizon and doesn't
# always cover a full 24h from now — using 22h keeps us safely within the available data range,
# avoiding gaps that would otherwise need to be handled after merging with weather data.
start = pd.Timestamp(datetime.now(), tz="Europe/Berlin")
end = start + pd.Timedelta(hours=22)

zone= "DE_LU"

forecasted_situation = build_forecast_dataset(start,end,zone,52.52, 13.41)


print('whoa')
for i, row in forecasted_situation.iterrows():
    price = market.clear(demand_capacity=row['demand'], c02_price=80, wind_speed=row["wind_speed_100m"], temperature=row['temperature'], irradiance=row['irradiance'])
    print(f"{row['time']}: Price={price}")

