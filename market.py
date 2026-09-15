from plant import Plant
from weather import fetch_weather




class Market():

    def __init__(self, plants):
        self.plants = plants

   # def merit_order_stack(self, c02_price):
    def merit_order_stack(self, c02_price, wind_speed, irradiance):

        #key=lambda p: p.marginal_cost() se lit en trois morceaux :

        # key= : le paramètre de sorted() qui dit "voici comment comparer les éléments"
        # lambda p: : "je définis une petite fonction anonyme, qui prend un argument que j'appelle p"
        # p.marginal_cost() : "et retourne, pour cet argument p, la valeur de son coût marginal"


        sorted_plants = sorted(self.plants, key=lambda p: p.marginal_cost(c02_price))


        total = 0
        cumuls = []

        for element in sorted_plants:
            total += element.available_capacity_mw(wind_speed=wind_speed, irradiance=irradiance)
            cumuls.append(total)

        return sorted_plants, cumuls

    def clear(self, demand_capacity,c02_price, wind_speed, irradiance):
        sorted_plants, cumuls = self.merit_order_stack(c02_price, wind_speed, irradiance)
        

        i = 0

        while i < len(cumuls) and cumuls[i] < demand_capacity :
            i += 1

        if i >= len(cumuls):
            return "SHORTAGE"

        else: price = sorted_plants[i].marginal_cost(c02_price)

        return price
