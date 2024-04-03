
# RenderDash

This document contains the development plan of the `RenderDash` tool. 

### Mar. 27th, 2024

- [x] `__init__.py` files can be removed
- [x] `building_stock_ids.py` can be moved into `building_stock_dash.py`?
- [x] ids are linked, e.g., when `id_sector = 6` is unselected, `id_subsector = 61` should also be removed. See if there is a flexible way to have such relation considered. If not, we can postpone this demand.
- [x] energy intensity redefined in the new building stock table
- add tables (end-use v.s. energy carrier) on the dashboard: 
  - [x] model results
  - [x] calibration targets (Sirin is updating the target value table)
  - [ ] difference in absolute number -> different energy carriers with value in the two tables
  - [ ] difference in percentage

### Apr. 3th, 2024

- [ ] Add tab buttons on the same website, so we can easily switch between the dashboards --> Tutorial: https://dash.plotly.com/urls
- [x] Tables for `id_end_use` and `id_energy_carrier`.
- [x] `id_energy_carrier` for appliances?
- [ ] Songmin will align the energy carrier inconsistency between model results and reference table.

### Apr. 10th, 2024

- [ ] To be added...

### Later stage

- geographic visualization
- GHSL data processing to distribute NUTS3 and location results to 100m x 100m grid cell (hectare) level.

