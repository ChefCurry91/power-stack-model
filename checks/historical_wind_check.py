import pandas as pd
from datetime import datetime

from power_stack.sources.renewable_locations import load_installations
from power_stack.pipelines.wind_pipeline import prepare_wind_on_shore_clusters_historical, prepare_wind_off_shore_clusters_historical

end = pd.Timestamp(datetime.now(), tz="Europe/Berlin") - pd.Timedelta(days=1)
start = end - pd.Timedelta(days=58)


wind_on_shore_file = "data/csv/Wind_Energy_Onshore_V20240104.csv"
wind_off_shore_file = "data/csv/Wind_Energy_Offshore_V20240104.csv"

coordinates_wind_on_shore = load_installations(wind_on_shore_file, extra_columns=["hub_height"])
coordinates_wind_on_shore_capacities = coordinates_wind_on_shore[coordinates_wind_on_shore["y_coordinates"] >= 40]

coordinates_wind_off_shore = load_installations(wind_off_shore_file, extra_columns=["hub_height"])


clusters_wind_on_shore, weather_on_shore = prepare_wind_on_shore_clusters_historical(
    coordinates_wind_on_shore_capacities, 100,
    start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"))

  

clusters_wind_off_shore, weather_off_shore = prepare_wind_off_shore_clusters_historical(
    coordinates_wind_off_shore, 25,
    start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"))

