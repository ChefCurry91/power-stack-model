import pandas as pd
from datetime import datetime

from power_stack.sources.renewable_locations import load_installations
from power_stack.pipelines.solar_pipeline import prepare_solar_clusters_historical

end = pd.Timestamp(datetime.now(), tz="Europe/Berlin") - pd.Timedelta(days=1)
start = end - pd.Timedelta(days=58)

solar_file = "data/csv/Solar_Energy_V20240104.csv"

coordinates_solar = load_installations(solar_file)
# return Data frame

# Filter value outside Germany
coordinates_solar = coordinates_solar[coordinates_solar["y_coordinates"] <= 55.1]

clusters, weather = prepare_solar_clusters_historical(
    coordinates_solar, 25,
    start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"))



