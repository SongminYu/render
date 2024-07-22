import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from dash import dcc, html, callback
from dash.dependencies import Input, Output


def render(data, reference, id_dots_barchart, dropdowns, reference_dropdowns, x, y, category) -> html.Div:
    # Extract dropdown ids from list of dictionary of dropdowns
    dropdown_ids = [dropdown['id'] for dropdown in dropdowns]

    @callback(
        Output(id_dots_barchart, "children"),
        [Input(id, "value") for id in dropdown_ids],
    )
    def update_bar_chart(*values: list[str]):
        value_dict = dict(zip(dropdown_ids, values))
        # build query to filter in different columns, eg. for one filter f"{id_filtered_colum} in @values"
        filters = ' & '.join([f"{dropdown['column']} in {values[i]}" for i, dropdown in enumerate(dropdowns)])
        filtered_data = data.query(filters)

        reference_filters = ' & '.join(
            [f"{dropdown['column']} in {value_dict[dropdown['id']]}" for i, dropdown in enumerate(reference_dropdowns)])
        filtered_reference = reference.query(reference_filters)

        if filtered_data.shape[0] == 0:
            return html.Div("No data selected.", id=id_dots_barchart)

        # get values for stacked bar chart
        grouped_data = filtered_data.groupby([x, category])[y].sum().reset_index()

        grouped_data[x] = grouped_data[x].astype(str)
        grouped_data[category] = grouped_data[category].astype(str)

        fig = px.bar(grouped_data, x=x, y=y,
                     color=category, color_discrete_sequence=px.colors.qualitative.Bold,
                     labels={'x': x, 'y': y})

        grouped_reference_data = filtered_reference.groupby([x])[y].sum().reset_index()
        grouped_reference_data[x] = grouped_reference_data[x].astype(str)
        x_labels = list(grouped_data[x].unique())
        grouped_reference_data = grouped_reference_data[grouped_reference_data[x].isin(x_labels)]

        fig.add_trace(go.Scatter(
            x=grouped_reference_data[x],
            y=grouped_reference_data[y],
            mode='markers',  # Use 'markers' mode to display only dots
            marker=dict(size=12, color='red'),
            name='reference data'
        ))

        return dcc.Graph(figure=fig)

    return html.Div(id=id_dots_barchart)
