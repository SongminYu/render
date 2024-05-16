import pandas as pd
import math


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


def change_ventilation_to_appliances(df: pd.DataFrame) -> pd.DataFrame:
    df.loc[df['id_end_use'] == 5, ['id_end_use']] = 1
    return df


def change_ec_to_renewables(df: pd.DataFrame) -> pd.DataFrame:
    # to compare model data with calibration target we change for id_sector=6 the ec 14, 15, 19 to 24
    df.loc[(df['id_sector'] == 3) & (df['id_energy_carrier'].isin([14, 15, 19])), ['id_energy_carrier']] = 24

    # for id_sector = 3 we change 12, 14, 15, 19 to 24
    df.loc[(df['id_sector'] == 6) & (df['id_energy_carrier'].isin([12, 14, 15, 19])), ['id_energy_carrier']] = 24
    return df


def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    df = change_ventilation_to_appliances(df)
    df = change_ec_to_renewables(df)
    df['value_in_TWh'] = df['value'] / 1000000000
    return df


def convert_TJ_to_TWh(df: pd.DataFrame) -> pd.DataFrame:
    df['value_in_TWh'] = df['value'] / 3600
    return df


def convert_id_region(rkey_id_region: int):
    rkey_id_region_list = list(str(rkey_id_region))
    rkey_region_level = math.ceil(len(rkey_id_region_list) / 2) - 1
    return int("".join(rkey_id_region_list[:- 2 * (rkey_region_level - 1)]))


def aggregate_to_nuts1(df: pd.DataFrame) -> pd.DataFrame:
    df['id_region'] = df['id_region'].apply(convert_id_region)
    return df


def load_data(path: str) -> pd.DataFrame:
    # load the data from the CSV file
    data = pd.read_csv(path)
    return data
