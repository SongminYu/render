import random
from typing import Optional
from typing import TYPE_CHECKING

from models.render_building.building_key import BuildingKey
from models.render_building.tech import EnergyIntensity
from utils.funcs import dict_sample

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
            if self.heating_technology_main.rkey.id_heating_technology in [11]:
                self.district_heating_available = True
                self.scenario.location_building_num_heating_tech_district_heating.accumulate_item(rkey=self.rkey, value=1)
            elif self.heating_technology_main.rkey.id_heating_technology in [21, 24, 26, 31, 41]:
                self.gas_available = True
                self.scenario.location_building_num_heating_tech_gas.accumulate_item(rkey=self.rkey, value=1)

        self.heating_technology_main = HeatingTechnology(self.rkey.make_copy(), self.scenario)
        self.heating_technology_main.init_option()
        self.heating_technology_main.init_supply_temperature()
        self.heating_technology_main.init_installation_year()
        self.heating_technology_main.update_energy_intensity()
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
            self.heating_technology_second = HeatingTechnology(rkey, self.scenario)
            self.heating_technology_second.init_supply_temperature()
            self.heating_technology_second.init_installation_year()
            self.heating_technology_second.space_heating_contribution = self.scenario.p_heating_technology_second_contribution_space_heating.get_item(rkey)
            self.heating_technology_second.hot_water_contribution = self.scenario.p_heating_technology_second_contribution_hot_water.get_item(rkey)
            self.heating_technology_second.update_energy_intensity()
            # update main heating technology
            self.heating_technology_main.space_heating_contribution = 1 - self.scenario.p_heating_technology_second_contribution_space_heating.get_item(rkey)
            self.heating_technology_main.hot_water_contribution = 1 - self.scenario.p_heating_technology_second_contribution_hot_water.get_item(rkey)
            self.heating_technology_main.update_energy_intensity()

    def update_heating_system(self):
        # triggered by some reasons, for example,
        # (1) main heating technology reaching lifetime,
        # (2) major renovation decision
        # ...
        # However, when triggered, the perspective is always "what should I do about my heating system, not technology".
        # So, all different *systems* with different configurations, incl. multiple technologies, should be compared.
        # Maybe, we need to pre-calculate a huge table: for any possible building.rkey, the costs of all possible heating systems.
        ...


class HeatingTechnology:

    def __init__(self, rkey: "BuildingKey", scenario: "BuildingScenario"):
        self.rkey = rkey
        self.scenario = scenario
        self.supply_temperature_space_heating = 0
        self.supply_temperature_hot_water = 0
        self.space_heating_contribution = 1
        self.hot_water_contribution = 1
        self.installation_year = 0
        self.next_replace_year = 0
        self.space_heating_energy_intensities = []
        self.hot_water_energy_intensities = []

    def init_option(self):
        if self.rkey.id_heating_technology is None:
            self.rkey.init_dimension(
                dimension_name="id_heating_technology",
                dimension_ids=self.scenario.r_heating_system_technology_main.get_item(self.rkey),
                rdict=self.scenario.s_heating_technology_main
            )

    def init_supply_temperature(self):
        self.supply_temperature_space_heating = self.scenario.p_building_supply_temperature_space_heating.get_item(self.rkey)
        self.supply_temperature_hot_water = self.scenario.p_building_supply_temperature_hot_water.get_item(self.rkey)

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

    def update_energy_intensity(self):

        def efficiency_adjustment_factor(supply_temperature):
            adjustment_parameter = self.scenario.p_heating_technology_supply_temperature_efficiency_adjustment.get_item(self.rkey)
            adjustment_factor = ...  # TODO: depending on supply_temperature
            return adjustment_factor

        self.space_heating_energy_intensities = []
        self.hot_water_energy_intensities = []
        for id_energy_carrier in self.scenario.r_heating_technology_energy_carrier.get_item(self.rkey):
            rkey = self.rkey.make_copy().set_id({"id_energy_carrier": id_energy_carrier, "year": self.installation_year})
            self.space_heating_energy_intensities.append(EnergyIntensity(
                id_end_use=3,
                id_energy_carrier=rkey.id_energy_carrier,
                # value=self.space_heating_contribution * (1 / (self.scenario.s_heating_technology_efficiency.get_item(rkey) * efficiency_adjustment_factor(self.supply_temperature_space_heating)))
                value=self.space_heating_contribution * (1 / self.scenario.s_heating_technology_efficiency.get_item(rkey))
            ))
            self.hot_water_energy_intensities.append(EnergyIntensity(
                id_end_use=4,
                id_energy_carrier=rkey.id_energy_carrier,
                # value=self.hot_water_contribution * (1 / (self.scenario.s_heating_technology_efficiency.get_item(rkey) * efficiency_adjustment_factor(self.supply_temperature_hot_water)))
                value=self.hot_water_contribution * (1 / self.scenario.s_heating_technology_efficiency.get_item(rkey))
            ))

    def update_due_to_radiator_change(self, id_radiator: int):
        self.rkey.id_radiator = id_radiator
        self.supply_temperature_space_heating = self.scenario.p_building_supply_temperature_space_heating.get_item(self.rkey)
        self.update_energy_intensity()
