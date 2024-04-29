from typing import TYPE_CHECKING, Optional

import pandas as pd

from models.render.data_collector import RenderDataCollector
from models.render_building.building_key import BuildingKey

if TYPE_CHECKING:
    from Melodie import AgentList
    from models.render.render_dict import RenderDict
    from models.render_building.scenario import BuildingScenario
    from models.render_building.building import Building


class BuildingDataCollector(RenderDataCollector):
    scenario: "BuildingScenario"

    def export(self):
        self.export_building_stock()
        self.export_renovation_action_info()
        self.export_heating_system_action_info()

    def export_rdict(self, rdict: "RenderDict", df_name: str, unit: Optional[str] = None):
        df = rdict.to_dataframe()
        if unit is not None:
            unit_position = max([i for i, col in enumerate(df.columns) if col.startswith("id_")]) + 1
            df.insert(unit_position, "unit", unit)
        self.save_dataframe(df=df, df_name=df_name)

    """
    Initialization data
    """
    def export_initialization_data(self):
        # self.export_rdict(rdict=self.scenario.s_final_energy_carrier_price, df_name=f"FinalEnergyPrice_R{self.scenario.id_region}", unit="euro/kWh")
        # self.export_rdict(rdict=self.scenario.heating_technology_main_initial_adoption, df_name=f"HeatingTechnologyMainInitialAdoption_R{self.scenario.id_region}", unit="count")
        # self.export_rdict(rdict=self.scenario.building_component_capex, df_name=f"BuildingComponentCapex_R{self.scenario.id_region}", unit="euro/m2")
        # self.export_rdict(rdict=self.scenario.heating_technology_energy_cost, df_name=f"HeatingTechnologyEnergyCost_R{self.scenario.id_region}", unit="euro/kWh")
        # self.export_rdict(rdict=self.scenario.radiator_capex, df_name=f"RadiatorCapex_R{self.scenario.id_region}", unit="euro/m2")
        # self.export_rdict(rdict=self.scenario.cooling_technology_capex, df_name=f"CoolingTechnologyCapex_R{self.scenario.id_region}", unit="euro/kW")
        # self.export_rdict(rdict=self.scenario.cooling_technology_opex, df_name=f"CoolingTechnologyOpex_R{self.scenario.id_region}", unit="euro/kWh")
        # self.export_rdict(rdict=self.scenario.ventilation_technology_capex, df_name=f"VentilationTechnologyCapex_R{self.scenario.id_region}", unit="euro/m2")
        # self.export_rdict(rdict=self.scenario.ventilation_technology_opex, df_name=f"VentilationTechnologyOpex_R{self.scenario.id_region}", unit="euro/m2")
        # self.export_rdict(rdict=self.scenario.building_num_model, df_name=f"BuildingNumModel_R{self.scenario.id_region}", unit="count")
        # self.export_rdict(rdict=self.scenario.building_num_total, df_name=f"BuildingNumTotal_R{self.scenario.id_region}", unit="count")
        # self.export_historical_renovation_rate()
        ...

    def export_historical_renovation_rate(self):

        def export_to_csv(df: pd.DataFrame, file_name: str):
            unit_position = max([i for i, col in enumerate(df.columns) if col.startswith("id_")]) + 1
            df.insert(unit_position, "unit", "count")
            self.save_dataframe(df=df, df_name=f"{file_name}_R{self.scenario.id_region}")

        def get_construction_period_percentage(row_rkey: "BuildingKey"):
            df = self.scenario.load_dataframe("Scenario_Building_ConstructionPeriod.xlsx")
            df1 = df.loc[
                (df["id_region"] == row_rkey.id_region) &
                (df["id_sector"] == row_rkey.id_sector) &
                (df["id_building_type"] == row_rkey.id_building_type)
            ]
            df2 = df1.loc[df1["id_building_construction_period"] == row_rkey.id_building_construction_period]
            return df2.iloc[0]["2019"] / df1["2019"].sum()

        def create_renovation_rate_building_plain():
            l = []
            for _, row in renovation_action_building.iterrows():
                rkey = BuildingKey().from_dict(row.to_dict())
                d = row.to_dict()
                d["num_building_renovation_model"] = d.pop("value")
                d["num_building_model_construction_period"] = self.scenario.building_num_model.get_item(rkey) * get_construction_period_percentage(row_rkey=rkey)
                d["building_renovation_rate_construction_period"] = d["num_building_renovation_model"] / d["num_building_model_construction_period"]
                d["num_building_model_type"] = self.scenario.building_num_model.get_item(rkey)
                d["building_renovation_rate_type"] = d["num_building_renovation_model"] / d["num_building_model_type"]
                l.append(d)
            return pd.DataFrame(l)

        def create_renovation_rate_building_component_plain():
            l = []
            for _, row in renovation_action_component.iterrows():
                rkey = BuildingKey().from_dict(row.to_dict())
                d = row.to_dict()
                d["num_component_renovation_model"] = d.pop("value")
                d["num_building_model_construction_period"] = self.scenario.building_num_model.get_item(rkey) * get_construction_period_percentage(row_rkey=rkey)
                d["component_renovation_rate_construction_period"] = d["num_component_renovation_model"] / d["num_building_model_construction_period"]
                d["num_building_model_type"] = self.scenario.building_num_model.get_item(rkey)
                d["component_renovation_rate_type"] = d["num_component_renovation_model"] / d["num_building_model_type"]
                l.append(d)
            return pd.DataFrame(l)

        def create_renovation_rate_building_component_processed(df: pd.DataFrame):
            df_dropped = df.drop(columns=[
                "num_building_model_construction_period",
                "component_renovation_rate_construction_period",
                "num_building_model_type",
                "component_renovation_rate_type"
            ])
            grouped_df = df_dropped.groupby([
                "id_scenario",
                "id_region",
                "id_sector",
                "id_subsector",
                "id_building_component",
                "year"
            ])['num_component_renovation_model'].sum().reset_index()

            def get_num_building_types(row):
                num_building_types = 0
                rkey = BuildingKey().from_dict(row.to_dict())
                for id_building_type in self.scenario.r_subsector_building_type.get_item(rkey):
                    rkey.id_building_type = id_building_type
                    num_building_types += self.scenario.building_num_model.get_item(rkey)
                return num_building_types

            grouped_df["num_building_types"] = grouped_df.apply(get_num_building_types, axis=1)
            grouped_df = grouped_df.assign(
                renovation_rate=grouped_df["num_component_renovation_model"] / grouped_df["num_building_types"]
            )
            return grouped_df

        def create_renovation_rate_building_weighted(df: pd.DataFrame):
            df_dropped = df.drop(columns=[
                "num_component_renovation_model",
                "num_building_types"
            ])

            pivot_df = df_dropped.pivot_table(
                index=[
                    "id_scenario",
                    "id_region",
                    "id_sector",
                    "id_subsector",
                    "year",
                ],
                columns='id_building_component',
                values='renovation_rate',
                aggfunc='mean'
            ).reset_index()

            component_names = {
                1: "wall",
                2: "window",
                3: "roof",
                4: "basement"
            }
            for col in pivot_df.columns:
                if col in [1, 2, 3, 4]:
                    pivot_df.rename(columns={col: component_names[col]}, inplace=True)
                    pivot_df[component_names[col]].fillna(0, inplace=True)

            def weighted_renovation_rate(row):
                return row["wall"] * 0.4 + row["window"] * 0.09 + row["roof"] * 0.28 + row["basement"] * 0.23

            pivot_df["building_weighted_average_renovation_rate"] = pivot_df.apply(weighted_renovation_rate, axis=1)

            return pivot_df

        renovation_action_building = self.scenario.renovation_action_building.to_dataframe()
        renovation_action_component = self.scenario.renovation_action_component.to_dataframe()

        building_plain = create_renovation_rate_building_plain()
        # export_to_csv(df=building_plain, file_name="historical_renovation_rate_building_plain")

        component_plain = create_renovation_rate_building_component_plain()
        # export_to_csv(df=component_plain, file_name="historical_renovation_rate_component_plain")

        component_processed = create_renovation_rate_building_component_processed(component_plain)
        export_to_csv(df=component_processed, file_name="historical_renovation_rate_component")

        building_weighted = create_renovation_rate_building_weighted(component_processed)
        export_to_csv(df=building_weighted, file_name="historical_renovation_rate_building")

    """
    Results
    """
    # Building stock
    def collect_building_stock(self, buildings: "AgentList[Building]"):
        for building in buildings:
            building_dict = building.rkey.to_dict()
            building_dict["exists"] = building.exists
            # collect building parameters
            for key, value in building.__dict__.items():
                if value is not None:
                    if isinstance(value, int) or isinstance(value, float):
                        if key not in ["id", "id_energy_carrier", "id_heating_technology", "id_end_use", "exists"]:
                            building_dict[key] = value
            # collect building components
            for component_name, building_component in building.building_components.items():
                building_dict[f"{component_name}_id_component_option"] = building_component.rkey.id_building_component_option
                building_dict[f"{component_name}_id_efficiency_class"] = building_component.rkey.id_building_component_option_efficiency_class
                for component_key, component_value in building_component.__dict__.items():
                    if component_value is not None:
                        if isinstance(component_value, int) or isinstance(component_value, float):
                            building_dict[f"{component_name}_{component_key}"] = component_value
            # collect building number
            building_dict["building_number"] = (self.scenario.building_num_total.get_item(building.rkey) /
                                                self.scenario.building_num_model.get_item(building.rkey))
            # collect building heating system
            building_dict["id_heating_system"] = building.heating_system.rkey.id_heating_system
            building_dict["district_heating_available"] = building.heating_system.district_heating_available
            building_dict["gas_available"] = building.heating_system.gas_available
            for ht_name, heating_technology in [
                ["main", building.heating_system.heating_technology_main],
                ["second", building.heating_system.heating_technology_second],
            ]:
                if heating_technology is not None:
                    building_dict[f"heating_system_{ht_name}_id_heating_technology"] = heating_technology.rkey.id_heating_technology
                    building_dict[f"heating_system_{ht_name}_supply_temperature_space_heating"] = heating_technology.supply_temperature_space_heating
                    building_dict[f"heating_system_{ht_name}_supply_temperature_hot_water"] = heating_technology.supply_temperature_hot_water
                    building_dict[f"heating_system_{ht_name}_installation_year"] = heating_technology.installation_year
                    building_dict[f"heating_system_{ht_name}_next_replace_year"] = heating_technology.next_replace_year
                    building_dict[f"heating_system_{ht_name}_space_heating_contribution"] = heating_technology.space_heating_contribution
                    building_dict[f"heating_system_{ht_name}_hot_water_contribution"] = heating_technology.hot_water_contribution
                    for end_use, end_use_useful_demand, energy_intensities in [
                        ["space_heating", building.heating_demand, heating_technology.space_heating_energy_intensities],
                        ["hot_water", building.hot_water_demand, heating_technology.hot_water_energy_intensities],
                    ]:
                        count = 1
                        for energy_intensity in energy_intensities:
                            building_dict[f"heating_system_{ht_name}_{end_use}_energy_carrier_{count}_id_energy_carrier"] = energy_intensity.id_energy_carrier
                            building_dict[f"heating_system_{ht_name}_{end_use}_energy_carrier_{count}_energy_intensity"] = energy_intensity.value
                            building_dict[f"heating_system_{ht_name}_{end_use}_energy_carrier_{count}_energy_consumption"] = energy_intensity.value * end_use_useful_demand
                            count += 1
                        if len(energy_intensities) == 1:
                            building_dict[f"heating_system_{ht_name}_{end_use}_energy_carrier_2_id_energy_carrier"] = None
                            building_dict[f"heating_system_{ht_name}_{end_use}_energy_carrier_2_energy_intensity"] = None
                            building_dict[f"heating_system_{ht_name}_{end_use}_energy_carrier_2_energy_consumption"] = None
                else:
                    building_dict[f"heating_system_{ht_name}_id_heating_technology"] = None
                    building_dict[f"heating_system_{ht_name}_supply_temperature_space_heating"] = None
                    building_dict[f"heating_system_{ht_name}_supply_temperature_hot_water"] = None
                    building_dict[f"heating_system_{ht_name}_installation_year"] = None
                    building_dict[f"heating_system_{ht_name}_next_replace_year"] = None
                    building_dict[f"heating_system_{ht_name}_space_heating_contribution"] = None
                    building_dict[f"heating_system_{ht_name}_hot_water_contribution"] = None
                    for end_use in ["space_heating", "hot_water"]:
                        for count in [1, 2]:
                            building_dict[f"heating_system_{ht_name}_{end_use}_energy_carrier_{count}_id_energy_carrier"] = None
                            building_dict[f"heating_system_{ht_name}_{end_use}_energy_carrier_{count}_energy_intensity"] = None
                            building_dict[f"heating_system_{ht_name}_{end_use}_energy_carrier_{count}_energy_consumption"] = None
            # collect building cooling system
            building_dict[f"cooling_system_id_cooling_technology"] = building.cooling_system.rkey.id_cooling_technology
            building_dict[f"cooling_system_installation_year"] = building.cooling_system.installation_year
            building_dict[f"cooling_system_next_replace_year"] = building.cooling_system.next_replace_year
            if building.cooling_system.energy_intensity is not None:
                building_dict[f"cooling_system_id_energy_carrier"] = building.cooling_system.energy_intensity.id_energy_carrier
                building_dict[f"cooling_system_energy_intensity"] = building.cooling_system.energy_intensity.value
                building_dict[f"cooling_system_energy_consumption"] = building.cooling_system.energy_intensity.value * building.cooling_demand
            else:
                building_dict[f"cooling_system_id_energy_carrier"] = None
                building_dict[f"cooling_system_energy_intensity"] = None
                building_dict[f"cooling_system_energy_consumption"] = None
            # collection building ventilation system
            building_dict[f"ventilation_system_id_ventilation_technology"] = building.ventilation_system.rkey.id_ventilation_technology
            building_dict[f"ventilation_system_installation_year"] = building.ventilation_system.installation_year
            building_dict[f"ventilation_system_next_replace_year"] = building.ventilation_system.next_replace_year
            if building.ventilation_system.energy_intensity is not None:
                building_dict[f"ventilation_system_id_energy_carrier"] = building.ventilation_system.energy_intensity.id_energy_carrier
                building_dict[f"ventilation_system_energy_intensity"] = building.ventilation_system.energy_intensity.value
                building_dict[f"ventilation_system_energy_consumption"] = building.ventilation_system.energy_intensity.value * building.total_living_area
            else:
                building_dict[f"ventilation_system_id_energy_carrier"] = None
                building_dict[f"ventilation_system_energy_intensity"] = None
                building_dict[f"ventilation_system_energy_consumption"] = None
            # save the building dict
            self.scenario.building_stock.append(building_dict)

    def export_building_stock(self):
        self.save_dataframe(df=pd.DataFrame(self.scenario.building_stock), df_name=f"building_stock_R{self.scenario.id_region}")

    # Renovation action info
    def export_renovation_action_info(self):
        self.save_dataframe(df=pd.DataFrame(self.scenario.renovation_action_info), df_name=f"renovation_action_info_R{self.scenario.id_region}")

    # Heating system action info
    def export_heating_system_action_info(self):
        self.save_dataframe(df=pd.DataFrame(self.scenario.heating_system_action_info), df_name=f"heating_system_action_info_R{self.scenario.id_region}")
