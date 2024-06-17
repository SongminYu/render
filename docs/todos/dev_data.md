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
- [x] the ownership information (Sabine has some data)
  * unit users: ownership or tenant, which is not used yet
  * buildings: more types of ownership, which impacts the probability of renovation
- [ ] willingness-to-pay

## Profiles
- [ ] the "teleworking" scenario profiles should consider the assumption of teleworking ratio
- [ ] for tertiary sectors, the profiles (especially occupancy profiles) should be carefully updated
- [ ] the occupancy profiles of households could to be replaced with smooth synthetic profiles

## Later stage
- Data on material demand for new construction
  - differentiate green/sustainable materials such as green cement, steel etc.
  - This will be relevant only during new construction
