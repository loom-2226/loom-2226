SM_SOURCES=[
('SAT_SPK','JPL planetary satellite ephemerides / Saturn satellite SPKs','NASA/JPL NAIF','NAVIGATION_AUTHORITY','https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/satellites/',None,None),
('CAS_SPICE','Cassini mission SPICE archive','NASA/JPL NAIF/PDS','MISSION_ARCHIVE','https://naif.jpl.nasa.gov/pub/naif/CASSINI/',None,None),
('MIM_LIB','Mimas libration and interior constraints','Science','PEER_REVIEWED','https://doi.org/10.1126/science.1255299','10.1126/science.1255299','2014'),
('MIM_OCEAN','A recently formed ocean inside Saturn moon Mimas','Nature','PEER_REVIEWED','https://doi.org/10.1038/s41586-023-06975-9','10.1038/s41586-023-06975-9','2024'),
('MIM_THERM','Thermal landscapes of Mimas from Cassini','Icarus','PEER_REVIEWED','https://doi.org/10.1016/j.icarus.2020.113745','10.1016/j.icarus.2020.113745','2020'),
('ENC_GEO','Enceladus south polar terrain and plume source fractures','Science','PEER_REVIEWED','https://doi.org/10.1126/science.1123013','10.1126/science.1123013','2006'),
('ENC_OCEAN','The interior of Enceladus including a global ocean from libration','Icarus','PEER_REVIEWED','https://doi.org/10.1016/j.icarus.2015.08.037','10.1016/j.icarus.2015.08.037','2016'),
('ENC_GRAV','Gravity field and interior structure of Enceladus','Science','PEER_REVIEWED','https://doi.org/10.1126/science.1250551','10.1126/science.1250551','2014'),
('ENC_SALT','Sodium salts in E-ring ice grains from Enceladus ocean','Nature','PEER_REVIEWED','https://doi.org/10.1038/nature08046','10.1038/nature08046','2009'),
('ENC_SILICA','Ongoing hydrothermal activities within Enceladus','Nature','PEER_REVIEWED','https://doi.org/10.1038/nature14262','10.1038/nature14262','2015'),
('ENC_H2','Cassini finds molecular hydrogen in Enceladus plume','Science','PEER_REVIEWED','https://doi.org/10.1126/science.aai8703','10.1126/science.aai8703','2017'),
('ENC_P','Detection of phosphates originating from Enceladus ocean','Nature','PEER_REVIEWED','https://doi.org/10.1038/s41586-023-05987-9','10.1038/s41586-023-05987-9','2023'),
('ENC_ORG','Macromolecular organic compounds from Enceladus ice grains','Nature','PEER_REVIEWED','https://doi.org/10.1038/s41586-018-0246-4','10.1038/s41586-018-0246-4','2018'),
('TETH_GEO','Tethys geology and tectonic history from Cassini','Icarus','PEER_REVIEWED','https://doi.org/10.1016/j.icarus.2011.12.019','10.1016/j.icarus.2011.12.019','2012'),
('DIO_GEO','Dione geology and tectonics from Cassini','Icarus','PEER_REVIEWED','https://doi.org/10.1016/j.icarus.2014.03.014','10.1016/j.icarus.2014.03.014','2014'),
('DIO_OCEAN','Enceladus and Dione internal oceans constrained by gravity/topography','Geophysical Research Letters','PEER_REVIEWED','https://doi.org/10.1002/2016GL070650','10.1002/2016GL070650','2016'),
('RHEA_GEO','Rhea geology from Cassini imaging','Icarus','PEER_REVIEWED','https://doi.org/10.1016/j.icarus.2014.03.019','10.1016/j.icarus.2014.03.019','2014'),
('RHEA_EXO','Oxygen and carbon dioxide exosphere of Rhea','Science','PEER_REVIEWED','https://doi.org/10.1126/science.1198366','10.1126/science.1198366','2010'),
('TIT_HASI','Huygens atmospheric structure instrument measurements','Nature','PEER_REVIEWED','https://doi.org/10.1038/nature04314','10.1038/nature04314','2005'),
('TIT_GCMS','Huygens GCMS Titan atmosphere and surface','Nature','PEER_REVIEWED','https://doi.org/10.1038/nature04122','10.1038/nature04122','2005'),
('TIT_HYDRO','Titan hydrology and methane cycle review','Nature Geoscience','PEER_REVIEWED','https://doi.org/10.1038/ngeo1063','10.1038/ngeo1063','2011'),
('TIT_SEAS','Titan polar lakes and seas from Cassini radar','Icarus','PEER_REVIEWED','https://doi.org/10.1016/j.icarus.2013.03.022','10.1016/j.icarus.2013.03.022','2013'),
('TIT_DUNES','The sand seas of Titan: Cassini RADAR observations','Science','PEER_REVIEWED','https://doi.org/10.1126/science.1123257','10.1126/science.1123257','2006'),
('TIT_OCEAN','Titan gravity and tidal response constraints on interior/ocean','Icarus','PEER_REVIEWED','https://doi.org/10.1016/j.icarus.2014.03.018','10.1016/j.icarus.2014.03.018','2014'),
('IAP_DICH','Formation of Iapetus albedo dichotomy by thermal ice migration','Science','PEER_REVIEWED','https://doi.org/10.1126/science.1177132','10.1126/science.1177132','2010'),
('IAP_IMG','Cassini imaging science initial Iapetus results','Science','PEER_REVIEWED','https://doi.org/10.1126/science.1107981','10.1126/science.1107981','2005'),
('IAP_MICRO','Microwave spectra of leading and trailing hemispheres of Iapetus','Icarus','PEER_REVIEWED','https://doi.org/10.1016/j.icarus.2024.115950','10.1016/j.icarus.2024.115950','2024')]
SM_SOURCE_IDS={}
for key,title,auth,typ,url,doi,pub in SM_SOURCES:
 cur=db.execute('insert into source(source_key,title,authority,source_type,url,doi,publication_date,acquired_at,notes) values(?,?,?,?,?,?,?,?,?)',(key,title,auth,typ,url,doi,pub,'2026-10-06','Saturn major moons expansion reference'))
 SM_SOURCE_IDS[key]=cur.lastrowid
 db.execute('insert into source_artifact(source_id,artifact_key,retrieval_url,acquired_at,origin_kind) values(?,?,?,?,?)',(cur.lastrowid,key+'_REMOTE',url,'2026-10-06','REMOTE_REFERENCE_ONLY'))
for b in ['MIMAS','ENCELADUS','TETHYS','DIONE','RHEA','TITAN','IAPETUS']:
 cur=db.execute('insert into ephemeris_source(provider,product_name,source_url,acquired_at,status) values(?,?,?,?,?)',('NASA/JPL NAIF','Saturn satellite generic + Cassini mission SPICE authority',next(x[4] for x in SM_SOURCES if x[0]=='SAT_SPK'),'2026-10-06','REFERENCE_ONLY'))
 db.execute('insert into ephemeris_coverage(ephemeris_source_id,body_id,valid_from,valid_until,reference_frame,units,coverage_class,status) values(?,?,?,?,?,?,?,?)',(cur.lastrowid,b,None,None,'J2000 plus IAU_'+b,'km, s','GENERIC_SATURN_SATELLITE_SPK_PLUS_CASSINI_SPICE','CANDIDATE'))
