import random
from typing import TYPE_CHECKING, Optional

from models.render_building.building_key import BuildingKey
from models.render_building import cons
from utils.funcs import dict_sample

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

    def get_lifetime(self):
        df = self.rkey.filter_dataframe(self.scenario.p_building_component_lifetime)
        d = {}
        for index, row in df.iterrows():
            d[(row["min"], row["max"])] = row["pdf"]
        lifetime_min, lifetime_max = dict_sample(d)
        return random.randint(lifetime_min, lifetime_max)

    def init_construction(self, building_construction_year):
        self.construction_year = building_construction_year
        self.installation_year = building_construction_year
        self.next_replace_year = building_construction_year + self.get_lifetime()
        self.historical_random_select(
            action_year=building_construction_year,
            id_building_action=cons.ID_BUILDING_ACTION_CONSTRUCTION
        )

    def init_historical_renovation(self, action_year: int):
        minimum_lifetime = self.scenario.p_building_component_minimum_lifetime.get_item(self.rkey)
        # this minimum_lifetime should be no longer than the possible shortest lifetime
        if action_year - self.installation_year >= minimum_lifetime:
            self.installation_year = action_year
            self.next_replace_year = action_year + self.get_lifetime()
            self.historical_random_select(action_year=action_year, id_building_action=cons.ID_BUILDING_ACTION_RENOVATION)

    def historical_random_select(self, action_year: int, id_building_action: int):
        rkey = self.rkey.make_copy()
        rkey.year, rkey.id_building_action = action_year, id_building_action
        d = {}
        for id_building_component_option_efficiency_class in self.scenario.building_component_option_efficiency_classes.keys():
            rkey.id_building_component_option_efficiency_class = id_building_component_option_efficiency_class
            d[id_building_component_option_efficiency_class] = self.scenario.s_building_component_availability.get_item(rkey)
        self.rkey.id_building_component_option_efficiency_class = dict_sample(d)
        self.u_value = self.scenario.p_building_component_efficiency.get_item(self.rkey)
        self.record_historical_renovation_action(rkey=rkey)

    def record_historical_renovation_action(self, rkey: Optional["BuildingKey"]):
        self.scenario.renovation_action_building.accumulate_item(rkey=rkey, value=1)
        self.scenario.renovation_action_component.accumulate_item(rkey=rkey, value=1)
        self.scenario.renovation_action_labor_demand.accumulate_item(
            rkey=rkey, value=self.scenario.s_building_component_input_labor.get_item(rkey)
        )

    def renovate(self, id_building_component_option_efficiency_class: int):
        self.rkey.id_building_component_option_efficiency_class = id_building_component_option_efficiency_class
        self.u_value = self.scenario.p_building_component_efficiency.get_item(self.rkey)
        self.installation_year = self.rkey.year
        self.next_replace_year = self.rkey.year + self.get_lifetime()




