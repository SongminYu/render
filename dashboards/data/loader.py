import pandas as pd


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


class DataSchema_Building_Stock:
    ID_SCENARIO = "id_scenario"
    ID_REGION = "id_region"
    ID_SECTOR = "id_sector"
    ID_SUBSECTOR = "id_subsector"
    YEAR = "year"
    ID_BUILDING_TYPE = "id_building_type"
    ID_BUILDING = "id_building"
    ID_BUILDING_CONSTRUCTION_PERIOD = "id_building_construction_period"

    APPLIANCE_ELECTRICITY_DEMAND = "appliance_electricity_demand"
    COOLING_DEMAND = "cooling_demand"

    MAIN_EC1_HEATING_DEMAND_CONSUMPTION = "main_ec1_heating_demand_consumption"
    MAIN_EC2_HEATING_DEMAND_CONSUMPTION = "main_ec2_heating_demand_consumption"
    SECOND_EC1_HEATING_DEMAND_CONSUMPTION = "second_ec1_heating_demand_consumption"
    SECOND_EC2_HEATING_DEMAND_CONSUMPTION = "second_ec2_heating_demand_consumption"
    TOTAL_HEATING_CONSUMPTION = "total_heating_consumption"

    MAIN_EC1_HOT_WATER_DEMAND_CONSUMPTION = "main_ec1_hot_water_demand_consumption"
    MAIN_EC2_HOT_WATER_DEMAND_CONSUMPTION = "main_ec2_hot_water_demand_consumption"
    SECOND_EC1_HOT_WATER_DEMAND_CONSUMPTION = "second_ec1_hot_water_demand_consumption"
    SECOND_EC2_HOT_WATER_DEMAND_CONSUMPTION = "second_ec2_hot_water_demand_consumption"
    TOTAL_HOT_WATER_CONSUMPTION = "total_hot_water_consumption"


def create_total_heating_consumption_column(df: pd.DataFrame) -> pd.DataFrame:
    columns = [DataSchema_Building_Stock.MAIN_EC1_HEATING_DEMAND_CONSUMPTION,
               DataSchema_Building_Stock.MAIN_EC2_HEATING_DEMAND_CONSUMPTION,
               DataSchema_Building_Stock.SECOND_EC1_HEATING_DEMAND_CONSUMPTION,
               DataSchema_Building_Stock.SECOND_EC2_HEATING_DEMAND_CONSUMPTION]

    for column in columns:
        df[column] = df[column].fillna(0)

    df[DataSchema_Building_Stock.TOTAL_HEATING_CONSUMPTION] = df[columns].sum(axis=1)
    return df


def create_total_hot_water_consumption_column(df: pd.DataFrame) -> pd.DataFrame:
    columns = [DataSchema_Building_Stock.MAIN_EC1_HOT_WATER_DEMAND_CONSUMPTION,
               DataSchema_Building_Stock.MAIN_EC2_HOT_WATER_DEMAND_CONSUMPTION,
               DataSchema_Building_Stock.SECOND_EC1_HOT_WATER_DEMAND_CONSUMPTION,
               DataSchema_Building_Stock.SECOND_EC2_HOT_WATER_DEMAND_CONSUMPTION]

    for column in columns:
        df[column] = df[column].fillna(0)

    df[DataSchema_Building_Stock.TOTAL_HOT_WATER_CONSUMPTION] = df[columns].sum(axis=1)
    return df


def preprocessing_building_stock_data(df: pd.DataFrame, path:str) -> pd.DataFrame:
    changed_df = False
    if DataSchema_Building_Stock.TOTAL_HEATING_CONSUMPTION not in df.columns:
        df = create_total_heating_consumption_column(df)
        changed_df = True
    if DataSchema_Building_Stock.TOTAL_HOT_WATER_CONSUMPTION not in df.columns:
        df = create_total_hot_water_consumption_column(df)
        changed_df = True

    if changed_df:
        df.to_csv(path, index=False)

    return df


def load_data(path: str) -> pd.DataFrame:
    # load the data from the CSV file
    data = pd.read_csv(path)
    return data
