from typing import TYPE_CHECKING

from Melodie import Environment
from tqdm import tqdm


if TYPE_CHECKING:
    from Melodie import AgentList
    from models.render_building.scenario import BuildingScenario
    from models.render_building.building import Building


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
            building.init_building_cooling_system()
            building.init_building_heating_system()
            building.init_building_ventilation_system()
            building.init_building_renovation_history()
            building.init_building_heating_cooling_demand()
            building.init_final_energy_demand()

    @staticmethod
    def update_buildings_year(buildings: "AgentList[Building]"):
        for building in tqdm(buildings, desc="Updating buildings year --> "):
            building.rkey.year += 1

    def update_buildings_profile_appliance(self, buildings: "AgentList[Building]"):
        # efficiency improvement (shifting down profiles)
        # --> multiply the hourly values with an exogenous factor (indexed by key_cols)
        # --> non-electricity and non-residential appliances (taking the output of other models)
        ...

    def update_buildings_technology_cooling(self, buildings: "AgentList[Building]"):
        # diffusion: decided by an exogenous penetration rate (pathway from FORECAST)
        # --> for example, the penetration rates are a1, a2, a3, ..., then in period 2, the adoption probability is (a2 - a1)/(1 - a1)
        # replace: triggered by lifetime
        ...

    def update_buildings_profile_hot_water(self, buildings: "AgentList[Building]"):
        # behavior change (shifting profiles)
        # --> multiply the hourly values with an exogenous factor (indexed by key_cols)
        ...

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
        # diffusion: decided by an exogenous penetration rate (pathway from FORECAST)
        # replace: triggered by lifetime
        ...

    def update_buildings_renovation(self, buildings: "AgentList[Building]"):

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


