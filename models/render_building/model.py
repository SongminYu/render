from typing import TYPE_CHECKING

from models.render.model import RenderModel
from models.render_building.building import Building
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

    def setup(self):
        self.scenario.setup_agent_params()
        # self.buildings.setup_agents(agents_num=len(self.scenario.agent_params), params_df=self.scenario.agent_params)
        # self.environment.setup_buildings(self.buildings)

    def run(self):
        print()
        ...
