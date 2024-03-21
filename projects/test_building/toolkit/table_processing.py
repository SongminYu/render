import os

import pandas as pd
from Melodie import Config


def read_dataframe(file_path: str):
    if file_path.endswith(".xlsx"):
        df = pd.read_excel(file_path)
    else:
        df = pd.read_csv(file_path)
    return df


def concat_region_tables(cfg: "Config", file_name_prefix: str):
    df_list = []
    region_ids = read_dataframe(os.path.join(cfg.input_folder, "ID_Region.xlsx"))["id_region"].to_list()
    for id_region in region_ids:
        file_path = os.path.join(os.path.join(cfg.output_folder, f'{file_name_prefix}_R{id_region}.csv'))
        if os.path.exists(file_path):
            df_list.append(read_dataframe(file_path))
    df = pd.concat(df_list)
    df.to_csv(os.path.join(cfg.output_folder, f"{file_name_prefix}.csv"), index=False)
    for id_sector in df["id_sector"].unique():
        df_sector = df.loc[df["id_sector"] == id_sector]
        if file_name_prefix == "energy_consumption":
            df_sector.loc[:, "value"] = df_sector["value"]/10**9
            df_sector.loc[:, "unit"] = "TWh"
            df_sector_heating = df_sector.loc[df_sector["id_end_use"] == 3]
            df_sector_heating.to_csv(os.path.join(cfg.output_folder, f"{file_name_prefix}_Sector{id_sector}_SpaceHeating.csv"), index=False)
        df_sector.to_csv(os.path.join(cfg.output_folder, f"{file_name_prefix}_Sector{id_sector}.csv"), index=False)


def find_id(cfg: "Config", id_name: str):

    def get_data_files():
        return [
            file for file in os.listdir(cfg.input_folder) if
            file.endswith(".xlsx") or file.endswith(".csv")
        ]

    files = []
    print(f'Following tables are relevant to {id_name} --> ')
    for file_name in get_data_files():
        df = pd.read_excel(os.path.join(cfg.input_folder, file_name), engine='openpyxl')
        if id_name in list(df.columns):
            files.append(file_name)
    if files:
        for file_name in files:
            print(file_name)
    else:
        print(f"No table is relevant to {id_name}.")
    return files
