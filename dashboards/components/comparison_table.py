import pandas as pd
import plotly.express as px

from dash import dash_table, html, callback
from dash.dependencies import Input, Output
from dash.dash_table import FormatTemplate


def render(id_comparison, id_data, id_reference, id_absolute, id_relative, x, coloring='column') -> html.Div:
    @callback(
        Output(id_comparison, "children"),
        [Input(id_data, "children"), Input(id_reference, "children")]
    )
    def update_data_table(data, reference):
        # If no data is selected, return empty string
        if len(data) == 0:
            return ""
        data_df = pd.DataFrame(data[1]['props']['data'])
        reference_df = pd.DataFrame(reference[1]['props']['data'])

        end_use = list(data_df.columns)
        end_use.remove(x)

        absolute = data_df[end_use] - reference_df[end_use]
        absolute.insert(loc=0, column=x, value=data_df[x])
        # Round every entry to no digits after the decimal point
        absolute = absolute.round(2)
        absolute = absolute.fillna(0)

        relative = pd.DataFrame()
        for column in end_use:
            relative[column] = (data_df[column] - reference_df[column]).div(reference_df[column])
        relative.insert(loc=0, column=x, value=data_df[x])
        # Round every entry to no digits after the decimal point
        relative = relative.fillna(0)
        relative = relative.round(4)

        if coloring == 'column':
            absolute_styles = get_styles_for_data_table_column(absolute)
            relative_styles = get_styles_for_data_table_column(relative)
        elif coloring == 'row':
            absolute_styles = get_styles_for_data_table_row(absolute)
            relative_styles = get_styles_for_data_table_row(relative)
        else:
            absolute_styles = []
            relative_styles = []

        absolute_html = html.Div(className='table-container',
                                 id=id_absolute,
                                 children=[html.H6("Absolute difference in TWh"),
                                           dash_table.DataTable(absolute.to_dict('records'),
                                                                [{"name": i, "id": i} for i in absolute.columns],
                                                                style_cell_conditional=[
                                                                    {'if': {'column_id': x},
                                                                     'textAlign': 'left'}],
                                                                style_data_conditional=absolute_styles)
                                           ])

        column_dict = [{"name": x, "id": x}]
        column_dict.extend(
            [{"name": i, "id": i, "type": 'numeric', 'format': FormatTemplate.percentage(2)} for i in end_use])
        relative_html = html.Div(className='table-container',
                                 id=id_relative,
                                 children=[html.H6("Relative difference"),
                                           dash_table.DataTable(relative.to_dict('records'),
                                                                columns=column_dict,
                                                                style_cell_conditional=[
                                                                    {'if': {'column_id': x},
                                                                     'textAlign': 'left'}],
                                                                style_data_conditional=relative_styles)
                                           ])
        return [absolute_html, relative_html]

    return html.Div(className='flex-container', id=id_comparison)


def get_styles_for_data_table_column(df):
    # Select numeric columns
    numeric_columns = df.select_dtypes(include='number')

    # Define the colormap
    colormap = px.colors.sequential.RdBu[::-1]  # Reverse and truncate for proper interpolation

    styles = []
    for column in numeric_columns:
        # Get min and max values
        min_val = df[column].min()
        max_val = df[column].max()
        extreme_val = max(abs(min_val), abs(max_val))
        for i, value in df[column].items():
            if pd.notna(value):  # Exclude NaN values
                color = get_interpolated_color(colormap, value, -1 * extreme_val, extreme_val)
                text_color = get_text_color(color)
                styles.append({
                    'if': {'column_id': column, 'row_index': i},
                    'backgroundColor': color,
                    'color': text_color
                })

    return styles


def get_styles_for_data_table_row(df):
    # Select numeric columns
    numeric_columns = df.select_dtypes(include='number')

    # Define the colormap
    colormap = px.colors.sequential.RdBu[::-1]  # Reverse and truncate for proper interpolation
    row_min_val = numeric_columns.min(axis=1)
    row_max_val = numeric_columns.max(axis=1)

    styles = []

    for i, row in df.iterrows():
        # Get min and max values within the row
        min_val = row_min_val[i]
        max_val = row_max_val[i]
        extreme_val = max(abs(min_val), abs(max_val))
        for column in numeric_columns:
            value = row[column]
            if pd.notna(value):  # Exclude NaN values
                color = get_interpolated_color(colormap, value, -1 * extreme_val, extreme_val)
                text_color = get_text_color(color)
                styles.append({
                    'if': {'column_id': column, 'row_index': i},
                    'backgroundColor': color,
                    'color': text_color
                })

    return styles


def get_interpolated_color(colormap, value, min_val, max_val):
    # Normalize the value between 0 and 1 based on the min and max values
    normalized_value = (value - min_val) / (max_val - min_val)
    # Ensure the normalized value is within [0, 1]
    normalized_value = max(0, min(1, normalized_value))
    # Get the index of the color stop in the colormap
    index = int(normalized_value * (len(colormap) - 1))
    # Get the color from the colormap at the computed index
    return colormap[index]


def get_text_color(background_color):
    # Extract RGB values from the background_color string
    rgb_values = [int(value) for value in background_color.strip('rgb()').split(',')]
    # Calculate the luminance of the background color
    luminance = (0.299 * rgb_values[0] + 0.587 * rgb_values[1] + 0.114 * rgb_values[2]) / 255
    # Decide text color based on luminance threshold
    if luminance > 0.5:
        return 'black'
    else:
        return 'white'
