
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
  - [x] difference in absolute number -> different energy carriers with value in the two tables
  - [x] difference in percentage

### Apr. 3th, 2024

- [x] Add tab buttons on the same website, so we can easily switch between the dashboards --> Tutorial: https://dash.plotly.com/urls
- [x] Tables for `id_end_use` and `id_energy_carrier`.
- [x] `id_energy_carrier` for appliances?
- [x] Songmin will align the energy carrier inconsistency between model results and reference table and push the new calibration target table.
- [x] Songmin will confirm where ventilation goes, appliance or cooling, and change calibration target table accordingly.

### Apr. 12th, 2024

- [x] Songmin develops the postprocessing functions to generate `final_energy_demand`, `floor_area`, `building_efficiency_class_count` tables based on the `building_stock` table.
- [x] The model result table looks not right (try final energy demand table first in the call).
- [x] Two end-use columns are missing.
- [x] Some functions in the `loader.py` file are not used anymore?
- [x] Add the total columns (sum of energy carrier) in the four tables.
- [x] Change the unit to TWh and align to 100.00 TWh.
- [x] All numbers in the table to the right.
- [x] When selecting `id_sector = 3` and `id_subsector = 31`, there is the zero row.
- [x] Dropdown menu does work right?

### Apr. 17th. 2024

- [x] NUTS3 weather data download (Songmin has some previous code)
  - [ ] check which data is missing & complete (radiation, temperature, PV generation): why?
    - [x] also, which other years are there? (2005 - 2019)
  - [x] see if post-processing to convert input data format directly is possible (wide format for hour, regions listed vertically)
    - you can use ..\RenderNew\docs\data_prep\weather_files for preparation code and output file
    - the weather profile and ID tables are here: ..\RenderNew\projects\test_building\input

### Apr. 25th. 2024

- [x] implement color coding for the degree of deviation in tables: Absolute difference and relative difference.
  - the darker color for higher numbers

## May 3rd, 2024
- [x] NUTS1 and NUTS2 weather data download
  - [ ] check why data is missing & complete (radiation, temperature, PV generation)
  - [x] download and process other years: start from 2010
  - file size ~19 MB for temp and PV gen, but ~70 MB for radiation for 1 year. if more years added, will be bigger. (~linear) do we use separate files for different years
- [x] adjust color coding scale to be within 'end-use' columns (also within total)
- [ ] ask Hannah if the dashboard works without the combination of EC and end-use (for regional use. also ask for 3 drop-down tabs: NUTS 1,2,3)

### Later stage
- beautify dashboards
- geo-visualization (new dashboard)
- enhance Floor Area dashboard
- new dashboard for building_efficiency_class
- timeseries plotting for calibration (new dashboard)
- GHSL data processing to distribute NUTS3 and location results to 100m x 100m grid cell (hectare) level.

