import random 


class Plant():

    def __init__(self, name, capacity_mw, country, availability=1.0):

        # Un attribut reste dans Plant (le parent) si toutes les technologies en ont besoin, 
        # sous la même forme. Un attribut irait plutôt dans une classe fille si :

        self.name = name
        self.capacity_mw= capacity_mw
        self.country = country
        self.availability = availability


    # define weather Plant is available to be run
    def is_available(self):
        random_number = random.random()

        if random_number < self.availability:
            return True
        else:
            return False


    def available_capacity_mw(self):
        if self.is_available():
            return self.capacity_mw
        else:
            return 0





# Un attribut irait plutôt dans une classe fille si :
# seule cette techno en a besoin (les autres n'en ont pas l'usage du tout)


### Class Gas


class Gas(Plant):

    def __init__(self, name, capacity_mw, country, fuel_price, efficiency, emission_factor, availability = 0.93):
        super().__init__(name, capacity_mw, country, availability)
        self.fuel_price = fuel_price
        self.efficiency = efficiency
        self.emission_factor = emission_factor


    def marginal_cost(self, c02_price):

        # diviser le prix (EUR/MWh thermique) par le rendement donne le coût en EUR/MWh électrique
        # emission_factor : c'est une quantité physique, en tonnes de CO2 émises par MWh thermique brûlée
        # c02_price : c'est le prix du marché carbone, en EUR par tonne de CO2

        marginal_cost = self.fuel_price/self.efficiency + (self.emission_factor * c02_price) / self.efficiency

        # emission_factor * c02_price = (tonnes/MWh) × (EUR/tonne) = EUR par MWh thermique — c'est le coût du CO2 pour chaque MWh thermique brûlé.

        return marginal_cost 


### Class Nuclear


class Nuclear(Plant):

    def __init__(self, name, capacity_mw, country, fuel_price, efficiency, emission_factor, availability=0.8):
        super().__init__(name, capacity_mw, country,availability)
        self.fuel_price = fuel_price
        self.efficiency = efficiency
        self.emission_factor = emission_factor


    def marginal_cost(self,c02_price):

        marginal_cost = self.fuel_price/self.efficiency + (self.emission_factor * c02_price) / self.efficiency

        return marginal_cost



### Class Wind


class Wind(Plant):
    def __init__(self, name, capacity_mw, country, availability = 0.99, cut_in=12, rated=55, cut_out=90, wind_speed=0,temperature =0, hub_height=100):
        super().__init__(name,capacity_mw, country, availability)
        self.cut_in = cut_in
        self.rated = rated
        self.cut_out = cut_out
        self.wind_speed = wind_speed
        self.temperature = temperature
        self.hub_height = hub_height

    def set_weather(self, wind_speed, temperature):

        # Meant to be called once per cluster per hour, right before actual_capacity_mw(), so this instance always
        # reflects the current time/cluster's weather condition.

        self.wind_speed = wind_speed
        self.temperature = temperature




    # provide how much capacity is currently produced

    def actual_capacity_mw(self):

        # Check if wind farm is available to be run
        current_availability = self.is_available() 



        # ρ = P / (R × T)  — the ideal gas law, rearranged to solve for density (ρ)
        # 101325 = standard atmospheric pressure at sea level, in Pascals (P)
        #  287.05 = specific gas constant for dry air, in J/(kg·K) (R) — a fixed physical constant
        #   T  = temperature in Kelvin (must convert from Celsius: + 273.15)


        current_density = 101325 / (287.05 * (self.temperature + 273.15))

        # ratio_density: how today's actual air density compares to the standard
        # reference density (1.225 kg/m^3). Below 1.0 on a hot day (less dense air, less power), 
        # above 1.0 on a cold day (denser air, more power).

        ratio_density = current_density / 1.225

        # Air density correction: wind turbine power output is directly proportional
        # to air density (not just wind speed). Manufacturers rate turbines assuming
        # a standard reference density of 1.225 kg/m^3 (sea level, 15°C). On a hot day,
        # air is thinner (lower density) and the turbine produces less than the rated
        # curve suggests, even at the same wind speed; on a cold day, denser air means
        # slightly more output.


        corrected_wind_speed = self.wind_speed * (self.hub_height / 100) ** 0.143

        # Hellmann power law: wind_speed is measured at 100m, but each turbine sits at its own
        # hub_height. v_hub = v_100m * (hub_height / 100)^alpha, alpha = 0.143 for onshore.
        # Stored as a local variable — never overwrites self.wind_speed (the raw measured value),
        # so repeated calls to actual_capacity_mw() without a new set_weather() stay correct.
        corrected_wind_speed = self.wind_speed * (self.hub_height / 100) ** 0.143



        # initialize current MWH capacity


        if not current_availability:
            return 0

        if corrected_wind_speed < self.cut_in:
            return 0
        elif self.cut_in < corrected_wind_speed < self.rated:
            current_capacity_mw = (self.capacity_mw * (corrected_wind_speed**3 - self.cut_in**3)
                                    / (self.rated**3 - self.cut_in**3)) * ratio_density
            return current_capacity_mw
        elif self.rated < corrected_wind_speed < self.cut_out:
            return self.capacity_mw * ratio_density
        elif corrected_wind_speed > self.cut_out:
            return 0


    def available_capacity_mw(self): 
        return self.actual_capacity_mw() 


    def marginal_cost(self, c02_price):
        return 0


        
### Class Solar


class Solar(Plant):
    def __init__(self,name, capacity_mw, country, availability = 0.99, irradiance=0):
        super().__init__(name, capacity_mw, country, availability)
        self.irradiance = irradiance





    def set_weather(self, irradiance):

        # Meant to be called once per cluster per hour, right before actual_capacity_mw(), so this instance always
        # reflects the current time/cluster's weather condition.

        self.irradiance = irradiance


    def actual_capacity_mw(self, irradiance_max=1000):

        # Check if solar park is available to be "run"
        current_availability = self.is_available()


        if not current_availability:
            return 0


        else:

            # irradiance: amount of sunlight energy hitting a surface, expressed as a rate (per second)
            # -> that rate is what we call power, measured in W/m^2 (0 at night, up to ~1000 in full sun)
            # capacity_factor: fraction (0 to 1) of installed capacity actually usable right now
  
            capacity_factor = min(self.irradiance / irradiance_max, 1)

            # self.capacity_mw is fixed (this cluster's installed capacity, doesn't change over time).
            # capacity_factor varies with weather. The result below is what actually changes per hour:
            # this cluster's real production at the current time, given its currently stored irradiance.

            return self.capacity_mw * capacity_factor


    def available_capacity_mw(self): 
        return self.actual_capacity_mw()



    def marginal_cost(self, c02_price):
        return 0

#https://www.pv-tech.org/germany-passes-100gw-of-installed-solar-pv/?utm_source=chatgpt.com
