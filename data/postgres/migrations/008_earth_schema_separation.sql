-- Separate the longitudinal Earth authority from CIVSTATE without copying rows.
-- Existing snapshots, table content, and CIVSTATE objects remain unchanged.
CREATE SCHEMA IF NOT EXISTS loom_earth AUTHORIZATION ubuntu;

ALTER TABLE loom_civ.earth_derivation SET SCHEMA loom_earth;
ALTER TABLE loom_civ.earth_area SET SCHEMA loom_earth;
ALTER TABLE loom_civ.earth_demographic_year SET SCHEMA loom_earth;
ALTER TABLE loom_civ.earth_biological_cohort_year SET SCHEMA loom_earth;
ALTER TABLE loom_civ.earth_economic_year SET SCHEMA loom_earth;
ALTER TABLE loom_civ.earth_sector_year SET SCHEMA loom_earth;
ALTER TABLE loom_civ.earth_sector_asset_year SET SCHEMA loom_earth;
ALTER TABLE loom_civ.earth_legacy_labor_year SET SCHEMA loom_earth;
ALTER TABLE loom_civ.earth_labor_composition_year SET SCHEMA loom_earth;

-- Preserve the existing read-only role's access to the moved authority.
GRANT USAGE ON SCHEMA loom_earth TO loom_viewer;

DO $$
DECLARE
    expected text[] := ARRAY[
        'earth_area', 'earth_biological_cohort_year', 'earth_demographic_year',
        'earth_derivation', 'earth_economic_year', 'earth_labor_composition_year',
        'earth_legacy_labor_year', 'earth_sector_asset_year', 'earth_sector_year'
    ];
    actual text[];
BEGIN
    SELECT array_agg(c.relname ORDER BY c.relname)
      INTO actual
      FROM pg_class c
      JOIN pg_namespace n ON n.oid = c.relnamespace
     WHERE n.nspname = 'loom_earth' AND c.relkind = 'r';
    IF actual IS DISTINCT FROM expected THEN
        RAISE EXCEPTION 'Earth schema guard failed: %', actual;
    END IF;
    IF EXISTS (
        SELECT 1
          FROM pg_class c
          JOIN pg_namespace n ON n.oid = c.relnamespace
         WHERE n.nspname = 'loom_civ' AND c.relkind = 'r'
           AND c.relname LIKE 'earth_%'
    ) THEN
        RAISE EXCEPTION 'Earth base table remains in loom_civ';
    END IF;
END $$;
