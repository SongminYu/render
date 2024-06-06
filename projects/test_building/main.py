import os

from Melodie import Config

from models.render_building.main import run_building_model
from models.render_building.toolkit import post_processor
from models.render_building.toolkit import plotter
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
    data_toolkit.find_id(cfg=cfg, id_name="id_ownership")
    # data_toolkit.extract_id_data(cfg=cfg, id_name="id_region", id_value=9010101)
    # data_toolkit.pack_sqlite(cfg=cfg)


def run_post_processor(cfg: "Config"):
    post_processor.process_region_building_stock(cfg=cfg)
    post_processor.aggregate_region_building_stock(cfg=cfg, nuts_level=3)


def run_plotter(cfg: "Config"):
    plotter.plot_hist_heating_demand_per_m2(cfg, year=2019, input_table="building_stock_R9010101.csv")


if __name__ == "__main__":
    config = get_config("test_building")
    # run_toolkit(cfg=config)
    run_building_model(cfg=config, cores=8)
    # run_post_processor(cfg=config)
    # run_plotter(cfg=config)

