import pandas as pd


def produce_household_type(df):
    df = df.groupby([
        "id_region",
        "id_unit_user_type",
    ])['2011'].sum().reset_index()
    df["id_sector"] = 6
    df.to_excel("output_Scenario_UnitUser.xlsx", index=False)


def produce_ownership(df):
    df = df.groupby([
        "id_region",
        "id_unit_user_type",
        "id_ownership",
    ])['2011'].sum().reset_index()
    df["id_sector"] = 6
    df.to_excel("output_Scenario_Ownership.xlsx", index=False)


def main():
    df = pd.read_excel("NUTS2_household.xlsx", sheet_name="DE_filtered_NUTS2")
    # produce_household_type(df)
    produce_ownership(df)


if __name__ == "__main__":
    main()
