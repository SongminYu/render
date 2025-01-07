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
Process region building stock --> final energy demand, building stock summary
"""

BS = "building_stock"
BSS = "building_stock_summary"
FED = "final_energy_demand"
PV = "pv_generation"
HT = "heating_tech"
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
    'total_heating_per_m2_norm': 'mean',
    'hot_water_demand_per_person': 'mean',
    'hot_water_demand_per_m2': 'mean',
    'occupancy_rate': 'mean',
}
PV_AGG_COLS = {
    "pv_size": "sum",
    "pv_generation": "sum",
    "pv_self_consumption": "sum",
    "pv_2_grid": "sum",
}

HT_KEY_COLS = [
    'id_scenario',
    'id_region',
    'id_sector',
    'id_subsector',
    'id_building_type',
    'id_building_construction_period',
    'id_building_efficiency_class',
    'id_building_location',
    'year',
    'heating_system_main_id_heating_technology',
    'heating_system_main_space_heating_energy_carrier_1_id_energy_carrier',
]

HT_AGG_COLS = {"building_number": 'sum'}

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
        gen_pv_generation_from_region_building_stock(
            cfg=cfg,
            building_stock=region_building_stock,
            output_table_name=f'{PV}_{region_table_name.split("_")[-1]}'
        )
        gen_region_building_stock_summary(
            cfg=cfg,
            building_stock=region_building_stock,
            output_table_name=f'{BSS}_{region_table_name.split("_")[-1]}'
        )
        gen_region_heating_tech_from_region_building_stock(
            cfg=cfg,
            building_stock=region_building_stock,
            output_table_name=f'{HT}_{region_table_name.split("_")[-1]}'
        )


    tasks = [
        {
            "region_table_name": region_table_name
        }
        for region_table_name in get_region_table_names(cfg=cfg, file_name_prefix=BS)
    ]
    Parallel(n_jobs=cores)(delayed(process_region)(**task) for task in tasks)


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


def gen_pv_generation_from_region_building_stock(
    cfg: "Config",
    building_stock: pd.DataFrame,
    output_table_name: str,
):

    def get_pv_generation():
        l_pv_generation = []
        factor = row["building_number"] * row["occupancy_rate"]
        if row["pv_adoption"]:
            d = get_base_d(row=row)
            d.update({
                "pv_size": row["pv_size"] * factor,
                "pv_size_unit": "kW_peak",
                "pv_generation": row["pv_generation"] * factor,
                "pv_self_consumption": row["pv_self_consumption"] * factor,
                "pv_2_grid": row["pv_2_grid"] * factor,
                "pv_generation_unit": "kWh",
            })
            l_pv_generation.append(d)
        return l_pv_generation

    l = []
    building_stock = building_stock.loc[building_stock["exists"] == 1]
    for _, row in building_stock.iterrows():
        l += get_pv_generation()
    df = pd.DataFrame(l)
    group_ids = copy.deepcopy(KEY_COLS)
    group_ids += ['pv_size_unit', 'pv_generation_unit']
    pv_generation_nuts3 = df.groupby(group_ids).agg(PV_AGG_COLS).reset_index()
    save_dataframe(
        path=os.path.join(cfg.output_folder, cons.REGION_DATA_SUBFOLDER, f'{output_table_name}.csv'),
        df=pv_generation_nuts3,
        if_exists="replace"
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

def gen_region_heating_tech_from_region_building_stock(
    cfg: "Config",
    building_stock: pd.DataFrame,
    output_table_name: str
):
    l = []
    building_stock = building_stock.loc[building_stock["exists"] == 1]
    for index, row in building_stock.iterrows():
        d = get_base_d(row=row)
        d["heating_system_main_id_heating_technology"] = row["heating_system_main_id_heating_technology"]
        d["heating_system_main_space_heating_energy_carrier_1_id_energy_carrier"] = row["heating_system_main_space_heating_energy_carrier_1_id_energy_carrier"]
        d["building_number"] = row["building_number"]
        l.append(d)
    df = pd.DataFrame(l)
    aggregated_df = df.groupby(HT_KEY_COLS).agg(HT_AGG_COLS).reset_index()
    save_dataframe(
        path=os.path.join(cfg.output_folder, cons.REGION_DATA_SUBFOLDER, f'{output_table_name}.csv'),
        df=aggregated_df,
        if_exists="replace"
    )


"""
Aggregate region building stock
"""

AGG_FED_KEY_COLS = [
    "id_scenario",
    "id_region",
    "id_sector",
    "id_subsector",
    "id_end_use",
    "id_energy_carrier",
    "year",
    "unit",
]
AGG_FED_AGG_COLS = {'value': 'sum'}

AGG_PV_KEY_COLS = [
    "id_scenario",
    "id_region",
    "id_sector",
    "id_subsector",
    "year",
    "pv_size_unit",
    "pv_generation_unit"
]


def aggregate_region_building_stock(cfg: "Config", nuts_level: int = 3):
    fed_output = f"{FED}_nuts{nuts_level}.csv"
    pv_output = f"{PV}_nuts{nuts_level}.csv"
    bss_output = f"{BSS}_nuts{nuts_level}.csv"
    ht_output = f"{HT}_nuts{nuts_level}.csv"
    # regional aggregation
    for region_table_name in tqdm(
        get_region_table_names(cfg=cfg, file_name_prefix=BS),
        desc="aggregating region building stock"
    ):
        aggregate_region_final_energy_demand(
            cfg=cfg,
            region_final_energy_demand_file_name=f'{FED}_{region_table_name.split("_")[-1]}',
            output_file_name=fed_output,
            nuts_level=nuts_level
        )
        aggregate_region_pv_generation(
            cfg=cfg,
            region_final_energy_demand_file_name=f'{PV}_{region_table_name.split("_")[-1]}',
            output_file_name=pv_output,
            nuts_level=nuts_level
        )
        aggregate_region_building_stock_summary(
            cfg=cfg,
            region_building_stock_summary_file_name=f'{BSS}_{region_table_name.split("_")[-1]}',
            output_file_name=bss_output,
            nuts_level=nuts_level
        )
        aggregate_region_heating_tech(
            cfg=cfg,
            region_heating_tech_file_name=f'{HT}_{region_table_name.split("_")[-1]}',
            output_file_name=ht_output,
            nuts_level=nuts_level
        )
    # final aggregation
    if nuts_level < 3:
        fed_path = os.path.join(cfg.output_folder, fed_output)
        df_fed = pd.read_csv(fed_path)
        save_dataframe(
            path=fed_path,
            df=df_fed.groupby(AGG_FED_KEY_COLS).agg(AGG_FED_AGG_COLS).reset_index(),
            if_exists="replace"
        )
        pv_path = os.path.join(cfg.output_folder, pv_output)
        df_pv = pd.read_csv(pv_path)
        save_dataframe(
            path=pv_path,
            df=df_pv.groupby(AGG_PV_KEY_COLS).agg(PV_AGG_COLS).reset_index(),
            if_exists="replace"
        )
        bss_path = os.path.join(cfg.output_folder, bss_output)
        df_bss = pd.read_csv(bss_path)
        save_dataframe(
            path=bss_path,
            df=df_bss.groupby(KEY_COLS).agg(AGG_COLS).reset_index(),
            if_exists="replace"
        )
        ht_path = os.path.join(cfg.output_folder, ht_output)
        df_ht = pd.read_csv(ht_path)
        save_dataframe(
            path=ht_path,
            df=df_ht.groupby(HT_KEY_COLS).agg(HT_AGG_COLS).reset_index(),
            if_exists="replace"
        )


def replace_nuts3_region_id(df_nuts3: pd.DataFrame, nuts_level: int):
    region_df = pd.read_excel(os.path.join(os.path.dirname(os.path.abspath(__file__)), "region_mapping.xlsx"))
    df_nuts3 = df_nuts3[df_nuts3["id_region"].isin(region_df["id_nuts3"])]
    d = dict(zip(region_df["id_nuts3"].to_list(), region_df[f"id_nuts{nuts_level}"].to_list()))
    df_nuts3.rename(columns={"id_region": "id_region_nuts3"}, inplace=True)
    df_nuts3["id_region"] = [d[id_region_nuts3] for id_region_nuts3 in df_nuts3["id_region_nuts3"]]
    df = df_nuts3.drop(columns=["id_region_nuts3"])
    return df


def aggregate_nuts_level(df_nuts3: pd.DataFrame, nuts_level: int, group_by_cols: List[str], agg_cols: Dict[str, str]):
    if nuts_level < 3:
        df_nuts3 = replace_nuts3_region_id(df_nuts3, nuts_level)
    return df_nuts3.groupby(group_by_cols).agg(agg_cols).reset_index()


def aggregate_region_final_energy_demand(
    cfg: "Config",
    region_final_energy_demand_file_name: str,
    output_file_name: str,
    nuts_level: int
):
    assert nuts_level in [0, 1, 2, 3]
    energy_demand_nuts3 = pd.read_csv(os.path.join(
        cfg.output_folder,
        cons.REGION_DATA_SUBFOLDER,
        f'{region_final_energy_demand_file_name}.csv'
    ))
    save_dataframe(
        path=os.path.join(cfg.output_folder, output_file_name),
        df=aggregate_nuts_level(
            df_nuts3=energy_demand_nuts3,
            nuts_level=nuts_level,
            group_by_cols=AGG_FED_KEY_COLS,
            agg_cols=AGG_FED_AGG_COLS
        ),
        if_exists="append"
    )


def aggregate_region_pv_generation(
    cfg: "Config",
    region_final_energy_demand_file_name: str,
    output_file_name: str,
    nuts_level: int
):
    assert nuts_level in [0, 1, 2, 3]
    pv_generation_nuts3 = pd.read_csv(os.path.join(
        cfg.output_folder,
        cons.REGION_DATA_SUBFOLDER,
        f'{region_final_energy_demand_file_name}.csv'
    ))
    save_dataframe(
        path=os.path.join(cfg.output_folder, output_file_name),
        df=aggregate_nuts_level(
            df_nuts3=pv_generation_nuts3,
            nuts_level=nuts_level,
            group_by_cols=AGG_PV_KEY_COLS,
            agg_cols=PV_AGG_COLS
        ),
        if_exists="append"
    )


def aggregate_region_building_stock_summary(
    cfg: "Config",
    region_building_stock_summary_file_name: str,
    output_file_name: str,
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
        path=os.path.join(cfg.output_folder, output_file_name),
        df=aggregate_nuts_level(
            df_nuts3=building_stock_summary_nuts3,
            nuts_level=nuts_level,
            group_by_cols=KEY_COLS,
            agg_cols=AGG_COLS
        ),
        if_exists="append"
    )

def aggregate_region_heating_tech(
    cfg: "Config",
    region_heating_tech_file_name: str,
    output_file_name: str,
    nuts_level: int
):
    assert nuts_level in [0, 1, 2, 3]
    heating_tech_nuts3 = pd.read_csv(os.path.join(
        cfg.output_folder,
        cons.REGION_DATA_SUBFOLDER,
        f'{region_heating_tech_file_name}.csv'
    ))
    save_dataframe(
        path=os.path.join(cfg.output_folder, output_file_name),
        df=aggregate_nuts_level(
            df_nuts3=heating_tech_nuts3,
            nuts_level=nuts_level,
            group_by_cols=HT_KEY_COLS,
            agg_cols=HT_AGG_COLS
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
    output_table = f"{input_table.split('.')[0]}_cols.csv"
    building_stock = pd.read_csv(os.path.join(cfg.output_folder, input_table))
    building_stock_cols = building_stock.loc[:, cols]
    building_stock_cols.to_csv(os.path.join(cfg.output_folder, output_table), index=False)


"""
Renovation actions

Following functions are used to generate the annual renovation rate at national level. 
The main steps are written in the function `gen_renovation_rate`.
(1) building_stock_summary_nuts0.csv --> renovation_building_component_area_total.csv
(2) renovation_actions.csv --> renovation_building_component_area_renovated.csv
(3) renovation_building_component_area_total.csv + renovation_building_component_area_renovated.csv --> renovation_rate.csv
"""


def gen_renovation_rate(cfg: "Config"):
    """
    Only run this function when all nuts3 regions are finished.
    And, the "building_stock_summary_nuts0.csv" file is generated.
    """
    aggregate_building_component_area(cfg=cfg)
    aggregate_renovation_actions(cfg=cfg)
    calculate_renovation_rate(cfg=cfg)


def aggregate_building_component_area(cfg: "Config"):

    def get_building_component_ids():
        id_building_component = pd.read_excel(os.path.join(cfg.input_folder, "ID_BuildingComponent.xlsx"))
        return dict(zip(id_building_component["name"], id_building_component["id_building_component"]))

    df = pd.read_csv(os.path.join(cfg.output_folder, "building_stock_summary_nuts0.csv"))
    df_agg = df.groupby(["id_scenario", "id_region", "id_sector", "year"]).agg({
        "wall_area": "sum",
        "window_area": "sum",
        "roof_area": "sum",
        "basement_area": "sum",
    }).reset_index()
    building_component_ids = get_building_component_ids()

    l = []
    for _, row in df_agg.iterrows():
        for component in ["wall", "window", "roof", "basement"]:
            l.append({
                "id_scenario": row["id_scenario"],
                "id_region": row["id_region"],
                "id_sector": row["id_sector"],
                "id_building_component": building_component_ids[component],
                "year": row["year"],
                "value": row[f"{component}_area"]
            })
    pd.DataFrame(l).to_csv(os.path.join(cfg.output_folder, "renovation_building_component_area_total.csv"), index=False)


def aggregate_renovation_actions(cfg: "Config"):
    df = pd.read_csv(os.path.join(cfg.output_folder, "renovation_actions.csv"))
    df["value"] = df["component_area"] * df["building_number"]
    df = replace_nuts3_region_id(df_nuts3=df, nuts_level=0)
    df_agg = df.groupby(["id_scenario", "id_region", "id_sector", "id_building_component", "year"]).agg({"value": "sum"}).reset_index()
    df_agg.to_csv(os.path.join(cfg.output_folder, "renovation_building_component_area_renovated.csv"), index=False)


def calculate_renovation_rate(cfg: "Config"):

    def get_building_component_names():
        id_building_component = pd.read_excel(os.path.join(cfg.input_folder, "ID_BuildingComponent.xlsx"))
        return dict(zip(id_building_component["id_building_component"], id_building_component["name"]))

    def get_renovated_area():
        d = {}
        for _, row in df_renovated.iterrows():
            d[(row["id_scenario"], row["id_region"], row["id_sector"], row["id_building_component"], row["year"])] = row["value"]
        return d

    df_renovated = pd.read_csv(os.path.join(cfg.output_folder, "renovation_building_component_area_renovated.csv"))
    years = df_renovated["year"].unique()
    renovated_area = get_renovated_area()
    building_component_names = get_building_component_names()
    df_total = pd.read_csv(os.path.join(cfg.output_folder, "renovation_building_component_area_total.csv"))
    df_total_pivot = df_total.pivot_table(
        index=["id_scenario", "id_region", "id_sector", "year"],
        columns="id_building_component",
        values='value'
    ).reset_index()
    l = []
    for _, row in df_total_pivot.iterrows():
        if row["year"] in years:
            l.append({
                "id_scenario": row["id_scenario"],
                "id_region": row["id_region"],
                "id_sector": row["id_sector"],
                "year": row["year"],
                f"{building_component_names[1]}": renovated_area[(row["id_scenario"], row["id_region"], row["id_sector"], 1, row["year"])]/row[1],
                f"{building_component_names[2]}": renovated_area[(row["id_scenario"], row["id_region"], row["id_sector"], 2, row["year"])]/row[2],
                f"{building_component_names[3]}": renovated_area[(row["id_scenario"], row["id_region"], row["id_sector"], 3, row["year"])]/row[3],
                f"{building_component_names[4]}": renovated_area[(row["id_scenario"], row["id_region"], row["id_sector"], 4, row["year"])]/row[4],
            })
    df = pd.DataFrame(l)
    df["average"] = df["wall"] * 0.4 + df["roof"] * 0.28 + df["basement"] * 0.23 + df["window"] * 0.09
    df.to_csv(os.path.join(cfg.output_folder, "renovation_rate.csv"), index=False)


"""
Building demolition and construction
"""


def agg_building_number(df: pd.DataFrame):
    df = replace_nuts3_region_id(df, nuts_level=0)
    df = df.groupby(["id_scenario", "id_region", "id_sector", "year"]).agg({"value": "sum"}).reset_index()
    d = {}
    for _, row in df.iterrows():
        d[(row["id_scenario"], row["id_region"], row["id_sector"], row["year"])] = row["value"]
    return d


def gen_demolition_rate(cfg: "Config"):
    demolition = agg_building_number(pd.read_csv(os.path.join(cfg.output_folder, "building_demolition_number.csv")))
    building = agg_building_number(pd.read_csv(os.path.join(cfg.output_folder, "building_number.csv")))
    l = []
    for key, value in building.items():
        if key in demolition.keys():
            demolished_building = demolition[key]
        else:
            demolished_building = 0
        l.append({
            "id_scenario": key[0],
            "id_region": key[1],
            "id_sector": key[2],
            "year": key[3],
            "value": demolished_building / value
        })
    pd.DataFrame(l).to_csv(os.path.join(cfg.output_folder, "demolition_rate.csv"), index=False)


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


"""
add CO2 emission
"""

def add_emission_to_fed(cfg: "Config", fed_file: str):

    def get_ef_dict():
        # id_scenario and id_region are not considered, i.e., assuming there is only one combination of the two
        d = {}
        years = [int(col) for col in ef.columns if col.startswith("2")]
        for _, row in ef.iterrows():
            for year in years:
                d[row["id_energy_carrier"], year] = row[str(year)]
        return d

    fed = pd.read_csv(os.path.join(cfg.output_folder, f"{fed_file}.csv"))
    ef = pd.read_excel(os.path.join(cfg.input_folder, f"Scenario_EnergyCarrier_EmissionFactor.xlsx"))
    ef_dict = get_ef_dict()
    fed.rename(columns={"unit": "unit_energy_demand"}, inplace=True)
    fed["unit_emission"] = "tCO2"
    fed["emission"] = fed.apply(
        lambda row: row["value"] * ef_dict[(row["id_energy_carrier"], row["year"])], axis=1
    )
    fed.rename(columns={"value": "energy_demand"}, inplace=True)
    save_dataframe(
        path=os.path.join(cfg.output_folder, f"{fed_file}_with_emission.csv"),
        df=fed,
        if_exists="replace"
    )



