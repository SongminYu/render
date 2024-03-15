import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html
from dash.dependencies import Input, Output


def render(app: Dash, data: pd.DataFrame, id_barchart, id_dropdown, id_filtered_colum, x, y) -> html.Div:
    @app.callback(
        Output(id_barchart, "children"),
        [
            Input(id_dropdown, "value"),
        ],
    )
    def update_bar_chart(
            values: list[str],
    ) -> html.Div:
        filtered_data = data.query(
            f"{id_filtered_colum} in @values"
        )

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
