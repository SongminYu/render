import pandas as pd

from dash import dcc, html, callback
from dash.dependencies import Input, Output


def render(data: pd.DataFrame, id_sub_dropdown, id_dropdown, id_sub_options, id_options,
           id_select_all_button) -> html.Div:
    all_options: list[str] = data[id_sub_options].tolist()
    unique_options = sorted(set(all_options), key=int)

    @callback(
        Output(id_sub_dropdown, "value"),
        [
            Input(id_dropdown, "value"),
            Input(id_select_all_button, "n_clicks")
        ],
    )
    def select_all(filter, _: int) -> list[str]:
        filtered_data = data.query(f"{id_options} in {filter}")
        return sorted(set(filtered_data[id_sub_options].tolist()))

    sub_dropdown = html.Div(className='dropdown-container',
                            children=[dcc.Dropdown(id=id_sub_dropdown,
                                                   options=[{"label": options, "value": options} for options in unique_options],
                                                   value=unique_options,
                                                   multi=True, )])
    select_all_button = html.Button(className='button-container', children=["Select All"],
                                    id=id_select_all_button,
                                    n_clicks=0, )

    return html.Div(
        children=[
            html.H6(f"Select {id_sub_options}"),
            html.Div(className='flex-container', children=[sub_dropdown, select_all_button], )
        ],
    )
