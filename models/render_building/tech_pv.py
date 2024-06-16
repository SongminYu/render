from typing import TYPE_CHECKING

import numpy as np

from models.render_building.building_key import BuildingKey

if TYPE_CHECKING:
    from models.render_building.scenario import BuildingScenario


class PhotovoltaicSystem:

    def __init__(self, rkey: "BuildingKey", scenario: "BuildingScenario"):
        self.rkey = rkey
        self.scenario = scenario
        self.is_adopted = False
        self.installation_year = 0
        self.next_replace_year = 0

    def init_adoption(self, roof_area: float, generation_profile: np.ndarray):
        self.is_adopted = True
        self.size = roof_area * 0.12  # 0.12kWp per square meter (source: https://www.comparemysolar.co.uk/learn-about-solar/solar-education/your-own-roof/)
        self.generation = generation_profile.sum() * self.size / 1000  # Wh --> kWh
        self.self_consumption_rate = self.scenario.s_pv_self_consumption_rate.get_item(self.rkey)  # could be used to reflect SEMS
        self.self_consumption = self.generation * self.self_consumption_rate
        self.pv2grid = self.generation - self.self_consumption  # TODO: loss needs to be considered?





