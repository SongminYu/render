import dash
from dash import html, dcc

from dashboards.data.loader import DataSchema_Final_Energy as DataSchema
from dashboards.data import loader
from dashboards.components import (
    dropdown,
    sub_dropdown,
    comparison_table,
    stacked_bar_chart,
)

dash.register_page(__name__, path='/region_analysis_nuts3', name="Region Analysis Nuts 3")

# -------------------- IDs --------------------
SCENARIO_DROPDOWN = "scenario-dropdown-region-nuts3"
SELECT_ALL_SCENARIOS_BUTTON = "select-all-scenarios-button-region-nuts3"

REGION_DROPDOWN = "region-dropdown-region-nuts3"
SELECT_ALL_REGIONS_BUTTON = "select-all-regions-button-region-nuts3"

SECTOR_DROPDOWN = "sector-dropdown-region-nuts3"
SELECT_ALL_SECTORS_BUTTON = "select-all-sectors-button-region-nuts3"

SUBSECTOR_DROPDOWN = "subsector-dropdown-region-nuts3"
SELECT_ALL_SUBSECTORS_BUTTON = "select-all-subsectors-button-region-nuts3"

BAR_CHART_EC = "bar-chart-energy-carrier-region-nuts3"
BAR_CHART_EU = "bar-chart-end-use-region-nuts3"
BAR_CHART_EC_1 = "bar-chart-energy-carrier-1-region-nuts3"
BAR_CHART_EC_2 = "bar-chart-energy-carrier-2-region-nuts3"
BAR_CHART_EC_3 = "bar-chart-energy-carrier-3-region-nuts3"
BAR_CHART_EC_4 = "bar-chart-energy-carrier-4-region-nuts3"

# -------------------- LOAD DATASET --------------------
print("Load data for National Timeseries Calibration...")
data = loader.load_energy_data()

# -------------------- VARIABLES --------------------
id_energy_carriers = list(data[DataSchema.ID_ENERGY_CARRIER].unique())
id_energy_carriers.sort()

years = list(data[DataSchema.YEAR].unique())
years.sort()

dropdowns = [{'id': SCENARIO_DROPDOWN, 'column': DataSchema.ID_SCENARIO},
             {'id': REGION_DROPDOWN, 'column': DataSchema.ID_REGION},
             {'id': SECTOR_DROPDOWN, 'column': DataSchema.ID_SECTOR},
             {'id': SUBSECTOR_DROPDOWN, 'column': DataSchema.ID_SUBSECTOR}, ]

reference_dropdowns = [{'id': SECTOR_DROPDOWN, 'column': DataSchema.ID_SECTOR},
                       {'id': SUBSECTOR_DROPDOWN, 'column': DataSchema.ID_SUBSECTOR}, ]

x = DataSchema.YEAR
x_options = years
y = DataSchema.VALUE_TWh
category = DataSchema.ID_ENERGY_CARRIER
category_options = id_energy_carriers

enduse = DataSchema.ID_END_USE
enduse_options = list(data[DataSchema.ID_END_USE].unique())
enduse_options.sort()

# -------------------- DATA TABLES FOR DIFFERENT END USES --------------------
data_1 = data[data[enduse] == 1]
data_2 = data[data[enduse] == 2]
data_3 = data[data[enduse] == 3]
data_4 = data[data[enduse] == 4]

# -------------------- PAGE LAYOUT --------------------
layout = html.Div(children=[
    html.H2("National Timeseries Calibration"),
    dropdown.render(data, data, SCENARIO_DROPDOWN, DataSchema.ID_SCENARIO, SELECT_ALL_SCENARIOS_BUTTON),
    dropdown.render(data, data, REGION_DROPDOWN, DataSchema.ID_REGION, SELECT_ALL_REGIONS_BUTTON),
    dropdown.render(data, data, SECTOR_DROPDOWN, DataSchema.ID_SECTOR, SELECT_ALL_SECTORS_BUTTON),
    sub_dropdown.render(data, SUBSECTOR_DROPDOWN, SECTOR_DROPDOWN, DataSchema.ID_SUBSECTOR,
                        DataSchema.ID_SECTOR, SELECT_ALL_SUBSECTORS_BUTTON),
    # Energy carrier analysis
    html.H4("Analysis by Energy Carrier", style={'textAlign': 'center'}),
    dcc.Loading(children=[
        stacked_bar_chart.render(data, BAR_CHART_EC, dropdowns, x, y, category),]),
    html.Hr(),
    # End use analysis
    html.H4("Analysis by End use", style={'textAlign': 'center'}),
    dcc.Loading(children=[
        stacked_bar_chart.render(data, BAR_CHART_EU, dropdowns, x, y, enduse), ]),
    html.Hr(),
    # Energy carrier analysis by different end uses
    html.H4("Analysis by Energy Carrier for end use 1", style={'textAlign': 'center'}),
    dcc.Loading(children=[
        stacked_bar_chart.render(data_1, BAR_CHART_EC_1, dropdowns, x, y, category), ]),
    html.Hr(),
    html.H4("Analysis by Energy Carrier for end use 2", style={'textAlign': 'center'}),
    dcc.Loading(children=[
        stacked_bar_chart.render(data_2, BAR_CHART_EC_2, dropdowns, x, y, category), ]),
    html.Hr(),
    html.H4("Analysis by Energy Carrier for end use 3", style={'textAlign': 'center'}),
    dcc.Loading(children=[
        stacked_bar_chart.render(data_3, BAR_CHART_EC_3, dropdowns, x, y, category), ]),
    html.Hr(),
    html.H4("Analysis by Energy Carrier for end use 4", style={'textAlign': 'center'}),
    dcc.Loading(children=[
        stacked_bar_chart.render(data_4, BAR_CHART_EC_4, dropdowns, x, y, category), ]),
], )
