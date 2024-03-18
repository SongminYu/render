import math
from typing import List
from typing import Optional
from typing import TYPE_CHECKING
from typing import Union
import pandas as pd
from tab2dict import TabDict

if TYPE_CHECKING:
    from models.render.render_key import RenderKey

TabDictType = Union["ID", "Relation", "Data"]


class RenderDict(TabDict):

    def __init__(
        self,
        tdict_type: TabDictType,
        key_cols: List[str],
        tdict_data: dict,
        region_level: Optional[int] = None
    ):
        super().__init__(
            tdict_type=tdict_type,
            key_cols=key_cols,
            tdict_data=tdict_data
        )
        self.region_level = region_level

    def keys(self):
        if self.tdict_type in ["ID", "Relation"]:
            keys = [t[0] for t in self._data.keys()]
        else:
            keys = self._data.keys()
        return keys

    @classmethod
    def create_empty_rdict(cls, key_cols: List[str]):
        return cls.create_empty_data_tdict(key_cols)

    def _tkey2tuple_with_region_level_check(self, rkey: "RenderKey") -> tuple:

        def calc_region_level(id_region):
            return math.ceil(len(list(str(id_region))) / 2) - 1

        def convert_id_region(rkey_id_region: int):
            rkey_id_region_list = list(str(rkey_id_region))
            rkey_region_level = math.ceil(len(rkey_id_region_list) / 2) - 1
            return int("".join(rkey_id_region_list[:- 2 * (rkey_region_level - self.region_level)]))

        if (
            rkey.id_region is not None and
            self.region_level is not None and
            calc_region_level(rkey.id_region) > self.region_level
        ):
            key_list = []
            for col in self.key_cols:
                if col != "id_region":
                    key_list.append(int(rkey.__dict__[col]))
                else:
                    key_list.append(convert_id_region(int(rkey.__dict__[col])))
            key = tuple(key_list)
        else:
            key = tuple([int(rkey.__dict__[col]) for col in self.key_cols])
        return key

    def get_item(self, rkey: "RenderKey", not_found_default=None):
        key = self._tkey2tuple_with_region_level_check(rkey)
        if key in self._data.keys():
            value = self._data[key]
        else:
            if not_found_default is not None:
                value = not_found_default
            else:
                raise KeyError
        return value

    def set_item(self, rkey: "RenderKey", value):
        super().set_item(tkey=rkey, value=value)

    def accumulate_item(self, rkey: "RenderKey", value):
        super().accumulate_item(tkey=rkey, value=value)

    @classmethod
    def from_profile_dataframe(
            cls,
            df: pd.DataFrame,
            tdict_type: TabDictType,
        ):
        key_cols = [col for col in df.columns if col.startswith(("id_", "year"))]
        val_cols = [col for col in df.columns if not col.startswith(("id_", "year", "unit"))]
        tdict_data = {}
        for _, row in df.iterrows():
            key = []
            for key_col in key_cols:
                key.append(row[key_col])
            tdict_data[tuple(key)] = row.loc[val_cols].astype(float).to_numpy()
        return cls._construct_tdict(
            tdict_type=tdict_type,
            key_cols=key_cols,
            tdict_data=tdict_data
        )
