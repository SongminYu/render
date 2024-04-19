import pandas as pd

from models.render.render_dict import RenderDict
from models.render.scenario import RenderScenario
from models.render_building.building_key import BuildingKey
from utils.decorators import timer


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
        self.renovation_mandatory = 0
        self.heating_technology_mandatory = 0

    def setup_scenario_data(self):
        self.load_input_data()
        self.setup_agent_params()
        self.setup_cost_data()
        self.create_data_containers()

    """
    load input data
    """
    def load_input_data(self):
        self.load_framework()
        self.load_ids()
        self.load_relations()
        self.load_params()
        self.load_profiles()
        self.load_scenarios()

    def load_ids(self):
        self.building_actions = self.load_id("ID_Building_Action.xlsx")
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
        self.heating_system_actions = self.load_id("ID_HeatingSystem_Action.xlsx")
        self.heating_technologies = self.load_id("ID_HeatingTechnology.xlsx")
        self.radiators = self.load_id("ID_Radiator.xlsx")
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
        self.p_building_supply_temperature_space_heating = self.load_param("Parameter_Building_SupplyTemperature.xlsx", col="space_heating")
        self.p_building_supply_temperature_hot_water = self.load_param("Parameter_Building_SupplyTemperature.xlsx", col="hot_water")
        self.p_building_construction_year_min = self.load_param("Parameter_Building_ConstructionYear.xlsx", col="min")
        self.p_building_construction_year_max = self.load_param("Parameter_Building_ConstructionYear.xlsx", col="max")
        self.p_building_lifetime_min = self.load_param("Parameter_Building_Lifetime.xlsx", col="min", region_level=0)
        self.p_building_lifetime_max = self.load_param("Parameter_Building_Lifetime.xlsx", col="max", region_level=0)
        self.p_building_component_minimum_lifetime = self.load_param("Parameter_BuildingComponent_MinimumLifetime.xlsx")
        self.p_building_envelope_component_area_ref = self.load_param("Parameter_Building_Envelope_ComponentArea.xlsx", col='reference', region_level=0)
        self.p_building_envelope_component_area_ratio = self.load_param("Parameter_Building_Envelope_ComponentArea.xlsx", col='ratio', region_level=0)
        self.p_building_envelope_window_area_orientation = self.load_param("Parameter_Building_Envelope_WindowAreaOrientation.xlsx", region_level=0)
        self.p_building_rc_appliance_internal_gain = self.load_param("Parameter_Building_RC_ApplianceInternalGain.xlsx")
        self.p_radiator_lifetime_min = self.load_param("Parameter_Radiator_Lifetime.xlsx", col="min")
        self.p_radiator_lifetime_max = self.load_param("Parameter_Radiator_Lifetime.xlsx", col="max")
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
        self.p_heating_technology_supply_temperature_efficiency_adjustment = self.load_param("Parameter_HeatingTechnology_SupplyTemperatureEfficiencyAdjustment.xlsx")
        self.p_heating_technology_cost_multiplier_material = self.load_param("Parameter_HeatingTechnology_Cost.xlsx", region_level=0, col="multiplier_material_cost")
        self.p_heating_technology_cost_exponent_material = self.load_param("Parameter_HeatingTechnology_Cost.xlsx", region_level=0, col="exponent_material_cost")
        self.p_heating_technology_cost_share_multiplier_material = self.load_param("Parameter_HeatingTechnology_Cost.xlsx", region_level=0, col="multiplier_material_share")
        self.p_heating_technology_cost_share_exponent_material = self.load_param("Parameter_HeatingTechnology_Cost.xlsx", region_level=0, col="exponent_material_share")
        self.p_heating_technology_cost_learning_coefficient = self.load_param("Parameter_HeatingTechnology_Cost.xlsx", region_level=0, col="learning_coefficient")
        self.p_heating_technology_cost_multiplier_om = self.load_param("Parameter_HeatingTechnology_Cost.xlsx", region_level=0, col="multiplier_om_cost")
        self.p_heating_technology_cost_exponent_om = self.load_param("Parameter_HeatingTechnology_Cost.xlsx", region_level=0, col="exponent_om_cost")
        self.p_heating_technology_cost_criterion_small = self.load_param("Parameter_HeatingTechnology_Cost.xlsx", region_level=0, col="criterion_small")
        self.p_heating_technology_cost_pp_index = self.load_param("Parameter_HeatingTechnology_Cost.xlsx", region_level=0, col="pp_index")
        self.p_heating_technology_cost_wages_index = self.load_param("Parameter_HeatingTechnology_Cost.xlsx", region_level=0, col="wages_index")
        self.p_heating_technology_cost_payback_time = self.load_param("Parameter_HeatingTechnology_Cost.xlsx", region_level=0, col="payback_time")
        self.p_heating_technology_size_quantile = self.load_param("Parameter_HeatingTechnology_SizeQuantile.xlsx")
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
        self.s_building_component_option = self.load_scenario("Scenario_BuildingComponent_Option.xlsx", region_level=0)
        self.s_building_component_availability = self.load_scenario("Scenario_BuildingComponent_Availability.xlsx", region_level=0, all_years=True)
        self.s_building_component_cost_material = self.load_scenario("Scenario_BuildingComponent_Cost_Material.xlsx", region_level=0)
        self.s_building_component_cost_labor = self.load_scenario("Scenario_BuildingComponent_Cost_Labor.xlsx", region_level=0, all_years=True)
        self.s_building_component_cost_payback_time = self.load_scenario("Scenario_BuildingComponent_Cost_PaybackTime.xlsx", region_level=0)
        self.s_building_component_input_labor = self.load_scenario("Scenario_BuildingComponent_Input_Labor.xlsx", region_level=0, all_years=True)
        self.s_building_component_utility_power = self.load_scenario("Scenario_BuildingComponent_UtilityPower.xlsx", region_level=0)
        self.s_unit_user = self.load_scenario("Scenario_UnitUser.xlsx", region_level=0)
        self.s_heating_system = self.load_scenario("Scenario_HeatingSystem.xlsx")
        self.s_heating_technology_main = self.load_scenario("Scenario_HeatingTechnology_Main.xlsx", region_level=0)
        self.s_heating_technology_efficiency = self.load_scenario("Scenario_HeatingTechnology_EfficiencyCoefficient.xlsx", all_years=True)
        self.s_heating_technology_availability = self.load_scenario("Scenario_HeatingTechnology_Availability.xlsx", region_level=0)
        self.s_heating_technology_input_labor = self.load_scenario("Scenario_HeatingTechnology_Input_Labor.xlsx", region_level=0)
        self.s_heating_technology_utility_power = self.load_scenario("Scenario_HeatingTechnology_UtilityPower.xlsx", region_level=0)
        self.s_infrastructure_availability_district_heating = self.load_scenario("Scenario_Infrastructure_Availability_DistrictHeating.xlsx")
        self.s_infrastructure_availability_gas = self.load_scenario("Scenario_Infrastructure_Availability_Gas.xlsx")
        self.s_radiator = self.load_scenario("Scenario_Radiator.xlsx", region_level=0)
        self.s_radiator_availability = self.load_scenario("Scenario_Radiator_Availability.xlsx", region_level=0)
        self.s_radiator_cost_material = self.load_scenario("Scenario_Radiator_Cost_Material.xlsx", region_level=0)
        self.s_radiator_cost_labor = self.load_scenario("Scenario_Radiator_Cost_Labor.xlsx", region_level=0)
        self.s_radiator_cost_payback_time = self.load_scenario("Scenario_Radiator_Cost_PaybackTime.xlsx", region_level=0)
        self.s_radiator_input_labor = self.load_scenario("Scenario_Radiator_Input_Labor.xlsx", region_level=0)
        self.s_radiator_utility_power = self.load_scenario("Scenario_Radiator_UtilityPower.xlsx", region_level=0)
        self.s_cooling_penetration_rate = self.load_scenario("Scenario_Cooling_PenetrationRate.xlsx", region_level=0)
        self.s_cooling_technology_market_share = self.load_scenario("Scenario_CoolingTechnology_MarketShare.xlsx", region_level=0)
        self.s_cooling_technology_efficiency_class_market_share = self.load_scenario("Scenario_CoolingTechnology_EfficiencyClass_MarketShare.xlsx", region_level=0)
        self.s_cooling_technology_availability = self.load_scenario("Scenario_CoolingTechnology_Availability.xlsx", region_level=0)
        self.s_cooling_technology_cost_material = self.load_scenario("Scenario_CoolingTechnology_Cost_Material.xlsx", region_level=0)
        self.s_cooling_technology_cost_om = self.load_scenario("Scenario_CoolingTechnology_Cost_OM.xlsx", region_level=0)
        self.s_cooling_technology_cost_labor = self.load_scenario("Scenario_CoolingTechnology_Cost_Labor.xlsx", region_level=0)
        self.s_cooling_technology_cost_payback_time = self.load_scenario("Scenario_CoolingTechnology_Cost_PaybackTime.xlsx", region_level=0)
        self.s_cooling_technology_input_labor = self.load_scenario("Scenario_CoolingTechnology_Input_Labor.xlsx", region_level=0)
        self.s_cooling_technology_utility_power = self.load_scenario("Scenario_CoolingTechnology_UtilityPower.xlsx", region_level=0)
        self.s_ventilation_penetration_rate = self.load_scenario("Scenario_Ventilation_PenetrationRate.xlsx", region_level=0)
        self.s_ventilation_technology_market_share = self.load_scenario("Scenario_VentilationTechnology_MarketShare.xlsx", region_level=0)
        self.s_ventilation_technology_efficiency_class_market_share = self.load_scenario("Scenario_VentilationTechnology_EfficiencyClass_MarketShare.xlsx", region_level=0)
        self.s_ventilation_technology_availability = self.load_scenario("Scenario_VentilationTechnology_Availability.xlsx", region_level=0)
        self.s_ventilation_technology_cost_material = self.load_scenario("Scenario_VentilationTechnology_Cost_Material.xlsx", region_level=0)
        self.s_ventilation_technology_cost_om = self.load_scenario("Scenario_VentilationTechnology_Cost_OM.xlsx", region_level=0)
        self.s_ventilation_technology_cost_labor = self.load_scenario("Scenario_VentilationTechnology_Cost_Labor.xlsx", region_level=0)
        self.s_ventilation_technology_cost_payback_time = self.load_scenario("Scenario_VentilationTechnology_Cost_PaybackTime.xlsx", region_level=0)
        self.s_ventilation_technology_input_labor = self.load_scenario("Scenario_VentilationTechnology_Input_Labor.xlsx", region_level=0)
        self.s_ventilation_technology_utility_power = self.load_scenario("Scenario_VentilationTechnology_UtilityPower.xlsx", region_level=0)
        self.s_useful_energy_demand_index_appliance_electricity = self.load_scenario("Scenario_UsefulEnergyDemandIndex_ApplianceElectricity.xlsx", region_level=0)
        self.s_useful_energy_demand_index_hot_water = self.load_scenario("Scenario_UsefulEnergyDemandIndex_HotWater.xlsx", region_level=0)
        self.s_interest_rate = self.load_scenario("Scenario_InterestRate.xlsx", region_level=0)
        # Dataframe
        self.s_heating_technology_second = self.load_dataframe("Scenario_HeatingTechnology_Second.xlsx")

    """
    setup agent params
    """
    def setup_agent_params(self):
        building_num_key_cols = [
            "id_scenario",
            "id_region",
            "id_sector",
            "id_subsector",
            "id_building_type"
        ]
        self.building_num_model = RenderDict.create_empty_rdict(key_cols=building_num_key_cols)
        self.building_num_total = RenderDict.create_empty_rdict(key_cols=building_num_key_cols)
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

    """
    setup cost data
    """
    def setup_cost_data(self):
        self.setup_building_component_cost()
        self.setup_heating_technology_cost()
        # self.setup_radiator_cost()
        # self.setup_cooling_technology_cost()
        # self.setup_ventilation_technology_cost()

    @staticmethod
    def calc_capex(investment_cost: float, period_num: float, interest_rate: float):
        return investment_cost * interest_rate / (1 - (1 + interest_rate) ** (- period_num))

    @staticmethod
    def calc_opex(energy_intensity: float, energy_price: float, om_cost: float):
        return energy_intensity * energy_price + om_cost

    @timer()
    def setup_building_component_cost(self):

        self.building_component_capex = RenderDict.create_empty_rdict(key_cols=[
            "id_scenario",
            "id_region",
            "id_sector",
            "id_subsector",
            "id_building_type",
            "id_building_component",
            "id_building_component_option",
            "id_building_component_option_efficiency_class",
            "id_building_action",
            "year"
        ], region_level=0)  # unit: euro/m2 (component area)

        rkey = BuildingKey(id_scenario=self.id, id_region=int(list(str(self.id_region))[0]))
        for id_sector in self.sectors.keys():
            rkey.id_sector = id_sector
            for id_subsector in self.r_sector_subsector.get_item(rkey):
                rkey.id_subsector = id_subsector
                for id_building_type in self.r_subsector_building_type.get_item(rkey):
                    rkey.id_building_type = id_building_type
                    for id_building_component in self.building_components.keys():
                        rkey.id_building_component = id_building_component
                        for id_building_component_option in self.r_building_component_option.get_item(rkey):
                            rkey.id_building_component_option = id_building_component_option
                            for id_building_component_option_efficiency_class in self.building_component_option_efficiency_classes.keys():
                                rkey.id_building_component_option_efficiency_class = id_building_component_option_efficiency_class
                                for id_building_action in self.building_actions.keys():
                                    rkey.id_building_action = id_building_action
                                    for year in range(self.start_year, self.end_year + 1):
                                        rkey.year = year
                                        if self.s_building_component_availability.get_item(rkey):
                                            self.building_component_capex.set_item(rkey=rkey, value=self.calc_capex(
                                                investment_cost=self.s_building_component_cost_material.get_item(rkey) + self.s_building_component_input_labor.get_item(rkey) * self.s_building_component_cost_labor.get_item(rkey),
                                                period_num=self.s_building_component_cost_payback_time.get_item(rkey),
                                                interest_rate=self.s_interest_rate.get_item(rkey)
                                            ))

    @timer()
    def setup_heating_technology_cost(self):

        def calc_heating_technology_energy_cost():
            opex = 0
            for id_energy_carrier in self.r_heating_technology_energy_carrier.get_item(rkey):
                rkey.id_energy_carrier = id_energy_carrier
                energy_intensity = 1 / self.s_heating_technology_efficiency.get_item(rkey)
                energy_price = self.s_final_energy_carrier_price.get_item(rkey)
                opex += energy_intensity * energy_price
            return opex

        self.heating_technology_energy_cost = RenderDict.create_empty_rdict(key_cols=[
            "id_scenario",
            "id_region",
            "id_sector",
            "id_subsector",
            "id_heating_technology",
            "year"
        ], region_level=0)  # unit: euro/kWh

        rkey = BuildingKey(id_scenario=self.id, id_region=int(list(str(self.id_region))[0]))
        for id_sector in self.sectors.keys():
            rkey.id_sector = id_sector
            for id_subsector in self.r_sector_subsector.get_item(rkey):
                rkey.id_subsector = id_subsector
                for id_heating_technology in self.heating_technologies.keys():
                    rkey.id_heating_technology = id_heating_technology
                    for year in range(self.start_year, self.end_year + 1):
                        rkey.year = year
                        if self.s_heating_technology_availability.get_item(rkey):
                            self.heating_technology_energy_cost.set_item(rkey=rkey, value=calc_heating_technology_energy_cost())

    @timer()
    def setup_radiator_cost(self):

        self.radiator_capex = RenderDict.create_empty_rdict(key_cols=[
            "id_scenario",
            "id_region",
            "id_sector",
            "id_subsector",
            "id_building_type",
            "id_radiator",
            "id_building_action",
            "year"
        ], region_level=0)  # unit: euro/m2 (living area)

        rkey = BuildingKey(id_scenario=self.id, id_region=int(list(str(self.id_region))[0]))
        for id_sector in self.sectors.keys():
            rkey.id_sector = id_sector
            for id_subsector in self.r_sector_subsector.get_item(rkey):
                rkey.id_subsector = id_subsector
                for id_building_type in self.r_subsector_building_type.get_item(rkey):
                    rkey.id_building_type = id_building_type
                    for id_radiator in self.radiators.keys():
                        rkey.id_radiator = id_radiator
                        for id_building_action in self.building_actions.keys():
                            rkey.id_building_action = id_building_action
                            for year in range(self.start_year, self.end_year + 1):
                                rkey.year = year
                                if self.s_radiator_availability.get_item(rkey):
                                    self.radiator_capex.set_item(rkey=rkey, value=self.calc_capex(
                                        investment_cost=self.s_radiator_cost_material.get_item(rkey) + self.s_radiator_input_labor.get_item(rkey) * self.s_radiator_cost_labor.get_item(rkey),
                                        period_num=self.s_radiator_cost_payback_time.get_item(rkey),
                                        interest_rate=self.s_interest_rate.get_item(rkey)
                                    ))

    @timer()
    def setup_cooling_technology_cost(self):

        def get_energy_price():
            rkey.id_energy_carrier = self.r_cooling_technology_energy_carrier.get_item(rkey)[0]
            return self.s_final_energy_carrier_price.get_item(rkey)

        self.cooling_technology_capex = RenderDict.create_empty_rdict(key_cols=[
            "id_scenario",
            "id_region",
            "id_sector",
            "id_subsector",
            "id_cooling_technology",
            "id_cooling_technology_efficiency_class",
            "year"
        ], region_level=0)  # unit: euro/kW

        self.cooling_technology_opex = RenderDict.create_empty_rdict(key_cols=[
            "id_scenario",
            "id_region",
            "id_sector",
            "id_subsector",
            "id_cooling_technology",
            "id_cooling_technology_efficiency_class",
            "year"
        ], region_level=0)  # unit: euro/kWh

        rkey = BuildingKey(id_scenario=self.id, id_region=int(list(str(self.id_region))[0]))
        for id_sector in self.sectors.keys():
            rkey.id_sector = id_sector
            for id_subsector in self.r_sector_subsector.get_item(rkey):
                rkey.id_subsector = id_subsector
                for id_cooling_technology in self.cooling_technologies.keys():
                    rkey.id_cooling_technology = id_cooling_technology
                    for id_cooling_technology_efficiency_class in self.r_cooling_technology_efficiency_class.get_item(rkey):
                        rkey.id_cooling_technology_efficiency_class = id_cooling_technology_efficiency_class
                        for year in range(self.start_year, self.end_year + 1):
                            rkey.year = year
                            if self.s_cooling_technology_availability.get_item(rkey):
                                self.cooling_technology_capex.set_item(rkey=rkey, value=self.calc_capex(
                                    investment_cost=self.s_cooling_technology_cost_material.get_item(rkey) + self.s_cooling_technology_input_labor.get_item(rkey) * self.s_cooling_technology_cost_labor.get_item(rkey),
                                    period_num=self.s_cooling_technology_cost_payback_time.get_item(rkey),
                                    interest_rate=self.s_interest_rate.get_item(rkey)
                                ))
                                self.cooling_technology_opex.set_item(rkey=rkey, value=self.calc_opex(
                                    energy_intensity=1 / self.p_cooling_technology_efficiency.get_item(rkey),
                                    energy_price=get_energy_price(),
                                    om_cost=self.s_cooling_technology_cost_om.get_item(rkey)
                                ))

    @timer()
    def setup_ventilation_technology_cost(self):

        def get_energy_price():
            rkey.id_energy_carrier = self.r_ventilation_technology_energy_carrier.get_item(rkey)[0]
            return self.s_final_energy_carrier_price.get_item(rkey)

        self.ventilation_technology_capex = RenderDict.create_empty_rdict(key_cols=[
            "id_scenario",
            "id_region",
            "id_sector",
            "id_subsector",
            "id_ventilation_technology",
            "id_ventilation_technology_efficiency_class",
            "year"
        ], region_level=0)  # unit: euro/m2 (total living area)

        self.ventilation_technology_opex = RenderDict.create_empty_rdict(key_cols=[
            "id_scenario",
            "id_region",
            "id_sector",
            "id_subsector",
            "id_ventilation_technology",
            "id_ventilation_technology_efficiency_class",
            "year"
        ], region_level=0)  # unit: euro/m2-year (total living area)

        rkey = BuildingKey(id_scenario=self.id, id_region=int(list(str(self.id_region))[0]))
        for id_sector in self.sectors.keys():
            rkey.id_sector = id_sector
            for id_subsector in self.r_sector_subsector.get_item(rkey):
                rkey.id_subsector = id_subsector
                for id_ventilation_technology in self.ventilation_technologies.keys():
                    rkey.id_ventilation_technology = id_ventilation_technology
                    for id_ventilation_technology_efficiency_class in self.r_ventilation_technology_efficiency_class.get_item(rkey):
                        rkey.id_ventilation_technology_efficiency_class = id_ventilation_technology_efficiency_class
                        for year in range(self.start_year, self.end_year + 1):
                            rkey.year = year
                            if self.s_ventilation_technology_availability.get_item(rkey):
                                self.ventilation_technology_capex.set_item(rkey=rkey, value=self.calc_capex(
                                    investment_cost=self.s_ventilation_technology_cost_material.get_item(rkey) + self.s_ventilation_technology_input_labor.get_item(rkey) * self.s_ventilation_technology_cost_labor.get_item(rkey),
                                    period_num=self.s_ventilation_technology_cost_payback_time.get_item(rkey),
                                    interest_rate=self.s_interest_rate.get_item(rkey)
                                ))
                                self.ventilation_technology_opex.set_item(rkey=rkey, value=self.calc_opex(
                                    energy_intensity=self.p_ventilation_technology_energy_intensity.get_item(rkey),
                                    energy_price=get_energy_price(),
                                    om_cost=self.s_ventilation_technology_cost_om.get_item(rkey)
                                ))

    """
    create data containers
    """
    def create_data_containers(self):
        # initialization data containers
        self.heating_technology_main_initial_adoption = RenderDict.create_empty_rdict(key_cols=[
            "id_scenario",
            "id_region",
            "id_building_location",
            "id_heating_system",
            "id_heating_technology",
            "year"
        ])
        self.location_building_num = RenderDict.create_empty_rdict(key_cols=[
                "id_scenario",
                "id_region",
                "id_building_location",
                "year"
            ])
        self.location_building_num_heating_tech_district_heating = RenderDict.create_empty_rdict(key_cols=[
            "id_scenario",
            "id_region",
            "id_building_location",
            "year"
        ])
        self.location_building_num_heating_tech_gas = RenderDict.create_empty_rdict(key_cols=[
            "id_scenario",
            "id_region",
            "id_building_location",
            "year"
        ])
        # result data containers
        self.building_stock = []
        self.renovation_action_info = []
        self.heating_system_action_info = []
        self.renovation_action_building = RenderDict.create_empty_rdict(key_cols=[
            "id_scenario",
            "id_region",
            "id_sector",
            "id_subsector",
            "id_building_type",
            "id_building_construction_period",
            "year"
        ])
        self.renovation_action_component = RenderDict.create_empty_rdict(key_cols=[
            "id_scenario",
            "id_region",
            "id_sector",
            "id_subsector",
            "id_building_type",
            "id_building_construction_period",
            "id_building_component",
            "year"
        ])
        self.renovation_action_labor_demand = RenderDict.create_empty_rdict(key_cols=[
            "id_scenario",
            "id_region",
            "id_sector",
            "id_subsector",
            "id_building_type",
            "id_building_construction_period",
            "id_building_component",
            "year"
        ])

