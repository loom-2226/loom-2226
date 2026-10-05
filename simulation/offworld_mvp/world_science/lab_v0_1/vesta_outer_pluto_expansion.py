# Vesta + outer planets + Pluto expansion source registration.
VOPP_SOURCES=[
('VESTA_DAWN_PDS','Dawn Vesta science archive','NASA PDS','MISSION_ARCHIVE','https://sbnarchive.psi.edu/pds3/dawn/','DAWN-VESTA-PDS',None),
('VESTA_OVERVIEW','Overview of the composition of asteroid 4 Vesta: Constraints from Dawn and HEDs','Meteoritics & Planetary Science','PEER_REVIEWED','https://doi.org/10.1111/maps.12190','10.1111/maps.12190','2013'),
('VESTA_GEOLOGY','Asteroid (4) Vesta II: geologically and geochemically complex world','Chemie der Erde','PEER_REVIEWED','https://doi.org/10.1016/j.chemer.2014.12.001','10.1016/j.chemer.2014.12.001','2015'),
('JUPITER_GALILEO','Galileo Probe measurements of Jupiter atmosphere','NASA PDS / Galileo','MISSION_ARCHIVE','https://pds-atmospheres.nmsu.edu/data_and_services/atmospheres_data/Galileo/galileo_probe.html','GALILEO-PROBE',None),
('JUPITER_JUNO_GRAV','Jupiter gravity field, interior structure and deep winds from Juno','Juno science team','PEER_REVIEWED','https://doi.org/10.1038/s41586-018-0070-9','10.1038/s41586-018-0070-9','2018'),
('JUPITER_JUNO_CORE','A dilute core in Jupiter','Juno interior science','PEER_REVIEWED','https://doi.org/10.1051/0004-6361/201936012','10.1051/0004-6361/201936012','2019'),
('JUPITER_JUNO_MAG','Jupiter magnetic field from Juno','Nature','PEER_REVIEWED','https://doi.org/10.1038/nature22058','10.1038/nature22058','2017'),
('SATURN_CASSINI_GRAV','Measurement and implications of Saturn gravity field and ring mass','Science','PEER_REVIEWED','https://doi.org/10.1126/science.aat2965','10.1126/science.aat2965','2019'),
('SATURN_CORE','A diffuse core in Saturn revealed by ring seismology','Nature Astronomy','PEER_REVIEWED','https://doi.org/10.1038/s41550-021-01448-3','10.1038/s41550-021-01448-3','2021'),
('SATURN_CIRS','Saturn atmospheric temperature and composition from Cassini CIRS','Cassini science','PEER_REVIEWED','https://doi.org/10.1016/j.icarus.2015.11.010','10.1016/j.icarus.2015.11.010','2016'),
('URANUS_VOYAGER','Uranus atmosphere and magnetic field Voyager 2 archive','NASA PDS / Voyager','MISSION_ARCHIVE','https://pds-atmospheres.nmsu.edu/data_and_services/atmospheres_data/Voyager/voyager.html','VOYAGER2-URANUS',None),
('URANUS_INTERIOR','Uranus and Neptune: origin, evolution and internal structure','Space Science Reviews','PEER_REVIEWED','https://doi.org/10.1007/s11214-020-00660-3','10.1007/s11214-020-00660-3','2020'),
('NEPTUNE_VOYAGER','Neptune atmosphere and magnetic field Voyager 2 archive','NASA PDS / Voyager','MISSION_ARCHIVE','https://pds-atmospheres.nmsu.edu/data_and_services/atmospheres_data/Voyager/voyager.html','VOYAGER2-NEPTUNE',None),
('NEPTUNE_INTERIOR','Uranus and Neptune: origin, evolution and internal structure','Space Science Reviews','PEER_REVIEWED','https://doi.org/10.1007/s11214-020-00660-3','10.1007/s11214-020-00660-3','2020'),
('PLUTO_NH_GEO','The geology of Pluto and Charon through the eyes of New Horizons','Science','PEER_REVIEWED','https://doi.org/10.1126/science.aad7055','10.1126/science.aad7055','2016'),
('PLUTO_NH_COMP','Surface compositions across Pluto and Charon','Science','PEER_REVIEWED','https://doi.org/10.1126/science.aad9189','10.1126/science.aad9189','2016'),
('PLUTO_NH_ATMOS','The atmosphere of Pluto as observed by New Horizons','Science','PEER_REVIEWED','https://doi.org/10.1126/science.aad8866','10.1126/science.aad8866','2016'),
('PLUTO_ATMOS_PROFILE','Structure and composition of Pluto atmosphere from New Horizons solar ultraviolet occultation','Icarus','PEER_REVIEWED','https://doi.org/10.1016/j.icarus.2017.06.006','10.1016/j.icarus.2017.06.006','2018'),
('PLUTO_PRESSURE_TIME','Lower atmosphere and pressure evolution on Pluto from stellar occultations 1988-2016','Astronomy & Astrophysics','PEER_REVIEWED','https://doi.org/10.1051/0004-6361/201834281','10.1051/0004-6361/201834281','2019'),
('PLUTO_VOLATILE_MODEL','Observed glacier and volatile distribution on Pluto from atmosphere-topography processes','Nature','PEER_REVIEWED','https://doi.org/10.1038/nature19337','10.1038/nature19337','2016'),
('PLUTO_OCEAN','Reorientation and faulting of Pluto due to volatile loading within Sputnik Planitia','Nature','PEER_REVIEWED','https://doi.org/10.1038/nature20120','10.1038/nature20120','2016'),
('PDS_RINGS','Planetary ring system archives','NASA PDS Ring-Moon Systems Node','MISSION_ARCHIVE','https://pds-rings.seti.org/','PDS-RINGS',None)]
VOPP_SOURCE_IDS={}
for key,title,auth,typ,url,doi,pub in VOPP_SOURCES:
 cur=db.execute('insert into source(source_key,title,authority,source_type,url,doi,publication_date,acquired_at,notes) values(?,?,?,?,?,?,?,?,?)',(key,title,auth,typ,url,doi,pub,'2026-10-06','Vesta/outer planets/Pluto expansion; remote reference unless frozen predecessor lineage exists'))
 VOPP_SOURCE_IDS[key]=cur.lastrowid
 db.execute('insert into source_artifact(source_id,artifact_key,retrieval_url,acquired_at,origin_kind) values(?,?,?,?,?)',(cur.lastrowid,key+'_REMOTE',url,'2026-10-06','REMOTE_REFERENCE_ONLY'))
