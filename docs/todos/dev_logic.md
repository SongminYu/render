# Logic development

## Investment decisions

### heating system

- [ ] modeling second heating technology?
  - diffusion?
  - in the new buildings (ignored at the moment)
  - more complicated combinations (should be reasonable), e.g., HP and gas --> 65% requirement effective
  - discontinued after reaching lifetime (checking penetration rate table)

### renovation

- [x] limit the probability of lifecycle renovation being triggered (maybe too high now)
  - done by adding the action probability related to the building ownership types

### both

- [x] capex calculation: lifetime is replaced with payback time for all investment decisions
- [ ] impact of unit user properties: income group, age group
- [ ] endogenous price change of heating technology, biomass, etc. due to demand change
- [ ] consider willingness-to-pay: as the on-top money that may change the order of the options in the last step

## Building demolition

- [ ] material recycling by connecting the work by Thurid
- [ ] craftsman demand

## Building construction

- [ ] material demand by connecting the work by Thurid
- [ ] craftsman demand

## Heating system

- [ ] more detailed modeling of combined technologies, e.g., HP as a main technology and supported by a secondary gas boiler (extending the second technology table, also with reasonable limits)
- [ ] contribution factor depends on the type of main heating technology and building efficiency class?
- [ ] use better COP of HP to show the impact of smart management (in general, use results of optimization model as input parameters for the RENDER-Building model, to reflect prosumaging / SEMS scenarios)

## Post processor

- [x] Add distribution of `id_building_efficiency_class` (or kWh/m2) as an output, 
  - [x] space&water heating intensity
  - [x] space heating intensity
  - [x] efficiency class


