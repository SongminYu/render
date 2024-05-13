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
- [ ] relate income and age information at the same time (to be added to BuildingKey: id_income_group, id_age_group)
- [ ] the role of owner or tenant (Sabine has some data)
  * should also depend on `id_building_type`?
  * missing good assumptions for non-residential buildings.
- [ ] willingness-to-pay

## Later stage
- Data on material demand for new construction (and then differentiation of green/sustainable materials such as green cement, steel etc.) This will be relevant only during new construction