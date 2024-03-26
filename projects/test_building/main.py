import os

from Melodie import Config

from models.render_building.main import run_building_model
from projects.test_building.toolkit.table_processing import concat_region_tables
from projects.test_building.toolkit.table_processing import find_id


def get_config(project_name: str):
    project_root = os.path.join(os.path.dirname(__file__))
    return Config(
        project_name=project_name,
        project_root=project_root,
        input_folder=os.path.join(project_root, "input"),
        output_folder=os.path.join(project_root, "output"),
        input_cache=True
    )


def run_tool(cfg: "Config"):
    # concat_region_tables(cfg=cfg, file_name_prefix="AgentNumAgg")
    find_id(cfg=cfg, id_name="id_building_action")


if __name__ == "__main__":
    config = get_config("test_building")
    run_building_model(cfg=config)
    # run_tool(cfg=config)
