-- LOOM Solar Phase 4B closure.
-- Direct JPL/NAIF/Horizons authority is preferred where it reaches the horizon.
-- Jupiter/Pluto post-horizon records are explicit empirical propagations from
-- authoritative predecessor states; they are not direct JPL authority.

ALTER TABLE loom_solar.ephemeris_source
    ADD COLUMN state_capability text NOT NULL DEFAULT 'DIRECT_SPICE_2250_QUALIFIED'
        CHECK (state_capability IN (
            'DIRECT_SPICE_2250_QUALIFIED',
            'DIRECT_SPICE_PARTIAL_2226',
            'DIRECT_SPICE_PARTIAL_2200',
            'DIRECT_SPICE_PARTIAL_2199',
            'EMPIRICAL_PROPAGATED_2250'
        )),
    ADD COLUMN navigation_grade boolean NOT NULL DEFAULT true,
    ADD COLUMN uncertainty_km numeric NULL CHECK (uncertainty_km IS NULL OR uncertainty_km >= 0),
    ADD COLUMN source_lineage text NULL;

UPDATE loom_solar.ephemeris_source
SET state_capability = CASE
        WHEN ephemeris_source_id = 'JPL_SAT441' THEN 'DIRECT_SPICE_PARTIAL_2200'
        WHEN ephemeris_source_id = 'CERES_SPK_2025_2227' THEN 'DIRECT_SPICE_PARTIAL_2226'
        ELSE state_capability
    END
WHERE ephemeris_source_id IN ('JPL_SAT441', 'CERES_SPK_2025_2227');

UPDATE loom_solar.ephemeris_coverage
SET status = 'RETIRED'
WHERE ephemeris_source_id IN ('JPL_SAT441', 'CERES_SPK_2025_2227');

UPDATE loom_solar.ephemeris_source
SET status = 'RETIRED'
WHERE ephemeris_source_id IN ('JPL_SAT441', 'CERES_SPK_2025_2227');

INSERT INTO loom_solar.body(body_id, canonical_name, body_class, parent_body_id, status) VALUES
 ('JUPITER','Jupiter','PLANET','JUPITER_SYSTEM_BARYCENTER','ACTIVE'),
 ('IO','Io','NATURAL_SATELLITE','JUPITER_SYSTEM_BARYCENTER','ACTIVE'),
 ('EUROPA','Europa','NATURAL_SATELLITE','JUPITER_SYSTEM_BARYCENTER','ACTIVE'),
 ('GANYMEDE','Ganymede','NATURAL_SATELLITE','JUPITER_SYSTEM_BARYCENTER','ACTIVE'),
 ('CALLISTO','Callisto','NATURAL_SATELLITE','JUPITER_SYSTEM_BARYCENTER','ACTIVE'),
 ('PLUTO','Pluto','DWARF_PLANET','PLUTO_SYSTEM_BARYCENTER','ACTIVE'),
 ('CHARON','Charon','NATURAL_SATELLITE','PLUTO_SYSTEM_BARYCENTER','ACTIVE');

INSERT INTO loom_solar.body_identifier(body_id, authority, identifier_type, identifier_value, status) VALUES
 ('JUPITER','NAIF','NAIF_ID','599','ACTIVE'),
 ('IO','NAIF','NAIF_ID','501','ACTIVE'),
 ('EUROPA','NAIF','NAIF_ID','502','ACTIVE'),
 ('GANYMEDE','NAIF','NAIF_ID','503','ACTIVE'),
 ('CALLISTO','NAIF','NAIF_ID','504','ACTIVE'),
 ('PLUTO','NAIF','NAIF_ID','999','ACTIVE'),
 ('CHARON','NAIF','NAIF_ID','901','ACTIVE');

INSERT INTO loom_solar.ephemeris_source(
 ephemeris_source_id, provider, product_name, product_version, asset_filename,
 sha256, byte_count, source_url, acquired_at, status, state_capability,
 navigation_grade, uncertainty_km, source_lineage
) VALUES
 ('CERES_SPK_PHASE4B_2251','JPL/Horizons','Ceres supplementary SPK','2025-2251-guard',
  '2000001_ceres_2025_2251_guard.bsp',
  'e90bf70280961d61f7b505a5d2a9c39abcc558d9a2442570e4c0e384aa9f0956',4106240,
  'https://ssd.jpl.nasa.gov/api/horizons.api','2026-09-25T00:00:00Z','QUALIFIED',
  'DIRECT_SPICE_2250_QUALIFIED',true,NULL,'JPL/Horizons orbit solution'),
 ('JPL_SAT441XL_PART2','JPL/NAIF','sat441xl_part-2','2022-05-24',
  'sat441xl_part-2.bsp',
  'd021819387e6045e2cd2819a7907ca62cc8cb3091ca925dfe894d2e0f4f7af1e',2021645312,
  'https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/satellites/sat441xl_part-2.bsp',
  '2026-09-25T00:00:00Z','QUALIFIED','DIRECT_SPICE_2250_QUALIFIED',true,NULL,
  'JPL/NAIF sat441xl_part-2 plus DE440 planetary backbone'),
 ('JPL_JUP365_PRE2250','JPL/NAIF','JUP365','JUP365','jup365.bsp',
  'dbf016c01ba4d022154838000cf3f06962cf958ddc503a366f7fe8f81495c5cb',1136581632,
  'https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/satellites/jup365.bsp',
  '2026-09-25T00:00:00Z','QUALIFIED','DIRECT_SPICE_PARTIAL_2200',true,NULL,
  'JPL/NAIF JUP365 predecessor authority'),
 ('JPL_PLU060_PRE2250','JPL/NAIF','PLU060','PLU060','plu060.bsp',
  'dfbb102491a26ed41ae08ca3f8963f22f0219df1d8f265ab87b9ad825a826fc6',135207936,
  'https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/satellites/plu060.bsp',
  '2026-09-25T00:00:00Z','QUALIFIED','DIRECT_SPICE_PARTIAL_2199',true,NULL,
  'JPL/NAIF PLU060 predecessor authority'),
 ('PROP_JUPITER_599_PHASE4B','LOOM/JPL-NASA-derived','Phase-4B Jupiter propagation SPK',
  'LOOM_SOLAR_PHASE4B_RK4_NBODY_V1','propagated_599_from_5_2251.bsp',
  '626c3425323eea7999a7701604c7ea80f00a70b1946e24ef208247a22fd6c5f7',2094080,
  'JUP365 + DE440 authoritative initial state; local deterministic propagation',
  '2026-09-25T00:00:00Z','QUALIFIED','EMPIRICAL_PROPAGATED_2250',false,1000.0,
  'JPL_JUP365_PRE2250;DE440;LOOM_SOLAR_PHASE4B_RK4_NBODY_V1'),
 ('PROP_IO_501_PHASE4B','LOOM/JPL-NASA-derived','Phase-4B Io propagation SPK',
  'LOOM_SOLAR_PHASE4B_RK4_NBODY_V1','propagated_501_from_5_2251.bsp',
  '78bea0d67a28c0c4fe04c83ad840f6cd9a3ad98c71469cd3d47c25e601624a0d',2094080,
  'JUP365 + DE440 authoritative initial state; local deterministic propagation',
  '2026-09-25T00:00:00Z','QUALIFIED','EMPIRICAL_PROPAGATED_2250',false,1000000.0,
  'JPL_JUP365_PRE2250;DE440;LOOM_SOLAR_PHASE4B_RK4_NBODY_V1'),
 ('PROP_EUROPA_502_PHASE4B','LOOM/JPL-NASA-derived','Phase-4B Europa propagation SPK',
  'LOOM_SOLAR_PHASE4B_RK4_NBODY_V1','propagated_502_from_5_2251.bsp',
  'a7fe17be71d02b01c7dc0a6510280d62cbdc3e79dbd1a760e959d1888a717c59',2094080,
  'JUP365 + DE440 authoritative initial state; local deterministic propagation',
  '2026-09-25T00:00:00Z','QUALIFIED','EMPIRICAL_PROPAGATED_2250',false,1000000.0,
  'JPL_JUP365_PRE2250;DE440;LOOM_SOLAR_PHASE4B_RK4_NBODY_V1'),
 ('PROP_GANYMEDE_503_PHASE4B','LOOM/JPL-NASA-derived','Phase-4B Ganymede propagation SPK',
  'LOOM_SOLAR_PHASE4B_RK4_NBODY_V1','propagated_503_from_5_2251.bsp',
  '48df30179445d0dab12d1799c9f865f4eaf2521ef133df2dc771f80c097c415b',2094080,
  'JUP365 + DE440 authoritative initial state; local deterministic propagation',
  '2026-09-25T00:00:00Z','QUALIFIED','EMPIRICAL_PROPAGATED_2250',false,1000000.0,
  'JPL_JUP365_PRE2250;DE440;LOOM_SOLAR_PHASE4B_RK4_NBODY_V1'),
 ('PROP_CALLISTO_504_PHASE4B','LOOM/JPL-NASA-derived','Phase-4B Callisto propagation SPK',
  'LOOM_SOLAR_PHASE4B_RK4_NBODY_V1','propagated_504_from_5_2251.bsp',
  'ff4e91bf041ab350f6afc4304c178dd884396a4d5db5ed02e8f1c2960960d732',2094080,
  'JUP365 + DE440 authoritative initial state; local deterministic propagation',
  '2026-09-25T00:00:00Z','QUALIFIED','EMPIRICAL_PROPAGATED_2250',false,1000000.0,
  'JPL_JUP365_PRE2250;DE440;LOOM_SOLAR_PHASE4B_RK4_NBODY_V1'),
 ('PROP_PLUTO_999_PHASE4B','LOOM/JPL-NASA-derived','Phase-4B Pluto propagation SPK',
  'LOOM_SOLAR_PHASE4B_RK4_NBODY_V1','propagated_999_from_9_2251.bsp',
  'abb7de2d27ca3bb6a7124133f634491cf806b2c4680bcd14e8aef84c90ce19d8',2095104,
  'PLU060 + DE440 authoritative initial state; local deterministic propagation',
  '2026-09-25T00:00:00Z','QUALIFIED','EMPIRICAL_PROPAGATED_2250',false,1000000.0,
  'JPL_PLU060_PRE2250;DE440;LOOM_SOLAR_PHASE4B_RK4_NBODY_V1'),
 ('PROP_CHARON_901_PHASE4B','LOOM/JPL-NASA-derived','Phase-4B Charon propagation SPK',
  'LOOM_SOLAR_PHASE4B_RK4_NBODY_V1','propagated_901_from_9_2251.bsp',
  '24b63919c90e4de152ca2e612b7469fe4600c31f2a1c684c300cc43a7bfc29c5',2095104,
  'PLU060 + DE440 authoritative initial state; local deterministic propagation',
  '2026-09-25T00:00:00Z','QUALIFIED','EMPIRICAL_PROPAGATED_2250',false,1000000.0,
  'JPL_PLU060_PRE2250;DE440;LOOM_SOLAR_PHASE4B_RK4_NBODY_V1');

INSERT INTO loom_solar.ephemeris_coverage(
 ephemeris_source_id, body_id, valid_from, valid_until, reference_frame, units,
 coverage_class, status
) VALUES
 ('CERES_SPK_PHASE4B_2251','CERES','2024-12-31T23:58:50.816Z','2251-01-02T23:58:50.816Z','ECLIPJ2000','km,km/s','BODY','QUALIFIED'),
 ('JPL_SAT441XL_PART2','SATURN','2014-09-27T23:58:52.818Z','4500-01-17T23:58:50.817Z','ECLIPJ2000','km,km/s','BODY','QUALIFIED'),
 ('JPL_JUP365_PRE2250','JUPITER','1600-01-09T23:59:18.816Z','2200-01-09T23:58:50.816Z','ECLIPJ2000','km,km/s','BODY','QUALIFIED'),
 ('JPL_JUP365_PRE2250','IO','1600-01-09T23:59:18.816Z','2200-01-09T23:58:50.816Z','ECLIPJ2000','km,km/s','BODY','QUALIFIED'),
 ('JPL_JUP365_PRE2250','EUROPA','1600-01-09T23:59:18.816Z','2200-01-09T23:58:50.816Z','ECLIPJ2000','km,km/s','BODY','QUALIFIED'),
 ('JPL_JUP365_PRE2250','GANYMEDE','1600-01-09T23:59:18.816Z','2200-01-09T23:58:50.816Z','ECLIPJ2000','km,km/s','BODY','QUALIFIED'),
 ('JPL_JUP365_PRE2250','CALLISTO','1600-01-09T23:59:18.816Z','2200-01-09T23:58:50.816Z','ECLIPJ2000','km,km/s','BODY','QUALIFIED'),
 ('JPL_PLU060_PRE2250','PLUTO','1800-01-01T23:59:18.816Z','2199-12-29T23:58:50.816Z','ECLIPJ2000','km,km/s','BODY','QUALIFIED'),
 ('JPL_PLU060_PRE2250','CHARON','1800-01-01T23:59:18.816Z','2199-12-29T23:58:50.816Z','ECLIPJ2000','km,km/s','BODY','QUALIFIED'),
 ('PROP_JUPITER_599_PHASE4B','JUPITER','2200-01-09T23:58:50.816Z','2251-01-01T00:00:00.816Z','ECLIPJ2000','km,km/s','DERIVED','QUALIFIED'),
 ('PROP_IO_501_PHASE4B','IO','2200-01-09T23:58:50.816Z','2251-01-01T00:00:00.816Z','ECLIPJ2000','km,km/s','DERIVED','QUALIFIED'),
 ('PROP_EUROPA_502_PHASE4B','EUROPA','2200-01-09T23:58:50.816Z','2251-01-01T00:00:00.816Z','ECLIPJ2000','km,km/s','DERIVED','QUALIFIED'),
 ('PROP_GANYMEDE_503_PHASE4B','GANYMEDE','2200-01-09T23:58:50.816Z','2251-01-01T00:00:00.816Z','ECLIPJ2000','km,km/s','DERIVED','QUALIFIED'),
 ('PROP_CALLISTO_504_PHASE4B','CALLISTO','2200-01-09T23:58:50.816Z','2251-01-01T00:00:00.816Z','ECLIPJ2000','km,km/s','DERIVED','QUALIFIED'),
 ('PROP_PLUTO_999_PHASE4B','PLUTO','2199-12-29T23:58:50.816Z','2251-01-01T00:00:00.816Z','ECLIPJ2000','km,km/s','DERIVED','QUALIFIED'),
 ('PROP_CHARON_901_PHASE4B','CHARON','2199-12-29T23:58:50.816Z','2251-01-01T00:00:00.816Z','ECLIPJ2000','km,km/s','DERIVED','QUALIFIED');

DO $$
DECLARE body_count integer; identifier_count integer; qualified_count integer;
BEGIN
 SELECT count(*) INTO body_count FROM loom_solar.body WHERE status='ACTIVE';
 SELECT count(*) INTO identifier_count FROM loom_solar.body_identifier WHERE status='ACTIVE';
 SELECT count(*) INTO qualified_count FROM loom_solar.ephemeris_coverage WHERE status='QUALIFIED';
 IF body_count <> 26 OR identifier_count <> 26 OR qualified_count <> 33 THEN
   RAISE EXCEPTION 'Phase-4B expected 26 active bodies/26 identifiers/33 qualified coverage rows, got %/%/%', body_count, identifier_count, qualified_count;
 END IF;
END $$;
