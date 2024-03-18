from dash import Dash, html
from dash_bootstrap_components.themes import BOOTSTRAP

from dashboards.data.loader import DataSchema_Building_Stock as DataSchema
from dashboards.data import loader
from dashboards.layouts import building_stock_ids as ids

import pandas as pd

from dashboards.components import (
    bar_chart_data,
    dropdown,
)

DATA_PATH = "../data/building_stock_R9160025.csv"


def run_building_stock_dash() -> None:
    # load the data and create the data manager
    data = loader.load_data(DATA_PATH)
    data = loader.preprocessing_building_stock_data(data, DATA_PATH)

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
                                    id_dropdown=ids.SCENARIO_DROPDOWN,
                                    id_options=DataSchema.ID_SCENARIO,
                                    id_select_all_button=ids.SELECT_ALL_SCENARIOS_BUTTON
                                    ),
                ],
            ),
            html.Div(
                className="dropdown-container",
                children=[
                    dropdown.render(app,
                                    data,
                                    id_dropdown=ids.REGION_DROPDOWN,
                                    id_options=DataSchema.ID_REGION,
                                    id_select_all_button=ids.SELECT_ALL_REGIONS_BUTTON
                                    ),
                ],
            ),
            html.Div(
                className="dropdown-container",
                children=[
                    dropdown.render(app,
                                    data,
                                    id_dropdown=ids.SECTOR_DROPDOWN,
                                    id_options=DataSchema.ID_SECTOR,
                                    id_select_all_button=ids.SELECT_ALL_SECTORS_BUTTON
                                    ),
                ],
            ),
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
            html.Div(
                className="dropdown-container",
                children=[
                    dropdown.render(app,
                                    data,
                                    id_dropdown=ids.YEAR_DROPDOWN,
                                    id_options=DataSchema.YEAR,
                                    id_select_all_button=ids.SELECT_ALL_YEARS_BUTTON
                                    ),
                ],
            ),
            bar_chart_data.render(app,
                                  data,
                                  id_barchart=ids.BAR_CHART,
                                  dropdowns=[{'id': ids.SECTOR_DROPDOWN, 'column': DataSchema.ID_SECTOR},
                                             {'id': ids.SUBSECTOR_DROPDOWN, 'column': DataSchema.ID_SUBSECTOR}],
                                  x=[DataSchema.APPLIANCE_ELECTRICITY_DEMAND,
                                     DataSchema.COOLING_DEMAND,
                                     DataSchema.TOTAL_HEATING_CONSUMPTION,
                                     DataSchema.TOTAL_HOT_WATER_CONSUMPTION],
                                  ),
        ],
    )


if __name__ == "__main__":
    run_building_stock_dash()
