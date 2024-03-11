from typing import Optional

from tab2dict import TabKey


class RenderKey(TabKey):

    def __init__(
            self,
            id_scenario: Optional[int] = None,
            id_region: Optional[int] = None,
            id_sector: Optional[int] = None,
            id_subsector: Optional[int] = None,
            id_subsector_agent: Optional[int] = None,
            id_energy_carrier: Optional[int] = None,
            year: Optional[int] = None,
    ):
        self.id_scenario = id_scenario
        self.id_region = id_region
        self.id_sector = id_sector
        self.id_subsector = id_subsector
        self.id_subsector_agent = id_subsector_agent
        self.id_energy_carrier = id_energy_carrier
        self.year = year
