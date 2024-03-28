import pandas as pd
from dash import Dash, dcc, html
from dash.dependencies import Input, Output


def render(app: Dash, data: pd.DataFrame, id_sub_dropdown, id_dropdown, id_sub_options, id_options, id_select_all_button) -> html.Div:
    all_options: list[str] = data[id_sub_options].tolist()
    unique_options = sorted(set(all_options), key=int)

    @app.callback(
        Output(id_sub_dropdown, "value"),
        [
            Input(id_dropdown, "value"),
            Input(id_select_all_button, "n_clicks")
        ],
    )
    def select_all(filter, _: int) -> list[str]:
        filtered_data = data.query(f"{id_options} in {filter}")
        return sorted(set(filtered_data[id_sub_options].tolist()))

    sub_dropdown = html.Div(children=[dcc.Dropdown(id=id_sub_dropdown,
                                               options=[{"label": options, "value": options} for options in unique_options],
                                               value=unique_options,
                                               multi=True, )],
                        style=dict(width='80%'))
    select_all_button = html.Button(children=["Select All"],
                                    id=id_select_all_button,
                                    n_clicks=0,
                                    style=dict(width='20%'))

    return html.Div(
        children=[
            html.H6(f"Select {id_sub_options}"),
            html.Div(children=[sub_dropdown, select_all_button], style=dict(display='flex'))
        ],
    )
