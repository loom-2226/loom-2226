-- Solar Phase 4D: strategic small-body identity and horizon authority.
-- Trajectory samples and SPK binaries remain outside PostgreSQL.

ALTER TABLE loom_solar.ephemeris_source
    DROP CONSTRAINT ephemeris_source_state_capability_check;
ALTER TABLE loom_solar.ephemeris_source
    ADD CONSTRAINT ephemeris_source_state_capability_check CHECK (state_capability IN (
      'DIRECT_SPICE_2250_QUALIFIED','DIRECT_SPICE_PARTIAL_2135',
      'DIRECT_SPICE_PARTIAL_2226','DIRECT_SPICE_PARTIAL_2200',
      'DIRECT_SPICE_PARTIAL_2199','EMPIRICAL_PROPAGATED_2250'
    ));

INSERT INTO loom_solar.body(body_id, canonical_name, body_class, status) VALUES
 ('PSYCHE','16 Psyche','ASTEROID','ACTIVE'),('ERIS','136199 Eris','DWARF_PLANET','ACTIVE'),
 ('HYGIEA','10 Hygiea','ASTEROID','ACTIVE'),('PALLAS','2 Pallas','ASTEROID','ACTIVE'),
 ('VESTA','4 Vesta','ASTEROID','ACTIVE'),('KLEOPATRA','216 Kleopatra','BINARY_ASTEROID_PRIMARY','ACTIVE'),
 ('MAKEMAKE','136472 Makemake','DWARF_PLANET','ACTIVE'),('CHIRON','2060 Chiron','CENTAUR','ACTIVE'),
 ('PATROCLUS','617 Patroclus','BINARY_ASTEROID_PRIMARY','ACTIVE'),('BENNU','101955 Bennu','NEAR_EARTH_ASTEROID','ACTIVE'),
 ('RYUGU','162173 Ryugu','NEAR_EARTH_ASTEROID','ACTIVE'),('ASTEROID_6178','6178 (1986 DA)','ASTEROID','ACTIVE'),
 ('AMUN','3554 Amun','NEAR_EARTH_ASTEROID','ACTIVE'),('COMET_67P','67P/Churyumov-Gerasimenko','COMET','ACTIVE'),
 ('COMET_HALLEY','1P/Halley','COMET','ACTIVE'),('HAUMEA','136108 Haumea','DWARF_PLANET','ACTIVE'),
 ('EURYBATES','3548 Eurybates','TROJAN_ASTEROID','ACTIVE'),('EROS','433 Eros','NEAR_EARTH_ASTEROID','ACTIVE'),
 ('ITOKAWA','25143 Itokawa','NEAR_EARTH_ASTEROID','ACTIVE'),('DIDYMOS','65803 Didymos','BINARY_ASTEROID_PRIMARY','ACTIVE');

INSERT INTO loom_solar.body_identifier(body_id, authority, identifier_type, identifier_value, status) VALUES
 ('PSYCHE','NAIF','NAIF_ID','20000016','ACTIVE'),('ERIS','NAIF','NAIF_ID','20136199','ACTIVE'),
 ('HYGIEA','NAIF','NAIF_ID','20000010','ACTIVE'),('PALLAS','NAIF','NAIF_ID','20000002','ACTIVE'),
 ('VESTA','NAIF','NAIF_ID','20000004','ACTIVE'),('KLEOPATRA','NAIF','NAIF_ID','20000216','ACTIVE'),
 ('MAKEMAKE','NAIF','NAIF_ID','20136472','ACTIVE'),('CHIRON','NAIF','NAIF_ID','20002060','ACTIVE'),
 ('PATROCLUS','NAIF','NAIF_ID','20000617','ACTIVE'),('BENNU','NAIF','NAIF_ID','2101955','ACTIVE'),
 ('RYUGU','NAIF','NAIF_ID','20162173','ACTIVE'),('ASTEROID_6178','NAIF','NAIF_ID','20006178','ACTIVE'),
 ('AMUN','NAIF','NAIF_ID','20003554','ACTIVE'),('COMET_67P','NAIF','NAIF_ID','1000012','ACTIVE'),
 ('COMET_HALLEY','NAIF','NAIF_ID','1000036','ACTIVE'),('HAUMEA','NAIF','NAIF_ID','20136108','ACTIVE'),
 ('EURYBATES','NAIF','NAIF_ID','20003548','ACTIVE'),('EROS','NAIF','NAIF_ID','20000433','ACTIVE'),
 ('ITOKAWA','NAIF','NAIF_ID','20025143','ACTIVE'),('DIDYMOS','NAIF','NAIF_ID','20065803','ACTIVE');

INSERT INTO loom_solar.ephemeris_source(
 ephemeris_source_id,provider,product_name,product_version,asset_filename,sha256,byte_count,
 source_url,acquired_at,status,state_capability,navigation_grade,uncertainty_km,source_lineage
) VALUES
 ('JPL_HORIZONS_PSY','JPL/Horizons','16 Psyche SPK','Horizons 2026-09-25','psyche_2026_2251.bsp','35b52667910b76307bbd32506d653ea5960a0a24c6a03fa70dbbce91ea476e78',4050944,'https://ssd.jpl.nasa.gov/api/horizons.api','2026-09-26T05:00:00Z','QUALIFIED','DIRECT_SPICE_2250_QUALIFIED',true,NULL,'JPL Horizons COMMAND=16'),
 ('JPL_HORIZONS_ERIS','JPL/Horizons','136199 Eris SPK','Horizons 2026-09-25','eris_2026_2251.bsp','b326cd075e1bd5d1e896950fa79ac0ea811f3c943e502d57dce121afb4f9c9be',4073472,'https://ssd.jpl.nasa.gov/api/horizons.api','2026-09-26T05:00:00Z','QUALIFIED','DIRECT_SPICE_2250_QUALIFIED',true,NULL,'JPL Horizons COMMAND=136199'),
 ('JPL_HORIZONS_HYG','JPL/Horizons','10 Hygiea SPK','Horizons 2026-09-25','hygiea_2026_2251.bsp','1c0636bf10250cb86a2cb95c0515cbbe1dc1620dd16958ff7d14215a2b8a821d',4074496,'https://ssd.jpl.nasa.gov/api/horizons.api','2026-09-26T05:00:00Z','QUALIFIED','DIRECT_SPICE_2250_QUALIFIED',true,NULL,'JPL Horizons COMMAND=10'),
 ('JPL_HORIZONS_PAL','JPL/Horizons','2 Pallas SPK','Horizons 2026-09-25','pallas_2026_2251.bsp','2282fbdd15c8c3bb8e41bdcc8dab990783b6cf6859d0f004f5d1657be9e85c47',4071424,'https://ssd.jpl.nasa.gov/api/horizons.api','2026-09-26T05:00:00Z','QUALIFIED','DIRECT_SPICE_2250_QUALIFIED',true,NULL,'JPL Horizons COMMAND=2'),
 ('JPL_HORIZONS_VES','JPL/Horizons','4 Vesta SPK','Horizons 2026-09-25','vesta_2026_2251.bsp','c9db15a8baf355a85cf0bc2bea9665764f0864671974ba2dbac7e9e52ae6df26',4079616,'https://ssd.jpl.nasa.gov/api/horizons.api','2026-09-26T05:00:00Z','QUALIFIED','DIRECT_SPICE_2250_QUALIFIED',true,NULL,'JPL Horizons COMMAND=4'),
 ('JPL_HORIZONS_KLE','JPL/Horizons','216 Kleopatra SPK','Horizons 2026-09-25','kleopatra_2026_2251.bsp','011869dba26ace7c5b023485c05e9fe832a7d98d53be9753ad99b2882196441a',4107264,'https://ssd.jpl.nasa.gov/api/horizons.api','2026-09-26T05:00:00Z','QUALIFIED','DIRECT_SPICE_2250_QUALIFIED',true,NULL,'JPL Horizons COMMAND=216'),
 ('JPL_HORIZONS_MAK','JPL/Horizons','136472 Makemake SPK','Horizons 2026-09-25','makemake_2026_2251.bsp','aec58f2a4863bc47e49f68d9516f7fb6084b44fa39b86c32f5640ecff6118463',4044800,'https://ssd.jpl.nasa.gov/api/horizons.api','2026-09-26T05:00:00Z','QUALIFIED','DIRECT_SPICE_2250_QUALIFIED',true,NULL,'JPL Horizons COMMAND=136472'),
 ('JPL_HORIZONS_CHI','JPL/Horizons','2060 Chiron SPK','Horizons 2026-09-25','chiron_2026_2251.bsp','908da67ff553f8960e373c4e1dbc6c0c9ca3b4898f4815e188da5578d40fd087',4017152,'https://ssd.jpl.nasa.gov/api/horizons.api','2026-09-26T05:00:00Z','QUALIFIED','DIRECT_SPICE_2250_QUALIFIED',true,NULL,'JPL Horizons COMMAND=2060'),
 ('JPL_HORIZONS_PAT','JPL/Horizons','617 Patroclus SPK','Horizons 2026-09-25','patroclus_2026_2251.bsp','5befb0b270c454571c434ada9d0c9d7deced7d79d018c387ea0fb4dc7e28942d',4094976,'https://ssd.jpl.nasa.gov/api/horizons.api','2026-09-26T05:00:00Z','QUALIFIED','DIRECT_SPICE_2250_QUALIFIED',true,NULL,'JPL Horizons COMMAND=617'),
 ('JPL_HORIZONS_RYU','JPL/Horizons','162173 Ryugu SPK','Horizons 2026-09-25','ryugu_2026_2251.bsp','3ce3fe466e3ac30564ad7be686b89b7211bdd14fb4870849889fcc20d705b977',4230144,'https://ssd.jpl.nasa.gov/api/horizons.api','2026-09-26T05:00:00Z','QUALIFIED','DIRECT_SPICE_2250_QUALIFIED',true,NULL,'JPL Horizons COMMAND=162173'),
 ('JPL_HORIZONS_6178','JPL/Horizons','6178 (1986 DA) SPK','Horizons 2026-09-25','1986da_2026_2251.bsp','c8eafffe2fe946bace07b63784375717187ff57960a3c828ad27d1a9be65fa19',4068352,'https://ssd.jpl.nasa.gov/api/horizons.api','2026-09-26T05:00:00Z','QUALIFIED','DIRECT_SPICE_2250_QUALIFIED',true,NULL,'JPL Horizons COMMAND=6178'),
 ('JPL_HORIZONS_AMU','JPL/Horizons','3554 Amun SPK','Horizons 2026-09-25','amun_2026_2251.bsp','fd94f50e0504cd868d1926024474e3c6c6b12323252cf89a92c82151e0365f8d',3954688,'https://ssd.jpl.nasa.gov/api/horizons.api','2026-09-26T05:00:00Z','QUALIFIED','DIRECT_SPICE_2250_QUALIFIED',true,NULL,'JPL Horizons COMMAND=3554'),
 ('JPL_HORIZONS_67P','JPL/Horizons','67P/Churyumov-Gerasimenko SPK','K284/1 2026-09-04','67p_2026_2251.bsp','1d58cc508b21fc1e9a3d8b5b27e1ab49ba571f76504e94d3fc974b7c532422a3',4245504,'https://ssd.jpl.nasa.gov/api/horizons.api','2026-09-26T05:00:00Z','QUALIFIED','DIRECT_SPICE_2250_QUALIFIED',true,NULL,'JPL Horizons COMMAND=90000703; non-gravitational model retained'),
 ('JPL_HORIZONS_HALLEY','JPL/Horizons','1P/Halley SPK','JPL#75 2025-11-21','halley_2026_2251.bsp','800ecda4992fb5326c65c9a4e654f69cd376bf0e5f6f3c8a4a5b293013c05142',4283392,'https://ssd.jpl.nasa.gov/api/horizons.api','2026-09-26T05:00:00Z','QUALIFIED','DIRECT_SPICE_2250_QUALIFIED',true,NULL,'JPL Horizons COMMAND=90000030; non-gravitational model retained'),
 ('JPL_HORIZONS_HAU','JPL/Horizons','136108 Haumea SPK','Horizons 2026-09-25','haumea_2026_2251.bsp','ddde6c4fd28417fad930b3562649ad88aed58b33964cd77713011234b8841b43',4039680,'https://ssd.jpl.nasa.gov/api/horizons.api','2026-09-26T05:00:00Z','QUALIFIED','DIRECT_SPICE_2250_QUALIFIED',true,NULL,'JPL Horizons COMMAND=136108'),
 ('JPL_HORIZONS_EUR','JPL/Horizons','3548 Eurybates SPK','Horizons 2026-09-25','eurybates_2026_2251.bsp','5266aeb0f71fb35bcdb10147afcaf19d27c47c3349fa1811b13bce1e555e9596',4063232,'https://ssd.jpl.nasa.gov/api/horizons.api','2026-09-26T05:00:00Z','QUALIFIED','DIRECT_SPICE_2250_QUALIFIED',true,NULL,'JPL Horizons COMMAND=3548'),
 ('JPL_HORIZONS_EROS','JPL/Horizons','433 Eros SPK','Horizons 2026-09-25','eros_2026_2251.bsp','2aa37b1080a2e666e5bd5e3d02bee1fa6ac029b65d5aea70d6b24ff9c3c9cdcf',4128768,'https://ssd.jpl.nasa.gov/api/horizons.api','2026-09-26T05:00:00Z','QUALIFIED','DIRECT_SPICE_2250_QUALIFIED',true,NULL,'JPL Horizons COMMAND=433'),
 ('JPL_HORIZONS_ITO','JPL/Horizons','25143 Itokawa SPK','Horizons 2026-09-25','itokawa_2026_2251.bsp','cc03dcd0d36261307f42b055ea3452279525b97ccac57c0a489d09ee5e2803ed',4194304,'https://ssd.jpl.nasa.gov/api/horizons.api','2026-09-26T05:00:00Z','QUALIFIED','DIRECT_SPICE_2250_QUALIFIED',true,NULL,'JPL Horizons COMMAND=25143'),
 ('JPL_HORIZONS_DID','JPL/Horizons','65803 Didymos SPK','Horizons 2026-09-25','didymos_2026_2251.bsp','5c6cd5b808a403d5aac53718039bdb5552de80a50206da17b2f3dde9d2c34c88',4068352,'https://ssd.jpl.nasa.gov/api/horizons.api','2026-09-26T05:00:00Z','QUALIFIED','DIRECT_SPICE_2250_QUALIFIED',true,NULL,'JPL Horizons COMMAND=65803'),
 ('JPL_BENNU_SB441','JPL/Horizons','sb-101955-118_long mission SPK','ORX_merged_DE424 / JPL#118','bennu_sb-101955-118_long.bsp','2e25094e62542f388071b43e6f7b794024ca3fa4e399306976ac62a1a5c3b48f',84648960,'https://ssd.jpl.nasa.gov/ftp/xfr/sb-101955-118_long.bsp','2026-09-26T05:00:00Z','QUALIFIED','DIRECT_SPICE_PARTIAL_2135',true,NULL,'OSIRIS-REx merged solution; Farnocchia et al. 2021'),
 ('PROP_BENNU_2101955_PHASE4D','LOOM/JPL-NASA-derived','Phase-4D Bennu propagation SPK','LOOM_SOLAR_PHASE4B_RK4_NBODY_V2_SMALL_BODY','propagated_bennu_2101955_2026_2251.bsp','1496602d7f9f645ca3f5721b07c9dfe771f17cb91e7909356a8994859a85d439',9223168,'JPL Bennu predecessor + DE440; local deterministic propagation','2026-09-26T05:00:00Z','QUALIFIED','EMPIRICAL_PROPAGATED_2250',false,1000000000.0,'JPL_BENNU_SB441;DE440;RK4 6-hour step; omitted Yarkovsky/close-encounter uncertainty explicit');

INSERT INTO loom_solar.ephemeris_coverage(ephemeris_source_id,body_id,valid_from,valid_until,reference_frame,units,coverage_class,status) VALUES
 ('JPL_HORIZONS_PSY','PSYCHE','2025-12-31T23:58:50.816Z','2251-01-01T23:58:50.816Z','ECLIPJ2000','km,km/s','BODY','QUALIFIED'),
 ('JPL_HORIZONS_ERIS','ERIS','2025-12-31T23:58:50.816Z','2251-01-01T23:58:50.816Z','ECLIPJ2000','km,km/s','BODY','QUALIFIED'),
 ('JPL_HORIZONS_HYG','HYGIEA','2025-12-31T23:58:50.816Z','2251-01-01T23:58:50.816Z','ECLIPJ2000','km,km/s','BODY','QUALIFIED'),
 ('JPL_HORIZONS_PAL','PALLAS','2025-12-31T23:58:50.816Z','2251-01-01T23:58:50.816Z','ECLIPJ2000','km,km/s','BODY','QUALIFIED'),
 ('JPL_HORIZONS_VES','VESTA','2025-12-31T23:58:50.816Z','2251-01-01T23:58:50.816Z','ECLIPJ2000','km,km/s','BODY','QUALIFIED'),
 ('JPL_HORIZONS_KLE','KLEOPATRA','2025-12-31T23:58:50.816Z','2251-01-01T23:58:50.816Z','ECLIPJ2000','km,km/s','BODY','QUALIFIED'),
 ('JPL_HORIZONS_MAK','MAKEMAKE','2025-12-31T23:58:50.816Z','2251-01-01T23:58:50.816Z','ECLIPJ2000','km,km/s','BODY','QUALIFIED'),
 ('JPL_HORIZONS_CHI','CHIRON','2025-12-31T23:58:50.816Z','2251-01-01T23:58:50.816Z','ECLIPJ2000','km,km/s','BODY','QUALIFIED'),
 ('JPL_HORIZONS_PAT','PATROCLUS','2025-12-31T23:58:50.816Z','2251-01-01T23:58:50.816Z','ECLIPJ2000','km,km/s','BODY','QUALIFIED'),
 ('JPL_HORIZONS_RYU','RYUGU','2025-12-31T23:58:50.816Z','2251-01-01T23:58:50.816Z','ECLIPJ2000','km,km/s','BODY','QUALIFIED'),
 ('JPL_HORIZONS_6178','ASTEROID_6178','2025-12-31T23:58:50.816Z','2251-01-01T23:58:50.816Z','ECLIPJ2000','km,km/s','BODY','QUALIFIED'),
 ('JPL_HORIZONS_AMU','AMUN','2025-12-31T23:58:50.816Z','2251-01-01T23:58:50.816Z','ECLIPJ2000','km,km/s','BODY','QUALIFIED'),
 ('JPL_HORIZONS_67P','COMET_67P','2025-12-31T23:58:50.816Z','2251-01-01T23:58:50.816Z','ECLIPJ2000','km,km/s','BODY','QUALIFIED'),
 ('JPL_HORIZONS_HALLEY','COMET_HALLEY','2025-12-31T23:58:50.816Z','2251-01-01T23:58:50.816Z','ECLIPJ2000','km,km/s','BODY','QUALIFIED'),
 ('JPL_HORIZONS_HAU','HAUMEA','2025-12-31T23:58:50.816Z','2251-01-01T23:58:50.816Z','ECLIPJ2000','km,km/s','BODY','QUALIFIED'),
 ('JPL_HORIZONS_EUR','EURYBATES','2025-12-31T23:58:50.816Z','2251-01-01T23:58:50.816Z','ECLIPJ2000','km,km/s','BODY','QUALIFIED'),
 ('JPL_HORIZONS_EROS','EROS','2025-12-31T23:58:50.816Z','2251-01-01T23:58:50.816Z','ECLIPJ2000','km,km/s','BODY','QUALIFIED'),
 ('JPL_HORIZONS_ITO','ITOKAWA','2025-12-31T23:58:50.816Z','2251-01-01T23:58:50.816Z','ECLIPJ2000','km,km/s','BODY','QUALIFIED'),
 ('JPL_HORIZONS_DID','DIDYMOS','2025-12-31T23:58:50.816Z','2251-01-01T23:58:50.816Z','ECLIPJ2000','km,km/s','BODY','QUALIFIED'),
 ('JPL_BENNU_SB441','BENNU','1899-12-31T23:59:18.816Z','2135-09-30T23:58:50.818Z','ECLIPJ2000','km,km/s','BODY','QUALIFIED'),
 ('PROP_BENNU_2101955_PHASE4D','BENNU','2026-01-01T00:00:00.000Z','2251-01-01T00:01:00Z','ECLIPJ2000','km,km/s','DERIVED','QUALIFIED');

DO $$
DECLARE body_count integer; identifier_count integer; qualified_count integer;
BEGIN
 SELECT count(*) INTO body_count FROM loom_solar.body WHERE status='ACTIVE';
 SELECT count(*) INTO identifier_count FROM loom_solar.body_identifier WHERE status='ACTIVE';
 SELECT count(*) INTO qualified_count FROM loom_solar.ephemeris_coverage WHERE status='QUALIFIED';
 IF body_count <> 63 OR identifier_count <> 63 OR qualified_count <> 71 THEN
   RAISE EXCEPTION 'Phase-4D expected 63 active bodies/63 identifiers/71 qualified coverage rows, got %/%/%', body_count, identifier_count, qualified_count;
 END IF;
END $$;
