# Actions

## Ongoing

### Meeting

* How about the server use?
* Does the new scaling logic produce similar final energy demand result? We can try 9010101 quickly. If so, we can 
  * merge the branch to main
  * remove the two min and max parameters from scenario.
  * send building stock data to Nico
* Updates on the logic development
  * designing of building demolition and construction
  * go over `dev_logic.md`
  * Regarding 2019 takes longer...
    * Many building components are renovated or demolished in 2019. 
    * We need to find a way to smooth this --> logic of `next_replace_year`, e.g., be postponed?
* Updates on meetings with 
  * Hannah likes working on coding and data processing...
    * pv_gis data
    * beautify dashboards
    * timeseries plotting?
    * geo-visualization in the dashboard?
  * Weijia
    * energy balance of regions
    * cost data?
* Discussion on the open points
  * Regarding population...
    * What data do we have regarding "population/employee", at what geo-level (e.g., region, location, etc.)?  
    * Should the residential and non-residential population roughly equal to each other? We can check.
    * We should first organize this, if necessary, update unit user logic, then continue with building construction logic.
* Plan next meetings

### Songmin

- [x] Develop the main logics for demolition
- [ ] Develop the main logics for construction
- [ ] Send building stock data to Nico

### Sirin

- [ ] Summarize data gap lists and prepare the workshop with Fraunhofer IBP
- [ ] Find tasks for Weijia
- [ ] Develop population data
- [ ] Verify results
  - [ ] building stock
    - [ ] final energy demand
    - [ ] floor area
    - [ ] dwelling number
  - [ ] renovation actions, incl. renovation rate calculation
  - [ ] heating system actions, incl. heating system size

## Done

### Songmin



### Sirin

- [x] Contact IT for server use, and before they replying to us, test `kamino`