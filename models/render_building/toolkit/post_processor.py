import copy
import os.path
from typing import List, Optional
from Melodie import Config
import pandas as pd
from models.render_building import cons

KEY_COLS = [
    'id_scenario',
    'id_region',
    'id_sector',
    'id_subsector',
    'id_building_type',
    'id_building_construction_period',
    'id_building_efficiency_class',
    'id_building_location',
    'year',
]


def get_region_table_names(cfg: "Config", file_name_prefix: str):
    region_table_names = []
    region_ids = pd.read_excel(os.path.join(cfg.input_folder, "ID_Region.xlsx"))["id_region"].to_list()
    for id_region in region_ids:
        region_table_name = f'{file_name_prefix}_R{id_region}'
        file_path = os.path.join(os.path.join(cfg.output_folder, f'{file_name_prefix}_R{id_region}.csv'))
        if os.path.exists(file_path):
            region_table_names.append(region_table_name)
    return region_table_names


def concat_region_tables(cfg: "Config", file_name_prefix_list: Optional[List[str]] = None):
    if file_name_prefix_list is None:
        file_name_prefix_list = ["building_stock"]
    for file_name_prefix in file_name_prefix_list:
        print(f'Concating {file_name_prefix} tables...')
        df_list = []
        for region_table_name in get_region_table_names(cfg=cfg, file_name_prefix=file_name_prefix):
            file_path = os.path.join(os.path.join(cfg.output_folder, f'{region_table_name}.csv'))
            df_list.append(pd.read_csv(file_path))
        df = pd.concat(df_list)
        df.to_csv(os.path.join(cfg.output_folder, f"{file_name_prefix}.csv"), index=False)


def get_base_d(row):
    base_d = {}
    for key_col in KEY_COLS:
        base_d[key_col] = row[key_col]
    return base_d


def gen_final_energy_demand_from_building_stock(
    cfg: "Config",
    input_table: str = "building_stock.csv",
    output_table: str = "final_energy_demand.csv"
):

    def get_appliance_electricity():
        d = get_base_d(row=row)
        d.update({
            "id_end_use": cons.ID_END_USE_APPLIANCE,
            "id_energy_carrier": cons.ID_ENERGY_CARRIER_ELECTRICITY,
            "unit": "kWh",
            "value": row["appliance_electricity_demand"] * row["building_number"]
        })
        return [d]

    def get_space_cooling():
        l_space_cooling = []
        if pd.notna(row["cooling_system_id_energy_carrier"]):
            d = get_base_d(row=row)
            d.update({
                "id_end_use": cons.ID_END_USE_SPACE_COOLING,
                "id_energy_carrier": row["cooling_system_id_energy_carrier"],
                "unit": "kWh",
                "value": row["cooling_system_energy_consumption"] * row["building_number"]
            })
            l.append(d)
        return l_space_cooling

    def get_space_heating():
        l_space_heating = []
        for tech in ["main", "second"]:
            for energy_carrier in [1, 2]:
                if pd.notna(row[f"heating_system_{tech}_space_heating_energy_carrier_{energy_carrier}_id_energy_carrier"]):
                    d = get_base_d(row=row)
                    d.update({
                        "id_end_use": cons.ID_END_USE_SPACE_HEATING,
                        "id_energy_carrier": row[f"heating_system_{tech}_space_heating_energy_carrier_{energy_carrier}_id_energy_carrier"],
                        "unit": "kWh",
                        "value": row[f"heating_system_{tech}_space_heating_energy_carrier_{energy_carrier}_energy_consumption"] * row["building_number"]
                    })
                    l_space_heating.append(d)
        return l_space_heating

    def get_hot_water():
        l_hot_water = []
        for tech in ["main", "second"]:
            for energy_carrier in [1, 2]:
                if pd.notna(row[f"heating_system_{tech}_hot_water_energy_carrier_{energy_carrier}_id_energy_carrier"]):
                    d = get_base_d(row=row)
                    d.update({
                        "id_end_use": cons.ID_END_USE_HOT_WATER,
                        "id_energy_carrier": row[f"heating_system_{tech}_hot_water_energy_carrier_{energy_carrier}_id_energy_carrier"],
                        "unit": "kWh",
                        "value": row[f"heating_system_{tech}_hot_water_energy_carrier_{energy_carrier}_energy_consumption"] * row["building_number"]
                    })
                    l_hot_water.append(d)
        return l_hot_water

    def get_ventilation():
        l_ventilation = []
        if pd.notna(row["ventilation_system_id_energy_carrier"]):
            d = get_base_d(row=row)
            d.update({
                "id_end_use": cons.ID_END_USE_VENTILATION,
                "id_energy_carrier": row["ventilation_system_id_energy_carrier"],
                "unit": "kWh",
                "value": row["ventilation_system_energy_consumption"] * row["building_number"]
            })
            l_ventilation.append(d)
        return l_ventilation

    l = []
    building_stock = pd.read_csv(os.path.join(cfg.output_folder, input_table))
    for index, row in building_stock.iterrows():
        l += get_appliance_electricity()
        l += get_space_cooling()
        l += get_space_heating()
        l += get_hot_water()
        l += get_ventilation()
    df = pd.DataFrame(l)
    group_ids = copy.deepcopy(KEY_COLS)
    group_ids += ['id_end_use', 'id_energy_carrier', 'unit']
    aggregated_df = df.groupby(group_ids).agg({'value': 'sum'}).reset_index()
    aggregated_df.to_csv(os.path.join(cfg.output_folder, output_table), index=False)


def gen_building_stock_summary(
    cfg: "Config",
    input_table: str = "building_stock.csv",
    output_table: str = "building_stock_summary.csv"
):
    info_cols = {
        'total_living_area': 'sum',
        'population': 'sum',
        'appliance_electricity_demand_per_person': 'mean',
        'cooling_demand_per_m2': 'mean',
        'heating_demand_per_m2': 'mean',
        'hot_water_demand_per_person': 'mean',
        'hot_water_demand_per_m2': 'mean',
    }
    l = []
    df = pd.read_csv(os.path.join(cfg.output_folder, input_table))
    for index, row in df.iterrows():
        d = get_base_d(row=row)
        d["building_number"] = row["building_number"]
        for col_name, col_calc in info_cols.items():
            d[col_name] = row[col_name] * row["building_number"] if col_calc == "sum" else row[col_name]
        l.append(d)
    df = pd.DataFrame(l)
    info_cols["building_number"] = "sum"
    aggregated_df = df.groupby(KEY_COLS).agg(info_cols).reset_index()
    aggregated_df.to_csv(os.path.join(cfg.output_folder, output_table), index=False)



