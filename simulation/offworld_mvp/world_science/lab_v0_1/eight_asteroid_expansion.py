EA_SOURCES=[
('PSYCHE_PREFLIGHT','Observations, Meteorites, and Models: A Preflight Assessment of (16) Psyche','JGR Planets','PEER_REVIEWED','https://doi.org/10.1029/2019JE006296','10.1029/2019JE006296','2020'),
('PSYCHE_SPICE','Psyche SPICE Data Archive','NASA NAIF/PDS','MISSION_ARCHIVE','https://naif.jpl.nasa.gov/pub/naif/pds/pds4/psyche/psyche_spice/document/spiceds_v003.html',None,'2026'),
('RYUGU_SHAPE','Hayabusa2 observations of the top-shaped carbonaceous asteroid 162173 Ryugu','Science','PEER_REVIEWED','https://doi.org/10.1126/science.aav8032','10.1126/science.aav8032','2019'),
('RYUGU_SAMPLE','Samples returned from the asteroid Ryugu are similar to Ivuna-type carbonaceous meteorites','Science','PEER_REVIEWED','https://doi.org/10.1126/science.abn8671','10.1126/science.abn8671','2022'),
('RYUGU_SPICE','Hayabusa2 SPICE Data Archive','NASA NAIF/PDS','MISSION_ARCHIVE','https://naif.jpl.nasa.gov/pub/naif/pds/pds4/hyb2/hyb2_spice/document/spiceds_v001.html',None,'2025'),
('ITOKAWA_SCIENCE','Rubble-pile structure of asteroid Itokawa','Science','PEER_REVIEWED','https://doi.org/10.1126/science.1125841','10.1126/science.1125841','2006'),
('ITOKAWA_SAMPLE','Itokawa dust particles: a direct link between S-type asteroids and ordinary chondrites','Science','PEER_REVIEWED','https://doi.org/10.1126/science.1207758','10.1126/science.1207758','2011'),
('HAYABUSA_SPICE','Hayabusa SPICE Data Archive','NASA NAIF/PDS','MISSION_ARCHIVE','https://naif.jpl.nasa.gov/pub/naif/pds/data/hay-a-spice-6-v1.0/haysp_1000/aareadme.htm',None,None),
('EROS_GEO','The landing of the NEAR-Shoemaker spacecraft on asteroid 433 Eros','Nature','PEER_REVIEWED','https://doi.org/10.1038/35059079','10.1038/35059079','2001'),
('EROS_COMP','Elemental composition of asteroid 433 Eros: new calibration of the NEAR-Shoemaker XRS data','Meteoritics & Planetary Science','PEER_REVIEWED','https://doi.org/10.1111/j.1945-5100.2011.01169.x','10.1111/j.1945-5100.2011.01169.x','2011'),
('NEAR_SPICE','NEAR mission SPICE archive','NASA NAIF/PDS','MISSION_ARCHIVE','https://naif.jpl.nasa.gov/pub/naif/NEAR/',None,None),
('LUTETIA_SCI','Asteroid 21 Lutetia: low-mass, high-density world','Science','PEER_REVIEWED','https://doi.org/10.1126/science.1207325','10.1126/science.1207325','2011'),
('STEINS_SCI','Images of asteroid 2867 Steins from Rosetta fly-by','Science','PEER_REVIEWED','https://doi.org/10.1126/science.1179559','10.1126/science.1179559','2010'),
('ROSETTA_SPICE','Rosetta mission SPICE archive','NASA NAIF/PDS','MISSION_ARCHIVE','https://naif.jpl.nasa.gov/pub/naif/ROSETTA/',None,None),
('MATHILDE_SCI','Asteroid 253 Mathilde: shape, size and geology','Icarus','PEER_REVIEWED','https://doi.org/10.1006/icar.1999.6122','10.1006/icar.1999.6122','1999'),
('MATHILDE_DENS','Estimate of bulk density of asteroid 253 Mathilde','Science','PEER_REVIEWED','https://doi.org/10.1126/science.278.5346.2106','10.1126/science.278.5346.2106','1997'),
('IDA_GEO','First images of asteroid 243 Ida','Science','PEER_REVIEWED','https://doi.org/10.1126/science.265.5178.1543','10.1126/science.265.5178.1543','1994'),
('IDA_DACTYL','Discovery and physical properties of Dactyl, a satellite of asteroid 243 Ida','Nature','PEER_REVIEWED','https://doi.org/10.1038/374783a0','10.1038/374783a0','1995'),
('IDA_COMP','A compositional study of asteroid 243 Ida and Dactyl from Galileo NIMS and SSI observations','JGR Planets','PEER_REVIEWED','https://doi.org/10.1029/2001JE001759','10.1029/2001JE001759','2002'),
('GALILEO_SPICE','Galileo mission SPICE archive','NASA NAIF/PDS','MISSION_ARCHIVE','https://naif.jpl.nasa.gov/pub/naif/GLL/',None,None),
('HORIZONS','JPL Horizons System','NASA/JPL','NAVIGATION_AUTHORITY','https://ssd.jpl.nasa.gov/horizons/',None,None)]
EA_SOURCE_IDS={}
for key,title,auth,typ,url,doi,pub in EA_SOURCES:
 cur=db.execute('insert into source(source_key,title,authority,source_type,url,doi,publication_date,acquired_at,notes) values(?,?,?,?,?,?,?,?,?)',(key,title,auth,typ,url,doi,pub,'2026-10-06','Eight-asteroid expansion reference'))
 EA_SOURCE_IDS[key]=cur.lastrowid
 db.execute('insert into source_artifact(source_id,artifact_key,retrieval_url,acquired_at,origin_kind) values(?,?,?,?,?)',(cur.lastrowid,key+'_REMOTE',url,'2026-10-06','REMOTE_REFERENCE_ONLY'))
# Governed navigation references: mission kernels where they exist; Horizons remains fallback/on-demand authority, not stored ephemeris time series.
nav=[
('PSYCHE','Psyche PDS4 SPICE','PSYCHE_SPICE','2023-10-13',None,'MISSION_SPICE'),
('RYUGU','Hayabusa2 PDS4 SPICE','RYUGU_SPICE','2014-12-03','2020-12-06','MISSION_SPICE'),
('ITOKAWA','Hayabusa mission SPICE including JPL Itokawa ephemeris','HAYABUSA_SPICE','2005-09-11','2005-11-19','MISSION_SPICE'),
('EROS','NEAR mission SPICE','NEAR_SPICE','1996-02-17','2001-02-28','MISSION_SPICE'),
('LUTETIA','Rosetta mission SPICE','ROSETTA_SPICE','2004-03-02','2016-09-30','MISSION_SPICE'),
('STEINS','Rosetta mission SPICE','ROSETTA_SPICE','2004-03-02','2016-09-30','MISSION_SPICE'),
('MATHILDE','NEAR mission SPICE','NEAR_SPICE','1996-02-17','2001-02-28','MISSION_SPICE'),
('IDA','Galileo mission SPICE','GALILEO_SPICE','1989-10-18','2003-09-21','MISSION_SPICE')]
for b,name,skey,a,z,cl in nav:
 cur=db.execute('insert into ephemeris_source(provider,product_name,source_url,acquired_at,status) values(?,?,?,?,?)',('NASA/JPL NAIF or JPL Horizons',name,next(x[4] for x in EA_SOURCES if x[0]==skey),'2026-10-06','REFERENCE_ONLY'))
 db.execute('insert into ephemeris_coverage(ephemeris_source_id,body_id,valid_from,valid_until,reference_frame,units,coverage_class,status) values(?,?,?,?,?,?,?,?)',(cur.lastrowid,b,a,z,'J2000 / mission body-fixed where available','km, s',cl,'CANDIDATE'))
