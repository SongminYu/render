import dash
from dash import html

from dashboards.data.loader import DataSchema_Floor_Area as DataSchema
from dashboards.data import loader


from dashboards.components import (
    bar_chart_filtered,
    dropdown,
    sub_dropdown,
)

dash.register_page(__name__, path='/floor_area', name="Floor Area")

# -------------------- IDs --------------------
SECTOR_DROPDOWN = "sector-dropdown-floor"
SELECT_ALL_SECTORS_BUTTON = "select-all-sectors-button-floor"

SUBSECTOR_DROPDOWN = "subsector-dropdown-floor"
SELECT_ALL_SUBSECTORS_BUTTON = "select-all-subsectors-button-floor"

BAR_CHART = "bar-chart-floor"

# -------------------- LOAD DATASET --------------------
print("Load data for Floor Area...")
data = loader.load_floor_area_data()
print("Finished!")

# -------------------- VARIABLES --------------------
dropdowns = [{'id': SECTOR_DROPDOWN, 'column': DataSchema.ID_SECTOR},
             {'id': SUBSECTOR_DROPDOWN, 'column': DataSchema.ID_SUBSECTOR}, ]

# -------------------- PAGE LAYOUT --------------------
layout = html.Div(children=[
        html.H2("Floor Area"),
        dropdown.render(data, SECTOR_DROPDOWN, DataSchema.ID_SECTOR, SELECT_ALL_SECTORS_BUTTON),
        sub_dropdown.render(data, SUBSECTOR_DROPDOWN, SECTOR_DROPDOWN, DataSchema.ID_SUBSECTOR,
                            DataSchema.ID_SECTOR, SELECT_ALL_SUBSECTORS_BUTTON),
        bar_chart_filtered.render(data,
                                  id_barchart=BAR_CHART,
                                  dropdowns=dropdowns,
                                  x=DataSchema.ID_BUILDING_TYPE,
                                  y=DataSchema.VALUE),
    ],
)
