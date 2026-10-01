BEGIN;

-- V1 representable-ET seam convention:
-- the outgoing qualified source owns the exact shared endpoint; the incoming
-- continuation begins at the next representable binary64 ET.  This removes
-- exact-ET ambiguity without creating any representable runtime instant that
-- lacks authority. Human-readable UTC provenance remains unchanged.
DO $$
DECLARE n integer;
BEGIN
  SELECT count(*) INTO n
  FROM loom_solar.ephemeris_coverage
  WHERE ephemeris_source_id IN (
    'PROP_PLU060_EXACT_902_PHASE4F',
    'PROP_PLU060_EXACT_903_PHASE4F',
    'PROP_PLU060_EXACT_904_PHASE4F',
    'PROP_PLU060_EXACT_905_PHASE4F'
  )
    AND body_id IN ('NIX','HYDRA','KERBEROS','STYX')
    AND status='QUALIFIED'
    AND coverage_start_et=6311217600.0;
  IF n <> 4 THEN
    RAISE EXCEPTION 'expected exactly 4 Phase-4F Pluto small-moon seam rows, found %', n;
  END IF;
END $$;

UPDATE loom_solar.ephemeris_coverage
SET coverage_start_et = 6311217600.000001
WHERE ephemeris_source_id IN (
  'PROP_PLU060_EXACT_902_PHASE4F',
  'PROP_PLU060_EXACT_903_PHASE4F',
  'PROP_PLU060_EXACT_904_PHASE4F',
  'PROP_PLU060_EXACT_905_PHASE4F'
)
  AND body_id IN ('NIX','HYDRA','KERBEROS','STYX')
  AND status='QUALIFIED'
  AND coverage_start_et=6311217600.0;

COMMIT;
