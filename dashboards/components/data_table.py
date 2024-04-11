import pandas as pd

from dash import Dash, dash_table, html
from dash.dependencies import Input, Output


def render(app: Dash, data: pd.DataFrame, id_datatable, dropdowns, x, y, category) -> html.Div:
    # dropdowns here: list of dictionary of dropdowns,
    # One dictionary has keys 'id' (of dropdown) and
    # 'column' (respective column in data in which the filter should be applied)

    # Extract dropdown ids from list of dictionary of dropdowns
    dropdown_ids = [dropdown['id'] for dropdown in dropdowns]

    @app.callback(
        Output(id_datatable, "children"),
        [Input(id, "value") for id in dropdown_ids],
    )
    def update_data_table(*values: list[str]):
        # build query to filter in different columns, eg. for one filter f"{id_filtered_colum} in @values"
        filters = ' & '.join([f"{dropdown['column']} in {values[i]}" for i, dropdown in enumerate(dropdowns)])
        filtered_data = data.query(filters)

        if filtered_data.shape[0] == 0:
            return ""

        # get values for stacked bar chart
        wide_df = filtered_data.pivot_table(index=category, columns=x, values=y, aggfunc='sum')
        # Reset index to make 'energy_carrier' a column again
        wide_df.reset_index(inplace=True)
        wide_df.columns.name = None

        # Add the sum of columns
        end_use = list(wide_df.columns)
        end_use.remove('id_energy_carrier')

        sum_row = pd.DataFrame(wide_df[end_use].sum(axis=0)).T
        sum_row.insert(loc=0, column=category, value='total')
        # sum_row.at[0, 'id_energy_carrier'] = 'total'
        wide_df = pd.concat([wide_df, sum_row], ignore_index=True)

        # Round every entry to no digits after the decimal point
        wide_df = wide_df.round(0)
        wide_df = wide_df.fillna(0)

        # Ensure that column names are string, needed for dash DataTable
        wide_df.columns = wide_df.columns.astype(str)
        wide_df['id_energy_carrier'] = wide_df['id_energy_carrier'].astype(str)

        return [html.H6(f"{id_datatable}"),
                dash_table.DataTable(wide_df.to_dict('records'),
                                     [{"name": i, "id": i} for i in wide_df.columns],
                                     style_cell={'textAlign': 'left'})]

    return html.Div(className='table-container', id=id_datatable)
