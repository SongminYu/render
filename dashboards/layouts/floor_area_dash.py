from dash import Dash, html
from dash_bootstrap_components.themes import BOOTSTRAP

from dashboards.data.loader import DataSchema_Floor_Area as DataSchema
from dashboards.data.loader import load_data

import pandas as pd

from dashboards.components import (
    bar_chart_filtered,
    dropdown,
)

DATA_PATH = "../data/floor_area.csv"

# IDs for dashboard
SECTOR_DROPDOWN = "sector-dropdown"
SELECT_ALL_SECTORS_BUTTON = "select-all-sectors-button"

SUBSECTOR_DROPDOWN = "subsector-dropdown"
SELECT_ALL_SUBSECTORS_BUTTON = "select-all-subsectors-button"

BAR_CHART = "bar-chart"


def run_floor_area_dash() -> None:
    # load the data and create the data manager
    data = load_data(DATA_PATH)

    app = Dash(external_stylesheets=[BOOTSTRAP])
    app.title = "Floor Area Dashboard"
    app.layout = create_layout(app, data)
    app.run()


def create_layout(app: Dash, data: pd.DataFrame) -> html.Div:
    return html.Div(
        className="app-div",
        children=[
            html.H1(app.title),
            html.Hr(),
            html.Div(
                className="dropdown-container",
                children=[
                    dropdown.render(app,
                                    data,
                                    id_dropdown=SECTOR_DROPDOWN,
                                    id_options=DataSchema.ID_SECTOR,
                                    id_select_all_button=SELECT_ALL_SECTORS_BUTTON
                                    ),
                ],
            ),
            bar_chart_filtered.render(app,
                             data,
                             id_barchart=BAR_CHART,  #
                             dropdowns=[{'id': SECTOR_DROPDOWN, 'column': DataSchema.ID_SECTOR}],
                             x=DataSchema.ID_BUILDING_TYPE,
                             y=DataSchema.VALUE
                             ),
        ],
    )


if __name__ == "__main__":
    run_floor_area_dash()
