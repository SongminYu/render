import pandas as pd
import numpy as np

def calculate_difference_matrix(df, base_year, target_year):
    # Filter the DataFrame for the base year and the target year
    df_base = df[df['year'] == base_year].drop(columns=df.columns[:3])
    df_target = df[df['year'] == target_year].drop(columns=df.columns[:3])
    base = df_base.to_numpy()
    target = df_target.to_numpy()
    # Calculate absolute differences
    abs_diff = target - base

    # Calculate relative differences
    # Using np.divide to avoid division by zero warnings
    rel_diff = np.divide(abs_diff, np.abs(base), out=np.zeros_like(abs_diff), where=base != 0)

    return rel_diff


def calculate_factor(df, base_year, target_year):
    df_base = df[df['year'] == base_year].drop(columns=df.columns[:3])
    df_target = df[df['year'] == target_year].drop(columns=df.columns[:3])
    base_totals = np.nansum(df_base.to_numpy(), axis=1)
    target_totals = np.nansum(df_target.to_numpy(), axis=1)
    abs_diff = target_totals - base_totals
    rel_diff = np.divide(abs_diff, np.abs(base_totals), out=np.zeros_like(abs_diff), where=base_totals != 0)
    print(f'In the relative diff for {target_year}, the minimal value of radiation is {np.min(rel_diff)} and '
          f'the maximal value of radiation is {np.max(rel_diff)}.')
    return rel_diff


def calculate_extrapolated_radiation(base_year, target_year):
    print('Calculate extrapolation factor...')
    df_differences = pd.read_csv('Profile_WeatherRadiation_Future.csv')
    df_differences = df_differences.sort_values(by=['id_region']).reset_index(drop=True)
    region_list_differences = list(df_differences['id_region'].unique())
    rel_diff = calculate_factor(df_differences, base_year, target_year)

    print('Read PV Gis data...')
    df_data = pd.read_csv('Profile_WeatherRadiation.csv')
    region_list_data = list(df_data['id_region'].unique())

    if region_list_differences != region_list_data:
        return print('Not the same regions in the two dataframes')

    print('Calculate extrapolated values...')
    dict_of_dfs = {}
    for orientation in list(df_data['id_orientation'].unique()):
        df_base = df_data[(df_data['year'] == base_year) & (df_data['id_orientation'] == orientation)]
        index_df = df_base[df_base.columns[:4]].reset_index(drop=True)
        base = df_base.drop(columns=df_data.columns[:4]).reset_index(drop=True)
        extrapolated_diff = base.multiply(rel_diff, axis=0)
        extrapolated_data = base + extrapolated_diff

        # extrapolated_data = base * (1 + rel_diff)  # when using difference matrix, make base numpy before
        # extrapolated_data = pd.DataFrame(extrapolated_data)  # convert back to df

        # Create a new DataFrame by concatenating first_4_columns and matrix
        combined_df = pd.concat([index_df, extrapolated_data], axis=1)
        combined_df['year'] = target_year

        dict_of_dfs[orientation] = combined_df

    concatenated_df = pd.concat(dict_of_dfs.values(), axis=0).reset_index(drop=True)

    sorted_df = concatenated_df.sort_values(by=['year', 'id_region', 'id_orientation']).reset_index(drop=True)
    df_data = df_data.sort_values(by=['year', 'id_region', 'id_orientation']).reset_index(drop=True)

    print('Determine error...')
    determine_error_total(df_data, sorted_df, target_year, base_year)

    print('Save extrapolated data...')
    # Save extrapolated data to a CSV file
    sorted_df.to_csv(f'extrapolated_data_for_{target_year}.csv', index=False)


def determine_error(df_data, extrapolated_data, target_year, base_year):
    df_data = df_data[df_data['year'] == target_year]
    desired = df_data.drop(columns=df_data.columns[:4]).fillna(0).to_numpy()
    print(f'In the PV GIS data for {target_year}, the minimal value of radiation is {np.min(desired)} and the maximal '
          f'value of radiation is {np.max(desired)}.')
    extrapolated = extrapolated_data.drop(columns=df_data.columns[:4]).fillna(0).to_numpy()
    print(f'In the extrapolated data for {target_year}, the minimal value of radiation is {np.min(extrapolated)} and '
          f'the maximal value of radiation is {np.max(extrapolated)}.')
    error = desired - extrapolated
    rel_error = np.divide(error, np.abs(desired), out=np.zeros_like(error), where=desired != 0)
    print(f'In the minimal relative error for {target_year} is {np.min(rel_error)} and the maximal relative error is {np.max(rel_error)}.')
    print(f'The total 1-norm of relative error is {np.linalg.norm(rel_error, 1)}.')
    print(f'The mean of relative error: {np.mean(rel_error)}')
    error_df = pd.DataFrame(rel_error)
    region_list = list(df_data['id_region'])
    orientation_list = list(df_data['id_orientation'])
    error_df.insert(loc=0, column='id_orientation', value=orientation_list)
    error_df.insert(loc=0, column='id_region', value=region_list)
    error_df.to_csv(f'error_base_{base_year}_target_{target_year}_2.csv', index=False)

def determine_error_total(df_data, extrapolated_data, target_year, base_year):
    df_data = df_data[df_data['year'] == target_year]
    desired = df_data.drop(columns=df_data.columns[:4]).fillna(0).to_numpy()
    extrapolated = extrapolated_data.drop(columns=df_data.columns[:4]).fillna(0).to_numpy()

    desired_total = np.nansum(desired, axis=1)
    print(f'desired: {desired_total[0:5]}')
    extrapolated_total = np.nansum(extrapolated, axis=1)
    print(f'extrapolated: {extrapolated_total[0:5]}')

    error = desired_total - extrapolated_total
    rel_error = np.divide(error, np.abs(desired_total), out=np.zeros_like(error), where=desired_total != 0)
    print(f'In the minimal relative error for {target_year} is {np.min(rel_error)} and the maximal reltaive error is {np.max(rel_error)}.')
    print(f'The total 1-norm of relative error is {np.linalg.norm(rel_error, 1)}.')
    print(f'The mean of relative error: {np.mean(rel_error)}')
    print(rel_error)


def build_extrapolated_dataframes(base_year, target_year):
    calculate_extrapolated_radiation(base_year, target_year)
    # calculate_extrapolated_pv_generation(base_year, target_year)


if __name__ == '__main__':
    build_extrapolated_dataframes(2017, 2018)
    # df_differences = pd.read_csv('Profile_WeatherRadiation_Future.csv')
    # calculate_factor(df_differences, 2015, 2026)
    # sorted_df = pd.read_csv('extrapolated_data_for_2018.csv')
    # df_data = pd.read_csv('Profile_WeatherRadiation.csv')
    # determine_error(df_data, sorted_df, 2018, 2017)

