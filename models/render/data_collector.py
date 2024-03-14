from typing import TYPE_CHECKING
from Melodie import DataCollector

if TYPE_CHECKING:
    from models.render.scenario import RenderScenario


class RenderDataCollector(DataCollector):
    scenario: "RenderScenario"

