import random
from typing import TYPE_CHECKING

from utils.funcs import dict_sample
from models.render_building.building_key import BuildingKey

if TYPE_CHECKING:
    from models.render_building.scenario import BuildingScenario


class BuildingComponent:

    def __init__(self, rkey: "BuildingKey", scenario: "BuildingScenario"):
        self.rkey = rkey
        self.scenario = scenario
        self.name = ""
        self.construction_year = 0
        self.installation_year = 0
        self.next_replace_year = 0

    def init_name(self):
        self.name = self.scenario.building_components.get_item(self.rkey)

    def init_option(self):
        self.rkey.init_dimension(
            dimension_name="id_building_component_option",
            dimension_ids=self.scenario.r_building_component_option.get_item(self.rkey),
            rdict=self.scenario.s_building_component_option
        )

    def init_area(self, ref_area, ratio):
        self.area = ref_area * ratio

    def construct(self):
        self.construction_year = random.randint(
            self.scenario.p_building_construction_year_min.get_item(self.rkey),
            self.scenario.p_building_construction_year_max.get_item(self.rkey)
        )
        self.installation_year = self.construction_year
        self.next_replace_year = self.construction_year + self.get_lifetime()
        self.set_efficiency(action_year=self.construction_year, id_action=1)

    def renovate(self, action_year: int):
        minimum_lifetime = self.scenario.p_building_component_minimum_lifetime.get_item(self.rkey)
        # this minimum_lifetime should be no longer than the possible shortest lifetime
        if action_year - self.installation_year >= minimum_lifetime:
            self.installation_year = action_year
            self.next_replace_year = action_year + self.get_lifetime()
            self.set_efficiency(action_year=action_year, id_action=2)
            rkey = self.rkey.make_copy().set_id({"year": action_year})
            self.scenario.renovation_action_building.accumulate_item(rkey=rkey, value=1)
            self.scenario.renovation_action_component.accumulate_item(rkey=rkey, value=1)

    def set_efficiency(self, action_year: int, id_action: int):
        rkey = self.rkey.make_copy()
        rkey.year, rkey.id_action = action_year, id_action
        d = {}
        for id_building_component_option_efficiency_class in self.scenario.building_component_option_efficiency_classes.keys():
            rkey.id_building_component_option_efficiency_class = id_building_component_option_efficiency_class
            d[id_building_component_option_efficiency_class] = self.scenario.s_building_component_availability.get_item(rkey)
        self.rkey.id_building_component_option_efficiency_class = dict_sample(d)
        self.u_value = self.scenario.p_building_component_efficiency.get_item(self.rkey)

    def get_lifetime(self):
        df = self.rkey.filter_dataframe(self.scenario.p_building_component_lifetime)
        d = {}
        for index, row in df.iterrows():
            d[(row["min"], row["max"])] = row["pdf"]
        lifetime_min, lifetime_max = dict_sample(d)
        return random.randint(lifetime_min, lifetime_max)

