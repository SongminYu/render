# Questions

* Problem of scaling up: not all building agents are representing same number of buildings, is this a problem? For example, one building is renovated, it means all the buildings represented by it are renovated. Do we need to revise how "agent_num_model" and "agent_num_total" are decided?
  * Maybe we simply use 10% (or a bit lower) according to the server capacity to avoid this problem, and we can round up to 1 for those who are zeros.
* Shall we post-process the results for higher geo-resolution (e.g., 100*100 m2) with GHSL data?
* To talk in the same language, we may update the ranges of `id_building_efficiency_class` consistent with the "energy performance certificates" (using EPBD/official definitions):
  * Does it include only space heating, or space heating and hot water, or all end uses?
  * Does it assume 20°C internal set temperature like the norm (I.e. demand)? Or, is it flexible with use behaviour (I.e. consumption)?

