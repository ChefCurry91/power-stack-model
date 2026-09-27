from plant import Gas, Nuclear, Wind, Solar
from solar_pipeline import prepare_solar_clusters, compute_solar_production_series
from market import Market
import pandas as pd
from datetime import datetime
from entsoe_data import fetch_load_forecast, fetch_installed_capacity_zone
from fuel_prices import fetch_gas_price, fetch_c02_price
from renewable_locations import load_installations
from weather import fetch_weather



# Convert current time into a pandas Timestamp with timezone, required by fetch_load_forecast().
# Window is 22h (not 24h): ENTSO-E's day-ahead load forecast has a limited horizon and doesn't
# always cover a full 24h from now — using 22h keeps us safely within the available data range,
# avoiding gaps that would otherwise need to be handled after merging with weather data.
start = pd.Timestamp(datetime.now(), tz="Europe/Berlin")
end = start + pd.Timedelta(hours=22)

zone= "DE_LU"


installed_capacity_DE_LU = fetch_installed_capacity_zone(zone,start,end)

latest_gas_price = fetch_gas_price()
latest_c02_price = fetch_c02_price()



######## Initialize instance Gaz

gaz = Gas(
    name="CCGT_gaz", 
    capacity_mw=installed_capacity_DE_LU["Fossil Gas"].iloc[0], 
    country="Germany",
    fuel_price=latest_gas_price, 
    efficiency=0.5, 
    emission_factor=0.2,
    )


########


######## Initialize instance Wind

wind_on_shore = Wind(name = 'Wind_farm_1', capacity_mw=installed_capacity_DE_LU["Wind Onshore"].iloc[0], country="Germany")

########


######## Initialize instance Solar

solar_file = "data/csv/Solar_Energy_V20240104.csv"

coordinates_solar_capacities = load_installations(solar_file) # return Data frame

# Filter value outside Germany
coordinates_solar_capacities = coordinates_solar_capacities[coordinates_solar_capacities["y_coordinates"] <= 55.1]



clusters_25, weather_list = prepare_solar_clusters(coordinates_solar_capacities,25)

#print(weather_list)
hours_of_forecasting = fetch_load_forecast(zone, start, end) # return date hours forecasted Load

# return for each cluster of list, 168 row with columns time, wind_speed, irradiance temperature based on next 7 * 24 hours of forecast
 
solar_instances = []


# instantiate 25 solar "plant" according to # clusters and data from Zenodo) :
solar_instances = [Solar(name=f"Solar_{i}", capacity_mw=row["installed_capacity"], country="Germany") for i,row in clusters_25.iterrows()]


# Convergence test:
# K = 25, 50, 100 and 200 clusters were evaluated.
# Estimated national solar production differed by only
# around 1-3% across all configurations.
#
# Increasing K beyond 25 therefore provides limited
# additional accuracy while significantly increasing
# computational cost and weather-data processing.
#
# K = 25 is retained as the default configuration.




list_plants = [gaz, wind_on_shore] + solar_instances



market = Market(list_plants)



def build_forecast_dataset(start_time_forecasting, end_time_forecasting, zone_forecasting, latitude, longitude):
    demand_df = fetch_load_forecast(zone_forecasting, start_time_forecasting, end_time_forecasting)

    weather_df = fetch_weather(latitude, longitude)
    weather_next_24h = weather_df[(weather_df["time"] >= start_time_forecasting) & (weather_df["time"] < end_time_forecasting)]

    combined_df = pd.merge(weather_next_24h, demand_df, on="time", how="inner")

    return combined_df




forecasted_situation = build_forecast_dataset(start,end,zone,52.52, 13.41)



for i, row in forecasted_situation.iterrows():
    current_time = row["time"]
    print(current_time)
    wind_on_shore.set_weather(wind_speed=row["wind_speed_100m"], temperature=row["temperature"])

    for j, cluster_row in clusters_25.iterrows():
        weather_at_this_cluster = weather_list[j]
        matching_row = weather_at_this_cluster[weather_at_this_cluster["time"] == current_time]
        irradiance_now = matching_row.iloc[0]["irradiance"]
        solar_instances[j].set_weather(irradiance_now)

    price = market.clear(demand_capacity=row['demand'], c02_price=latest_c02_price)
    print(f"{current_time}: Price={price}")










