import pandas as pd
from dash import Dash, dcc, html
from dash.dependencies import Input, Output


def render(app: Dash, data: pd.DataFrame, id_dropdown, id_options, id_select_all_button) -> html.Div:
    all_options: list[str] = data[id_options].tolist()
    unique_options = sorted(set(all_options), key=int)

    @app.callback(
        Output(id_dropdown, "value"),
        Input(id_select_all_button, "n_clicks"),
    )
    def select_all(_: int) -> list[str]:
        return unique_options

    dropdown = html.Div(className='dropdown-container', children=[dcc.Dropdown(id=id_dropdown,
                                               options=[{"label": options, "value": options} for options in unique_options],
                                               value=unique_options,
                                               multi=True, )],)
    select_all_button = html.Button(className='button-container',  children=["Select All"],
                                    id=id_select_all_button,
                                    n_clicks=0,)

    return html.Div(
        children=[
            html.H6(f"Select {id_options}:"),
            html.Div(className='flex-container', children=[dropdown, select_all_button])
        ],
    )
