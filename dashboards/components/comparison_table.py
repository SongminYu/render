import pandas as pd
import numpy as np
import plotly.express as px

from dash import dash_table, html, callback
from dash.dependencies import Input, Output
from dash.dash_table import FormatTemplate


def render(id_comparison, id_data, id_reference, id_absolute, id_relative, category) -> html.Div:
    """
        Render function to create a Dash Div element containing comparison tables (absolute and relative differences)
        between data and reference datasets.

        Parameters:
            id_comparison: ID of the Dash element containing the comparison tables
            id_data: ID of the Dash element containing the data table
            id_reference: ID of the Dash element containing the reference table
            id_absolute: ID of the Dash element containing the absolute difference table
            id_relative: ID of the Dash element containing the relative difference table
            category: Column name of data to be used as the category for comparisons (Columns of tables)

        Return: Dash Div element containing the comparison tables
    """
    @callback(
        Output(id_comparison, "children"),
        [Input(id_data, "children"), Input(id_reference, "children")]
    )
    def update_data_table(data, reference):
        # If no data is selected, return an empty string
        if len(data) == 0:
            return ""

        # Convert data and reference tables to DataFrames
        data_df = pd.DataFrame(data[1]['props']['data'])
        reference_df = pd.DataFrame(reference[1]['props']['data'])

        # Get list of columns excluding the category column
        columns = list(data_df.columns)
        columns.remove(category)

        # Calculate absolute differences
        absolute = data_df[columns] - reference_df[columns]
        absolute.insert(loc=0, column=category, value=data_df[category])
        absolute = absolute.round(2).fillna(0)  # Round to 2 decimal places and fill NaN with 0

        # Calculate relative differences
        relative = pd.DataFrame()
        for column in columns:
            relative[column] = (data_df[column] - reference_df[column]).div(reference_df[column])

        zeros_in_reference = (reference_df == 0)  # Identify zeros in reference data table
        relative[zeros_in_reference] = 0  # Set corresponding cells in relative difference table to 0
        relative.insert(loc=0, column=category, value=data_df[category])
        relative = relative.fillna(0).round(4)  # Fill NaN with 0 and round to 4 decimal places

        # Get styles for absolute and relative difference tables
        # absolute_styles = get_styles_for_data_table(absolute, extreme_val=1000)
        relative_styles = get_styles_for_data_table(relative, extreme_val=1)

        absolute_html = html.Div(className='table-container',
                                 id=id_absolute,
                                 children=[html.H6("Absolute difference in TWh"),
                                           dash_table.DataTable(absolute.to_dict('records'),
                                                                [{"name": i, "id": i} for i in absolute.columns],
                                                                style_cell_conditional=[
                                                                    {'if': {'column_id': category},
                                                                     'textAlign': 'left'}],
                                                                #style_data_conditional=absolute_styles
                                                                )
                                           ])

        # Define columns for relative difference table with percentage formatting
        column_dict = [{"name": category, "id": category}]
        column_dict.extend(
            [{"name": i, "id": i, "type": 'numeric', 'format': FormatTemplate.percentage(2)} for i in columns])

        relative_html = html.Div(className='table-container',
                                 id=id_relative,
                                 children=[html.H6("Relative difference"),
                                           dash_table.DataTable(relative.to_dict('records'),
                                                                columns=column_dict,
                                                                style_cell_conditional=[
                                                                    {'if': {'column_id': category},
                                                                     'textAlign': 'left'}],
                                                                style_data_conditional=relative_styles)
                                           ])

        return [absolute_html, relative_html]

    return html.Div(className='flex-container', id=id_comparison)


def get_styles_for_data_table(df, extreme_val):
    """
    Generate styles for Dash DataTable based on the values in the DataFrame.
    """
    # Select numeric columns from the DataFrame
    numeric_columns = df.select_dtypes(include='number')

    # Define the colormap
    colormap = px.colors.sequential.RdBu[::-1]  # Reverse and truncate for proper interpolation

    styles = []
    for column in numeric_columns:
        for i, value in df[column].items():
            if pd.notna(value):  # Exclude NaN values
                # Clip the value between -extreme_val and extreme_val
                value = max(-1 * extreme_val, value)
                value = min(extreme_val, value)

                # Get the interpolated color based on the value
                color = get_interpolated_color(colormap, value, -1 * extreme_val, extreme_val)

                # Get the appropriate text color based on background color
                text_color = get_text_color(color)

                # Append style dictionary for the DataTable
                styles.append({
                    'if': {'column_id': column, 'row_index': i},
                    'backgroundColor': color,
                    'color': text_color
                })

    return styles


def get_interpolated_color(colormap, value, min_val, max_val):
    """
    Interpolate color from the colormap based on the value.
    """
    # Normalize the value between 0 and 1 based on the min and max values
    normalized_value = (value - min_val) / (max_val - min_val)
    normalized_value = max(0, min(1, normalized_value)) # Ensure the normalized value is within [0, 1]
    # Get the index of the color stop in the colormap
    index = int(normalized_value * (len(colormap) - 1))
    # Get the color from the colormap at the computed index
    return colormap[index]


def get_text_color(background_color):
    """
    Determine the appropriate text color (black or white) based on the background color for readability.
    """
    # Extract RGB values from the background_color string
    rgb_values = [int(value) for value in background_color.strip('rgb()').split(',')]
    # Calculate the luminance of the background color
    luminance = (0.299 * rgb_values[0] + 0.587 * rgb_values[1] + 0.114 * rgb_values[2]) / 255
    # Decide text color based on luminance threshold
    if luminance > 0.5:
        return 'black'
    else:
        return 'white'
