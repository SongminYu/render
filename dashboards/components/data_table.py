import pandas as pd

from dash import dash_table, html, callback
from dash.dependencies import Input, Output


def render(data: pd.DataFrame, id_datatable, title, dropdowns, x, x_options, y, category) -> html.Div:
    # dropdowns here: list of dictionary of dropdowns,
    # One dictionary has keys 'id' (of dropdown) and
    # 'column' (respective column in data in which the filter should be applied)

    # Extract dropdown ids from list of dictionary of dropdowns
    dropdown_ids = [dropdown['id'] for dropdown in dropdowns]

    @callback(
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

        # ensure every energy carrier is listed in data table, in case as zero consumption
        for idx in x_options:
            if idx not in wide_df[category].values:
                # Create a row of zeros with index equal to missing index
                zeros_row = pd.DataFrame([[idx] + [0] * (len(wide_df.columns) - 1)], columns=wide_df.columns)
                # Find the position to insert the row
                insert_position = sum(wide_df[category] < idx)
                # Insert the row at the appropriate position based on the index column
                wide_df = pd.concat([wide_df.iloc[:insert_position], zeros_row, wide_df.iloc[insert_position:]], ignore_index=True)

        # Add the sum of columns
        end_use = list(wide_df.columns)
        end_use.remove(category)

        sum_row = pd.DataFrame(wide_df[end_use].sum(axis=0)).T
        sum_row.insert(loc=0, column=category, value='total')
        wide_df = pd.concat([wide_df, sum_row], ignore_index=True)
        wide_df['total'] = wide_df[wide_df.columns[1:]].sum(axis=1)

        # Round every entry to no digits after the decimal point
        wide_df = wide_df.round(2)
        wide_df = wide_df.fillna(0)

        # Ensure that column names are string, needed for dash DataTable
        wide_df.columns = wide_df.columns.astype(str)
        wide_df[category] = wide_df[category].astype(str)
        return [html.H6(f"{title}"),
                dash_table.DataTable(wide_df.to_dict('records'),
                                     [{"name": i, "id": i} for i in wide_df.columns],
                                     style_cell_conditional=[{'if': {'column_id': category},'textAlign': 'left'}],)
                ]

    return html.Div(className='table-container', id=id_datatable)
