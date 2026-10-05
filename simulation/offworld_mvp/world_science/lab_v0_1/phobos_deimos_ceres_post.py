S=PD_SOURCE_IDS
def RR(b,k,n,t,parent=None,notes=None): return db.execute('insert into region(body_id,region_key,region_name,region_type,parent_region_id,notes) values(?,?,?,?,?,?)',(b,k,n,t,parent,notes)).lastrowid
stick=RR('PHOBOS','STICKNEY','Stickney crater','REGION'); pglob=RR('PHOBOS','PHOBOS_GLOBAL','Phobos global surface','REGION')
dglob=RR('DEIMOS','DEIMOS_GLOBAL','Deimos global surface','REGION')
occ=db.execute("select region_id from region where body_id='CERES' and region_key='OCCATOR'").fetchone()[0]
ah=RR('CERES','AHUNA_MONS','Ahuna Mons','REGION'); psr=RR('CERES','CERES_N_PSR','Ceres northern polar permanently shadowed regions','REGION'); er=RR('CERES','ERNUTET','Ernutet organic-bearing region','REGION'); dtmr=RR('CERES','CERES_REGIONAL_DTM','Ceres regional DTM coverage','REGION')
def PP(b,r,k,t,title,src,res=None,u=None,scope='BODY',frame=None):
 return db.execute('insert into spatial_product(body_id,region_id,product_key,product_type,title,source_id,horizontal_resolution_value,horizontal_resolution_unit,coordinate_frame,scope,status) values(?,?,?,?,?,?,?,?,?,?,?)',(b,r,k,t,title,S[src],res,u,frame,scope,'CANDIDATE')).lastrowid
pshape=PP('PHOBOS',None,'PHOBOS_SHAPE_2024','SHAPE_MODEL','High-resolution Phobos shape model from Mars Express/SRC and Viking imaging','PHOBOS_SHAPE_2024',scope='BODY')
pimg=PP('PHOBOS',pglob,'PHOBOS_HRSC_SRC','IMAGE_MOSAIC','Mars Express HRSC/SRC Phobos imaging','MEX_HRSC_PDS',scope='REGION')
dimg=PP('DEIMOS',dglob,'DEIMOS_VIKING_MOSAIC','IMAGE_MOSAIC','Viking global Deimos image mosaic','DEIMOS_SHAPE',scope='REGION')
cshape=PP('CERES',None,'CERES_SPC_SHAPE','SHAPE_MODEL','Ceres SPC shape model V1.0','CERES_HCQ_SHAPE',100,'m','BODY','Dawn Ceres body-fixed')
cgrav=PP('CERES',None,'CERES70E','GRAVITY_FIELD','CERES70E degree/order 70 gravity field','CERES_HCQ_GRAV',scope='MODEL_DOMAIN',frame='Dawn Ceres body-fixed')
cdtm=PP('CERES',None,'CERES_HAMO_DTM','DIGITAL_TERRAIN_MODEL','Ceres HAMO SPG DTM ~98% coverage','CERES_HCQ_DTM',136.7,'m','BODY','dawn_ceres_SPG20160107')
cvir=PP('CERES',None,'CERES_VIR_MAP','MINERALOGY_MAP','Dawn VIR global/localized composition mapping','CERES_HCQ_VIR',scope='BODY')
cpsr=PP('CERES',psr,'CERES_PSR_MODEL','THERMAL_COLD_TRAP_MODEL','Ceres northern polar permanently shadowed region model','CERES_HCQ_PSR',scope='MODEL_DOMAIN')
creg=PP('CERES',dtmr,'CERES_LAMO_REGIONAL_DTM','REGIONAL_DIGITAL_TERRAIN_MODEL','Dawn LAMO regional DTM collection','CERES_HCQ_DTM',scope='REGION')
def Q(key,b,prop,ont,scope,src,kind='TEXT',num=None,text=None,unit=None,unc=None,vmin=None,vmax=None,rep='UNKNOWN',region=None,product=None,method=None,notes=None):
 db.execute('''insert into scientific_assertion(assertion_key,body_id,property_code,ontology,scope,region_id,spatial_product_id,value_kind,value_numeric,value_text,unit,uncertainty_text,value_min,value_max,epistemic_class,measurement_method,representativeness,source_id,admission_status,preferred,origin,notes) values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',(key,b,prop,ont,scope,region,product,kind,num,text,unit,unc,vmin,vmax,'MEASURED' if ont=='REAL_EVIDENCE' else 'MODEL_INFERENCE',method,rep,S[src],'CANDIDATE',0,'NEW_CHATGPT_RESEARCH' if not src.startswith('CERES_HCQ_') else 'EXISTING_LOOM',notes))
# Phobos
Q('R_PHOBOS_MEX_GM','PHOBOS','GM_MARS_EXPRESS','REAL_EVIDENCE','BODY','PHOBOS_MEX_MASS','NUMERIC',0.0007127,unit='km^3/s^2',unc='±0.0000021',rep='BODY_REPRESENTATIVE',method='Mars Express radio tracking')
Q('R_PHOBOS_MEX_DENS','PHOBOS','BULK_DENSITY_MARS_EXPRESS','DERIVED','BODY','PHOBOS_MEX_MASS','NUMERIC',1876,unit='kg/m^3',unc='±20',rep='BODY_REPRESENTATIVE')
Q('R_PHOBOS_POROSITY','PHOBOS','POROSITY_MODEL','MODEL_INFERENCE','MODEL_DOMAIN','PHOBOS_MEX_MASS','NUMERIC',30,unit='%',unc='±5',rep='MODEL_DOMAIN_ONLY',notes='depends on assumed grain-density/composition; bulk density is measured more directly than porosity')
Q('R_PHOBOS_SHAPE','PHOBOS','HIGH_RESOLUTION_SHAPE','MODEL_INFERENCE','BODY','PHOBOS_SHAPE_2024','SPATIAL_PRODUCT',text='photogrammetric 3-D shape reconstructed from nearly 900 Mars Express/SRC and Viking images',rep='BODY_REPRESENTATIVE',product=pshape)
Q('R_PHOBOS_STICKNEY','PHOBOS','STICKNEY_CRATER','REAL_EVIDENCE','REGION','MEX_HRSC_PDS','DETECTION',text='large impact crater dominating one hemisphere',rep='REGION_REPRESENTATIVE',region=stick)
Q('R_PHOBOS_GROOVES','PHOBOS','GROOVE_NETWORK','REAL_EVIDENCE','REGION','PHOBOS_GROOVES','DETECTION',text='multiple families of parallel grooves mapped over Phobos',rep='REGION_REPRESENTATIVE',region=pglob)
Q('R_PHOBOS_GROOVE_ORIGIN','PHOBOS','GROOVE_ORIGIN','MODEL_INFERENCE','MODEL_DOMAIN','PHOBOS_GROOVES','MODEL',text='2011 morphology/geography study favors chains of secondary impacts from Mars over six tested alternatives',rep='MODEL_DOMAIN_ONLY',notes='origin interpretation, not morphology measurement')
Q('R_PHOBOS_SPECTRAL','PHOBOS','SPECTRAL_COMPOSITION_CONSTRAINT','REAL_EVIDENCE','REGION','PHOBOS_REVIEW_2024','TEXT',text='low-albedo red/blue spectral units and primitive/carbonaceous spectral analogues; detailed mineral composition remains unresolved',rep='REGION_REPRESENTATIVE',region=pglob)
Q('R_PHOBOS_ORIGIN','PHOBOS','ORIGIN_HYPOTHESES','MODEL_INFERENCE','MODEL_DOMAIN','PHOBOS_REVIEW_2024','MODEL',text='capture and impact/co-accretion families remain model hypotheses; identity remains natural satellite of Mars',rep='MODEL_DOMAIN_ONLY')
Q('R_PHOBOS_IMAGERY','PHOBOS','GLOBAL_IMAGERY_SUPPORT','REAL_EVIDENCE','REGION','MEX_HRSC_PDS','SPATIAL_PRODUCT',text='Mars Express HRSC/SRC imaging provides meter-to-tens-of-meters morphology in covered regions',rep='REGION_REPRESENTATIVE',region=pglob,product=pimg)
# Deimos, deliberately sparse
Q('R_DEIMOS_IMAGERY','DEIMOS','GLOBAL_IMAGERY_SUPPORT','REAL_EVIDENCE','REGION','DEIMOS_SHAPE','SPATIAL_PRODUCT',text='Viking image mosaic provides global morphology at limited resolution',rep='REGION_REPRESENTATIVE',region=dglob,product=dimg)
Q('R_DEIMOS_SURFACE','DEIMOS','SURFACE_MORPHOLOGY','REAL_EVIDENCE','REGION','DEIMOS_SHAPE','TEXT',text='cratered, regolith-mantled surface with smoother appearance than Phobos at available imaging resolution',rep='REGION_REPRESENTATIVE',region=dglob)
Q('R_DEIMOS_SPECTRAL','DEIMOS','SPECTRAL_COMPOSITION_CONSTRAINT','REAL_EVIDENCE','REGION','DEIMOS_SPECTRA','TEXT',text='dark red spectral character broadly primitive/carbonaceous-like; mineralogical uniqueness and bulk composition remain unresolved',rep='REGION_REPRESENTATIVE',region=dglob)
Q('R_DEIMOS_ORIGIN','DEIMOS','ORIGIN_HYPOTHESES','MODEL_INFERENCE','MODEL_DOMAIN','DEIMOS_SPECTRA','MODEL',text='spectral similarity does not decide captured-asteroid versus Mars-system formation hypotheses',rep='MODEL_DOMAIN_ONLY')
Q('R_DEIMOS_INTERIOR','DEIMOS','INTERIOR_STRUCTURE','REAL_EVIDENCE','MODEL_DOMAIN','DEIMOS_SPECTRA','UNKNOWN',rep='MODEL_DOMAIN_ONLY',notes='No direct interior measurement admitted; low density alone is insufficient to assert rubble-pile structure')
# Ceres HCQ transfer/enrichment
Q('R_CERES_SPC','CERES','GLOBAL_SHAPE_MODEL','MODEL_INFERENCE','BODY','CERES_HCQ_SHAPE','SPATIAL_PRODUCT',text='PDS SPC global shape/topography model; ~100 m delivery family',rep='BODY_REPRESENTATIVE',product=cshape)
Q('R_CERES_GRAV70','CERES','GLOBAL_GRAVITY_FIELD','MODEL_INFERENCE','MODEL_DOMAIN','CERES_HCQ_GRAV','SPATIAL_PRODUCT',text='CERES70E spherical harmonic gravity field degree/order 70',rep='MODEL_DOMAIN_ONLY',product=cgrav)
Q('R_CERES_HAMO','CERES','GLOBAL_TOPOGRAPHY','REAL_EVIDENCE','BODY','CERES_HCQ_DTM','SPATIAL_PRODUCT',text='HAMO stereo-photogrammetric DTM ~136.7 m/pixel, approximately 98% coverage, ~10 m vertical accuracy',rep='BODY_REPRESENTATIVE',product=cdtm)
Q('R_CERES_VIR','CERES','GLOBAL_MINERALOGY_MAP','REAL_EVIDENCE','BODY','CERES_HCQ_VIR','SPATIAL_PRODUCT',text='Dawn VIR global and localized spectral composition mapping',rep='BODY_REPRESENTATIVE',product=cvir)
Q('R_CERES_AHUNA','CERES','AHUNA_CRYOVOLCANIC_DOME_INTERPRETATION','MODEL_INFERENCE','REGION','CERES_HCQ_VIR','MODEL',text='Ahuna Mons interpreted as a geologically young cryovolcanic/extrusive construct',rep='REGION_REPRESENTATIVE',region=ah)
Q('R_CERES_PSR','CERES','POLAR_COLD_TRAP_MODEL','MODEL_INFERENCE','MODEL_DOMAIN','CERES_HCQ_PSR','SPATIAL_PRODUCT',text='modeled northern polar permanently shadowed regions; modeled area is not measured ice extent',rep='MODEL_DOMAIN_ONLY',region=psr,product=cpsr)
Q('R_CERES_REGDTM','CERES','REGIONAL_HIGH_RESOLUTION_TOPOGRAPHY','REAL_EVIDENCE','REGION','CERES_HCQ_DTM','SPATIAL_PRODUCT',text='regional LAMO DTM catalogue includes Occator, Ahuna, Ernutet and other regions',rep='REGION_REPRESENTATIVE',region=dtmr,product=creg)
Q('R_CERES_OCCATOR_CRYO','CERES','OCCATOR_CRYOVOLCANIC_ACTIVITY_INTERPRETATION','MODEL_INFERENCE','REGION','CERES_HCQ_OCCATOR','MODEL',text='high-resolution morphology and faculae evolution interpreted as long-lasting/recent cryovolcanic activity with competing brine-source models',rep='REGION_REPRESENTATIVE',region=occ)
Q('R_CERES_INTERIOR_HCQ','CERES','PARTIALLY_DIFFERENTIATED_INTERIOR','MODEL_INFERENCE','MODEL_DOMAIN','CERES_HCQ_INTERIOR','MODEL',text='gravity and shape support a partially differentiated interior; layer composition remains model-dependent',rep='MODEL_DOMAIN_ONLY')
Q('R_CERES_ERNUTET','CERES','LOCALIZED_ALIPHATIC_ORGANICS','REAL_EVIDENCE','REGION','CERES_HCQ_VIR','DETECTION',text='3.4 micrometre spectral feature characteristic of aliphatic organic material concentrated near Ernutet',rep='REGION_REPRESENTATIVE',region=er,notes='localized detection, not global organic abundance')
Q('R_CERES_EXPOSED_ICE','CERES','EXPOSED_WATER_ICE_CRATERS','REAL_EVIDENCE','REGION','CERES_ICE_2019','DETECTION',text='water-ice exposures spectroscopically detected in multiple fresh craters, preferentially at higher latitudes',rep='REGION_REPRESENTATIVE',region=reg['CERES_HIGH_LAT'],notes='exposures do not define global subsurface ice inventory')
# coverage
grades={'PHOBOS':['STRONG','STRONG','MODERATE','MODERATE','UNKNOWN','MODERATE','STRONG','WEAK','NOT_APPLICABLE','WEAK'],'DEIMOS':['STRONG','MODERATE','WEAK','WEAK','UNKNOWN','WEAK','MODERATE','UNKNOWN','NOT_APPLICABLE','UNKNOWN']}
for b in grades:
 for dom,st in zip(domains,grades[b]):
  db.execute('insert or ignore into coverage(body_id,domain,property_or_class,state,origin,reason) values(?,?,?,?,?,?)',(b,dom,'DOMAIN_COVERAGE','SUPPORTED' if st not in ('UNKNOWN','NOT_APPLICABLE') else st,'NEW_CHATGPT_RESEARCH','Strength='+st))
# explicit satellite hierarchy assertion guard is body.parent_body_id; no origin hypothesis changes identity.
