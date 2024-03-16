from typing import TYPE_CHECKING

from models.render_building.building_key import BuildingKey

if TYPE_CHECKING:
    from models.render_building.scenario import BuildingScenario


class Unit:

    def __init__(self, rkey: "BuildingKey", scenario: "BuildingScenario"):
        self.rkey = rkey
        self.scenario = scenario
        self.user = UnitUser(self.rkey.make_copy(), self.scenario)


class UnitUser:

    def __init__(self, rkey: "BuildingKey", scenario: "BuildingScenario"):
        self.rkey = rkey
        self.scenario = scenario
        self.init_unit_user_rkey()
        self.init_person_num()
        self.init_demand_profile()
        self.init_occupancy_profile()

    def init_unit_user_rkey(self):
        self.rkey.init_dimension(
            dimension_name="id_unit_user_type",
            dimension_ids=self.scenario.r_subsector_unit_user_type.get_item(self.rkey),
            rdict=self.scenario.s_unit_user
        )

    def init_person_num(self):
        area_relevance = self.scenario.p_unit_user_person_number_area_relevance.get_item(self.rkey)
        if area_relevance == 0:
            self.person_num = self.scenario.p_unit_user_person_number.get_item(self.rkey)
        else:
            self.person_num = int(self.scenario.s_building_unit_area.get_item(self.rkey) / self.scenario.p_unit_user_person_number.get_item(self.rkey))

    def init_demand_profile(self):
        person_num_relevance = self.scenario.p_unit_demand_profile_person_number_relevance.get_item(self.rkey)
        if person_num_relevance == 0:
            self.appliance_electricity_profile = self.scenario.pr_appliance_electricity.get_item(self.rkey)
            self.hot_water_profile = self.scenario.pr_hot_water.get_item(self.rkey)
        else:
            self.appliance_electricity_profile = self.scenario.pr_appliance_electricity.get_item(self.rkey) * self.person_num
            self.hot_water_profile = self.scenario.pr_hot_water.get_item(self.rkey) * self.person_num

    def init_occupancy_profile(self):
        self.occupancy_profile = self.scenario.pr_building_occupancy.get_item(self.rkey)
