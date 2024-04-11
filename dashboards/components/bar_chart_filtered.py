import pandas as pd
import plotly.express as px

from dash import dcc, html, callback
from dash.dependencies import Input, Output


def render(data: pd.DataFrame, id_barchart, dropdowns, x, y) -> html.Div:
    # dropdowns here: list of dictionary of dropdowns,
    # One dictionary has keys 'id' (of dropdown) and
    # 'column' (respective column in data in which the filter should be applied)

    # Extract dropdown ids from list of dictionary of dropdowns
    dropdown_ids = [dropdown['id'] for dropdown in dropdowns]

    @callback(
        Output(id_barchart, "children"),
        [Input(id, "value") for id in dropdown_ids],
    )
    def update_bar_chart(*values: list[str]) -> html.Div:

        # build query to filter in different columns, eg. for one filter f"{id_filtered_colum} in @values"
        filters = ' & '.join([f"{dropdown['column']} in {values[i]}" for i, dropdown in enumerate(dropdowns)])
        filtered_data = data.query(filters)

        if filtered_data.shape[0] == 0:
            return html.Div("No data selected.", id=id_barchart)

        def create_pivot_table() -> pd.DataFrame:
            pt = filtered_data.pivot_table(
                values=y,
                index=[x],
                aggfunc="sum",
                fill_value=0,
                dropna=False,
            )
            return pt.reset_index()

        fig = px.bar(create_pivot_table(), x=x, y=y, color=x)

        return html.Div(dcc.Graph(figure=fig), id=id_barchart)

    return html.Div(id=id_barchart)
