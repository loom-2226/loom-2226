-- Solar Phase 4E targeted residual closure: spacecraft direct-source acquisition and explicit propagation seams.
-- No new cohort members are introduced. Derived spacecraft states are non-navigation-grade.

ALTER TABLE loom_solar.ephemeris_source DROP CONSTRAINT ephemeris_source_state_capability_check;
ALTER TABLE loom_solar.ephemeris_source ADD CONSTRAINT ephemeris_source_state_capability_check CHECK (state_capability IN (
 'DIRECT_SPICE_2250_QUALIFIED','DIRECT_SPICE_PARTIAL_1990','DIRECT_SPICE_PARTIAL_2033','DIRECT_SPICE_PARTIAL_2099',
 'DIRECT_SPICE_PARTIAL_2135','DIRECT_SPICE_PARTIAL_2226','DIRECT_SPICE_PARTIAL_2200','DIRECT_SPICE_PARTIAL_2199',
 'EMPIRICAL_PROPAGATED_2250','HORIZONS_SPK_2250_QUALIFIED','EPHEMERIS_PARTIAL','CATALOG_ONLY','UNRESOLVED'));

UPDATE loom_solar.ephemeris_source SET state_capability='DIRECT_SPICE_PARTIAL_1990' WHERE ephemeris_source_id IN ('NAIF_PIONEER10_SPK','NAIF_PIONEER11_SPK');
UPDATE loom_solar.ephemeris_source SET state_capability='DIRECT_SPICE_PARTIAL_2099' WHERE ephemeris_source_id IN ('NAIF_VOYAGER1_SPK','NAIF_VOYAGER2_SPK');
UPDATE loom_solar.ephemeris_coverage SET valid_until='1990-01-02T00:00:00Z' WHERE ephemeris_source_id IN ('NAIF_PIONEER10_SPK','NAIF_PIONEER11_SPK');

INSERT INTO loom_solar.ephemeris_source(ephemeris_source_id,provider,product_name,product_version,asset_filename,sha256,byte_count,source_url,acquired_at,status,state_capability,navigation_grade,uncertainty_km,source_lineage) VALUES
('NAIF_NH_OD164','JPL/PDS/NAIF','New Horizons predicted OD164 SPK','PDS 2024-08','nh_pred_alleph_od164.bsp','b676f0053ee02f6e32f7e2b23ca2e865ec9f424caa3f2710e87aa06621adc050',13074432,'https://naif.jpl.nasa.gov/pub/naif/pds/data/nh-j_p_ss-spice-6-v1.0/nhsp_1000/data/spk/nh_pred_alleph_od164.bsp','2026-09-26T00:00:00Z','QUALIFIED','DIRECT_SPICE_PARTIAL_2033',false,NULL,'Official New Horizons PDS OD164 reconstructed/predicted mission trajectory'),
('PROP_4E_PIONEER10','LOOM/JPL-NASA-derived','Pioneer 10 spacecraft propagation','PHASE4E_RK4_NBODY_V1','propagated_pioneer10_1990_2251.bsp','217611f8da7a264eeeee8920af635fc8ac451872c269eb01c823ef73d2eb5114',4614144,'JPL mission SPK + DE440; local deterministic propagation','2026-09-26T00:00:00Z','QUALIFIED','EMPIRICAL_PROPAGATED_2250',false,1000000000000.0,'Solar gravity + differential DE440 planets; RK4 86400 s; held-out errors recorded'),
('PROP_4E_PIONEER11','LOOM/JPL-NASA-derived','Pioneer 11 spacecraft propagation','PHASE4E_RK4_NBODY_V1','propagated_pioneer11_1990_2251.bsp','d081eb7f4888f3629303102365bd07355374f270a9fd80fc2969db51d8a73dd7',4614144,'JPL mission SPK + DE440; local deterministic propagation','2026-09-26T00:00:00Z','QUALIFIED','EMPIRICAL_PROPAGATED_2250',false,1000000000000.0,'Solar gravity + differential DE440 planets; RK4 86400 s; held-out errors recorded'),
('PROP_4E_VOYAGER1','LOOM/JPL-NASA-derived','Voyager 1 spacecraft propagation','PHASE4E_RK4_NBODY_V1','propagated_voyager1_2100_2251.bsp','68ea2420006b560ae3e59243cd21a3ba515380cb2bfb54d7c9e93e38527014f3',3098624,'JPL mission SPK + DE440; local deterministic propagation','2026-09-26T00:00:00Z','QUALIFIED','EMPIRICAL_PROPAGATED_2250',false,100000000.0,'Solar gravity + differential DE440 planets; RK4 86400 s; held-out errors recorded'),
('PROP_4E_VOYAGER2','LOOM/JPL-NASA-derived','Voyager 2 spacecraft propagation','PHASE4E_RK4_NBODY_V1','propagated_voyager2_2100_2251.bsp','4daa5b72afff049ad909252a35f4b8b34fbcf5fc31c1057a69238da520575726',3098624,'JPL mission SPK + DE440; local deterministic propagation','2026-09-26T00:00:00Z','QUALIFIED','EMPIRICAL_PROPAGATED_2250',false,100000000.0,'Solar gravity + differential DE440 planets; RK4 86400 s; held-out errors recorded'),
('PROP_4E_NEWHORIZONS','LOOM/JPL-NASA-derived','New Horizons spacecraft propagation','PHASE4E_RK4_NBODY_V1','propagated_new_horizons_2033_2251.bsp','f8c7f0e16f1ba9dc3b6ae78b727e656c3059a5035b2e7c280f90edcd91d37506',4470784,'JPL mission SPK + DE440; local deterministic propagation','2026-09-26T00:00:00Z','QUALIFIED','EMPIRICAL_PROPAGATED_2250',false,1000000000.0,'Solar gravity + differential DE440 planets; RK4 86400 s; held-out errors recorded');

INSERT INTO loom_solar.ephemeris_coverage(ephemeris_source_id,body_id,valid_from,valid_until,reference_frame,units,coverage_class,status) VALUES
('NAIF_NH_OD164','NEWHORIZONS','2019-01-01T05:34:32Z','2033-01-01T11:58:51Z','ECLIPJ2000','km,km/s','BODY','QUALIFIED'),
('PROP_4E_PIONEER10','PIONEER10','2026-01-01T00:00:00Z','2251-01-01T00:00:00Z','ECLIPJ2000','km,km/s','DERIVED','QUALIFIED'),
('PROP_4E_PIONEER11','PIONEER11','2026-01-01T00:00:00Z','2251-01-01T00:00:00Z','ECLIPJ2000','km,km/s','DERIVED','QUALIFIED'),
('PROP_4E_VOYAGER1','VOYAGER1','2026-01-01T00:00:00Z','2251-01-01T00:00:00Z','ECLIPJ2000','km,km/s','DERIVED','QUALIFIED'),
('PROP_4E_VOYAGER2','VOYAGER2','2026-01-01T00:00:00Z','2251-01-01T00:00:00Z','ECLIPJ2000','km,km/s','DERIVED','QUALIFIED'),
('PROP_4E_NEWHORIZONS','NEWHORIZONS','2033-01-01T00:00:00Z','2251-01-01T00:00:00Z','ECLIPJ2000','km,km/s','DERIVED','QUALIFIED');

UPDATE loom_solar.curated_cohort_member SET final_outcome='QUALIFIED_PROPAGATED', reason='Explicit LOOM empirical spacecraft propagation from authoritative mission state; held-out comparison recorded; navigation_grade=false.' WHERE body_id IN ('PIONEER10','PIONEER11','VOYAGER1','VOYAGER2','NEWHORIZONS');

DO $$ DECLARE c integer; q integer; BEGIN SELECT count(*) INTO c FROM loom_solar.curated_cohort_member; SELECT count(*) INTO q FROM loom_solar.ephemeris_coverage WHERE status='QUALIFIED'; IF c<>47 OR q<>120 THEN RAISE EXCEPTION 'Phase-4E residual closure expected 47 cohort rows/120 qualified coverage rows, got %/%',c,q; END IF; END $$;
