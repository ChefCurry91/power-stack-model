from renewable_locations import load_installations
from wind_pipeline import prepare_wind_on_shore_clusters, prepare_wind_off_shore_clusters, compute_wind_on_shore_production_series, compute_wind_off_shore_production_series

from entsoe_data import fetch_load_forecast 
from plant import Wind


import pandas as pd
from datetime import datetime




# Required to be passed into fetch_installed_capacity_zone
start = pd.Timestamp(datetime.now(), tz="Europe/Berlin")
end = start + pd.Timedelta(hours=22)
zone = "DE_LU"


wind_on_shore_file = "data/csv/Wind_Energy_Onshore_V20240104.csv"

coordinates_wind_on_shore = load_installations(wind_on_shore_file, extra_columns=["hub_height"])
coordinates_wind_on_shore_capacities = coordinates_wind_on_shore[coordinates_wind_on_shore["y_coordinates"] >= 40]
# filter out rows with swapped lat/lon coordinates (25 rows identified, see README)

wind_off_shore_file = "data/csv/Wind_Energy_Offshore_V20240104.csv"
coordinates_wind_off_shore = load_installations(wind_off_shore_file, extra_columns=["hub_height"])
# no coordinate anomalies found for offshore


hours_of_forecasting = fetch_load_forecast(zone, start, end)


# Convergence test (onshore):
# K = 25, 50, 100, 200 clusters were evaluated. An initial run with default availability
# (0.99) showed 5-10% oscillation across K. To rule out random availability noise as the
# cause, the test was re-run with availability=1.0 (forcing all plants always available) —
# results were nearly identical (<0.2% difference from the default-availability run),
# confirming the oscillation reflects genuine geographic variation in wind speed, not
# statistical noise. This is consistent with wind's known sensitivity to local terrain,
# unlike solar irradiance. K=100 was chosen as a pragmatic balance between granularity
# and computational cost, not a value validated by clean convergence.

clusters_on_shore, weather_on_shore = prepare_wind_on_shore_clusters(coordinates_wind_on_shore_capacities, 100)
wind_on_shore_instances = [Wind(name=f"Wind_on_shore_{i}", capacity_mw=row["installed_capacity"], country="Germany", hub_height=row["hub_height"]) for i, row in clusters_on_shore.iterrows()]
wind_on_shore_production = compute_wind_on_shore_production_series(clusters_on_shore, weather_on_shore, wind_on_shore_instances, hours_of_forecasting)


# Convergence test (offshore):
# K = 25, 50, 100, 200 clusters were evaluated. Results varied by less than 1.5% across
# all configurations — clean convergence, similar to solar, consistent with offshore
# wind's greater spatial homogeneity (open sea, fewer local obstacles).
# K=25 is retained as sufficient.
clusters_off_shore, weather_off_shore = prepare_wind_off_shore_clusters(coordinates_wind_off_shore, 25)
wind_off_shore_instances = [Wind(name=f"Wind_off_shore_{i}", capacity_mw=row["installed_capacity"], country="Germany", hub_height=row["hub_height"]) for i, row in clusters_off_shore.iterrows()]
wind_off_shore_production = compute_wind_off_shore_production_series(clusters_off_shore, weather_off_shore, wind_off_shore_instances, hours_of_forecasting)


print(wind_on_shore_production)
print(wind_off_shore_production)





