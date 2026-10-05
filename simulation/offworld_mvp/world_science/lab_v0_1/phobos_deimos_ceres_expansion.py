# Phobos/Deimos + Ceres enrichment source registration.
PD_SOURCES=[
('PHOBOS_MEX_MASS','Precise mass determination and the nature of Phobos','Geophysical Research Letters','PEER_REVIEWED','https://doi.org/10.1029/2009GL041829','10.1029/2009GL041829','2010'),
('PHOBOS_SHAPE_2024','Advancements in the 3D shape reconstruction of Phobos','Astronomy & Astrophysics','PEER_REVIEWED','https://doi.org/10.1051/0004-6361/202348665','10.1051/0004-6361/202348665','2024'),
('PHOBOS_GROOVES','Morphological and geographical evidence for the origin of Phobos grooves','Geological Society Special Publications','PEER_REVIEWED','https://doi.org/10.1144/SP356.3','10.1144/SP356.3','2011'),
('PHOBOS_REVIEW_2024','Composition and Basic Physical Properties of the Phobos Surface: A Comprehensive Review','Applied Sciences','PEER_REVIEWED','https://doi.org/10.3390/app14073127','10.3390/app14073127','2024'),
('MEX_HRSC_PDS','Mars Express HRSC/SRC Phobos observations','ESA/NASA PDS','MISSION_ARCHIVE','https://pds-geosciences.wustl.edu/missions/mars_express/hrsc.htm',None,None),
('DEIMOS_SHAPE','Deimos global shape and topography from spacecraft imaging','USGS/NASA planetary cartography','AGENCY_DATA','https://astrogeology.usgs.gov/search/map/Deimos/Viking/Deimos_Viking_Mosaic_global_40ppd',None,None),
('DEIMOS_SPECTRA','Visible and near-infrared spectral properties of Phobos and Deimos','Icarus / Mars moon spectroscopy','PEER_REVIEWED','https://doi.org/10.1016/j.icarus.2013.11.004','10.1016/j.icarus.2013.11.004','2014'),
('CERES_HCQ_SHAPE','Ceres SPC Shape Model Dataset V1.0','NASA PDS','LOOM_FROZEN_SOURCE','https://sbnarchive.psi.edu/pds3/dawn/fc/DWNCSPC_4_01/','DAWN-A-FC2-5-CERESSHAPESPC-V1.0','2018'),
('CERES_HCQ_GRAV','Dawn Ceres Gravity Science Derived Science Data V4.0','NASA PDS','LOOM_FROZEN_SOURCE','https://sbnarchive.psi.edu/pds3/dawn/grav/DWNCGRS_2_v4/','DAWN-A-RSS-5-CEGR-V4.0','2024'),
('CERES_HCQ_DTM','Dawn FC2 Derived Ceres HAMO DTM SPG V1.0','NASA PDS','LOOM_FROZEN_SOURCE','https://sbnarchive.psi.edu/pds3/dawn/fc/DWNCHSPG_2/','DAWN-A-FC2-5-CERESHAMODTMSPG-V1.0','2016'),
('CERES_HCQ_VIR','Global and localized mineralogical composition of Ceres from Dawn VIR','Dawn VIR science team','LOOM_FROZEN_SOURCE','https://doi.org/10.1111/maps.13104','10.1111/maps.13104','2018'),
('CERES_HCQ_OCCATOR','Recent cryovolcanic activity at Occator crater on Ceres','Nature Astronomy','LOOM_FROZEN_SOURCE','https://doi.org/10.1038/s41550-020-1146-8','10.1038/s41550-020-1146-8','2020'),
('CERES_HCQ_PSR','The permanently shadowed regions of dwarf planet Ceres','Geophysical Research Letters','LOOM_FROZEN_SOURCE','https://doi.org/10.1002/2016GL069368','10.1002/2016GL069368','2016'),
('CERES_HCQ_INTERIOR','A partially differentiated interior for Ceres deduced from gravity and shape','Nature','LOOM_FROZEN_SOURCE','https://doi.org/10.1038/nature18955','10.1038/nature18955','2016'),
('CERES_ICE_2019','Exposed water ice on Ceres in fresh craters','Icarus','PEER_REVIEWED','https://doi.org/10.1016/j.icarus.2018.09.008','10.1016/j.icarus.2018.09.008','2019')]
PD_SOURCE_IDS={}
for key,title,auth,typ,url,doi,pub in PD_SOURCES:
 cur=db.execute('insert into source(source_key,title,authority,source_type,url,doi,publication_date,acquired_at,notes) values(?,?,?,?,?,?,?,?,?)',(key,title,auth,typ,url,doi,pub,'2026-10-06','Phobos/Deimos/Ceres expansion; HCQ entries preserve predecessor lineage where marked'))
 PD_SOURCE_IDS[key]=cur.lastrowid
 db.execute('insert into source_artifact(source_id,artifact_key,retrieval_url,acquired_at,origin_kind) values(?,?,?,?,?)',(cur.lastrowid,key+'_REMOTE',url,'2026-10-06','REMOTE_REFERENCE_ONLY'))
# Preserve hashes of three frozen HCQ products actually available locally.
for key,sha,n in [
 ('CERES_HCQ_SHAPE','526bf5211ef103b8a587a55e7a1e1ba28246e04a484569d720d8b1107bf4c86e',6190563),
 ('CERES_HCQ_GRAV','9fa286877c0b8a7761b8bc68c46b048d2849350aa5d456738414fba122839c79',311954),
 ('CERES_HCQ_DTM','f01d63f0466540990cb1e67f6cb00be7954b38f6e9d8858cba6b9fb2138df537',23680)]:
 db.execute("update source_artifact set sha256=?,byte_count=?,origin_kind='LOOM_FROZEN' where artifact_key=?",(sha,n,key+'_REMOTE'))
