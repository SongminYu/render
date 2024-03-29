import random
from typing import TYPE_CHECKING

from Melodie import Environment
from tqdm import tqdm


if TYPE_CHECKING:
    from Melodie import AgentList
    from models.render_building.scenario import BuildingScenario
    from models.render_building.building import Building
    from models.render_building.building_key import BuildingKey


class BuildingEnvironment(Environment):
    scenario: "BuildingScenario"
    agent: "Building"

    @staticmethod
    def setup_buildings(buildings: "AgentList[Building]"):
        for building in tqdm(buildings, desc="Setting up buildings --> "):
            building.init_rkey()
            building.init_units()
            building.init_building_profiles()
            building.init_building_size()
            building.init_building_components_construction()
            building.init_radiator()
            building.init_building_renovation_history()
            building.init_building_heating_cooling_demand()
            building.init_building_cooling_system()
            building.init_building_heating_system()
            building.init_building_ventilation_system()
            building.init_final_energy_demand()

    @staticmethod
    def update_buildings_year(buildings: "AgentList[Building]"):

        def update_units_year():
            for unit in building.units:
                unit.rkey.year += 1
                unit.user.rkey.year += 1

        def update_components_year():
            for component in building.building_components:
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
            if not building.heating_system.district_heating_available:
                if random.uniform(0, 1) <= get_district_heating_connection_prob(building.rkey.make_copy()):
                    building.heating_system.district_heating_available = True

    def update_buildings_gas_availability(self, buildings: "AgentList[Building]"):

        def get_gas_connection_prob(rkey: "BuildingKey"):
            connection_rate_1 = self.scenario.s_infrastructure_availability_gas.get_item(rkey)
            rkey.year = rkey.year - 1
            connection_rate_0 = self.scenario.s_infrastructure_availability_gas.get_item(rkey)
            return (connection_rate_1 - connection_rate_0) / (1 - connection_rate_0)

        for building in buildings:
            if not building.heating_system.gas_available:
                if random.uniform(0, 1) <= get_gas_connection_prob(building.rkey.make_copy()):
                    building.heating_system.gas_available = True

    def update_buildings_profile_appliance(self, buildings: "AgentList[Building]"):
        for building in buildings:
            index = self.scenario.s_useful_energy_demand_index_appliance_electricity.get_item(building.rkey)
            if index != 1:
                building.appliance_electricity_profile = building.appliance_electricity_profile * index
                building.appliance_electricity_demand = building.appliance_electricity_profile.sum()
                building.appliance_electricity_demand_per_person = building.appliance_electricity_demand / building.population

    def update_buildings_technology_cooling(self, buildings: "AgentList[Building]"):

        def get_cooling_adoption_prob(rkey: "BuildingKey"):
            penetration_rate_1 = self.scenario.s_cooling_penetration_rate.get_item(rkey)
            rkey.year = rkey.year - 1
            penetration_rate_0 = self.scenario.s_cooling_penetration_rate.get_item(rkey)
            return (penetration_rate_1 - penetration_rate_0) / (1 - penetration_rate_0)

        for building in buildings:
            if not building.cooling_system.is_adopted:
                building.cooling_system.adopt(adoption_prob=get_cooling_adoption_prob(building.rkey.make_copy()))
            else:
                building.cooling_system.replace()

    def update_buildings_profile_hot_water(self, buildings: "AgentList[Building]"):
        for building in buildings:
            index = self.scenario.s_useful_energy_demand_index_hot_water.get_item(building.rkey)
            if index != 1:
                building.hot_water_profile = building.hot_water_profile * index
                building.hot_water_demand = building.hot_water_profile.sum()
                building.hot_water_demand_per_person = building.hot_water_demand / building.population
                building.hot_water_demand_per_m2 = building.hot_water_demand / building.total_living_area

    def update_buildings_technology_heating(self, buildings: "AgentList[Building]"):
        # replace: triggered by lifetime
        # (1) sync renovation
        # --> might be triggered before replacing the heating system, then the feasible technologies could be more.
        # (2) availability
        # --> district heating, gas might not be available (requires infrastructure data & modeling)
        # --> renewable source availability, e.g., biomass, HP, etc.
        # --> technology availability in the market (banning policies)
        # (3) feasibility
        # --> some buildings cannot adopt HP and (low-temperature) district heating due to low-efficiency
        # (4) technology choice logic (after filtering)
        # --> the layers of system and technology have to be considered
        #     --> switching from one type of system to another is totally open
        #     --> the barrier is reflected in the cost for switching from one type of technology to the other
        # --> a utility function is designed and the utilities are pre-calculated and saved in a rdict
        ...

    def update_buildings_technology_ventilation(self, buildings: "AgentList[Building]"):

        def get_ventilation_adoption_prob(rkey: "BuildingKey"):
            penetration_rate_1 = self.scenario.s_ventilation_penetration_rate.get_item(rkey)
            rkey.year = rkey.year - 1
            penetration_rate_0 = self.scenario.s_ventilation_penetration_rate.get_item(rkey)
            return (penetration_rate_1 - penetration_rate_0) / (1 - penetration_rate_0)

        for building in buildings:
            if not building.ventilation_system.is_adopted:
                building.ventilation_system.adopt(adoption_prob=get_ventilation_adoption_prob(building.rkey.make_copy()))
            else:
                building.ventilation_system.replace()

    def update_buildings_renovation_lifecycle(self, buildings: "AgentList[Building]"):
        if self.scenario.renovation_lifecycle:
            for building in buildings:
                ...

        # How is renovation triggered?
        # (1) natural renovation
        # --> triggered by lifetime (each component),
        # --> sync_renovation can be triggerd (incl. heating system) but those minimum lifetime is considered
        # (2) forced renovation
        # --> triggerd by efficiency requirement (policy scenario)

        # How is renovation done?
        # (1) conventional renovation
        # --> for individual components, with longer time and lower cost
        # (2) serial renovation
        # --> for individual or multiple components, with shorter time and higher cost (less craftsman demand?)

        # furthermore
        # (1) craftsman demand, with data from:
        # --> https://www.nature.com/articles/s41597-023-02379-6
        # --> https://springernature.figshare.com/collections/Realization_times_of_energetic_modernization_measures_for_buildings_based_on_interviews_with_craftworkers/6650900/1)
        # (2) renovation_actions are stored in a pipeline and executed by the end of the year to implement
        # --> ranking
        # --> limitation of craftsman capacity (with a high capacity, we can still have the not-limited demand as results)
        # (3) material demand
        ...

    def update_buildings_renovation_mandatory(self, buildings: "AgentList[Building]"):
        if self.scenario.renovation_mandatory:
            for building in buildings:
                ...

    def update_buildings_demolition(self, buildings: "AgentList[Building]"):
        # How is demolition triggered?
        # --> logic of FORECAST-Building
        # --> lifetime of everything? (see INVERT, Andreas' thesis)

        # How is demolition done?
        # --> the agent is removed from model.buildings

        # furthermore
        # --> Be careful: when scaling up the consumption, we need to consider the change of total number of buildings
        # --> material that can be recycled can be saved as result (connecting Thurid's model)
        # --> craftsman demand (pipeline-based modeling)
        ...

    def update_buildings_construction(self, buildings: "AgentList[Building]"):
        # How is construction triggered?
        # --> to cover the people from demolished buildings + population growth?
        # --> moving of people? But it also means buildings are left empty somewhere.
        # --> we define an exogenous construction rate
        # --> use Scenario_Building input (provided by GHSL until 2030 with population and urbanization change considered)

        # How is construction done?
        # --> an agent will be initialized and added to model.buildings

        # furthermore
        # --> material demand
        # --> craftsman demand (pipeline-based modeling)
        ...


