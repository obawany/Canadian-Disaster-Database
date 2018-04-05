
/* Roll up
Determine total estimated costs of each disaster category IN each canadian city
*/

SELECT a.disaster_category, b.city, SUM(CAST(c.estimated_total_cost AS bigint)) AS total_costs

FROM disaster_dimension a, location_dimension b, cost_dimension c, disaster_fact d

WHERE NOT (c.estimated_total_cost = 'unknown') AND d.cost_key = c.cost_key AND d.location_key = b.location_key
AND d.disaster_key = a.disaster_key

GROUP BY ROLLUP(a.disaster_category, b.city);


/* Slice
Determining the total cost of disasters IN Canada
*/

SELECT a.disaster_category, SUM(CAST(b.estimated_total_cost AS int)) AS CostofIncidentDisasters

FROM disaster_dimension a, cost_dimension b, disaster_fact c

WHERE NOT (b.estimated_total_cost = 'unknown') AND a.disaster_category = 'Incident' AND a.disaster_key = c.disaster_key AND b.cost_key = c.cost_key

GROUP  BY a.disaster_category;



/* Dice
Determining the total cost of Technology related Incidences IN Canada
*/

SELECT a.disaster_category, SUM(CAST(b.estimated_total_cost AS int)) 

FROM disaster_dimension a, cost_dimension b, disaster_fact c

WHERE NOT (estimated_total_cost = 'unknown') AND a.disaster_category = 'Incident' AND a.disaster_group = 'Technology'
AND a.disaster_key = c.disaster_key AND b.cost_key = c.cost_key

GROUP BY a.disaster_category;



/* Iceberg
For instance, determine the 5 cities IN Canada with the most Fires
*/

SELECT l.city, COUNT(dd.disaster_subgroup) as Fires

FROM disaster_fact d, location_dimension l, disaster_dimension dd

WHERE dd.disaster_subgroup = 'Fire' AND d.disaster_key = dd.disaster_key AND l.location_key = d.location_key

GROUP BY dd.disaster_subgroup, l.city

ORDER BY Fires DESC

LIMIT 5;

/* Slice
For instance determine the total number of fatalaties in Ottawa/Ontario during 1999 
*/

SELECT SUM(CAST(d.fatalities AS int)) AS Fatalities, dd.year

FROM disaster_fact d, location_dimension l, date_dimension dd

WHERE NOT (d.fatalities = 'unknown') AND l.location_key = d.location_key AND dd.year = 1999 AND l.city = 'Ottawa'

GROUP BY dd.year;


/* Slice
Determining estimated total costs caused by Disasters IN each province
*/

SELECT d.city, a.disaster_category, SUM(CAST(b.estimated_total_cost AS bigint))

FROM disaster_dimension a, cost_dimension b, disaster_fact c, location_dimension d

WHERE NOT (b.estimated_total_cost = 'unknown') AND a.disaster_category = 'Disaster'
AND a.disaster_key = c.disaster_key AND b.cost_key = c.cost_key AND d.location_key = c.location_key

GROUP  BY d.city, a.disaster_category;


/* Roll down
Determining the total number of fatalities IN each province during 1999
*/

Select l.province, Count(df.fatalities) as fatalities

FROM location_dimension l, disaster_fact df, disaster_dimension dd, date_dimension ddd

WHERE l.location_key = df.location_key AND ddd.year = 1999 AND ddd.date_key = df.date_key AND dd.disaster_key = df.disaster_key

GROUP by l.province;


/*Dice/ Roll down
Determining the total number of fatalities caused by a Fire IN each province during 1999 
*/
Select l.province, Count(df.fatalities) as fatalities

FROM location_dimension l, disaster_fact df, disaster_dimension dd, date_dimension ddd

WHERE l.location_key = df.location_key AND ddd.year = 1990 AND ddd.date_key = df.date_key AND dd.disaster_type = 'Wildfire' AND df.disaster_key = df.disaster_key

GROUP by l.province;



