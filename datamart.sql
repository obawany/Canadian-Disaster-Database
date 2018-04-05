-- Deletion queries to restart db and restart serial

DELETE FROM "cost_dimension";
ALTER SEQUENCE cost_dimension_cost_key_seq RESTART;
Delete FROM "date_dimension";
ALTER SEQUENCE date_dimension_date_key_seq RESTART;
Delete FROM "disaster_dimension";
ALTER SEQUENCE disaster_dimension_disaster_key_seq RESTART;
Delete FROM "location_dimension";
ALTER SEQUENCE location_dimension_location_key_seq RESTART;
Delete FROM "summary_dimension";
ALTER SEQUENCE summary_dimension_description_key_seq RESTART;

Delete FROM "disaster_fact";

-- dont always want to delete this only after i reformat it to utf-8
Delete FROM "placeholder";
ALTER SEQUENCE placeholder_sid_seq RESTART;

-- dont want to delete this only after i have the full csv done
Delete FROM "population_dimension";
ALTER SEQUENCE population_dimension_population_key_seq RESTART;

-- Insert into dimensions
Insert into cost_dimension(normalized_total_cost,federal_dfaa_payment,provincial_dfaa_payment,
provincial_department_payment,insurance_payments,ngo_payments, ogd_cost, municipal_cost, estimated_total_cost ) 
Select "normalized_total_cost", "federal_dfaa_payment", "provincial_dfaa_payment","provincial_department_payment",
"insurance", "ngo_payment", "ogd_cost", "municipal_costs","estimated_total_cost"
FROM placeholder;


Insert into date_dimension(day,month,year,weekend, season_canada)
Select EXTRACT(DAY FROM event_start_date) as day, EXTRACT(MONTH FROM event_start_date) as Month, EXTRACT(YEAR FROM event_start_date) as Year,
	CASE 
	WHEN to_char(event_start_date, 'D') = '7' THEN 'y'
	WHEN to_char(event_start_date, 'D') = '1' then 'y'
	ELSE 'n' 
	END,
	CASE
	WHEN to_char(event_start_date, 'MM') >= '01' AND to_char(event_start_date, 'MM') <= '03'  THEN 'Winter'
	WHEN to_char(event_start_date, 'MM') >= '04' AND to_char(event_start_date, 'MM') <= '06' THEN 'Spring'
	WHEN to_char(event_start_date, 'MM') >= '07' AND to_char(event_start_date, 'MM') <= '09' THEN 'Summer'
	WHEN to_char(event_start_date, 'MM') >= '10' AND to_char(event_start_date, 'MM') <= '12' THEN 'Fall'
	END
FROM placeholder;

Insert into disaster_dimension(disaster_type, disaster_group, disaster_subgroup, disaster_category,
 magnitude, utility_people_affected) 
Select event_type, event_group, event_subgroup, event_category,
 magnitude, utility_people_affected
FROM placeholder;

Insert into location_dimension(city, province, country, canada) 
Select city, province, country,
	CASE 
	WHEN country = 'CA' then 'y'
	ELSE 'n'
	END
FROM placeholder;

INSERT INTO summary_dimension(summary)
SELECT comments
FROM placeholder;

-- fact table
INSERT INTO disaster_fact(start_date_key,location_key, disaster_key, description_key,
cost_key, fatalities, injured, evacuated, population_key)
Select c.cost_key, d.date_key, z.disaster_key, l.location_key, s.description_key, 
p.fatalities, p.injured, p.evacuated, o.population_key 
FROM "cost_dimension" c, "date_dimension" d, "disaster_dimension" z, "location_dimension" l,
"population_dimension" o, "summary_dimension" s, "placeholder" p
WHERE c.cost_key = p.key and p.key = d.date_key AND p.key = z.disaster_key AND 
p.key = l.location_key AND p.key = s.description_key AND o.geographic_name = l.city;

INSERT INTO disaster_fact(cost_key, date_key, disaster_key, description_key, location_key, fatalities, injured, evacuated)
Select c.cost_key, d.date_key, z.disaster_key, s.description_key, l.location_key, p.fatalities, p.injured, p.evacuated
FROM "cost_dimension" c, "placeholder" p, "date_dimension" d, "disaster_dimension" z,
 "summary_dimension" s, "location_dimension" l
WHERE c.cost_key = p.sid AND p.sid = d.date_key AND p.sid = z.disaster_key AND p.sid = s.description_key
AND p.sid = l.location_key;
