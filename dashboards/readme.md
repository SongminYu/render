
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
  - [x] download and process other years: start from 2010
  - file size ~19 MB for temp and PV gen, but ~70 MB for radiation for 1 year. if more years added, will be bigger. (~linear) do we use separate files for different years
- [x] adjust color coding scale to be within 'end-use' columns (also within total)

## May 14th, 2024
- [x] ask Hannah if the dashboard works without the combination of EC and end-use (for regional use. also ask for 3 drop-down tabs: NUTS 1,2,3)
  - [x] Hannah develops new dashboard for regional (NUTS1-level) comparison. 
    - There won't be end-use break-down, but total of energy carriers. 
    - The graph can have regions on the x-axis, demand (TWh) on the y-axis. Legend is still energy carriers
    - The model result and reference tables are dynamic according to region selection
  - [x] Sirin provides regional "calibration target" file as example: RenderNew\dashboards\data\Energiebilanzen_Regional_Example.xlsx

## May 17th, 2024
- [x] Hannah adds data tables to the region analysis dashboard
- [x] Sirin checks DWD for future year weather profile.


## May 24th, 2024
- [x] Future year weather profiles: https://zenodo.org/records/7907883
  - check if all years (2010-2050) exceed 100 MB. If so, reduce future years to 5 (or 10) steps like 2025,2030, etc.
  - check how PVGIS creates NUTS2 region temperature. Accordingly, we will decide if we use spatial mean or population mean
  - what type of radiation does PVGIS give? (global irradiation or direct normal irradiation)
  - if there is a way to generate orientation-specific radiation from one global or one direct normal irradiation?
- [x] new dashboard (named "national timeseries calibration"): 
      plotting timeseries for historic comparison. it's a "mixed-plot" where model results are bars, reference is line
  - years on x-axis
  - one bar chart with energy carriers (in legend) accumulated for each year from model results.
    line (or data points connected via dashed line) for the total coming from reference data years.
  - one bar chart with end-uses (in legend) accumulated for each year from model results.
    line (or data points connected via dashed line) for the total coming from reference data years.
  - tables: 
    - for each of the four end-uses, we will have the four tables (16 table in total)
    - we rename the "end-use analysis" to "national year calibration"
- [x] Sirin updates the CalibrationTarget file with historic reference data.

## June 21st, 2024
- [ ] Global radiation (solar radiation flux on horizontal surface) and direct normal irradiance (for perpendicular surfaces) are given
  - (if?) which one do we want to use? I guess it is possible to calculate the different orientations but I am confused about the units (W or W/m^2?)
    - [x] Hannah downloads Global radiation.
    - [ ] Sirin checks methodology of generating orientation-specific radiation from global radiation
    - we can also generate the PV generation "relatively" to global radiation of 2020.
  - if we have 4 orientations, file size will exceed 100 MB, for temperature it is okay
    - [x] we deal with this by having only intermediate years after 2020: 2030, 2040, 2050
- [x] Which scenario do we want to choose? RCP 4.5 or RCP 8.5
  - we chose RCP 4.5
- [x] End use as dropdown
  - end-use plots (by energy carrier) are shown separately one after each other for now.
  - aggregation at national/state-level in the input file relevant? --> faster processing?

## June 27th, 2024
- [ ] check if aggregation at national/state-level in the input file relevant? --> is it faster processing?
- [x] dashboard header or indication of which dashboard we are
- we generate the PV generation and orientation-specific radiation "relatively" to global radiation of 2020.
  - [x] check what is the "error margin" of this method by looking into a historic year e.g. 2015-2016.
  - [ ] produce radiation and PV generation outputs for 2030, 2040, 2050.

## July 5th, 2024
- [x] check if aggregation at national/state-level in the input file relevant? --> is it faster processing?
- we generate the PV generation and orientation-specific radiation "relatively" to global radiation of 2020.
  - [x] understand the "error" of this method: why is it high? e.g. sort the regions in the same order in both datasets to be sure. 
- [x] filter the year when reading the regional reference data
- [x] Sirin updates the Energiebilanzen_Regional.csv file with the collected regional data
  - [x] renaming of reference data files: Reference_EnergyBalance_National.csv, Reference_EnergyBalance_Regional.csv
  - [x] model results are named as final_energy_demand_nutsX

## July 12th, 2024
- continuing on open points from the previous weeks

- [x] Caching of datasets which are frequently used
- [x] Once preprocess data (maybe even incorporate in model)
- [x] Centralized data loading

## July 25th, 2024
- [x] (for national timeseries calibration, national year calibration and region analysis) default data file we use is: final_energy_demand_nuts1
- [x] we have another dashboard for individual nuts3 region analysis:
  - where we don't print tables, and there is no reference data
  - we just plot figures of: Analysis by Energy Carrier, Analysis by End-use, and Analyses for each end-use by energy carrier (x4)

# August 2nd, 2024
- [x] small bug about energy carrier = 24. 
      only reference data has it, but it disappears from the difference tables.
- [x] new dashboard: heating technologies on nuts 1 level
  - Sirin uploads a recent regional (NUTS 3) building stock table (for small size)
    later we can produce NUTS 1 level building stock table as output for regional analysis
  - Sirin uploads the reference data for heating technologies in the same convention as model (id_heating_tech etc.)
  - Hannah: the dashboard is similar structure to region_analysis_nuts1 dashboard
    stacked are number of heating technologies: "heating_system_main_id_heating_technology" 
    (legend is the heating technology type)

# August 6th, 2024
- [ ] Should 9 be part of regions? Totals do not fit...
  --> We do not include id_region=9 from reference, it must be the sum of individual regions
- [ ] Heating Technologies 32 and 33 not in Reference 
  --> we put them under 31 for now
- [ ] we should filter for sector=6 already when preparing the data (loader) as the reference only includes sector=6
- CSV files need to be seperated by ',' not by ';' (Maybe that is also the reason why Sirin can't open the csv files in excel)
  Control Panel -> Clock and Region –> Change the date, time, or number format -> Additional settings -> List seperator
- Comments in existing code so that it is better understandable
- [ ] (Sirin) adjust the building_stock_summary files to include heating_system_main_id_heating_technology --> then we use nuts1 aggregation directly in dashboard

- [ ] new dashboard: Energy performance of buildings
  - stacked bar chart for buildings belonging to each id_building_efficiency_class (for sector=6)
    x-axis: id_building_efficiency_class
    y-axis: either the absolute number of buildings, or ratio of the absolute number to the total of the stock
    stacked are building types (but types 1&2 and types 3-5 aggregated)
  - (Sirin) prepares the reference


### Later stage

- new dashboard for building_efficiency_class
- enhance Floor Area dashboard
- geo-visualization (new dashboard)
- beautify dashboards

- GHSL data processing to distribute NUTS3 and location results to 100m x 100m grid cell (hectare) level.

