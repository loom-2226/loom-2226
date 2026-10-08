-- Solar Phase 4F: explicit low-authority nominal relative-state closure.
-- These products are visualization/game-state estimates, not direct ephemerides
-- and not validated physical propagation. Uncertainty spans the nominal orbit.
BEGIN;
ALTER TABLE loom_solar.ephemeris_source DROP CONSTRAINT ephemeris_source_state_capability_check;
ALTER TABLE loom_solar.ephemeris_source ADD CONSTRAINT ephemeris_source_state_capability_check CHECK (state_capability IN (
 'DIRECT_SPICE_2250_QUALIFIED','DIRECT_SPICE_PARTIAL_1990','DIRECT_SPICE_PARTIAL_2033',
 'DIRECT_SPICE_PARTIAL_2099','DIRECT_SPICE_PARTIAL_2135','DIRECT_SPICE_PARTIAL_2226',
 'DIRECT_SPICE_PARTIAL_2200','DIRECT_SPICE_PARTIAL_2199','EMPIRICAL_PROPAGATED_2250',
 'HORIZONS_SPK_2250_QUALIFIED','EPHEMERIS_PARTIAL','CATALOG_ONLY','UNRESOLVED','ESTIMATED_RELATIVE'));
ALTER TABLE loom_solar.curated_cohort_member DROP CONSTRAINT curated_cohort_member_final_outcome_check;
ALTER TABLE loom_solar.curated_cohort_member ADD CONSTRAINT curated_cohort_member_final_outcome_check CHECK (
 final_outcome IN ('QUALIFIED_DIRECT','QUALIFIED_HORIZONS','QUALIFIED_PROPAGATED','PARTIAL','CATALOG_ONLY','UNRESOLVED','ESTIMATED_RELATIVE'));

INSERT INTO loom_solar.body_identifier(body_id,authority,identifier_type,identifier_value,status) VALUES
 ('DACTYL','LOOM','SPK_TARGET_ID','920000243','ACTIVE'),
 ('SELAM','LOOM','SPK_TARGET_ID','920152830','ACTIVE');

INSERT INTO loom_solar.ephemeris_source(ephemeris_source_id,provider,product_name,product_version,asset_filename,sha256,byte_count,source_url,acquired_at,status,state_capability,navigation_grade,uncertainty_km,source_lineage) VALUES
 ('EST_PROTEUS_808_PHASE4F','LOOM/NASA-JPL-derived estimate','Proteus nominal relative continuation','LOOM_SOLAR_PHASE4F_ESTIMATED_RELATIVE_V1','estimated_proteus_808_2199_2251.bsp','417a08649bafeb79c22139d57bfbfac9e1203e1c69893781d922cbee71f81bcc',25078784,'JPL mean orbital period + NEP098 endpoint anchor','2026-10-01T00:00:00Z','QUALIFIED','ESTIMATED_RELATIVE',false,235526.63521461692,'NEP098 direct endpoint; JPL mean period 1.122315 d; circular nominal continuation'),
 ('EST_DACTYL_PHASE4F','LOOM/NASA-JPL-derived estimate','Dactyl nominal parent-relative state','LOOM_SOLAR_PHASE4F_ESTIMATED_RELATIVE_V1','estimated_dactyl_920000243_2026_2251.bsp','13da938aa1d7e6bf6b531e38eee759fd53306728a785d48840ba91dcb546b0fc',110613504,'NASA Galileo observational geometry','2026-10-01T00:00:00Z','QUALIFIED','ESTIMATED_RELATIVE',false,180.0,'~90 km observed separation; approximate historical period; game-epoch phase unconstrained'),
 ('EST_SELAM_PHASE4F','LOOM/NASA-JPL-derived estimate','Selam nominal parent-relative state','LOOM_SOLAR_PHASE4F_ESTIMATED_RELATIVE_V1','estimated_selam_920152830_2026_2251.bsp','f0d779d38c9fe24d38960ef371da5dcf9f5863bf243f29ad4204f415b3e02c5d',110613504,'NASA Lucy observational geometry','2026-10-01T00:00:00Z','QUALIFIED','ESTIMATED_RELATIVE',false,6.2,'NASA Lucy ~3.1 km separation and ~53 h synchronous period; game-epoch phase unconstrained');

INSERT INTO loom_solar.ephemeris_coverage(ephemeris_source_id,body_id,valid_from,valid_until,reference_frame,units,coverage_class,status,coverage_start_et,coverage_end_et) VALUES
 ('EST_PROTEUS_808_PHASE4F','PROTEUS','2199-12-30T23:58:50.816Z','2251-01-01T23:58:50.816Z','ECLIPJ2000','km,km/s','DERIVED','QUALIFIED',6311304000.0,7920849600.0),
 ('EST_DACTYL_PHASE4F','DACTYL','2025-12-31T23:58:50.816Z','2251-01-01T23:58:50.816Z','ECLIPJ2000','km,km/s','DERIVED','QUALIFIED',820497600.0,7920849600.0),
 ('EST_SELAM_PHASE4F','SELAM','2025-12-31T23:58:50.816Z','2251-01-01T23:58:50.816Z','ECLIPJ2000','km,km/s','DERIVED','QUALIFIED',820497600.0,7920849600.0);

UPDATE loom_solar.curated_cohort_member SET final_outcome='ESTIMATED_RELATIVE',
 reason='Nominal parent-relative state available through 2250 with explicit orbit-scale uncertainty; not direct or propagated truth.'
WHERE body_id IN ('PROTEUS','DACTYL','SELAM');

DO $$ DECLARE b integer; q integer; BEGIN
 SELECT count(*) INTO b FROM loom_solar.body;
 SELECT count(*) INTO q FROM loom_solar.ephemeris_coverage WHERE status='QUALIFIED';
 IF b<>110 OR q<>124 THEN RAISE EXCEPTION 'Phase4F estimate pre-Pluto expected 110 bodies/124 qualified coverage rows, got %/%',b,q; END IF;
END $$;
COMMIT;
