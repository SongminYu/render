from typing import Dict
from typing import List
from typing import Optional

from tab2dict import TabKey

from models.render.render_dict import RenderDict
from utils.funcs import dict_sample


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

    def __str__(self):
        d = {}
        for key_col in self.key_cols:
            d[key_col] = self.__dict__[key_col]
        return f"<RenderKey{d}>"

    def set_id(self, id_values: Dict[str, int]):
        for id_name, id_value in id_values.items():
            self.__dict__[id_name] = id_value
        return self

    def init_dimension(self, dimension_name: str, dimension_ids: List[int], rdict: "RenderDict"):
        d = {}
        for dimension_id in dimension_ids:
            self.__dict__[dimension_name] = dimension_id
            d[dimension_id] = rdict.get_item(self)
        self.__dict__[dimension_name] = dict_sample(d)

    def to_dict(self):
        d = {}
        for key, value in self.__dict__.items():
            if key.startswith("id") or key.startswith("year"):
                if value is not None:
                    d[key] = value
        return d
