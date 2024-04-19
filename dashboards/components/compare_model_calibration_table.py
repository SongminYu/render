import pandas as pd

from dash import dash_table, html, callback
from dash.dependencies import Input, Output
from dash.dash_table import FormatTemplate


def render(id_comparison, id_data, id_reference, id_absolute, id_relative) -> html.Div:
    @callback(
        Output(id_comparison, "children"),
        [Input(id_data, "children"), Input(id_reference, "children")]
    )
    def update_data_table(data, reference):
        data_df = pd.DataFrame(data[1]['props']['data'])
        reference_df = pd.DataFrame(reference[1]['props']['data'])

        if data_df.shape[0] == 0:
            return ""

        end_use = list(data_df.columns)
        end_use.remove('id_energy_carrier')

        absolute = data_df[end_use] - reference_df[end_use]
        absolute.insert(loc=0, column='id_energy_carrier', value=data_df['id_energy_carrier'])
        # Round every entry to no digits after the decimal point
        absolute = absolute.round(2)
        absolute = absolute.fillna(0)

        relative = pd.DataFrame()
        for column in end_use:
            relative[column] = (data_df[column] - reference_df[column]).div(reference_df[column])
        relative.insert(loc=0, column='id_energy_carrier', value=data_df['id_energy_carrier'])
        # Round every entry to no digits after the decimal point
        relative = relative.fillna(0)
        relative = relative.round(4)

        absolute_html = html.Div(className='table-container',
                                 id=id_absolute,
                                 children=[html.H6(f"{id_absolute}"),
                                           dash_table.DataTable(absolute.to_dict('records'),
                                                                [{"name": i, "id": i} for i in absolute.columns],
                                                                style_cell_conditional=[{'if': {'column_id': 'id_energy_carrier'},'textAlign': 'left'}],)
                                           ])

        column_dict = [{"name": 'id_energy_carrier', "id": 'id_energy_carrier'}]
        column_dict.extend([{"name": i, "id": i, "type": 'numeric', 'format': FormatTemplate.percentage(2)} for i in end_use])
        relative_html = html.Div(className='table-container',
                                 id=id_relative,
                                 children=[html.H6(f"{id_relative}"),
                                           dash_table.DataTable(relative.to_dict('records'),
                                                                columns=column_dict,
                                                                style_cell_conditional=[{'if': {'column_id': 'id_energy_carrier'},'textAlign': 'left'}],)
                                           ])
        return [absolute_html, relative_html]

    return html.Div(className='flex-container', id=id_comparison)
