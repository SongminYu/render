import random
from typing import TYPE_CHECKING, List, Optional

import numpy as np
from Melodie import Agent

from models.render_building.building_component import BuildingComponent
from models.render_building.building_key import BuildingKey
from models.render_building.building_r5c1 import R5C1, spec
from models.render_building.building_unit import Unit
from models.render_building.tech_cooling import CoolingSystem
from models.render_building.tech_heating import HeatingSystem
from models.render_building.tech_ventilation import VentilationSystem
from models.render_building.tech_radiator import Radiator
from utils.funcs import dict_sample

if TYPE_CHECKING:
    from models.render_building.scenario import BuildingScenario


def create_empty_arr():
    return np.zeros((8760, ))


class Building(Agent):
    scenario: "BuildingScenario"

    """
    Building initialization functions
    """

    def setup(self):
        self.id_region = 0
        self.id_sector = 0
        self.id_subsector = 0
        self.id_building_type = 0
        self.id_subsector_agent = 0

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

        self.name = f'R{self.id_region}S{self.id_subsector}B{self.id_building_type}N{self.id_subsector_agent}'

        self.rkey.init_dimension(
            dimension_name="id_building_construction_period",
            dimension_ids=self.scenario.building_construction_periods.keys(),
            rdict=self.scenario.s_building_construction_period
        )

        self.rkey.init_dimension(
            dimension_name="id_building_location",
            dimension_ids=self.scenario.building_locations.keys(),
            rdict=self.scenario.s_building_location
        )

        self.rkey.init_dimension(
            dimension_name="id_building_height",
            dimension_ids=self.scenario.r_building_type_height.get_item(self.rkey),
            rdict=self.scenario.s_building_height
        )

    def init_units(self):
        self.units: Optional[List[Unit]] = []
        self.population = 0
        self.unit_area = self.scenario.s_building_unit_area.get_item(self.rkey)
        self.unit_number = random.randint(self.scenario.p_building_unit_number_min.get_item(self.rkey),
                                          self.scenario.p_building_unit_number_max.get_item(self.rkey))
        for id_unit in range(0, self.unit_number):
            unit = Unit(self.rkey.make_copy(), self.scenario)
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

    def init_building_components_construction(self):
        self.building_components: Optional[List[BuildingComponent]] = []
        for id_building_component in self.scenario.building_components.keys():
            component = BuildingComponent(self.rkey.make_copy(), self.scenario)
            component.rkey.id_building_component = id_building_component
            component.init_name()
            component.init_option()
            component.init_area(
                ref_area=self.__dict__[self.scenario.p_building_envelope_component_area_ref.get_item(component.rkey)],
                ratio=self.scenario.p_building_envelope_component_area_ratio.get_item(component.rkey)
            )
            component.construct()
            self.building_components.append(component)

    def init_radiator(self):
        self.radiator = Radiator(self.rkey.make_copy(), self.scenario)
        self.radiator.init_option()
        self.radiator.init_installation_year()

    def init_building_cooling_system(self):
        self.cooling_system = CoolingSystem(self.rkey.make_copy(), self.scenario)
        if random.uniform(0, 1) <= self.scenario.s_cooling_penetration_rate.get_item(self.rkey):
            self.cooling_system.init_adoption()

        # for a percentage of buildings, cooling systems are initialized (id_end_use = 2)
        # (1) dwelling-based or building-based?
        # --> It can be mixed if the whole building has to be installed with cooling together or not.
        # --> Penetration modeling can be more complicated with dwelling-based approach (iterating through units not buildings)
        # --> Take data from FORECAST-Appliance, but FORECAST-Appliance takes a dwelling-based approach
        # --> adoption history needs to be developed
        # (2) technology modeling
        # --> air-conditioner (with different efficiency levels in the availability table)
        # --> id_cooling_technology, id_cooling_technology_efficiency_class

        # Residential
        # - Penetration curve is extracted from FORECAST-ResidentialAppliance (adoption probability of a building can be calculated based on the dwelling-based numbers)
        # - Technology availability table and efficiency/energy intensity of different efficiency levels (for modeling MEPS) will be developed based on FORECAST-ResidentialAppliance
        # Tertiary
        # - Penetration curve will be developed based on GHD-Befragung data
        # - Technology availability table and efficiency/energy intensity of different efficiency levels (for modeling MEPS) will be developed based on FORECAST-ResidentialAppliance

    def init_building_heating_system(self):
        self.heating_system = HeatingSystem(self.rkey.make_copy(), self.scenario)
        self.heating_system.init_system_type()
        self.heating_system.init_supply_temperature()
        self.heating_system.init_heating_technology_main()
        self.heating_system.init_heating_technology_second()
        self.heating_system.technologies = [
            self.heating_system.heating_technology_main,
            self.heating_system.heating_technology_second
        ]

    def init_building_ventilation_system(self):
        self.ventilation_system = VentilationSystem(self.rkey.make_copy(), self.scenario)
        if random.uniform(0, 1) <= self.scenario.s_ventilation_penetration_rate.get_item(self.rkey):
            self.ventilation_system.init_adoption()

    def init_building_renovation_history(self):
        for component in self.building_components:
            while component.next_replace_year < self.rkey.year:
                if random.uniform(0, 1) <= 0.70:
                    action_year = component.next_replace_year
                    component.renovate(action_year=action_year)
                else:
                    break

    def init_building_heating_cooling_demand(self):

        def init_building_efficiency_class():
            self.update_building_rc_params()
            self.update_building_rc_temperature()
            self.update_building_heating_cooling_demand()
            self.heating_demand_norm = self.heating_demand_profile.sum()
            self.heating_demand_per_m2_norm = self.heating_demand_norm / self.total_living_area
            self.total_heating_per_m2_norm = self.heating_demand_per_m2_norm + self.hot_water_demand_per_m2
            self.update_building_efficiency_class()

        init_building_efficiency_class()
        self.update_building_rc_temperature()
        self.update_building_heating_cooling_demand()

    """
    5R1C model - ISO13790
    """

    def update_building_rc_params(self):

        def get_building_component(component_name: str):
            building_component: Optional["BuildingComponent"] = None
            for component in self.building_components:
                if component.name == component_name:
                    building_component = component
                    break
            return building_component

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
        window = get_building_component("window")
        self.h_tr_w = window.area * window.u_value  # W/K

        # h_tr_op --> heat transfer coefficient of opaque elements to external air (equation 18)
        b_tr_wall = 1  # adjustment factor
        b_tr_roof = 1  # adjustment factor
        b_tr_basement = 0.5  # adjustment factor
        wall = get_building_component("wall")
        roof = get_building_component("roof")
        basement = get_building_component("basement")
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
        q_ve_inf = get_infiltration_param(
            window.rkey.id_building_component_option_efficiency_class)  # air flow rate due to infiltration (unit: 1/hour)
        q_ve_ven = 0.4  # air flow rate due to ventilation (unit: 1/hour)
        h = 2.5  # height per storey (unit: m)
        self.h_vent_adj = pho_a_c * b_ve_k * \
                          (q_ve_inf + q_ve_ven) * self.total_living_area * h

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
        self.internal_gain_occ = phi_occ * \
                                 self.occupancy_profile * self.population

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
            component = get_building_component(component_name)
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
            outside_temperature = self.scenario.pr_weather_temperature.get_item(self.rkey)
            # external radiant heat transfer coefficient
            h_r = 4 * epsilon * sigma * ((outside_temperature + 273.15) ** 3)
            component = get_building_component(component_name)
            return component.area * component.u_value * resistance_coefficient * temp_diff * form_param[
                component_name] * h_r

        total_radiation = create_empty_arr()
        rkey = self.rkey.make_copy()
        for id_orientation in self.scenario.orientations.keys():
            rkey.id_orientation = id_orientation
            total_radiation += self.scenario.pr_weather_radiation.get_item(rkey)

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
                                   self.scenario.pr_weather_radiation.get_item(rkey) * \
                                   self.scenario.p_building_envelope_window_area_orientation.get_item(rkey)

        # gains in total
        self.internal_gain = self.internal_gain_occ + self.internal_gain_app
        self.solar_gain = self.solar_gain_opa + self.solar_gain_gla

    def update_building_rc_temperature(self):
        self.weather_temperature = self.scenario.pr_weather_temperature.get_item(self.rkey)
        if self.rkey.id_building_efficiency_class is None:
            self.set_temperature_min = np.ones((8760,)) * 20
            self.set_temperature_max = np.ones((8760,)) * 27
        else:
            occupied_min = self.scenario.p_set_temperature_occupied_min.get_item(self.rkey)
            occupied_max = self.scenario.p_set_temperature_occupied_max.get_item(self.rkey)
            empty_min = self.scenario.p_set_temperature_empty_min.get_item(self.rkey)
            empty_max = self.scenario.p_set_temperature_empty_max.get_item(self.rkey)
            self.set_temperature_min = np.ones((8760,))
            self.set_temperature_max = np.ones((8760,))
            # update set_temperature based on occupancy
            for hour in range(0, 8760):
                if random.uniform(0, 1) < self.scenario.optimal_heating_behavior_prob:
                    self.set_temperature_min[hour] = empty_min + (occupied_min - empty_min) * self.occupancy_profile[hour]
                    self.set_temperature_max[hour] = empty_max - (empty_max - occupied_max) * self.occupancy_profile[hour]
                else:
                    self.set_temperature_min[hour] = occupied_min
                    self.set_temperature_max[hour] = occupied_max

    def update_building_heating_cooling_demand(self):

        def inherit_params(empty_r5c1_model: "R5C1"):
            for attribute, _ in spec:
                if hasattr(self, attribute):
                    setattr(empty_r5c1_model, attribute, getattr(self, attribute))
            return empty_r5c1_model

        r5c1_model = inherit_params(R5C1())
        r5c1_model.update_building_heating_cooling_demand()
        self.heating_demand_profile: np.ndarray = r5c1_model.heating_demand_profile / 1000  # from Wh to kWh
        self.heating_demand = self.heating_demand_profile.sum()
        self.heating_demand_per_m2 = self.heating_demand / self.total_living_area
        self.total_heating_per_m2 = self.heating_demand_per_m2 + self.hot_water_demand_per_m2
        self.cooling_demand_profile: np.ndarray = abs(r5c1_model.cooling_demand_profile / 1000)  # from Wh to kWh
        self.cooling_demand = self.cooling_demand_profile.sum()
        self.cooling_demand_per_m2 = self.cooling_demand / self.total_living_area

        # for memory efficiency, the three profiles below are commented out:
        # self.temp_mass_profile: np.ndarray = r5c1_model.temp_mass_profile
        # self.temp_surface_profile: np.ndarray = r5c1_model.temp_surface_profile
        # self.temp_air_profile: np.ndarray = r5c1_model.temp_air_profile

    def update_building_efficiency_class(self):
        for _, row in self.scenario.p_building_efficiency_class_intensity.iterrows():
            if row["min"] <= self.total_heating_per_m2 <= row["max"]:
                self.rkey.id_building_efficiency_class = row["id_building_efficiency_class"]
                break

    """
    Calculate final energy demand
    """

    def init_final_energy_demand(self):

        self.final_energy_demand: dict = {}  # {key: id_end_use, value: [(id_energy_carrier, final_energy_demand)]}
        self.update_appliance_electricity_final_energy_demand()
        self.update_space_cooling_final_energy_demand()
        self.update_space_heating_final_energy_demand()
        self.update_hot_water_final_energy_demand()
        self.update_ventilation_final_energy_demand()

    def update_appliance_electricity_final_energy_demand(self):
        self.final_energy_demand[1] = [
            (1, self.appliance_electricity_profile.sum())
        ]

    def update_space_cooling_final_energy_demand(self):
        if self.cooling_system.is_adopted:
            self.final_energy_demand[2] = [
                (
                    self.cooling_system.energy_intensity.id_energy_carrier,
                    self.cooling_system.energy_intensity.value * abs(self.cooling_demand_profile.sum())
                )
            ]
        else:
            self.final_energy_demand[2] = []

    def update_space_heating_final_energy_demand(self):
        self.final_energy_demand[3] = []
        for heating_technology in self.heating_system.technologies:
            if heating_technology is not None:
                for energy_intensity in heating_technology.space_heating_energy_intensities:
                    self.final_energy_demand[energy_intensity.id_end_use].append(
                        (
                            energy_intensity.id_energy_carrier,
                            energy_intensity.value * self.heating_demand_profile.sum()
                        )
                    )

    def update_hot_water_final_energy_demand(self):
        self.final_energy_demand[4] = []
        for heating_technology in self.heating_system.technologies:
            if heating_technology is not None:
                for energy_intensity in heating_technology.hot_water_energy_intensities:
                    self.final_energy_demand[energy_intensity.id_end_use].append(
                        (
                            energy_intensity.id_energy_carrier,
                            energy_intensity.value * self.hot_water_profile.sum()
                        )
                    )

    def update_ventilation_final_energy_demand(self):
        if self.ventilation_system.is_adopted:
            self.final_energy_demand[5] = [
                (
                    self.ventilation_system.energy_intensity.id_energy_carrier,
                    self.total_living_area * self.ventilation_system.energy_intensity.value
                )
            ]
        else:
            self.final_energy_demand[5] = []

    """
    Future projection functions
    """

    def conduct_sync_renovation(self, trigger_type: str, trigger_id: str or int, action_year: int):
        # TODO: We don't consider sync_renovation in initialization but in future projection.
        sync_renovation_actions = self.get_sync_renovation_actions(trigger_type, trigger_id)
        for col, action in sync_renovation_actions.items():
            if col.startswith("building_component") and action == 1:
                id_building_component = int(col.split("_")[-1])
                for component in self.building_components:
                    if component.rkey.id_building_component == id_building_component:
                        component.renovate(action_year=action_year)

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

