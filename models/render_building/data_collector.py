import os
from typing import TYPE_CHECKING, Optional

import pandas as pd

from models.render.data_collector import RenderDataCollector

if TYPE_CHECKING:
    from Melodie import AgentList
    from models.render.render_dict import RenderDict
    from models.render_building.scenario import BuildingScenario
    from models.render_building.building import Building


class BuildingDataCollector(RenderDataCollector):
    scenario: "BuildingScenario"

    """
    Export initialization data
    """

    def export_initialization_data(self):
        self.export_rdict(rdict=self.scenario.s_final_energy_carrier_price, df_name=f"final_energy_price", unit="euro/kWh", sub_folder="init_data", if_exists="pass")
        self.export_rdict(rdict=self.scenario.building_component_capex, df_name=f"building_component_capex", unit="euro/m2", sub_folder="init_data", if_exists="pass")
        self.export_rdict(rdict=self.scenario.heating_technology_energy_cost, df_name=f"heating_technology_energy_cost", unit="euro/kWh", sub_folder="init_data", if_exists="pass")
        self.export_rdict(rdict=self.scenario.radiator_capex, df_name=f"radiator_capex", unit="euro/m2", sub_folder="init_data", if_exists="pass")
        self.export_rdict(rdict=self.scenario.cooling_technology_capex, df_name=f"cooling_technology_capex", unit="euro/kW", sub_folder="init_data", if_exists="pass")
        self.export_rdict(rdict=self.scenario.cooling_technology_opex, df_name=f"cooling_technology_opex", unit="euro/kWh", sub_folder="init_data", if_exists="pass")
        self.export_rdict(rdict=self.scenario.ventilation_technology_capex, df_name=f"ventilation_technology_capex", unit="euro/m2", sub_folder="init_data", if_exists="pass")
        self.export_rdict(rdict=self.scenario.ventilation_technology_opex, df_name=f"ventilation_technology_opex", unit="euro/m2", sub_folder="init_data", if_exists="pass")
        self.export_rdict(rdict=self.scenario.heating_technology_main_initial_adoption, df_name=f"heating_tech_adoption", unit="count", sub_folder="init_data")
        self.export_rdict(rdict=self.scenario.location_building_num, df_name=f"infrastructure_building_num", unit="count", sub_folder="init_data")
        self.export_rdict(rdict=self.scenario.location_building_num_heating_tech_district_heating, df_name=f"infrastructure_building_num_dh_adoption", unit="count", sub_folder="init_data")
        self.export_rdict(rdict=self.scenario.location_building_num_heating_tech_gas, df_name=f"infrastructure_building_num_gas_adoption", unit="count", sub_folder="init_data")
        self.export_rdict(rdict=self.scenario.location_building_num_heating_tech_hydrogen, df_name=f"infrastructure_building_num_hydrogen_adoption", unit="count", sub_folder="init_data")

    """
    Collect building stock data
    """

    def collect_building_stock(self, buildings: "AgentList[Building]"):
        building_stock = []
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
            # collect building heating system
            building_dict["id_heating_system"] = building.heating_system.rkey.id_heating_system
            building_dict["district_heating_available"] = building.heating_system.district_heating_available
            building_dict["gas_available"] = building.heating_system.gas_available
            building_dict["hydrogen_available"] = building.heating_system.hydrogen_available
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
            building_stock.append(building_dict)
        self.save_dataframe(df=pd.DataFrame(building_stock), df_name=f"building_stock_R{self.scenario.id_region}")

    """
    Export result data
    """

    def export_result_data(self):
        self.export_dwelling_number()
        self.export_household_number()
        self.export_renovation_action_info()
        self.export_heating_system_action_info()

    # Dwelling number
    def export_dwelling_number(self):
        self.export_rdict(rdict=self.scenario.dwelling_number, df_name=f"dwelling_number", unit="count")

    # Household number
    def export_household_number(self):
        self.export_rdict(rdict=self.scenario.household_number, df_name=f"household_number", unit="count")

    # Renovation action info
    def export_renovation_action_info(self):
        self.save_dataframe(df=pd.DataFrame(self.scenario.renovation_action_info), df_name=f"renovation_actions")

    # Heating system action info
    def export_heating_system_action_info(self):
        self.save_dataframe(df=pd.DataFrame(self.scenario.heating_system_action_info), df_name=f"heating_system_actions")

    """
    Export functions
    """

    def export_rdict(
            self,
            rdict: "RenderDict",
            df_name: str,
            if_exists="append",
            unit: Optional[str] = None,
            sub_folder: Optional[str] = None
    ):
        df = rdict.to_dataframe()
        if len(df) > 0:
            if unit is not None:
                unit_position = max([i for i, col in enumerate(df.columns) if col.startswith("id_")]) + 1
                df.insert(unit_position, "unit", unit)
            self.save_dataframe(df=df, df_name=df_name, if_exists=if_exists, sub_folder=sub_folder)

    def save_dataframe(
            self,
            df: pd.DataFrame,
            df_name: str,
            if_exists: str = "append",
            sub_folder: Optional[str] = None
    ):
        if len(df) > 0:
            if sub_folder is None:
                path = os.path.join(self.config.output_folder, f"{df_name}.csv")
            else:
                os.makedirs(os.path.join(self.config.output_folder, sub_folder), exist_ok=True)
                path = os.path.join(self.config.output_folder, sub_folder, f"{df_name}.csv")
            if os.path.isfile(path):
                if if_exists == "append":
                    df.to_csv(path, mode="a", header=False, index=False)
                elif if_exists == "replace":
                    df.to_csv(path, index=False)
                elif if_exists == "pass":
                    pass
                else:
                    raise NotImplementedError(
                        f"if_exists = {if_exists} --> not implemented."
                    )
            else:
                df.to_csv(path, index=False)
