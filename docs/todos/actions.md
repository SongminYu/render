# Actions

## Ongoing

### Meeting

- Updates
  - RokiG meeting feedbacks
    - meeting with IBP and Nico (separately) on Thursday, 27th. Nico commented on PV, IBP commented mainly on new technologies in Neubau and smart operation
  - meeting with Hannah
  - meeting with Weijia
    - completed the extraction of data from the study (Wie heizt DE?): detailed data at state level on heating system (tech., age, EC, etc.) --> how do we proceed?
    - completed data collection of final energy consumption at state level. however, not every state has data for every year; in fact, no common year so far on all 16. Also, some states have HH and GHD, separate; some together.
    - CO2 emissions statistics are in progress.
- Arrange a meeting
  - record detailed code walk-through
  - update the two plots on the Miro board

### Songmin

- [x] Revise: all the new heating system must satisfy 65% renewable requirement --> not changed, because the policy can be captured by the availability table. This "mandatory" logic was added as a symmetric policy with the building renovation. We can keep it "closed" for most scenarios.
- [x] report renovation rate for residential and non-residential buildings separately

### Sirin

- [ ] Check first scenario results and see if further improvements are necessary
  - heating technology ban for oil, even gas
  - district heating cost calibration (check infrastructure, calibration choice among technologies)
- [ ] Migrate comments from eceee and RokiG RWTH meeting to the todos
- [ ] Check literature and sources about cooling
  - decide how we model cooling demand in RENDER (replacing 5R1C if necessary)
- [x] increase window lifetime for lower renovation rate: increased mean lifetime by roughly 50%

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
- [x] add function `post_processor.aggregate_final_energy_demand`
- [x] update table names --> second thought: slower, consistency and maintenance, 2011 can be scenario values
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
- [x] subsidy program for `heating_modernization` --> `Scenario_Subsidy_HeatingModernization`
- [x] subsidy program for `building_renovation` --> `Scenario_Subsidy_BuildingRenovation`
- [x] calibrate based on updated 2010-2022 results
  - add other energy carriers in appliance consumption and efficiency index
  - space cooling: maybe update the penetration rate, or cooling temperature? --> found and fixed bug in cooling demand collection
  - behavior profiles need to be updated
  - Heads up on calibration
    - The calibration was done by starting the model from 2010 with 10% coverage.
    - This decides the building and employee number in the tertiary sectors, because there is only demolished buildings replaced by new buildings
    - This further decides the calibration of appliance and hot water demand per person. 
    - As a result, if the model is started from 2019. The deviation in 2019 will be larger. 
    - Changing coverage percentage may also impact but not that much.
- [x] collect investment cost of `heating_modernization` and `building_renovation` by both building and state
- [x] Understand why cooling is underestimated
  - now it is about 4% of the statistics
  - checked energy intensity (0.3-0.4) --> looks fine
  - checked the output tables and aggregation --> no mistake
  - compared with the 5R1C model results in FLEX, taking useful energy demand of one building as example
    - flex ratio: cooling/heating = 145437/45471288 = 0.003198436 --> considering the adoption rate and technology efficiency, this number can be reduced --> close to render ratio
    - render ratio: 0.000923967
    - statistics ratio: 0.022491748
      - maybe RC model is not a good approach? 
      - Sonja's results are likely to be calculated with operation hours and power according to the questions in the survey. 
      - We should check literature on cooling demand.
- [x] add function
  - `post_processor.gen_renovation_rate`
    - definitions
      - not added --> component renovation rate = number of component renovated buildings / total number of buildings
      - component area-weighted renovation rate = renovated component area / total component area in stock
      - overall modernization rate = (area-weighted renovation rate wall * 0.4 + area-weighted renovation rate roof * 0.28 + area-weighted renovation rate basement * 0.23 + area-weighted renovation rate window * 0.09)
    - progress
      - added `component_area` in the renovation table
      - steps designed
  - `post_processor.gen_building_demolition_and_construction`
    - definition: number of demolished/constructed buildings / total number of buildings
    - progress: data collection code added, will add the function in post_processor and calculate results after next run
- [x] modeling of PV and battery
  - exogenous penetration rate + optional policy scenario: mandatory for new buildings
  - no battery
  - size of PV depends on `roof_area`
  - temporal resolution: annual resolution + with self-consumption rate
  - heads-up: parameters to be developed

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
- - [x] Send slides to RokiG meeting to publish
- [x] for calibration and prepare for RokiG meeting on June 18th
  - update energy price and availability tables
  - re-run the model 2010-2022
  - upload `final_energy_demand.csv` to drive and send to Songmin 
  - check with Mahsa if we provide results to RWTH beforehand to show the "scenario generator"
- [x] For JF on June 3rd
    - update slides to introduce how qualitative input from IBP are used to develop scenarios
    - show IBP how the scenarios are quantified in the model (show the related tables)
    - ask them to fill in the data gap
- [x] Overview the data gap
- [x] Check scenario tables and update them for the reference scenario run after calibration in the first week of June
  - Update the energy carrier price, based on discussions about "mark-up" and "tax" on 31.05.2024
