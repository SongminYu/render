from typing import TYPE_CHECKING

import pandas as pd
from tqdm import tqdm

from models.render.data_collector import RenderDataCollector
from models.render_building.building_key import BuildingKey

if TYPE_CHECKING:
    from Melodie import AgentList
    from models.render_building.scenario import BuildingScenario
    from models.render_building.building import Building


class BuildingDataCollector(RenderDataCollector):
    scenario: "BuildingScenario"

    def setup(self):
        # define table names (move constants.py here)
        ...

    def export_scenario_cost(self):
        self.save_dataframe(df=self.scenario.building_component_capex.to_dataframe(), df_name=f"BuildingComponentCapex_R{self.scenario.id_region}")
        self.save_dataframe(df=self.scenario.heating_technology_capex.to_dataframe(), df_name=f"HeatingTechnologyCapex_R{self.scenario.id_region}")
        self.save_dataframe(df=self.scenario.heating_technology_opex.to_dataframe(), df_name=f"HeatingTechnologyOpex_R{self.scenario.id_region}")
        self.save_dataframe(df=self.scenario.radiator_capex.to_dataframe(), df_name=f"RadiatorCapex_R{self.scenario.id_region}")
        self.save_dataframe(df=self.scenario.cooling_technology_capex.to_dataframe(), df_name=f"CoolingTechnologyCapex_R{self.scenario.id_region}")
        self.save_dataframe(df=self.scenario.cooling_technology_opex.to_dataframe(), df_name=f"CoolingTechnologyOpex_R{self.scenario.id_region}")
        self.save_dataframe(df=self.scenario.ventilation_technology_capex.to_dataframe(), df_name=f"VentilationTechnologyCapex_R{self.scenario.id_region}")
        self.save_dataframe(df=self.scenario.ventilation_technology_opex.to_dataframe(), df_name=f"VentilationTechnologyOpex_R{self.scenario.id_region}")

    def export_heating_technology_main_initial_adoption(self):
        self.save_dataframe(
            df=self.scenario.heating_technology_main_initial_adoption.to_dataframe(),
            df_name=f"HeatingTechnologyMainInitialAdoption_R{self.scenario.id_region}"
        )

    def export_location_infrastructure(self):
        self.save_dataframe(
            df=self.scenario.location_building_num.to_dataframe(),
            df_name=f"LocationBuildingNum_R{self.scenario.id_region}"
        )
        self.save_dataframe(
            df=self.scenario.location_building_num_heating_tech_district_heating.to_dataframe(),
            df_name=f"LocationBuildingNum_DistrictHeating_R{self.scenario.id_region}"
        )
        self.save_dataframe(
            df=self.scenario.location_building_num_heating_tech_gas.to_dataframe(),
            df_name=f"LocationBuildingNum_GasBoiler_R{self.scenario.id_region}"
        )

    def collect_building_floor_area(self, buildings: "AgentList[Building]"):
        for building in buildings:
            self.scenario.building_floor_area.accumulate_item(
                building.rkey,
                building.unit_area * building.unit_number *
                self.scenario.get_building_num_scaling(building.rkey)
            )

    def export_building_floor_area(self):
        df = self.scenario.building_floor_area.to_dataframe()
        df.insert(self.get_unit_position(df), "unit", "m2")
        self.save_dataframe(df=df, df_name=f"floor_area_R{self.scenario.id_region}")

    def collect_building_profile(self, buildings: "AgentList[Building]"):
        for building in tqdm(buildings, desc="Collecting buildings_profile --> "):
            for profile_name in [
                "heating_demand_profile",
                "cooling_demand_profile",
                # "temp_mass_profile",
                # "temp_surface_profile",
                # "temp_air_profile"
            ]:
                building_dict = building.rkey.to_dict()
                building_dict["profile_name"] = profile_name
                for index, value in enumerate(building.__dict__[profile_name]):
                    building_dict[f'h{index + 1}'] = value
                self.scenario.building_profile.append(building_dict)

    def export_building_profile(self):
        def match_unit(profile_name: str):
            if profile_name.startswith("temp"):
                unit = "Celsius degree"
            else:
                unit = "W"
            return unit

        df = pd.DataFrame(self.scenario.building_profile)
        unit_values = df['profile_name'].apply(match_unit)
        unit_position = df.columns.get_loc("profile_name") + 1
        df.insert(unit_position, "unit", unit_values)
        self.save_dataframe(df=df, df_name=f"building_profile_R{self.scenario.id_region}")

    def collect_building_stock(self, buildings: "AgentList[Building]"):
        building_component_name = {
            1: "wall",
            2: "window",
            3: "roof",
            4: "basement"
        }
        for building in tqdm(buildings, desc="Collecting buildings_info --> "):
            building_dict = building.rkey.to_dict()
            building_dict["name"] = building.name
            # collect building parameters
            for key, value in building.__dict__.items():
                if value is not None:
                    if isinstance(value, int) or isinstance(value, float):
                        if key not in ["id", "id_energy_carrier", "id_heating_technology", "id_end_use"]:
                            building_dict[key] = value
            # collect building components
            for building_component in building.building_components:
                component_name = building_component_name[building_component.rkey.id_building_component]
                building_dict[f"{component_name}_id_component_option"] = building_component.rkey.id_building_component_option
                building_dict[f"{component_name}_id_efficiency_class"] = building_component.rkey.id_building_component_option_efficiency_class
                for component_key, component_value in building_component.__dict__.items():
                    if component_value is not None:
                        if isinstance(component_value, int) or isinstance(component_value, float):
                            building_dict[f"{component_name}_{component_key}"] = component_value
            # collect building number
            building_dict["building_number"] = self.scenario.get_building_num_scaling(building.rkey)
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

    def collect_building_final_energy_demand(self, buildings: "AgentList[Building]"):
        for building in buildings:
            rkey = building.rkey.make_copy()
            scaling = self.scenario.get_building_num_scaling(rkey)
            for id_end_use, end_use_energy_intensities in building.final_energy_demand.items():
                for id_energy_carrier, final_energy_demand in end_use_energy_intensities:
                    rkey.set_id({"id_end_use": id_end_use, "id_energy_carrier": id_energy_carrier})
                    self.scenario.final_energy_demand.accumulate_item(rkey, value=final_energy_demand * scaling)

    def export_building_final_energy_demand(self):
        df = self.scenario.final_energy_demand.to_dataframe()
        df.insert(self.get_unit_position(df), "unit", "kWh")
        self.save_dataframe(df=df, df_name=f"final_energy_demand_R{self.scenario.id_region}")

    def collect_building_efficiency_class_count(self, buildings: "AgentList[Building]"):
        for building in buildings:
            self.scenario.building_efficiency_class_count.accumulate_item(
                rkey=building.rkey,
                value=self.scenario.get_building_num_scaling(building.rkey)
            )

    def export_building_efficiency_class_count(self):
        df = self.scenario.building_efficiency_class_count.to_dataframe()
        df.insert(self.get_unit_position(df), "unit", "count")
        self.save_dataframe(df=df, df_name=f"building_efficiency_class_count_R{self.scenario.id_region}")

    def export_renovation_rate(self):

        def export_to_csv(df: pd.DataFrame, file_name: str):
            df.insert(self.get_unit_position(df), "unit", "count")
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
        # export_to_csv(df=building_plain, file_name="renovation_rate_building_plain")

        component_plain = create_renovation_rate_building_component_plain()
        # export_to_csv(df=component_plain, file_name="renovation_rate_component_plain")

        component_processed = create_renovation_rate_building_component_processed(component_plain)
        export_to_csv(df=component_processed, file_name="renovation_rate_component")

        building_weighted = create_renovation_rate_building_weighted(component_processed)
        export_to_csv(df=building_weighted, file_name="renovation_rate_building")

    @staticmethod
    def get_unit_position(df: pd.DataFrame):
        return max([i for i, col in enumerate(df.columns) if col.startswith("id_")]) + 1
