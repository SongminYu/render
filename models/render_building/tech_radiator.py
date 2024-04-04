import random
from typing import TYPE_CHECKING

from models.render_building.building_key import BuildingKey
from utils.funcs import dict_normalize, dict_utility_sample

if TYPE_CHECKING:
    from models.render_building.scenario import BuildingScenario


class Radiator:

    def __init__(self, rkey: "BuildingKey", scenario: "BuildingScenario"):
        self.rkey = rkey
        self.scenario = scenario
        self.installation_year = 0
        self.next_replace_year = 0

    def init_option(self):
        self.rkey.init_dimension(
            dimension_name="id_radiator",
            dimension_ids=self.scenario.radiators.keys(),
            rdict=self.scenario.s_radiator
        )

    def init_installation_year(self):
        lifetime = self.get_lifetime()
        age = random.randint(0, lifetime)
        self.installation_year = self.rkey.year - age
        self.next_replace_year = self.rkey.year + lifetime - age

    def get_lifetime(self):
        return random.randint(
            self.scenario.p_radiator_lifetime_min.get_item(self.rkey),
            self.scenario.p_radiator_lifetime_max.get_item(self.rkey)
        )

    def select(self, id_building_action: int):
        rkey = self.rkey.make_copy().set_id({"id_building_action": id_building_action})
        d_option_cost = {}
        for id_radiator in self.scenario.radiators.keys():
            rkey.id_radiator = id_radiator
            if self.scenario.s_radiator_availability.get_item(rkey):
                capex = self.scenario.radiator_capex.get_item(rkey)
                d_option_cost[id_radiator] = capex
        self.rkey.id_radiator = dict_utility_sample(
            options=dict_normalize(d_option_cost),
            utility_power=self.scenario.s_radiator_utility_power.get_item(rkey)
        )

    def install(self):
        self.installation_year = self.rkey.year
        self.next_replace_year = self.rkey.year + self.get_lifetime()

