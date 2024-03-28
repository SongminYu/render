from typing import List
import pandas as pd
import os


def parse_memory_log(file_names: List[str]):
    for file_name in file_names:
        with open(f'{file_name}.txt', 'r') as file:
            lines = file.readlines()
            memory_usage = []
            for line in lines:
                memory = line.split()[-2]
                memory_usage.append(int(memory)/1024**2)
            df = pd.DataFrame({file_name: memory_usage})
            df["unit"] = "GB"
            sheet_name = "_".join(file_name.split("_")[0:3])
            target_file = "memory_track.xlsx"
            if os.path.exists(target_file):
                with pd.ExcelWriter(target_file, engine='openpyxl', mode='a') as writer:
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
            else:
                df.to_excel(target_file, sheet_name=sheet_name, index=False)


if __name__ == "__main__":
    parse_memory_log(file_names=[
        "lvm_no_cache_103min_384scenarios",
        "lvm_with_cache_62min_267scenarios",
        "mac_with_cache_44min_401scenarios",
        "mac_no_cache_44min_401scenarios",
    ])
