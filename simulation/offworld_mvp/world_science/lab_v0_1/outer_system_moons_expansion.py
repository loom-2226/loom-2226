OS_SOURCES=[
('URA_SPK','JPL Uranian satellite ephemerides','NASA/JPL NAIF','NAVIGATION_AUTHORITY','https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/satellites/',None,None),
('VOY_SPICE','Voyager mission SPICE archive','NASA/JPL NAIF/PDS','MISSION_ARCHIVE','https://naif.jpl.nasa.gov/pub/naif/VOYAGER/',None,None),
('URA_GEO','Uranian satellite geology and crater distributions from Voyager 2','Planetary Science Journal','PEER_REVIEWED','https://doi.org/10.3847/psj/ac42d7','10.3847/psj/ac42d7','2022'),
('MIR_OCEAN','Miranda geological stress and possible past ocean constraints','Planetary Science Journal','PEER_REVIEWED','https://doi.org/10.3847/psj/ad77d7','10.3847/psj/ad77d7','2024'),
('MIR_HEAT','Miranda Inverness Corona heat-flow constraints','Planetary Science Journal','PEER_REVIEWED','https://doi.org/10.3847/PSJ/ac7be5','10.3847/PSJ/ac7be5','2022'),
('URA_SPEC','Spectral composition of Uranian satellites: water ice, CO2 and hemispheric distributions','Icarus','PEER_REVIEWED','https://doi.org/10.1016/j.icarus.2015.12.041','10.1016/j.icarus.2015.12.041','2016'),
('URA_NH3','Ammonia-bearing species on Ariel and Uranian moons','Astronomical Journal','PEER_REVIEWED','https://doi.org/10.3847/1538-3881/ab9535','10.3847/1538-3881/ab9535','2020'),
('URA_INTERIOR','Thermal evolution and ocean persistence in Uranian moons','Journal of Geophysical Research Planets','PEER_REVIEWED','https://doi.org/10.1029/2022JE007432','10.1029/2022JE007432','2023'),
('NEP_SPK','JPL Neptunian satellite ephemerides','NASA/JPL NAIF','NAVIGATION_AUTHORITY','https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/satellites/',None,None),
('TRI_GEO','Voyager 2 Triton geology and active plume observations','Science','PEER_REVIEWED','https://doi.org/10.1126/science.250.4979.435','10.1126/science.250.4979.435','1990'),
('TRI_ATM','Triton atmospheric pressure evolution from stellar occultations','Astronomy and Astrophysics','PEER_REVIEWED','https://doi.org/10.1051/0004-6361/201935064','10.1051/0004-6361/201935064','2019'),
('TRI_SPEC','Triton volatile and ice composition spectroscopy','Icarus','PEER_REVIEWED','https://doi.org/10.1016/j.icarus.2009.07.010','10.1016/j.icarus.2009.07.010','2010'),
('TRI_OCEAN','Triton thermal evolution and subsurface ocean models','Icarus','PEER_REVIEWED','https://doi.org/10.1016/j.icarus.2012.11.021','10.1016/j.icarus.2012.11.021','2013'),
('PLU_SPK','JPL Pluto system ephemerides','NASA/JPL NAIF','NAVIGATION_AUTHORITY','https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/satellites/',None,None),
('NH_SPICE','New Horizons mission SPICE archive','NASA/JPL NAIF/PDS','MISSION_ARCHIVE','https://naif.jpl.nasa.gov/pub/naif/NEWHORIZONS/',None,None),
('CHA_GEO','Geology of Charon from New Horizons','Science','PEER_REVIEWED','https://doi.org/10.1126/science.aad9189','10.1126/science.aad9189','2016'),
('CHA_COMP','Charon surface composition and ammonia-bearing material','Science','PEER_REVIEWED','https://doi.org/10.1126/science.aad9189','10.1126/science.aad9189','2016'),
('CHA_POLAR','Charon red polar coloration sourced from Pluto atmosphere','Nature','PEER_REVIEWED','https://doi.org/10.1038/nature19340','10.1038/nature19340','2016'),
('PLU_SMALL','Small satellites of Pluto observed by New Horizons','Science','PEER_REVIEWED','https://doi.org/10.1126/science.aae0030','10.1126/science.aae0030','2016'),
('PLU_DYN','Resonant interactions and chaotic rotation of Pluto small moons','Nature','PEER_REVIEWED','https://doi.org/10.1038/nature14469','10.1038/nature14469','2015'),
('PLU_MASS','Orbits and masses of Pluto small satellites','Planetary Science Journal','PEER_REVIEWED','https://doi.org/10.3847/psj/acde77','10.3847/psj/acde77','2023')]
OS_SOURCE_IDS={}
for key,title,auth,typ,url,doi,pub in OS_SOURCES:
 cur=db.execute('insert into source(source_key,title,authority,source_type,url,doi,publication_date,acquired_at,notes) values(?,?,?,?,?,?,?,?,?)',(key,title,auth,typ,url,doi,pub,'2026-10-06','Outer-system major moons expansion reference'))
 OS_SOURCE_IDS[key]=cur.lastrowid
 db.execute('insert into source_artifact(source_id,artifact_key,retrieval_url,acquired_at,origin_kind) values(?,?,?,?,?)',(cur.lastrowid,key+'_REMOTE',url,'2026-10-06','REMOTE_REFERENCE_ONLY'))
for b,src,klass in [('MIRANDA','URA_SPK','GENERIC_URANUS_SATELLITE_SPK_PLUS_VOYAGER'),('ARIEL','URA_SPK','GENERIC_URANUS_SATELLITE_SPK_PLUS_VOYAGER'),('UMBRIEL','URA_SPK','GENERIC_URANUS_SATELLITE_SPK_PLUS_VOYAGER'),('TITANIA','URA_SPK','GENERIC_URANUS_SATELLITE_SPK_PLUS_VOYAGER'),('OBERON','URA_SPK','GENERIC_URANUS_SATELLITE_SPK_PLUS_VOYAGER'),('TRITON','NEP_SPK','GENERIC_NEPTUNE_SATELLITE_SPK_PLUS_VOYAGER'),('CHARON','PLU_SPK','PLUTO_SYSTEM_SPK_PLUS_NEW_HORIZONS'),('STYX','PLU_SPK','PLUTO_SYSTEM_CIRCUMBINARY_SPK_PLUS_NEW_HORIZONS'),('NIX','PLU_SPK','PLUTO_SYSTEM_CIRCUMBINARY_SPK_PLUS_NEW_HORIZONS'),('KERBEROS','PLU_SPK','PLUTO_SYSTEM_CIRCUMBINARY_SPK_PLUS_NEW_HORIZONS'),('HYDRA','PLU_SPK','PLUTO_SYSTEM_CIRCUMBINARY_SPK_PLUS_NEW_HORIZONS')]:
 cur=db.execute('insert into ephemeris_source(provider,product_name,source_url,acquired_at,status) values(?,?,?,?,?)',('NASA/JPL NAIF','Governed satellite-system + mission SPICE authority',next(x[4] for x in OS_SOURCES if x[0]==src),'2026-10-06','REFERENCE_ONLY'))
 db.execute('insert into ephemeris_coverage(ephemeris_source_id,body_id,valid_from,valid_until,reference_frame,units,coverage_class,status) values(?,?,?,?,?,?,?,?)',(cur.lastrowid,b,None,None,'J2000 plus IAU_'+b,'km, s',klass,'CANDIDATE'))
