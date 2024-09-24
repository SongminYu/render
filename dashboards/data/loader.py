import pandas as pd
import math

from functools import lru_cache

# The loader preprocesses the data suitable for the dashboards.
# Also, it loads the data and cashes the data, such that the dash app is faster

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
    ID_BUILDING_TYPE = "id_building_type"
    ID_EFFICIENCY_CLASS = "id_building_efficiency_class"

class DataSchema_Energy_Performance:
    ID_REGION = "id_region"
    YEAR = "year"
    ID_BUILDING_TYPE = "id_building_type"
    ID_EFFICIENCY_CLASS = "id_building_efficiency_class"
    BUILDING_NUMBER = "building_number"
    PERCENTAGE_BUILDING_NUMBER = 'share_fraction'


class DataSchema_Heating_Reference:
    ID_REGION = "id_region"
    ID_HEATING_SYSTEM = "id_heating_system"
    ID_HEATING_TECHNOLOGY = "id_heating_technology"
    YEAR = "year"
    BUILDING_NUMBER = "building_number"
    SHARE_PERCENTAGE = "share_percentage"

class DataSchema_Nuts1_Building_Stock:
    ID_SCENARIO = "id_scenario"
    ID_REGION = "id_region"
    ID_SECTOR = "id_sector"
    ID_SUBSECTOR = "id_subsector"
    YEAR = "year"
    ID_BUILDING_TYPE = "id_building_type"
    ID_BUILDING_LOCATION = "id_building_location"
    MAIN_HEATING_TECHNOLOGY = "heating_system_main_id_heating_technology"
    MAIN_HEATING_EC = "heating_system_main_space_heating_energy_carrier_1_id_energy_carrier"
    BUILDING_NUMBER = "building_number"

class DataSchema_Renovation_Rate:
    ID_SCENARIO = "id_scenario"
    ID_REGION = "id_region"
    ID_SECTOR = "id_sector"
    YEAR = "year"
    WALL = "wall"
    WALL_MARGIN = "wall_margin"
    WINDOW = "window"
    WINDOW_MARGIN = "window_margin"
    ROOF = "roof"
    ROOF_MARGIN = "roof_margin"
    BASEMENT = "basement"
    BASEMENT_MARGIN = "basement_margin"
    AVERAGE = "average"


# Define paths to data files
NUTS1_ENERGY_PATH = "final_energy_demand_nuts1"
NUTS3_ENERGY_PATH = "final_energy_demand_nuts3"
NATIONAL_REFERENCE_ENERGY_PATH = "Reference_EnergyBalance_National"
REGIONAL_REFERENCE_ENERGY_PATH = "Reference_EnergyBalance_Regional"

FLOOR_AREA_PATH = "floor_area"

NUTS3_BUILDING_PATH = "heating_tech_nuts3"
NUTS3_HEATING_TECHNOLOGY_PATH = "final_heating_technology_nuts3"
NUTS3_EFFICIENCY_CLASS_PATH = "final_efficiency_class_nuts3"
NUTS1_BUILDING_PATH = "heating_tech_nuts1" # "output_mainheatingsystem"
NUTS1_HEATING_TECHNOLOGY_PATH = "final_heating_technology_nuts1"
NUTS1_EFFICIENCY_CLASS_PATH = "final_efficiency_class_nuts1"
REGIONAL_REFERENCE_BUILDING_PATH = "Reference_HeatingTech_Regional"
REFERENCE_ENERGY_PERFORMANCE_PATH = "Reference_StockEnergyPerformance_National"

RENOVATION_RATE_PATH = "renovation_rate"
REFERENCE_RENOVATION_RATE_PATH = "Reference_RenovationRate"


# ventilation is end_use = 5, but in reference we do not separate these end_uses
def change_ventilation_to_appliances(df: pd.DataFrame) -> pd.DataFrame:
    df.loc[df['id_end_use'] == 5, ['id_end_use']] = 1
    return df


# Certain energy carriers have to be adapted to fit to the reference data
def change_ec_to_renewables(df: pd.DataFrame) -> pd.DataFrame:
    # to compare model data with calibration target we change ec 14, 15, 19 to 24
    df.loc[df['id_energy_carrier'].isin([14, 15, 19]), ['id_energy_carrier']] = 24

    # for id_sector = 6 we change 12 to 24
    df.loc[(df['id_sector'] == '6') & (df['id_energy_carrier'] == 12), ['id_energy_carrier']] = 24

    # change 7 to 3
    df.loc[(df['id_energy_carrier'] == 7), ['id_energy_carrier']] = 3
    return df


# Certain heating technologies have to be adapted to fit to the reference data
def change_id_heating_technology(df: pd.DataFrame) -> pd.DataFrame:
    df.loc[df[DataSchema_Building_Stock.MAIN_HEATING_TECHNOLOGY].isin([29, 210, 211, 33]), [
        DataSchema_Building_Stock.MAIN_HEATING_TECHNOLOGY]] = 250

    df.loc[df[DataSchema_Building_Stock.MAIN_HEATING_TECHNOLOGY].isin([26]), [
        DataSchema_Building_Stock.MAIN_HEATING_TECHNOLOGY]] = 21

    df.loc[df[DataSchema_Building_Stock.MAIN_HEATING_TECHNOLOGY].isin([27]), [
        DataSchema_Building_Stock.MAIN_HEATING_TECHNOLOGY]] = 22

    df.loc[df[DataSchema_Building_Stock.MAIN_HEATING_TECHNOLOGY].isin([28]), [
        DataSchema_Building_Stock.MAIN_HEATING_TECHNOLOGY]] = 23

    df.loc[df[DataSchema_Building_Stock.MAIN_HEATING_TECHNOLOGY].isin([24, 25, 32, 213]), [
        DataSchema_Building_Stock.MAIN_HEATING_TECHNOLOGY]] = 299

    df.loc[df[DataSchema_Building_Stock.MAIN_HEATING_TECHNOLOGY].isin([212, 34]), [
        DataSchema_Building_Stock.MAIN_HEATING_TECHNOLOGY]] = 46

    return df


# Certain building types have to be adapted to fit to the reference data
def change_id_building_type(df: pd.DataFrame) -> pd.DataFrame:
    df.loc[df[DataSchema_Building_Stock.ID_BUILDING_TYPE].isin([1, 2]), [DataSchema_Building_Stock.ID_BUILDING_TYPE]] = "1&2"

    df.loc[df[DataSchema_Building_Stock.ID_BUILDING_TYPE].isin([3, 4, 5]), [DataSchema_Building_Stock.ID_BUILDING_TYPE]] = "3-5"
    return df


def change_building_number_to_percentage(df: pd.DataFrame) -> pd.DataFrame:
    years = list(df[DataSchema_Energy_Performance.YEAR].unique())
    totals_per_year = {}
    for year in years:
        df_year = df[df[DataSchema_Energy_Performance.YEAR] == year]
        total_building_number = df_year[DataSchema_Energy_Performance.BUILDING_NUMBER].sum()
        totals_per_year[year] = total_building_number

    df[DataSchema_Energy_Performance.PERCENTAGE_BUILDING_NUMBER] = df.apply(lambda row: row[DataSchema_Energy_Performance.BUILDING_NUMBER] / totals_per_year[row[DataSchema_Energy_Performance.YEAR]], axis=1)
    return df


# For some states in regional reference data we do not differentiate sectors
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


# To convert the nuts3 region keys to nuts 1
def convert_id_region(rkey_id_region: int):
    rkey_id_region_list = list(str(rkey_id_region))
    rkey_region_level = math.ceil(len(rkey_id_region_list) / 2) - 1
    return int("".join(rkey_id_region_list[:- 2 * (rkey_region_level - 1)]))


def aggregate_to_nuts1(df: pd.DataFrame) -> pd.DataFrame:
    df['id_region'] = df['id_region'].apply(convert_id_region)
    return df


# Gerneral method to load the energy data. Here we cash the data for 5 different function calls
@lru_cache(maxsize=5)
def load_energy_data(path: str) -> pd.DataFrame:
    # load the data from the CSV file
    data = pd.read_csv(path, dtype={'id_sector': str, 'id_energy_carrier': int})
    return data


# Individual functions to load specific datasets.
# This will be called by the pages of the app. Therefor we need to specify the data folder in the data path
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
    return pd.read_csv("data/" + NUTS3_HEATING_TECHNOLOGY_PATH + "_preprocessed.csv")


@lru_cache(maxsize=1)
def load_nuts3_efficiency_data():
    return pd.read_csv("data/" + NUTS3_EFFICIENCY_CLASS_PATH + "_preprocessed.csv")

@lru_cache(maxsize=1)
def load_reference_efficiency_data():
    return pd.read_csv("data/" + REFERENCE_ENERGY_PERFORMANCE_PATH + ".csv")

@lru_cache(maxsize=1)
def load_nuts1_heating_data():
    return pd.read_csv("data/" + NUTS1_HEATING_TECHNOLOGY_PATH + "_preprocessed.csv")


@lru_cache(maxsize=1)
def load_regional_reference_heating_data():
    return pd.read_csv("data/" + REGIONAL_REFERENCE_BUILDING_PATH + "_preprocessed.csv")

@lru_cache(maxsize=1)
def load_nuts1_efficiency_data():
    return pd.read_csv("data/" + NUTS1_EFFICIENCY_CLASS_PATH + "_preprocessed.csv")

@lru_cache(maxsize=1)
def load_renovation_rate_data():
    return pd.read_csv("data/" + RENOVATION_RATE_PATH + ".csv")

@lru_cache(maxsize=1)
def load_reference_renovation_rate_data():
    return pd.read_csv("data/" + REFERENCE_RENOVATION_RATE_PATH + ".csv")


# Individual functions to preprocess specific datasets
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
    df = df[df['id_sector'] == 6]  # Reference is only for Sector 6
    df = change_id_heating_technology(df)
    df = change_id_building_type(df)

    # Heating Technology preprocessed table
    grouped_df = df.groupby([DataSchema_Building_Stock.ID_REGION,
                             DataSchema_Building_Stock.YEAR,
                             DataSchema_Building_Stock.MAIN_HEATING_TECHNOLOGY]).size().reset_index(
        name=DataSchema_Heating_Reference.BUILDING_NUMBER)

    grouped_df = grouped_df.rename(
        columns={DataSchema_Building_Stock.MAIN_HEATING_TECHNOLOGY: DataSchema_Heating_Reference.ID_HEATING_TECHNOLOGY}
    )

    grouped_df.to_csv(NUTS3_HEATING_TECHNOLOGY_PATH + "_preprocessed.csv", index=False)

    # Building efficiency class preprocessed table
    grouped_df = df.groupby([DataSchema_Building_Stock.ID_REGION,
                             DataSchema_Building_Stock.YEAR,
                             DataSchema_Building_Stock.ID_BUILDING_TYPE,
                             DataSchema_Building_Stock.ID_EFFICIENCY_CLASS]).size().reset_index(
        name=DataSchema_Heating_Reference.BUILDING_NUMBER)

    grouped_df = change_building_number_to_percentage(grouped_df)

    grouped_df.to_csv(NUTS3_EFFICIENCY_CLASS_PATH + "_preprocessed.csv", index=False)


def preprocess_nuts1_heating_data():
    print("Preprocess nuts1 heating data...")
    df = pd.read_csv(NUTS1_BUILDING_PATH + ".csv")
    df = df[df['id_sector'] == 6]  # Reference is only for Sector 6
    #df = df[(df['id_sector'] == 6) & (df['id_scenario'] == 10)]
    df = change_id_heating_technology(df)
    df = change_id_building_type(df)

    # Heating Technology preprocessed table
    grouped_df = df.groupby([DataSchema_Nuts1_Building_Stock.ID_REGION,
                             DataSchema_Nuts1_Building_Stock.YEAR,
                             DataSchema_Nuts1_Building_Stock.MAIN_HEATING_TECHNOLOGY])[DataSchema_Nuts1_Building_Stock.BUILDING_NUMBER].sum().reset_index(
        name=DataSchema_Heating_Reference.BUILDING_NUMBER)

    grouped_df = grouped_df.rename(
        columns={DataSchema_Nuts1_Building_Stock.MAIN_HEATING_TECHNOLOGY: DataSchema_Heating_Reference.ID_HEATING_TECHNOLOGY}
    )

    grouped_df[DataSchema_Heating_Reference.BUILDING_NUMBER] = grouped_df[DataSchema_Heating_Reference.BUILDING_NUMBER].round().astype(int)

    grouped_df.to_csv(NUTS1_HEATING_TECHNOLOGY_PATH + "_preprocessed.csv", index=False)

    # Building efficiency class preprocessed table
    print("Preprocess nuts1 efficiency class data...")
    grouped_df = df.groupby([DataSchema_Building_Stock.ID_REGION,
                             DataSchema_Building_Stock.YEAR,
                             DataSchema_Building_Stock.ID_BUILDING_TYPE,
                             DataSchema_Building_Stock.ID_EFFICIENCY_CLASS])[DataSchema_Nuts1_Building_Stock.BUILDING_NUMBER].sum().reset_index(
        name=DataSchema_Heating_Reference.BUILDING_NUMBER)

    grouped_df = change_building_number_to_percentage(grouped_df)

    grouped_df.to_csv(NUTS1_EFFICIENCY_CLASS_PATH + "_preprocessed.csv", index=False)


def preprocess_regional_reference_heating_data():
    print("Preprocess regional reference heating data...")
    df = pd.read_csv(REGIONAL_REFERENCE_BUILDING_PATH + ".csv")
    df = df[df[DataSchema_Heating_Reference.ID_REGION] != 9]
    df.to_csv(REGIONAL_REFERENCE_BUILDING_PATH + "_preprocessed.csv", index=False)


if __name__ == '__main__':
    print("Preprocess data for dashboards...")

    # preprocess_nuts1_energy_data()
    # preprocess_nuts3_energy_data()
    #preprocess_national_reference_energy_data()
    #preprocess_regional_reference_energy_data()

    # preprocess_nuts3_heating_data()
    preprocess_regional_reference_heating_data()
    preprocess_nuts1_heating_data()

    print("Finished preprocessing data!")
