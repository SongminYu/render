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

dash.register_page(__name__, path='/region_analysis', name="Region Analysis")

# -------------------- IDs --------------------
SCENARIO_DROPDOWN = "scenario-dropdown-region"
SELECT_ALL_SCENARIOS_BUTTON = "select-all-scenarios-button-region"

REGION_DROPDOWN = "region-dropdown-region"
SELECT_ALL_REGIONS_BUTTON = "select-all-regions-button-region"

SECTOR_DROPDOWN = "sector-dropdown-region"
SELECT_ALL_SECTORS_BUTTON = "select-all-sectors-button-region"

YEAR_DROPDOWN = "year-dropdown-region"
SELECT_ALL_YEARS_BUTTON = "select-all-years-button-region"

EEV_PATH = "data/final_energy_demand.csv"
REFERENCE_PATH = "data/Energiebilanzen_Regional_Example.csv"

# -------------------- LOAD DATASET --------------------
data = loader.load_data(EEV_PATH)
data = loader.preprocess_data(data)
data = loader.aggregate_to_nuts1(data)

reference = loader.load_data(REFERENCE_PATH)
reference = loader.convert_TJ_to_TWh(reference)

# -------------------- VARIABLES --------------------
id_energy_carriers = list(data[DataSchema.ID_ENERGY_CARRIER].unique())
id_energy_carriers.sort()

dropdowns = [{'id': SCENARIO_DROPDOWN, 'column': DataSchema.ID_SCENARIO},
             {'id': REGION_DROPDOWN, 'column': DataSchema.ID_REGION},
             {'id': SECTOR_DROPDOWN, 'column': DataSchema.ID_SECTOR},
             {'id': YEAR_DROPDOWN, 'column': DataSchema.YEAR}, ]

x = DataSchema.ID_REGION
y = DataSchema.VALUE_TWh
category = DataSchema.ID_ENERGY_CARRIER

# -------------------- DATA TABLES --------------------


# -------------------- PAGE LAYOUT --------------------
layout = html.Div(children=[
    dropdown.render(data, SCENARIO_DROPDOWN, DataSchema.ID_SCENARIO, SELECT_ALL_SCENARIOS_BUTTON),
    dropdown.render(data, REGION_DROPDOWN, DataSchema.ID_REGION, SELECT_ALL_REGIONS_BUTTON),
    dropdown.render(data, SECTOR_DROPDOWN, DataSchema.ID_SECTOR, SELECT_ALL_SECTORS_BUTTON),
    dropdown.render(data, YEAR_DROPDOWN, DataSchema.YEAR, SELECT_ALL_YEARS_BUTTON),
    html.H4("Model Results", style={'textAlign': 'center'}),
    stacked_bar_chart.render(data,
                             id_barchart="bar-chart-region",
                             dropdowns=dropdowns,
                             x=x,
                             y=y,
                             category=category),
    html.H4("Reference Data", style={'textAlign': 'center'}),
    stacked_bar_chart.render(reference,
                             id_barchart="bar-chart-region-reference",
                             dropdowns=[{'id': REGION_DROPDOWN, 'column': DataSchema.ID_REGION},
                                        {'id': SECTOR_DROPDOWN, 'column': DataSchema.ID_SECTOR},
                                        #{'id': YEAR_DROPDOWN, 'column': DataSchema.YEAR},
                                        ],
                             x=x,
                             y=y,
                             category=category),
],
)
