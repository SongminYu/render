from typing import TYPE_CHECKING, Optional

import numpy as np
from Melodie import Agent

if TYPE_CHECKING:
    from models.render_building.scenario import BuildingScenario


def create_empty_arr():
    return np.zeros((8760, ))


class Building(Agent):
    scenario: "BuildingScenario"
    ...
