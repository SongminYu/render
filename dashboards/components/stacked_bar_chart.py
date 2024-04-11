import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html
from dash.dependencies import Input, Output


def render(app: Dash, data: pd.DataFrame, id_barchart, dropdowns, x, y, category) -> html.Div:
    # dropdowns here: list of dictionary of dropdowns,
    # One dictionary has keys 'id' (of dropdown) and
    # 'column' (respective column in data in which the filter should be applied)

    # Extract dropdown ids from list of dictionary of dropdowns
    dropdown_ids = [dropdown['id'] for dropdown in dropdowns]

    @app.callback(
        Output(id_barchart, "children"),
        [Input(id, "value") for id in dropdown_ids],
    )
    def update_bar_chart(*values: list[str]):
        # build query to filter in different columns, eg. for one filter f"{id_filtered_colum} in @values"
        filters = ' & '.join([f"{dropdown['column']} in {values[i]}" for i, dropdown in enumerate(dropdowns)])
        filtered_data = data.query(filters)

        if filtered_data.shape[0] == 0:
            return "No data selected."

        # get values for stacked bar chart
        grouped_data = filtered_data.groupby([x, category])[y].sum().reset_index()

        grouped_data.columns = grouped_data.columns.astype(str)
        grouped_data['id_energy_carrier'] = grouped_data['id_energy_carrier'].astype(str)

        fig = px.bar(grouped_data, x=x, y=y,
                     color=category, color_discrete_sequence=px.colors.qualitative.Bold,
                     labels={'x': 'End Use', 'y': 'Total demand'})

        return dcc.Graph(figure=fig)

    return html.Div(id=id_barchart)
