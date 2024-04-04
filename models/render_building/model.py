from typing import TYPE_CHECKING

from models.render.model import RenderModel
from models.render_building.building import Building
from models.render_building.data_collector import BuildingDataCollector
from models.render_building.environment import BuildingEnvironment
from models.render_building.scenario import BuildingScenario

if TYPE_CHECKING:
    from Melodie import AgentList


class BuildingModel(RenderModel):
    scenario: "BuildingScenario"

    def create(self):
        self.set_seed()
        self.buildings: "AgentList[Building]" = self.create_agent_list(Building)
        self.environment: "BuildingEnvironment" = self.create_environment(BuildingEnvironment)
        self.data_collector: "BuildingDataCollector" = self.create_data_collector(BuildingDataCollector)

    def setup(self):
        self.scenario.load_scenario_data()
        self.scenario.setup_results_containers()
        self.scenario.setup_agent_params()
        # self.scenario.setup_cost_data()
        self.buildings.setup_agents(agents_num=len(self.scenario.agent_params), params_df=self.scenario.agent_params)
        self.environment.setup_buildings(self.buildings)
        # self.export_initialization_info()

    def export_initialization_info(self):
        self.data_collector.export_scenario_cost()
        self.data_collector.export_heating_technology_main_initial_adoption()
        self.data_collector.export_location_infrastructure()

    def collect_building_info(self):
        # self.data_collector.collect_building_floor_area(self.buildings)
        self.data_collector.collect_building_stock(self.buildings)
        self.data_collector.collect_building_final_energy_demand(self.buildings)
        # self.data_collector.collect_building_efficiency_class_count(self.buildings)
        # self.data_collector.collect_building_profile(self.buildings)
        ...

    def export_building_info(self):
        # self.data_collector.export_building_floor_area()
        self.data_collector.export_building_stock()
        self.data_collector.export_building_final_energy_demand()
        # self.data_collector.export_building_efficiency_class_count()
        # self.data_collector.export_building_profile()
        # self.data_collector.export_renovation_rate()
        ...

    def run(self):
        for year in range(self.scenario.start_year, self.scenario.end_year + 1):
            self.collect_building_info()
            # TODO: the costs may need to be normalized before calculating utility,
            #  or the capex and opex can be too high after multiplying the capacity and annual demand,
            #  the utility is not sensitive at all any more
            # self.environment.update_buildings_year(self.buildings)
            # self.environment.update_buildings_district_heating_availability(self.buildings)
            # self.environment.update_buildings_gas_availability(self.buildings)
            # self.environment.update_buildings_profile_appliance(self.buildings)
            # self.environment.update_buildings_profile_hot_water(self.buildings)
            # self.environment.update_buildings_technology_cooling(self.buildings)
            # self.environment.update_buildings_technology_ventilation(self.buildings)
            # self.environment.update_buildings_radiator_lifecycle(self.buildings)
            # self.environment.update_buildings_technology_heating_lifecycle(self.buildings)
            # self.environment.update_buildings_technology_heating_mandatory(self.buildings)
            # self.environment.update_buildings_renovation_lifecycle(self.buildings)
            # self.environment.update_buildings_renovation_mandatory(self.buildings)
            # self.environment.update_buildings_demolition(self.buildings)
            # self.environment.update_buildings_construction(self.buildings)
        self.export_building_info()
