import dash
from dash import html, dcc

from dashboards.data.loader import DataSchema_Heating_Reference as DataSchema
from dashboards.data.loader import DataSchema_Nuts1_Building_Stock as DataSchema_Results
from dashboards.data import loader
from dashboards.components import (
    dots_bar_chart,
    data_table,
    dropdown,
    comparison_table,
)

# Dashboard to analyze the building stock for the model wrt. to the share of heating technologies

dash.register_page(__name__, path='/heating_technologies_share', name="Heating Technologies Share")

# -------------------- IDs --------------------
SCENARIO_DROPDOWN = "scenario-dropdown-heating-share"
SELECT_ALL_SCENARIOS_BUTTON = "select-all-scenarios-button-heating-share"

REGION_DROPDOWN = "region-dropdown-heating-share"
SELECT_ALL_REGIONS_BUTTON = "select-all-regions-button-heating-share"

YEAR_DROPDOWN = "year-dropdown-heating-share"
SELECT_ALL_YEARS_BUTTON = "select-all-years-button-heating-share"

BAR_CHART = "bar-chart-heating-share"

DATA_TABLE = "data-table-heating-share"
DATA_TABLE_REFERENCE = "data-table-reference-heating-share"

# -------------------- LOAD DATASET --------------------
print("Load data for Heating Technologies Share...")
data = loader.load_nuts1_heating_data()
reference = loader.load_regional_reference_heating_data()

# -------------------- VARIABLES --------------------
id_heating_technologies = list(data[DataSchema.ID_HEATING_TECHNOLOGY].unique())
id_heating_technologies.sort()

regions = list(data[DataSchema.ID_REGION].unique())
regions.sort()

dropdowns = [{'id': SCENARIO_DROPDOWN, 'column': DataSchema_Results.ID_SCENARIO},
             {'id': REGION_DROPDOWN, 'column': DataSchema.ID_REGION},
             {'id': YEAR_DROPDOWN, 'column': DataSchema.YEAR},]

x = DataSchema.ID_REGION
x_options = regions
y = DataSchema.SHARE_PERCENTAGE
category = DataSchema.ID_HEATING_TECHNOLOGY
category_options = id_heating_technologies

# -------------------- DATA TABLES --------------------
region_table = data_table.render(data,
                                 id_datatable=DATA_TABLE,
                                 title='Model Results: Percentage of Buildings',
                                 dropdowns=dropdowns,
                                 x=category,
                                 x_options=category_options,
                                 y=y,
                                 category=x,
                                 category_options=x_options)

reference_table = data_table.render(reference,
                                    id_datatable=DATA_TABLE_REFERENCE,
                                    title='Reference Data: Percentage of Buildings',
                                    dropdowns=[{'id': REGION_DROPDOWN, 'column': DataSchema.ID_REGION},
                                               {'id': YEAR_DROPDOWN, 'column': DataSchema.YEAR},],
                                    x=category,
                                    x_options=category_options,
                                    y=y,
                                    category=x,
                                    category_options=x_options)

# -------------------- PAGE LAYOUT --------------------
layout = html.Div(children=[
    html.H2("Heating Technologies Share"),
    dropdown.render(data, reference, SCENARIO_DROPDOWN, DataSchema_Results.ID_SCENARIO, SELECT_ALL_SCENARIOS_BUTTON),
    dropdown.render(data, reference, REGION_DROPDOWN, DataSchema.ID_REGION, SELECT_ALL_REGIONS_BUTTON),
    dropdown.render(reference, reference, YEAR_DROPDOWN, DataSchema.YEAR, SELECT_ALL_YEARS_BUTTON),
    dcc.Loading(children=[html.H4("Model Results", style={'textAlign': 'center'}),
                          dots_bar_chart.render(data,
                                                reference,
                                                id_dots_barchart=BAR_CHART,
                                                dropdowns=dropdowns,
                                                reference_dropdowns=[{'id': REGION_DROPDOWN, 'column': DataSchema.ID_REGION},
                                                                     {'id': YEAR_DROPDOWN, 'column': DataSchema.YEAR},],
                                                x=x,
                                                y=y,
                                                category=category),
                          html.Div(className='flex-container', children=[region_table, reference_table]),
                          comparison_table.render("comparison-table-heating-share", DATA_TABLE, DATA_TABLE_REFERENCE,
                                                  "absolute-diff-table-heating-share", "relative-diff-table-heating-share",
                                                  category=x)
                          ])
], )
