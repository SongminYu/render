import dash
from dash import html

from dashboards.data.loader import DataSchema_Final_Energy as DataSchema
from dashboards.data import loader
from dashboards.components import (
    stacked_bar_chart,
    data_table,
    dropdown,
    sub_dropdown,
    comparison_table,
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

END_USE_DROPDOWN = "enduse-dropdown-timeseries"
SELECT_ALL_END_USES_BUTTON = "select-all-enduses-button-timeseries"

BAR_CHART = "bar-chart-timeseries"

DATA_TABLE = "data-table-timeseries"
DATA_TABLE_REFERENCE = "data-table-reference-timeseries"

END_USE_PATH = "data/final_energy_demand_multiple_years.csv"
REFERENCE_PATH = "data/CalibrationTarget.csv"

# -------------------- LOAD DATASET --------------------
data = loader.load_data(END_USE_PATH)
data = loader.preprocess_data(data)
reference_data = loader.load_data(REFERENCE_PATH)
reference_data = loader.preprocess_data(reference_data)

# -------------------- VARIABLES --------------------
id_energy_carriers = list(data[DataSchema.ID_ENERGY_CARRIER].unique())
id_energy_carriers.sort()

years = list(data[DataSchema.YEAR].unique())
years.sort()

dropdowns = [{'id': SCENARIO_DROPDOWN, 'column': DataSchema.ID_SCENARIO},
             {'id': REGION_DROPDOWN, 'column': DataSchema.ID_REGION},
             {'id': SECTOR_DROPDOWN, 'column': DataSchema.ID_SECTOR},
             {'id': SUBSECTOR_DROPDOWN, 'column': DataSchema.ID_SUBSECTOR},
             {'id': END_USE_DROPDOWN, 'column': DataSchema.ID_END_USE},]

x = DataSchema.YEAR
x_options = years
y = DataSchema.VALUE_TWh
category = DataSchema.ID_ENERGY_CARRIER
category_options=id_energy_carriers

# -------------------- DATA TABLES --------------------
end_use_table = data_table.render(data,
                                  id_datatable=DATA_TABLE,
                                  title='Model Results in TWh',
                                  dropdowns=dropdowns,
                                  x=category,
                                  x_options=category_options,
                                  y=y,
                                  category=x,
                                  category_options=x_options)

reference_table = data_table.render(reference_data[reference_data[DataSchema.YEAR].isin(years)],
                                    id_datatable=DATA_TABLE_REFERENCE,
                                    title='Reference Data in TWh',
                                    dropdowns=[{'id': SECTOR_DROPDOWN, 'column': DataSchema.ID_SECTOR},
                                               {'id': SUBSECTOR_DROPDOWN, 'column': DataSchema.ID_SUBSECTOR},
                                               {'id': END_USE_DROPDOWN, 'column': DataSchema.ID_END_USE},],
                                    x=category,
                                    x_options=category_options,
                                    y=y,
                                    category=x,
                                    category_options=x_options)

# -------------------- PAGE LAYOUT --------------------
layout = html.Div(children=[
    dropdown.render(data, SCENARIO_DROPDOWN, DataSchema.ID_SCENARIO, SELECT_ALL_SCENARIOS_BUTTON),
    dropdown.render(data, REGION_DROPDOWN, DataSchema.ID_REGION, SELECT_ALL_REGIONS_BUTTON),
    dropdown.render(data, SECTOR_DROPDOWN, DataSchema.ID_SECTOR, SELECT_ALL_SECTORS_BUTTON),
    sub_dropdown.render(data, SUBSECTOR_DROPDOWN, SECTOR_DROPDOWN, DataSchema.ID_SUBSECTOR,
                        DataSchema.ID_SECTOR, SELECT_ALL_SUBSECTORS_BUTTON),
    dropdown.render(data, END_USE_DROPDOWN, DataSchema.ID_END_USE, SELECT_ALL_END_USES_BUTTON),
    stacked_bar_chart.render(data,
                             id_barchart=BAR_CHART,
                             dropdowns=dropdowns,
                             x=x,
                             y=y,
                             category=category),
    html.Div(className='flex-container', children=[end_use_table, reference_table]),
    comparison_table.render("comparison-table-timeseries", DATA_TABLE, DATA_TABLE_REFERENCE,
                            "absolute-diff-table-timeseries", "relative-diff-table-timeseries", category=x, coloring='row')
], )
