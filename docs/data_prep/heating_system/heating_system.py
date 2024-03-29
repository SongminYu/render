import pandas as pd


def get_region_id():
    df = pd.read_excel("./ID_Region.xlsx")
    region_ids = {}
    for index, row in df.iterrows():
        region_ids[row["NUTS_Code"]] = row["id_region"]
    return region_ids


def calc_heating_system():
    regions = get_region_id()
    df = pd.read_excel("./AssumptionZensus_HeatingSystem.xlsx")
    heating_system_list = []
    for region_code, id_region in regions.items():
        for id_building_location in range(1, 8):
            for id_heating_system in range(1, 5):
                d = {
                    "id_scenario": 1,
                    "id_region": id_region,
                    "id_sector": 6,
                    "id_building_location": id_building_location,
                    "id_heating_system": id_heating_system,
                    "unit": "count"
                }
                df_filtered = df.loc[
                    (df["id_region"] == region_code) &
                    (df["id_building_location"] == id_building_location) &
                    (df["id_heating_system"] == id_heating_system)
                ]
                if len(df_filtered) > 0:
                    if id_heating_system == 2:
                        d["2010"] = df_filtered["2010"].sum()
                    elif id_heating_system == 1:
                        d["2010"] = df_filtered.iloc[0]["2010"]
                        # d["2010"] = df_filtered.iloc[0]["2010"] * 1.153846154
                    elif id_heating_system == 3:
                        d["2010"] = df_filtered.iloc[0]["2010"]
                        # d["2010"] = df_filtered.iloc[0]["2010"] * 0.826606691
                    elif id_heating_system == 4:
                        d["2010"] = df_filtered.iloc[0]["2010"]
                    else:
                        pass
                else:
                    d["2010"] = 0
                heating_system_list.append(d)
    pd.DataFrame(heating_system_list).to_excel("./Scenario_HeatingSystem.xlsx", index=False)


if __name__ == "__main__":
    calc_heating_system()
