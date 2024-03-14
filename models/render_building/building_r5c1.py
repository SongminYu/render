import numpy as np
from numba import njit, float32, float64, int64
from numba.experimental import jitclass


@njit
def create_empty_arr():
    return np.zeros((8760, ))


spec = [
    ('a_m', float64),
    ('a_is', float64),
    ('phi_m', float64),
    ('phi_st', float64),
    ('phi_ia', float64),
    ('h_tr_em', float64),
    ('h_tr_1', float64),
    ('h_tr_2', float64),
    ('h_tr_3', float64),
    ('h_tr_w', float64),
    ('h_tr_op', float64),
    ('h_tr_ms', float64),
    ('h_tr_is', float64),
    ('h_vent_adj', float64),
    ('phi_hc_nd', float64),
    ('t_ext', float64),
    ('phi_m_tot', float64),
    ("building_occupancy_profile", float64[:]),
    ("building_appliance_electricity_profile", float64[:]),
    ("building_hot_water_profile", float64[:]),
    ("height", int64),
    ("total_living_area", int64),
    ("height", int64),
    ("internal_gain", float64[:]),
    ("weather_temperature", float64[:]),
    ("set_temperature_max", float64[:]),
    ("set_temperature_min", float64[:]),
    ("heating_demand_profile", float64[:]),
    ("cooling_demand_profile", float64[:]),
    ("temp_mass_profile", float64[:]),
    ("temp_surface_profile", float64[:]),
    ("temp_air_profile", float64[:]),
    ("temp_mass_next", float64),
    ("temp_mass", float64),
    ("solar_gain", float64[:]),
    ("temp_air", float64),
    ("temp_surface", float64),
    ("c_m", float64),
]


@jitclass(spec)
class R5C1:

    def __init__(self):
        self.temp_mass_next = 0.0

    def heat_flow(self, hour):
        # heat flow to the air node - Equation C1
        self.phi_ia = 0.5 * self.internal_gain[hour]
        # heat flow to the thermal mass node - Equation C2
        self.phi_m = (self.a_m / self.a_is) * \
            ((0.5 * self.internal_gain[hour]) + self.solar_gain[hour])
        # heat flow to the surface node - Equation C3
        self.phi_st = (1 - (self.a_m / self.a_is) - (self.h_tr_w / (9.1 * self.a_is))) * \
                      ((0.5 * self.internal_gain[hour]) + self.solar_gain[hour])

    def calc_phi_m_tot(self, hour, phi_hc_nd):
        # Equation 5 from Annex C of ISO 13790:2008 P.114
        t_ext = self.weather_temperature[hour]
        self.phi_m_tot = self.phi_m + (t_ext * self.h_tr_em) + self.h_tr_3 * \
            (
            self.phi_st + (self.h_tr_w * t_ext) +
            self.h_tr_1 * (((self.phi_ia + phi_hc_nd) / self.h_vent_adj) + t_ext)
        ) / self.h_tr_2

    def calc_temp_mass_next(self, temp_mass_prev):
        self.temp_mass_next = (temp_mass_prev * (self.c_m - 0.5 * (self.h_tr_3 + self.h_tr_em)) + self.phi_m_tot) / \
                              (self.c_m + (0.5 * (self.h_tr_3 + self.h_tr_em)))

    def calc_temp_mass(self, temp_mass_prev):
        # Equation 9 from Annex C of ISO 13790:2008 P.114
        # average between the new next temperature and the previous temperature
        self.temp_mass = (self.temp_mass_next + temp_mass_prev) / 2

    def calc_temp_surface(self, hour, phi_hc_nd):
        # Equation 10 from Annex C of ISO 13790:2008 P.114
        # the average temperature value at the surface node
        t_ext = self.weather_temperature[hour]
        self.temp_surface = (
            (self.h_tr_ms * self.temp_mass) +
            self.phi_st + (self.h_tr_w * t_ext) +
            self.h_tr_1 * (t_ext + ((self.phi_ia + phi_hc_nd) / self.h_vent_adj))
        ) / (self.h_tr_ms + self.h_tr_w + self.h_tr_1)

    def calc_temp_air(self, hour, phi_hc_nd):
        # Equation 11 from Annex C of ISO 13790:2008 P.115
        # average temperature of the air inside the building
        t_ext = self.weather_temperature[hour]
        self.temp_air = (
            self.h_tr_is * self.temp_surface +
            self.h_vent_adj * t_ext +
            self.phi_ia + phi_hc_nd
        ) / (self.h_tr_is + self.h_vent_adj)

    def calc_crank_nicholson(self, hour, phi_hc_nd, temp_mass_prev):
        """
        Calculates the temp_air, temp_mass, temp_surface for each hour
        """
        self.heat_flow(hour)
        self.calc_phi_m_tot(hour, phi_hc_nd)
        self.calc_temp_mass_next(temp_mass_prev)
        self.calc_temp_mass(temp_mass_prev)
        self.calc_temp_surface(hour, phi_hc_nd)
        self.calc_temp_air(hour, phi_hc_nd)
        return self.temp_air, self.temp_surface, self.temp_mass

    def update_building_heating_cooling_demand(self):
        self.heating_demand_profile: np.ndarray = create_empty_arr()
        self.cooling_demand_profile: np.ndarray = create_empty_arr()
        self.temp_mass_profile: np.ndarray = create_empty_arr()
        self.temp_surface_profile: np.ndarray = create_empty_arr()
        self.temp_air_profile: np.ndarray = create_empty_arr()
        TEMP_MASS_PREV_START = 20.0
        for hour in range(0, 8760):
            temp_cooling = self.set_temperature_max[hour]
            temp_heating = self.set_temperature_min[hour]
            temp_mass_prev = TEMP_MASS_PREV_START if hour == 0 else self.temp_mass_next
            temp_air_start, temp_surface_start, temp_mass_start = self.calc_crank_nicholson(
                hour, 0, temp_mass_prev)
            if temp_air_start < temp_heating:
                phi_hc_nd = 10 * self.total_living_area
                temp_air_heated, temp_surface_heated, temp_mass_heated = self.calc_crank_nicholson(
                    hour, phi_hc_nd, temp_mass_prev)
                self.heating_demand_profile[hour] = phi_hc_nd * (
                    temp_heating - temp_air_start) / (temp_air_heated - temp_air_start)
                self.cooling_demand_profile[hour] = 0
                self.temp_air_profile[hour], self.temp_surface_profile[hour], self.temp_mass_profile[hour] = \
                    self.calc_crank_nicholson(hour, self.heating_demand_profile[hour], temp_mass_prev)
            elif temp_heating <= temp_air_start <= temp_cooling:
                self.heating_demand_profile[hour] = 0
                self.cooling_demand_profile[hour] = 0
                self.temp_air_profile[hour] = temp_air_start
                self.temp_surface_profile[hour] = temp_surface_start
                self.temp_mass_profile[hour] = temp_mass_start
            else:
                phi_hc_nd = 10 * self.total_living_area
                temp_air_cooled, temp_surface_cooled, temp_mass_cooled = self.calc_crank_nicholson(
                    hour, phi_hc_nd, temp_mass_prev)
                self.heating_demand_profile[hour] = 0
                self.cooling_demand_profile[hour] = phi_hc_nd * \
                                                    (temp_cooling - temp_air_start) / \
                                                    (temp_air_cooled - temp_air_start)
                self.temp_air_profile[hour], self.temp_surface_profile[hour], self.temp_mass_profile[hour] = \
                    self.calc_crank_nicholson(hour, self.cooling_demand_profile[hour], temp_mass_prev)
        return self

