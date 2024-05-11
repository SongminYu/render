import random
from typing import Optional
from typing import TYPE_CHECKING

from models.render_building.building_key import BuildingKey
from models.render_building.tech import EnergyIntensity
from utils.funcs import dict_normalize, dict_utility_sample

if TYPE_CHECKING:
    from models.render_building.scenario import BuildingScenario


class VentilationSystem:

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
            dimension_name="id_ventilation_technology",
            dimension_ids=self.scenario.ventilation_technologies.keys(),
            rdict=self.scenario.s_ventilation_technology_market_share
        )

    def init_efficiency_class(self):
        self.rkey.init_dimension(
            dimension_name="id_ventilation_technology_efficiency_class",
            dimension_ids=self.scenario.r_ventilation_technology_efficiency_class.get_item(self.rkey),
            rdict=self.scenario.s_ventilation_technology_efficiency_class_market_share
        )

    def init_installation_year(self):
        lifetime = self.get_lifetime()
        age = random.randint(0, lifetime)
        self.installation_year = self.rkey.year - age
        self.next_replace_year = self.rkey.year + lifetime - age

    def get_lifetime(self):
        return random.randint(
            self.scenario.p_ventilation_technology_lifetime_min.get_item(self.rkey),
            self.scenario.p_ventilation_technology_lifetime_max.get_item(self.rkey)
        )

    def update_energy_intensity(self):
        self.energy_intensity = EnergyIntensity(
            id_end_use=5,
            id_energy_carrier=self.scenario.r_ventilation_technology_energy_carrier.get_item(self.rkey)[0],
            value=self.scenario.p_ventilation_technology_energy_intensity.get_item(self.rkey)
        )

    def select(self, total_living_area: float):
        rkey = self.rkey.make_copy()
        d_option_cost = {}
        for id_ventilation_technology in self.scenario.ventilation_technologies.keys():
            rkey.id_ventilation_technology = id_ventilation_technology
            for id_ventilation_technology_efficiency_class in self.scenario.r_ventilation_technology_efficiency_class.get_item(rkey):
                rkey.id_ventilation_technology_efficiency_class = id_ventilation_technology_efficiency_class
                if self.scenario.s_ventilation_technology_availability.get_item(rkey):
                    capex = self.scenario.ventilation_technology_capex.get_item(rkey) * total_living_area
                    opex = self.scenario.ventilation_technology_opex.get_item(rkey) * total_living_area
                    d_option_cost[(id_ventilation_technology, id_ventilation_technology_efficiency_class)] = capex + opex
        self.rkey.id_ventilation_technology, self.rkey.id_ventilation_technology_efficiency_class = dict_utility_sample(
            options=dict_normalize(d_option_cost),
            utility_power=self.scenario.s_ventilation_technology_utility_power.get_item(rkey)
        )

    def install(self):
        self.is_adopted = True
        self.update_energy_intensity()
        self.installation_year = self.rkey.year
        self.next_replace_year = self.rkey.year + self.get_lifetime()

