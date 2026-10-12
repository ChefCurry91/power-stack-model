import pandas as pd

def load_installations(csv_path, extra_columns=None):
    df = pd.read_csv(csv_path, sep=";")
    columns = ["x_coordinates", "y_coordinates", "installed_capacity", "location"]
    
    if extra_columns:
        columns += extra_columns
    df = df[columns]
    df["installed_capacity"] = df["installed_capacity"] / 1000
    return df














