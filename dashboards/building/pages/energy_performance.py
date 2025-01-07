import dash
from dash import html, dcc

from dashboards.building.data.loader import DataSchema_Energy_Performance as DataSchema
from dashboards.building.data.loader import DataSchema_Nuts1_Building_Stock as DataSchema_Results
from dashboards.building.data import loader
from dashboards.building.components import comparison_table, dropdown, data_table, dots_bar_chart

# Dashboard to analyze the building stock for the model wrt. to the share of heating technologies

dash.register_page(__name__, path='/energy_performance', name="Energy Performance")

# -------------------- IDs --------------------
SCENARIO_DROPDOWN = "scenario-dropdown-energy-performance"
SELECT_ALL_SCENARIOS_BUTTON = "select-all-scenarios-button-energy-performance"

REGION_DROPDOWN = "region-dropdown-energy-performance"
SELECT_ALL_REGIONS_BUTTON = "select-all-regions-button-energy-performance"

YEAR_DROPDOWN = "year-dropdown-energy-performance"
SELECT_ALL_YEARS_BUTTON = "select-all-years-button-energy-performance"

BAR_CHART = "bar-chart-energy-performance"

DATA_TABLE = "data-table-energy-performance"
DATA_TABLE_REFERENCE = "data-table-reference-energy-performance"

# -------------------- LOAD DATASET --------------------
print("Load data for Energy Performance...")
data = loader.load_nuts1_efficiency_data()
reference = loader.load_reference_efficiency_data()

# -------------------- VARIABLES --------------------
id_building_type = list(data[DataSchema.ID_BUILDING_TYPE].unique())
id_building_type.sort()

efficiency_class = list(data[DataSchema.ID_EFFICIENCY_CLASS].unique())
efficiency_class.sort()

dropdowns = [{'id': SCENARIO_DROPDOWN, 'column': DataSchema_Results.ID_SCENARIO},
             {'id': REGION_DROPDOWN, 'column': DataSchema.ID_REGION},
             {'id': YEAR_DROPDOWN, 'column': DataSchema.YEAR}, ]

x = DataSchema.ID_EFFICIENCY_CLASS
x_options = efficiency_class
y = DataSchema.PERCENTAGE_BUILDING_NUMBER
category = DataSchema.ID_BUILDING_TYPE
category_options = id_building_type

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
                                    dropdowns=[{'id': REGION_DROPDOWN, 'column': DataSchema.ID_REGION},
                                               {'id': YEAR_DROPDOWN, 'column': DataSchema.YEAR},],
                                    x=category,
                                    x_options=category_options,
                                    y=y,
                                    category=x,
                                    category_options=x_options)

# -------------------- PAGE LAYOUT --------------------
layout = html.Div(children=[
    html.H2("Energy Performance"),
    dropdown.render(data, reference, SCENARIO_DROPDOWN, DataSchema_Results.ID_SCENARIO, SELECT_ALL_SCENARIOS_BUTTON),
    dropdown.render(data, reference, REGION_DROPDOWN, DataSchema.ID_REGION, SELECT_ALL_REGIONS_BUTTON),
    dropdown.render(data, reference, YEAR_DROPDOWN, DataSchema.YEAR, SELECT_ALL_YEARS_BUTTON),
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
                          comparison_table.render("comparison-table-energy-performance", DATA_TABLE, DATA_TABLE_REFERENCE,
                                                  "absolute-diff-table-energy-performance", "relative-diff-table-energy-performance",
                                                  category=x)
                          ])
], )
