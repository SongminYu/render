from typing import TYPE_CHECKING

import numpy as np

from models.render_building.building_key import BuildingKey

if TYPE_CHECKING:
    from models.render.render_dict import RenderDict
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

        # self.rkey.init_dimension(
        #     dimension_name="id_income_group",  # can be linked to financial constraint
        #     dimension_ids=self.scenario.unit_user_types.keys(),
        #     rdict=self.scenario.s_unit_user
        # )
        # TODO: check with Sabine and see if we can add more behavioral parameters based on their surveys

    def init_person_num(self):
        area_relevance = self.scenario.p_unit_user_person_number_area_relevance.get_item(self.rkey)
        if area_relevance == 0:
            self.person_num = self.scenario.p_unit_user_person_number.get_item(self.rkey)
        else:
            self.person_num = int((self.scenario.s_building_unit_area.get_item(self.rkey)/
                                   self.scenario.p_unit_user_person_number.get_item(self.rkey)))

    def init_demand_profile(self):
        person_num_relevance = self.scenario.p_unit_demand_profile_person_number_relevance.get_item(self.rkey)
        if person_num_relevance == 0:
            self.appliance_electricity_profile = self.scenario.get_hour_profile(self.scenario.pr_appliance_electricity, self.rkey)
            self.hot_water_profile = self.scenario.get_hour_profile(self.scenario.pr_hot_water, self.rkey)
        else:
            self.appliance_electricity_profile = self.scenario.get_hour_profile(self.scenario.pr_appliance_electricity, self.rkey) * self.person_num
            self.hot_water_profile = self.scenario.get_hour_profile(self.scenario.pr_hot_water, self.rkey) * self.person_num

    def init_occupancy_profile(self):
        self.occupancy_profile = self.scenario.get_hour_profile(self.scenario.pr_building_occupancy, self.rkey)

    def get_hour_profile(self, profile_rdict: "RenderDict"):
        pr = np.zeros(8760, )
        for hour in range(1, 8761):
            self.rkey.hour = hour
            pr[hour - 1] = profile_rdict.get_item(self.rkey)
        return pr











