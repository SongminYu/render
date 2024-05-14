import random
from typing import TYPE_CHECKING

from Melodie import Environment
from tqdm import tqdm

from models.render_building import cons
from models.render_building.building_key import BuildingKey
from utils.funcs import dict_normalize, dict_utility_sample

if TYPE_CHECKING:
    from Melodie import AgentList
    from models.render_building.scenario import BuildingScenario
    from models.render_building.building import Building


class BuildingEnvironment(Environment):
    scenario: "BuildingScenario"
    agent: "Building"

    def setup(self):
        self.year = 0

    @staticmethod
    def setup_buildings(buildings: "AgentList[Building]"):

        for building in tqdm(buildings, desc="Setting up buildings --> "):
            building.init_rkey()
            building.init_units()
            building.init_building_profiles()
            building.init_building_size()
            building.init_building_construction()
            building.init_building_components()
            building.init_building_renovation_history()
            building.init_radiator()
            building.calc_building_heating_cooling_demand()
            building.init_building_cooling_system()
            building.init_building_heating_system()
            building.init_building_ventilation_system()
            building.init_final_energy_demand()
            building.update_total_energy_cost()

        for building in tqdm(buildings, desc="Setting up infrastructure availability --> "):
            building.init_building_district_heating_availability()
            building.init_building_gas_availability()

    @staticmethod
    def update_buildings_year(buildings: "AgentList[Building]"):

        def update_units_year():
            for unit in building.units:
                unit.rkey.year += 1
                unit.user.rkey.year += 1

        def update_components_year():
            for _, component in building.building_components.items():
                component.rkey.year += 1

        def update_radiator_year():
            building.radiator.rkey.year += 1

        def update_heating_system_year():
            building.heating_system.rkey.year += 1
            building.heating_system.heating_technology_main.rkey.year += 1
            if building.heating_system.heating_technology_second is not None:
                building.heating_system.heating_technology_second.rkey.year += 1

        def update_cooling_system_year():
            building.cooling_system.rkey.year += 1

        def update_ventilation_system_year():
            building.ventilation_system.rkey.year += 1

        for building in buildings:
            if building.exists:
                building.rkey.year += 1
                update_units_year()
                update_components_year()
                update_radiator_year()
                update_heating_system_year()
                update_cooling_system_year()
                update_ventilation_system_year()

    def update_buildings_district_heating_availability(self, buildings: "AgentList[Building]"):

        def get_district_heating_connection_prob(rkey: "BuildingKey"):
            connection_rate_1 = self.scenario.s_infrastructure_availability_district_heating.get_item(rkey)
            rkey.year = rkey.year - 1
            connection_rate_0 = self.scenario.s_infrastructure_availability_district_heating.get_item(rkey)
            return (connection_rate_1 - connection_rate_0) / (1 - connection_rate_0)

        for building in buildings:
            if building.exists and (not building.heating_system.district_heating_available):
                if random.uniform(0, 1) <= get_district_heating_connection_prob(building.rkey.make_copy()):
                    building.heating_system.district_heating_available = True

    def update_buildings_gas_availability(self, buildings: "AgentList[Building]"):

        def get_gas_connection_prob(rkey: "BuildingKey"):
            connection_rate_1 = self.scenario.s_infrastructure_availability_gas.get_item(rkey)
            rkey.year = rkey.year - 1
            connection_rate_0 = self.scenario.s_infrastructure_availability_gas.get_item(rkey)
            return (connection_rate_1 - connection_rate_0) / (1 - connection_rate_0)

        for building in buildings:
            if building.exists and (not building.heating_system.gas_available):
                if random.uniform(0, 1) <= get_gas_connection_prob(building.rkey.make_copy()):
                    building.heating_system.gas_available = True

    def update_buildings_profile_appliance(self, buildings: "AgentList[Building]"):
        for building in buildings:
            if building.exists:
                index = self.scenario.s_useful_energy_demand_index_appliance_electricity.get_item(building.rkey)
                if index != 1:
                    building.appliance_electricity_profile = building.appliance_electricity_profile * index
                    building.appliance_electricity_demand = building.appliance_electricity_profile.sum()
                    building.appliance_electricity_demand_per_person = building.appliance_electricity_demand / building.population

    def update_buildings_profile_hot_water(self, buildings: "AgentList[Building]"):
        for building in buildings:
            if building.exists:
                index = self.scenario.s_useful_energy_demand_index_hot_water.get_item(building.rkey)
                if index != 1:
                    building.hot_water_profile = building.hot_water_profile * index
                    building.hot_water_demand = building.hot_water_profile.sum()
                    building.hot_water_demand_per_person = building.hot_water_demand / building.population
                    building.hot_water_demand_per_m2 = building.hot_water_demand / building.total_living_area

    def update_buildings_technology_cooling(self, buildings: "AgentList[Building]"):

        def get_cooling_adoption_prob(rkey: "BuildingKey"):
            penetration_rate_1 = self.scenario.s_cooling_penetration_rate.get_item(rkey)
            rkey.year = rkey.year - 1
            penetration_rate_0 = self.scenario.s_cooling_penetration_rate.get_item(rkey)
            return (penetration_rate_1 - penetration_rate_0) / (1 - penetration_rate_0)

        for building in buildings:
            not_adopted = not building.cooling_system.is_adopted
            triggered_to_adopt = random.uniform(0, 1) <= get_cooling_adoption_prob(building.rkey.make_copy())
            time_to_replace = building.cooling_system.rkey.year >= building.cooling_system.next_replace_year
            if building.exists and ((not_adopted and triggered_to_adopt) or time_to_replace):
                building.cooling_system.select(
                    cooling_demand_peak=building.cooling_demand_peak,
                    cooling_demand=building.cooling_demand,
                )
                building.cooling_system.install()

    def update_buildings_technology_ventilation(self, buildings: "AgentList[Building]"):

        def get_ventilation_adoption_prob(rkey: "BuildingKey"):
            penetration_rate_1 = self.scenario.s_ventilation_penetration_rate.get_item(rkey)
            rkey.year = rkey.year - 1
            penetration_rate_0 = self.scenario.s_ventilation_penetration_rate.get_item(rkey)
            return (penetration_rate_1 - penetration_rate_0) / (1 - penetration_rate_0)

        for building in buildings:
            not_adopted = not building.ventilation_system.is_adopted
            triggered_to_adopt = random.uniform(0, 1) <= get_ventilation_adoption_prob(building.rkey.make_copy())
            time_to_replace = building.ventilation_system.rkey.year >= building.ventilation_system.next_replace_year
            if building.exists and ((not_adopted and triggered_to_adopt) or time_to_replace):
                building.ventilation_system.select(total_living_area=building.total_living_area)
                building.ventilation_system.install()

    @staticmethod
    def update_buildings_radiator_lifecycle(buildings: "AgentList[Building]"):
        for building in buildings:
            if building.exists and building.radiator.rkey.year >= building.radiator.next_replace_year:
                building.radiator.select(id_building_action=2)
                building.radiator.install()
                for heating_technology in [
                    building.heating_system.heating_technology_main,
                    building.heating_system.heating_technology_second
                ]:
                    if heating_technology is not None:
                        heating_technology.update_due_to_radiator_change(id_radiator=building.radiator.rkey.id_radiator)

    def update_buildings_technology_heating_lifecycle(self, buildings: "AgentList[Building]"):
        for building in buildings:
            if building.exists and random.uniform(0, 1) <= self.scenario.p_building_action_probability.get_item(building.rkey):
                for heating_technology in [
                    building.heating_system.heating_technology_main,
                    building.heating_system.heating_technology_second
                ]:
                    if heating_technology is not None:
                        if heating_technology.rkey.year >= heating_technology.next_replace_year:
                            total_energy_cost_before = building.total_energy_cost
                            heating_technology.update_optional_heating_technologies(
                                district_heating_available=building.heating_system.district_heating_available,
                                gas_available=building.heating_system.gas_available
                            )
                            option_action_info = heating_technology.select(
                                heating_demand_profile=building.heating_demand_profile,
                                hot_water_profile=building.hot_water_profile,
                            )
                            heating_technology.install()
                            building.update_space_heating_final_energy_demand()
                            building.update_hot_water_final_energy_demand()
                            building.update_total_energy_cost()
                            option_action_info["total_heating_demand_peak"] = building.total_heating_demand_peak
                            option_action_info["id_heating_technology_after"] = heating_technology.rkey.id_heating_technology
                            option_action_info["total_energy_cost_before"] = total_energy_cost_before
                            option_action_info["total_energy_cost_after"] = building.total_energy_cost
                            self.scenario.heating_system_action_info.append(option_action_info)

    def update_buildings_technology_heating_mandatory(self, buildings: "AgentList[Building]"):
        if self.scenario.heating_technology_mandatory:
            for building in buildings:
                if building.exists:
                    ...

    @staticmethod
    def update_buildings_total_energy_cost(buildings: "AgentList[Building]"):
        for building in buildings:
            if building.exists:
                building.update_total_energy_cost()

    def update_buildings_renovation_lifecycle(self, buildings: "AgentList[Building]"):
        self.update_buildings_total_energy_cost(buildings)
        for building in buildings:
            if building.exists and random.uniform(0, 1) <= self.scenario.p_building_action_probability.get_item(building.rkey):
                for component_name, building_component in building.building_components.items():
                    if building_component.rkey.year >= building_component.next_replace_year:
                        if random.uniform(0, 1) <= cons.PROB_POSTPONING_RENOVATION:
                            # mark status before renovation
                            before_renovation_status = {
                                "id_building_component_option_before": building_component.rkey.id_building_component_option,
                                "id_building_component_option_efficiency_class_before": building_component.rkey.id_building_component_option_efficiency_class,
                                "heating_demand_before": building.heating_demand,
                                "cooling_demand_before": building.cooling_demand,
                                "total_energy_cost_before": building.total_energy_cost,
                            }
                            d_option_cost = {}
                            rkey = building_component.rkey.make_copy().set_id({"id_building_action": cons.ID_BUILDING_ACTION_RENOVATION})
                            for id_building_component_option_efficiency_class in self.scenario.building_component_option_efficiency_classes.keys():
                                rkey.id_building_component_option_efficiency_class = id_building_component_option_efficiency_class
                                if self.scenario.s_building_component_availability.get_item(rkey):
                                    capex = self.scenario.building_component_capex.get_item(rkey) * building_component.area
                                    building.renovate_component(
                                        component_name=component_name,
                                        id_building_component_option_efficiency_class=id_building_component_option_efficiency_class
                                    )
                                    energy_cost_saving = (before_renovation_status["total_energy_cost_before"] - building.total_energy_cost)
                                    d_option_cost[id_building_component_option_efficiency_class] = capex - energy_cost_saving
                            id_building_component_option_efficiency_class = dict_utility_sample(
                                options=dict_normalize(d_option_cost),
                                utility_power=self.scenario.s_building_component_utility_power.get_item(rkey)
                            )
                            building.renovate_component(
                                component_name=component_name,
                                id_building_component_option_efficiency_class=id_building_component_option_efficiency_class
                            )
                            self.record_renovation_action_info(
                                building=building,
                                component_name=component_name,
                                before_renovation_status=before_renovation_status
                            )
                        else:
                            building_component.next_replace_year += self.scenario.p_building_component_postponing_lifetime.get_item(building_component.rkey)

    def record_renovation_action_info(self, building: "Building", component_name: str, before_renovation_status: dict):
        building_component = building.building_components[component_name]
        rkey = building_component.rkey.make_copy().set_id({"id_building_action": cons.ID_BUILDING_ACTION_RENOVATION})
        self.scenario.renovation_action_info.append({
            "id_scenario": rkey.id_scenario,
            "id_region": rkey.id_region,
            "id_sector": rkey.id_sector,
            "id_subsector": rkey.id_subsector,
            "id_subsector_agent": rkey.id_subsector_agent,
            "id_building_type": rkey.id_building_type,
            "id_building_construction_period": rkey.id_building_construction_period,
            "id_building_ownership": rkey.id_building_ownership,
            "id_building_component": rkey.id_building_component,
            "year": rkey.year,
            "id_building_component_option_before": before_renovation_status["id_building_component_option_before"],
            "id_building_component_option_after": rkey.id_building_component_option,
            "id_building_component_option_efficiency_class_before": before_renovation_status["id_building_component_option_efficiency_class_before"],
            "id_building_component_option_efficiency_class_after": rkey.id_building_component_option_efficiency_class,
            "efficiency_class_change": before_renovation_status["id_building_component_option_efficiency_class_before"] - rkey.id_building_component_option_efficiency_class,
            "heating_demand_before": before_renovation_status["heating_demand_before"],
            "heating_demand_after": building.heating_demand,
            "heating_demand_change": before_renovation_status["heating_demand_before"] - building.heating_demand,
            "cooling_demand_before": before_renovation_status["cooling_demand_before"],
            "cooling_demand_after": building.cooling_demand,
            "cooling_demand_change": before_renovation_status["cooling_demand_before"] - building.cooling_demand,
            "total_energy_cost_before": before_renovation_status["total_energy_cost_before"],
            "total_energy_cost_after": building.total_energy_cost,
            "total_energy_cost_change": before_renovation_status["total_energy_cost_before"] - building.total_energy_cost,
            "capex": self.scenario.building_component_capex.get_item(rkey) * building_component.area,
            "labor_demand": self.scenario.s_building_component_input_labor.get_item(rkey) * building_component.area
        })

    def update_buildings_renovation_mandatory(self, buildings: "AgentList[Building]"):
        if self.scenario.renovation_mandatory:
            for building in buildings:
                if building.exists:
                    ...

    def update_buildings_demolition(self, buildings: "AgentList[Building]"):
        self.demolished_buildings_this_year = []
        self.remaining_dwelling_number_this_year = self.scenario.dwelling_number.get_item(BuildingKey(
            id_scenario=self.scenario.id,
            id_region=self.scenario.id_region,
            year=self.year
        ))
        for building in buildings:
            if building.exists and building.rkey.year >= building.demolish_year:
                building.exists = False
                self.demolished_buildings_this_year.append(building)
                if building.rkey.id_sector == cons.ID_SECTOR_RESIDENTIAL:
                    self.remaining_dwelling_number_this_year -= building.unit_number * building.building_number

    def update_buildings_construction(self, buildings: "AgentList[Building]"):
        self.construct_new_tertiary_buildings(buildings=buildings)
        self.update_household_number()
        self.construct_new_residential_buildings(buildings=buildings)

    def construct_new_tertiary_buildings(self, buildings: "AgentList[Building]"):
        for building in self.demolished_buildings_this_year:
            if building.rkey.id_sector == cons.ID_SECTOR_TERTIARY:
                new_tertiary_building = self.construct_new_building(buildings=buildings, params={
                    "id_region": building.rkey.id_region,
                    "id_sector": building.rkey.id_sector,
                    "id_subsector": building.rkey.id_subsector,
                    "id_building_type": building.rkey.id_building_type,
                    "id_subsector_agent": self.scenario.get_new_building_id_subsector_agent(building.rkey),
                    "building_number": building.building_number
                })

    def update_household_number(self):

        def get_household_changing_rate():
            n_household_this_year = self.scenario.s_unit_user.get_item(rkey_this_year)
            n_household_next_year = self.scenario.s_unit_user.get_item(rkey_next_year)
            return (n_household_next_year - n_household_this_year) / n_household_this_year

        rkey_this_year = BuildingKey(
            id_scenario=self.scenario.id,
            id_region=self.scenario.id_region,
            id_sector=cons.ID_SECTOR_RESIDENTIAL,
            id_subsector=cons.ID_SUBSECTOR_RESIDENTIAL,
            year=self.year
        )
        rkey_next_year = rkey_this_year.make_copy().set_id({"year": self.year + 1})
        for id_unit_user_type in self.scenario.r_subsector_unit_user_type.get_item(rkey_this_year):
            rkey_this_year.id_unit_user_type = id_unit_user_type
            rkey_next_year.id_unit_user_type = id_unit_user_type
            changing_rate = get_household_changing_rate()
            household_number_next_year = round(self.scenario.household_number.get_item(rkey_this_year) * (1 + changing_rate))
            self.scenario.household_number.accumulate_item(rkey=rkey_next_year, value=household_number_next_year)

    def construct_new_residential_buildings(self, buildings: "AgentList[Building]"):

        def select_building_type():
            rkey_copy = rkey.make_copy()
            rkey_copy.year -= 1
            rkey_copy.init_dimension(
                dimension_name="id_building_type",
                dimension_ids=self.scenario.r_subsector_building_type.get_item(rkey_copy),
                rdict=self.scenario.s_construction_residential_building
            )
            return rkey_copy.id_building_type

        def get_total_household_number_next_year():
            total_household_number_next_year = 0
            for id_unit_user_type in cons.HOUSEHOLD_UNIT_USER_IDS:
                rkey.id_unit_user_type = id_unit_user_type
                total_household_number_next_year += self.scenario.household_number.get_item(rkey)
            return total_household_number_next_year

        rkey = BuildingKey(
            id_scenario=self.scenario.id,
            id_region=self.scenario.id_region,
            id_sector=cons.ID_SECTOR_RESIDENTIAL,
            id_subsector=cons.ID_SUBSECTOR_RESIDENTIAL,
            year=self.year + 1
        )
        household_number_next_year = get_total_household_number_next_year()
        if self.remaining_dwelling_number_this_year >= household_number_next_year:
            self.scenario.dwelling_number.set_item(rkey=rkey, value=self.remaining_dwelling_number_this_year)
            occupancy_rate = household_number_next_year/self.remaining_dwelling_number_this_year
        else:
            final_dwelling_number_next_year = self.remaining_dwelling_number_this_year
            while final_dwelling_number_next_year < household_number_next_year:
                rkey.id_building_type = select_building_type()
                building_number = 1 / self.scenario.p_building_coverage.get_item(rkey=rkey)
                new_residential_building = self.construct_new_building(buildings=buildings, params={
                    "id_region": rkey.id_region,
                    "id_sector": rkey.id_sector,
                    "id_subsector": rkey.id_subsector,
                    "id_building_type": rkey.id_building_type,
                    "id_subsector_agent": self.scenario.get_new_building_id_subsector_agent(rkey),
                    "building_number": building_number
                })
                final_dwelling_number_next_year += new_residential_building.unit_number * building_number
            self.scenario.dwelling_number.set_item(rkey=rkey, value=final_dwelling_number_next_year)
            occupancy_rate = household_number_next_year/final_dwelling_number_next_year
        # update `occupancy_rate` for all the buildings in the next year
        for building in buildings:
            if building.rkey.id_sector == cons.ID_SECTOR_RESIDENTIAL:
                building.occupancy_rate = occupancy_rate

    def construct_new_building(self, buildings: "AgentList[Building]", params: dict):
        new_building = buildings.add(params=params)
        new_building.init_rkey_new_construction(construction_year=self.year)
        new_building.init_units()
        new_building.init_building_profiles()
        new_building.init_building_size()
        new_building.init_building_construction_new_construction()
        new_building.init_building_components()
        new_building.init_radiator_new_construction()
        new_building.calc_building_heating_cooling_demand()
        new_building.init_building_cooling_system_new_construction()
        new_building.init_building_ventilation_system_new_construction()
        new_building.init_building_heating_system_new_construction()
        return new_building



