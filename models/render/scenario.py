from typing import Optional, Dict

from Melodie import Scenario
import pandas as pd
from models.render.render_dict import RenderDict
from models.render.render_key import RenderKey
from utils.logger import get_logger
from utils.decorators import load_timer

log = get_logger(__name__)


class RenderScenario(Scenario):
    start_year: int
    end_year: int

    @load_timer()
    def load_id(self, file_name: str, id_filter: Optional[dict] = None) -> RenderDict:
        df = self.load_dataframe(file_name)
        if id_filter is not None:
            for column, value in id_filter.items():
                df = df.loc[df[column] == value]
        return RenderDict.from_dataframe(
            tdict_type="ID",
            df=df
        )

    @load_timer()
    def load_relation(self, file_name: str) -> RenderDict:
        return RenderDict.from_dataframe(
            tdict_type="Relation",
            df=self.load_dataframe(file_name)
        )

    @load_timer()
    def load_param(
            self,
            file_name: str,
            col: Optional[str] = "value",
            region_level: Optional[int] = None
    ) -> RenderDict:
        rdict = RenderDict.from_dataframe(
            tdict_type="Data",
            df=self.load_dataframe(file_name),
            value_column_name=col
        )
        if region_level is not None:
            rdict.region_level = region_level
        return rdict

    @load_timer()
    def load_scenario(
            self,
            file_name: str,
            scenario_filter: Optional[str] = None,
            all_years: Optional[bool] = False,
            region_level: Optional[int] = None,
    ) -> RenderDict:
        df = self.load_dataframe(file_name)
        if scenario_filter is not None:
            df = df.loc[df["id_scenario"] == self.__dict__[scenario_filter]]
            df.loc[:, "id_scenario"] = self.id
        else:
            if "id_scenario" in df.columns:
                df = df.loc[df["id_scenario"] == df["id_scenario"].unique()[0]]
                df.loc[:, "id_scenario"] = self.id
        if not all_years:
            df_index_cols = df[[col for col in df.columns if col.startswith(("id_", "unit"))]]
            df_data_cols = df.loc[:, str(self.start_year):str(min(self.end_year, int(df.columns[-1])))]
            df = pd.concat([df_index_cols, df_data_cols], axis=1)
        rdict = RenderDict.from_dataframe(
            tdict_type="Data",
            df=df,
            time_column_name="year",
        )
        if region_level is not None:
            rdict.region_level = region_level
        return rdict

    def load_profile(
            self,
            file_name: str,
            scenario_filter: Optional[str] = None,
            region_level: Optional[int] = None,
    ) -> RenderDict:
        df = self.load_dataframe(file_name)
        if scenario_filter is not None:
            df = df.loc[df["id_scenario"] == self.__dict__[scenario_filter]]
            df.loc[:, "id_scenario"] = self.id
        else:
            if "id_scenario" in df.columns:
                df = df.loc[df["id_scenario"] == df["id_scenario"].unique()[0]]
                df.loc[:, "id_scenario"] = self.id
        rdict = RenderDict.from_profile_dataframe(
            tdict_type="Data",
            df=df
        )
        if region_level is not None:
            rdict.region_level = region_level
        return rdict

    def load_framework(self):
        self.regions = self.load_id("ID_Region.xlsx", id_filter={"region_level": 3})
        self.sectors = self.load_id("ID_Sector.xlsx")
        self.subsectors = self.load_id("ID_SubSector.xlsx")
        self.energy_carriers = self.load_id("ID_EnergyCarrier.xlsx")
        self.r_sector_subsector = self.load_relation("Relation_Sector_SubSector.xlsx")
        self.s_emission_factor = self.load_scenario("Scenario_EnergyCarrier_EmissionFactor.xlsx", scenario_filter="id_scenario_energy_emission_factor")
        self.s_energy_carrier_price_wholesale = self.load_scenario("Scenario_EnergyCarrier_Price_Wholesale.xlsx", scenario_filter="id_scenario_energy_price_wholesale")
        self.s_energy_carrier_price_tax_rate = self.load_scenario("Scenario_EnergyCarrier_Price_TaxRate.xlsx", scenario_filter="id_scenario_energy_price_tax_rate")
        self.s_energy_carrier_price_markup = self.load_scenario("Scenario_EnergyCarrier_Price_MarkUp.xlsx", scenario_filter="id_scenario_energy_price_mark_up")
        self.s_energy_carrier_price_co2_emission = self.load_scenario("Scenario_EnergyCarrier_Price_CO2Emission.xlsx", scenario_filter="id_scenario_energy_price_co2_emission")
        self.setup_final_energy_carrier_price()

    def setup_final_energy_carrier_price(self):
        self.s_final_energy_carrier_price = RenderDict.create_empty_data_tdict(key_cols=[
            "id_scenario",
            "id_region",
            "id_sector",
            "id_energy_carrier",
            "year"
        ])
        self.s_final_energy_carrier_price.region_level = 0
        markup = self.load_dataframe("Scenario_EnergyCarrier_Price_MarkUp.xlsx")
        # markup table has the most detailed index columns and can cover the possible rkeys in other tables:
        # wholesale, tax_rate, and co2_emission
        for index, row in markup.iterrows():
            for year in range(self.start_year, self.end_year + 1):
                rkey = RenderKey(id_scenario=self.id).from_dict({
                    "id_region": row["id_region"],
                    "id_sector": row["id_sector"],
                    "id_energy_carrier": row["id_energy_carrier"],
                    "year": year
                })
                self.s_final_energy_carrier_price.set_item(
                    rkey,
                    (
                            self.s_energy_carrier_price_wholesale.get_item(rkey) +
                            self.s_energy_carrier_price_markup.get_item(rkey) +
                            (
                                    self.s_energy_carrier_price_co2_emission.get_item(rkey) *
                                    self.s_emission_factor.get_item(rkey)
                            )
                    ) * (1 + self.s_energy_carrier_price_tax_rate.get_item(rkey))
                )
