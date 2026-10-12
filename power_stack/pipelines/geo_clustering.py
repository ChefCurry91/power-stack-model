from sklearn.cluster import KMeans




# Assign each installation to a geographical cluster

def cluster_installations(df, n_clusters):

    coordinates = df[["x_coordinates", "y_coordinates"]]
    kmeans = KMeans(n_clusters=n_clusters, 
                    random_state=42, 
                    n_init="auto")
    df["cluster"] = kmeans.fit_predict(coordinates)

    return df, kmeans

# Aggregate information at cluster level.
# For each cluster compute:
# - mean latitude and longitude (cluster centroid)
# - total installed capacity (MW)
# - number of installations
#
# The centroid coordinates will later be used to retrieve
# weather data (irradiance, wind speed, temperature) and
# estimate available renewable generation.



def aggregate_clusters(df):
    agg_dict = {
        "latitude": ("y_coordinates", "mean"),
        "longitude": ("x_coordinates", "mean"),
        "installed_capacity": ("installed_capacity", "sum"),
        "n_installations": ("cluster", "size")
    }
    
    if "hub_height" in df.columns:
        agg_dict["hub_height"] = ("hub_height", "mean")
    
    clusters = df.groupby("cluster").agg(**agg_dict).reset_index()
    return clusters




