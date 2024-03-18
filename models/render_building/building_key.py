from models.render.render_key import RenderKey
from typing import Optional


class BuildingKey(RenderKey):

    def __init__(
        self,
        id_scenario: Optional[int] = None,
        id_region: Optional[int] = None,
        id_sector: Optional[int] = None,
        id_subsector: Optional[int] = None,
        id_subsector_agent: Optional[int] = None,
        id_energy_carrier: Optional[int] = None,
        year: Optional[int] = None,
        id_action: Optional[int] = None,
        id_building_construction_period: Optional[int] = None,
        id_building_height: Optional[int] = None,
        id_building_location: Optional[int] = None,
        id_building_type: Optional[int] = None,
        id_building_component: Optional[int] = None,
        id_building_component_option: Optional[int] = None,
        id_building_component_option_efficiency_class: Optional[int] = None,
        id_building_efficiency_class: Optional[int] = None,
        id_orientation: Optional[int] = None,
        id_unit_user_type: Optional[int] = None,
        id_heating_system: Optional[int] = None,
        id_heating_technology: Optional[int] = None,
        id_cooling_technology: Optional[int] = None,
        id_cooling_technology_efficiency_class: Optional[int] = None,
        id_ventilation_technology: Optional[int] = None,
        id_ventilation_technology_efficiency_class: Optional[int] = None,
        id_end_use: Optional[int] = None,
    ):
        super().__init__(
            id_scenario=id_scenario,
            id_region=id_region,
            id_sector=id_sector,
            id_subsector=id_subsector,
            id_subsector_agent=id_subsector_agent,
            id_energy_carrier=id_energy_carrier,
            year=year
        )
        self.id_action = id_action
        self.id_building_construction_period = id_building_construction_period
        self.id_building_height = id_building_height
        self.id_building_location = id_building_location
        self.id_building_type = id_building_type
        self.id_building_component = id_building_component
        self.id_building_component_option = id_building_component_option
        self.id_building_component_option_efficiency_class = id_building_component_option_efficiency_class
        self.id_building_efficiency_class = id_building_efficiency_class
        self.id_orientation = id_orientation
        self.id_unit_user_type = id_unit_user_type
        self.id_heating_system = id_heating_system
        self.id_heating_technology = id_heating_technology
        self.id_cooling_technology = id_cooling_technology
        self.id_cooling_technology_efficiency_class = id_cooling_technology_efficiency_class
        self.id_ventilation_technology = id_ventilation_technology
        self.id_ventilation_technology_efficiency_class = id_ventilation_technology_efficiency_class
        self.id_end_use = id_end_use
