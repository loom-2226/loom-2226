GM_SOURCES=[
('JUP_SPK','JPL planetary satellite ephemerides / Jupiter satellite SPKs','NASA/JPL NAIF','NAVIGATION_AUTHORITY','https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/satellites/',None,None),
('GLL_SPICE','Galileo mission SPICE archive','NASA/JPL NAIF/PDS','MISSION_ARCHIVE','https://naif.jpl.nasa.gov/pub/naif/GLL/',None,None),
('JUNO_SPICE','Juno mission SPICE archive','NASA/JPL NAIF/PDS','MISSION_ARCHIVE','https://naif.jpl.nasa.gov/pub/naif/JUNO/',None,None),
('JUICE_SPICE','JUICE SPICE archive','ESA/NAIF','MISSION_ARCHIVE','https://spiftp.esac.esa.int/data/SPICE/JUICE/kernels/',None,None),
('EUCLIP_SPICE','Europa Clipper SPICE archive','NASA/JPL NAIF/PDS','MISSION_ARCHIVE','https://naif.jpl.nasa.gov/pub/naif/EUROPACLIPPER/',None,None),
('IO_REVIEW','Io after Galileo','Reports on Progress in Physics','PEER_REVIEWED','https://doi.org/10.1088/0034-4885/68/2/R02','10.1088/0034-4885/68/2/R02','2005'),
('IO_MAGMA','A global magma ocean in Io? constraints from Galileo magnetometer observations','Science','PEER_REVIEWED','https://doi.org/10.1126/science.1201425','10.1126/science.1201425','2011'),
('IO_JUNO_GRAV','Tidal response and interior of Io from Juno close flybys','Nature','PEER_REVIEWED','https://doi.org/10.1038/s41586-024-08421-6','10.1038/s41586-024-08421-6','2024'),
('IO_VOLC','Global distribution of volcanic activity on Io','Planetary Science Journal','PEER_REVIEWED','https://doi.org/10.3847/PSJ/ad4346','10.3847/PSJ/ad4346','2024'),
('EU_MAG','Europa magnetic-field measurements and conductive-layer interpretation','Nature','PEER_REVIEWED','https://doi.org/10.1038/27394','10.1038/27394','1998'),
('EU_GEO','Geologic Map of Europa, SIM 3513','USGS','AUTHORITATIVE_MAP','https://doi.org/10.3133/sim3513','10.3133/sim3513','2024'),
('EU_NACL','Sodium chloride on the surface of Europa','Science Advances','PEER_REVIEWED','https://doi.org/10.1126/sciadv.aaw7123','10.1126/sciadv.aaw7123','2019'),
('EU_PLUME','Transient water vapor at Europa south pole','Science','PEER_REVIEWED','https://doi.org/10.1126/science.1247051','10.1126/science.1247051','2014'),
('EU_PLUME_ND','Constraints on Europa water vapor plumes from HST','Astrophysical Journal','PEER_REVIEWED','https://doi.org/10.1088/2041-8205/829/1/L6','10.1088/2041-8205/829/1/L6','2016'),
('EU_CO2','Endogenous CO2 ice mixture on Europa and distribution from JWST','Science','PEER_REVIEWED','https://doi.org/10.1126/science.adg4270','10.1126/science.adg4270','2023'),
('GAN_MAG','Discovery of Ganymede magnetic field by Galileo','Nature','PEER_REVIEWED','https://doi.org/10.1038/384537a0','10.1038/384537a0','1996'),
('GAN_OCEAN','Ganymede magnetic induction and subsurface ocean constraints','Icarus','PEER_REVIEWED','https://doi.org/10.1016/j.icarus.2002.12.008','10.1016/j.icarus.2002.12.008','2003'),
('GAN_INTERIOR','Ganymede interior structure from Galileo gravity','Icarus','PEER_REVIEWED','https://doi.org/10.1006/icar.1998.5964','10.1006/icar.1998.5964','1998'),
('GAN_GEO','Geologic Map of Ganymede','USGS','AUTHORITATIVE_MAP','https://doi.org/10.3133/sim3237','10.3133/sim3237','2013'),
('GAN_CO2','JWST observations of Ganymede CO2 and surface heterogeneity','Astronomy & Astrophysics','PEER_REVIEWED','https://doi.org/10.1051/0004-6361/202347903','10.1051/0004-6361/202347903','2024'),
('CAL_MAG','Induced magnetic fields as evidence for Callisto subsurface ocean','Journal of Geophysical Research','PEER_REVIEWED','https://doi.org/10.1029/98JA01821','10.1029/98JA01821','1998'),
('CAL_GRAV','Gravitational evidence for an undifferentiated Callisto','Nature','PEER_REVIEWED','https://doi.org/10.1038/387264a0','10.1038/387264a0','1997'),
('CAL_ATMOS','A tenuous carbon dioxide atmosphere on Callisto','Science','PEER_REVIEWED','https://doi.org/10.1126/science.283.5403.820','10.1126/science.283.5403.820','1999'),
('CAL_CO2','Revealing Callisto carbon-rich surface and CO2 atmosphere with JWST','Planetary Science Journal','PEER_REVIEWED','https://doi.org/10.3847/PSJ/ad23e6','10.3847/PSJ/ad23e6','2024')]
GM_SOURCE_IDS={}
for key,title,auth,typ,url,doi,pub in GM_SOURCES:
 cur=db.execute('insert into source(source_key,title,authority,source_type,url,doi,publication_date,acquired_at,notes) values(?,?,?,?,?,?,?,?,?)',(key,title,auth,typ,url,doi,pub,'2026-10-06','Galilean-moons expansion reference'))
 GM_SOURCE_IDS[key]=cur.lastrowid
 db.execute('insert into source_artifact(source_id,artifact_key,retrieval_url,acquired_at,origin_kind) values(?,?,?,?,?)',(cur.lastrowid,key+'_REMOTE',url,'2026-10-06','REMOTE_REFERENCE_ONLY'))
for b in ['IO','EUROPA','GANYMEDE','CALLISTO']:
 cur=db.execute('insert into ephemeris_source(provider,product_name,source_url,acquired_at,status) values(?,?,?,?,?)',('NASA/JPL NAIF','Jupiter satellite generic + mission SPICE authority',next(x[4] for x in GM_SOURCES if x[0]=='JUP_SPK'),'2026-10-06','REFERENCE_ONLY'))
 db.execute('insert into ephemeris_coverage(ephemeris_source_id,body_id,valid_from,valid_until,reference_frame,units,coverage_class,status) values(?,?,?,?,?,?,?,?)',(cur.lastrowid,b,None,None,'J2000 plus IAU_'+b,'km, s','GENERIC_JUPITER_SATELLITE_SPK_PLUS_MISSION_SPICE','CANDIDATE'))
