import pandas as pd


def calc_heating_tech():
    df_bt = pd.read_excel("./AssumptionIWU_HeatingTechnology_BuildingType.xlsx")
    df_cp = pd.read_excel("./AssumptionIWU_HeatingTechnology_ConstructionPeriod.xlsx")
    aggregated_list = []
    for i_bt, row_bt in df_bt.iterrows():
        df = df_cp.loc[
            (df_cp["id_heating_system"] == row_bt["id_heating_system"]) &
            (df_cp["id_heating_technology"] == row_bt["id_heating_technology"])
        ]
        sum_2016 = df["2016"].sum()
        for i_cp, row_cp in df.iterrows():
            aggregated_list.append({
                "id_region": row_bt["id_region"],
                "id_building_type": row_bt["id_building_type"],
                "id_building_construction_period": row_cp["id_building_construction_period"],
                "id_heating_system": row_bt["id_heating_system"],
                "id_heating_technology": row_bt["id_heating_technology"],
                "unit": "fraction",
                "2016": row_bt["2016_adjusted"] * row_cp["2016"]/sum_2016
            })
    pd.DataFrame(aggregated_list).to_excel("./Scenario_HeatingTechnology_Main_update.xlsx", index=False)


if __name__ == "__main__":
    calc_heating_tech()
