import copy
import os.path
from typing import List, Optional, Dict

import pandas as pd
from Melodie import Config
from joblib import Parallel
from joblib import delayed
from tqdm import tqdm

from models.render_building import cons
from utils.logger import get_logger

log = get_logger(__name__)

"""
Building stock --> final energy demand, building stock summary
"""


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
AGG_COLS = {
    'total_living_area': 'sum',
    'unit_number': 'sum',
    'population': 'sum',
    'wall_area': 'sum',
    'window_area': 'sum',
    'roof_area': 'sum',
    'basement_area': 'sum',
    'cooling_demand_per_m2': 'mean',
    'heating_demand_per_m2': 'mean',
    'hot_water_demand_per_person': 'mean',
    'hot_water_demand_per_m2': 'mean',
    'occupancy_rate': 'mean',
}


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


def process_region_building_stock(cfg: "Config", cores: int = 4):

    def process_region(region_table_name):
        log.info(f"processing {region_table_name}")
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
        gen_region_building_stock_summary(
            cfg=cfg,
            building_stock=region_building_stock,
            output_table_name=f'{BSS}_{region_table_name.split("_")[-1]}'
        )

    tasks = [
        {
            "region_table_name": region_table_name
        }
        for region_table_name in get_region_table_names(cfg=cfg, file_name_prefix=BS)
    ]
    Parallel(n_jobs=cores)(delayed(process_region)(**task) for task in tasks)


def aggregate_region_building_stock(cfg: "Config", nuts_level: int = 3):
    for region_table_name in tqdm(
        get_region_table_names(cfg=cfg, file_name_prefix=BS),
        desc="aggregating region building stock"
    ):
        aggregate_region_final_energy_demand(
            cfg=cfg,
            region_final_energy_demand_file_name=f'{FED}_{region_table_name.split("_")[-1]}',
            nuts_level=nuts_level
        )
        aggregate_region_building_stock_summary(
            cfg=cfg,
            region_building_stock_summary_file_name=f'{BSS}_{region_table_name.split("_")[-1]}',
            nuts_level=nuts_level
        )


def gen_final_energy_demand_from_region_building_stock(
    cfg: "Config",
    building_stock: pd.DataFrame,
    output_table_name: str,
):

    def get_appliance_electricity():
        l_appliance = []
        for col in building_stock.columns:
            if col.startswith("appliance_demand_energy_carrier"):
                if row[col] > 0:
                    d = get_base_d(row=row)
                    d.update({
                        "id_end_use": cons.ID_END_USE_APPLIANCE,
                        "id_energy_carrier": int(col.split("_")[-1]),
                        "unit": "kWh",
                        "value": row[col] * row["building_number"] * row["occupancy_rate"]
                    })
                    l_appliance.append(d)
        return l_appliance

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
            l_space_cooling.append(d)
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
    save_dataframe(
        path=os.path.join(
            cfg.output_folder,
            cons.REGION_DATA_SUBFOLDER,
            f'{output_table_name}.csv'
        ),
        df=energy_demand_nuts3,
        if_exists="replace"
    )


def aggregate_nuts_level(df_nuts3: pd.DataFrame, nuts_level: int, group_by_cols: List[str], agg_cols: Dict[str, str]):
    if nuts_level < 3:
        region_df = pd.read_excel(os.path.join(os.path.dirname(os.path.abspath(__file__)), "region_mapping.xlsx"))
        d = dict(zip(region_df["id_nuts3"].to_list(), region_df[f"id_nuts{nuts_level}"].to_list()))
        df_nuts3.rename(columns={"id_region": "id_region_nuts3"}, inplace=True)
        df_nuts3["id_region"] = [d[id_region_nuts3] for id_region_nuts3 in df_nuts3["id_region_nuts3"]]
    return df_nuts3.groupby(group_by_cols).agg(agg_cols).reset_index()


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
    save_dataframe(
        path=os.path.join(cfg.output_folder, f"{FED}_nuts{nuts_level}.csv"),
        df=aggregate_nuts_level(
            df_nuts3=energy_demand_nuts3,
            nuts_level=nuts_level,
            group_by_cols=[
                "id_scenario",
                "id_region",
                "id_sector",
                "id_subsector",
                "id_end_use",
                "id_energy_carrier",
                "year",
                "unit",
            ],
            agg_cols={'value': 'sum'}
        ),
        if_exists="append"
    )


def gen_region_building_stock_summary(
    cfg: "Config",
    building_stock: pd.DataFrame,
    output_table_name: str
):
    l = []
    building_stock = building_stock.loc[building_stock["exists"] == 1]
    for index, row in building_stock.iterrows():
        d = get_base_d(row=row)
        d["building_number"] = row["building_number"]
        for col_name, col_calc in AGG_COLS.items():
            d[col_name] = row[col_name] * row["building_number"] if col_calc == "sum" else row[col_name]
        l.append(d)
    df = pd.DataFrame(l)
    AGG_COLS["building_number"] = "sum"
    aggregated_df = df.groupby(KEY_COLS).agg(AGG_COLS).reset_index()
    save_dataframe(
        path=os.path.join(cfg.output_folder, cons.REGION_DATA_SUBFOLDER, f'{output_table_name}.csv'),
        df=aggregated_df,
        if_exists="replace"
    )


def aggregate_region_building_stock_summary(
    cfg: "Config",
    region_building_stock_summary_file_name: str,
    nuts_level: int
):
    assert nuts_level in [0, 1, 2, 3]
    building_stock_summary_nuts3 = pd.read_csv(os.path.join(
        cfg.output_folder,
        cons.REGION_DATA_SUBFOLDER,
        f'{region_building_stock_summary_file_name}.csv'
    ))
    AGG_COLS["building_number"] = "sum"
    save_dataframe(
        path=os.path.join(cfg.output_folder, f"{BSS}_nuts{nuts_level}.csv"),
        df=aggregate_nuts_level(
            df_nuts3=building_stock_summary_nuts3,
            nuts_level=nuts_level,
            group_by_cols=[
                "id_scenario",
                "id_region",
                "id_sector",
                "id_subsector",
                "id_building_type",
                "id_building_construction_period",
                "id_building_efficiency_class",
                "id_building_location",
                "year",
            ],
            agg_cols=AGG_COLS
        ),
        if_exists="append"
    )


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


"""
Renovation actions
"""


def gen_renovation_rate(cfg: "Config"):
    """
    (1) Create the building summary file
    (2) Aggregate the summary file:
        (2.1) keep the ids that are consistent with expected output of renovation rate table
        (2.2) aggregate the values of building number and building component area
    (3) Calculate the renovation rate per definition
    """
    df = pd.read_csv(os.path.join(cfg.output_folder, "renovation_actions.csv"))


"""
Heating system modernization actions
"""


"""
Building demolition and construction
"""


def gen_building_demolition_and_construction():
    # by processing the last year dataframe of the building stock, the results should be able to be generated.
    ...




"""
Save data
"""
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


