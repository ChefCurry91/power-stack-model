class Plant():

    def __init__(self, name, capacity_mw, country):

        # Un attribut reste dans Plant (le parent) si toutes les technologies en ont besoin, 
        # sous la même forme. Un attribut irait plutôt dans une classe fille si :

        self.name = name
        self.capacity_mw= capacity_mw
        self.country = country



        # Un attribut irait plutôt dans une classe fille si :
        # seule cette techno en a besoin (les autres n'en ont pas l'usage du tout)


class Gas(Plant):

    def __init__(self, name, capacity_mw, country, fuel_price, efficiency, emission_factor):
        super().__init__(name, capacity_mw, country)
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


class Nuclear(Plant):

    def __init__(self, name, capacity_mw, country, fuel_price, efficiency, emission_factor):
        super().__init__(name, capacity_mw, country)
        self.fuel_price = fuel_price
        self.efficiency = efficiency
        self.emission_factor = emission_factor


    def marginal_cost(self,c02_price):

        marginal_cost = self.fuel_price/self.efficiency + (self.emission_factor * c02_price) / self.efficiency

        return marginal_cost


class Wind(Plant):
    def __init__(self, name, capacity_mw, country, cut_in=12, rated=55, cut_out=90):
        super().__init__(name,capacity_mw, country)
        self.cut_in = cut_in
        self.rated = rated
        self.cut_out = cut_out



    def actual_capacity_mw(self, wind_speed):

        current_cappacity_mw = 0

        if wind_speed < self.cut_in:
            return 0
        # formule cubique, qui donne une valeur progressive — proche de 0 juste après cut_in, 
        # et qui monte jusqu'à approcher capacity_mw quand wind_speed s'approche de rated. 
        # Ce n'est pas le maximum constant, c'est une valeur qui change selon wind_speed, 
        # dans cette plage précise.
        elif self.cut_in < wind_speed < self.rated:
            current_cappacity_mw = self.capacity_mw * (wind_speed**3 - self.cut_in**3) / (self.rated**3 - self.cut_in**3)
        elif self.rated < wind_speed < self.cut_out:
            return self.capacity_mw
        elif wind_speed > self.cut_out:
            return 0

        return current_cappacity_mw

    def marginal_cost(self, c02_price):
        return 0