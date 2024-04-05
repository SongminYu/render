import os

from Melodie import Config

from models.render_building.main import run_building_model
from models.render_building.toolkit import post_processor
from utils import data_toolkit


def get_config(project_name: str):
    project_root = os.path.join(os.path.dirname(__file__))
    return Config(
        project_name=project_name,
        project_root=project_root,
        input_folder=os.path.join(project_root, "input"),
        output_folder=os.path.join(project_root, "output"),
        input_cache=True
    )


def run_post_processor(cfg: "Config"):
    l = [
        "building_stock",
        # "renovation_rate_building",
        # "renovation_rate_component",
    ]
    # post_processor.concat_region_tables(cfg=cfg, file_name_prefix_list=l)
    post_processor.gen_final_energy_demand_from_building_stock(cfg=cfg, input_table="building_stock_R9010101.csv")
    post_processor.gen_building_stock_summary(cfg=cfg, input_table="building_stock_R9010101.csv")


def run_toolkit(cfg: "Config"):
    data_toolkit.find_id(cfg=cfg, id_name="id_building_action")
    data_toolkit.extract_id_data(cfg=cfg, id_name="id_region", id_value=9010101)
    data_toolkit.pack_sqlite(cfg=cfg)


if __name__ == "__main__":
    config = get_config("test_building")
    run_building_model(cfg=config, cores=1)
    # run_toolkit(cfg=config)
    run_post_processor(cfg=config)

