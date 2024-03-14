import random
from typing import Dict
from typing import List
from typing import Optional
from typing import TYPE_CHECKING
from typing import Tuple

from models.render.render_dict import RenderDict
from models.render_building.building_key import BuildingKey
from utils.funcs import dict_sample

if TYPE_CHECKING:
    from models.render_building.scenario import BuildingScenario


class HeatingSystem:

    def __init__(self, rkey: "BuildingKey", scenario: "BuildingScenario"):
        self.rkey = rkey
        self.scenario = scenario
        self.heating_technology_main: Optional["HeatingTechnology"] = None
        self.heating_technology_second: Optional["HeatingTechnology"] = None
        self.energy_intensity: Dict[Tuple[int, int], float] = {}

    def init_option(self):
        self.rkey.init_dimension(
            dimension_name="id_heating_system",
            dimension_ids=self.scenario.r_sector_heating_system.get_item(self.rkey),
            rdict=self.scenario.s_heating_system
        )

    def init_heating_technology_main(self):
        self.heating_technology_main = HeatingTechnology(self.rkey.make_copy(), self.scenario)
        self.heating_technology_main.init_option()
        self.heating_technology_main.init_installation_year()
        self.heating_technology_main.init_energy_carrier()

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
            id_heating_technology_second = dict_sample(second_technologies)
            rkey = self.rkey.make_copy().set_id({"id_heating_technology": id_heating_technology_second})
            # init second heating technology
            self.heating_technology_second = HeatingTechnology(rkey, self.scenario)
            self.heating_technology_second.init_installation_year()
            self.heating_technology_second.init_energy_carrier()
            self.heating_technology_second.space_heating_contribution = self.scenario.p_heating_technology_second_contribution_space_heating.get_item(rkey)
            self.heating_technology_second.hot_water_contribution = self.scenario.p_heating_technology_second_contribution_hot_water.get_item(rkey)
            # update main heating technology
            self.heating_technology_main.space_heating_contribution = 1 - self.scenario.p_heating_technology_second_contribution_space_heating.get_item(rkey)
            self.heating_technology_main.hot_water_contribution = 1 - self.scenario.p_heating_technology_second_contribution_hot_water.get_item(rkey)

    def update_energy_intensity(self):

        self.energy_intensity = RenderDict.create_empty_rdict(
            key_cols=[
                "id_heating_technology",
                "id_energy_carrier",
                "id_end_use"
            ]
        )
        # TODO: the energy intensity maybe not saved as tdict but aligned with other end-uses
        for heating_technology in [self.heating_technology_main, self.heating_technology_second]:
            if heating_technology is not None:
                for energy_carrier in heating_technology.energy_carriers:
                    rkey = energy_carrier.rkey.make_copy()
                    self.energy_intensity.set_item(
                        rkey.set_id({"id_end_use": 3}),
                        heating_technology.space_heating_contribution * (1 / energy_carrier.efficiency)
                    )
                    self.energy_intensity.set_item(
                        rkey.set_id({"id_end_use": 4}),
                        heating_technology.hot_water_contribution * (1 / energy_carrier.efficiency)
                    )

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
        self.energy_carriers: List["HeatingTechnologyEnergyCarrier"] = []
        self.space_heating_contribution = 1
        self.hot_water_contribution = 1

    def init_option(self, id_heating_technology: Optional[int] = None):
        if id_heating_technology is None:
            self.rkey.init_dimension(
                dimension_name="id_heating_technology",
                dimension_ids=self.scenario.r_heating_system_technology_main.get_item(self.rkey),
                rdict=self.scenario.s_heating_technology_main
            )
        else:
            self.rkey.id_heating_technology = id_heating_technology

    def get_lifetime(self):
        return random.randint(
            self.scenario.p_heating_technology_lifetime_min.get_item(self.rkey),
            self.scenario.p_heating_technology_lifetime_max.get_item(self.rkey)
        )

    def init_installation_year(self):
        lifetime = self.get_lifetime()
        age = random.randint(0, lifetime)
        self.installation_year = self.rkey.year - age
        self.next_replace_year = self.rkey.year + lifetime - age

    def init_energy_carrier(self):
        for id_energy_carrier in self.scenario.r_heating_technology_energy_carrier.get_item(self.rkey):
            rkey = self.rkey.make_copy()
            rkey.id_energy_carrier = id_energy_carrier
            energy_carrier = HeatingTechnologyEnergyCarrier(rkey=rkey, scenario=self.scenario)
            energy_carrier.set_efficiency(self.installation_year)
            self.energy_carriers.append(energy_carrier)


class HeatingTechnologyEnergyCarrier:

    def __init__(self, rkey: "BuildingKey", scenario: "BuildingScenario"):
        self.rkey = rkey
        self.scenario = scenario

    def set_efficiency(self, installation_year: int):
        rkey = self.rkey.make_copy()
        rkey.year = installation_year
        self.efficiency = self.scenario.s_heating_technology_efficiency.get_item(rkey)

