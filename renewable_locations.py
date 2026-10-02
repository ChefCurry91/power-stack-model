import pandas as pd
from sklearn.cluster import KMeans


#solar_file = "data/csv/Solar_Energy_V20240104.csv"

def load_installations(csv_path, extra_columns=None):
    # load entire CSV file in DataFrame
    df = pd.read_csv(csv_path, sep=";")
    # Only select specific columns
    df = df[["x_coordinates", "y_coordinates", "installed_capacity", "location"]]

    if extra_columns:
            columns += extra_columns
    df = df[columns]

    # Dataset capacity is reported in kW -> convert to MW
    df["installed_capacity"] = df["installed_capacity"] / 1000


    return df



def load_installations(csv_path, extra_columns=None):
    df = pd.read_csv(csv_path, sep=";")
    columns = ["x_coordinates", "y_coordinates", "installed_capacity", "location"]
    
    if extra_columns:
        columns += extra_columns
    df = df[columns]
    df["installed_capacity"] = df["installed_capacity"] / 1000
    return df














