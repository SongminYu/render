import copy
import os.path
from typing import List, Optional
from Melodie import Config
import pandas as pd
from models.render_building import cons
from tqdm import tqdm

BS = "building_stock"
BSS = "building_stock_summary"
FED = "final_energy_demand"
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


def get_base_d(row):
    base_d = {}
    for key_col in KEY_COLS:
        base_d[key_col] = row[key_col]
    return base_d


def get_region_table_names(cfg: "Config", file_name_prefix: str):
    region_table_names = []
    df = pd.read_excel(os.path.join(cfg.input_folder, "ID_Region.xlsx"))
    region_ids = df.loc[df["region_level"] == 3]["id_region"].to_list()
    for id_region in region_ids:
        region_table_name = f'{file_name_prefix}_R{id_region}'
        file_path = os.path.join(os.path.join(
            cfg.output_folder,
            cons.REGION_DATA_SUBFOLDER,
            f'{file_name_prefix}_R{id_region}.csv'
        ))
        if os.path.exists(file_path):
            region_table_names.append(region_table_name)
    return region_table_names


def process_region_building_stock(cfg: "Config", nuts_level: int = 3):
    for region_table_name in tqdm(get_region_table_names(cfg=cfg, file_name_prefix=BS), desc="processing region building stock"):
        region_building_stock = pd.read_csv(os.path.join(os.path.join(
            cfg.output_folder,
            cons.REGION_DATA_SUBFOLDER,
            f'{region_table_name}.csv'
        )))
        gen_final_energy_demand_from_region_building_stock(
            cfg=cfg,
            building_stock=region_building_stock,
            output_table_name=f'{FED}_{region_table_name.split("_")[-1]}'
        )
        aggregate_region_final_energy_demand(
            cfg=cfg,
            region_final_energy_demand_file_name=f'{FED}_{region_table_name.split("_")[-1]}',
            nuts_level=nuts_level
        )
        gen_region_building_stock_summary(
            cfg=cfg,
            building_stock=region_building_stock
        )


def gen_final_energy_demand_from_region_building_stock(
    cfg: "Config",
    building_stock: pd.DataFrame,
    output_table_name: str,
):

    def get_appliance_electricity():
        d = get_base_d(row=row)
        d.update({
            "id_end_use": cons.ID_END_USE_APPLIANCE,
            "id_energy_carrier": cons.ID_ENERGY_CARRIER_ELECTRICITY,
            "unit": "kWh",
            "value": row["appliance_electricity_demand"] * row["building_number"] * row["occupancy_rate"]
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
                "value": row["cooling_system_energy_consumption"] * row["building_number"] * row["occupancy_rate"]
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
                        "value": row[f"heating_system_{tech}_space_heating_energy_carrier_{energy_carrier}_energy_consumption"] * row["building_number"] * row["occupancy_rate"]
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
                        "value": row[f"heating_system_{tech}_hot_water_energy_carrier_{energy_carrier}_energy_consumption"] * row["building_number"] * row["occupancy_rate"]
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
                "value": row["ventilation_system_energy_consumption"] * row["building_number"] * row["occupancy_rate"]
            })
            l_ventilation.append(d)
        return l_ventilation

    l = []
    building_stock = building_stock.loc[building_stock["exists"] == 1]
    for index, row in building_stock.iterrows():
        l += get_appliance_electricity()
        l += get_space_cooling()
        l += get_space_heating()
        l += get_hot_water()
        l += get_ventilation()
    df = pd.DataFrame(l)
    group_ids = copy.deepcopy(KEY_COLS)
    group_ids += ['id_end_use', 'id_energy_carrier', 'unit']
    energy_demand_nuts3 = df.groupby(group_ids).agg({'value': 'sum'}).reset_index()
    energy_demand_nuts3.to_csv(
        os.path.join(
            cfg.output_folder,
            cons.REGION_DATA_SUBFOLDER,
            f'{output_table_name}.csv'
        ),
        index=False
    )


def aggregate_region_final_energy_demand(
    cfg: "Config",
    region_final_energy_demand_file_name: str,
    nuts_level: int
):
    assert nuts_level in [0, 1, 2, 3]
    energy_demand_nuts3 = pd.read_csv(os.path.join(
        cfg.output_folder,
        cons.REGION_DATA_SUBFOLDER,
        f'{region_final_energy_demand_file_name}.csv'
    ))
    if nuts_level < 3:
        region_df = pd.read_excel(os.path.join(os.path.dirname(os.path.abspath(__file__)), "region_mapping.xlsx"))
        d = dict(zip(region_df["id_nuts3"].to_list(), region_df[f"id_nuts{nuts_level}"].to_list()))
        energy_demand_nuts3.rename(columns={"id_region": "id_region_nuts3"}, inplace=True)
        energy_demand_nuts3["id_region"] = [d[id_region_nuts3] for id_region_nuts3 in energy_demand_nuts3["id_region_nuts3"]]
    group_by_cols = [
        "id_scenario",
        "id_region",
        "id_sector",
        "id_subsector",
        "id_end_use",
        "id_energy_carrier",
        "year",
        "unit",
    ]
    energy_demand_aggregated = energy_demand_nuts3.groupby(group_by_cols).agg({'value': 'sum'}).reset_index()
    save_dataframe(
        path=os.path.join(cfg.output_folder, f"{FED}_nuts{nuts_level}.csv"),
        df=energy_demand_aggregated,
        if_exists="append"
    )


def gen_region_building_stock_summary(
    cfg: "Config",
    building_stock: pd.DataFrame,
):
    info_cols = {
        'total_living_area': 'sum',
        'unit_number': 'sum',
        'population': 'sum',
        'appliance_electricity_demand_per_person': 'mean',
        'cooling_demand_per_m2': 'mean',
        'heating_demand_per_m2': 'mean',
        'hot_water_demand_per_person': 'mean',
        'hot_water_demand_per_m2': 'mean',
        'occupancy_rate': 'mean',
    }
    l = []
    building_stock = building_stock.loc[building_stock["exists"] == 1]
    for index, row in building_stock.iterrows():
        d = get_base_d(row=row)
        d["building_number"] = row["building_number"]
        for col_name, col_calc in info_cols.items():
            d[col_name] = row[col_name] * row["building_number"] if col_calc == "sum" else row[col_name]
        l.append(d)
    df = pd.DataFrame(l)
    info_cols["building_number"] = "sum"
    aggregated_df = df.groupby(KEY_COLS).agg(info_cols).reset_index()
    save_dataframe(
        path=os.path.join(cfg.output_folder, f'{BSS}.csv'),
        df=aggregated_df,
        if_exists="append"
    )


def gen_renovation_rate():
    ...


def gen_building_demolition_and_construction():
    # by processing the last year dataframe of the building stock, the results should be able to be generated.
    ...


def concat_region_tables(cfg: "Config", file_name_prefix_list: Optional[List[str]]):
    for file_name_prefix in file_name_prefix_list:
        print(f'Concating {file_name_prefix} tables...')
        df_list = []
        for region_table_name in get_region_table_names(cfg=cfg, file_name_prefix=file_name_prefix):
            file_path = os.path.join(os.path.join(
                cfg.output_folder,
                cons.REGION_DATA_SUBFOLDER,
                f'{region_table_name}.csv'
            ))
            df_list.append(pd.read_csv(file_path))
        df = pd.concat(df_list)
        df.to_csv(os.path.join(cfg.output_folder, f"{file_name_prefix}.csv"), index=False)


def extract_cols(
    cfg: "Config",
    input_table: str,
    cols: List[str],
):
    output_table = f"{input_table.split(".")[0]}_cols.csv"
    building_stock = pd.read_csv(os.path.join(cfg.output_folder, input_table))
    building_stock_cols = building_stock.loc[:, cols]
    building_stock_cols.to_csv(os.path.join(cfg.output_folder, output_table), index=False)


def save_dataframe(
    path,
    df: pd.DataFrame,
    if_exists: str = "append"
):
    if os.path.isfile(path):
        if if_exists == "append":
            df.to_csv(path, mode="a", header=False, index=False)
        elif if_exists == "replace":
            df.to_csv(path, index=False)
        elif if_exists == "pass":
            pass
        else:
            raise NotImplementedError(
                f"if_exists = {if_exists} --> not implemented."
            )
    else:
        df.to_csv(path, index=False)
