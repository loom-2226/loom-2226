#!/usr/bin/env python3
import sqlite3, pathlib, hashlib, json, datetime, os
ROOT=pathlib.Path(__file__).resolve().parent
REPO=ROOT.parents[3]  # repository root from simulation/offworld_mvp/world_science/lab_v0_1
OUT=ROOT/'LOOM_SOLAR_WORLD_SCIENCE_LAB_v0_1.sqlite3'
SCHEMA=ROOT/'SCHEMA.sql'
V10=REPO/'dev/solar_baseline_02_wgccre/LOOM_SOLAR_BASELINE_02_WGCCRE_CANDIDATE_V10.sqlite3'
M4B=REPO/'dev/solar_civprop_m4b/LOOM_SOLAR_CIVPROP_M4B_CANDIDATE.sqlite3'
BODIES=['MOON','MARS','CERES','BENNU','JUNO','VARUNA','MERCURY','VENUS','PHOBOS','DEIMOS','VESTA','JUPITER','SATURN','URANUS','NEPTUNE','PLUTO','PSYCHE','RYUGU','ITOKAWA','EROS','LUTETIA','STEINS','MATHILDE','IDA','DACTYL','IO','EUROPA','GANYMEDE','CALLISTO','MIMAS','ENCELADUS','TETHYS','DIONE','RHEA','TITAN','IAPETUS','MIRANDA','ARIEL','UMBRIEL','TITANIA','OBERON','TRITON','CHARON','STYX','NIX','KERBEROS','HYDRA']
if OUT.exists(): OUT.unlink()
db=sqlite3.connect(OUT); db.execute('PRAGMA foreign_keys=ON'); db.executescript(SCHEMA.read_text())
db.executemany('insert into lab_meta values(?,?)',[('classification','EXPERIMENTAL_NON_CANON_NON_RUNTIME_NON_AUTHORITY'),('built_utc','2026-10-06T00:00:00Z'),('github_authority_commit','788f31c200ce59e844e44ef01ca62f37eb129bd8'),('predecessor_v10_sha256',hashlib.sha256(V10.read_bytes()).hexdigest()),('predecessor_m4b_sha256',hashlib.sha256(M4B.read_bytes()).hexdigest())])
v=sqlite3.connect(V10); v.row_factory=sqlite3.Row
pending={b:v.execute('select * from authority_body_ref where body_id=?',(b,)).fetchone() for b in BODIES}
while pending:
 progressed=False
 for b,r in list(pending.items()):
  parent = 'MARS' if r['parent_body_id']=='MARS_SYSTEM_BARYCENTER' else ('JUPITER' if r['parent_body_id']=='JUPITER_SYSTEM_BARYCENTER' and r['body_id'] in ('IO','EUROPA','GANYMEDE','CALLISTO') else ('SATURN' if r['parent_body_id']=='SATURN_SYSTEM_BARYCENTER' and r['body_id'] in ('MIMAS','ENCELADUS','TETHYS','DIONE','RHEA','TITAN','IAPETUS') else ('URANUS' if r['parent_body_id']=='URANUS_SYSTEM_BARYCENTER' and r['body_id'] in ('MIRANDA','ARIEL','UMBRIEL','TITANIA','OBERON') else ('NEPTUNE' if r['parent_body_id']=='NEPTUNE_SYSTEM_BARYCENTER' and r['body_id']=='TRITON' else ('PLUTO' if r['parent_body_id']=='PLUTO_SYSTEM_BARYCENTER' and r['body_id']=='CHARON' else (None if r['parent_body_id'] in ('JUPITER_SYSTEM_BARYCENTER','SATURN_SYSTEM_BARYCENTER','URANUS_SYSTEM_BARYCENTER','NEPTUNE_SYSTEM_BARYCENTER','PLUTO_SYSTEM_BARYCENTER') else r['parent_body_id']))))))
  if parent is None or db.execute('select 1 from body where body_id=?',(parent,)).fetchone():
   db.execute('insert into body values(?,?,?,?,?)',(r['body_id'],r['canonical_name'],r['body_class'],parent,'EXPERIMENTAL'))
   for x in v.execute('select * from body_identifier_ref where body_id=?',(b,)):
    db.execute('insert into body_identifier values(?,?,?,?,?)',(b,x['authority'],x['identifier_type'],x['identifier_value'],x['identifier_status']))
   del pending[b]; progressed=True
 if not progressed: raise RuntimeError('Unresolved body-parent dependency: '+repr(list(pending)))
# preserve V10 source artifacts and assertions
srcmap={}
for r in v.execute("select distinct sa.* from source_artifact sa join candidate_assertion ca on ca.source_artifact_id=sa.artifact_id where ca.body_id in (%s)"%','.join('?'*len(BODIES)),BODIES):
 key='LOOM_V10_'+r['artifact_id']; cur=db.execute('insert into source(source_key,title,authority,source_type,url,publication_date,notes) values(?,?,?,?,?,?,?)',(key,r['product'] or key,r['authority'],'LOOM_FROZEN_SOURCE',r['source_url'],None,'Imported read-only from V10; product_version='+str(r['version']))); sid=cur.lastrowid; srcmap[r['artifact_id']]=sid
 db.execute('insert into source_artifact(source_id,artifact_key,local_path,sha256,byte_count,retrieval_url,acquired_at,origin_kind) values(?,?,?,?,?,?,?,?)',(sid,key+'_ART',None,r['sha256'],r['byte_count'],r['source_url'],r['acquired_at_utc'],'LOOM_FROZEN'))
for b in BODIES:
 for r in v.execute('select * from candidate_assertion where body_id=?',(b,)):
  sid=srcmap[r['source_artifact_id']]
  vk='TEXT'; vn=None; vt=r['reported_value']
  try: vn=float(str(r['normalized_value'])); vk='NUMERIC'; vt=None
  except: pass
  db.execute("""insert into scientific_assertion(assertion_key,body_id,property_code,ontology,scope,value_kind,value_numeric,value_text,unit,uncertainty_text,epistemic_class,representativeness,source_id,source_locator,lineage,admission_status,preferred,origin,notes)
  values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",('LOOM_V10_'+r['assertion_id'],b,r['property_code'],'DERIVED' if r['epistemic_class']=='DERIVED' else ('MODEL_INFERENCE' if r['epistemic_class'] in ('DYNAMICAL_INFERENCE','PHYSICAL_MODEL') else 'REAL_EVIDENCE'),'BODY',vk,vn,vt,r['reported_unit'],r['reported_uncertainty'],r['epistemic_class'],'BODY_REPRESENTATIVE',sid,r['source_reference'],r['source_lineage'],r['fact_status'],r['preferred_fact'],'EXISTING_LOOM','Original scope='+str(r['scope'])+'; disposition='+str(r['disposition'])))
 for g in v.execute("select * from coverage where body_id=? and disposition<>'SUPPORTED'",(b,)):
  state={'SOURCE_DOES_NOT_COVER_BODY_CLASS':'SOURCE_DOES_NOT_COVER','SOURCE_NOT_FOUND':'SOURCE_NOT_FOUND','SOURCE_NOT_PRESENT':'SOURCE_NOT_PRESENT','NOT_APPLICABLE':'NOT_APPLICABLE'}.get(g['disposition'],'UNKNOWN')
  db.execute('insert or ignore into coverage(body_id,domain,property_or_class,state,origin,reason) values(?,?,?,?,?,?)',(b,'PHYSICAL_BASELINE',g['property_code'],state,'EXISTING_LOOM',g['reason']))
v.close()
# M4B evidence preserved as candidate without pretending region IDs transfer across schemas
m=sqlite3.connect(M4B); m.row_factory=sqlite3.Row
m4src={}
for b in BODIES:
 for r in m.execute('select * from material_evidence where body_id=?',(b,)):
  oldsid=r['source_id']
  if oldsid not in m4src:
   sr=m.execute('select * from source where source_id=?',(oldsid,)).fetchone(); key='LOOM_M4B_SOURCE_'+str(oldsid)
   cur=db.execute('insert into source(source_key,title,authority,source_type,url,doi,publication_date,notes) values(?,?,?,?,?,?,?,?)',(key,sr['title'],sr['provider'],sr['source_type'],sr['url'],sr['doi'],sr['publication_date'],'Imported from M4B source_id '+str(oldsid))); m4src[oldsid]=cur.lastrowid
  db.execute("""insert into material_evidence(body_id,material_family,material_species,physical_form,evidence_class,abundance_semantics,abundance_value,abundance_min,abundance_max,abundance_unit,depth_min,depth_max,depth_unit,scope,representativeness,source_id,admission_status,origin,notes) values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",(b,r['material_family'],r['material_species'],r['physical_form'],r['evidence_class'],r['abundance_semantics'],r['abundance_value'],r['abundance_min'],r['abundance_max'],r['abundance_unit'],r['depth_min'],r['depth_max'],r['depth_unit'],'SAMPLE' if 'SAMPLE' in (r['spatial_heterogeneity'] or '') else ('REGION' if r['region_id'] else 'BODY'),'SAMPLE_ONLY' if 'SAMPLE' in (r['spatial_heterogeneity'] or '') else ('REGION_REPRESENTATIVE' if r['region_id'] else 'UNKNOWN'),m4src[oldsid],r['fact_status'],'EXISTING_LOOM','Original M4B material_evidence_id='+str(r['material_evidence_id'])+'; '+str(r['notes'])))
# preserve M4B frozen artifact hashes for sources actually used by the six bodies
for oldsid,newsid in m4src.items():
 for ar in m.execute('select * from source_artifact where source_id=?',(oldsid,)):
  db.execute('insert or ignore into source_artifact(source_id,artifact_key,local_path,sha256,byte_count,retrieval_url,acquired_at,origin_kind) values(?,?,?,?,?,?,?,?)',(newsid,'LOOM_M4B_ART_'+str(ar['artifact_id']),str(ar['local_path']) if ar['local_path'] else None,ar['sha256'],ar['byte_count'],ar['locator'],ar['retrieved_at'],'LOOM_FROZEN'))
m.close()
exec((ROOT/'mercury_venus_expansion.py').read_text(),globals())
exec((ROOT/'phobos_deimos_ceres_expansion.py').read_text(),globals())
exec((ROOT/'vesta_outer_pluto_expansion.py').read_text(),globals())
exec((ROOT/'eight_asteroid_expansion.py').read_text(),globals())
exec((ROOT/'galilean_moons_expansion.py').read_text(),globals())
exec((ROOT/'saturn_moons_expansion.py').read_text(),globals())
exec((ROOT/'outer_system_moons_expansion.py').read_text(),globals())
# independent research sources
sources=[
('USGS_MOON_GEOLOGY','Unified Geologic Map of the Moon','USGS','AGENCY_DATA','https://www.usgs.gov/news/astrogeology-releases-new-map-moon','10.5066/P98X1IVS','2020-04-20'),
('NASA_MOON_WATER','Moon Water and Ices','NASA','AGENCY_SYNTHESIS','https://science.nasa.gov/moon/moon-water-and-ices/',None,None),
('LCROSS_WATER','LCROSS Cabeus water analysis','NASA/mission science','PEER_REVIEWED','https://ntrs.nasa.gov/api/citations/20180000405/downloads/20180000405.pdf',None,None),
('NASA_MOON_ILLUM','South Pole Illumination Map','NASA/LRO','MISSION_PRODUCT','https://science.nasa.gov/photojournal/south-pole-illumination-map/',None,None),
('USGS_MARS_GEOLOGY','Geologic Map of Mars','USGS','AGENCY_DATA','https://pubs.usgs.gov/publication/sim3292','10.3133/sim3292','2014'),
('NASA_MARS_SWIM','SWIM subsurface water ice map','NASA/JPL','MISSION_PRODUCT','https://science.nasa.gov/resource/swim-map-shows-subsurface-water-ice-on-mars/',None,None),
('NASA_PHOENIX','Mars Phoenix science highlights','NASA','MISSION_SYNTHESIS','https://science.nasa.gov/mission/mars-phoenix/',None,None),
('NASA_CERES','Dawn Ceres science summary','NASA','MISSION_SYNTHESIS','https://science.nasa.gov/mission/dawn/science/ceres/',None,None),
('JPL_CERES_INTERIOR','Ceres internal structure','NASA/JPL','MISSION_SYNTHESIS','https://www.jpl.nasa.gov/images/pia22660-ceres-internal-structure-artists-concept/',None,'2018-08-14'),
('NASA_BENNU','Bennu facts and returned sample','NASA','MISSION_SYNTHESIS','https://science.nasa.gov/solar-system/asteroids/101955-bennu/facts/',None,None),
('BENNU_PHOSPHATE','Initial Bennu sample mineralogy','NASA/OSIRIS-REx','MISSION_SYNTHESIS','https://www.nasa.gov/missions/osiris-rex/surprising-phosphate-finding-in-nasas-osiris-rex-asteroid-sample/','10.1111/maps.14227','2024-06-26'),
('BENNU_BRINE','Evaporite sequence from ancient brine recorded in Bennu samples','Nature','PEER_REVIEWED','https://www.nature.com/articles/s41586-024-08495-6','10.1038/s41586-024-08495-6','2025'),
('BENNU_HYDROTHERMAL','Mineralogical evidence for hydrothermal alteration of Bennu samples','Nature Geoscience','PEER_REVIEWED','https://www.nature.com/articles/s41561-025-01741-0','10.1038/s41561-025-01741-0','2025'),
('BENNU_MATERIALS','Variety and origin of materials accreted by Bennu parent asteroid','Nature Astronomy','PEER_REVIEWED','https://www.nature.com/articles/s41550-025-02631-6','10.1038/s41550-025-02631-6','2025'),
('JUNO_SHAPE','VLT/SPHERE- and ALMA-based shape reconstruction of asteroid 3 Juno','Astronomy & Astrophysics','PEER_REVIEWED','https://www.aanda.org/articles/aa/full_html/2015/09/aa26626-15/aa26626-15.html','10.1051/0004-6361/201526626','2015'),
('JUNO_ALMA','ALMA observations of asteroid 3 Juno at 60 km resolution','Astrophysical Journal Letters','PEER_REVIEWED','https://doi.org/10.1088/2041-8205/808/1/L2','10.1088/2041-8205/808/1/L2','2015'),
('JUNO_COMPOSITION','Multispectral analysis of asteroid 3 Juno','Icarus','PEER_REVIEWED','https://doi.org/10.1016/S0019-1035(03)00049-6','10.1016/S0019-1035(03)00049-6','2003'),
('VARUNA_SIZE','Size and albedo of Kuiper-belt object 20000 Varuna','Nature','PEER_REVIEWED','https://www.nature.com/articles/35078008','10.1038/35078008','2001'),
('VARUNA_PHYSICAL','Physical Properties of Trans-Neptunian Object 20000 Varuna','Astronomical Journal','PEER_REVIEWED','https://arxiv.org/abs/astro-ph/0201082',None,'2002'),
('VARUNA_SPECTRA','Rotationally resolved spectroscopy of 20000 Varuna in near-infrared','Astronomy & Astrophysics','PEER_REVIEWED','https://www.iac.es/en/science-and-technology/publications/rotationally-resolved-spectroscopy-20000-varuna-near-infrared',None,'2014')]
newsrc={}
for key,title,auth,typ,url,doi,pub in sources:
 cur=db.execute('insert into source(source_key,title,authority,source_type,url,doi,publication_date,acquired_at,notes) values(?,?,?,?,?,?,?,?,?)',(key,title,auth,typ,url,doi,pub,'2026-10-06','Discovered/verified in independent 2026-10-06 research pass; remote reference unless separately acquired')); newsrc[key]=cur.lastrowid
 db.execute('insert into source_artifact(source_id,artifact_key,retrieval_url,acquired_at,origin_kind) values(?,?,?,?,?)',(cur.lastrowid,key+'_REMOTE',url,'2026-10-06','REMOTE_REFERENCE_ONLY'))
# regions and sample
regions=[('MOON','MOON_SOUTH_POLAR','Lunar south polar region','REGION'),('MOON','CABEU','Cabeus crater','LOCAL_SITE'),('MARS','MARS_N_MIDLAT','Northern mid-latitudes','REGION'),('MARS','PHOENIX_SITE','Phoenix landing site','LOCAL_SITE'),('CERES','CERES_HIGH_LAT','Ceres high latitudes','REGION'),('CERES','OCCATOR','Occator crater','REGION'),('BENNU','NIGHTINGALE','Nightingale TAG site','LOCAL_SITE'),('JUNO','JUNO_SURFACE','Juno observed surface','REGION'),('VARUNA','VARUNA_VISIBLE','Varuna disk-integrated surface','FOOTPRINT')]
reg={}
for b,k,n,t in regions: reg[k]=db.execute('insert into region(body_id,region_key,region_name,region_type) values(?,?,?,?)',(b,k,n,t)).lastrowid
sample=db.execute('insert into sample(body_id,region_id,sample_key,sample_name,collection_site,collection_method,mass_value,mass_unit,source_id,notes) values(?,?,?,?,?,?,?,?,?,?)',('BENNU',reg['NIGHTINGALE'],'BENNU_RETURN_2023','OSIRIS-REx returned Bennu sample','Nightingale','TAGSAM',121.6,'g',newsrc['NASA_BENNU'],'Returned mass; sample is not automatically body-representative')).lastrowid
# spatial products
products=[
('MOON',None,'MOON_GLOBAL_GEOLOGY','GEOLOGIC_MAP','Unified Geologic Map of the Moon','USGS_MOON_GEOLOGY',5000,'m','BODY'),
('MOON',reg['MOON_SOUTH_POLAR'],'MOON_SOUTH_ILLUM','ILLUMINATION_MAP','LRO south-pole illumination mapping','NASA_MOON_ILLUM',None,None,'REGION'),
('MARS',None,'MARS_GLOBAL_GEOLOGY','GEOLOGIC_MAP','USGS global geologic map of Mars','USGS_MARS_GEOLOGY',20000,'m','BODY'),
('MARS',reg['MARS_N_MIDLAT'],'MARS_SWIM','ICE_STABILITY_PROBABILITY','SWIM subsurface water-ice mapping','NASA_MARS_SWIM',None,None,'MODEL_DOMAIN')]
prod={}
for b,rid,k,t,title,sk,res,u,scope in products: prod[k]=db.execute('insert into spatial_product(body_id,region_id,product_key,product_type,title,source_id,horizontal_resolution_value,horizontal_resolution_unit,scope,status) values(?,?,?,?,?,?,?,?,?,?)',(b,rid,k,t,title,newsrc[sk],res,u,scope,'CANDIDATE')).lastrowid
def A(key,b,prop,ont,scope,src,kind='TEXT',num=None,text=None,unit=None,unc=None,vmin=None,vmax=None,rep='UNKNOWN',region=None,sample_id=None,product=None,method=None,notes=None):
 db.execute("""insert into scientific_assertion(assertion_key,body_id,property_code,ontology,scope,region_id,sample_id,spatial_product_id,value_kind,value_numeric,value_text,unit,uncertainty_text,value_min,value_max,epistemic_class,measurement_method,representativeness,source_id,admission_status,preferred,origin,notes) values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",(key,b,prop,ont,scope,region,sample_id,product,kind,num,text,unit,unc,vmin,vmax,'MEASURED' if ont=='REAL_EVIDENCE' else 'MODEL_INFERENCE',method,rep,newsrc[src],'CANDIDATE',0,'NEW_CHATGPT_RESEARCH',notes))
# high-value independent constraints, intentionally selective
A('R_MOON_GEOLOGY','MOON','GLOBAL_GEOLOGIC_UNITS','REAL_EVIDENCE','BODY','USGS_MOON_GEOLOGY','SPATIAL_PRODUCT',text='global mapped geologic units',rep='BODY_REPRESENTATIVE',product=prod['MOON_GLOBAL_GEOLOGY'])
A('R_MOON_PSR','MOON','PERMANENT_SHADOW_AND_ILLUMINATION','REAL_EVIDENCE','REGION','NASA_MOON_ILLUM','SPATIAL_PRODUCT',text='persistent illumination and permanent-shadow geography',rep='REGION_REPRESENTATIVE',region=reg['MOON_SOUTH_POLAR'],product=prod['MOON_SOUTH_ILLUM'])
A('R_MOON_CAB_WATER','MOON','WATER_ICE_WT_PERCENT','REAL_EVIDENCE','LOCAL_SITE','LCROSS_WATER','NUMERIC',5.6,None,'wt%','±2.9',rep='SITE_ONLY',region=reg['CABEU'],method='LCROSS impact plume spectroscopy',notes='Cabeus local measurement; never a lunar/global abundance')
A('R_MARS_GEOLOGY','MARS','GLOBAL_GEOLOGIC_UNITS','REAL_EVIDENCE','BODY','USGS_MARS_GEOLOGY','SPATIAL_PRODUCT',text='global mapped geologic units and landforms',rep='BODY_REPRESENTATIVE',product=prod['MARS_GLOBAL_GEOLOGY'])
A('R_MARS_SWIM','MARS','SUBSURFACE_WATER_ICE_PROBABILITY','MODEL_INFERENCE','MODEL_DOMAIN','NASA_MARS_SWIM','SPATIAL_PRODUCT',text='integrated orbital ice-consistency/stability mapping',rep='MODEL_DOMAIN_ONLY',region=reg['MARS_N_MIDLAT'],product=prod['MARS_SWIM'])
A('R_MARS_PHOENIX_ICE','MARS','SUBSURFACE_WATER_ICE','REAL_EVIDENCE','LOCAL_SITE','NASA_PHOENIX','DETECTION',text='water ice verified in shallow subsurface',rep='SITE_ONLY',region=reg['PHOENIX_SITE'],method='Phoenix excavation/TEGA')
A('R_MARS_PHOENIX_PERCH','MARS','PERCHLORATE','REAL_EVIDENCE','LOCAL_SITE','NASA_PHOENIX','DETECTION',text='perchlorate detected in soil',rep='SITE_ONLY',region=reg['PHOENIX_SITE'])
A('R_CERES_DIFF','CERES','INTERIOR_DIFFERENTIATION','MODEL_INFERENCE','MODEL_DOMAIN','NASA_CERES','MODEL',text='density increases with depth; differentiated water-rich phases over denser rock',rep='MODEL_DOMAIN_ONLY')
A('R_CERES_HIGH_ICE','CERES','HIGH_LATITUDE_ICE','REAL_EVIDENCE','REGION','NASA_CERES','DETECTION',text='multiple lines of evidence indicate abundant ice at high latitudes',rep='REGION_REPRESENTATIVE',region=reg['CERES_HIGH_LAT'])
A('R_CERES_CRUST','CERES','CRUST_COMPOSITION_MODEL','MODEL_INFERENCE','MODEL_DOMAIN','JPL_CERES_INTERIOR','MODEL',text='~40 km crust modeled as mixture of ice, salts and hydrated minerals',rep='MODEL_DOMAIN_ONLY',notes='model interpretation, not direct sampled stratigraphy')
A('R_BENNU_RETURN_MASS','BENNU','RETURNED_SAMPLE_MASS','REAL_EVIDENCE','SAMPLE','NASA_BENNU','NUMERIC',121.6,None,'g',rep='SAMPLE_ONLY',sample_id=sample)
A('R_BENNU_PHOS','BENNU','MG_NA_PHOSPHATE','REAL_EVIDENCE','SAMPLE','BENNU_PHOSPHATE','DETECTION',text='magnesium-sodium phosphate present; not detected in spacecraft remote sensing',rep='SAMPLE_ONLY',sample_id=sample)
A('R_BENNU_SALTS','BENNU','EVAPORITE_SALT_ASSEMBLAGE','REAL_EVIDENCE','SAMPLE','BENNU_BRINE','DETECTION',text='Na-bearing phosphates plus Na-rich carbonates, sulfates, chlorides and fluorides',rep='SAMPLE_ONLY',sample_id=sample)
A('R_BENNU_BRINE_MODEL','BENNU','ANCIENT_BRINE_HISTORY','MODEL_INFERENCE','SAMPLE','BENNU_BRINE','MODEL',text='salts interpreted as precipitation during evaporation/freezing of late-stage parent-body brine',rep='SAMPLE_ONLY',sample_id=sample)
A('R_BENNU_HYDRO','BENNU','HYDROTHERMAL_ALTERATION','MODEL_INFERENCE','SAMPLE','BENNU_HYDROTHERMAL','MODEL',text='mineral textures record evolving aqueous alteration fluid; sulfide compositions imply ~25 C alteration',rep='SAMPLE_ONLY',sample_id=sample)
A('R_BENNU_HETERO','BENNU','PARENT_RESERVOIR_HETEROGENEITY','MODEL_INFERENCE','SAMPLE','BENNU_MATERIALS','MODEL',text='sample components imply heterogeneous outer-protoplanetary-disk reservoir and extensive aqueous alteration',rep='SAMPLE_ONLY',sample_id=sample)
A('R_JUNO_SHAPE','JUNO','THREE_DIMENSIONAL_SHAPE','MODEL_INFERENCE','BODY','JUNO_SHAPE','MODEL',text='ADAM reconstruction from SPHERE, ALMA, adaptive optics, occultation and lightcurves; sizable non-rounded impact-shaped features',rep='BODY_REPRESENTATIVE')
A('R_JUNO_DIAM','JUNO','GEOMETRIC_MEAN_DIAMETER','REAL_EVIDENCE','FOOTPRINT','JUNO_ALMA','NUMERIC',259,None,'km','±4',rep='FOOTPRINT_ONLY',region=reg['JUNO_SURFACE'],method='ALMA 1.3 mm imaging')
A('R_JUNO_TEMP_MED','JUNO','SURFACE_BRIGHTNESS_TEMPERATURE_MEDIAN','REAL_EVIDENCE','FOOTPRINT','JUNO_ALMA','NUMERIC',197,None,'K','±15',rep='FOOTPRINT_ONLY',region=reg['JUNO_SURFACE'],method='ALMA 1.3 mm imaging',notes='median over observed surface during one epoch, not equilibrium/global temperature')
A('R_JUNO_TEMP_PEAK','JUNO','SURFACE_BRIGHTNESS_TEMPERATURE_PEAK_MEDIAN','REAL_EVIDENCE','FOOTPRINT','JUNO_ALMA','NUMERIC',215,None,'K','±13',rep='FOOTPRINT_ONLY',region=reg['JUNO_SURFACE'])
A('R_JUNO_REGOLITH','JUNO','THERMAL_INERTIA_HETEROGENEITY','MODEL_INFERENCE','FOOTPRINT','JUNO_ALMA','MODEL',text='longitude-dependent brightness pattern suggests lower thermal inertia near putative large impact feature',rep='FOOTPRINT_ONLY',region=reg['JUNO_SURFACE'])
A('R_JUNO_MIN','JUNO','OLIVINE_PYROXENE_SURFACE','REAL_EVIDENCE','REGION','JUNO_COMPOSITION','DETECTION',text='olivine-pyroxene-rich surface with areal spectral variation interpreted near large impact feature',rep='REGION_REPRESENTATIVE',region=reg['JUNO_SURFACE'])
A('R_VARUNA_DIAM_2001','VARUNA','EFFECTIVE_DIAMETER','REAL_EVIDENCE','BODY','VARUNA_SIZE','NUMERIC',900,None,'km','+129/-145',rep='BODY_REPRESENTATIVE')
A('R_VARUNA_ALBEDO_2001','VARUNA','RED_GEOMETRIC_ALBEDO','REAL_EVIDENCE','BODY','VARUNA_SIZE','NUMERIC',0.070,None,None,'+0.030/-0.017',rep='BODY_REPRESENTATIVE')
A('R_VARUNA_ROT','VARUNA','ROTATION_PERIOD','REAL_EVIDENCE','BODY','VARUNA_PHYSICAL','NUMERIC',6.3442,None,'h','±0.0002',rep='BODY_REPRESENTATIVE')
A('R_VARUNA_LC','VARUNA','LIGHTCURVE_AMPLITUDE_R','REAL_EVIDENCE','BODY','VARUNA_PHYSICAL','NUMERIC',0.42,None,'mag','±0.02',rep='BODY_REPRESENTATIVE')
A('R_VARUNA_SHAPE','VARUNA','ELONGATED_SHAPE','MODEL_INFERENCE','MODEL_DOMAIN','VARUNA_PHYSICAL','MODEL',text='rapid double-peaked lightcurve consistent with elongated/Jacobi-like body; projected axis ratio about 1.5:1 under model assumptions',rep='MODEL_DOMAIN_ONLY')
A('R_VARUNA_DENS','VARUNA','BULK_DENSITY_MODEL','MODEL_INFERENCE','MODEL_DOMAIN','VARUNA_PHYSICAL','NUMERIC',1000,None,'kg/m^3',None,rep='MODEL_DOMAIN_ONLY',notes='model-dependent Jacobi/rubble-pile inference, not direct dynamical mass-density measurement')
A('R_VARUNA_H2O','VARUNA','SURFACE_WATER_ICE','REAL_EVIDENCE','FOOTPRINT','VARUNA_SPECTRA','DETECTION',text='2.0 micron absorption consistent with surface water ice in all rotational spectra',rep='FOOTPRINT_ONLY',region=reg['VARUNA_VISIBLE'])
A('R_VARUNA_HET','VARUNA','SPECTRAL_ROTATIONAL_HETEROGENEITY','REAL_EVIDENCE','FOOTPRINT','VARUNA_SPECTRA','TEXT',text='no surface spectral variability detected at 2 sigma over observed rotation',rep='FOOTPRINT_ONLY',region=reg['VARUNA_VISIBLE'],notes='nondetection at study sensitivity is not proof of global homogeneity')
A('R_VARUNA_OTHER_VOL','VARUNA','OTHER_VOLATILES','REAL_EVIDENCE','FOOTPRINT','VARUNA_SPECTRA','TEXT',text='no other volatile absorption detected; S/N insufficient to exclude small quantities',rep='FOOTPRINT_ONLY',region=reg['VARUNA_VISIBLE'])
# explicit research coverage frontier
domains=['NAVIGATION_DYNAMICS','PHYSICAL','GEOLOGICAL','COMPOSITION','VOLATILES','ENVIRONMENTAL','SPATIAL','MECHANICAL_GEOTECHNICAL','SAMPLE_EVIDENCE','RESOURCE_RELEVANCE']
strength={
'MOON':['STRONG','STRONG','STRONG','STRONG','STRONG','STRONG','STRONG','MODERATE','STRONG','MODERATE'],
'MARS':['STRONG','STRONG','STRONG','STRONG','STRONG','STRONG','STRONG','MODERATE','STRONG','MODERATE'],
'CERES':['STRONG','STRONG','MODERATE','STRONG','STRONG','MODERATE','MODERATE','WEAK','NOT_APPLICABLE','MODERATE'],
'BENNU':['STRONG','STRONG','MODERATE','STRONG','MODERATE','MODERATE','STRONG','MODERATE','STRONG','MODERATE'],
'JUNO':['MODERATE','MODERATE','WEAK','MODERATE','UNKNOWN','MODERATE','MODERATE','WEAK','NOT_APPLICABLE','WEAK'],
'VARUNA':['WEAK','WEAK','UNKNOWN','WEAK','WEAK','WEAK','WEAK','UNKNOWN','NOT_APPLICABLE','UNKNOWN']}
for b in ['MOON','MARS','CERES','BENNU','JUNO','VARUNA']:
 for dom,st in zip(domains,strength[b]):
  state='SUPPORTED' if st not in ('UNKNOWN','NOT_APPLICABLE') else st
  db.execute('insert or ignore into coverage(body_id,domain,property_or_class,state,origin,reason) values(?,?,?,?,?,?)',(b,dom,'DOMAIN_COVERAGE',state,'NEW_CHATGPT_RESEARCH','Strength='+st+'; see COVERAGE_MATRIX.csv for evaluative grade'))
db.commit()
exec((ROOT/'mercury_venus_post.py').read_text(),globals())
db.commit()
exec((ROOT/'phobos_deimos_ceres_post.py').read_text(),globals())
exec((ROOT/'vesta_outer_pluto_post.py').read_text(),globals())
exec((ROOT/'eight_asteroid_post.py').read_text(),globals())
exec((ROOT/'galilean_moons_post.py').read_text(),globals())
exec((ROOT/'saturn_moons_post.py').read_text(),globals())
exec((ROOT/'outer_system_moons_post.py').read_text(),globals())
db.commit()
# manifest generated from DB
manifest=[dict(zip([d[0] for d in db.execute('select * from source').description],r)) for r in db.execute('select * from source order by source_id')]
(ROOT/'SOURCE_MANIFEST.json').write_text(json.dumps(manifest,indent=2))
db.close()
print(OUT)
