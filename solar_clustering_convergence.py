from renewable_locations import load_installations
from solar_pipeline import prepare_solar_clusters, compute_solar_production_series


from entsoe_data import fetch_load_forecast 
from plant import Solar


import pandas as pd
from datetime import datetime

# Required to be passed into fetch_installed_capacity_zone
start = pd.Timestamp(datetime.now(), tz="Europe/Berlin")
end = start + pd.Timedelta(hours=22)
zone= "DE_LU"



# Scale up to match real national total (see README: known limitation on ground-mounted vs rooftop mix)

solar_file = "data/csv/Solar_Energy_V20240104.csv"

coordinates_solar_capacities = load_installations(solar_file)
# return Data frame

# Filter value outside Germany
coordinates_solar_capacities = coordinates_solar_capacities[coordinates_solar_capacities["y_coordinates"] <= 55.1]



clusters_25, weather_list = prepare_solar_clusters(coordinates_solar_capacities,25)


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

solar_production = compute_solar_production_series(clusters_25,weather_list,solar_instances, hours_of_forecasting)


# exploratory check:
# compare cluster distribution against
# Bavaria / BW / NRW solar concentrations

def assign_approx_region(lat, lon):
    if 47.3 <= lat <= 50.6 and 8.9 <= lon <= 13.8:
        return "Bavaria"
    elif 47.5 <= lat <= 49.8 and 7.5 <= lon <= 10.5:
        return "Baden-Württemberg"
    elif 50.3 <= lat <= 52.5 and 5.9 <= lon <= 9.5:
        return "NRW"
    else:
        return "Other"

clusters_25["region"] = clusters_25.apply(lambda row: assign_approx_region(row["latitude"], row["longitude"]), axis=1)

