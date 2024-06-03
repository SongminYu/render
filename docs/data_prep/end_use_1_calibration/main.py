from typing import List, Dict
import pandas as pd
import os


def gen_population():
    df = pd.read_csv(os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "building_stock_summary_nuts0.csv"
    ))
    df = df.groupby([
        "id_scenario",
        "id_region",
        "id_sector",
        "id_subsector",
        "year"
    ]).agg({"population": "sum"}).reset_index()
    df.to_csv("population.csv", index=False)


def _convert_dict(df: pd.DataFrame, keys: List[str], value_name: str = "value") -> Dict[tuple, float]:
    d = {}
    for _, row in df.iterrows():
        d[tuple([row[key] for key in keys])] = row[value_name]
    return d


def gen_person_average_demand():
    fed_df = pd.read_excel(os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "end_use_1_demand.xlsx"
    ))
    fed = _convert_dict(
        df=fed_df,
        keys=["id_subsector", "id_energy_carrier", "year"]
    )
    pop = _convert_dict(
        df=pd.read_csv(os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "population.csv"
        )),
        keys=["id_subsector", "year"],
        value_name="population"
    )
    l = []
    for _, row in fed_df.iterrows():
        d = row.to_dict()
        d["value"] = fed[(d["id_subsector"], d["id_energy_carrier"], d["year"])] / pop[(d["id_subsector"], d["year"])]
        l.append(d)
    df = pd.DataFrame(l)
    df["unit"] = "kWh/person"
    df.to_csv("demand_per_person.csv", index=False)


def pivot_demand_per_person():
    df = pd.read_csv("demand_per_person.csv")
    pivot_df = df.pivot_table(
        index=['id_region', 'id_sector', 'id_subsector', 'id_end_use', 'id_energy_carrier', 'unit'],
        columns='year',
        values='value'
    ).reset_index()
    pivot_df[2051] = pivot_df[2050] + (pivot_df[2050] - pivot_df[2049])
    pivot_df[2052] = pivot_df[2051] + (pivot_df[2051] - pivot_df[2050])
    pivot_df.to_csv("demand_per_person_pivot.csv", index=False)


if __name__ == "__main__":
    # gen_population()
    # gen_person_average_demand()
    pivot_demand_per_person()

