from plant import Plant,Gas, Nuclear, Wind
from market import Market

# initialize instance Gaz

gaz = Gas(
    name="CCGT_gaz", 
    capacity_mw=13000, 
    country="Germany",
    fuel_price=30, 
    efficiency=0.5, 
    emission_factor=0.2
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


# initialize instance Wind

list_plants = [gaz, nuclear,wind]
market = Market(list_plants)

print(market.clear(demand_capacity=30000, c02_price=80))
