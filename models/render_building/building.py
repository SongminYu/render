import random
from typing import TYPE_CHECKING, List, Optional, Dict

import numpy as np
from Melodie import Agent

from models.render_building import cons
from models.render_building.building_component import BuildingComponent
from models.render_building.building_key import BuildingKey
from models.render_building.building_r5c1 import R5C1, spec
from models.render_building.building_unit import Unit
from models.render_building.tech_cooling import CoolingSystem
from models.render_building.tech_heating import HeatingSystem, HeatingTechnology
from models.render_building.tech_radiator import Radiator
from models.render_building.tech_ventilation import VentilationSystem
from models.render_building.tech_pv import PhotovoltaicSystem
from utils.funcs import dict_sample, dict_normalize, dict_utility_sample

if TYPE_CHECKING:
    from models.render_building.scenario import BuildingScenario


def create_empty_arr():
    return np.zeros((8760, ))


class Building(Agent):
    scenario: "BuildingScenario"

    """
    Building initialization
    """

    def setup(self):
        self.id_region = 0
        self.id_sector = 0
        self.id_subsector = 0
        self.id_building_type = 0
        self.id_subsector_agent = 0
        self.building_number = 0
        self.occupancy_rate = 1
        self.exists = True
        self.mandatory_renovation_year = cons.MANDATORY_RENOVATION_YEAR_DEFAULT
        self.mandatory_heating_system_modernization_year = cons.MANDATORY_HEATING_SYSTEM_MODERNIZATION_YEAR_DEFAULT

    def init_rkey(self):
        self.rkey = BuildingKey(
            id_scenario=self.scenario.id,
            id_region=self.id_region,
            id_sector=self.id_sector,
            id_subsector=self.id_subsector,
            id_building_type=self.id_building_type,
            id_subsector_agent=self.id_subsector_agent,
            year=self.scenario.start_year
        )
        self.init_rkey_id_building_construction_period()
        self.init_rkey_id_building_location()
        self.init_rkey_id_building_height()
        self.init_rkey_id_building_ownership()

    def init_rkey_new_construction(self, construction_year: int):
        self.rkey = BuildingKey(
            id_scenario=self.scenario.id,
            id_region=self.id_region,
            id_sector=self.id_sector,
            id_subsector=self.id_subsector,
            id_building_type=self.id_building_type,
            id_subsector_agent=self.id_subsector_agent,
            year=construction_year,
            id_building_construction_period=cons.ID_BUILDING_CONSTRUCTION_PERIOD_NEW_BUILDING,
        )
        self.init_rkey_id_building_location()
        self.init_rkey_id_building_height()
        self.init_rkey_id_building_ownership()

    def init_rkey_id_building_construction_period(self):
        self.rkey.init_dimension(
            dimension_name="id_building_construction_period",
            dimension_ids=self.scenario.building_construction_periods.keys(),
            rdict=self.scenario.s_building_construction_period
        )

    def init_rkey_id_building_location(self):
        self.rkey.init_dimension(
            dimension_name="id_building_location",
            dimension_ids=self.scenario.building_locations.keys(),
            rdict=self.scenario.s_building_location
        )

    def init_rkey_id_building_ownership(self):
        self.rkey.init_dimension(
            dimension_name="id_building_ownership",
            dimension_ids=self.scenario.building_ownerships.keys(),
            rdict=self.scenario.s_building_ownership
        )

    def init_rkey_id_building_height(self):
        self.rkey.init_dimension(
            dimension_name="id_building_height",
            dimension_ids=self.scenario.r_building_type_height.get_item(self.rkey),
            rdict=self.scenario.s_building_height
        )

    def __repr__(self):
        return (f"Building<Region-{self.rkey.id_region}_"
                f"Sector-{self.rkey.id_sector}_"
                f"Subsector-{self.rkey.id_subsector}_"
                f"Agent-{self.rkey.id_subsector_agent}>")

    def init_units(self):
        self.units: Optional[List[Unit]] = []
        self.population = 0
        self.unit_area = self.scenario.s_building_unit_area.get_item(self.rkey)
        self.unit_number = random.randint(self.scenario.p_building_unit_number_min.get_item(self.rkey),
                                          self.scenario.p_building_unit_number_max.get_item(self.rkey))
        for id_unit in range(0, self.unit_number):
            unit = Unit(self.rkey.make_copy(), self.scenario)
            if self.rkey.id_sector == cons.ID_SECTOR_RESIDENTIAL and self.rkey.year == self.scenario.start_year:
                self.scenario.dwelling_number.accumulate_item(self.rkey, self.building_number)
                self.scenario.household_number.accumulate_item(unit.user.rkey, self.building_number)
            self.population += unit.user.person_num
            self.units.append(unit)

    def init_building_profiles(self):

        def sum_unit_profile(unit_profile_name: str):
            sum_profile = create_empty_arr()
            for unit in self.units:
                sum_profile += getattr(unit.user, unit_profile_name)
            return sum_profile

        self.occupancy_profile = sum_unit_profile("occupancy_profile") / self.unit_number
        self.appliance_electricity_profile = sum_unit_profile("appliance_electricity_profile")
        self.appliance_electricity_demand = self.appliance_electricity_profile.sum()
        self.appliance_electricity_demand_per_person = self.appliance_electricity_demand / self.population
        self.hot_water_profile = sum_unit_profile("hot_water_profile")
        self.hot_water_demand = self.hot_water_profile.sum()
        self.hot_water_demand_per_person = self.hot_water_demand / self.population

    def init_building_size(self):
        self.height = random.randint(self.scenario.p_building_height_min.get_item(self.rkey),
                                     self.scenario.p_building_height_max.get_item(self.rkey))
        self.total_living_area = self.unit_area * self.unit_number
        self.storey_living_area = self.unit_area * (self.unit_number / self.height)
        self.hot_water_demand_per_m2 = self.hot_water_demand / self.total_living_area

    def init_building_construction(self):
        self.construction_year = random.randint(
            self.scenario.p_building_construction_year_min.get_item(self.rkey),
            min(self.scenario.start_year - 1, self.scenario.p_building_construction_year_max.get_item(self.rkey))
        )
        self.demolish_year = random.randint(
            max(
                self.scenario.start_year,
                self.construction_year + self.scenario.p_building_lifetime_min.get_item(self.rkey)
            ),
            self.construction_year + self.scenario.p_building_lifetime_max.get_item(self.rkey)
        )
        self.lifetime = self.demolish_year - self.construction_year

    def init_building_construction_new_construction(self):
        self.construction_year = self.rkey.year
        self.lifetime = random.randint(
            self.scenario.p_building_lifetime_min.get_item(self.rkey),
            self.scenario.p_building_lifetime_max.get_item(self.rkey)
        )
        self.demolish_year = self.construction_year + self.lifetime

    def init_building_components(self):
        self.building_components: Optional[Dict[str, BuildingComponent]] = {}
        for id_building_component, component_name in self.scenario.building_components.items():
            component = BuildingComponent(self.rkey.make_copy(), self.scenario)
            component.rkey.id_building_component = id_building_component
            component.init_name()
            component.init_option()
            component.init_area(
                ref_area=self.__dict__[self.scenario.p_building_envelope_component_area_ref.get_item(component.rkey)],
                ratio=self.scenario.p_building_envelope_component_area_ratio.get_item(component.rkey)
            )
            component.init_construction(building_construction_year=self.construction_year)
            self.building_components[component_name] = component

    def init_building_renovation_history(self):
        for component in self.building_components.values():
            while component.next_replace_year < self.rkey.year:
                if random.uniform(0, 1) <= cons.PROB_POSTPONING_RENOVATION:
                    action_year = component.next_replace_year
                    component.init_historical_renovation(action_year=action_year)
                else:
                    component.next_replace_year += self.scenario.p_building_component_postponing_lifetime.get_item(component.rkey)

    def init_radiator(self):
        self.radiator = Radiator(self.rkey.make_copy(), self.scenario)
        self.radiator.init_option()
        self.rkey.id_radiator = self.radiator.rkey.id_radiator
        self.radiator.init_installation_year()

    def init_radiator_new_construction(self):
        self.radiator = Radiator(self.rkey.make_copy(), self.scenario)
        self.radiator.init_option()
        self.rkey.id_radiator = self.radiator.rkey.id_radiator
        self.radiator.installation_year = self.rkey.year
        self.radiator.next_replace_year = self.rkey.year + self.radiator.get_lifetime()

    def init_building_cooling_system(self):
        self.cooling_system = CoolingSystem(self.rkey.make_copy(), self.scenario)
        if random.uniform(0, 1) <= self.scenario.s_cooling_penetration_rate.get_item(self.rkey):
            self.cooling_system.init_adoption()

    def init_building_cooling_system_new_construction(self):
        self.cooling_system = CoolingSystem(self.rkey.make_copy(), self.scenario)
        if random.uniform(0, 1) <= self.scenario.s_cooling_penetration_rate.get_item(self.rkey):
            self.cooling_system.select(
                cooling_demand_peak=self.cooling_demand_peak,
                cooling_demand=self.cooling_demand,
            )
            self.cooling_system.install()

    def init_building_heating_system(self):
        self.heating_system = HeatingSystem(self.rkey.make_copy(), self.scenario)
        self.heating_system.init_system_type()
        self.heating_system.init_heating_technology_main(building_age=self.rkey.year - self.construction_year)
        self.heating_system.init_heating_technology_second(building_age=self.rkey.year - self.construction_year)
        self.heating_system.heating_technology_main.init_heating_technology_size(
            heating_demand_profile=self.heating_demand_profile,
            hot_water_profile=self.hot_water_profile
        )
        self.heating_system.heating_technologies = [
            self.heating_system.heating_technology_main,
            self.heating_system.heating_technology_second
        ]

    def init_building_heating_system_new_construction(self):
        self.heating_system = HeatingSystem(self.rkey.make_copy(), self.scenario)
        self.init_building_district_heating_availability_new_construction()
        self.init_building_gas_availability_new_construction()
        self.init_building_hydrogen_availability_new_construction()
        action_info = self.heating_system.init_heating_technology_main_new_construction(
            heating_demand_profile=self.heating_demand_profile,
            hot_water_profile=self.hot_water_profile
        )
        # TODO: second heating technology is left as None for new buildings
        self.heating_system.heating_technologies = [
            self.heating_system.heating_technology_main,
            self.heating_system.heating_technology_second
        ]
        self.init_final_energy_demand()
        self.update_total_energy_cost()
        self.update_heating_system_renewable_percentage()
        action_info["total_heating_demand_peak"] = self.total_heating_demand_peak
        action_info["id_heating_technology_after"] = self.heating_system.heating_technology_main.rkey.id_heating_technology
        action_info["heating_system_renewable_percentage_before"] = None
        action_info["heating_system_renewable_percentage_after"] = self.heating_system_renewable_percentage
        action_info["total_energy_cost_before"] = None
        action_info["total_energy_cost_after"] = self.total_energy_cost
        action_info["building_number"] = self.building_number
        self.scenario.heating_system_action_info.append(action_info)

    def init_building_district_heating_availability(self):

        def get_district_heating_connection_prob():
            connection_prob = 0
            n = self.scenario.location_building_num.get_item(self.rkey, not_found_default=0)
            if n > 0:
                m = self.scenario.location_building_num_heating_tech_district_heating.get_item(self.rkey, not_found_default=0)
                initial_ratio = m / n
                target_ratio = self.scenario.s_infrastructure_availability_district_heating.get_item(self.rkey)
                if target_ratio > initial_ratio:
                    connection_prob = (target_ratio - initial_ratio) / (1 - initial_ratio)
            return connection_prob

        if not self.heating_system.district_heating_available:
            if random.uniform(0, 1) <= get_district_heating_connection_prob():
                self.heating_system.district_heating_available = True

    def init_building_district_heating_availability_new_construction(self):
        if random.uniform(0, 1) <= self.scenario.s_infrastructure_availability_district_heating.get_item(self.rkey):
            self.heating_system.district_heating_available = True

    def init_building_gas_availability(self):

        def get_gas_connection_prob():
            connection_prob = 0
            n = self.scenario.location_building_num.get_item(self.rkey, not_found_default=0)
            if n > 0:
                m = self.scenario.location_building_num_heating_tech_gas.get_item(self.rkey, not_found_default=0)
                initial_ratio = m / n
                target_ratio = self.scenario.s_infrastructure_availability_gas.get_item(self.rkey)
                if target_ratio > initial_ratio:
                    connection_prob = (target_ratio - initial_ratio) / (1 - initial_ratio)
            return connection_prob

        if not self.heating_system.gas_available:
            if random.uniform(0, 1) <= get_gas_connection_prob():
                self.heating_system.gas_available = True

    def init_building_gas_availability_new_construction(self):
        if random.uniform(0, 1) <= self.scenario.s_infrastructure_availability_gas.get_item(self.rkey):
            self.heating_system.gas_available = True

    def init_building_hydrogen_availability(self):

        def get_hydrogen_connection_prob():
            connection_prob = 0
            n = self.scenario.location_building_num.get_item(self.rkey, not_found_default=0)
            if n > 0:
                m = self.scenario.location_building_num_heating_tech_hydrogen.get_item(self.rkey, not_found_default=0)
                initial_ratio = m / n
                target_ratio = self.scenario.s_infrastructure_availability_hydrogen.get_item(self.rkey)
                if target_ratio > initial_ratio:
                    connection_prob = (target_ratio - initial_ratio) / (1 - initial_ratio)
            return connection_prob

        if not self.heating_system.hydrogen_available:
            if random.uniform(0, 1) <= get_hydrogen_connection_prob():
                self.heating_system.hydrogen_available = True

    def init_building_hydrogen_availability_new_construction(self):
        if random.uniform(0, 1) <= self.scenario.s_infrastructure_availability_hydrogen.get_item(self.rkey):
            self.heating_system.hydrogen_available = True

    def init_building_ventilation_system(self):
        self.ventilation_system = VentilationSystem(self.rkey.make_copy(), self.scenario)
        if random.uniform(0, 1) <= self.scenario.s_ventilation_penetration_rate.get_item(self.rkey):
            self.ventilation_system.init_adoption()

    def init_building_ventilation_system_new_construction(self):
        self.ventilation_system = VentilationSystem(self.rkey.make_copy(), self.scenario)
        if random.uniform(0, 1) <= self.scenario.s_ventilation_penetration_rate.get_item(self.rkey):
            self.ventilation_system.select(total_living_area=self.total_living_area)
            self.ventilation_system.install()

    def init_building_pv_system(self):
        self.pv_system = PhotovoltaicSystem(self.rkey.make_copy(), self.scenario)
        if random.uniform(0, 1) <= self.scenario.s_pv_penetration_rate.get_item(self.rkey):
            self.pv_system.init_adoption(
                roof_area=self.building_components["roof"].area,
                generation_profile=self.get_pv_generation_profile(self.rkey)
            )

    def get_pv_generation_profile(self, rkey_to_adjust_year: "BuildingKey"):
        rkey_adjusted = self.adjust_rkey_year_for_weather_profiles(rkey_to_adjust_year)
        return self.scenario.pr_pv_generation.get_item(rkey_adjusted)

    def init_building_pv_system_new_construction(self):
        self.pv_system = PhotovoltaicSystem(self.rkey.make_copy(), self.scenario)
        new_construction_requirement = random.uniform(0, 1) <= self.scenario.s_construction_pv_adoption_rate.get_item(self.rkey)
        penetration = random.uniform(0, 1) <= self.scenario.s_pv_penetration_rate.get_item(self.rkey)
        if new_construction_requirement or penetration:
            self.pv_system.init_adoption(
                roof_area=self.building_components["roof"].area,
                generation_profile=self.get_pv_generation_profile(self.rkey)
            )

    """
    heating and cooling demand calculation
    """

    def calc_building_heating_cooling_demand(self):
        self.init_building_efficiency_class()
        self.update_r5c1_temperature()
        self.conduct_r5c1_calculation()
        self.reality_norm_factor = self.heating_demand_per_m2 / self.heating_demand_per_m2_norm

    def init_building_efficiency_class(self):
        self.update_r5c1_params()
        self.update_r5c1_temperature(norm=True)
        self.conduct_r5c1_calculation()
        self.heating_demand_norm = self.heating_demand
        self.heating_demand_per_m2_norm = self.heating_demand_norm / self.total_living_area
        self.total_heating_per_m2_norm = self.heating_demand_per_m2_norm + self.hot_water_demand_per_m2
        self.cooling_demand_norm = self.cooling_demand
        self.cooling_demand_per_m2_norm = self.cooling_demand_per_m2
        self.assign_building_efficiency_class()

    def assign_building_efficiency_class(self):
        for _, row in self.scenario.p_building_efficiency_class_intensity.iterrows():
            if row["min"] <= self.heating_demand_per_m2 <= row["max"]:
                self.rkey.id_building_efficiency_class = row["id_building_efficiency_class"]
                break

    def update_r5c1_params(self):

        def get_infiltration_param(id_window_option_efficiency_class: int):
            if id_window_option_efficiency_class <= 2:
                infiltration_param = 0.05
            elif 2 < id_window_option_efficiency_class <= 4:
                infiltration_param = 0.1
            else:
                infiltration_param = 0.2
            return infiltration_param

        """
        Losses
        """
        # h_tr_is --> heat transfer coefficient of surface to internal air (equation 9)
        h_is = 3.45  # W/m2K
        a_at = 4.5  # factor, no unit
        self.a_is = a_at * self.total_living_area  # internal surface area, m2
        self.h_tr_is = h_is * self.a_is  # W/K
        c_m = 45  # heat capacity per square meter (Wh/m2K)
        self.c_m = c_m * self.a_is  # total heat capacity of the thermal mass

        # h_tr_w --> heat transfer coefficient of glazed elements to external air (equation 18)
        window = self.building_components["window"]
        self.h_tr_w = window.area * window.u_value  # W/K

        # h_tr_op --> heat transfer coefficient of opaque elements to external air (equation 18)
        b_tr_wall = 1  # adjustment factor
        b_tr_roof = 1  # adjustment factor
        b_tr_basement = 0.5  # adjustment factor
        wall = self.building_components["wall"]
        roof = self.building_components["roof"]
        basement = self.building_components["basement"]
        self.h_tr_op = b_tr_wall * wall.area * wall.u_value + \
                       b_tr_roof * roof.area * roof.u_value + \
                       b_tr_basement * basement.area * basement.u_value

        # h_tr_ms --> heat transfer coefficient of effective thermal mass to internal surface (equation 64)
        a_am = 2.5  # factor, no unit
        # effective surface of thermal mass, m2
        self.a_m = a_am * self.total_living_area
        h_ms = 9.1  # W/m2K
        self.h_tr_ms = self.a_m * h_ms  # W/K

        # h_tr_em --> heat transfer coefficient of thermal mass to external air (equation 63)
        self.h_tr_em = 1 / (1 / self.h_tr_op - 1 / self.h_tr_ms)

        # h_ve_adj --> heat transfer coefficient of ventilation to external air (equation 21)
        pho_a_c = 1200 / 3600  # Wh/m3K
        b_ve_k = 1  # when there is no ventilation or a "buffer zone", it equals to 1
        q_ve_inf = get_infiltration_param(window.rkey.id_building_component_option_efficiency_class)  # air flow rate due to infiltration (unit: 1/hour)
        q_ve_ven = 0.4  # air flow rate due to ventilation (unit: 1/hour)
        h = 2.5  # height per storey (unit: m)
        self.h_vent_adj = pho_a_c * b_ve_k * (q_ve_inf + q_ve_ven) * self.total_living_area * h

        # h_tr_1, h_tr_2, h_tr_3 --> intermediate variables in the equation
        self.h_tr_1 = 1 / ((1 / self.h_vent_adj) + (1 / self.h_tr_is))
        self.h_tr_2 = self.h_tr_1 + self.h_tr_w
        self.h_tr_3 = 1 / ((1 / self.h_tr_2) + (1 / self.h_tr_ms))

        """
        Gains
        """
        # 1. internal gains
        # 1.1 internal gains through occupancy
        phi_occ = 80  # W per person  (number of person from units)
        self.internal_gain_occ = phi_occ * self.occupancy_profile * self.population

        # 1.2 internal gains through appliance
        self.internal_gain_app = self.appliance_electricity_profile * \
                                 self.scenario.p_building_rc_appliance_internal_gain.get_item(self.rkey)

        # 2. solar gains
        # 2.1 opaque gains

        def get_opaque_effective_area(component_name: str) -> float:
            shading_factor = 0.6
            absorption_coefficient = 0.75
            # surface thermal resistence of the opaque part (m2K/W)
            resistance_coefficient = 0.04
            component = self.building_components[component_name]
            return component.area * component.u_value * resistance_coefficient * shading_factor * absorption_coefficient

        def get_opaque_sky_reflection_profile(component_name: str) -> np.ndarray:
            form_param = {"wall": 0.5, "roof": 1}
            # surface thermal resistence of the opaque part (m2K/W)
            resistance_coefficient = 0.04
            # average temperature difference between ambient air and sky (°C)
            temp_diff = 11
            epsilon = 0.9  # emissivity of the thermal radiation of the outer surface
            # Stefan-Boltzmann constant: σ = 5.67 × 10-8 W/(m2⋅K4)
            sigma = 5.67 * 10 ** (-8)
            outside_temperature = self.get_weather_temperature_profile(self.rkey)
            # external radiant heat transfer coefficient
            h_r = 4 * epsilon * sigma * ((outside_temperature + 273.15) ** 3)
            component = self.building_components[component_name]
            return component.area * component.u_value * resistance_coefficient * temp_diff * form_param[component_name] * h_r

        total_radiation = create_empty_arr()
        rkey = self.rkey.make_copy()
        for id_orientation in self.scenario.orientations.keys():
            rkey.id_orientation = id_orientation
            total_radiation += self.get_weather_radiation_profile(rkey)

        self.solar_gain_opa = create_empty_arr()
        for component_name in ["roof", "wall"]:
            self.solar_gain_opa += total_radiation * get_opaque_effective_area(component_name) - \
                                   get_opaque_sky_reflection_profile(component_name)

        # 2.2 glazing gains
        transmittance_factor = 0.7  # solar transmittance of glass
        shading_factor = 0.6  # shading factor
        frame_share = 0.3  # share of frame area
        correction_param = 0.9  # correction factor
        self.solar_gain_gla = create_empty_arr()
        rkey = self.rkey.make_copy()
        for id_orientation in self.scenario.orientations.keys():
            rkey.id_orientation = id_orientation
            self.solar_gain_gla += correction_param * transmittance_factor * shading_factor * (1 - frame_share) * \
                                   self.get_weather_radiation_profile(rkey) * \
                                   self.scenario.p_building_envelope_window_area_orientation.get_item(rkey)

        # gains in total
        self.internal_gain = self.internal_gain_occ + self.internal_gain_app
        self.solar_gain = self.solar_gain_opa + self.solar_gain_gla

    def update_r5c1_temperature(self, norm: Optional[bool] = False):
        self.weather_temperature = self.get_weather_temperature_profile(self.rkey)
        if self.rkey.id_building_efficiency_class is None or norm:
            self.set_temperature_min = np.ones((8760,)) * 20
            self.set_temperature_max = np.ones((8760,)) * 27
        else:
            self.set_temperature_occupied_min = self.scenario.p_set_temperature_occupied_min.get_item(self.rkey)
            self.set_temperature_occupied_max = self.scenario.p_set_temperature_occupied_max.get_item(self.rkey)
            self.set_temperature_empty_min = self.scenario.p_set_temperature_empty_min.get_item(self.rkey)
            self.set_temperature_empty_max = self.scenario.p_set_temperature_empty_max.get_item(self.rkey)
            self.set_temperature_min = np.ones((8760,))
            self.set_temperature_max = np.ones((8760,))
            # update set_temperature based on occupancy
            for hour in range(0, 8760):
                if random.uniform(0, 1) <= self.scenario.optimal_heating_behavior_prob:
                    self.set_temperature_min[hour] = (self.set_temperature_empty_min +
                                                      (self.set_temperature_occupied_min - self.set_temperature_empty_min) *
                                                      self.occupancy_profile[hour])
                    self.set_temperature_max[hour] = (self.set_temperature_empty_max -
                                                      (self.set_temperature_empty_max - self.set_temperature_occupied_max)
                                                      * self.occupancy_profile[hour])
                else:
                    self.set_temperature_min[hour] = self.set_temperature_occupied_min
                    self.set_temperature_max[hour] = self.set_temperature_occupied_max

    @staticmethod
    def adjust_rkey_year_for_weather_profiles(rkey_to_adjust_year: "BuildingKey"):
        rkey_copy = rkey_to_adjust_year.make_copy()
        if rkey_copy.year > 2020:
            if rkey_copy.year <= 2025:
                rkey_copy.year = 2020
            elif 2025 < rkey_copy.year <= 2035:
                rkey_copy.year = 2030
            elif 2035 < rkey_copy.year <= 2045:
                rkey_copy.year = 2040
            elif 2045 < rkey_copy.year:
                rkey_copy.year = 2050
        return rkey_copy

    def get_weather_temperature_profile(self, rkey_to_adjust_year: "BuildingKey"):
        rkey_adjusted = self.adjust_rkey_year_for_weather_profiles(rkey_to_adjust_year)
        return self.scenario.pr_weather_temperature.get_item(rkey_adjusted)

    def get_weather_radiation_profile(self, rkey_to_adjust_year: "BuildingKey"):
        rkey_adjusted = self.adjust_rkey_year_for_weather_profiles(rkey_to_adjust_year)
        return self.scenario.pr_weather_radiation.get_item(rkey_adjusted)

    def conduct_r5c1_calculation(self):

        def inherit_params(empty_r5c1_model: "R5C1"):
            for attribute, _ in spec:
                if hasattr(self, attribute):
                    setattr(empty_r5c1_model, attribute, getattr(self, attribute))
            return empty_r5c1_model

        r5c1_model = inherit_params(R5C1())
        r5c1_model.update_building_heating_cooling_demand()
        self.heating_demand_profile: np.ndarray = r5c1_model.heating_demand_profile / 1000  # from Wh to kWh
        self.heating_demand = self.heating_demand_profile.sum()
        self.total_heating_demand_peak = (self.heating_demand_profile + self.hot_water_profile).max()
        self.heating_demand_per_m2 = self.heating_demand / self.total_living_area
        self.total_heating_per_m2 = self.heating_demand_per_m2 + self.hot_water_demand_per_m2
        self.cooling_demand_profile: np.ndarray = abs(r5c1_model.cooling_demand_profile / 1000)  # from Wh to kWh
        self.cooling_demand = self.cooling_demand_profile.sum()
        self.cooling_demand_peak = self.cooling_demand_profile.max()
        self.cooling_demand_per_m2 = self.cooling_demand / self.total_living_area


    """
    Calculate final energy demand
    """

    def init_final_energy_demand(self):
        self.final_energy_demand: dict = {}  # {key: id_end_use, value: [(id_energy_carrier, final_energy_demand)]}
        self.update_appliance_final_energy_demand()
        self.update_space_cooling_final_energy_demand()
        self.update_space_heating_final_energy_demand()
        self.update_hot_water_final_energy_demand()
        self.update_ventilation_final_energy_demand()

    def update_appliance_final_energy_demand(self):
        self.final_energy_demand[cons.ID_END_USE_APPLIANCE] = []
        df = self.scenario.s_end_use_demand_appliance_df
        energy_carrier_ids = df.loc[df["id_subsector"] == self.rkey.id_subsector]["id_energy_carrier"]
        rkey = self.rkey.make_copy()
        for id_energy_carrier in energy_carrier_ids:
            rkey.id_end_use = cons.ID_END_USE_APPLIANCE
            rkey.id_energy_carrier = id_energy_carrier
            self.final_energy_demand[cons.ID_END_USE_APPLIANCE].append(
                (
                    id_energy_carrier,
                    self.scenario.s_end_use_demand_appliance.get_item(rkey) * self.population
                )
            )

    def update_space_cooling_final_energy_demand(self):
        if self.cooling_system.is_adopted:
            self.final_energy_demand[cons.ID_END_USE_SPACE_COOLING] = [
                (
                    self.cooling_system.energy_intensity.id_energy_carrier,
                    self.cooling_system.energy_intensity.value * abs(self.cooling_demand)
                )
            ]
        else:
            self.final_energy_demand[cons.ID_END_USE_SPACE_COOLING] = []

    def update_space_heating_final_energy_demand(self):
        self.final_energy_demand[cons.ID_END_USE_SPACE_HEATING] = []
        for heating_technology in self.heating_system.heating_technologies:
            if heating_technology is not None:
                for energy_intensity in heating_technology.space_heating_energy_intensities:
                    self.final_energy_demand[energy_intensity.id_end_use].append(
                        (
                            energy_intensity.id_energy_carrier,
                            energy_intensity.value * self.heating_demand
                        )
                    )

    def update_hot_water_final_energy_demand(self):
        self.final_energy_demand[cons.ID_END_USE_HOT_WATER] = []
        for heating_technology in self.heating_system.heating_technologies:
            if heating_technology is not None:
                for energy_intensity in heating_technology.hot_water_energy_intensities:
                    self.final_energy_demand[energy_intensity.id_end_use].append(
                        (
                            energy_intensity.id_energy_carrier,
                            energy_intensity.value * self.hot_water_demand
                        )
                    )

    def update_ventilation_final_energy_demand(self):
        if self.ventilation_system.is_adopted:
            self.final_energy_demand[cons.ID_END_USE_VENTILATION] = [
                (
                    self.ventilation_system.energy_intensity.id_energy_carrier,
                    self.total_living_area * self.ventilation_system.energy_intensity.value
                )
            ]
        else:
            self.final_energy_demand[cons.ID_END_USE_VENTILATION] = []

    """
    Calculate total energy cost
    """

    def update_total_energy_cost(self):
        self.total_energy_cost = 0
        for _, end_use_energy_intensities in self.final_energy_demand.items():
            for id_energy_carrier, final_energy_demand in end_use_energy_intensities:
                rkey = self.rkey.make_copy().set_id({"id_energy_carrier": id_energy_carrier})
                self.total_energy_cost += final_energy_demand * self.scenario.s_final_energy_carrier_price.get_item(rkey)

    def update_heating_system_renewable_percentage(self):
        self.heating_system_renewable_percentage = 0
        renewable_demand = 0
        non_renewable_demand = 0
        for id_energy_carrier, energy_demand in self.final_energy_demand[cons.ID_END_USE_HOT_WATER]:
            if id_energy_carrier in cons.ID_ENERGY_CARRIER_RENEWABLES:
                renewable_demand += energy_demand
            else:
                non_renewable_demand += energy_demand
        for id_energy_carrier, energy_demand in self.final_energy_demand[cons.ID_END_USE_SPACE_HEATING]:
            if id_energy_carrier in cons.ID_ENERGY_CARRIER_RENEWABLES:
                renewable_demand += energy_demand
            else:
                non_renewable_demand += energy_demand
        self.heating_system_renewable_percentage = renewable_demand / (renewable_demand + non_renewable_demand)

    def update_final_energy_demand_and_cost(self):
        self.calc_building_heating_cooling_demand()
        self.update_appliance_final_energy_demand()
        self.update_space_cooling_final_energy_demand()
        self.update_space_heating_final_energy_demand()
        self.update_hot_water_final_energy_demand()
        self.update_ventilation_final_energy_demand()
        self.update_total_energy_cost()
        self.update_heating_system_renewable_percentage()

    """
    Future projection functions
    """

    def select_component(self, component_name: str):
        building_component = self.building_components[component_name]
        before_renovation_status = {
            "id_building_efficiency_class_before": self.rkey.id_building_efficiency_class,
            "id_building_component_option_before": building_component.rkey.id_building_component_option,
            "id_building_component_option_efficiency_class_before": building_component.rkey.id_building_component_option_efficiency_class,
            "heating_demand_before": self.heating_demand,
            "heating_demand_per_m2_before": self.heating_demand_per_m2,
            "cooling_demand_before": self.cooling_demand,
            "cooling_demand_per_m2_before": self.cooling_demand_per_m2,
            "total_energy_cost_before": self.total_energy_cost,
            "component_area": building_component.area
        }
        d_option_cost = {}
        for id_building_action in [cons.ID_BUILDING_ACTION_CONVENTIONAL_RENOVATION, cons.ID_BUILDING_ACTION_SERIAL_RENOVATION]:
            rkey = building_component.rkey.make_copy().set_id({"id_building_action": id_building_action})
            for id_building_component_option_efficiency_class in self.scenario.building_component_option_efficiency_classes.keys():
                rkey.id_building_component_option_efficiency_class = id_building_component_option_efficiency_class
                if self.scenario.s_building_component_availability.get_item(rkey):
                    capex = (
                            self.scenario.building_component_capex.get_item(rkey) *
                            building_component.area *
                            (1 - self.scenario.s_subsidy_building_renovation.get_item(rkey))
                    )
                    self.renovate_component(
                        component_name=component_name,
                        id_building_component_option_efficiency_class=id_building_component_option_efficiency_class
                    )
                    energy_cost_saving = (before_renovation_status["total_energy_cost_before"] - self.total_energy_cost)
                    d_option_cost[(id_building_action, id_building_component_option_efficiency_class)] = capex - energy_cost_saving
        id_building_action, id_building_component_option_efficiency_class = dict_utility_sample(
            options=dict_normalize(d_option_cost),
            utility_power=self.scenario.s_building_component_utility_power.get_item(rkey)
        )
        return before_renovation_status, id_building_action, id_building_component_option_efficiency_class

    def renovate_component(
            self,
            component_name: str,
            id_building_component_option_efficiency_class: int
    ):
        self.building_components[component_name].renovate(id_building_component_option_efficiency_class=id_building_component_option_efficiency_class)
        self.calc_building_heating_cooling_demand()
        self.update_space_cooling_final_energy_demand()
        self.update_space_heating_final_energy_demand()
        self.update_total_energy_cost()
        self.update_heating_system_renewable_percentage()

    def update_heating_technology(
            self,
            heating_technology: "HeatingTechnology",
            reason: str,
            limit_to: Optional[List[str]] = None
    ):
        self.update_final_energy_demand_and_cost()
        total_energy_cost_before = self.total_energy_cost
        heating_system_renewable_percentage_before = self.heating_system_renewable_percentage
        heating_technology.update_optional_heating_technologies(
            district_heating_available=self.heating_system.district_heating_available,
            gas_available=self.heating_system.gas_available,
            hydrogen_available=self.heating_system.hydrogen_available,
            limit_to=limit_to
        )
        option_action_info = heating_technology.select(
            heating_demand_profile=self.heating_demand_profile,
            hot_water_profile=self.hot_water_profile,
            reason=reason
        )
        heating_technology.install()
        self.update_space_heating_final_energy_demand()
        self.update_hot_water_final_energy_demand()
        self.update_total_energy_cost()
        self.update_heating_system_renewable_percentage()
        option_action_info["total_heating_demand_peak"] = self.total_heating_demand_peak
        option_action_info["id_heating_technology_after"] = heating_technology.rkey.id_heating_technology
        option_action_info["heating_system_renewable_percentage_before"] = heating_system_renewable_percentage_before
        option_action_info["heating_system_renewable_percentage_after"] = self.heating_system_renewable_percentage
        option_action_info["total_energy_cost_before"] = total_energy_cost_before
        option_action_info["total_energy_cost_after"] = self.total_energy_cost
        option_action_info["building_number"] = self.building_number
        self.scenario.heating_system_action_info.append(option_action_info)











    """
    code not used (should check if unnecessary data exists due to this part)
    """
    def conduct_sync_renovation(self, trigger_type: str, trigger_id: str or int, action_year: int):
        # We don't consider sync_renovation in initialization but in future projection.
        sync_renovation_actions = self.get_sync_renovation_actions(trigger_type, trigger_id)
        for col, action in sync_renovation_actions.items():
            if col.startswith("building_component") and action == 1:
                id_building_component = int(col.split("_")[-1])
                for component in self.building_components.values():
                    if component.rkey.id_building_component == id_building_component:
                        component.init_historical_renovation(action_year=action_year)

    def get_sync_renovation_actions(self, trigger_type: str, trigger_id: str or int):
        col = f'{trigger_type}_{trigger_id}'
        df = self.scenario.p_renovation_sync_probability.loc[self.scenario.p_renovation_sync_probability[col] == 1]
        d1 = {}
        d2 = {}
        for index, row in df.iterrows():
            sync_renovation_actions = row.to_dict()
            del sync_renovation_actions[col]
            del sync_renovation_actions["total_renovation"]
            del sync_renovation_actions["prob"]
            d1[index] = row["prob"]
            d2[index] = sync_renovation_actions
        return d2[dict_sample(d1)]

