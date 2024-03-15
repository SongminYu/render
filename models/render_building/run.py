from typing import Optional

from Melodie import Config
from Melodie import Simulator
from Melodie import run_profile
from models.render_building.model import BuildingModel
from models.render_building.scenario import BuildingScenario


def run_building_model(cfg: "Config", cores: Optional[int] = None):
    simulator = Simulator(
        config=cfg,
        model_cls=BuildingModel,
        scenario_cls=BuildingScenario
    )
    if cores is None:
        # run_profile(simulator.run)
        simulator.run()
    else:
        simulator.run_parallel(cores=cores)
