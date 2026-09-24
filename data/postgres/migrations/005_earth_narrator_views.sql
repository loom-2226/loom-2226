CREATE OR REPLACE VIEW loom_narrator.current_earth_snapshot AS
SELECT s.snapshot_id
FROM loom_control.snapshot s
JOIN loom_control.model_context_record m
  ON m.snapshot_id=s.snapshot_id AND m.context_key='model_designation'
WHERE s.state='VALIDATED'
  AND m.context_value #>> '{}'='EARTH_LEAN_BIOSYNTHETIC_COUPLED_SUCCESSOR_v0_1_2026_09_24'
ORDER BY s.created_at DESC LIMIT 1;

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
             sum(total_effective_labor) total_effective_labor,
             sum(recognized_person_population) recognized_person_population
      FROM loom_civ.earth_labor_composition_year JOIN sid USING(snapshot_id) GROUP BY year)
SELECT sid.snapshot_id,d.year,d.biological_population,l.synthetic_population,
       l.recognized_person_population,d.age_under_20,d.age_20_64,d.age_65_plus,
       d.age_80_plus,d.age_100_plus,d.age_120_plus,d.age_150_plus,
       l.biological_effective_labor,l.synthetic_effective_labor,l.machine_task_capacity,
       l.total_effective_labor,e.value_added,e.gross_output,e.investment,e.capital,
       CASE WHEN d.year<=2100 THEN 'WPP_2024_MEDIUM' ELSE 'MED_CENTRAL' END demographic_status,
       CASE WHEN d.year<=2100 THEN 'V4_PREDECESSOR' ELSE 'MED_CENTRAL__SYNTH_CENTRAL' END economic_status
FROM sid CROSS JOIN d LEFT JOIN e USING(year) LEFT JOIN l USING(year);

CREATE OR REPLACE VIEW loom_narrator.current_country_year AS
WITH sid AS (SELECT snapshot_id FROM loom_narrator.current_earth_snapshot)
SELECT a.snapshot_id,a.iso3,a.display_name,d.year,d.biological_population,d.births,d.deaths,
       d.median_age,d.age_under_20,d.age_20_64,d.age_65_plus,d.age_80_plus,
       d.age_100_plus,d.age_120_plus,d.age_150_plus,e.value_added,e.gross_output,
       e.investment,e.capital,ll.legacy_employment,ll.legacy_labor_force,
       l.labor_capable_biological_population,l.biological_effective_labor,
       l.synthetic_population,l.synthetic_effective_labor,l.machine_task_capacity,
       l.total_effective_labor,l.recognized_person_population,
       a.economic_qualified,
       CASE WHEN e.iso3 IS NULL THEN 'DEMOGRAPHY_ONLY' ELSE 'ECONOMICALLY_QUALIFIED' END economic_coverage,
       CASE WHEN l.iso3 IS NULL THEN 'NOT_MODELED_BY_THIS_AUTHORITY' ELSE 'MODELED' END biosynthetic_labor_coverage
FROM sid JOIN loom_civ.earth_area a USING(snapshot_id)
JOIN loom_civ.earth_demographic_year d USING(snapshot_id,iso3)
LEFT JOIN loom_civ.earth_economic_year e USING(snapshot_id,iso3,year)
LEFT JOIN loom_civ.earth_legacy_labor_year ll USING(snapshot_id,iso3,year)
LEFT JOIN loom_civ.earth_labor_composition_year l USING(snapshot_id,iso3,year);

CREATE OR REPLACE VIEW loom_narrator.fact_semantics AS
SELECT v.* FROM loom_control.variable_semantics v
JOIN loom_narrator.current_earth_snapshot s USING(snapshot_id);
CREATE OR REPLACE VIEW loom_narrator.model_context AS
SELECT m.* FROM loom_control.model_context_record m
JOIN loom_narrator.current_earth_snapshot s USING(snapshot_id);
CREATE OR REPLACE VIEW loom_narrator.temporal_coverage AS
SELECT c.* FROM loom_control.temporal_coverage c
JOIN loom_narrator.current_earth_snapshot s USING(snapshot_id);

CREATE OR REPLACE VIEW loom_narrator.current_country_fact AS
SELECT c.snapshot_id,c.iso3 subject_id,c.year,v.variable_key,
 CASE v.variable_key
  WHEN 'DEM.BIO_POP' THEN c.biological_population
  WHEN 'DEM.SYNTH_POP' THEN c.synthetic_population
  WHEN 'DEM.RECOGNIZED_POP' THEN c.recognized_person_population
  WHEN 'DEM.MEDIAN_AGE' THEN c.median_age
  WHEN 'DEM.AGE_UNDER_20' THEN c.age_under_20
  WHEN 'DEM.AGE_20_64' THEN c.age_20_64
  WHEN 'DEM.AGE_65_PLUS' THEN c.age_65_plus
  WHEN 'DEM.AGE_80_PLUS' THEN c.age_80_plus
  WHEN 'DEM.AGE_100_PLUS' THEN c.age_100_plus
  WHEN 'DEM.AGE_120_PLUS' THEN c.age_120_plus
  WHEN 'DEM.AGE_150_PLUS' THEN c.age_150_plus
  WHEN 'WORK.LEGACY_EMPLOYMENT' THEN c.legacy_employment
  WHEN 'WORK.LABOR_CAPABLE_BIO' THEN c.labor_capable_biological_population
  WHEN 'WORK.BIO_EFFECTIVE_LABOR' THEN c.biological_effective_labor
  WHEN 'WORK.SYNTH_EFFECTIVE_LABOR' THEN c.synthetic_effective_labor
  WHEN 'WORK.MACHINE_TASK_CAPACITY' THEN c.machine_task_capacity
  WHEN 'WORK.TOTAL_EFFECTIVE_LABOR' THEN c.total_effective_labor
  WHEN 'ECON.VALUE_ADDED' THEN c.value_added
  WHEN 'ECON.GROSS_OUTPUT' THEN c.gross_output
  WHEN 'ECON.CAPITAL' THEN c.capital
  WHEN 'ECON.INVESTMENT' THEN c.investment END numeric_value,
 v.unit,v.definition,v.epistemic_status,v.derivation_method derivation_id,
 v.source_artifact_hashes source_artifact,v.misuse_warning
FROM loom_narrator.current_country_year c
JOIN loom_narrator.fact_semantics v ON true
WHERE CASE v.variable_key
  WHEN 'DEM.BIO_POP' THEN c.biological_population
  WHEN 'DEM.SYNTH_POP' THEN c.synthetic_population
  WHEN 'DEM.RECOGNIZED_POP' THEN c.recognized_person_population
  WHEN 'DEM.MEDIAN_AGE' THEN c.median_age
  WHEN 'DEM.AGE_UNDER_20' THEN c.age_under_20
  WHEN 'DEM.AGE_20_64' THEN c.age_20_64
  WHEN 'DEM.AGE_65_PLUS' THEN c.age_65_plus
  WHEN 'DEM.AGE_80_PLUS' THEN c.age_80_plus
  WHEN 'DEM.AGE_100_PLUS' THEN c.age_100_plus
  WHEN 'DEM.AGE_120_PLUS' THEN c.age_120_plus
  WHEN 'DEM.AGE_150_PLUS' THEN c.age_150_plus
  WHEN 'WORK.LEGACY_EMPLOYMENT' THEN c.legacy_employment
  WHEN 'WORK.LABOR_CAPABLE_BIO' THEN c.labor_capable_biological_population
  WHEN 'WORK.BIO_EFFECTIVE_LABOR' THEN c.biological_effective_labor
  WHEN 'WORK.SYNTH_EFFECTIVE_LABOR' THEN c.synthetic_effective_labor
  WHEN 'WORK.MACHINE_TASK_CAPACITY' THEN c.machine_task_capacity
  WHEN 'WORK.TOTAL_EFFECTIVE_LABOR' THEN c.total_effective_labor
  WHEN 'ECON.VALUE_ADDED' THEN c.value_added
  WHEN 'ECON.GROSS_OUTPUT' THEN c.gross_output
  WHEN 'ECON.CAPITAL' THEN c.capital
  WHEN 'ECON.INVESTMENT' THEN c.investment END IS NOT NULL;

REVOKE ALL ON SCHEMA loom_narrator FROM PUBLIC;
GRANT USAGE ON SCHEMA loom_narrator TO PUBLIC;
GRANT SELECT ON ALL TABLES IN SCHEMA loom_narrator TO PUBLIC;
