from plant import Gas, Wind, Solar
from solar_pipeline import prepare_solar_clusters, compute_solar_production_series
from wind_pipeline import prepare_wind_on_shore_clusters, prepare_wind_off_shore_clusters, compute_wind_on_shore_production_series, compute_wind_off_shore_production_series
from market import Market
import pandas as pd
from datetime import datetime
from entsoe_data import fetch_load_forecast, fetch_installed_capacity_zone
from fuel_prices import fetch_gas_price, fetch_c02_price
from renewable_locations import load_installations



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

hours_of_forecasting = fetch_load_forecast(zone, start, end) # return date hours forecasted Load

# return for each cluster of list, 168 row with columns time, wind_speed, irradiance temperature based on next 7 * 24 hours of forecast



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


#### Wind On Shore


wind_on_shore_file = "data/csv/Wind_Energy_Onshore_V20240104.csv"

coordinates_wind_on_shore = load_installations(wind_on_shore_file, extra_columns=["hub_height"])
coordinates_wind_on_shore_capacities = coordinates_wind_on_shore[coordinates_wind_on_shore["y_coordinates"] >= 40]
# filter out rows with swapped lat/lon coordinates (25 rows identified, see README)

clusters_on_shore, weather_on_shore = prepare_wind_on_shore_clusters(coordinates_wind_on_shore_capacities, 100)

wind_on_shore_instances = [Wind(name=f"Wind_on_shore_{i}", capacity_mw=row["installed_capacity"], country="Germany", hub_height=row["hub_height"]) for i, row in clusters_on_shore.iterrows()]



### Wind Off shore 


wind_off_shore_file = "data/csv/Wind_Energy_Offshore_V20240104.csv"

coordinates_wind_off_shore = load_installations(wind_off_shore_file, extra_columns=["hub_height"])
# no coordinate anomalies found for offshore

clusters_off_shore, weather_off_shore = prepare_wind_off_shore_clusters(coordinates_wind_off_shore, 25)
wind_off_shore_instances = [Wind(name=f"Wind_off_shore_{i}", capacity_mw=row["installed_capacity"], country="Germany", hub_height=row["hub_height"]) for i, row in clusters_off_shore.iterrows()]



########


######## Initialize instance Solar

solar_file = "data/csv/Solar_Energy_V20240104.csv"

coordinates_solar_capacities = load_installations(solar_file) # return Data frame

# Filter value outside Germany
coordinates_solar_capacities = coordinates_solar_capacities[coordinates_solar_capacities["y_coordinates"] <= 55.1]



clusters_25, weather_list = prepare_solar_clusters(coordinates_solar_capacities,25)


# return for each cluster of list, 168 row with columns time, wind_speed, irradiance temperature based on next 7 * 24 hours of forecast
 
solar_instances = []


# instantiate 25 solar "plant" according to # clusters and data from Zenodo) :
solar_instances = [Solar(name=f"Solar_{i}", capacity_mw=row["installed_capacity"], country="Germany") for i,row in clusters_25.iterrows()]



# list_plants must be ONE FLAT list of individual plant instances, not a list containing
# sub-lists. [gaz] (a single-item list) is concatenated with "+" to the existing lists
# (wind_on_shore_instances, wind_off_shore_instances, solar_instances) so that Market's
# loop (for element in sorted_plants:) sees each plant one by one, not a nested list
list_plants = [gaz] + wind_on_shore_instances + wind_off_shore_instances + solar_instances


market = Market(list_plants)



#def build_forecast_dataset(start_time_forecasting, end_time_forecasting, zone_forecasting, latitude, longitude):
#    demand_df = fetch_load_forecast(zone_forecasting, start_time_forecasting, end_time_forecasting)

   # weather_df = fetch_weather(latitude, longitude)
    #weather_next_24h = weather_df[(weather_df["time"] >= start_time_forecasting) & (weather_df["time"] < end_time_forecasting)]

    #combined_df = pd.merge(weather_next_24h, demand_df, on="time", how="inner")

    #return combined_df




#forecasted_situation = build_forecast_dataset(start,end,zone,52.52, 13.41)



#for i, row in forecasted_situation.iterrows():
#    current_time = row["time"]
#    print(current_time)
#    wind_on_shore.set_weather(wind_speed=row["wind_speed_100m"], temperature=row["temperature"])

#    for j, cluster_row in clusters_25.iterrows():
#        weather_at_this_cluster = weather_list[j]
#        matching_row = weather_at_this_cluster[weather_at_this_cluster["time"] == current_time]
#        irradiance_now = matching_row.iloc[0]["irradiance"]
#        solar_instances[j].set_weather(irradiance_now)

 #   price = market.clear(demand_capacity=row['demand'], c02_price=latest_c02_price)
 #   print(f"{current_time}: Price={price}")







for i, row in hours_of_forecasting.iterrows():
    current_time = row["time"]
    print(current_time)

    for j, cluster_row in clusters_25.iterrows():
        matching_row = weather_list[j][weather_list[j]["time"] == current_time]
        irradiance_now = matching_row.iloc[0]["irradiance"]
        solar_instances[j].set_weather(irradiance_now)

    for j, cluster_row in clusters_on_shore.iterrows():
        matching_row = weather_on_shore[j][weather_on_shore[j]["time"] == current_time]
        wind_speed_now = matching_row.iloc[0]["wind_speed_100m"]
        temperature_now = matching_row.iloc[0]["temperature"]
        wind_on_shore_instances[j].set_weather(wind_speed_now, temperature_now)

    for j, cluster_row in clusters_off_shore.iterrows():
        matching_row = weather_off_shore[j][weather_off_shore[j]["time"] == current_time]
        wind_speed_now = matching_row.iloc[0]["wind_speed_100m"]
        temperature_now = matching_row.iloc[0]["temperature"]
        wind_off_shore_instances[j].set_weather(wind_speed_now, temperature_now)

    price = market.clear(demand_capacity=row['demand'], c02_price=latest_c02_price)
    print(f"{current_time}: Price={price}")


