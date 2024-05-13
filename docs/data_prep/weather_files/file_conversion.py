import pandas as pd
import os
from tqdm import tqdm


def create_temperature_pivot_tables(df: pd.DataFrame, year) -> pd.DataFrame:
    pivoted_df = df.pivot(index='region', columns='id_hour', values='temperature')
    pivoted_df.insert(0, 'year', year)
    return pivoted_df


def create_pv_generation_pivot_tables(df: pd.DataFrame, year) -> pd.DataFrame:
    pivoted_df = df.pivot(index='region', columns='id_hour', values='pv_generation')
    pivoted_df.insert(0, 'year', year)
    return pivoted_df


def create_radiation_pivot_tables(df: pd.DataFrame, year) -> pd.DataFrame:
    melted_df = pd.melt(df, id_vars=['region', 'id_hour'],
                        value_vars=['radiation_south', 'radiation_east', 'radiation_west', 'radiation_north'],
                        var_name='orientation')
    pivoted_df = melted_df.pivot_table(index=['region', 'orientation'], columns='id_hour', values='value')
    pivoted_df.reset_index(level='orientation', inplace=True)
    pivoted_df.insert(0, 'year', year)
    return pivoted_df


def map_nuts_to_region_id(df: pd.DataFrame) -> pd.DataFrame:
    # Replace NUTS region IDs with actual regions from the ID table
    id_table = pd.read_excel('../../../projects/test_building/input/ID_Region.xlsx')
    id_table = id_table[id_table['region_level'] == 2]

    df['id_region'] = df.index.map(id_table.set_index('nuts_code')['id_region'])
    df.set_index('id_region', inplace=True, drop=True)
    return df


def map_orientations_to_id(df: pd.DataFrame) -> pd.DataFrame:
    id_table = pd.read_excel('../../../projects/test_building/input/ID_Orientation.xlsx')
    id_table['name'] = 'radiation_' + id_table['name']
    orientation_to_id = dict(zip(id_table['name'], id_table['id_orientation']))

    df['orientation'] = df['orientation'].map(orientation_to_id)
    return df.rename(columns={'orientation': 'id_orientation'})


def get_year_from_filename(filename: str) -> int:
    # Find the index of the ".csv" extension
    index = filename.find('.csv')

    # Extract the substring containing the four characters before ".csv"
    return int(filename[index - 4:index])


def create_weather_profile() -> pd.DataFrame:
    files = os.listdir(os.path.dirname(__file__))
    csv_files = [file for file in files if file.endswith('.csv') and 'pv_gis' in file]

    # Create a list to store pivoted DataFrames
    pv_generation_dfs = []
    temperature_dfs = []
    radiation_dfs = []

    # Iterate over each .csv file pivot it, and append to the list
    for file in tqdm(csv_files):
        year = get_year_from_filename(file)

        df = pd.read_csv(file)
        pv_generation_df = create_pv_generation_pivot_tables(df, year)
        pv_generation_dfs.append(pv_generation_df)

        temperature_df = create_temperature_pivot_tables(df, year)
        temperature_dfs.append(temperature_df)

        radiation_df = create_radiation_pivot_tables(df, year)
        radiation_dfs.append(radiation_df)

    # Merge the pivoted DataFrame
    pv_generation = pd.concat(pv_generation_dfs, axis=0)
    temperature = pd.concat(temperature_dfs, axis=0)
    radiation = pd.concat(radiation_dfs, axis=0)

    # insert unit column before the first hour column
    pv_generation.insert(pv_generation.columns.get_loc(1), 'unit', 'W/kW_peak')
    temperature.insert(temperature.columns.get_loc(1), 'unit', '°C')
    radiation.insert(radiation.columns.get_loc(1), 'unit', 'W')

    pv_generation = map_nuts_to_region_id(pv_generation)
    temperature = map_nuts_to_region_id(temperature)
    radiation = map_nuts_to_region_id(radiation)

    radiation = map_orientations_to_id(radiation)

    pv_generation.to_csv(f'Profile_WeatherPVGeneration.csv')
    temperature.to_csv(f'Profile_WeatherTemperature.csv')
    radiation.to_csv(f'Profile_WeatherRadiation.csv')


if __name__ == '__main__':
    create_weather_profile()

