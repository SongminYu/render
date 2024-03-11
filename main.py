import os

from Melodie import Config

from models.render_building.run import run_building_model


def get_config(project_name: str):
    project_root = os.path.join(os.path.dirname(__file__), f"projects/{project_name}")
    return Config(
        project_name=project_name,
        project_root=project_root,
        input_folder=os.path.join(project_root, "input"),
        output_folder=os.path.join(project_root, "output"),
        input_cache=True
    )


if __name__ == "__main__":
    run_building_model(cfg=get_config("rokig"))
