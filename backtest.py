from plant import Gas, Wind, Solar
from solar_pipeline import prepare_solar_clusters_historical
from wind_pipeline import prepare_wind_on_shore_clusters_historical, prepare_wind_off_shore_clusters_historical
from entsoe_data import fetch_installed_capacity_zone, fetch_day_ahead_prices, fetch_day_ahead_demand
from renewable_locations import load_installations
from fuel_prices import load_gas_price_history, load_co2_price_history
import pandas as pd
from datetime import datetime
import random
from market import Market


random.seed(42) 
# The breakdowns happen in the exact same spots from one launch to the next: 
# the same power plant failing at the same time. While randomness always varies during a live run, 
# it repeats itself identically with every launch.


end = pd.Timestamp(datetime.now(), tz="Europe/Berlin") - pd.Timedelta(days=1)
start = end - pd.Timedelta(days=58)

zone= "DE_LU"



demand = fetch_day_ahead_demand(zone, start, end) # columns : time, demand
prices = fetch_day_ahead_prices(zone, start, end) # columns : time, prices


hourly = pd.merge(prices, demand, on="time", how="inner")

hourly["date"] = hourly["time"].dt.tz_localize(None).dt.normalize()
hourly = hourly.merge(load_gas_price_history(), on="date", how="left")
hourly = hourly.merge(load_co2_price_history(), on="date", how="left")

# returns 1390 rows with following columns:
# time: 2026-08-07 18:00:00+02:00  price, demand, only date, gas_price c02_price
#       2026-08-07 19:00:00+02:00

fuel_price = hourly['gas_price'].iloc[0]



######## Initialize instance Gaz

installed_capacity_DE_LU = fetch_installed_capacity_zone(zone,start,end)
fuel_price = hourly['gas_price'].iloc[0]


gaz = Gas(
    name="CCGT_gaz", 
    capacity_mw=installed_capacity_DE_LU["Fossil Gas"].iloc[0], 
    country="Germany",
    fuel_price=fuel_price, 
    efficiency=0.5, 
    emission_factor=0.2,
    )


######## Initialize instance Wind


#### Wind On Shore


wind_on_shore_file = "data/csv/Wind_Energy_Onshore_V20240104.csv"

coordinates_wind_on_shore = load_installations(wind_on_shore_file, extra_columns=["hub_height"])
coordinates_wind_on_shore_capacities = coordinates_wind_on_shore[coordinates_wind_on_shore["y_coordinates"] >= 40]

# start and end are Timestamp, archive API expects "YYYY-MM-DD" format
start_str = start.strftime("%Y-%m-%d")
end_str = end.strftime("%Y-%m-%d")

clusters_on_shore, weather_on_shore = prepare_wind_on_shore_clusters_historical(coordinates_wind_on_shore_capacities, 100, start_str, end_str)
# clusters_on_shore is a DataFrame with 100 rows, one per cluster, and 6 columns:
#  cluster latitude longitude installed_capacity n_installations n_installations 

# weather_on_shore is a list of 100 DataFrames, one per cluster. Each has 1'416 rows (59 days × 24 hours), 
# with the columns `time`, `wind_speed_100m`, `irradiance`, and `temperature`.

wind_on_shore_instances = [Wind(name=f"Wind_on_shore_{i}", capacity_mw=row["installed_capacity"], country="Germany", hub_height=row["hub_height"]) for i, row in clusters_on_shore.iterrows()]


### Wind Off shore 


wind_off_shore_file = "data/csv/Wind_Energy_Offshore_V20240104.csv"
coordinates_wind_off_shore = load_installations(wind_off_shore_file, extra_columns=["hub_height"])
# no coordinate anomalies found for offshore
clusters_off_shore, weather_off_shore = prepare_wind_off_shore_clusters_historical(coordinates_wind_off_shore,25, start_str, end_str)

wind_off_shore_instances = [Wind(name=f"Wind_off_shore_{i}", capacity_mw=row["installed_capacity"], country="Germany", hub_height=row["hub_height"]) for i, row in clusters_off_shore.iterrows()]


######## Initialize instance Solar


solar_file = "data/csv/Solar_Energy_V20240104.csv"
coordinates_solar_capacities = load_installations(solar_file) # return Data frame
# Filter value outside Germany
coordinates_solar_capacities = coordinates_solar_capacities[coordinates_solar_capacities["y_coordinates"] <= 55.1]
clusters_solar, weather_solar = prepare_solar_clusters_historical(coordinates_solar_capacities,25, start_str, end_str)

solar_instances = []
# instantiate 25 solar "plant" according to # clusters and data from Zenodo) :
# instantiate 25 solar "plant" according to # clusters and data from Zenodo) :
solar_instances = [Solar(name=f"Solar_{i}", capacity_mw=row["installed_capacity"], country="Germany") for i,row in clusters_solar.iterrows()]



######## Set up marketplace


list_plants = [gaz] + wind_on_shore_instances + wind_off_shore_instances + solar_instances
market = Market(list_plants)

# For each cluster's weather DataFrame in the list, use the "time" column as the row labels (index).
# This lets us read a value directly by timestamp, e.g. weather_solar[j].loc[t, "irradiance"],
# instead of filtering all 1416 rows at every hour. After this line, "time" is no longer a column.
weather_solar = [w.set_index("time") for w in weather_solar]
weather_on_shore = [w.set_index("time") for w in weather_on_shore]
weather_off_shore = [w.set_index("time") for w in weather_off_shore]

#for j, w in enumerate(weather_solar):
 #   print(f"Cluster {j}")
 #   print(w["time"])


# weather_solar[0].index: weather_solar[0] is the weather DataFrame for the first cluster. 
# Since set_index(“time”) was applied, its .index now contains all its timestamps (1'416 hours). 
# This is the list of hours for which weather data is available.
# isin(...): For each element in hourly[“time”], returns True if that timestamp is in this list, False otherwise.
# hourly[ ... ]: uses this True/False column as a filter. Only rows with “True” are kept.

hourly = hourly[hourly["time"].isin(weather_solar[0].index)]



model_prices = []

for day, day_df in hourly.groupby("date"):
    # day_df is the DataFrame of ONE day at a time (24 hourly rows, one per hour).
    # The loop runs once per day, about 59 times.
    gaz.set_fuel_price(day_df["gas_price"].iloc[0])
    co2_today = day_df["co2_price"].iloc[0]

    for i,time_day in day_df.iterrows():
        t = time_day["time"]
        for j, plant in enumerate(solar_instances):
            plant.set_weather(weather_solar[j].loc[t, "irradiance"])
            # weather_solar[j]: the DataFrame for cluster j (all its hours)
            # in this DataFrame, one single value => at time t
        
        for j, plant in enumerate(wind_on_shore_instances):
            plant.set_weather(weather_on_shore[j].loc[t, "wind_speed_100m"],
                              weather_on_shore[j].loc[t, "temperature"])

        for j, plant in enumerate(wind_off_shore_instances):
            plant.set_weather(weather_off_shore[j].loc[t, "wind_speed_100m"],
                              weather_off_shore[j].loc[t, "temperature"])


        price = market.clear(demand_capacity=time_day['demand'], c02_price=co2_today)
        model_prices.append({"time": t, "model_price": price})





results = pd.DataFrame(model_prices)
results["model_price"] = pd.to_numeric(results["model_price"], errors="coerce")
results = results.merge(hourly[["time", "price"]], on="time")

valid = results.dropna(subset=["model_price"])
print("Heures :", len(results))
print("SHORTAGE :", round(results["model_price"].isna().mean() * 100), "%")
print("Corrélation :", valid["model_price"].corr(valid["price"]))
print("Erreur médiane :", (valid["model_price"] - valid["price"]).median())