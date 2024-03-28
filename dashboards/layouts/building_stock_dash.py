from dash import Dash, html
from dash_bootstrap_components.themes import BOOTSTRAP

from dashboards.data.loader import DataSchema_Building_Stock as DataSchema
from dashboards.data import loader

import pandas as pd

from dashboards.components import (
    bar_chart_data,
    dropdown,
    sub_dropdown,
)

DATA_PATH = "../data/building_stock_R9160025.csv"

# IDs for dashboard
SCENARIO_DROPDOWN = "scenario-dropdown"
SELECT_ALL_SCENARIOS_BUTTON = "select-all-scenarios-button"

REGION_DROPDOWN = "region-dropdown"
SELECT_ALL_REGIONS_BUTTON = "select-all-regions-button"

SECTOR_DROPDOWN = "sector-dropdown"
SELECT_ALL_SECTORS_BUTTON = "select-all-sectors-button"

SUBSECTOR_DROPDOWN = "subsector-dropdown"
SELECT_ALL_SUBSECTORS_BUTTON = "select-all-subsectors-button"

YEAR_DROPDOWN = "year-dropdown"
SELECT_ALL_YEARS_BUTTON = "select-all-years-button"

BAR_CHART = "bar-chart"


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
                                    id_dropdown=SCENARIO_DROPDOWN,
                                    id_options=DataSchema.ID_SCENARIO,
                                    id_select_all_button=SELECT_ALL_SCENARIOS_BUTTON
                                    ),
                ],
            ),
            html.Div(
                className="dropdown-container",
                children=[
                    dropdown.render(app,
                                    data,
                                    id_dropdown=REGION_DROPDOWN,
                                    id_options=DataSchema.ID_REGION,
                                    id_select_all_button=SELECT_ALL_REGIONS_BUTTON
                                    ),
                ],
            ),
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
            html.Div(
                className="sub-dropdown-container",
                children=[
                    sub_dropdown.render(app,
                                    data,
                                    id_sub_dropdown=SUBSECTOR_DROPDOWN,
                                    id_dropdown=SECTOR_DROPDOWN,
                                    id_sub_options=DataSchema.ID_SUBSECTOR,
                                    id_options = DataSchema.ID_SECTOR,
                                    id_select_all_button=SELECT_ALL_SUBSECTORS_BUTTON
                                    ),
                ],
            ),
            html.Div(
                className="dropdown-container",
                children=[
                    dropdown.render(app,
                                    data,
                                    id_dropdown=YEAR_DROPDOWN,
                                    id_options=DataSchema.YEAR,
                                    id_select_all_button=SELECT_ALL_YEARS_BUTTON
                                    ),
                ],
            ),
            bar_chart_data.render(app,
                                  data,
                                  id_barchart=BAR_CHART,
                                  dropdowns=[{'id': SECTOR_DROPDOWN, 'column': DataSchema.ID_SECTOR},
                                             {'id': SUBSECTOR_DROPDOWN, 'column': DataSchema.ID_SUBSECTOR}],
                                  x=[DataSchema.APPLIANCE_ELECTRICITY_DEMAND,
                                     DataSchema.COOLING_DEMAND,
                                     DataSchema.TOTAL_HEATING_CONSUMPTION,
                                     DataSchema.TOTAL_HOT_WATER_CONSUMPTION],
                                  ),
        ],
    )


if __name__ == "__main__":
    run_building_stock_dash()
