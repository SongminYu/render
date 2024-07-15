import dash
from dash import html, dcc

from dashboards.data.loader import DataSchema_Final_Energy as DataSchema
from dashboards.data import loader
from dashboards.components import (
    stacked_bar_chart,
    data_table,
    dropdown,
    sub_dropdown,
    comparison_table,
)

dash.register_page(__name__, path='/', name="National Year Calibration")

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

BAR_CHART = "bar-chart-enduse"

DATA_TABLE = "data-table-enduse"
DATA_TABLE_REFERENCE = "data-table-reference-enduse"

# -------------------- LOAD DATASET --------------------
print("Load data for National Year Calibration...")
data = loader.load_energy_data()
reference_data = loader.load_national_reference_data()
print("Finished!")

# -------------------- VARIABLES --------------------
id_energy_carriers = list(data[DataSchema.ID_ENERGY_CARRIER].unique())
id_energy_carriers.sort()

enduses= list(data[DataSchema.ID_END_USE].unique())
enduses.sort()

dropdowns = [{'id': SCENARIO_DROPDOWN, 'column': DataSchema.ID_SCENARIO},
             {'id': REGION_DROPDOWN, 'column': DataSchema.ID_REGION},
             {'id': SECTOR_DROPDOWN, 'column': DataSchema.ID_SECTOR},
             {'id': SUBSECTOR_DROPDOWN, 'column': DataSchema.ID_SUBSECTOR},
             {'id': YEAR_DROPDOWN, 'column': DataSchema.YEAR}, ]

x = DataSchema.ID_END_USE
x_options = enduses
y = DataSchema.VALUE_TWh
category = DataSchema.ID_ENERGY_CARRIER
category_options = id_energy_carriers

# -------------------- DATA TABLES --------------------
end_use_table = data_table.render(data,
                                  id_datatable=DATA_TABLE,
                                  title='Model Results in TWh',
                                  dropdowns=dropdowns,
                                  x=x,
                                  x_options=x_options,
                                  y=y,
                                  category=category,
                                  category_options=category_options)

reference_table = data_table.render(reference_data,
                                    id_datatable=DATA_TABLE_REFERENCE,
                                    title='Reference Data in TWh',
                                    dropdowns=[{'id': SECTOR_DROPDOWN, 'column': DataSchema.ID_SECTOR},
                                               {'id': SUBSECTOR_DROPDOWN, 'column': DataSchema.ID_SUBSECTOR},
                                               {'id': YEAR_DROPDOWN, 'column': DataSchema.YEAR}, ],
                                    x=x,
                                    x_options=x_options,
                                    y=y,
                                    category=category,
                                    category_options=category_options)

# -------------------- PAGE LAYOUT --------------------
layout = html.Div(children=[
    html.H2("National Year Calibration"),
    dropdown.render(data, SCENARIO_DROPDOWN, DataSchema.ID_SCENARIO, SELECT_ALL_SCENARIOS_BUTTON),
    dropdown.render(data, REGION_DROPDOWN, DataSchema.ID_REGION, SELECT_ALL_REGIONS_BUTTON),
    dropdown.render(data, SECTOR_DROPDOWN, DataSchema.ID_SECTOR, SELECT_ALL_SECTORS_BUTTON),
    sub_dropdown.render(data, SUBSECTOR_DROPDOWN, SECTOR_DROPDOWN, DataSchema.ID_SUBSECTOR,
                        DataSchema.ID_SECTOR, SELECT_ALL_SUBSECTORS_BUTTON),
    dropdown.render(data, YEAR_DROPDOWN, DataSchema.YEAR, SELECT_ALL_YEARS_BUTTON),
    dcc.Loading(children=[stacked_bar_chart.render(data,
                             id_barchart=BAR_CHART,
                             dropdowns=dropdowns,
                             x=x,
                             y=y,
                             category=category),
    html.Div(className='flex-container', children=[end_use_table, reference_table]),
    comparison_table.render("comparison-table-enduse", DATA_TABLE, DATA_TABLE_REFERENCE,
                            "absolute-diff-table-enduse", "relative-diff-table-enduse", category=category)]),
], )
