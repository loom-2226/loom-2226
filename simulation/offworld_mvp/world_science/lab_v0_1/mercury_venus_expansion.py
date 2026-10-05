# Mercury/Venus source registration. Executed after predecessor import, before common research sources.
MV_SOURCES=[
('MERCURY_PDS','MESSENGER PDS Geosciences archive','NASA PDS','MISSION_ARCHIVE','https://pds-geosciences.wustl.edu/missions/messenger/',None,None),
('MERCURY_TOPO','Image Mosaic and Topographic Maps of Mercury','USGS','AGENCY_DATA','https://pubs.usgs.gov/publication/sim3404','10.3133/sim3404','2018'),
('MERCURY_GEOLOGY','Geologic Map of Mercury','USGS','AGENCY_DATA','https://pubs.usgs.gov/sim/3459/','10.3133/sim3459','2020'),
('MERCURY_CARBON','Remote sensing evidence for an ancient carbon-bearing crust on Mercury','Nature Geoscience','PEER_REVIEWED','https://www.nature.com/articles/ngeo2669','10.1038/ngeo2669','2016'),
('MERCURY_GRAPHITE_2024','Less than one weight percent of graphite on the surface of Mercury','Nature Astronomy','PEER_REVIEWED','https://www.nature.com/articles/s41550-023-02169-5','10.1038/s41550-023-02169-5','2024'),
('MERCURY_MINERAL','Silicate mineralogy at the surface of Mercury','Nature Geoscience','PEER_REVIEWED','https://www.nature.com/articles/ngeo2860','10.1038/ngeo2860','2017'),
('MERCURY_POLAR','Mercury north polar shadow and ice constraints','Icarus/NASA NTRS','PEER_REVIEWED','https://ntrs.nasa.gov/api/citations/20160008397/downloads/20160008397.pdf',None,'2016'),
('VENUS_FACT','Venus Fact Sheet','NASA NSSDC','AGENCY_REFERENCE','https://nssdc.gsfc.nasa.gov/planetary/factsheet/venusfact.html',None,None),
('VENUS_MAGELLAN_PDS','Magellan radar/topography/emissivity products','NASA PDS','MISSION_ARCHIVE','https://pds-geosciences.wustl.edu/dataserv/doi.htm',None,None),
('VENUS_ATMOS','Venus atmosphere climate surface interior review','Space Science Reviews','PEER_REVIEWED','https://link.springer.com/article/10.1007/s11214-018-0467-8','10.1007/s11214-018-0467-8','2018'),
('VENUS_MINERAL','Mineralogy of the Venus Surface','Space Science Reviews','PEER_REVIEWED','https://link.springer.com/article/10.1007/s11214-023-00988-6','10.1007/s11214-023-00988-6','2023'),
('VENUS_VOLC_2024','Evidence of ongoing volcanic activity on Venus revealed by Magellan radar','Nature Astronomy','PEER_REVIEWED','https://www.nature.com/articles/s41550-024-02272-1','10.1038/s41550-024-02272-1','2024'),
('VENUS_VOLC_2026','Challenges to detecting present-day volcanism on Venus','Nature Astronomy','PEER_REVIEWED','https://www.nature.com/articles/s41550-026-02832-7','10.1038/s41550-026-02832-7','2026'),
('VENUS_GEOLOGY','USGS Magellan geologic mapping program / Guinevere Planitia V-30','USGS','AGENCY_DATA','https://www.usgs.gov/maps/geologic-map-guinevere-planitia-quadrangle-v-30-venus',None,'2025')]
MV_SOURCE_IDS={}
for key,title,auth,typ,url,doi,pub in MV_SOURCES:
 cur=db.execute('insert into source(source_key,title,authority,source_type,url,doi,publication_date,acquired_at,notes) values(?,?,?,?,?,?,?,?,?)',(key,title,auth,typ,url,doi,pub,'2026-10-06','Independent Mercury/Venus expansion research; remote reference unless separately acquired'))
 MV_SOURCE_IDS[key]=cur.lastrowid
 db.execute('insert into source_artifact(source_id,artifact_key,retrieval_url,acquired_at,origin_kind) values(?,?,?,?,?)',(cur.lastrowid,key+'_REMOTE',url,'2026-10-06','REMOTE_REFERENCE_ONLY'))
