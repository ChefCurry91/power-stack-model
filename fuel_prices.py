import os
import pandas as pd
from datetime import datetime

def fetch_gas_price():
    local_file = "data/TTF_NGP_60_Days.csv"
    url = "https://gasandregistry.eex.com/Gas/NGP/TTF_NGP_60_Days.csv"

    need_download = True

    if os.path.exists(local_file):
        # Load the locally cached CSV and check its first row's date —
        # this tells us how "fresh" the cached data is, without hitting the network
        existing_df = pd.read_csv(local_file, sep=";")
        print(existing_df.columns.tolist())
        print(existing_df.iloc[0])
        first_row_date = pd.to_datetime(existing_df.iloc[0]["Delivery date"])
    

        today = datetime.now()
        today_pd_format = pd.Timestamp.now().normalize()  # today, without hour

        if today.weekday() >= 5:
            need_download = False  # 5 = samedi, 6 = dimanch


        elif  first_row_date == today_pd_format:
            need_download = False



    if need_download:
        # Cache is missing or outdated (not today) — fetch the latest file from EEX
        # and overwrite the local copy, so next run can reuse it without re-downloading
        gas_price_df = pd.read_csv(url, sep=";")
        gas_price_df.to_csv(local_file, sep=";", index=False)
    else:
        gas_price_df = existing_df

    latest_price = gas_price_df.iloc[0]["Index Value (€/MWh)"]
    return latest_price

