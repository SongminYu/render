# RenderNew

This is a new repo for the RENDER models based on `Melodie V1.0.1` and `tab2dict`.

### To-dos
 - Code changes: 
   - add energy_cost_before column in the heating system action table.
   - we don't have diffusion of the "second heating technology" yet.
 - Questions: 
   - the heating system size might be overestimated, as most of them are "large".
   - check renovation and heating replacement rates --> too high maybe, needs limit
   - all represented buildings act together. We need to think about the validity of up-scaling.
   - check literature of ventilation, because maybe the "driver" should be m3 instead of m2
 - Data development
   - update the data in the energy carrier price tables
   - improve calibration of end-uses other than space and water heating.
   - fill in data for serial renovation --> `id_building_action = 3`
 - Improve calibration
   - develop region- and year-specific weather data.
   - regional calibration
   - predict history: base year 2010 and run until 2022 for model calibration
 
### Feature development
 - Technically, we can also distribute location-level results to hector-level, based on the GHSL data.

### Management issues
 - data maintenance work flow
