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
    UNIT = "unit"

    ID_END_USE = 'id_end_use'
    VALUE = 'value'
    VALUE_TWh = 'value_in_TWh'
    ID_ENERGY_CARRIER = 'id_energy_carrier'

class DataSchema_Building_Stock:
    ID_SCENARIO = "id_scenario"
    ID_REGION = "id_region"
    ID_SECTOR = "id_sector"
    ID_SUBSECTOR = "id_subsector"
    YEAR = "year"
    MAIN_HEATING_TECHNOLOGY = "heating_system_main_id_heating_technology"

class DataSchema_Heating_Reference:
    ID_REGION = "id_region"
    ID_HEATING_SYSTEM = "id_heating_system"
    ID_HEATING_TECHNOLOGY = "id_heating_technology"
    YEAR = "year"
    BUILDING_NUMBER = "building_number"
    SHARE_PERCENTAGE = "share_percentage"


# Define paths to data files
NUTS1_ENERGY_PATH = "final_energy_demand_nuts1"
NUTS3_ENERGY_PATH = "final_energy_demand_nuts3"
NATIONAL_REFERENCE_ENERGY_PATH = "Reference_EnergyBalance_National"
REGIONAL_REFERENCE_ENERGY_PATH = "Reference_EnergyBalance_Regional"

FLOOR_AREA_PATH = "floor_area"

NUTS3_BUILDING_PATH = "building_stock_R9160023"
REGIONAL_REFERENCE_BUILDING_PATH = "Reference_HeatingTech_Regional"


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


def change_id_heating_technology(df: pd.DataFrame) -> pd.DataFrame:
    df.loc[df[DataSchema_Building_Stock.MAIN_HEATING_TECHNOLOGY].isin([29, 210, 211]), [
        DataSchema_Building_Stock.MAIN_HEATING_TECHNOLOGY]] = 250

    df.loc[df[DataSchema_Building_Stock.MAIN_HEATING_TECHNOLOGY].isin([24, 25, 26, 27, 28, 212, 213]), [
        DataSchema_Building_Stock.MAIN_HEATING_TECHNOLOGY]] = 299

    return df


def handle_mixed_sector(df: pd.DataFrame) -> pd.DataFrame:
    df.loc[(df['id_sector'] == '3&6'), ['id_sector']] = '3 and 6'
    return df


def preprocess_energy_data(df: pd.DataFrame) -> pd.DataFrame:
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


@lru_cache(maxsize=5)
def load_energy_data(path: str) -> pd.DataFrame:
    # load the data from the CSV file
    data = pd.read_csv(path, dtype={'id_sector': str, 'id_energy_carrier': int})
    return data


# Individual functions to load specific datasets
def load_nuts3_energy_data():
    return load_energy_data("data/" + NUTS3_ENERGY_PATH + "_preprocessed.csv")


def load_national_reference_energy_data():
    return load_energy_data("data/" + NATIONAL_REFERENCE_ENERGY_PATH + "_preprocessed.csv")


def load_floor_area_data():
    return load_energy_data("data/" + FLOOR_AREA_PATH + ".csv")


def load_nuts1_energy_data():
    return load_energy_data("data/" + NUTS1_ENERGY_PATH + "_preprocessed.csv")


def load_regional_reference_energy_data():
    return load_energy_data("data/" + REGIONAL_REFERENCE_ENERGY_PATH + "_preprocessed.csv")


@lru_cache(maxsize=1)
def load_nuts3_heating_data():
    return pd.read_csv("data/" + NUTS3_BUILDING_PATH + "_preprocessed.csv")

@lru_cache(maxsize=1)
def load_regional_reference_heating_data():
    return pd.read_csv("data/" + REGIONAL_REFERENCE_BUILDING_PATH + "_preprocessed.csv")


def preprocess_nuts3_energy_data():
    print("Preprocess nuts3 energy data...")
    df = load_energy_data(NUTS3_ENERGY_PATH + ".csv")
    df = preprocess_energy_data(df)
    df.to_csv(NUTS3_ENERGY_PATH + "_preprocessed.csv", index=False)


def preprocess_national_reference_energy_data():
    print("Preprocess national reference energy data...")
    df = load_energy_data(NATIONAL_REFERENCE_ENERGY_PATH + ".csv")
    df = preprocess_energy_data(df)
    df.to_csv(NATIONAL_REFERENCE_ENERGY_PATH + "_preprocessed.csv", index=False)


def preprocess_nuts1_energy_data():
    print("Preprocess nuts1 energy data...")
    df = load_energy_data(NUTS1_ENERGY_PATH + ".csv")
    df = preprocess_energy_data(df)
    df.to_csv(NUTS1_ENERGY_PATH + "_preprocessed.csv", index=False)


def preprocess_regional_reference_energy_data():
    print("Preprocess regional reference energy data...")
    df = load_energy_data(REGIONAL_REFERENCE_ENERGY_PATH + ".csv")
    df = change_ec_to_renewables(df)
    #  df = convert_TJ_to_TWh(df)
    df = handle_mixed_sector(df)
    df.rename(columns={'value': 'value_in_TWh'}, inplace=True)
    df.to_csv(REGIONAL_REFERENCE_ENERGY_PATH + "_preprocessed.csv", index=False)


def preprocess_nuts3_heating_data():
    print("Preprocess nuts3 heating data...")
    df = pd.read_csv(NUTS3_BUILDING_PATH + ".csv")
    df = change_id_heating_technology(df)
    # Gruppieren und Zählen
    grouped_df = df.groupby([DataSchema_Building_Stock.ID_REGION,
                             DataSchema_Building_Stock.YEAR,
                             DataSchema_Building_Stock.MAIN_HEATING_TECHNOLOGY]).size().reset_index(name=DataSchema_Heating_Reference.BUILDING_NUMBER)

    grouped_df = grouped_df.rename(
        columns={DataSchema_Building_Stock.MAIN_HEATING_TECHNOLOGY: DataSchema_Heating_Reference.ID_HEATING_TECHNOLOGY}
    )
    grouped_df.to_csv(NUTS3_BUILDING_PATH + "_preprocessed.csv", index=False)


def preprocess_regional_reference_heating_data():
    print("Preprocess regional reference heating data...")
    df = pd.read_csv(REGIONAL_REFERENCE_BUILDING_PATH + ".csv")
    df.to_csv(REGIONAL_REFERENCE_BUILDING_PATH + "_preprocessed.csv", index=False)


if __name__ == '__main__':
    print("Preprocess data for dashboards...")

    # preprocess_nuts1_energy_data()
    # preprocess_nuts3_energy_data()
    # preprocess_national_reference_energy_data()
    # preprocess_regional_reference_energy_data()

    preprocess_nuts3_heating_data()
    preprocess_regional_reference_heating_data()

    print("Finished preprocessing data!")