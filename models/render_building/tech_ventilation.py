import random
from typing import TYPE_CHECKING

from models.render_building.building_key import BuildingKey

if TYPE_CHECKING:
    from models.render_building.scenario import BuildingScenario


class VentilationSystem:

    def __init__(self, rkey: "BuildingKey", scenario: "BuildingScenario"):
        self.rkey = rkey
        self.scenario = scenario
        self.is_adopted = False
        self.energy_intensity = 0
        self.installation_year = ...
        self.next_replace_year = ...

    def adopt(self, adoption_prob: float):
        if not self.is_adopted:
            if random.uniform(0, 1) <= adoption_prob:
                self.is_adopted = True
                self.set_energy_intensity()
                self.installation_year = ...
                self.next_replace_year = ...

    def set_energy_intensity(self):
        self.energy_intensity = ...




