import os

from Melodie import Config

from models.render_building.main import run_building_model
from utils import table_processor


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
    prefixes = [
        # "building_efficiency_class_count",
        # "building_stock",
        "final_energy_demand",
        # "floor_area",
        # "renovation_rate_building",
        # "renovation_rate_component",
    ]
    for prefix in prefixes:
        table_processor.concat_region_tables(cfg=cfg, file_name_prefix=prefix)
    # table_processor.find_id(cfg=cfg, id_name="id_building_action")
    # table_processor.extract_id_data(cfg=cfg, id_name="id_region", id_value=9010101)
    # table_processor.pack_sqlite(cfg=cfg)


if __name__ == "__main__":
    config = get_config("test_building")
    # run_building_model(cfg=config, cores=10)
    run_tool(cfg=config)

