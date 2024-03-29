
# RenderDash

This document contains the development plan of the `RenderDash` tool. 

### Mar. 27th, 2024

- [ ] `__init__.py` files can be removed
- [ ] `building_stock_ids.py` can be moved into `building_stock_dash.py`?
- [x] ids are linked, e.g., when `id_sector = 6` is unselected, `id_subsector = 61` should also be removed. See if there is a flexible way to have such relation considered. If not, we can postpone this demand.
- [x] energy intensity redefined in the new building stock table
- [ ] add tables (end-use v.s. energy carrier) on the dashboard: 
  - model results
  - calibration targets (Sirin is updating the target value table)
  - difference in absolute number
  - difference in percentage


### Apr. 3th, 2024

- [ ] Can we have all the dashboards on the same website, or with a few sheet pages? So we can easily switch between the dashboards.

### Later stage

- geographic visualization
- GHSL data processing to distribute NUTS3 and location results to 100m x 100m grid cell (hectare) level.

