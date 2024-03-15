from dash import Dash, html
from dash_bootstrap_components.themes import BOOTSTRAP

from dashboards.data.loader import DataSchema_Building_Stock as DataSchema
from dashboards.data.loader import load_data
from dashboards.layouts import building_stock_ids as ids

import pandas as pd

from dashboards.components import (
    bar_chart,
    dropdown,
)

DATA_PATH = "../data/building_stock_R9160025.csv"


def run_building_stock_dash() -> None:
    # load the data and create the data manager
    data = load_data(DATA_PATH)

    app = Dash(external_stylesheets=[BOOTSTRAP])
    app.title = "Building Stock Dashboard"
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
                                    id_dropdown=ids.SUBSECTOR_DROPDOWN,
                                    id_options=DataSchema.ID_SUBSECTOR,
                                    id_select_all_button=ids.SELECT_ALL_SUBSECTORS_BUTTON
                                    ),
                ],
            ),
            bar_chart.render(app,
                             data,
                             id_barchart=ids.BAR_CHART,
                             id_dropdown=ids.SUBSECTOR_DROPDOWN,
                             id_filtered_colum=DataSchema.ID_SUBSECTOR,
                             x=DataSchema.ID_BUILDING_TYPE,
                             y=DataSchema.ID_APPLIANCE_ELECTRICITY_DEMAND,
                             ),
        ],
    )


if __name__ == "__main__":
    run_building_stock_dash()