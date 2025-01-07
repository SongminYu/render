import pandas as pd
from dash import dcc, html, callback
from dash.dependencies import Input, Output


def render(data: pd.DataFrame, reference: pd.DataFrame, id_dropdown, id_options, id_select_all_button) -> html.Div:
    """
        Render function to create a Dash Div element containing a dropdown and a select-all button,
        which get updated based on the data provided.

        Parameters:
            data: Pandas DataFrame with the main data
            reference: Pandas DataFrame with reference data
            id_dropdown: ID of the Dash dropdown element
            id_options: Column name in the DataFrame to use for dropdown options
            id_select_all_button: ID of the Dash select-all button

        Return: Dash Div element containing the dropdown and the select-all button
    """
    # Get all options from the respective column in data
    all_options_data: list[str] = data[id_options].tolist()

    # Get all options from the reference DataFrame if the column exists, otherwise use an empty list
    if id_options in reference.columns:
        all_options_reference: list[str] = reference[id_options].tolist()
    else:
        all_options_reference = []

    # Create a sorted list of unique options from both data and reference
    unique_options = sorted(set(all_options_data + all_options_reference))

    @callback(
        Output(id_dropdown, "value"),
        Input(id_select_all_button, "n_clicks"),
    )
    def select_all(_: int) -> list[str]:
        """
        Callback function to select all options in the dropdown when the select-all button is clicked.
        """
        return unique_options

    # Create the dropdown component
    dropdown = html.Div(
        className='dropdown-container',
        children=[dcc.Dropdown(
            id=id_dropdown,
            options=[{"label": options, "value": options} for options in unique_options],
            value=unique_options,
            multi=True,  # Allow multiple selections
        )],
    )

    # Create the select-all button component
    select_all_button = html.Button(
        className='button-container',
        children=["Select All"],
        id=id_select_all_button,
        n_clicks=0, # Initialize the number of clicks to 0
    )

    return html.Div(
        children=[
            html.H6(f"Select {id_options}:"),  # Title for the dropdown
            html.Div(className='flex-container', children=[dropdown, select_all_button])
        ],
    )
