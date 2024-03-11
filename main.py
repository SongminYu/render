from Melodie import Simulator
from Melodie import Config
from typing import Optional
import os
from models.render_building.model import BuildingModel
from models.render_building.scenario import BuildingScenario


def run_building_model(cfg: "Config", cores: Optional[int] = None):
    simulator = Simulator(
        config=cfg,
        model_cls=BuildingModel,
        scenario_cls=BuildingScenario
    )
    if cores is None:
        simulator.run()
    else:
        simulator.run_parallel(cores=cores)


if __name__ == "__main__":
    project_root = os.path.join(os.path.dirname(__file__), "projects/rokig")
    config = Config(
        project_name="rokig",
        project_root=project_root,
        input_folder=os.path.join(project_root, "input"),
        output_folder=os.path.join(project_root, "output"),
        input_cache=True
    )
    run_building_model(cfg=config)
