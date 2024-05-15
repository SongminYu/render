from typing import TYPE_CHECKING

from tqdm import tqdm

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
        self.scenario.setup_scenario_data()
        self.buildings.setup_agents(agents_num=len(self.scenario.agent_params), params_df=self.scenario.agent_params)
        self.data_collector.export_initialization_data()

    def run(self):
        self.environment.setup_buildings(self.buildings)
        self.data_collector.collect_building_stock(self.buildings)
        for year in tqdm(range(self.scenario.start_year, self.scenario.end_year + 1), desc="Simulating years --> "):
            self.environment.year = year
            self.environment.update_buildings_renovation(self.buildings)
            self.environment.update_buildings_radiator_lifecycle(self.buildings)
            self.environment.update_buildings_district_heating_availability(self.buildings)
            self.environment.update_buildings_gas_availability(self.buildings)
            self.environment.update_buildings_profile_appliance(self.buildings)
            self.environment.update_buildings_profile_hot_water(self.buildings)
            self.environment.update_buildings_technology_cooling(self.buildings)
            self.environment.update_buildings_technology_ventilation(self.buildings)
            self.environment.update_buildings_technology_heating_lifecycle(self.buildings)
            # self.environment.update_buildings_technology_heating_mandatory(self.buildings)
            self.environment.update_buildings_demolition(self.buildings)
            self.environment.update_buildings_construction(self.buildings)
            self.environment.update_buildings_year(self.buildings)
            self.environment.update_buildings_energy_demand_and_cost(self.buildings)
            self.data_collector.collect_building_stock(self.buildings)
        self.data_collector.export()




