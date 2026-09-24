CREATE OR REPLACE VIEW loom_narrator.current_earth_year AS
WITH sid AS (SELECT snapshot_id FROM loom_narrator.current_earth_snapshot),
d AS (
 SELECT year, sum(biological_population) biological_population,
        sum(age_under_20) age_under_20, sum(age_20_64) age_20_64,
        sum(age_65_plus) age_65_plus, sum(age_80_plus) age_80_plus,
        sum(age_100_plus) age_100_plus, sum(age_120_plus) age_120_plus,
        sum(age_150_plus) age_150_plus
 FROM loom_civ.earth_demographic_year JOIN sid USING(snapshot_id) GROUP BY year),
e AS (SELECT year,sum(value_added) value_added,sum(gross_output) gross_output,
             sum(investment) investment,sum(capital) capital
      FROM loom_civ.earth_economic_year JOIN sid USING(snapshot_id) GROUP BY year),
l AS (SELECT year,sum(synthetic_population) synthetic_population,
             sum(synthetic_effective_labor) synthetic_effective_labor,
             sum(biological_effective_labor) biological_effective_labor,
             sum(machine_task_capacity) machine_task_capacity,
             sum(total_effective_labor) total_effective_labor
      FROM loom_civ.earth_labor_composition_year JOIN sid USING(snapshot_id) GROUP BY year)
SELECT sid.snapshot_id,d.year,d.biological_population,l.synthetic_population,
       d.biological_population+l.synthetic_population recognized_person_population,
       d.age_under_20,d.age_20_64,d.age_65_plus,d.age_80_plus,d.age_100_plus,
       d.age_120_plus,d.age_150_plus,l.biological_effective_labor,
       l.synthetic_effective_labor,l.machine_task_capacity,l.total_effective_labor,
       e.value_added,e.gross_output,e.investment,e.capital,
       CASE WHEN d.year<=2100 THEN 'WPP_2024_MEDIUM' ELSE 'MED_CENTRAL' END demographic_status,
       CASE WHEN d.year<=2100 THEN 'V4_PREDECESSOR' ELSE 'MED_CENTRAL__SYNTH_CENTRAL' END economic_status
FROM sid CROSS JOIN d LEFT JOIN e USING(year) LEFT JOIN l USING(year);
