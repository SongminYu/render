import dash
from dash import html, dcc

from dashboards.data.loader import DataSchema_Final_Energy as DataSchema
from dashboards.data import loader
from dashboards.components import (
    data_table,
    dropdown,
    sub_dropdown,
    comparison_table,
    line_bar_chart,
)

dash.register_page(__name__, path='/national_timeseries_analysis', name="National Timeseries Calibration")

# -------------------- IDs --------------------
SCENARIO_DROPDOWN = "scenario-dropdown-timeseries"
SELECT_ALL_SCENARIOS_BUTTON = "select-all-scenarios-button-timeseries"

REGION_DROPDOWN = "region-dropdown-timeseries"
SELECT_ALL_REGIONS_BUTTON = "select-all-regions-button-timeseries"

SECTOR_DROPDOWN = "sector-dropdown-timeseries"
SELECT_ALL_SECTORS_BUTTON = "select-all-sectors-button-timeseries"

SUBSECTOR_DROPDOWN = "subsector-dropdown-timeseries"
SELECT_ALL_SUBSECTORS_BUTTON = "select-all-subsectors-button-timeseries"

BAR_CHART = "bar-chart-timeseries"
LINE_BAR_CHART_EC = "line-bar-chart-energy-carrier-timeseries"
LINE_BAR_CHART_EU = "line-bar-chart-end-use-timeseries"
LINE_BAR_CHART_EC_1 = "line-bar-chart-energy-carrier-1-timeseries"
LINE_BAR_CHART_EC_2 = "line-bar-chart-energy-carrier-2-timeseries"
LINE_BAR_CHART_EC_3 = "line-bar-chart-energy-carrier-3-timeseries"
LINE_BAR_CHART_EC_4 = "line-bar-chart-energy-carrier-4-timeseries"

DATA_TABLE_EC = "data-table-energy-carrier-timeseries"
DATA_TABLE_REFERENCE_EC = "data-table-reference-energy-carrier-timeseries"
DATA_TABLE_COMPARISON_EC = "comparison-table-energy-carrier-timeseries"
DATA_TABLE_ABSOLUTE_DIFF_EC = "absolute-diff-table-energy-carrier-timeseries"
DATA_TABLE_RELATIVE_DIFF_EC = "relative-diff-table-energy-carrier-timeseries"

DATA_TABLE_EU = "data-table-end-use-timeseries"
DATA_TABLE_REFERENCE_EU = "data-table-reference-end-use-timeseries"
DATA_TABLE_COMPARISON_EU = "comparison-table-end-use-timeseries"
DATA_TABLE_ABSOLUTE_DIFF_EU = "absolute-diff-table-end-use-timeseries"
DATA_TABLE_RELATIVE_DIFF_EU = "relative-diff-table-end-use-timeseries"

DATA_TABLE_EC_1 = "data-table-energy-carrier-1-timeseries"
DATA_TABLE_REFERENCE_EC_1 = "data-table-reference-energy-carrier-1-timeseries"
DATA_TABLE_COMPARISON_EC_1 = "comparison-table-energy-carrier-1-timeseries"
DATA_TABLE_ABSOLUTE_DIFF_EC_1 = "absolute-diff-table-energy-carrier-1-timeseries"
DATA_TABLE_RELATIVE_DIFF_EC_1 = "relative-diff-table-energy-carrier-1-timeseries"

DATA_TABLE_EC_2 = "data-table-energy-carrier-2-timeseries"
DATA_TABLE_REFERENCE_EC_2 = "data-table-reference-energy-carrier-2-timeseries"
DATA_TABLE_COMPARISON_EC_2 = "comparison-table-energy-carrier-2-timeseries"
DATA_TABLE_ABSOLUTE_DIFF_EC_2 = "absolute-diff-table-energy-carrier-2-timeseries"
DATA_TABLE_RELATIVE_DIFF_EC_2 = "relative-diff-table-energy-carrier-2-timeseries"

DATA_TABLE_EC_3 = "data-table-energy-carrier-3-timeseries"
DATA_TABLE_REFERENCE_EC_3 = "data-table-reference-energy-carrier-3-timeseries"
DATA_TABLE_COMPARISON_EC_3 = "comparison-table-energy-carrier-3-timeseries"
DATA_TABLE_ABSOLUTE_DIFF_EC_3 = "absolute-diff-table-energy-carrier-3-timeseries"
DATA_TABLE_RELATIVE_DIFF_EC_3 = "relative-diff-table-energy-carrier-3-timeseries"

DATA_TABLE_EC_4 = "data-table-energy-carrier-4-timeseries"
DATA_TABLE_REFERENCE_EC_4 = "data-table-reference-energy-carrier-4-timeseries"
DATA_TABLE_COMPARISON_EC_4 = "comparison-table-energy-carrier-4-timeseries"
DATA_TABLE_ABSOLUTE_DIFF_EC_4 = "absolute-diff-table-energy-carrier-4-timeseries"
DATA_TABLE_RELATIVE_DIFF_EC_4 = "relative-diff-table-energy-carrier-4-timeseries"

# -------------------- LOAD DATASET --------------------
print("Load data for National Timeseries Calibration...")
data = loader.load_energy_data()
reference_data = loader.load_national_reference_data()
print("Finished!")

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

# -------------------- ENERGY CARRIER DATA TABLES --------------------
ec_table = data_table.render(data,
                             id_datatable=DATA_TABLE_EC,
                             title='Model Results in TWh',
                             dropdowns=dropdowns,
                             x=category,
                             x_options=category_options,
                             y=y,
                             category=x,
                             category_options=x_options)

ec_reference_table = data_table.render(reference_data[reference_data[DataSchema.YEAR].isin(years)],
                                       id_datatable=DATA_TABLE_REFERENCE_EC,
                                       title='Reference Data in TWh',
                                       dropdowns=reference_dropdowns,
                                       x=category,
                                       x_options=category_options,
                                       y=y,
                                       category=x,
                                       category_options=x_options)

# -------------------- END USE DATA TABLES --------------------
eu_table = data_table.render(data,
                             id_datatable=DATA_TABLE_EU,
                             title='Model Results in TWh',
                             dropdowns=dropdowns,
                             x=enduse,
                             x_options=enduse_options,
                             y=y,
                             category=x,
                             category_options=x_options)

eu_reference_table = data_table.render(reference_data[reference_data[DataSchema.YEAR].isin(years)],
                                       id_datatable=DATA_TABLE_REFERENCE_EU,
                                       title='Reference Data in TWh',
                                       dropdowns=reference_dropdowns,
                                       x=enduse,
                                       x_options=enduse_options,
                                       y=y,
                                       category=x,
                                       category_options=x_options)

# -------------------- END USE 1 DATA TABLES --------------------
data_1 = data[data[enduse] == 1]
reference_data_1 = reference_data[reference_data[enduse] == 1]

ec_1_table = data_table.render(data_1,
                               id_datatable=DATA_TABLE_EC_1,
                               title='Model Results in TWh',
                               dropdowns=dropdowns,
                               x=category,
                               x_options=category_options,
                               y=y,
                               category=x,
                               category_options=x_options)

ec_1_reference_table = data_table.render(reference_data_1[reference_data_1[DataSchema.YEAR].isin(years)],
                                         id_datatable=DATA_TABLE_REFERENCE_EC_1,
                                         title='Reference Data in TWh',
                                         dropdowns=reference_dropdowns,
                                         x=category,
                                         x_options=category_options,
                                         y=y,
                                         category=x,
                                         category_options=x_options)

# -------------------- END USE 1 DATA TABLES --------------------
data_2 = data[data[enduse] == 2]
reference_data_2 = reference_data[reference_data[enduse] == 2]

ec_2_table = data_table.render(data_2,
                               id_datatable=DATA_TABLE_EC_2,
                               title='Model Results in TWh',
                               dropdowns=dropdowns,
                               x=category,
                               x_options=category_options,
                               y=y,
                               category=x,
                               category_options=x_options)

ec_2_reference_table = data_table.render(reference_data_2[reference_data_2[DataSchema.YEAR].isin(years)],
                                         id_datatable=DATA_TABLE_REFERENCE_EC_2,
                                         title='Reference Data in TWh',
                                         dropdowns=reference_dropdowns,
                                         x=category,
                                         x_options=category_options,
                                         y=y,
                                         category=x,
                                         category_options=x_options)

# -------------------- END USE 1 DATA TABLES --------------------
data_3 = data[data[enduse] == 3]
reference_data_3 = reference_data[reference_data[enduse] == 3]

ec_3_table = data_table.render(data_3,
                               id_datatable=DATA_TABLE_EC_3,
                               title='Model Results in TWh',
                               dropdowns=dropdowns,
                               x=category,
                               x_options=category_options,
                               y=y,
                               category=x,
                               category_options=x_options)

ec_3_reference_table = data_table.render(reference_data_3[reference_data_3[DataSchema.YEAR].isin(years)],
                                         id_datatable=DATA_TABLE_REFERENCE_EC_3,
                                         title='Reference Data in TWh',
                                         dropdowns=reference_dropdowns,
                                         x=category,
                                         x_options=category_options,
                                         y=y,
                                         category=x,
                                         category_options=x_options)

# -------------------- END USE 1 DATA TABLES --------------------
data_4 = data[data[enduse] == 4]
reference_data_4 = reference_data[reference_data[enduse] == 4]

ec_4_table = data_table.render(data_4,
                               id_datatable=DATA_TABLE_EC_4,
                               title='Model Results in TWh',
                               dropdowns=dropdowns,
                               x=category,
                               x_options=category_options,
                               y=y,
                               category=x,
                               category_options=x_options)

ec_4_reference_table = data_table.render(reference_data_4[reference_data_4[DataSchema.YEAR].isin(years)],
                                         id_datatable=DATA_TABLE_REFERENCE_EC_4,
                                         title='Reference Data in TWh',
                                         dropdowns=reference_dropdowns,
                                         x=category,
                                         x_options=category_options,
                                         y=y,
                                         category=x,
                                         category_options=x_options)

# -------------------- PAGE LAYOUT --------------------
layout = html.Div(children=[
    html.H2("National Timeseries Calibration"),
    dropdown.render(data, SCENARIO_DROPDOWN, DataSchema.ID_SCENARIO, SELECT_ALL_SCENARIOS_BUTTON),
    dropdown.render(data, REGION_DROPDOWN, DataSchema.ID_REGION, SELECT_ALL_REGIONS_BUTTON),
    dropdown.render(data, SECTOR_DROPDOWN, DataSchema.ID_SECTOR, SELECT_ALL_SECTORS_BUTTON),
    sub_dropdown.render(data, SUBSECTOR_DROPDOWN, SECTOR_DROPDOWN, DataSchema.ID_SUBSECTOR,
                        DataSchema.ID_SECTOR, SELECT_ALL_SUBSECTORS_BUTTON),
    # Energy carrier analysis
    html.H4("Analysis by Energy Carrier", style={'textAlign': 'center'}),
    dcc.Loading(children=[
        line_bar_chart.render(data, reference_data, LINE_BAR_CHART_EC, dropdowns, reference_dropdowns, x, y, category),
        html.Div(className='flex-container', children=[ec_table, ec_reference_table]),
        comparison_table.render(DATA_TABLE_COMPARISON_EC, DATA_TABLE_EC, DATA_TABLE_REFERENCE_EC,
                                DATA_TABLE_ABSOLUTE_DIFF_EC, DATA_TABLE_RELATIVE_DIFF_EC, category=x,
                                coloring='row'), ]),
    html.Hr(),
    # End use analysis
    html.H4("Analysis by End use", style={'textAlign': 'center'}),
    dcc.Loading(children=[
        line_bar_chart.render(data, reference_data, LINE_BAR_CHART_EU, dropdowns, reference_dropdowns, x, y, enduse),
        html.Div(className='flex-container', children=[eu_table, eu_reference_table]),
        comparison_table.render(DATA_TABLE_COMPARISON_EU, DATA_TABLE_EU, DATA_TABLE_REFERENCE_EU,
                                DATA_TABLE_ABSOLUTE_DIFF_EU, DATA_TABLE_RELATIVE_DIFF_EC, category=x,
                                coloring='row'), ]),
    html.Hr(),
    # Energy carrier analysis by different end uses
    html.H4("Analysis by Energy Carrier for end use 1", style={'textAlign': 'center'}),
    dcc.Loading(children=[
        line_bar_chart.render(data_1, reference_data_1, LINE_BAR_CHART_EC_1, dropdowns, reference_dropdowns, x, y,
                              category),
        html.Div(className='flex-container', children=[ec_1_table, ec_1_reference_table]),
        comparison_table.render(DATA_TABLE_COMPARISON_EC_1, DATA_TABLE_EC_1, DATA_TABLE_REFERENCE_EC_1,
                                DATA_TABLE_ABSOLUTE_DIFF_EC_1, DATA_TABLE_RELATIVE_DIFF_EC_1, category=x,
                                coloring='row'), ]),
    html.Hr(),
    html.H4("Analysis by Energy Carrier for end use 2", style={'textAlign': 'center'}),
    dcc.Loading(children=[
        line_bar_chart.render(data_2, reference_data_2, LINE_BAR_CHART_EC_2, dropdowns, reference_dropdowns, x, y,
                              category),
        html.Div(className='flex-container', children=[ec_2_table, ec_2_reference_table]),
        comparison_table.render(DATA_TABLE_COMPARISON_EC_2, DATA_TABLE_EC_2, DATA_TABLE_REFERENCE_EC_2,
                                DATA_TABLE_ABSOLUTE_DIFF_EC_2, DATA_TABLE_RELATIVE_DIFF_EC_2, category=x,
                                coloring='row'), ]),
    html.Hr(),
    html.H4("Analysis by Energy Carrier for end use 3", style={'textAlign': 'center'}),
    dcc.Loading(children=[
        line_bar_chart.render(data_3, reference_data_3, LINE_BAR_CHART_EC_3, dropdowns, reference_dropdowns, x, y,
                              category),
        html.Div(className='flex-container', children=[ec_3_table, ec_3_reference_table]),
        comparison_table.render(DATA_TABLE_COMPARISON_EC_3, DATA_TABLE_EC_3, DATA_TABLE_REFERENCE_EC_3,
                                DATA_TABLE_ABSOLUTE_DIFF_EC_3, DATA_TABLE_RELATIVE_DIFF_EC_3, category=x,
                                coloring='row'), ]),
    html.Hr(),
    html.H4("Analysis by Energy Carrier for end use 4", style={'textAlign': 'center'}),
    dcc.Loading(children=[
        line_bar_chart.render(data_4, reference_data_4, LINE_BAR_CHART_EC_4, dropdowns, reference_dropdowns, x, y,
                              category),
        html.Div(className='flex-container', children=[ec_4_table, ec_4_reference_table]),
        comparison_table.render(DATA_TABLE_COMPARISON_EC_4, DATA_TABLE_EC_4, DATA_TABLE_REFERENCE_EC_4,
                                DATA_TABLE_ABSOLUTE_DIFF_EC_4, DATA_TABLE_RELATIVE_DIFF_EC_4, category=x,
                                coloring='row'), ]),

], )
