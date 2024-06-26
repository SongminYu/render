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


def build_year_hour_columns(df: pd.DataFrame) -> pd.DataFrame:
    time_column = df.columns[0]
    # Extract year
    df['year'] = df[time_column].str[:4]

    # Convert datetime to pandas datetime
    df[time_column] = pd.to_datetime(df[time_column], format='%Y-%m-%d-%H')

    # Calculate cumulative hours since the first datetime
    df['hour'] = df.groupby('year')[time_column].transform(lambda x: (x - x.min()).astype('timedelta64[h]') + 1)
    return df

def extract_country_columns(df: pd.DataFrame, country = 'DE') -> pd.DataFrame:
    # Filtering columns that contain 'DE'
    columns_with_de = [col for col in df.columns if 'DE' in col]
    # Selecting only those columns
    df_filtered = df[['year', 'hour'] + columns_with_de]
    return df_filtered

def pivot_region_hour_columns(df: pd.DataFrame) -> pd.DataFrame:
    # Melt the DataFrame to transform region columns into rows
    melted_df = pd.melt(df, id_vars=['year', 'hour'], var_name='id_region', value_name='value')

    # Pivot the melted DataFrame
    pivot_df = melted_df.pivot_table(index=['id_region', 'year'], columns='hour', values='value')

    # Reset index to convert back to a plain DataFrame
    pivot_df.reset_index(inplace=True)
    pivot_df.set_index('id_region', inplace=True)

    return pivot_df


def prep_future_data(path):
    print('Load future weather data...')
    df = pd.read_csv(path+'_NUTS2_Europe_popweight_rcp45_hourly_2001-2050.csv')

    print('Build year and hour columns...')
    df = build_year_hour_columns(df)

    print('Extract columns for Germany...')
    df = extract_country_columns(df)

    print('Save dataframe...')
    df.to_csv(path + '_NUTS2_Europe_popweight_rcp45_hourly_2001-2050_DE.csv', index=False)


def create_future_weather_profile():
    print('Load prepped future weather data...')
    df_temperature = pd.read_csv('T2M_NUTS2_Europe_popweight_rcp45_hourly_2001-2050_DE.csv')
    df_radiation = pd.read_csv('GLO_NUTS2_Europe_popweight_rcp45_hourly_2001-2050_DE.csv')

    print('Pivot region and hour columns...')
    df_temperature = pivot_region_hour_columns(df_temperature)
    df_radiation = pivot_region_hour_columns(df_radiation)

    df_temperature = map_nuts_to_region_id(df_temperature)
    df_temperature.insert(df_temperature.columns.get_loc(1), 'unit', '°C')

    df_radiation = map_nuts_to_region_id(df_radiation)
    df_radiation.insert(df_radiation.columns.get_loc(1), 'unit', 'W/m^2')

    print('Save dataframe...')
    df_temperature.to_csv('Profile_WeatherTemperature_Future.csv')
    df_radiation.to_csv('Profile_WeatherRadiation_Future.csv')


if __name__ == '__main__':
    print('Prepare temperature data.')
    temperature_path = 'T2M'
    prep_future_data(temperature_path)
    print('Prepare radiation data.')
    radiation_path = 'GLO'
    prep_future_data(radiation_path)
    print('Create future weather profiles.')
    create_future_weather_profile()
