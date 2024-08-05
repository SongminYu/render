import pandas as pd
import plotly.express as px

from dash import dcc, html, callback
from dash.dependencies import Input, Output


def render(data: pd.DataFrame, id_barchart, dropdowns, x, y, category) -> html.Div:
    """
        Creates a Dash Div containing a bar chart. The bar chart is updated based on the selected values from dropdowns.

        Parameters:
            data: DataFrame containing the data to be visualized
            id_barchart: ID for the Div element that will contain the bar chart
            dropdowns: List of dictionaries with dropdown information,
                keys: 'id' (ID of the dropdown) and 'column' (the respective column in data to apply the filter)
            x: Column of data to be used for the x-axis in the bar chart
            y: Column of data to be used for the y-axis in the bar chart
            category: Column of data to be used as categories (colors) in the bar chart

        Return: A Dash Div element containing the bar chart
    """

    # Extract the IDs of the dropdowns from the list of dictionaries
    dropdown_ids = [dropdown['id'] for dropdown in dropdowns]

    @callback(
        Output(id_barchart, "children"),
        [Input(id, "value") for id in dropdown_ids],
    )
    def update_bar_chart(*values: list[str]):
        # Build a query string to filter data based on selected dropdown values
        filters = ' & '.join([f"{dropdown['column']} in {values[i]}" for i, dropdown in enumerate(dropdowns)])
        filtered_data = data.query(filters)

        # If no data matches the filter, return a message
        if filtered_data.shape[0] == 0:
            return "No data selected."

        # Group data for the bar chart
        grouped_data = filtered_data.groupby([x, category])[y].sum().reset_index()

        # Ensure x and category columns are treated as strings for consistent plotting
        grouped_data[x] = grouped_data[x].astype(str)
        grouped_data[category] = grouped_data[category].astype(str)

        # Create a bar chart using Plotly Express
        fig = px.bar(grouped_data, x=x, y=y, color=category, color_discrete_sequence=px.colors.qualitative.Bold)

        return dcc.Graph(figure=fig)

    return html.Div(id=id_barchart)
