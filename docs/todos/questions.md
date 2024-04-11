# Questions

* Problem of scaling up: not all building agents are representing same number of buildings, is this a problem? For example, one building is renovated, it means all the buildings represented by it are renovated. Do we need to revise how "agent_num_model" and "agent_num_total" are decided?
* Shall we post-process the results for higher geo-resolution (e.g., 100*100 m2) with GHSL data?
* id_building_efficiency_class
  * we should calculate the initial id_building_efficiency_class without hot water demand --> then use these to assign customized internal set temperatures
  * We don't need to update these classes after we calculate the consumption (calculated according to customized temperatures); but, we can just plot the distribution of specific energy consumption for comparison with dena statistics
  * We check the "energy performance certificates" classes for definition (using EPBD/official definitions):
    * Does it include only space heating, or space heating and hot water, or all end uses?
    * Does it assume 20°C internal set temperature like the norm (I.e. demand)? Or, is it flexible with use behaviour (I.e. consumption)?
  * Feasibility of heating technology is both related to energy performance class AND supply temperature of space heating and hot water

