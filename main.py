from plant import Plant,Gas, Nuclear, Wind, Solar
from market import Market
from datetime import datetime
from weather import fetch_weather



# initialize instance Gaz

gaz = Gas(
    name="CCGT_gaz", 
    capacity_mw=13000, 
    country="Germany",
    fuel_price=30, 
    efficiency=0.5, 
    emission_factor=0.2,
    )

# initialize instance Nuclear

nuclear = Nuclear(
        name="Benznau_nuclear",
        capacity_mw = 30000,
        country="Switzerland",
        fuel_price = 20,
        efficiency = 1,
        emission_factor = 0
    )


# initialize instance Wind

wind = Wind(name = 'Wind_farm_1', capacity_mw=22000, country="Germany")

# initialize instance Solar

solar = Solar(name='Park_1',capacity_mw=20000, country="Germany")

#print('hello')


# initialize instance Wind

list_plants = [gaz, nuclear, solar, wind]
market = Market(list_plants)





# Fetch full 168h (7-day) forecast for Berlin: wind speed at 100m and solar irradiance,
# one value per hour, starting at midnight (00:00) of today.
wind_speed_list, irradiance_list, temperature_2m_list = fetch_weather(52.52, 13.41)


# Get the current real-world hour (0-23), to know where "now" falls
# within the 168h series returned by the API (which always starts at midnight).
current_time = datetime.now()
current_hour = current_time.hour

# Define the slice boundaries: from the current hour, 24 hours ahead.
index_next_24_hours = current_hour
end_of_24_hours = index_next_24_hours + 24


# Slice out just the next 24 hours of wind speed and irradiance, starting from now,
# instead of using the full 7-day series.
list_wind_speed_next_24_hours = wind_speed_list[index_next_24_hours:end_of_24_hours]
list_irradiance_next_24_hours = irradiance_list[index_next_24_hours:end_of_24_hours]
list_temperature_2m_next_24_hours = temperature_2m_list[index_next_24_hours:end_of_24_hours]
#print('hello')
#print(list_temperature_2m_next_24_hours)


# For each of the next 24 hours, run the market clearing with that hour's real
# wind speed and irradiance, to see how the price evolves as weather conditions change.
for i, speed in enumerate(list_wind_speed_next_24_hours):
     irradiance_hour = list_irradiance_next_24_hours[i]
     temperature_hour = list_temperature_2m_next_24_hours[i]
     price = market.clear(demand_capacity=30000, c02_price=80, wind_speed=speed, temperature =temperature_hour, irradiance=irradiance_hour)
     print(f"Hour {i}: vent={speed:.1f}, temperature={temperature_hour:.0f}, irradiance={irradiance_hour:.0f} → Price={price}")