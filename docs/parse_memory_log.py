from typing import List
import pandas as pd


def parse_memory_log(file_names: List[str]):
    for file_name in file_names:
        with open(f'{file_name}.txt', 'r') as file:
            lines = file.readlines()
            memory_usage = []
            for line in lines:
                memory = line.split()[-2]
                memory_usage.append(int(memory)/1024**2)
            pd.DataFrame({file_name: memory_usage}).to_excel(f"{file_name}.xlsx", index=False)


if __name__ == "__main__":
    parse_memory_log(file_names=[
        "lvm_memory_no_cache_103min_384scenarios",
        "lvm_memory_with_cache_62min_267scenarios",
    ])
