import pandas as pd

from dash import dcc, html, callback
from dash.dependencies import Input, Output


def render(data: pd.DataFrame, id_sub_dropdown, id_dropdown, id_sub_options, id_options,
           id_select_all_button) -> html.Div:
    """
        Creates a Dash Div containing a dropdown and a button to select all options.
        The dropdown options are dynamically updated based on the selection from another dropdown and the button click.

        Parameters:
            data: Pandas DataFrame with the main data
            id_sub_dropdown: ID for the sub-dropdown element
            id_dropdown: ID for the primary dropdown element used for filtering
            id_sub_options: Column name in the DataFrame to use for dropdown options
            id_options: Column name in the DataFrame to use for filtering based on the primary dropdown
            id_select_all_button:  ID of the Dash select-all button

        Return: A Dash Div element containing the sub-dropdown and the select-all button
    """
    # Get all options from the respective column in data
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
        """
        Callback function to update the options of the sub-dropdown based on the selected value from the primary dropdown
        when the select-all button is clicked.
        """
        filtered_data = data.query(f"{id_options} in {filter}")
        return sorted(set(filtered_data[id_sub_options].tolist()))

    # Create the sub-dropdown component
    sub_dropdown = html.Div(className='dropdown-container',
                            children=[dcc.Dropdown(id=id_sub_dropdown,
                                                   options=[{"label": options, "value": options} for options in unique_options],
                                                   value=unique_options,
                                                   multi=True, )])

    # Create the select-all button component
    select_all_button = html.Button(className='button-container', children=["Select All"],
                                    id=id_select_all_button,
                                    n_clicks=0, )

    return html.Div(
        children=[
            html.H6(f"Select {id_sub_options}"),
            html.Div(className='flex-container', children=[sub_dropdown, select_all_button], )
        ],
    )
