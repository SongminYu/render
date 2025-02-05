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


def run_toolkit(cfg: "Config"):
    data_toolkit.find_id(cfg=cfg, id_name="id_unit_user_type")
    # data_toolkit.extract_id_data(cfg=cfg, id_name="id_region", id_value=9010101)
    # data_toolkit.pack_sqlite(cfg=cfg)

def run_post_processor(cfg: "Config"):
    post_processor.process_region_building_stock(cfg=cfg, cores=8)
    post_processor.aggregate_region_building_stock(cfg=cfg, nuts_level=0)
    # post_processor.aggregate_region_building_stock(cfg=cfg, nuts_level=1)
    # post_processor.aggregate_region_building_stock(cfg=cfg, nuts_level=2)
    # post_processor.aggregate_region_building_stock(cfg=cfg, nuts_level=3)
    post_processor.gen_renovation_rate(cfg=cfg)
    post_processor.gen_demolition_rate(cfg=cfg)
    # post_processor.add_emission_to_fed(cfg=cfg, fed_file="final_energy_demand_nuts2")


if __name__ == "__main__":
    config = get_config("test_building")
    # run_toolkit(cfg=config)
    run_building_model(cfg=config)
    run_post_processor(cfg=config)

