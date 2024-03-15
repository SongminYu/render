import os

from Melodie import Config

from models.render_building.run import run_building_model
from projects.rokig.analysis.concat import concat_region_tables


def get_config(project_name: str):
    project_root = os.path.join(os.path.dirname(__file__))
    return Config(
        project_name=project_name,
        project_root=project_root,
        input_folder=os.path.join(project_root, "input"),
        output_folder=os.path.join(project_root, "output"),
        input_cache=True
    )


if __name__ == "__main__":
    config = get_config("rokig")
    run_building_model(cfg=config)
    # concat_region_tables(cfg=config, file_name_prefix="energy_consumption")
