

framework: PlotlyDash

some points to think about when designing...

- template module in the future
- possibility to download the figure and data as excel files


Todos...

from the building stock table, 
for a combination of `id_scenario`, `id_region`, `id_sector`, `id_subsector`, `year` (multiple choice),
we can have a matrix for the final energy demand
 - row: energy carrier
 - column: end-use, incl. appliance electricity, space cooling, hot water, space heating
On the dashboard, 
 - we can visualize it as a stack bar chart: x-axis as end-use, y-axis as final energy consumption
 - we can have a table showing the matrix