from dash import Dash, html
from dash_bootstrap_components.themes import BOOTSTRAP

from dashboards.data.loader import DataSchema_Building_Stock as DataSchema
from dashboards.data import loader

import pandas as pd

from dashboards.components import (
    stacked_bar_chart,
    data_table,
    dropdown,
    sub_dropdown,
    compare_model_calibration_table,
)

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

MODEL_DATA_TABLE = "Model Results"
REFERENCE_DATA_TABLE = "Reference Data"
ABSOLUTE_DIFF_TABLE = "Absolute difference"
RELATIVE_DIFF_TABLE = "Relative difference"
COMPARISON_DIFF_TABLE = "comparison-diff-table"

DATA_PATH = "../data/building_stock.csv"
END_USE_PATH = "../data/final_energy_demand.csv"
REFERENCE_PATH = "../data/CalibrationTarget.csv"


def run_building_stock_dash() -> None:
    # load the data and create the data manager
    data = loader.load_data(END_USE_PATH)
    reference_data = loader.load_data(REFERENCE_PATH)

    data['id_end_use'] = data['id_end_use'].astype(str)
    reference_data['id_end_use'] = reference_data['id_end_use'].astype(str)

    data['id_energy_carrier'] = data['id_energy_carrier'].astype(str)
    reference_data['id_energy_carrier'] = reference_data['id_energy_carrier'].astype(str)

    app = Dash(__name__, external_stylesheets=[BOOTSTRAP])
    app.title = "Building Stock Dashboard"
    app.layout = create_layout(app, data, reference_data)
    app.run(debug=True)


def create_layout(app: Dash, data: pd.DataFrame, reference_data) -> html.Div:
    dropdowns = [{'id': SCENARIO_DROPDOWN, 'column': DataSchema.ID_SCENARIO},
                 {'id': REGION_DROPDOWN, 'column': DataSchema.ID_REGION},
                 {'id': SECTOR_DROPDOWN, 'column': DataSchema.ID_SECTOR},
                 {'id': SUBSECTOR_DROPDOWN, 'column': DataSchema.ID_SUBSECTOR},
                 {'id': YEAR_DROPDOWN, 'column': DataSchema.YEAR}, ]

    x = 'id_end_use'
    y = 'value'
    category = 'id_energy_carrier'

    end_use_table = data_table.render(app,
                                      data,
                                      id_datatable=MODEL_DATA_TABLE,
                                      dropdowns=dropdowns,
                                      x=x,
                                      y=y,
                                      category=category)

    reference_table = data_table.render(app,
                                        reference_data,
                                        id_datatable=REFERENCE_DATA_TABLE,
                                        dropdowns=[{'id': SECTOR_DROPDOWN, 'column': DataSchema.ID_SECTOR},
                                                   {'id': SUBSECTOR_DROPDOWN, 'column': DataSchema.ID_SUBSECTOR},
                                                   {'id': YEAR_DROPDOWN, 'column': DataSchema.YEAR}, ],
                                        x=x,
                                        y='value',
                                        category=category)

    return html.Div(
        className="app-div",
        children=[
            html.H1(app.title),
            html.Hr(),
            dropdown.render(app, data, SCENARIO_DROPDOWN, DataSchema.ID_SCENARIO, SELECT_ALL_SCENARIOS_BUTTON),
            dropdown.render(app, data, REGION_DROPDOWN, DataSchema.ID_REGION, SELECT_ALL_REGIONS_BUTTON),
            dropdown.render(app, data, SECTOR_DROPDOWN, DataSchema.ID_SECTOR, SELECT_ALL_SECTORS_BUTTON),
            sub_dropdown.render(app, data, SUBSECTOR_DROPDOWN, SECTOR_DROPDOWN, DataSchema.ID_SUBSECTOR,
                                DataSchema.ID_SECTOR, SELECT_ALL_SUBSECTORS_BUTTON),
            dropdown.render(app, data, YEAR_DROPDOWN, DataSchema.YEAR, SELECT_ALL_YEARS_BUTTON),
            stacked_bar_chart.render(app,
                                     data,
                                     id_barchart=BAR_CHART,
                                     dropdowns=dropdowns,
                                     x=x,
                                     y=y,
                                     category=category),
            html.Div(className='flex-container', children=[end_use_table, reference_table]),
            compare_model_calibration_table.render(app, COMPARISON_DIFF_TABLE, MODEL_DATA_TABLE, REFERENCE_DATA_TABLE,
                                                   ABSOLUTE_DIFF_TABLE, RELATIVE_DIFF_TABLE)
        ],
    )


if __name__ == "__main__":
    run_building_stock_dash()
