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

def calculate_extrapolated_radiation(base_year, target_year):
    df_differences = pd.read_csv('Profile_WeatherRadiation_Future.csv')
    rel_diff = calculate_difference_matrix(df_differences, base_year, target_year)
    df_data = pd.read_csv('Profile_WeatherRadiation.csv')

    dict_of_dfs = {}
    for orientation in list(df_data['id_orientation'].unique()):
        df_base = df_data[(df_data['year'] == base_year) & (df_data['id_orientation'] == orientation)]
        base = df_base.drop(columns=df_data.columns[:4]).to_numpy()
        extrapolated_data = base * (1 + rel_diff)
        df_1 = df_base[df_base.columns[:4]].reset_index(drop=True)
        df_2 = pd.DataFrame(extrapolated_data)

        # Create a new DataFrame by concatenating first_4_columns and matrix
        combined_df = pd.concat([df_1, df_2], axis=1)
        combined_df['year'] = target_year

        dict_of_dfs[orientation] = combined_df

    concatenated_df = pd.concat(dict_of_dfs.values(), axis=0).reset_index(drop=True)

    sorted_df = concatenated_df.sort_values(by=['year', 'id_region', 'id_orientation']).reset_index(drop=True)

    determine_error(df_data, sorted_df, target_year)

    # Save extrapolated data to a CSV file
    sorted_df.to_csv(f'extrapolated_data_for_{target_year}.csv', index=False)


def determine_error(df_data, extrapolated_data, target_year):
    desired = df_data[df_data['year'] == target_year].drop(columns=df_data.columns[:4]).fillna(0).to_numpy()
    print(f'In the PV GIS data for {target_year}, the minimal value of radiation is {np.min(desired)} and the maximal '
          f'value of radiation is {np.max(desired)}.')
    extrapolated = extrapolated_data.drop(columns=df_data.columns[:4]).fillna(0).to_numpy()
    print(f'In the extrapolated data for {target_year}, the minimal value of radiation is {np.min(extrapolated)} and '
          f'the maximal value of radiation is {np.max(extrapolated)}.')
    error = desired - extrapolated
    print(f'In the minimal error for {target_year} is {np.min(error)} and the maximal error is {np.max(error)}.')
    print(f'The total error is {np.linalg.norm(error, 1)}.')

def build_extrapolated_dataframes(base_year, target_year):
    calculate_extrapolated_radiation(base_year, target_year)



if __name__ == '__main__':
    build_extrapolated_dataframes(2019, 2020)

