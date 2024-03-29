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

    END_USE = 'end_use'

    APPLIANCE_ELECTRICITY_DEMAND = "appliance_electricity_demand"

    # has to be extended by 'id_energy_carrier' or 'consumption'
    SPACE_HEATING = ["heating_system_main_space_heating_energy_carrier_1",
                     "heating_system_main_space_heating_energy_carrier_2",
                     "heating_system_second_space_heating_energy_carrier_1",
                     "heating_system_second_space_heating_energy_carrier_2"
                     ]

    HOT_WATER = ["heating_system_main_hot_water_energy_carrier_1",
                 "heating_system_main_hot_water_energy_carrier_2",
                 "heating_system_second_hot_water_energy_carrier_1",
                 "heating_system_second_hot_water_energy_carrier_2"]

    COOLING = ["cooling_system"]

    VENTILATION = ["ventilation_system"]


def create_end_use_table(df: pd.DataFrame, general_columns, end_use, end_use_columns) -> pd.DataFrame:
    rename_col = ['id_energy_carrier', 'energy_consumption']
    end_use_dfs = []

    temp_cols = {}
    for i, end_use_id in enumerate(end_use_columns):
        temp_cols[i] = [f'{end_use_id}_id_energy_carrier', f'{end_use_id}_energy_consumption']
        temp_df = df[general_columns + temp_cols[i]]
        rename = {}
        for j, column in enumerate(temp_cols[i]):
            rename[column] = rename_col[j]
        end_use_dfs.append(temp_df.rename(columns=rename))

    end_use_df = pd.concat(end_use_dfs, ignore_index=True)

    for column in rename_col:
        end_use_df[column] = end_use_df[column].fillna(0)

    end_use_df[DataSchema_Building_Stock.END_USE] = end_use

    return end_use_df


def create_appliances_table(df: pd.DataFrame, general_columns) -> pd.DataFrame:
    appliances = df[general_columns + [DataSchema_Building_Stock.APPLIANCE_ELECTRICITY_DEMAND]]

    appliances = appliances.rename(columns={DataSchema_Building_Stock.APPLIANCE_ELECTRICITY_DEMAND: 'energy_consumption'})
    appliances['energy_consumption'] = appliances['energy_consumption'].fillna(0)

    appliances['id_energy_carrier'] = 1
    appliances['end_use'] = 'appliances'

    return appliances


def preprocessing_building_stock_data(df: pd.DataFrame, general_columns, path: str) -> pd.DataFrame:
    space_heating = create_end_use_table(df, general_columns, 'space_heating', DataSchema_Building_Stock.SPACE_HEATING)
    hot_water = create_end_use_table(df, general_columns, 'hot_water', DataSchema_Building_Stock.HOT_WATER)
    cooling = create_end_use_table(df, general_columns, 'cooling', DataSchema_Building_Stock.COOLING)
    ventilation = create_end_use_table(df, general_columns, 'appliances', DataSchema_Building_Stock.VENTILATION)
    appliances = create_appliances_table(df, general_columns)

    end_use = pd.concat([space_heating, hot_water, cooling, ventilation, appliances], ignore_index=True)
    end_use.to_csv(path, index=False)
    return end_use


def load_data(path: str) -> pd.DataFrame:
    # load the data from the CSV file
    data = pd.read_csv(path)
    return data
