import dash
from dash import html, dcc

from dashboards.data.loader import DataSchema_Heating_Reference as DataSchema
from dashboards.data import loader
from dashboards.components import (
    dots_bar_chart,
    data_table,
    dropdown,
    comparison_table,
)

# Dashboard to analyze the building stock for the model wrt. to the share of heating technologies

dash.register_page(__name__, path='/heating_technologies', name="Heating Technologies")

# -------------------- IDs --------------------
REGION_DROPDOWN = "region-dropdown-heating"
SELECT_ALL_REGIONS_BUTTON = "select-all-regions-button-heating"

YEAR_DROPDOWN = "year-dropdown-heating"
SELECT_ALL_YEARS_BUTTON = "select-all-years-button-heating"

BAR_CHART = "bar-chart-heating"

DATA_TABLE = "data-table-heating"
DATA_TABLE_REFERENCE = "data-table-reference-heating"

# -------------------- LOAD DATASET --------------------
print("Load data for Heating Technologies...")
data = loader.load_nuts3_heating_data()
reference = loader.load_regional_reference_heating_data()

# -------------------- VARIABLES --------------------
id_heating_technologies = list(data[DataSchema.ID_HEATING_TECHNOLOGY].unique())
id_heating_technologies.sort()

regions = list(data[DataSchema.ID_REGION].unique())
regions.sort()

dropdowns = [{'id': REGION_DROPDOWN, 'column': DataSchema.ID_REGION},
             {'id': YEAR_DROPDOWN, 'column': DataSchema.YEAR}, ]

x = DataSchema.ID_REGION
x_options = regions
y = DataSchema.BUILDING_NUMBER
category = DataSchema.ID_HEATING_TECHNOLOGY
category_options = id_heating_technologies

# -------------------- DATA TABLES --------------------
region_table = data_table.render(data,
                                 id_datatable=DATA_TABLE,
                                 title='Model Results: Amount of Buildings',
                                 dropdowns=dropdowns,
                                 x=category,
                                 x_options=category_options,
                                 y=y,
                                 category=x,
                                 category_options=x_options)

reference_table = data_table.render(reference,
                                    id_datatable=DATA_TABLE_REFERENCE,
                                    title='Reference Data: Amount of Buildings',
                                    dropdowns=dropdowns,
                                    x=category,
                                    x_options=category_options,
                                    y=y,
                                    category=x,
                                    category_options=x_options)

# -------------------- PAGE LAYOUT --------------------
layout = html.Div(children=[
    html.H2("Heating Technologies"),
    dropdown.render(data, reference, REGION_DROPDOWN, DataSchema.ID_REGION, SELECT_ALL_REGIONS_BUTTON),
    dropdown.render(reference, reference, YEAR_DROPDOWN, DataSchema.YEAR, SELECT_ALL_YEARS_BUTTON),
    dcc.Loading(children=[html.H4("Model Results", style={'textAlign': 'center'}),
                          dots_bar_chart.render(data,
                                                reference,
                                                id_dots_barchart=BAR_CHART,
                                                dropdowns=dropdowns,
                                                reference_dropdowns=dropdowns,
                                                x=x,
                                                y=y,
                                                category=category),
                          html.Div(className='flex-container', children=[region_table, reference_table]),
                          comparison_table.render("comparison-table-heating", DATA_TABLE, DATA_TABLE_REFERENCE,
                                                  "absolute-diff-table-heating", "relative-diff-table-heating",
                                                  category=x)
                          ])
], )
