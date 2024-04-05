import random
from typing import Optional
from typing import TYPE_CHECKING

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
        self.technologies = []

    def init_system_type(self):
        self.rkey.init_dimension(
            dimension_name="id_heating_system",
            dimension_ids=self.scenario.r_sector_heating_system.get_item(self.rkey),
            rdict=self.scenario.s_heating_system
        )

    def init_heating_technology_main(self):

        def mark_info():
            self.scenario.location_building_num.accumulate_item(rkey=self.rkey, value=1)
            self.scenario.heating_technology_main_initial_adoption.accumulate_item(rkey=self.heating_technology_main.rkey, value=1)
            if self.heating_technology_main.rkey.id_heating_technology in cons.DISTRICT_HEATING_TECHNOLOGIES:
                self.district_heating_available = True
                self.scenario.location_building_num_heating_tech_district_heating.accumulate_item(rkey=self.rkey, value=1)
            elif self.heating_technology_main.rkey.id_heating_technology in cons.GAS_HEATING_TECHNOLOGIES:
                self.gas_available = True
                self.scenario.location_building_num_heating_tech_gas.accumulate_item(rkey=self.rkey, value=1)

        self.heating_technology_main = HeatingTechnology(
            rkey=self.rkey.make_copy(),
            scenario=self.scenario,
            priority="main"
        )
        self.heating_technology_main.init_option()
        self.heating_technology_main.init_installation_year()
        self.heating_technology_main.update_supply_temperature_space_heating()
        self.heating_technology_main.update_supply_temperature_hot_water()
        self.heating_technology_main.update_energy_intensity_space_heating()
        self.heating_technology_main.update_energy_intensity_hot_water()
        mark_info()

    def init_heating_technology_second(self):
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
            self.heating_technology_second.init_installation_year()
            self.heating_technology_main.update_supply_temperature_space_heating()
            self.heating_technology_main.update_supply_temperature_hot_water()
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

    def init_installation_year(self):
        lifetime = self.get_lifetime()
        age = random.randint(0, lifetime)
        self.installation_year = self.rkey.year - age
        self.next_replace_year = self.rkey.year + lifetime - age

    def get_lifetime(self):
        return random.randint(
            self.scenario.p_heating_technology_lifetime_min.get_item(self.rkey),
            self.scenario.p_heating_technology_lifetime_max.get_item(self.rkey)
        )

    def get_space_heating_efficiency_adjustment_factor(self):
        adjustment_parameter = self.scenario.p_heating_technology_supply_temperature_efficiency_adjustment.get_item(self.rkey)
        adjustment_factor = ...  # TODO: depending on supply_temperature
        self.supply_temperature_space_heating = ... # used in this function
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

    def update_optional_heating_technologies(self, district_heating_available: bool, gas_available: bool):
        if self.priority == "main":
            l = list(set(self.scenario.heating_technologies) - set(cons.SECOND_HEATING_TECHNOLOGIES))
            if not district_heating_available:
                l = list(set(l) - set(cons.DISTRICT_HEATING_TECHNOLOGIES))
            if not gas_available:
                l = list(set(l) - set(cons.GAS_HEATING_TECHNOLOGIES))
            self.optional_heating_technologies = l
        else:
            self.optional_heating_technologies = cons.SECOND_HEATING_TECHNOLOGIES

    def select(self, total_heating_demand_peak: float, heating_demand: float):

        def update_action_type():
            if rkey.id_heating_technology == self.rkey.id_heating_technology:
                rkey.set_id({"id_heating_system_action": cons.ID_HEATING_SYSTEM_ACTION_SAME})
            else:
                rkey.set_id({"id_heating_system_action": cons.ID_HEATING_SYSTEM_ACTION_DIFFERENT})

        def get_annuity_factor():
            interest_rate = self.scenario.s_interest_rate.get_item(rkey)
            lifetime = 0.5 * (self.scenario.p_heating_technology_lifetime_min.get_item(rkey) + self.scenario.p_heating_technology_lifetime_max.get_item(rkey))
            return interest_rate / (1 - (1 + interest_rate) ** (- lifetime))

        def calc_investment_cost(small_scale: bool):
            criterion_small = self.scenario.p_heating_technology_cost_criterion_small.get_item(rkey)
            m_cost = self.scenario.p_heating_technology_cost_multiplier_material.get_item(rkey)
            e_cost = self.scenario.p_heating_technology_cost_exponent_material.get_item(rkey)
            m_share = self.scenario.p_heating_technology_cost_share_multiplier_material.get_item(rkey)
            e_share = self.scenario.p_heating_technology_cost_share_exponent_material.get_item(rkey)
            pp_index = self.scenario.p_heating_technology_cost_pp_index.get_item(rkey)
            wage_index = self.scenario.p_heating_technology_cost_wages_index.get_item(rkey)
            learning_coefficient = self.scenario.p_heating_technology_cost_learning_coefficient.get_item(rkey)
            if small_scale:
                cost_material = m_cost * criterion_small ** e_cost * m_share * total_heating_demand_peak ** e_share * pp_index ** 0.5
                cost_labor = m_cost * criterion_small ** e_cost * (1 - m_share * total_heating_demand_peak ** e_share) * wage_index
                cost_annualized = ((cost_material + cost_labor) *
                                   (1 - learning_coefficient) ** (rkey.year - 2012) *
                                   total_heating_demand_peak / criterion_small) * get_annuity_factor()
            else:
                cost_material = m_cost * m_share * total_heating_demand_peak ** (e_cost + e_share) * pp_index ** 0.5
                cost_labor = m_cost * total_heating_demand_peak ** e_cost - (m_cost * m_share) * total_heating_demand_peak ** (e_cost + e_share) * wage_index
                cost_annualized = ((cost_material + cost_labor) * (1 - learning_coefficient) ** (rkey.year - 2012)) * get_annuity_factor()
            return cost_annualized

        def calc_om_cost(small_scale: bool):
            criterion_small = self.scenario.p_heating_technology_cost_criterion_small.get_item(rkey)
            m_om = self.scenario.p_heating_technology_cost_multiplier_om.get_item(rkey)
            e_om = self.scenario.p_heating_technology_cost_exponent_om.get_item(rkey)
            wage_index = self.scenario.p_heating_technology_cost_wages_index.get_item(rkey)
            if small_scale:
                om_cost = m_om * criterion_small ** e_om * wage_index * total_heating_demand_peak / criterion_small
            else:
                om_cost = m_om * total_heating_demand_peak ** e_om * wage_index
            return om_cost

        rkey = self.rkey.make_copy()
        d_option_cost = {}
        for id_heating_technology in self.optional_heating_technologies:
            rkey.id_heating_technology = id_heating_technology
            if self.scenario.s_heating_technology_availability.get_item(rkey):
                update_action_type()
                if total_heating_demand_peak < self.scenario.p_heating_technology_cost_criterion_small.get_item(rkey):
                    investment_cost = calc_investment_cost(small_scale=True)
                    om_cost = calc_om_cost(small_scale=True)
                else:
                    investment_cost = calc_investment_cost(small_scale=False)
                    om_cost = calc_om_cost(small_scale=False)
                energy_cost = self.scenario.heating_technology_energy_cost.get_item(rkey) * heating_demand
                d_option_cost[id_heating_technology] = investment_cost + om_cost + energy_cost
        self.rkey.id_heating_technology = dict_utility_sample(
            options=dict_normalize(d_option_cost),
            utility_power=self.scenario.s_heating_technology_utility_power.get_item(rkey)
        )

    def install(self):
        self.update_energy_intensity_space_heating()
        self.update_energy_intensity_hot_water()
        self.installation_year = self.rkey.year
        self.next_replace_year = self.rkey.year + self.get_lifetime()

