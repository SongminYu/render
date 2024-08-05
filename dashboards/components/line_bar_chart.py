import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from dash import dcc, html, callback
from dash.dependencies import Input, Output


def render(data, reference, id_line_barchart, dropdowns, reference_dropdowns, x, y, category) -> html.Div:
    """
        Render function to create a Dash Div element containing a bar chart with line overlays for comparison.

        Parameters:
            data: DataFrame containing the main data
            reference: DataFrame containing the reference data
            id_line_barchart: ID of the Dash element containing the bar chart
            dropdowns: List of dictionaries with dropdown information,
                keys: 'id' (ID of the dropdown) and 'column' (the respective column in data to apply the filter)
            reference_dropdowns: List of dictionaries with dropdown information for reference data,
                keys: 'id' (ID of the dropdown) and 'column' (the respective column in data to apply the filter)
            x: Column of data to be used for the x-axis in the bar chart
            y: Column of data to be used for the y-axis in the bar chart
            category: Column of data to be used as categories (colors) in the bar chart

        Return: Dash Div element containing the bar chart with line overlays
    """

    # Extract the IDs of the dropdowns from the list of dictionaries
    dropdown_ids = [dropdown['id'] for dropdown in dropdowns]

    @callback(
        Output(id_line_barchart, "children"),
        [Input(id, "value") for id in dropdown_ids],
    )
    def update_bar_chart(*values: list[str]):
        # Create a dictionary to map dropdown IDs to their selected values
        value_dict = dict(zip(dropdown_ids, values))

        # Build query to filter data based on dropdown values
        filters = ' & '.join([f"{dropdown['column']} in {values[i]}" for i, dropdown in enumerate(dropdowns)])
        filtered_data = data.query(filters)

        # Build query to filter reference data based on dropdown values
        reference_filters = ' & '.join(
            [f"{dropdown['column']} in {value_dict[dropdown['id']]}" for i, dropdown in enumerate(reference_dropdowns)])
        filtered_reference = reference.query(reference_filters)

        # If no data is selected, return a message
        if filtered_data.shape[0] == 0:
            return html.Div("No data selected.", id=id_line_barchart)

        # Group data for the bar chart
        grouped_data = filtered_data.groupby([x, category])[y].sum().reset_index()

        # Ensure that x and category columns are treated as strings
        grouped_data[x] = grouped_data[x].astype(str)
        grouped_data[category] = grouped_data[category].astype(str)

        # Create a bar chart using Plotly Express
        fig = px.bar(grouped_data, x=x, y=y,
                     color=category, color_discrete_sequence=px.colors.qualitative.Bold,
                     labels={'x': x, 'y': y})

        # Group reference data for the line overlay
        grouped_reference_data = filtered_reference.groupby([x])[y].sum().reset_index()
        grouped_reference_data[x] = grouped_reference_data[x].astype(str)

        # Ensure that the reference data only includes x labels present in the grouped data
        x_labels = list(grouped_data[x].unique())
        grouped_reference_data = grouped_reference_data[grouped_reference_data[x].isin(x_labels)]

        # Add a line trace to the bar chart using Plotly Graph Objects
        fig.add_trace(go.Scatter(x=grouped_reference_data[x], y=grouped_reference_data[y], # mode="lines",
                                 line=go.scatter.Line(color="blue"), fillcolor='blue', name='reference data'))

        return dcc.Graph(figure=fig)

    return html.Div(id=id_line_barchart)
