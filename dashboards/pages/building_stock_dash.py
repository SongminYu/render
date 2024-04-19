import dash
from dash import html

from dashboards.data.loader import DataSchema_Final_Energy as DataSchema
from dashboards.data import loader
from dashboards.components import (
    stacked_bar_chart,
    data_table,
    dropdown,
    sub_dropdown,
    compare_model_calibration_table,
)

dash.register_page(__name__, path='/', name="End Use Analysis")

# -------------------- IDs --------------------
SCENARIO_DROPDOWN = "scenario-dropdown-enduse"
SELECT_ALL_SCENARIOS_BUTTON = "select-all-scenarios-button-enduse"

REGION_DROPDOWN = "region-dropdown-enduse"
SELECT_ALL_REGIONS_BUTTON = "select-all-regions-button-enduse"

SECTOR_DROPDOWN = "sector-dropdown-enduse"
SELECT_ALL_SECTORS_BUTTON = "select-all-sectors-button-enduse"

SUBSECTOR_DROPDOWN = "subsector-dropdown-enduse"
SELECT_ALL_SUBSECTORS_BUTTON = "select-all-subsectors-button-enduse"

YEAR_DROPDOWN = "year-dropdown-enduse"
SELECT_ALL_YEARS_BUTTON = "select-all-years-button-enduse"

END_USE_PATH = "data/final_energy_demand.csv"
REFERENCE_PATH = "data/CalibrationTarget.csv"

# -------------------- LOAD DATASET --------------------
data = loader.load_data(END_USE_PATH)
data = loader.preprocess_data(data)
reference_data = loader.load_data(REFERENCE_PATH)
reference_data = loader.preprocess_data(reference_data)

# -------------------- VARIABLES --------------------
id_energy_carriers = list(data[DataSchema.ID_ENERGY_CARRIER].unique())
id_energy_carriers.sort()

dropdowns = [{'id': SCENARIO_DROPDOWN, 'column': DataSchema.ID_SCENARIO},
             {'id': REGION_DROPDOWN, 'column': DataSchema.ID_REGION},
             {'id': SECTOR_DROPDOWN, 'column': DataSchema.ID_SECTOR},
             {'id': SUBSECTOR_DROPDOWN, 'column': DataSchema.ID_SUBSECTOR},
             {'id': YEAR_DROPDOWN, 'column': DataSchema.YEAR}, ]

x = DataSchema.ID_END_USE
y = DataSchema.VALUE_TWh
category = DataSchema.ID_ENERGY_CARRIER

# -------------------- DATA TABLES --------------------
end_use_table = data_table.render(data,
                                  id_datatable="Model Results in TWh",
                                  dropdowns=dropdowns,
                                  x=x,
                                  x_options=id_energy_carriers,
                                  y=y,
                                  category=category)

reference_table = data_table.render(reference_data,
                                    id_datatable="Reference Data in TWh",
                                    dropdowns=[{'id': SECTOR_DROPDOWN, 'column': DataSchema.ID_SECTOR},
                                               {'id': SUBSECTOR_DROPDOWN, 'column': DataSchema.ID_SUBSECTOR},
                                               {'id': YEAR_DROPDOWN, 'column': DataSchema.YEAR}, ],
                                    x=x,
                                    x_options=id_energy_carriers,
                                    y=y,
                                    category=category)

# -------------------- PAGE LAYOUT --------------------
layout = html.Div(children=[
        dropdown.render(data, SCENARIO_DROPDOWN, DataSchema.ID_SCENARIO, SELECT_ALL_SCENARIOS_BUTTON),
        dropdown.render(data, REGION_DROPDOWN, DataSchema.ID_REGION, SELECT_ALL_REGIONS_BUTTON),
        dropdown.render(data, SECTOR_DROPDOWN, DataSchema.ID_SECTOR, SELECT_ALL_SECTORS_BUTTON),
        sub_dropdown.render(data, SUBSECTOR_DROPDOWN, SECTOR_DROPDOWN, DataSchema.ID_SUBSECTOR,
                            DataSchema.ID_SECTOR, SELECT_ALL_SUBSECTORS_BUTTON),
        dropdown.render(data, YEAR_DROPDOWN, DataSchema.YEAR, SELECT_ALL_YEARS_BUTTON),
        stacked_bar_chart.render(data,
                                 id_barchart="bar-chart-enduse",
                                 dropdowns=dropdowns,
                                 x=x,
                                 y=y,
                                 category=category),
        html.Div(className='flex-container', children=[end_use_table, reference_table]),
        compare_model_calibration_table.render("comparison-diff-table", "Model Results in TWh", "Reference Data in TWh",
                                               "Absolute difference in TWh", "Relative difference")
    ],
)
