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