# Actions

## Ongoing

### Meeting

- Updates
  - meeting with Hannah
  - meeting with Weijia
  - Code developments
- Open questions
  - `renovation_rate` output
  - `demolition` and `construction` output
- upload ecemf results
- arrange a meeting to record detailed code walk-through

### Songmin
- [x] add function `post_processor.aggregate_final_energy_demand`
- [ ] update table names --> second thought: slower, consistency and maintenance, 2011 can be scenario values
  - for some scenario tables, they are only used for initialization, or mixed used for initialization and new buildings
  - decision: create a new group of buildings called "Initialization_xxx" --> cleaner
- [x] revise tables to be `id_scenario` dependent
  - `renovation_mandatory`
  - `heating_technology_mandatory`
  - `gas_infrastructure_availability`
  - `dh_infrastructure_availability`
  - `building_component_availability`
  - `heating_technology_availability`
- [x] hydrogen grid
  - grid initialization and diffusion
  - update of available technologies
- [x] for new buildings: only renewable heating is allowed
- [ ] subsidy programs for renovation and heat pump
  - could depend on income group, so we need to add income group of unit users
  - add a new "subsidy" table depending on some ids, for example, 
    - `id_building_efficiency_class_after`
    - `id_heating_technology`
    - `id_income_group`
- [ ] modeling of PV and battery
  - do we model at hourly resolution? depending on if we contribute load profiles from our model
  - or we consider a coupling approach with other model, then in Render we use self-consumption rate
  - mandatory for new buildings?
- [ ] add function 
  - `post_processor.gen_renovation_rate`
  - `post_processor.gen_building_demolition_and_construction`
- [ ] calibrate based on updated 2010-2022 results
  - appliance
  - space cooling: maybe update the penetration rate, or cooling temperature?
  - behavior profiles need to be updated
  - [ ] for households,
    - the occupancy/app/hot-water profiles all need to be replaced with smooth synthetic profiles
    - the "teleworking" scenario profiles should be weighted-average based on an assumption of a share of the teleworking ratio
  - [ ] for tertiary sectors, the profiles (especially occupancy profiles) should be carefully updated



### Sirin

- [ ] Overview the data gap
- [ ] Send slides to RokiG meeting to publish
- [ ] for calibration and prepare for RokiG meeting on June 18th
  - update energy price and availability tables
  - re-run the model 2010-2022
  - upload `final_energy_demand.csv` to drive and send to Songmin 
  - check with Mahsa if we provide results to RWTH beforehand to show the "scenario generator"
- [ ] For JF on June 3rd
    - update slides to introduce how qualitative input from IBP are used to develop scenarios
    - show IBP how the scenarios are quantified in the model (show the related tables)
    - ask them to fill in the data gap

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
- [x] solve the size problem of weather input
  - add 2030/2040/2050 profiles for NUTS2
  - hardcode mapping years to 2020/2030/2040/2050 in the projection years
- [x] link renovation action to ownership
  - [x] currently `id_ownership` is initialized only for unit-users. Use "EIGENTUM.xlsx" to add ownership info to the building, then the renovation decisions can be impacted by this.
  - [x] `Parameter_Building_ActionProbability` added
- [x] mandatory renovation
- [x] mandatory heating system modernization
- [x] remove previous code on renovation rate
- [x] save building stock every year to the csv for memory saving?
- [x] when "mandatory" --> peak number of actions in the first year
  - delay logic: a year selected within the window

### Sirin

- [x] Contact IT for server use, and before them replying to us, test `kamino`
- [x] Find tasks for Weijia
- [x] design dashboards for Hannah to develop
- [x] Create a ticket about server use for IT
- [x] Summarize data gap lists and prepare the workshop with Fraunhofer IBP (Timeline: around mid-May by email, then the end of May or early June, we have the workshop)
- [x] add region ids (NUTS1 and NUTS2)
- [x] meet Hannah
  - [x] download NUTS2 weather data
  - [x] discuss how to integrate NUTS1 calibration data (maybe we need dropdowns for 3 levels of id_region in the dashboard)
  - [x] there is the code mapping id_regions at different levels (line 62 in models/render/render_dict.py)
  - [x] then design the table format for Weijia
- [x] update calibration target table (fluss gas)