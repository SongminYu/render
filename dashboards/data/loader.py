import pandas as pd
import math

from functools import lru_cache

class DataSchema_Floor_Area:
    ID_SCENARIO = "id_scenario"
    ID_REGION = "id_region"
    ID_SECTOR = "id_sector"
    ID_SUBSECTOR = "id_subsector"
    ID_BUILDING_TYPE = "id_building_type"
    ID_BUILDING = "id_building"
    ID_BUILDING_CONSTRUCTION_PERIOD = "id_building_construction_period"
    YEAR = "year"
    UNIT = "unit"
    VALUE = "value"


class DataSchema_Final_Energy:
    ID_SCENARIO = "id_scenario"
    ID_REGION = "id_region"
    ID_SECTOR = "id_sector"
    ID_SUBSECTOR = "id_subsector"
    YEAR = "year"
    ID_BUILDING_TYPE = "id_building_type"
    ID_BUILDING = "id_building"
    ID_BUILDING_CONSTRUCTION_PERIOD = "id_building_construction_period"

    ID_END_USE = 'id_end_use'
    VALUE = 'value'
    VALUE_TWh = 'value_in_TWh'
    ID_ENERGY_CARRIER = 'id_energy_carrier'


# Define paths to data files
ENERGY_PATH = "final_energy_demand_nuts3"
NATIONAL_REFERENCE_PATH = "Reference_EnergyBalance_National"
FLOOR_AREA_PATH = "floor_area"
NUTS1_PATH = "final_energy_demand_nuts1"
REGIONAL_REFERENCE_PATH = "Reference_EnergyBalance_Regional"


def change_ventilation_to_appliances(df: pd.DataFrame) -> pd.DataFrame:
    df.loc[df['id_end_use'] == 5, ['id_end_use']] = 1
    return df


def change_ec_to_renewables(df: pd.DataFrame) -> pd.DataFrame:
    # to compare model data with calibration target we change ec 14, 15, 19 to 24
    df.loc[df['id_energy_carrier'].isin([14, 15, 19]), ['id_energy_carrier']] = 24

    # for id_sector = 6 we change 12 to 24
    df.loc[(df['id_sector'] == '6') & (df['id_energy_carrier'] == 12), ['id_energy_carrier']] = 24

    # change 7 to 3
    df.loc[(df['id_energy_carrier'] == 7), ['id_energy_carrier']] = 3
    return df


def handle_mixed_sector(df: pd.DataFrame) -> pd.DataFrame:
    df.loc[(df['id_sector'] == '3&6'), ['id_sector']] = '3 and 6'
    return df


def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    df = change_ventilation_to_appliances(df)
    df = change_ec_to_renewables(df)
    df['value_in_TWh'] = df['value'] / 1000000000
    # df = make_sector_str(df)
    return df


def convert_TJ_to_TWh(df: pd.DataFrame) -> pd.DataFrame:
    df['value_in_TWh'] = df['value'] / 3600
    return df


def convert_id_region(rkey_id_region: int):
    rkey_id_region_list = list(str(rkey_id_region))
    rkey_region_level = math.ceil(len(rkey_id_region_list) / 2) - 1
    return int("".join(rkey_id_region_list[:- 2 * (rkey_region_level - 1)]))


def make_ec_int(df):
    if 'id_energy_carrier' in df.columns:
        df['id_energy_carrier'] = df['id_energy_carrier'].astype(int)
    return df


def make_sector_str(df):
    if 'sector' in df.columns:
        df['sector'] = df['sector'].astype(str)
    return df


def aggregate_to_nuts1(df: pd.DataFrame) -> pd.DataFrame:
    df['id_region'] = df['id_region'].apply(convert_id_region)
    return df


@lru_cache(maxsize=5)
def load_data(path: str) -> pd.DataFrame:
    # load the data from the CSV file
    data = pd.read_csv(path, dtype={'id_sector': str, 'id_energy_carrier': int})
    #data = make_ec_int(data)
    return data


# Individual functions to load specific datasets
def load_energy_data():
    return load_data("data/" + ENERGY_PATH + "_preprocessed.csv")

def load_national_reference_data():
    return load_data("data/" + NATIONAL_REFERENCE_PATH + "_preprocessed.csv")

def load_floor_area_data():
    return load_data("data/" + FLOOR_AREA_PATH + ".csv")

def load_nuts1_data():
    return load_data("data/" + NUTS1_PATH + "_preprocessed.csv")

def load_regional_reference_data():
    return load_data("data/" + REGIONAL_REFERENCE_PATH + "_preprocessed.csv")

def preprocess_energy_data():
    print("Preprocess energy data...")
    df = load_data(ENERGY_PATH + ".csv")
    df = preprocess_data(df)
    df.to_csv(ENERGY_PATH + "_preprocessed.csv", index=False)

def preprocess_national_reference_data():
    print("Preprocess national reference data...")
    df = load_data(NATIONAL_REFERENCE_PATH + ".csv")
    df = preprocess_data(df)
    df.to_csv(NATIONAL_REFERENCE_PATH + "_preprocessed.csv", index=False)

def preprocess_nuts1_data():
    print("Preprocess nuts1 data...")
    df = load_data(NUTS1_PATH + ".csv")
    df = preprocess_data(df)
    df.to_csv(NUTS1_PATH + "_preprocessed.csv", index=False)

def preprocess_regional_reference_data():
    print("Preprocess regional reference data...")
    df = load_data(REGIONAL_REFERENCE_PATH + ".csv")
    df = change_ec_to_renewables(df)
    # df = make_sector_str(df)
    #  df = convert_TJ_to_TWh(df)
    df = handle_mixed_sector(df)
    df.rename(columns={'value': 'value_in_TWh'}, inplace=True)
    df.to_csv(REGIONAL_REFERENCE_PATH + "_preprocessed.csv", index=False)

if __name__ == '__main__':
    print("Preprocess data for dashboards...")

    preprocess_energy_data()
    preprocess_national_reference_data()
    preprocess_regional_reference_data()
    preprocess_nuts1_data()

    print("Finished preprocessing data!")