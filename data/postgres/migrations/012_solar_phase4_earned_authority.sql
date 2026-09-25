-- Promote only Solar ephemeris authority already earned before Phase-4 2250 closure.
-- Physical bodies and system barycenters are distinct identities. This migration
-- intentionally preserves partial coverage for Ceres and Saturn; later Phase-4
-- migrations must close those horizon holes rather than overstating authority.

BEGIN;

DO $$
BEGIN
  IF to_regclass('loom_solar.body') IS NULL
     OR to_regclass('loom_solar.body_identifier') IS NULL
     OR to_regclass('loom_solar.ephemeris_source') IS NULL
     OR to_regclass('loom_solar.ephemeris_coverage') IS NULL
  THEN
    RAISE EXCEPTION 'Solar earned-authority promotion requires migration 009 schema';
  END IF;

  IF EXISTS (SELECT 1 FROM loom_solar.body)
     OR EXISTS (SELECT 1 FROM loom_solar.body_identifier)
     OR EXISTS (SELECT 1 FROM loom_solar.ephemeris_source)
     OR EXISTS (SELECT 1 FROM loom_solar.ephemeris_coverage)
  THEN
    RAISE EXCEPTION 'Solar earned-authority promotion expects empty loom_solar metadata tables';
  END IF;
END $$;

INSERT INTO loom_solar.body(body_id, canonical_name, body_class, status) VALUES
 ('MERCURY_SYSTEM_BARYCENTER','Mercury system barycenter','BARYCENTER','ACTIVE'),
 ('VENUS_SYSTEM_BARYCENTER','Venus system barycenter','BARYCENTER','ACTIVE'),
 ('EARTH_MOON_BARYCENTER','Earth-Moon barycenter','BARYCENTER','ACTIVE'),
 ('MARS_SYSTEM_BARYCENTER','Mars system barycenter','BARYCENTER','ACTIVE'),
 ('JUPITER_SYSTEM_BARYCENTER','Jupiter system barycenter','BARYCENTER','ACTIVE'),
 ('SATURN_SYSTEM_BARYCENTER','Saturn system barycenter','BARYCENTER','ACTIVE'),
 ('URANUS_SYSTEM_BARYCENTER','Uranus system barycenter','BARYCENTER','ACTIVE'),
 ('NEPTUNE_SYSTEM_BARYCENTER','Neptune system barycenter','BARYCENTER','ACTIVE'),
 ('PLUTO_SYSTEM_BARYCENTER','Pluto system barycenter','BARYCENTER','ACTIVE'),
 ('SUN','Sun','STAR','ACTIVE'),
 ('MERCURY','Mercury','PLANET','ACTIVE'),
 ('VENUS','Venus','PLANET','ACTIVE'),
 ('EARTH','Earth','PLANET','ACTIVE'),
 ('MOON','Moon','NATURAL_SATELLITE','ACTIVE'),
 ('CERES','Ceres','DWARF_PLANET','ACTIVE'),
 ('MARS','Mars','PLANET','ACTIVE'),
 ('SATURN','Saturn','PLANET','ACTIVE'),
 ('URANUS','Uranus','PLANET','ACTIVE'),
 ('NEPTUNE','Neptune','PLANET','ACTIVE');

INSERT INTO loom_solar.body_identifier(body_id,authority,identifier_type,identifier_value,status) VALUES
 ('MERCURY_SYSTEM_BARYCENTER','NAIF','NAIF_ID','1','ACTIVE'),
 ('VENUS_SYSTEM_BARYCENTER','NAIF','NAIF_ID','2','ACTIVE'),
 ('EARTH_MOON_BARYCENTER','NAIF','NAIF_ID','3','ACTIVE'),
 ('MARS_SYSTEM_BARYCENTER','NAIF','NAIF_ID','4','ACTIVE'),
 ('JUPITER_SYSTEM_BARYCENTER','NAIF','NAIF_ID','5','ACTIVE'),
 ('SATURN_SYSTEM_BARYCENTER','NAIF','NAIF_ID','6','ACTIVE'),
 ('URANUS_SYSTEM_BARYCENTER','NAIF','NAIF_ID','7','ACTIVE'),
 ('NEPTUNE_SYSTEM_BARYCENTER','NAIF','NAIF_ID','8','ACTIVE'),
 ('PLUTO_SYSTEM_BARYCENTER','NAIF','NAIF_ID','9','ACTIVE'),
 ('SUN','NAIF','NAIF_ID','10','ACTIVE'),
 ('MERCURY','NAIF','NAIF_ID','199','ACTIVE'),
 ('VENUS','NAIF','NAIF_ID','299','ACTIVE'),
 ('MOON','NAIF','NAIF_ID','301','ACTIVE'),
 ('EARTH','NAIF','NAIF_ID','399','ACTIVE'),
 ('MARS','NAIF','NAIF_ID','499','ACTIVE'),
 ('SATURN','NAIF','NAIF_ID','699','ACTIVE'),
 ('URANUS','NAIF','NAIF_ID','799','ACTIVE'),
 ('NEPTUNE','NAIF','NAIF_ID','899','ACTIVE'),
 ('CERES','NAIF','NAIF_ID','20000001','ACTIVE');

INSERT INTO loom_solar.ephemeris_source(
 ephemeris_source_id,provider,product_name,product_version,asset_filename,
 sha256,byte_count,source_url,acquired_at,status
) VALUES
 ('DE440','JPL/NAIF','DE440','440','de440.bsp',
  'a4ce9bf9b3282becc9f4b2ac3cebe03a2ae7599981aabd7265fd8482fff7c4b5',119799808,
  'https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/de440.bsp',
  '2026-09-24T21:39:02.529102Z','QUALIFIED'),
 ('CERES_SPK_2025_2227','JPL/Horizons','Ceres supplementary SPK','2025-2227',
  '2000001_ceres_2025_2227.bsp',
  'adb69cc0723550fad437b7466fedaf7480e2e36c489e9d2d727e783a78566137',3678208,
  'https://ssd.jpl.nasa.gov/api/horizons.api','2026-09-24T22:08:07.347328Z','QUALIFIED'),
 ('JPL_MAR099','JPL/NAIF','MAR099','MAR099.01','mar099.bsp',
  '9991e57b196bae1a096acc6e2afc6718102ee420d684695de0f0333064c046bc',1227574272,
  'https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/satellites/mar099.bsp',
  '2026-09-25T01:32:16Z','QUALIFIED'),
 ('JPL_SAT441','JPL/NAIF','SAT441','SAT441.24','sat441.bsp',
  'd7e444a9ba7a52b8f448ff0747030789524d2f0c1212e4e2bd7f5fc3c96444d5',661592064,
  'https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/satellites/sat441.bsp',
  '2026-09-25T01:32:16Z','QUALIFIED'),
 ('JPL_URA184_PART_3','JPL/NAIF','URA184 part 3','URA184 (NAIF 799 solution URA182.21)','ura184_part-3.bsp',
  '273cd4ccc470d1098562cd4e94fa48fc2b4c6b1c2896308e473c949b87937c53',386885632,
  'https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/satellites/ura184_part-3.bsp',
  '2026-09-25T01:32:16Z','QUALIFIED'),
 ('JPL_NEP097','JPL/NAIF','NEP097','NEP097 / ephemeris version 24','nep097.bsp',
  '5c1132fdc48c54e5d2e4eb663e1ed1a876911eae9433c203f29a5a1b5e1fa9b1',105262080,
  'https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/satellites/nep097.bsp',
  '2026-09-25T01:32:16Z','QUALIFIED');

-- DE440 contains all 14 promoted targets over the same declared interval.
INSERT INTO loom_solar.ephemeris_coverage(
 ephemeris_source_id,body_id,valid_from,valid_until,reference_frame,units,coverage_class,status
)
SELECT 'DE440', body_id,
 '1549-12-30T23:59:18.815889Z','2650-01-24T23:58:50.815708Z',
 'ECLIPJ2000','km,km/s','BODY','QUALIFIED'
FROM (VALUES
 ('MERCURY_SYSTEM_BARYCENTER'),('VENUS_SYSTEM_BARYCENTER'),('EARTH_MOON_BARYCENTER'),
 ('MARS_SYSTEM_BARYCENTER'),('JUPITER_SYSTEM_BARYCENTER'),('SATURN_SYSTEM_BARYCENTER'),
 ('URANUS_SYSTEM_BARYCENTER'),('NEPTUNE_SYSTEM_BARYCENTER'),('PLUTO_SYSTEM_BARYCENTER'),
 ('SUN'),('MERCURY'),('VENUS'),('MOON'),('EARTH')
) AS earned(body_id);

INSERT INTO loom_solar.ephemeris_coverage(
 ephemeris_source_id,body_id,valid_from,valid_until,reference_frame,units,coverage_class,status
) VALUES
 ('CERES_SPK_2025_2227','CERES','2024-12-31T23:58:50.816Z','2226-12-31T23:58:50.816Z','ECLIPJ2000','km,km/s','BODY','QUALIFIED'),
 ('JPL_MAR099','MARS','1599-12-31T23:59:18.815889Z','2600-01-01T23:58:50.816341Z','ECLIPJ2000','km,km/s','BODY','QUALIFIED'),
 ('JPL_SAT441','SATURN','1749-12-29T23:59:18.816003Z','2250-01-05T23:58:50.816055Z','ECLIPJ2000','km,km/s','BODY','QUALIFIED'),
 ('JPL_URA184_PART_3','URANUS','1600-01-03T23:59:18.815802Z','2399-12-16T23:58:50.816698Z','ECLIPJ2000','km,km/s','BODY','QUALIFIED'),
 ('JPL_NEP097','NEPTUNE','1600-01-09T23:59:18.815630Z','2399-12-30T23:58:50.816313Z','ECLIPJ2000','km,km/s','BODY','QUALIFIED');

DO $$
DECLARE
 body_count integer;
 coverage_count integer;
BEGIN
 SELECT count(*) INTO body_count FROM loom_solar.body;
 SELECT count(*) INTO coverage_count FROM loom_solar.ephemeris_coverage WHERE status='QUALIFIED';
 IF body_count <> 19 OR coverage_count <> 19 THEN
   RAISE EXCEPTION 'Solar earned-authority promotion expected 19 bodies/19 qualified coverage rows, got %/%',
     body_count, coverage_count;
 END IF;
END $$;

COMMIT;
