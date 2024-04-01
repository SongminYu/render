import os
import sqlite3
import pandas as pd
from Melodie import Config


def read_dataframe(file_path: str):
    if file_path.endswith(".xlsx"):
        df = pd.read_excel(file_path)
    else:
        df = pd.read_csv(file_path)
    return df


def get_data_files(folder: str):
    return [
        file for file in os.listdir(folder) if
        file.endswith(".xlsx") or file.endswith(".csv")
    ]


def concat_region_tables(cfg: "Config", file_name_prefix: str):
    print(f'Concating {file_name_prefix} tables...')
    df_list = []
    region_ids = read_dataframe(os.path.join(cfg.input_folder, "ID_Region.xlsx"))["id_region"].to_list()
    for id_region in region_ids:
        file_path = os.path.join(os.path.join(cfg.output_folder, f'{file_name_prefix}_R{id_region}.csv'))
        if os.path.exists(file_path):
            df_list.append(read_dataframe(file_path))
    df = pd.concat(df_list)
    df.to_csv(os.path.join(cfg.output_folder, f"{file_name_prefix}.csv"), index=False)
    if "id_sector" in df.columns:
        for id_sector in df["id_sector"].unique():
            df_sector = df.loc[df["id_sector"] == id_sector]
            if file_name_prefix == "final_energy_demand":
                df_sector.loc[:, "value"] = df_sector["value"]/10**9
                df_sector.loc[:, "unit"] = "TWh"
                for id_end_use in [1, 2, 3, 4, 5]:
                    df_sector_end_use = df_sector.loc[df_sector["id_end_use"] == id_end_use]
                    df_sector_end_use.to_csv(os.path.join(cfg.output_folder, f"{file_name_prefix}_Sector{id_sector}_EndUse{id_end_use}.csv"), index=False)
            df_sector.to_csv(os.path.join(cfg.output_folder, f"{file_name_prefix}_Sector{id_sector}.csv"), index=False)


def get_id_relevant_tables(cfg: "Config", id_name: str):

    tables = {}
    for file_name in get_data_files(cfg.input_folder):
        df = read_dataframe(os.path.join(cfg.input_folder, file_name))
        if id_name in list(df.columns):
            tables[file_name] = df
    return tables


def find_id(cfg: "Config", id_name: str):
    tables = get_id_relevant_tables(cfg=cfg, id_name=id_name)
    if tables:
        print(f'Following tables include `{id_name}` --> ')
        for file_name in tables.keys():
            print(file_name)
    else:
        print(f"No table is relevant to {id_name}.")


def extract_id_data(cfg: "Config", id_name: str, id_value: int):
    tables = get_id_relevant_tables(cfg=cfg, id_name=id_name)
    for table_name, table_df in tables.items():
        table_df = table_df.loc[table_df[id_name] == id_value]
        file_name, ext = table_name.split(".")
        table_df.to_csv(os.path.join(cfg.output_folder, f'{file_name}_{id_name}_{id_value}.csv'), index=False)


def pack_sqlite(cfg: "Config"):
    file_names = get_data_files(cfg.input_folder)
    conn = sqlite3.connect(os.path.join(cfg.output_folder, f'{cfg.project_name}.sqlite'))
    for file_name in file_names:
        df = read_dataframe(os.path.join(cfg.input_folder, file_name))
        try:
            df.to_sql(name=file_name.split('.')[0], con=conn, if_exists='replace', index=False)
        except sqlite3.OperationalError as e:
            print(f"Error: {e}")
    conn.close()



