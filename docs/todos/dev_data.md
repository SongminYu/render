# Data development

## Ventilation and cooling system data
- [ ] costs and energy intensity
- [ ] the driver for ventilation: m2 or m3?

## Radiator data
- [ ] cost
- [ ] supply temperature depending on radiator type and efficiency class

## Renovation
- [ ] fill in the data for serial renovation (id_building_action = 3)

## Heating system
- [ ] infrastructure expansion scenarios

## Population data
- [ ] from Census, we have household size percentages by region. The id_unit_user_type will also be updated accordingly, then the behavior aspects (e.g., teleworking linked to working status) will be added through other tables.
- [ ] relate income and age information at the same time (to be added to BuildingKey: id_income_group, id_age_group)
- [ ] the role of owner or tenant (Sabine has some data)
- [ ] willingness-to-pay

## Later stage
- Data on material demand for new construction (and then differentiation of green/sustainable materials such as green cement, steel etc.) This will be relevant only during new construction