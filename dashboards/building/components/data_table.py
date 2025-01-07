import pandas as pd

from dash import dash_table, html, callback
from dash.dependencies import Input, Output


def render(data: pd.DataFrame, id_datatable, title, dropdowns, x, x_options, y, category, category_options) -> html.Div:
    """
        Render function to create a Dash Div element containing a table that gets filtered based on dropdown selections.

        Parameters:
            data: Pandas DataFrame with the data to be visualized
            id_datatable: ID of the Dash datatable element
            title: Title of the table
            dropdowns: List of dictionaries with dropdown information,
                keys: 'id' (ID of the dropdown) and 'column' (the respective column in data to apply the filter)
            x: Column of data to be used for the columns in the pivot table
            x_options: List of possible values for x
            y: Column of data to be used for the values in the pivot table
            category: Column of data to be used as index in the pivot table
            category_options: List of possible values for category

        Return: Dash Div element containing the datatable
        """

    # Extract dropdown ids from list of dictionary of dropdowns
    dropdown_ids = [dropdown['id'] for dropdown in dropdowns]

    @callback(
        Output(id_datatable, "children"),
        [Input(id, "value") for id in dropdown_ids],
    )
    def update_data_table(*values: list[str]):
        # Build query to filter in different columns, eg. for one filter f"{id_filtered_colum} in @values"
        filters = ' & '.join([f"{dropdown['column']} in {values[i]}" for i, dropdown in enumerate(dropdowns)])
        filtered_data = data.query(filters)

        if filtered_data.shape[0] == 0:
            return ""

        # Get values for stacked bar chart
        wide_df = filtered_data.pivot_table(index=category, columns=x, values=y, aggfunc='sum')
        # Reset index to make 'category' a column again
        wide_df.reset_index(inplace=True)
        wide_df.columns.name = None

        # Ensure every category is listed in data table, in case as zero consumption
        for idx in category_options:
            if idx not in wide_df[category].values:
                # Create a row of zeros with index equal to missing index
                zeros_row = pd.DataFrame([[idx] + [0] * (len(wide_df.columns) - 1)], columns=wide_df.columns)
                # Find the position to insert the row
                insert_position = sum(wide_df[category] < idx)
                # Insert the row at the appropriate position based on the index column
                wide_df = pd.concat([wide_df.iloc[:insert_position], zeros_row, wide_df.iloc[insert_position:]], ignore_index=True)

        # Ensure every x option is listed in the data table, even if it has zero consumption
        for idx in x_options:
            if idx not in wide_df:
                def find_insert_position(sorted_list, value_to_insert):
                    """
                    Finds the position where the value should be inserted into the sorted list.
                    """
                    for i, num in enumerate(sorted_list):
                        if type(num) != int:
                            break
                        print(num)
                        print(value_to_insert)
                        if num > value_to_insert:
                            return i
                    return len(sorted_list)

                insert_position = find_insert_position(wide_df.columns, idx)
                wide_df.insert(insert_position, idx, [0] * (len(wide_df)))

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

        # Ensure that column names are strings, needed for Dash DataTable
        wide_df.columns = wide_df.columns.astype(str)
        wide_df[category] = wide_df[category].astype(str)
        return [html.H6(f"{title}"),
                dash_table.DataTable(wide_df.to_dict('records'),
                                     [{"name": i, "id": i} for i in wide_df.columns],
                                     style_cell_conditional=[{'if': {'column_id': category},'textAlign': 'left'}],)
                ]

    return html.Div(className='table-container', id=id_datatable)
