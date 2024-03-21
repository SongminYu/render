import pandas as pd

from models.render.render_dict import RenderDict
from models.render.scenario import RenderScenario
from models.render_building.building_key import BuildingKey


class BuildingScenario(RenderScenario):

    def setup(self):
        self.start_year = 0
        self.end_year = 0
        self.id_region = 0
        self.building_num_min = 0
        self.building_num_max = 0
        self.optimal_heating_behavior_prob = 0
        self.id_scenario_energy_price_wholesale = 0
        self.id_scenario_energy_price_tax_rate = 0
        self.id_scenario_energy_price_mark_up = 0
        self.id_scenario_energy_price_co2_emission = 0
        self.id_scenario_energy_emission_factor = 0

    def load_scenario_data(self):
        self.load_framework()
        self.load_ids()
        self.load_relations()
        self.load_params()
        self.load_profiles()
        self.load_scenarios()

    def load_ids(self):
        self.actions = self.load_id("ID_Action.xlsx")
        self.building_construction_periods = self.load_id("ID_Building_ConstructionPeriod.xlsx")
        self.building_heights = self.load_id("ID_Building_Height.xlsx")
        self.building_locations = self.load_id("ID_Building_Location.xlsx")
        self.building_types = self.load_id("ID_Building_Type.xlsx")
        self.building_components = self.load_id("ID_BuildingComponent.xlsx")
        self.building_component_options = self.load_id("ID_BuildingComponent_Option.xlsx")
        self.building_component_option_efficiency_classes = self.load_id("ID_BuildingComponent_Option_EfficiencyClass.xlsx")
        self.building_efficiency_classes = self.load_id("ID_Building_EfficiencyClass.xlsx")
        self.end_uses = self.load_id("ID_EndUse.xlsx")
        self.orientations = self.load_id("ID_Orientation.xlsx")
        self.unit_user_types = self.load_id("ID_UnitUserType.xlsx")
        self.heating_systems = self.load_id("ID_HeatingSystem.xlsx")
        self.heating_technologies = self.load_id("ID_HeatingTechnology.xlsx")
        self.cooling_technologies = self.load_id("ID_CoolingTechnology.xlsx")
        self.cooling_technology_efficiency_classes = self.load_id("ID_CoolingTechnology_EfficiencyClass.xlsx")
        self.ventilation_technologies = self.load_id("ID_VentilationTechnology.xlsx")
        self.ventilation_technology_efficiency_classes = self.load_id("ID_VentilationTechnology_EfficiencyClass.xlsx")

    def load_relations(self):
        self.r_building_component_option = self.load_relation("Relation_BuildingComponent_Option.xlsx")
        self.r_building_type_height = self.load_relation("Relation_BuildingType_Height.xlsx")
        self.r_subsector_building_type = self.load_relation("Relation_SubSector_BuildingType.xlsx")
        self.r_subsector_unit_user_type = self.load_relation("Relation_SubSector_UnitUserType.xlsx")
        self.r_sector_heating_system = self.load_relation("Relation_Sector_HeatingSystem.xlsx")
        self.r_heating_system_technology_main = self.load_relation("Relation_HeatingSystem_HeatingTechnologyMain.xlsx")
        self.r_heating_technology_energy_carrier = self.load_relation("Relation_HeatingTechnology_EnergyCarrier.xlsx")
        self.r_cooling_technology_efficiency_class = self.load_relation("Relation_CoolingTechnology_EfficiencyClass.xlsx")
        self.r_cooling_technology_energy_carrier = self.load_relation("Relation_CoolingTechnology_EnergyCarrier.xlsx")
        self.r_ventilation_technology_efficiency_class = self.load_relation("Relation_VentilationTechnology_EfficiencyClass.xlsx")
        self.r_ventilation_technology_energy_carrier = self.load_relation("Relation_VentilationTechnology_EnergyCarrier.xlsx")

    def load_params(self):
        # RenderDict
        self.p_building_component_efficiency = self.load_param("Parameter_BuildingComponent_EfficiencyCoefficient.xlsx")
        self.p_building_height_min = self.load_param("Parameter_Building_Height.xlsx", col="min")
        self.p_building_height_max = self.load_param("Parameter_Building_Height.xlsx", col="max")
        self.p_building_unit_number_min = self.load_param("Parameter_Building_UnitNumber.xlsx", col="min")
        self.p_building_unit_number_max = self.load_param("Parameter_Building_UnitNumber.xlsx", col="max")
        self.p_building_construction_year_min = self.load_param("Parameter_Building_ConstructionYear.xlsx", col="min")
        self.p_building_construction_year_max = self.load_param("Parameter_Building_ConstructionYear.xlsx", col="max")
        self.p_building_component_minimum_lifetime = self.load_param("Parameter_BuildingComponent_MinimumLifetime.xlsx")
        self.p_building_envelope_component_area_ref = self.load_param("Parameter_Building_Envelope_ComponentArea.xlsx", col='reference', region_level=0)
        self.p_building_envelope_component_area_ratio = self.load_param("Parameter_Building_Envelope_ComponentArea.xlsx", col='ratio', region_level=0)
        self.p_building_envelope_window_area_orientation = self.load_param("Parameter_Building_Envelope_WindowAreaOrientation.xlsx", region_level=0)
        self.p_building_rc_appliance_internal_gain = self.load_param("Parameter_Building_RC_ApplianceInternalGain.xlsx")
        self.p_unit_user_person_number = self.load_param("Parameter_UnitUser_PersonNumber.xlsx")
        self.p_unit_user_person_number_area_relevance = self.load_param("Parameter_UnitUser_PersonNumber_AreaRelevance.xlsx")
        self.p_unit_demand_profile_person_number_relevance = self.load_param("Parameter_UnitDemandProfile_PersonNumberRelevance.xlsx")
        self.p_set_temperature_occupied_min = self.load_param("Parameter_SetTemperature.xlsx", col="occupied_min")
        self.p_set_temperature_occupied_max = self.load_param("Parameter_SetTemperature.xlsx", col="occupied_max")
        self.p_set_temperature_empty_min = self.load_param("Parameter_SetTemperature.xlsx", col="empty_min")
        self.p_set_temperature_empty_max = self.load_param("Parameter_SetTemperature.xlsx", col="empty_max")
        self.p_heating_technology_lifetime_min = self.load_param("Parameter_HeatingTechnology_Lifetime.xlsx", col="min")
        self.p_heating_technology_lifetime_max = self.load_param("Parameter_HeatingTechnology_Lifetime.xlsx", col="max")
        self.p_heating_technology_second_contribution_space_heating = self.load_param("Parameter_HeatingTechnology_Second_Contribution.xlsx", col="space_heating")
        self.p_heating_technology_second_contribution_hot_water = self.load_param("Parameter_HeatingTechnology_Second_Contribution.xlsx", col="hot_water")
        self.p_cooling_technology_lifetime_min = self.load_param("Parameter_CoolingTechnology_Lifetime.xlsx", col="min")
        self.p_cooling_technology_lifetime_max = self.load_param("Parameter_CoolingTechnology_Lifetime.xlsx", col="max")
        self.p_cooling_technology_efficiency = self.load_param("Parameter_CoolingTechnology_EfficiencyCoefficient.xlsx")
        self.p_ventilation_technology_lifetime_min = self.load_param("Parameter_VentilationTechnology_Lifetime.xlsx", col="min")
        self.p_ventilation_technology_lifetime_max = self.load_param("Parameter_VentilationTechnology_Lifetime.xlsx", col="max")
        self.p_ventilation_technology_energy_intensity = self.load_param("Parameter_VentilationTechnology_EnergyIntensity.xlsx")
        # DataFrame
        self.p_building_component_lifetime = self.load_dataframe("Parameter_BuildingComponent_Lifetime.xlsx")
        self.p_building_efficiency_class_intensity = self.load_dataframe("Parameter_Building_EfficiencyClass_Intensity.xlsx")
        self.p_renovation_sync_probability = self.load_dataframe("Parameter_Renovation_SyncProbability.xlsx")

    def load_profiles(self):
        self.pr_building_occupancy = self.load_profile("Profile_BuildingOccupancy.xlsx")
        self.pr_appliance_electricity = self.load_profile("Profile_ApplianceElectricity.xlsx")
        self.pr_hot_water = self.load_profile("Profile_HotWater.xlsx")
        self.pr_weather_temperature = self.load_profile("Profile_WeatherTemperature.xlsx", region_level=0)
        self.pr_weather_radiation = self.load_profile("Profile_WeatherRadiation.xlsx", region_level=0)

    def load_scenarios(self):
        # RenderDict
        self.s_building = self.load_scenario("Scenario_Building.xlsx")
        self.s_building_construction_period = self.load_scenario("Scenario_Building_ConstructionPeriod.xlsx")
        self.s_building_height = self.load_scenario("Scenario_Building_Height.xlsx")
        self.s_building_location = self.load_scenario("Scenario_Building_Location.xlsx")
        self.s_building_unit_area = self.load_scenario("Scenario_Building_UnitArea.xlsx", region_level=0)
        self.s_building_component_availability = self.load_scenario("Scenario_BuildingComponent_Availability.xlsx", region_level=0, all_years=True)
        self.s_building_component_option = self.load_scenario("Scenario_BuildingComponent_Option.xlsx", region_level=0)
        self.s_unit_user = self.load_scenario("Scenario_UnitUser.xlsx", region_level=0)
        self.s_heating_system = self.load_scenario("Scenario_HeatingSystem.xlsx")
        self.s_heating_technology_efficiency = self.load_scenario("Scenario_HeatingTechnology_EfficiencyCoefficient.xlsx", all_years=True)
        self.s_heating_technology_main = self.load_scenario("Scenario_HeatingTechnology_Main.xlsx", region_level=0)
        self.s_cooling_penetration_rate = self.load_scenario("Scenario_Cooling_PenetrationRate.xlsx", region_level=0)
        self.s_cooling_technology_market_share = self.load_scenario("Scenario_CoolingTechnology_MarketShare.xlsx", region_level=0)
        self.s_cooling_technology_efficiency_class_market_share = self.load_scenario("Scenario_CoolingTechnology_EfficiencyClass_MarketShare.xlsx", region_level=0)
        self.s_cooling_technology_availability = self.load_scenario("Scenario_CoolingTechnology_Availability.xlsx", region_level=0)
        self.s_cooling_technology_investment_cost = self.load_scenario("Scenario_CoolingTechnology_EfficiencyClass_InvestmentCost.xlsx", region_level=0)
        self.s_ventilation_penetration_rate = self.load_scenario("Scenario_Ventilation_PenetrationRate.xlsx", region_level=0)
        self.s_ventilation_technology_market_share = self.load_scenario("Scenario_VentilationTechnology_MarketShare.xlsx", region_level=0)
        self.s_ventilation_technology_efficiency_class_market_share = self.load_scenario("Scenario_VentilationTechnology_EfficiencyClass_MarketShare.xlsx", region_level=0)
        self.s_ventilation_technology_availability = self.load_scenario("Scenario_VentilationTechnology_Availability.xlsx", region_level=0)
        self.s_ventilation_technology_investment_cost = self.load_scenario("Scenario_VentilationTechnology_EfficiencyClass_InvestmentCost.xlsx", region_level=0)

        # Dataframe
        self.s_heating_technology_second = self.load_dataframe("Scenario_HeatingTechnology_Second.xlsx")

    def setup_results_containers(self):
        self.building_profile = []
        self.building_stock = []
        self.building_num_model = RenderDict.create_empty_rdict(
            key_cols=[
                "id_scenario",
                "id_region",
                "id_sector",
                "id_subsector",
                "id_building_type"
            ],
        )
        self.building_num_total = RenderDict.create_empty_rdict(
            key_cols=[
                "id_scenario",
                "id_region",
                "id_sector",
                "id_subsector",
                "id_building_type"
            ],
        )
        self.renovation_action_building = RenderDict.create_empty_rdict(
            key_cols=[
                "id_scenario",
                "id_region",
                "id_sector",
                "id_subsector",
                "id_building_type",
                "id_building_construction_period",
                "year"
            ]
        )
        self.renovation_action_component = RenderDict.create_empty_rdict(
            key_cols=[
                "id_scenario",
                "id_region",
                "id_sector",
                "id_subsector",
                "id_building_type",
                "id_building_construction_period",
                "id_building_component",
                "year"
            ],
        )
        self.building_floor_area = RenderDict.create_empty_rdict(
            key_cols=[
                "id_scenario",
                "id_region",
                "id_sector",
                "id_subsector",
                "id_building_type",
                "id_building_construction_period",
                "year"
            ],
        )
        self.final_energy_demand = RenderDict.create_empty_rdict(
            key_cols=[
                "id_scenario",
                "id_region",
                "id_sector",
                "id_subsector",
                "id_building_type",
                "id_building_construction_period",
                "id_end_use",
                "id_energy_carrier",
                "year"
            ]
        )
        self.building_efficiency_class_count = RenderDict.create_empty_rdict(
            key_cols=[
                "id_scenario",
                "id_region",
                "id_sector",
                "id_subsector",
                "id_building_type",
                "id_building_construction_period",
                "id_building_efficiency_class",
                "year"
            ]
        )
        self.building_num_model = RenderDict.create_empty_rdict(key_cols=[
            "id_scenario",
            "id_region",
            "id_sector",
            "id_subsector",
            "id_building_type"
        ])
        self.building_num_total = RenderDict.create_empty_rdict(key_cols=[
            "id_scenario",
            "id_region",
            "id_sector",
            "id_subsector",
            "id_building_type"
        ])

    def setup_agent_params(self):
        df = self.load_dataframe("SimulatorCoverage.xlsx")
        df = df.loc[df["id_region"] == self.id_region]
        agent_params = []
        for index, row in df.iterrows():
            rkey = BuildingKey(id_scenario=self.id, year=self.start_year).from_dict(row.to_dict())
            real_building_num = int(self.s_building.get_item(rkey))
            if real_building_num <= self.building_num_min:
                agent_num = real_building_num
            else:
                agent_num = max(min(int(real_building_num * row["value"]), self.building_num_max), self.building_num_min)
            self.building_num_model.set_item(rkey, agent_num)
            self.building_num_total.set_item(rkey, real_building_num)
            for id_subsector_agent in range(1, agent_num + 1):
                agent_params.append({
                    "id_region": int(row["id_region"]),
                    "id_sector": int(row["id_sector"]),
                    "id_subsector": int(row["id_subsector"]),
                    "id_building_type": int(row["id_building_type"]),
                    "id_subsector_agent": id_subsector_agent
                })
        self.agent_params = pd.DataFrame(agent_params)

        def agent_num_analysis():
            # This function is used to calculate `agent_num` for memory demand analysis.
            # `self.agent_num` needs to be collected.
            self.agent_num = self.agent_params.groupby([
                "id_region", "id_sector", "id_subsector", "id_building_type"
            ], as_index=False)["id_subsector_agent"].count()
            self.agent_num.rename(columns={'id_subsector_agent': 'agent_num'}, inplace=True)
            self.agent_num["agent_min"] = self.building_num_min
            self.agent_num["agent_max"] = self.building_num_max
        agent_num_analysis()

    def get_building_num_scaling(self, rkey: "BuildingKey"):
        return self.building_num_total.get_item(rkey)/self.building_num_model.get_item(rkey)
