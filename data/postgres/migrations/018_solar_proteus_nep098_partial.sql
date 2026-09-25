-- Solar Phase 4E Proteus closure attack.
-- Target scope is exactly PROTEUS / NAIF 808; no new body is inserted.
-- NEP098 Part 3 is direct authoritative coverage through 2199 only.

INSERT INTO loom_solar.ephemeris_source(
    ephemeris_source_id, provider, product_name, product_version,
    asset_filename, sha256, byte_count, source_url, acquired_at, status,
    state_capability, navigation_grade, uncertainty_km, source_lineage
) VALUES (
    'NAIF_NEP098_808', 'JPL/NAIF', 'NEP098 Part 3',
    '2026-07-13 / ephemeris version 25', 'nep098_part-3.bsp',
    '16955f87878e41b16934e697213350bc2d6a1b3e04d98f29ba7e0fce328b4355',
    1791917056,
    'https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/satellites/nep098_part-3.bsp',
    '2026-09-26T00:00:00Z', 'QUALIFIED', 'EPHEMERIS_PARTIAL', true, NULL,
    'Official NEP098 SATORBINT integrated Neptune-system solution; target 808 present; DE442 planetary authority; direct object coverage ends 2199-12-30T23:58:50.816Z'
);

INSERT INTO loom_solar.ephemeris_coverage(
    ephemeris_source_id, body_id, valid_from, valid_until,
    reference_frame, units, coverage_class, status
) VALUES (
    'NAIF_NEP098_808', 'PROTEUS',
    '1799-12-31T23:59:18.816Z', '2199-12-30T23:58:50.816Z',
    'ECLIPJ2000', 'km,km/s', 'BODY', 'QUALIFIED'
);

UPDATE loom_solar.curated_cohort_member
SET final_outcome = 'PARTIAL',
    reason = 'Official NEP098 Part 3 directly contains target 808 through 2199-12-30; no accepted direct or validated propagated authority through 2250.'
WHERE body_id = 'PROTEUS';

DO $$ DECLARE c integer; q integer; o text; BEGIN
    SELECT count(*) INTO c FROM loom_solar.body;
    SELECT count(*) INTO q FROM loom_solar.ephemeris_coverage WHERE status = 'QUALIFIED';
    SELECT final_outcome INTO o FROM loom_solar.curated_cohort_member WHERE body_id = 'PROTEUS';
    IF c <> 110 OR q <> 121 OR o <> 'PARTIAL' THEN
        RAISE EXCEPTION 'Proteus closure expected 110 bodies/121 qualified coverage rows/PARTIAL, got %/%/%', c, q, o;
    END IF;
END $$;
