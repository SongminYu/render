import dash
from dash import html, dcc

from dashboards.data.loader import DataSchema_Final_Energy as DataSchema
from dashboards.data import loader
from dashboards.components import (
    dots_bar_chart,
    data_table,
    dropdown,
    comparison_table,
)

dash.register_page(__name__, path='/region_analysis_nuts1', name="Region Analysis Nuts 1")

# -------------------- IDs --------------------
SCENARIO_DROPDOWN = "scenario-dropdown-region"
SELECT_ALL_SCENARIOS_BUTTON = "select-all-scenarios-button-region"

REGION_DROPDOWN = "region-dropdown-region"
SELECT_ALL_REGIONS_BUTTON = "select-all-regions-button-region"

SECTOR_DROPDOWN = "sector-dropdown-region"
SELECT_ALL_SECTORS_BUTTON = "select-all-sectors-button-region"

YEAR_DROPDOWN = "year-dropdown-region"
SELECT_ALL_YEARS_BUTTON = "select-all-years-button-region"

BAR_CHART = "bar-chart-region"

DATA_TABLE = "data-table-region"
DATA_TABLE_REFERENCE = "data-table-reference-region"

# -------------------- LOAD DATASET --------------------
print("Load data for Regional Analysis...")
data = loader.load_nuts1_data()
reference = loader.load_regional_reference_data()

# -------------------- VARIABLES --------------------
id_energy_carriers = list(data[DataSchema.ID_ENERGY_CARRIER].unique())
id_energy_carriers.sort()

regions = list(data[DataSchema.ID_REGION].unique())
regions.sort()

dropdowns = [{'id': SCENARIO_DROPDOWN, 'column': DataSchema.ID_SCENARIO},
             {'id': REGION_DROPDOWN, 'column': DataSchema.ID_REGION},
             {'id': SECTOR_DROPDOWN, 'column': DataSchema.ID_SECTOR},
             {'id': YEAR_DROPDOWN, 'column': DataSchema.YEAR}, ]

x = DataSchema.ID_REGION
x_options = regions
y = DataSchema.VALUE_TWh
category = DataSchema.ID_ENERGY_CARRIER
category_options = id_energy_carriers

# -------------------- DATA TABLES --------------------
region_table = data_table.render(data,
                                 id_datatable=DATA_TABLE,
                                 title='Model Results in TWh',
                                 dropdowns=dropdowns,
                                 x=category,
                                 x_options=category_options,
                                 y=y,
                                 category=x,
                                 category_options=x_options)

reference_table = data_table.render(reference,
                                    id_datatable=DATA_TABLE_REFERENCE,
                                    title='Reference Data in TWh',
                                    dropdowns=[{'id': REGION_DROPDOWN, 'column': DataSchema.ID_REGION},
                                               {'id': SECTOR_DROPDOWN, 'column': DataSchema.ID_SECTOR},
                                               {'id': YEAR_DROPDOWN, 'column': DataSchema.YEAR}, ],
                                    x=category,
                                    x_options=category_options,
                                    y=y,
                                    category=x,
                                    category_options=x_options)

# -------------------- PAGE LAYOUT --------------------
layout = html.Div(children=[
    html.H2("Region Analysis"),
    dropdown.render(data, reference, SCENARIO_DROPDOWN, DataSchema.ID_SCENARIO, SELECT_ALL_SCENARIOS_BUTTON),
    dropdown.render(data, reference, REGION_DROPDOWN, DataSchema.ID_REGION, SELECT_ALL_REGIONS_BUTTON),
    dropdown.render(data, reference, SECTOR_DROPDOWN, DataSchema.ID_SECTOR, SELECT_ALL_SECTORS_BUTTON),
    dropdown.render(reference, reference, YEAR_DROPDOWN, DataSchema.YEAR, SELECT_ALL_YEARS_BUTTON),
    dcc.Loading(children=[html.H4("Model Results", style={'textAlign': 'center'}),
                          dots_bar_chart.render(data,
                                                reference,
                                                id_dots_barchart=BAR_CHART,
                                                dropdowns=dropdowns,
                                                reference_dropdowns=[
                                                    {'id': REGION_DROPDOWN, 'column': DataSchema.ID_REGION},
                                                    {'id': SECTOR_DROPDOWN, 'column': DataSchema.ID_SECTOR},
                                                    {'id': YEAR_DROPDOWN, 'column': DataSchema.YEAR},
                                                    ],
                                                x=x,
                                                y=y,
                                                category=category),
                          html.Div(className='flex-container', children=[region_table, reference_table]),
                          comparison_table.render("comparison-table-region", DATA_TABLE, DATA_TABLE_REFERENCE,
                                                  "absolute-diff-table-region", "relative-diff-table-region",
                                                  category=x)
                          ])
], )
