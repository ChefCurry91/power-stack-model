from entsoe_data import fetch_installed_capacity_zone 
from geo_clustering import cluster_installations, aggregate_clusters
from new_weather import fetch_weather_batch

import pandas as pd
from datetime import datetime

# Required to be passed into fetch_installed_capacity_zone
start = pd.Timestamp(datetime.now(), tz="Europe/Berlin")
end = start + pd.Timedelta(hours=22)
zone= "DE_LU"

installed_capacity_DE_LU = fetch_installed_capacity_zone(zone,start,end)




# Wind Onshore

def prepare_wind_on_shore_clusters(coordinates_df, n_clusters):

    # Fetch total Wind Onshore capacity DE-LU
    wind_on_shore_capacity_DE_LU = fetch_installed_capacity_zone(zone,start,end)
    # Extract value 
    target_total_capacity_wind_on_shore = wind_on_shore_capacity_DE_LU["Wind Onshore"].iloc[0]


    # Defines number of clusters # Wind Onshore
    df_number_clusters, kmean_number_clusters = cluster_installations(coordinates_df.copy(), n_clusters)

    # aggregate_clusters() calculate latitude,longitude,installed capacity and n_installation according to number of clusters
    clusters = aggregate_clusters(df_number_clusters)

    # Scale up to match real national total (see README: known limitation on ground-mounted vs rooftop mix)
    clusters["installed_capacity"] *= target_total_capacity_wind_on_shore / clusters["installed_capacity"].sum()


    lat_list = clusters["latitude"].tolist()
    lon_list = clusters["longitude"].tolist()

    
    # create string and separate by comma
    lat_string = ",".join(str(x) for x in lat_list)
    lon_string = ",".join(str(x) for x in lon_list)

    if len(lat_string) > 2000 or len(lon_string) > 2000:
        lat_string = ",".join(f"{x:.3f}" for x in lat_list)
        lon_string = ",".join(f"{x:.3f}" for x in lon_list)


    weather_list = fetch_weather_batch(lat_string, lon_string)

    return clusters, weather_list


# Wind Onshore

def compute_wind_on_shore_production_series(clusters_df, weather_list, wind_on_shore_instances, hours_of_forecasting):
    results = []

    for date_and_time, row in hours_of_forecasting.iterrows():
        current_time = row["time"]
        total_production_this_hour = 0

        for i, cluster_row in clusters_df.iterrows():
           weather_at_this_cluster = weather_list[i]
           matching_row = weather_at_this_cluster[weather_at_this_cluster["time"] == current_time]
           temperature_now = matching_row.iloc[0]["temperature"]
           wind_speed_100m_now = matching_row.iloc[0]["wind_speed_100m"]


           wind_on_shore_instances[i].set_weather(wind_speed_100m_now, temperature_now)
           total_production_this_hour += wind_on_shore_instances[i].actual_capacity_mw()

        results.append({"time": current_time, "wind_onshore_production": total_production_this_hour})

    return pd.DataFrame(results)



# Wind Offshore  

def prepare_wind_off_shore_clusters(coordinates_df, n_clusters):

    # Fetch total Wind Offshore capacity DE-LU
    wind_off_shore_capacity_DE_LU = fetch_installed_capacity_zone(zone,start,end)
    # Extract value 
    target_total_capacity_wind_off_shore = wind_off_shore_capacity_DE_LU["Wind Offshore"].iloc[0]

    # Defines number of clusters
    df_number_clusters, kmean_number_clusters = cluster_installations(coordinates_df.copy(), n_clusters)

    # aggregate_clusters() calculate latitude,longitude,installed capacity and n_installation according to number of clusters
    clusters = aggregate_clusters(df_number_clusters)

    # Scale up to match real national total (see README: known limitation on ground-mounted vs rooftop mix)
    clusters["installed_capacity"] *= target_total_capacity_wind_off_shore / clusters["installed_capacity"].sum()


    lat_list = clusters["latitude"].tolist()
    lon_list = clusters["longitude"].tolist()

    
    # create string and separate by comma
    lat_string = ",".join(str(x) for x in lat_list)
    lon_string = ",".join(str(x) for x in lon_list)

    if len(lat_string) > 2000 or len(lon_string) > 2000:
        lat_string = ",".join(f"{x:.3f}" for x in lat_list)
        lon_string = ",".join(f"{x:.3f}" for x in lon_list)


    weather_list = fetch_weather_batch(lat_string, lon_string)

    return clusters, weather_list


# Wind Offshore  

def compute_wind_off_shore_production_series(clusters_df, weather_list, wind_off_shore_instances, hours_of_forecasting):
    results = []

    for date_and_time, row in hours_of_forecasting.iterrows():
        current_time = row["time"]
        total_production_this_hour = 0

        for i, cluster_row in clusters_df.iterrows():
           weather_at_this_cluster = weather_list[i]
           matching_row = weather_at_this_cluster[weather_at_this_cluster["time"] == current_time]
           temperature_now = matching_row.iloc[0]["temperature"]
           wind_speed_100m_now = matching_row.iloc[0]["wind_speed_100m"]


           wind_off_shore_instances[i].set_weather(wind_speed_100m_now, temperature_now)
           total_production_this_hour += wind_off_shore_instances[i].actual_capacity_mw()

        results.append({"time": current_time, "wind_offshore_production": total_production_this_hour})

    return pd.DataFrame(results)