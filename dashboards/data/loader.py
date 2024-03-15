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
    ID_BUILDING_TYPE = "id_building_type"
    ID_BUILDING = "id_building"
    ID_BUILDING_CONSTRUCTION_PERIOD = "id_building_construction_period"
    ID_APPLIANCE_ELECTRICITY_DEMAND = "appliance_electricity_demand"


def load_data(path: str) -> pd.DataFrame:
    # load the data from the CSV file
    data = pd.read_csv(
        path,
    )
    return data
