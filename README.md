# RenderNew

This is a new repo for the RENDER models based on `Melodie V1.0.1` and `tab2dict`.

### Todos
 - fill in data for serial renovation --> `id_building_action = 3`
 - update the data in the energy carrier tables
 - fill in the values for all `cooling` and `ventilation` tables.
 - develop region- and year-specific weather data.
 - Technically, we can also distribute location-level results to hector-level, based on the GHSL data.
 - Question: all represented buildings act together. Is this right?
 - Question: check literature of ventilation, because maybe the "driver" should be m3 instead of m2
 - Bug: when checking the renovation action info table, following building component option 31 has area = 0 (input data). Maybe we should limit the possible options with another relation table? Also a table for heating system?
 - Question: the heating system size might be overestimated, as most of them are "large".
 - Question: confirm the definition of "similar change" for heating system action
