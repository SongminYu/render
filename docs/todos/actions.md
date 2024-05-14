# Actions

## Ongoing

### Meeting

### Songmin

- [x] solve the size problem of weather input
  - add 2030/2040/2050 profiles for NUTS2
  - hardcode mapping years to 2020/2030/2040/2050 in the projection years
- [x] link renovation action to ownership
  - [x] currently `id_ownership` is initialized only for unit-users. Use "EIGENTUM.xlsx" to add ownership info to the building, then the renovation decisions can be impacted by this.
  - [x] `Parameter_Building_ActionProbability` added?
- [ ] mandatory renovation and heating system
- [ ] modeling of PV and battery.
- [ ] during calibration, behavior profiles need to be updated
  - [ ] for households, 
    - the occupancy/app/hot-water profiles all need to be replaced with smooth synthetic profiles
    - the "teleworking" scenario profiles should be weighted-average based on an assumption of a share of the teleworking ratio
  - [ ] for tertiary sectors, the profiles (especially occupancy profiles) should be carefully updated

### Sirin

- [ ] meet Hannah
  - [x] download NUTS2 weather data
  - [ ] discuss how to integrate NUTS1 calibration data (maybe we need dropdowns for 3 levels of id_region in the dashboard)
  - [ ] there is the code mapping id_regions at different levels (line 62 in models/render/render_dict.py)
  - [ ] then design the table format for Weijia
- [ ] update calibration target table (fluss gas)
- [ ] Verify results
  - [ ] building stock
    - [x] final energy demand
    - [ ] floor area
    - [ ] dwelling number
  - [ ] renovation actions, incl. renovation rate calculation
  - [ ] heating system actions, incl. heating system size


## Done

### Songmin

- [x] Develop the main logics for demolition
- [x] merge the branch to main
- [x] remove the two min and max parameters from scenario.
- [x] logic of `next_replace_year` --> be postponed as a test
  - [x] add to renovation history
  - [x] add to renovation projection
  - [x] update building lifetime and demolition year
- [x] Send building stock data to Nico
- [x] process population data
  - eurostat dataset (NUTS3 regions): https://ec.europa.eu/eurostat/web/main/data/database
  - GHSL dataset (100m level and can be mapped to NUTS3 regions and locations)
  - validation: residential and non-residential population comparison
- [x] update the Scenario_UnitUser table
  - add id_region (NUTS2 level) based on https://ec.europa.eu/eurostat/databrowser/view/cens_11htts_r2/default/table?lang=en&category=reg.reg_dem.reg_cens_11r.cens_11rdf
  - generate the building stock and summary files, then verify 
    - total population of each NUTS3 region
    - the distribution percentages by id_region and id_location, then compare with GHSL data
- [x] Develop the main logics for construction, based on the population data development

### Sirin

- [x] Contact IT for server use, and before them replying to us, test `kamino`
- [x] Find tasks for Weijia
- [x] design dashboards for Hannah to develop
- [x] Create a ticket about server use for IT
- [x] Summarize data gap lists and prepare the workshop with Fraunhofer IBP (Timeline: around mid-May by email, then the end of May or early June, we have the workshop)
- [x] add region ids (NUTS1 and NUTS2)