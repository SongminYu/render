from typing import TYPE_CHECKING

from models.render_building.building_key import BuildingKey
from models.render_building import cons
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

    def init_unit_user_rkey(self):
        self.rkey.init_dimension(
            dimension_name="id_unit_user_type",
            dimension_ids=self.scenario.r_subsector_unit_user_type.get_item(self.rkey),
            rdict=self.scenario.s_unit_user
        )
        self.rkey.init_dimension(
            dimension_name="id_dwelling_ownership",
            dimension_ids=self.scenario.dwelling_ownerships.keys(),
            rdict=self.scenario.s_unit_user_dwelling_ownership
        )

    def init_person_num(self):
        if self.rkey.id_sector == cons.ID_SECTOR_RESIDENTIAL:
            self.person_num = self.scenario.p_unit_user_person_number.get_item(self.rkey)
        else:
            self.person_num = (self.scenario.s_building_unit_area.get_item(self.rkey) /
                               self.scenario.p_unit_user_person_number.get_item(self.rkey))

    @property
    def hot_water_profile(self):
        hot_water_profile = (
                self.scenario.pr_hot_water.get_item(self.rkey) *
                self.person_num *
                self.scenario.s_end_use_demand_hot_water.get_item(self.rkey)
        )
        return hot_water_profile

    @property
    def appliance_electricity_profile(self):
        appliance_electricity_rkey = self.rkey.make_copy().set_id({
            "id_end_use": cons.ID_END_USE_APPLIANCE,
            "id_energy_carrier": cons.ID_ENERGY_CARRIER_ELECTRICITY
        })
        appliance_electricity_profile = (
                self.scenario.pr_appliance_electricity.get_item(self.rkey) *
                self.person_num *
                self.scenario.s_end_use_demand_appliance.get_item(appliance_electricity_rkey)
        )
        return appliance_electricity_profile

    @property
    def occupancy_profile(self):
        return self.scenario.pr_building_occupancy.get_item(self.rkey)
