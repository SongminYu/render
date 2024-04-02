import random
from typing import Optional
from typing import TYPE_CHECKING

from models.render_building.building_key import BuildingKey
from models.render_building.tech import EnergyIntensity
from utils.funcs import dict_sample

if TYPE_CHECKING:
    from models.render_building.scenario import BuildingScenario


class CoolingSystem:

    def __init__(self, rkey: "BuildingKey", scenario: "BuildingScenario"):
        self.rkey = rkey
        self.scenario = scenario
        self.is_adopted = False
        self.installation_year = 0
        self.next_replace_year = 0
        self.energy_intensity: Optional["EnergyIntensity"] = None

    def init_adoption(self):
        self.is_adopted = True
        self.init_option()
        self.init_efficiency_class()
        self.init_installation_year()
        self.update_energy_intensity()

    def init_option(self):
        self.rkey.init_dimension(
            dimension_name="id_cooling_technology",
            dimension_ids=self.scenario.cooling_technologies.keys(),
            rdict=self.scenario.s_cooling_technology_market_share
        )

    def init_efficiency_class(self):
        self.rkey.init_dimension(
            dimension_name="id_cooling_technology_efficiency_class",
            dimension_ids=self.scenario.r_cooling_technology_efficiency_class.get_item(self.rkey),
            rdict=self.scenario.s_cooling_technology_efficiency_class_market_share
        )

    def init_installation_year(self):
        lifetime = self.get_lifetime()
        age = random.randint(0, lifetime)
        self.installation_year = self.rkey.year - age
        self.next_replace_year = self.rkey.year + lifetime - age

    def get_lifetime(self):
        return random.randint(
            self.scenario.p_cooling_technology_lifetime_min.get_item(self.rkey),
            self.scenario.p_cooling_technology_lifetime_max.get_item(self.rkey)
        )

    def update_energy_intensity(self):
        self.energy_intensity = EnergyIntensity(
            id_end_use=2,
            id_energy_carrier=self.scenario.r_cooling_technology_energy_carrier.get_item(self.rkey)[0],
            value=1 / self.scenario.p_cooling_technology_efficiency.get_item(self.rkey)
        )

    def adopt(self, adoption_prob: float, cooling_demand_peak: float, cooling_demand: float):
        if random.uniform(0, 1) <= adoption_prob:
            id_cooling_technology, id_cooling_technology_efficiency_class = self.select(
                cooling_demand_peak=cooling_demand_peak,
                cooling_demand=cooling_demand
            )
            self.install(id_cooling_technology, id_cooling_technology_efficiency_class)

    def replace(self, cooling_demand_peak: float, cooling_demand: float):
        if self.rkey.year == self.next_replace_year:
            id_cooling_technology, id_cooling_technology_efficiency_class = self.select(
                cooling_demand_peak=cooling_demand_peak,
                cooling_demand=cooling_demand
            )
            self.install(id_cooling_technology, id_cooling_technology_efficiency_class)

    def select(self, cooling_demand_peak: float, cooling_demand: float):
        rkey = self.rkey.make_copy()
        d = {}
        for id_cooling_technology in self.scenario.cooling_technologies.keys():
            rkey.id_cooling_technology = id_cooling_technology
            for id_cooling_technology_efficiency_class in self.scenario.r_cooling_technology_efficiency_class.get_item(rkey):
                rkey.id_cooling_technology_efficiency_class = id_cooling_technology_efficiency_class
                if self.scenario.s_cooling_technology_availability.get_item(rkey):
                    capex = self.scenario.cooling_technology_capex.get_item(rkey) * cooling_demand_peak
                    opex = self.scenario.cooling_technology_opex.get_item(rkey) * cooling_demand
                    utility = (capex + opex) ** (- self.scenario.s_cooling_technology_utility_power.get_item(rkey))
                    d[(id_cooling_technology, id_cooling_technology_efficiency_class)] = utility
        return dict_sample(d)

    def install(self, id_cooling_technology, id_cooling_technology_efficiency_class):
        self.rkey.id_cooling_technology = id_cooling_technology
        self.rkey.id_cooling_technology_efficiency_class = id_cooling_technology_efficiency_class
        self.update_energy_intensity()
        self.installation_year = self.rkey.year
        self.next_replace_year = self.rkey.year + self.get_lifetime()
