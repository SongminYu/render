import dash
from dash import html, dcc, dash_table

from dashboards.building.data.loader import DataSchema_Renovation_Rate as DataSchema
from dashboards.building.data import loader

import pandas as pd

# Simple dashboard which displays the floor area by id_building_type

dash.register_page(__name__, path='/renovation_rate', name="Renovation Rate")

# -------------------- IDs --------------------
DATA_TABLE = "data-table-renovation-rate"
DATA_TABLE_REFERENCE = "data-table-reference-renovation-rate"

# -------------------- LOAD DATASET --------------------
print("Load data for Renovation Rate...")
data = loader.load_renovation_rate_data()
reference = loader.load_reference_renovation_rate_data()

# -------------------- VARIABLES --------------------


# -------------------- DATA TABLES --------------------
reference_df = reference.drop(["id_building_type", "id_building_construction_period"], axis=1).iloc[:3, :]

# Combine the columns with error margin

columns_to_combine = {
    'wall': 'wall_margin',
    'window': 'window_margin',
    'basement': 'basement_margin',
    'roof': 'roof_margin'
}

# Combine columns
for col, margin_col in columns_to_combine.items():
    reference_df[col] = reference_df[col].astype(str) + ' +/- ' + reference_df[margin_col].astype(str)
    reference_df.drop(columns=[margin_col], inplace=True)

reference_table = html.Div(className='table-container', id=DATA_TABLE, children=[
    html.H6(f"Reference"),
    dash_table.DataTable(
    id='table',
    columns=[{"name": i, "id": i} for i in reference_df.columns],
    data=reference_df.to_dict('records'),
    style_table={'overflowX': 'auto'},
    style_header={'textAlign': 'center'},
    style_cell={'textAlign': 'center'},
)])

data_df = data[data[DataSchema.ID_SECTOR] == 6] #.drop(["id_scenario", ], axis=1)
data_df = data_df[data_df[DataSchema.YEAR].isin([2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019,
                                                 2020, 2021, 2022, 2023, 2024, 2025, 2026, 2027, 2028, 2029,
                                                 2030, 2031, 2032, 2033, 2034, 2035, 2036, 2037, 2038, 2039,
                                                 2040, 2041, 2042, 2043, 2044, 2045, 2046, 2047, 2048, 2049,
                                                 2050])]

# Identify the scenarios in results
scenarios = list(data[DataSchema.ID_SCENARIO].unique())
scenarios.sort()

# Combine rows in time periods
time_periods = [(2010, 2012), (2013, 2015), (2010, 2015), (2025, 2030), (2030, 2035), (2035, 2040), (2040, 2045), (2045, 2050)]
results_list = []

for scenario in scenarios:
    for start_year, end_year in time_periods:
        filtered_df = data_df[data_df['year'].between(start_year, end_year) & (data_df['id_scenario'] == scenario)]
        average_df = filtered_df[['id_scenario', 'id_region', 'id_sector', 'wall', 'window', 'roof', 'basement', 'average']].mean()
        result_df = pd.DataFrame(average_df).transpose()
        result_df['year'] = f'{start_year}-{end_year}'
        result_df = result_df[
            ['id_scenario', 'id_region', 'id_sector', 'year', 'wall', 'window', 'roof', 'basement', 'average']]  # Reorder columns
        results_list.append(result_df)

final_result_df = pd.concat(results_list, ignore_index=True)

columns_to_multiply = ['wall', 'window', 'roof', 'basement', 'average']

# Multiply the specified columns by 10
for column in columns_to_multiply:
    final_result_df[column] = (final_result_df[column] * 100).round(2)

data_table = html.Div(className='table-container', id=DATA_TABLE, children=[
    html.H6(f"Model"),
    dash_table.DataTable(
        id='table',
        columns=[{"name": i, "id": i} for i in final_result_df.columns],
        data=final_result_df.to_dict('records'),
        style_table={'overflowX': 'auto'},
        style_header={'textAlign': 'center'},
        style_cell={'textAlign': 'center'},
    )])

# -------------------- PAGE LAYOUT --------------------
layout = html.Div(children=[
    html.H2("Renovation Rate"),
    dcc.Loading(children=[html.Div(className='flex-container', children=[data_table, reference_table]),
                          ])
], )
