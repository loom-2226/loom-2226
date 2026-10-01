BEGIN;

-- LOOM Solar V1 physical qualification interval begins at
-- 2026-01-01 00:00:00 TDB = ET 820497600.0.
--
-- Migration 020 projected the legacy human-readable UTC valid_from value
-- (2026-01-01T00:00:00Z) into native ET, producing 820497669.18392 and a
-- spurious 69.18392-second hole. The primary SPKs for all three rows have
-- been independently verified to contain finite state at ET 820497600.0.
DO $$
DECLARE n integer;
BEGIN
  SELECT count(*) INTO n
  FROM loom_solar.ephemeris_coverage
  WHERE (ephemeris_source_id, body_id) IN (
    ('NAIF_NEP101XL_802','NEREID'),
    ('PROP_4E_PIONEER10','PIONEER10'),
    ('PROP_4E_PIONEER11','PIONEER11')
  )
  AND status='QUALIFIED'
  AND abs(coverage_start_et - 820497669.18392) < 1e-6;
  IF n <> 3 THEN
    RAISE EXCEPTION 'expected exactly 3 legacy UTC-projected V1 boundary rows, found %', n;
  END IF;
END $$;

UPDATE loom_solar.ephemeris_coverage
SET coverage_start_et = 820497600.0
WHERE (ephemeris_source_id, body_id) IN (
  ('NAIF_NEP101XL_802','NEREID'),
  ('PROP_4E_PIONEER10','PIONEER10'),
  ('PROP_4E_PIONEER11','PIONEER11')
)
AND status='QUALIFIED';

COMMIT;
