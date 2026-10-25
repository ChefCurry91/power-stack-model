import os
import pandas as pd
from datetime import datetime

def fetch_gas_price():
    local_file = "data/TTF_NGP_60_Days.csv"
    url = "https://gasandregistry.eex.com/Gas/NGP/TTF_NGP_60_Days.csv"

    need_download = True

    # Check whether the CSV already exists in the local data/ folder
    if os.path.exists(local_file):
        # Load the locally cached CSV and check its first row's date —
        # this tells us how "fresh" the cached data is, without hitting the network
        existing_df = pd.read_csv(local_file, sep=";")

        # Take the value from row 0 of the "Delivery date" column
        # (the most recent trading day in the file) and convert it
        # from a string into a pandas Timestamp.

        first_row_date = pd.to_datetime(existing_df.iloc[0]["Delivery date"])
        # 2026-09-20 00:00:00
    

        today = datetime.now() # 2026-09-20 14:37:25.123456
        today_pd_format = pd.Timestamp.now().normalize()  # 2026-09-20 00:00:00

        yesterday = pd.Timestamp.now().normalize() - pd.Timedelta(days=1)
        # e.g 2026-09-20 00:00:00

        if first_row_date >= yesterday:
            need_download = False



    if need_download:
        # Cache is missing or outdated (not today) — fetch the latest file from EEX
        # and overwrite the local copy, so next run can reuse it without re-downloading
        gas_price_df = pd.read_csv(url, sep=";")
        gas_price_df.to_csv(local_file, sep=";", index=False)
        print('télecharger')



    else:
        gas_price_df = existing_df

    latest_price = gas_price_df.iloc[0]["Index Value (€/MWh)"]
    
    
    return latest_price



def load_gas_csv():
    local_file = "data/TTF_NGP_60_Days.csv"
    url = "https://gasandregistry.eex.com/Gas/NGP/TTF_NGP_60_Days.csv"

    need_download = True

    if os.path.exists(local_file):
        existing_df = pd.read_csv(local_file, sep=";")
        latest_date = pd.to_datetime(existing_df["Delivery date"]).max()
        yesterday = pd.Timestamp.now().normalize() - pd.Timedelta(days=1)
        if latest_date >= yesterday:
            need_download = False

    if need_download:
        gas_price_df = pd.read_csv(url, sep=";")
        gas_price_df.to_csv(local_file, sep=";", index=False)
    else:
        gas_price_df = existing_df

    return gas_price_df



def load_gas_price_history():
    df = load_gas_csv()[["Delivery date", "Index Value (€/MWh)"]].copy()
    df.columns = ["date", "gas_price"]
    df["date"] = pd.to_datetime(df["date"])
    return df.sort_values("date").reset_index(drop=True)

# returns DF, contains two columns: date and respective gas price of the last 59 days


def fetch_gas_price():
    return load_gas_price_history().iloc[-1]["gas_price"]

# return most recent gas price

print(load_gas_price_history()["date"].min(), load_gas_price_history()["date"].max())



### C02 price: 

def load_co2_excel():
    local_file = "data/emission-spot-primary-market-auction-report-2026-data.xlsx"
    url = "https://public.eex-group.com/eex/eua-auction-report/emission-spot-primary-market-auction-report-2026-data.xlsx"

    need_download = True

    if os.path.exists(local_file):
        file_date = pd.Timestamp(os.path.getmtime(local_file), unit="s").normalize()
        if pd.Timestamp.now().normalize() <= file_date:
            need_download = False   # fichier déjà téléchargé aujourd'hui

    if need_download:
        co2_price_df = pd.read_excel(url, header=5)
        co2_price_df.to_excel(local_file, index=False)
    else:
        co2_price_df = pd.read_excel(local_file)

    return co2_price_df
# returns data from excel file with date, time, Auction names, countries and price



def load_co2_price_history():
    df = load_co2_excel()[["Date", "Auction Price €/tCO2"]].dropna()
    df.columns = ["date", "co2_price"]
    df["date"] = pd.to_datetime(df["date"]).dt.normalize()

    # plusieurs enchères le même jour -> on fait la moyenne
    df = df.groupby("date", as_index=False)["co2_price"].mean()

    # une ligne par jour calendaire, le dernier prix connu est reporté
    full_range = pd.date_range(df["date"].min(), pd.Timestamp.now().normalize(), freq="D")
    df = df.set_index("date").reindex(full_range).ffill().rename_axis("date").reset_index()
    return df
# return DF with columns date and price





def fetch_c02_price():
    local_file = "data/emission-spot-primary-market-auction-report-2026-data.xlsx"
    url = "https://public.eex-group.com/eex/eua-auction-report/emission-spot-primary-market-auction-report-2026-data.xlsx"


    if os.path.exists(local_file):

        current_date = pd.Timestamp.now().normalize()

        file_date = pd.Timestamp(
            os.path.getmtime(local_file),
            unit="s").normalize()

        if current_date > file_date:
            # download file EEX
            co2_price_df = pd.read_excel(url, header=5)

            # save locally
            co2_price_df.to_excel(local_file, index=False)

        else:
            # use existing local file
            co2_price_df = pd.read_excel(local_file)


    else:
        co2_price_df = pd.read_excel(url, header=5)
        # save localy
        co2_price_df.to_excel(local_file, index=False)


    co2_price = co2_price_df.iloc[0]["Auction Price €/tCO2"]

    return co2_price
