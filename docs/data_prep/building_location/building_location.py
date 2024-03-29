import pandas as pd
import copy

ID_ResidentialBuildingType = [1, 2, 3, 4, 5]
ID_TertiaryBuildingType = [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
ID_BuildingLocation = {
    8: 10,
    7: 11,
    6: 12,
    5: 13,
    4: 21,
    3: 22,
    2: 23,
    1: 30,
}


def get_region_code():
    df = pd.read_excel("./ID_Region.xlsx")
    region_ids = {}
    for index, row in df.iterrows():
        region_ids[row["id_region"]] = row["NUTS_Code"]
    return region_ids


def calc_building_location():
    RegionCode = get_region_code()
    df1 = pd.read_excel("./AssumptionZensus_BuildingLocation.xlsx")
    df2 = pd.read_excel("./OldScenario_Building_Location.xlsx")
    df2.insert(loc=3, column="id_building_type", value=0)
    building_location_list = []

    # residential buildings
    df2_r = df2.loc[df2["id_sector"] == 6]
    df2_r.loc[:, '1975':'2030'] = df2_r.loc[:, '1975':'2030'].div(df2_r['2010'], axis=0)
    for index, row in df2_r.iterrows():
        for id_residential_building_type in ID_ResidentialBuildingType:
            row_copy = copy.deepcopy(row)
            df1_filtered = df1.loc[
                (df1["region_code"] == RegionCode[row_copy["id_region"]]) &
                (df1["id_building_location"] == ID_BuildingLocation[row_copy["id_building_location"]]) &
                (df1["id_building_type"] == id_residential_building_type)
            ]
            if len(df1_filtered) > 0:
                row_copy['1975':'2030'] = row_copy['1975':'2030'] * df1_filtered.iloc[0]["2010"]
            else:
                row_copy['1975':'2030'] = row_copy['1975':'2030'] * 0
            d = row_copy.to_dict()
            d["id_building_type"] = id_residential_building_type
            d["unit"] = "building_number"
            building_location_list.append(d)

    # tertiary buildings
    df2_t = df2.loc[df2["id_sector"] == 3]
    for i2, row2 in df2_t.iterrows():
        for id_tertiary_building_type in ID_TertiaryBuildingType:
            d = row2.to_dict()
            d["id_building_type"] = id_tertiary_building_type
            building_location_list.append(d)

    df = pd.DataFrame(building_location_list)
    df.fillna(0, inplace=True)
    df.to_excel("./Scenario_Building_Location.xlsx", index=False)


if __name__ == "__main__":
    calc_building_location()
