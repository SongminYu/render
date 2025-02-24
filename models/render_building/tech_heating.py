import random
from typing import Optional, List
from typing import TYPE_CHECKING

import numpy as np

from models.render_building import cons
from models.render_building.building_key import BuildingKey
from models.render_building.tech import EnergyIntensity
from utils.funcs import dict_sample, dict_normalize, dict_utility_sample

if TYPE_CHECKING:
    from models.render_building.scenario import BuildingScenario


class HeatingSystem:

    def __init__(self, rkey: "BuildingKey", scenario: "BuildingScenario"):
        self.rkey = rkey
        self.scenario = scenario
        self.heating_technology_main: Optional["HeatingTechnology"] = None
        self.heating_technology_second: Optional["HeatingTechnology"] = None
        self.district_heating_available = False
        self.gas_available = False
        self.hydrogen_available = False
        self.heating_technologies = []

    def init_system_type(self):
        self.rkey.init_dimension(
            dimension_name="id_heating_system",
            dimension_ids=self.scenario.r_sector_heating_system.get_item(self.rkey),
            rdict=self.scenario.s_heating_system
        )

    def init_heating_technology_main(self, building_age: int):

        def mark_info():
            self.scenario.location_building_num.accumulate_item(rkey=self.rkey, value=1)
            self.scenario.heating_technology_main_initial_adoption.accumulate_item(rkey=self.heating_technology_main.rkey, value=1)
            if self.heating_technology_main.rkey.id_heating_technology in cons.DISTRICT_HEATING_TECHNOLOGIES:
                self.district_heating_available = True
                self.scenario.location_building_num_heating_tech_district_heating.accumulate_item(rkey=self.rkey, value=1)
            elif self.heating_technology_main.rkey.id_heating_technology in cons.GAS_HEATING_TECHNOLOGIES:
                self.gas_available = True
                self.scenario.location_building_num_heating_tech_gas.accumulate_item(rkey=self.rkey, value=1)
            elif self.heating_technology_main.rkey.id_heating_technology in cons.HYDROGEN_HEATING_TECHNOLOGIES:
                self.hydrogen_available = True
                self.scenario.location_building_num_heating_tech_hydrogen.accumulate_item(rkey=self.rkey, value=1)

        self.heating_technology_main = HeatingTechnology(
            rkey=self.rkey.make_copy(),
            scenario=self.scenario,
            priority="main"
        )
        self.heating_technology_main.init_option()
        self.heating_technology_main.init_installation_year(building_age=building_age)
        self.heating_technology_main.update_supply_temperature_space_heating()
        self.heating_technology_main.update_supply_temperature_hot_water()
        self.heating_technology_main.update_energy_intensity_space_heating()
        self.heating_technology_main.update_energy_intensity_hot_water()
        mark_info()

    def init_heating_technology_main_new_construction(self, heating_demand_profile: np.array, hot_water_profile: np.array):
        self.heating_technology_main = HeatingTechnology(
            rkey=self.rkey.make_copy(),
            scenario=self.scenario,
            priority="main"
        )
        if self.scenario.s_construction_mandatory_renewable_heating.get_item(self.rkey) == 1:
            self.heating_technology_main.update_optional_heating_technologies(
                district_heating_available=self.district_heating_available,
                gas_available=self.gas_available,
                hydrogen_available=self.hydrogen_available,
                limit_to=cons.RENEWABLE_MAIN_HEATING_TECHNOLOGIES
            )
        else:
            self.heating_technology_main.update_optional_heating_technologies(
                district_heating_available=self.district_heating_available,
                gas_available=self.gas_available,
                hydrogen_available=self.hydrogen_available,
            )
        action_info = self.heating_technology_main.select(
            heating_demand_profile=heating_demand_profile,
            hot_water_profile=hot_water_profile,
            new_construction=True,
            reason="new_construction"
        )
        self.heating_technology_main.install()
        self.rkey.id_heating_system = int(list(str(self.heating_technology_main.rkey.id_heating_technology))[0])
        return action_info

    def init_heating_technology_second(self, building_age: int):
        df = self.scenario.s_heating_technology_second
        df = df.loc[
            (df["id_building_type"] == self.rkey.id_building_type) &
            (df["id_building_construction_period"] == self.rkey.id_building_construction_period)
        ]
        total_market_share = 0
        second_technologies = {}
        for index, row in df.iterrows():
            total_market_share += row[str(self.rkey.year)]
            second_technologies[row["id_heating_technology"]] = row[str(self.rkey.year)]
        if random.uniform(0, 1) < total_market_share:
            rkey = self.rkey.make_copy().set_id({"id_heating_technology": dict_sample(second_technologies)})
            # init second heating technology
            self.heating_technology_second = HeatingTechnology(
                rkey=rkey,
                scenario=self.scenario,
                priority="second"
            )
            self.heating_technology_second.init_installation_year(building_age=building_age)
            self.heating_technology_second.update_supply_temperature_space_heating()
            self.heating_technology_second.update_supply_temperature_hot_water()
            self.heating_technology_second.space_heating_contribution = self.scenario.p_heating_technology_second_contribution_space_heating.get_item(rkey)
            self.heating_technology_second.hot_water_contribution = self.scenario.p_heating_technology_second_contribution_hot_water.get_item(rkey)
            self.heating_technology_second.update_energy_intensity_space_heating()
            self.heating_technology_second.update_energy_intensity_hot_water()
            # update main heating technology
            self.heating_technology_main.space_heating_contribution = 1 - self.scenario.p_heating_technology_second_contribution_space_heating.get_item(rkey)
            self.heating_technology_main.hot_water_contribution = 1 - self.scenario.p_heating_technology_second_contribution_hot_water.get_item(rkey)
            self.heating_technology_main.update_energy_intensity_space_heating()
            self.heating_technology_main.update_energy_intensity_hot_water()


class HeatingTechnology:

    def __init__(self, rkey: "BuildingKey", scenario: "BuildingScenario", priority: str):
        self.rkey = rkey
        self.scenario = scenario
        self.priority = priority
        self.heating_technology_size = 0
        self.supply_temperature_space_heating = 0
        self.supply_temperature_hot_water = 0
        self.space_heating_contribution = 1
        self.hot_water_contribution = 1
        self.installation_year = 0
        self.next_replace_year = 0
        self.space_heating_energy_intensities = []
        self.hot_water_energy_intensities = []
        self.optional_heating_technologies = []

    def init_option(self):
        if self.rkey.id_heating_technology is None:
            self.rkey.init_dimension(
                dimension_name="id_heating_technology",
                dimension_ids=self.scenario.r_heating_system_technology_main.get_item(self.rkey),
                rdict=self.scenario.s_heating_technology_main
            )

    def init_installation_year(self, building_age: int):
        lifetime = self.get_lifetime()
        age = min(random.randint(0, lifetime), building_age)
        self.installation_year = self.rkey.year - age
        self.next_replace_year = self.rkey.year + lifetime - age

    def init_heating_technology_size(self, heating_demand_profile: np.array, hot_water_profile: np.array,):
        heating_technology_demand_profile = (
            self.space_heating_contribution * heating_demand_profile +
            self.hot_water_contribution * hot_water_profile
        )
        rkey = self.rkey.make_copy()
        rkey.id_energy_carrier = self.scenario.r_heating_technology_energy_carrier.get_item(rkey=rkey)[0]  # for HPs, there are two energy carriers and the first one in the returned list is electricity
        heating_technology_efficiency = self.scenario.s_heating_technology_efficiency.get_item(rkey)
        self.heating_technology_size = np.quantile(
            heating_technology_demand_profile,
            1 - self.scenario.p_heating_technology_size_quantile.get_item(rkey)
        ) / heating_technology_efficiency

    def get_lifetime(self):
        return random.randint(
            self.scenario.p_heating_technology_lifetime_min.get_item(self.rkey),
            self.scenario.p_heating_technology_lifetime_max.get_item(self.rkey)
        )

    def get_space_heating_efficiency_adjustment_factor(self):
        adjustment_parameter = self.scenario.p_heating_technology_supply_temperature_efficiency_adjustment.get_item(self.rkey)
        adjustment_factor = ...  # depending on supply_temperature
        # supply_temperature_space_heating is used in this function
        return 1

    def update_supply_temperature_space_heating(self):
        self.supply_temperature_space_heating = self.scenario.p_building_supply_temperature_space_heating.get_item(self.rkey)

    def update_supply_temperature_hot_water(self):
        self.supply_temperature_hot_water = self.scenario.p_building_supply_temperature_hot_water.get_item(self.rkey)

    def update_energy_intensity_space_heating(self):
        self.space_heating_energy_intensities = []
        for id_energy_carrier in self.scenario.r_heating_technology_energy_carrier.get_item(self.rkey):
            rkey = self.rkey.make_copy().set_id({
                "id_energy_carrier": id_energy_carrier,
                "year": self.installation_year
            })
            adjusted_efficiency = (
                self.scenario.s_heating_technology_efficiency.get_item(rkey) *
                self.get_space_heating_efficiency_adjustment_factor()
            )
            self.space_heating_energy_intensities.append(EnergyIntensity(
                id_end_use=cons.ID_END_USE_SPACE_HEATING,
                id_energy_carrier=rkey.id_energy_carrier,
                value=self.space_heating_contribution * (1 / adjusted_efficiency)
            ))

    def update_energy_intensity_hot_water(self):
        self.hot_water_energy_intensities = []
        for id_energy_carrier in self.scenario.r_heating_technology_energy_carrier.get_item(self.rkey):
            rkey = self.rkey.make_copy().set_id({
                "id_energy_carrier": id_energy_carrier,
                "year": self.installation_year
            })
            self.hot_water_energy_intensities.append(EnergyIntensity(
                id_end_use=cons.ID_END_USE_HOT_WATER,
                id_energy_carrier=rkey.id_energy_carrier,
                value=self.hot_water_contribution * (1 / self.scenario.s_heating_technology_efficiency.get_item(rkey))
            ))

    def update_due_to_radiator_change(self, id_radiator: int):
        self.rkey.id_radiator = id_radiator
        self.update_supply_temperature_space_heating()
        self.update_energy_intensity_space_heating()

    def update_optional_heating_technologies(
        self,
        district_heating_available: bool,
        gas_available: bool,
        hydrogen_available: bool,
        limit_to: Optional[List[int]] = None
    ):

        def check_infrastructure_availability(tech_options):
            if not district_heating_available:
                tech_options = list(set(tech_options) - set(cons.DISTRICT_HEATING_TECHNOLOGIES))
            if not gas_available:
                tech_options = list(set(tech_options) - set(cons.GAS_HEATING_TECHNOLOGIES))
            if not hydrogen_available:
                tech_options = list(set(tech_options) - set(cons.HYDROGEN_HEATING_TECHNOLOGIES))
            return tech_options

        if limit_to is None:
            if self.priority == "main":
                self.optional_heating_technologies = check_infrastructure_availability(tech_options=list(
                    set(self.scenario.heating_technologies.keys()) - set(cons.SECOND_HEATING_TECHNOLOGIES)
                ))
            else:
                self.optional_heating_technologies = cons.SECOND_HEATING_TECHNOLOGIES
        else:
            self.optional_heating_technologies = check_infrastructure_availability(tech_options=limit_to)

    def select(
            self,
            heating_demand_profile: np.array,
            hot_water_profile: np.array,
            reason: str,
            new_construction: bool = False
    ):

        def get_heating_technology_size():
            heating_technology_demand_profile = (
                self.space_heating_contribution * heating_demand_profile +
                self.hot_water_contribution * hot_water_profile
            )
            rkey.id_energy_carrier = self.scenario.r_heating_technology_energy_carrier.get_item(rkey=rkey)[0] # for HPs, there are two energy carriers and the first one in the returned list is electricity
            heating_technology_efficiency = self.scenario.s_heating_technology_efficiency.get_item(rkey)
            return np.quantile(
                heating_technology_demand_profile,
                1 - self.scenario.p_heating_technology_size_quantile.get_item(rkey)
            ) / heating_technology_efficiency

        rkey = self.rkey.make_copy()
        total_heating_demand = np.sum(heating_demand_profile) + np.sum(hot_water_profile)
        d_option_cost = {}
        d_option_action_info = {}
        for id_heating_technology in self.optional_heating_technologies:
            rkey.id_heating_technology = id_heating_technology
            rkey = self.update_action_type(rkey=rkey, new_construction=new_construction)
            heating_technology_size = get_heating_technology_size()
            if self.scenario.s_heating_technology_availability.get_item(rkey):
                if heating_technology_size < self.scenario.p_heating_technology_cost_criterion_small.get_item(rkey):
                    scale = "small"
                    investment_cost_per_kW_not_annualized = self.calc_investment_cost(
                        rkey=rkey,
                        heating_technology_size=heating_technology_size,
                        small_scale=True
                    )
                    om_cost_per_kW = self.calc_om_cost(
                        rkey=rkey,
                        heating_technology_size=heating_technology_size,
                        small_scale=True
                    )
                else:
                    scale = "large"
                    investment_cost_per_kW_not_annualized = self.calc_investment_cost(
                        rkey=rkey,
                        heating_technology_size=heating_technology_size,
                        small_scale=False
                    )
                    om_cost_per_kW = self.calc_om_cost(
                        rkey=rkey,
                        heating_technology_size=heating_technology_size,
                        small_scale=False
                    )
                investment_cost_per_kW_annualized = investment_cost_per_kW_not_annualized * self.get_annuity_factor(rkey)
                investment_cost_annualized = investment_cost_per_kW_annualized * heating_technology_size
                subsidy_percentage = self.scenario.s_subsidy_heating_modernization.get_item(rkey=rkey)
                om_cost = om_cost_per_kW * heating_technology_size
                energy_cost_per_kWh = self.scenario.heating_technology_energy_cost.get_item(rkey)
                energy_cost = energy_cost_per_kWh * total_heating_demand
                d_option_cost[id_heating_technology] = investment_cost_annualized * (1 - subsidy_percentage) + energy_cost + om_cost
                total_investment = investment_cost_per_kW_not_annualized * heating_technology_size
                total_investment_building = total_investment * (1 - subsidy_percentage)
                total_investment_state = total_investment * subsidy_percentage
                d_option_action_info[id_heating_technology] = {
                    "id_scenario": rkey.id_scenario,
                    "id_region": rkey.id_region,
                    "id_sector": rkey.id_sector,
                    "id_subsector": rkey.id_subsector,
                    "id_subsector_agent": rkey.id_subsector_agent,
                    "id_building_type": rkey.id_building_type,
                    "id_building_construction_period": rkey.id_building_construction_period,
                    "id_building_ownership": rkey.id_building_ownership,
                    "year": rkey.year,
                    "heating_technology": self.priority,
                    "reason": reason,
                    "total_heating_demand_peak": 0,
                    "space_heating_contribution": self.space_heating_contribution,
                    "hot_water_contribution": self.hot_water_contribution,
                    "heating_technology_size": heating_technology_size,
                    "heating_demand": total_heating_demand,
                    "criterion_small": self.scenario.p_heating_technology_cost_criterion_small.get_item(rkey),
                    "scale": scale,
                    "id_heating_technology_before": self.rkey.id_heating_technology,
                    "id_heating_technology_after": 0,
                    "heating_system_renewable_percentage_before": 0,
                    "heating_system_renewable_percentage_after": 0,
                    "total_energy_cost_before": 0,
                    "total_energy_cost_after": 0,
                    "id_heating_system_action": rkey.id_heating_system_action,
                    "investment_cost_per_kW": investment_cost_per_kW_annualized,
                    "energy_cost_per_kWh": energy_cost_per_kWh,
                    "om_cost_per_kW": om_cost_per_kW,
                    "energy_cost": energy_cost,
                    "om_cost": om_cost,
                    "total_investment_cost_annualized": investment_cost_annualized,
                    "total_investment": investment_cost_per_kW_not_annualized * heating_technology_size,
                    "total_investment_building": total_investment_building,
                    "total_investment_state": total_investment_state,
                    "labor_demand": self.scenario.s_heating_technology_input_labor.get_item(rkey),
                    "annuity_factor": self.get_annuity_factor(rkey),
                }
        self.rkey.id_heating_technology = dict_utility_sample(
            options=dict_normalize(d_option_cost),
            utility_power=self.scenario.s_heating_technology_utility_power.get_item(rkey)
        )
        self.heating_technology_size = d_option_action_info[self.rkey.id_heating_technology]["heating_technology_size"]
        return d_option_action_info[self.rkey.id_heating_technology]

    def update_action_type(self, rkey: "BuildingKey", new_construction: bool = False):
        if not new_construction:
            if rkey.id_heating_technology == self.rkey.id_heating_technology:
                rkey.set_id({"id_heating_system_action": cons.ID_HEATING_SYSTEM_ACTION_SAME})
            else:
                rkey.set_id({"id_heating_system_action": cons.ID_HEATING_SYSTEM_ACTION_DIFFERENT})
        else:
            rkey.set_id({"id_heating_system_action": cons.ID_HEATING_SYSTEM_ACTION_NEW})
        return rkey

    def get_annuity_factor(self, rkey: "BuildingKey"):
        interest_rate = self.scenario.s_interest_rate.get_item(rkey)
        lifetime = self.scenario.p_heating_technology_cost_payback_time.get_item(rkey)
        return interest_rate / (1 - (1 + interest_rate) ** (- lifetime))

    def calc_investment_cost(self, rkey: "BuildingKey", heating_technology_size: float, small_scale: bool):
        criterion_small = self.scenario.p_heating_technology_cost_criterion_small.get_item(rkey)
        m_cost = self.scenario.p_heating_technology_cost_multiplier_material.get_item(rkey)
        e_cost = self.scenario.p_heating_technology_cost_exponent_material.get_item(rkey)
        m_share = self.scenario.p_heating_technology_cost_share_multiplier_material.get_item(rkey)
        e_share = self.scenario.p_heating_technology_cost_share_exponent_material.get_item(rkey)
        pp_index = self.scenario.p_heating_technology_cost_pp_index.get_item(rkey)
        wage_index = self.scenario.p_heating_technology_cost_wages_index.get_item(rkey)
        learning_coefficient = self.scenario.p_heating_technology_cost_learning_coefficient.get_item(rkey)
        if small_scale:
            cost_material = m_cost * criterion_small ** e_cost * m_share * heating_technology_size ** e_share * pp_index ** 0.5
            cost_labor = m_cost * criterion_small ** e_cost * (
                        1 - m_share * heating_technology_size ** e_share) * wage_index
            inv_cost_per_kW_not_annualized = ((cost_material + cost_labor) *
                                              (1 - learning_coefficient) ** (rkey.year - 2012) *
                                              heating_technology_size / criterion_small)
        else:
            cost_material = m_cost * m_share * heating_technology_size ** (e_cost + e_share) * pp_index ** 0.5
            cost_labor = m_cost * heating_technology_size ** e_cost - (m_cost * m_share) * heating_technology_size ** (
                        e_cost + e_share) * wage_index
            inv_cost_per_kW_not_annualized = (
                        (cost_material + cost_labor) * (1 - learning_coefficient) ** (rkey.year - 2012))
        return inv_cost_per_kW_not_annualized

    def calc_om_cost(self, rkey: "BuildingKey", heating_technology_size: float, small_scale: bool):
        criterion_small = self.scenario.p_heating_technology_cost_criterion_small.get_item(rkey)
        m_om = self.scenario.p_heating_technology_cost_multiplier_om.get_item(rkey)
        e_om = self.scenario.p_heating_technology_cost_exponent_om.get_item(rkey)
        wage_index = self.scenario.p_heating_technology_cost_wages_index.get_item(rkey)
        if small_scale:
            om_cost = m_om * criterion_small ** e_om * wage_index * heating_technology_size / criterion_small
        else:
            om_cost = m_om * heating_technology_size ** e_om * wage_index
        return om_cost

    def install(self):
        self.installation_year = self.rkey.year
        self.next_replace_year = self.rkey.year + self.get_lifetime()
        self.update_supply_temperature_space_heating()
        self.update_supply_temperature_hot_water()
        self.update_energy_intensity_space_heating()
        self.update_energy_intensity_hot_water()


