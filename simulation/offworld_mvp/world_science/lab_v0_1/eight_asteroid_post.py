ES=EA_SOURCE_IDS
def ER(b,k,n,t,notes=None): return db.execute('insert into region(body_id,region_key,region_name,region_type,notes) values(?,?,?,?,?)',(b,k,n,t,notes)).lastrowid
def EP(b,r,k,t,title,src,scope='REGION',res=None,unit=None,frame=None): return db.execute('insert into spatial_product(body_id,region_id,product_key,product_type,title,horizontal_resolution_value,horizontal_resolution_unit,coordinate_frame,source_id,scope,status) values(?,?,?,?,?,?,?,?,?,?,?)',(b,r,k,t,title,res,unit,frame,ES[src],scope,'CANDIDATE')).lastrowid
def EA(key,b,prop,ont,scope,src,kind='TEXT',num=None,text=None,unit=None,rep='UNKNOWN',region=None,sample=None,prod=None,start=None,end=None,notes=None):
 db.execute('''insert into scientific_assertion(assertion_key,body_id,property_code,ontology,scope,region_id,sample_id,spatial_product_id,value_kind,value_numeric,value_text,unit,epistemic_class,representativeness,valid_time_start,valid_time_end,source_id,admission_status,preferred,origin,notes) values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',(key,b,prop,ont,scope,region,sample,prod,kind,num,text,unit,'MEASURED' if ont=='REAL_EVIDENCE' else 'MODEL_INFERENCE',rep,start,end,ES[src],'CANDIDATE',0,'NEW_CHATGPT_RESEARCH',notes))
# regions
rg={}
for b,k,n,t in [
('PSYCHE','PSYCHE_GLOBAL','Psyche remotely observed surface','REGION'),
('RYUGU','RYUGU_GLOBAL','Ryugu global mapped surface','REGION'),('RYUGU','TD1','Hayabusa2 touchdown 1','SAMPLE_SITE'),('RYUGU','TD2','Hayabusa2 touchdown 2','SAMPLE_SITE'),
('ITOKAWA','ITOKAWA_GLOBAL','Itokawa global mapped surface','REGION'),('ITOKAWA','MUSES_SEA','Muses Sea','SAMPLE_SITE'),
('EROS','EROS_GLOBAL','Eros global mapped surface','REGION'),('EROS','EROS_LANDING','NEAR Shoemaker landing locality','LOCAL_SITE'),
('LUTETIA','LUTETIA_FLYBY','Rosetta-observed Lutetia hemisphere','FOOTPRINT'),
('STEINS','STEINS_FLYBY','Rosetta-observed Steins surface','FOOTPRINT'),
('MATHILDE','MATHILDE_FLYBY','NEAR-observed Mathilde hemisphere','FOOTPRINT'),
('IDA','IDA_FLYBY','Galileo-observed Ida surface','FOOTPRINT')]:
 rg[(b,k)]=ER(b,k,n,t)
# products
prod={}
for b,r,k,t,title,src,res,unit,frame in [
('PSYCHE','PSYCHE_GLOBAL','PSYCHE_PREARRIVAL_SHAPE','SHAPE_MODEL','Pre-arrival radar/occultation shape model','PSYCHE_SPICE',None,None,'IAU/mission Psyche frame'),
('RYUGU','RYUGU_GLOBAL','RYUGU_DSK','SHAPE_MODEL','Hayabusa2 SPC/SfM Ryugu digital shape kernels','RYUGU_SPICE',None,None,'Ryugu body-fixed'),
('ITOKAWA','ITOKAWA_GLOBAL','ITOKAWA_HAYABUSA_SHAPE','SHAPE_MODEL','Hayabusa Itokawa global shape and imaging products','ITOKAWA_SCIENCE',None,None,'Itokawa body-fixed'),
('EROS','EROS_GLOBAL','EROS_NEAR_GLOBAL','GLOBAL_MAPPING','NEAR Shoemaker global Eros imaging/topography products','NEAR_SPICE',None,None,'Eros body-fixed'),
('LUTETIA','LUTETIA_FLYBY','LUTETIA_ROSETTA_SHAPE','SHAPE_MODEL','Rosetta OSIRIS Lutetia shape/imaging products','LUTETIA_SCI',None,None,'Lutetia body-fixed'),
('STEINS','STEINS_FLYBY','STEINS_ROSETTA_SHAPE','SHAPE_MODEL','Rosetta OSIRIS Steins shape/imaging products','STEINS_SCI',None,None,'Steins body-fixed'),
('MATHILDE','MATHILDE_FLYBY','MATHILDE_NEAR_IMAGERY','IMAGERY','NEAR Mathilde flyby imaging/morphology products','MATHILDE_SCI',None,None,'image-derived'),
('IDA','IDA_FLYBY','IDA_GALILEO_MAP','IMAGERY_SPECTRAL_MAP','Galileo SSI/NIMS Ida imaging and spectral products','IDA_COMP',None,None,'Ida body-fixed')]:
 prod[b]=EP(b,rg[(b,r)],k,t,title,src,'REGION',res,unit,frame)
# samples with explicit collection epoch
ry1=db.execute('insert into sample(body_id,region_id,sample_key,sample_name,collection_site,collection_method,collection_time_start,collection_time_end,source_id,notes) values(?,?,?,?,?,?,?,?,?,?)',('RYUGU',rg[('RYUGU','TD1')],'RYUGU_TD1','Hayabusa2 TD1 returned material','TD1','touchdown sampler','2019-02-22','2019-02-22',ES['RYUGU_SAMPLE'],'Sample scope; no whole-body representativeness')).lastrowid
ry2=db.execute('insert into sample(body_id,region_id,sample_key,sample_name,collection_site,collection_method,collection_time_start,collection_time_end,source_id,notes) values(?,?,?,?,?,?,?,?,?,?)',('RYUGU',rg[('RYUGU','TD2')],'RYUGU_TD2','Hayabusa2 TD2 returned material','TD2','touchdown sampler after SCI experiment','2019-07-11','2019-07-11',ES['RYUGU_SAMPLE'],'Sample scope; subsurface-access experiment does not imply pristine global subsurface')).lastrowid
ito=db.execute('insert into sample(body_id,region_id,sample_key,sample_name,collection_site,collection_method,collection_time_start,collection_time_end,source_id,notes) values(?,?,?,?,?,?,?,?,?,?)',('ITOKAWA',rg[('ITOKAWA','MUSES_SEA')],'ITOKAWA_RETURN','Hayabusa returned Itokawa particles','Muses Sea','touchdown collection','2005-11-20','2005-11-26',ES['ITOKAWA_SAMPLE'],'Returned microscopic particles; sample-only evidence')).lastrowid
# Psyche
EA('R_PSY_METAL_MIX','PSYCHE','SURFACE_METAL_SILICATE_MIXTURE','MODEL_INFERENCE','MODEL_DOMAIN','PSYCHE_PREFLIGHT','MODEL',text='Radar, density and spectra favor mixed metal plus low-Fe silicate surface/bulk model families; pure exposed iron-core model is not established',rep='MODEL_DOMAIN_ONLY')
EA('R_PSY_POROSITY','PSYCHE','MACROPOROSITY_MODEL','MODEL_INFERENCE','MODEL_DOMAIN','PSYCHE_PREFLIGHT','RANGE',text='preflight composition-density models permit substantial but model-dependent porosity; not directly measured',rep='MODEL_DOMAIN_ONLY')
EA('R_PSY_HETERO','PSYCHE','SURFACE_HETEROGENEITY','REAL_EVIDENCE','REGION','PSYCHE_PREFLIGHT','DETECTION',text='radar reflectivity, thermal and spectral observations indicate heterogeneous surface properties',rep='REGION_REPRESENTATIVE',region=rg[('PSYCHE','PSYCHE_GLOBAL')],prod=prod['PSYCHE'])
EA('R_PSY_ORIGIN','PSYCHE','FORMATION_HYPOTHESES','MODEL_INFERENCE','MODEL_DOMAIN','PSYCHE_PREFLIGHT','MODEL',text='exposed-core, differentiated/reaccreted, ferrovolcanic and primitive metal-rich formation families remain competing hypotheses',rep='MODEL_DOMAIN_ONLY')
# Ryugu
EA('R_RYU_RUBBLE','RYUGU','RUBBLE_PILE_STRUCTURE','MODEL_INFERENCE','MODEL_DOMAIN','RYUGU_SHAPE','MODEL',text='low density, top shape and boulder-rich surface support a gravitational aggregate/rubble-pile interpretation',rep='MODEL_DOMAIN_ONLY')
EA('R_RYU_MORPH','RYUGU','BOULDER_RICH_SURFACE','REAL_EVIDENCE','REGION','RYUGU_SHAPE','DETECTION',text='Hayabusa2 mapped a boulder-rich, low-albedo surface with scarce fine smooth regolith',rep='REGION_REPRESENTATIVE',region=rg[('RYUGU','RYUGU_GLOBAL')],prod=prod['RYUGU'])
EA('R_RYU_SAMPLE1','RYUGU','CI_LIKE_SAMPLE_COMPOSITION','REAL_EVIDENCE','SAMPLE','RYUGU_SAMPLE','DETECTION',text='TD1 returned material is compositionally close to CI carbonaceous chondrites and contains hydrated phases and organics',rep='SAMPLE_ONLY',sample=ry1)
EA('R_RYU_SAMPLE2','RYUGU','CI_LIKE_SAMPLE_COMPOSITION','REAL_EVIDENCE','SAMPLE','RYUGU_SAMPLE','DETECTION',text='TD2 returned material is compositionally close to CI carbonaceous chondrites and contains hydrated phases and organics',rep='SAMPLE_ONLY',sample=ry2)
EA('R_RYU_GLOBAL_LIMIT','RYUGU','SAMPLE_REPRESENTATIVENESS_LIMIT','MODEL_INFERENCE','SAMPLE','RYUGU_SAMPLE','MODEL',text='agreement between samples and remote spectra supports broader relevance but does not establish uniform whole-body composition',rep='SAMPLE_ONLY',sample=ry1)
# Itokawa
EA('R_ITO_RUBBLE','ITOKAWA','RUBBLE_PILE_STRUCTURE','MODEL_INFERENCE','MODEL_DOMAIN','ITOKAWA_SCIENCE','MODEL',text='low bulk density relative to ordinary-chondrite grain density plus morphology support high-macroporosity rubble-pile structure',rep='MODEL_DOMAIN_ONLY')
EA('R_ITO_TERRAINS','ITOKAWA','ROUGH_SMOOTH_TERRAINS','REAL_EVIDENCE','REGION','ITOKAWA_SCIENCE','DETECTION',text='Hayabusa resolved rough boulder-rich terrain and smoother particle-rich gravitational lows including Muses Sea',rep='REGION_REPRESENTATIVE',region=rg[('ITOKAWA','ITOKAWA_GLOBAL')],prod=prod['ITOKAWA'])
EA('R_ITO_SAMPLE','ITOKAWA','ORDINARY_CHONDRITE_SAMPLE_LINK','REAL_EVIDENCE','SAMPLE','ITOKAWA_SAMPLE','DETECTION',text='returned particles directly link sampled Itokawa regolith to thermally metamorphosed LL ordinary chondrite material',rep='SAMPLE_ONLY',sample=ito)
EA('R_ITO_WEATHER','ITOKAWA','SPACE_WEATHERING_SAMPLE_EVIDENCE','REAL_EVIDENCE','SAMPLE','ITOKAWA_SAMPLE','DETECTION',text='returned grains preserve nanophase-iron-bearing space-weathering rims',rep='SAMPLE_ONLY',sample=ito)
# Eros
EA('R_EROS_GEO','EROS','REGOLITH_CRATER_POND_MORPHOLOGY','REAL_EVIDENCE','REGION','EROS_GEO','DETECTION',text='NEAR mapped craters, boulders, fractures and smooth pond-like regolith deposits across Eros',rep='REGION_REPRESENTATIVE',region=rg[('EROS','EROS_GLOBAL')],prod=prod['EROS'])
EA('R_EROS_COMP','EROS','ELEMENTAL_CHONDRITIC_AFFINITY','MODEL_INFERENCE','FOOTPRINT','EROS_COMP','MODEL',text='XRS elemental ratios are broadly compatible with ordinary-chondritic material, with calibration/footprint limitations',rep='FOOTPRINT_ONLY',region=rg[('EROS','EROS_GLOBAL')])
EA('R_EROS_LAND','EROS','LANDING_SITE_SURFACE','REAL_EVIDENCE','LOCAL_SITE','EROS_GEO','DETECTION',text='terminal descent/landing observations constrain local regolith and surface morphology only',rep='SITE_ONLY',region=rg[('EROS','EROS_LANDING')],start='2001-02-12',end='2001-02-12')
EA('R_EROS_INTERIOR','EROS','INTERIOR_STRUCTURE_CONSTRAINT','MODEL_INFERENCE','MODEL_DOMAIN','EROS_GEO','MODEL',text='bulk density and global structure constrain porosity/fracturing but do not uniquely determine monolithic versus fractured interior architecture',rep='MODEL_DOMAIN_ONLY')
# Lutetia
EA('R_LUT_GEO','LUTETIA','CRATERED_HETEROGENEOUS_TERRAIN','REAL_EVIDENCE','FOOTPRINT','LUTETIA_SCI','DETECTION',text='Rosetta resolved heavily cratered and morphologically diverse terrains on the observed hemisphere',rep='FOOTPRINT_ONLY',region=rg[('LUTETIA','LUTETIA_FLYBY')],prod=prod['LUTETIA'],start='2010-07-10',end='2010-07-10')
EA('R_LUT_AMBIG','LUTETIA','COMPOSITIONAL_AMBIGUITY','MODEL_INFERENCE','MODEL_DOMAIN','LUTETIA_SCI','MODEL',text='high density, moderate albedo and feature-poor spectra permit multiple compositional/taxonomic analogues; no unique bulk meteorite analogue is established',rep='MODEL_DOMAIN_ONLY')
EA('R_LUT_POR','LUTETIA','POROSITY_INTERIOR_MODEL','MODEL_INFERENCE','MODEL_DOMAIN','LUTETIA_SCI','MODEL',text='density and shape constrain but do not directly measure macroporosity or differentiation state',rep='MODEL_DOMAIN_ONLY')
# Steins
EA('R_STEINS_SHAPE','STEINS','DIAMOND_SHAPE_AND_CRATERS','REAL_EVIDENCE','FOOTPRINT','STEINS_SCI','DETECTION',text='Rosetta imaging shows diamond-like shape, large crater and crater-chain/surface morphology',rep='FOOTPRINT_ONLY',region=rg[('STEINS','STEINS_FLYBY')],prod=prod['STEINS'],start='2008-09-05',end='2008-09-05')
EA('R_STEINS_E','STEINS','E_TYPE_CLASSIFICATION','REAL_EVIDENCE','BODY','STEINS_SCI','CATEGORY',text='high albedo and spectral behavior support E-type classification',rep='BODY_REPRESENTATIVE')
EA('R_STEINS_ENS','STEINS','ENSTATITE_ANALOG_INTERPRETATION','MODEL_INFERENCE','MODEL_DOMAIN','STEINS_SCI','MODEL',text='E-type spectra motivate enstatite-rich analogues but do not measure exact bulk mineral abundance',rep='MODEL_DOMAIN_ONLY')
# Mathilde
EA('R_MAT_CRATERS','MATHILDE','GIANT_CRATER_MORPHOLOGY','REAL_EVIDENCE','FOOTPRINT','MATHILDE_SCI','DETECTION',text='NEAR imaging revealed several craters comparable to body radius surviving on an extremely dark body',rep='FOOTPRINT_ONLY',region=rg[('MATHILDE','MATHILDE_FLYBY')],prod=prod['MATHILDE'],start='1997-06-27',end='1997-06-27')
EA('R_MAT_POR','MATHILDE','HIGH_POROSITY_INFERENCE','MODEL_INFERENCE','MODEL_DOMAIN','MATHILDE_DENS','MODEL',text='very low bulk density relative to plausible carbonaceous grain densities implies large void fraction/macroporosity',rep='MODEL_DOMAIN_ONLY',notes='density plus assumed grain density, not direct porosity observation')
EA('R_MAT_STRUCT','MATHILDE','STRUCTURAL_SURVIVAL_MODELS','MODEL_INFERENCE','MODEL_DOMAIN','MATHILDE_SCI','MODEL',text='survival of giant craters constrains impact-energy dissipation/interior models but does not specify a unique rubble-pile geometry',rep='MODEL_DOMAIN_ONLY')
# Ida
EA('R_IDA_GEO','IDA','CRATERED_REGOLITH_GROOVE_MORPHOLOGY','REAL_EVIDENCE','FOOTPRINT','IDA_GEO','DETECTION',text='Galileo imaging shows saturated cratering, grooves, blocks, chutes, crater chains and substantial regolith',rep='FOOTPRINT_ONLY',region=rg[('IDA','IDA_FLYBY')],prod=prod['IDA'],start='1993-08-28',end='1993-08-28')
EA('R_IDA_COMP','IDA','S_TYPE_SILICATE_COMPOSITION','REAL_EVIDENCE','FOOTPRINT','IDA_COMP','DETECTION',text='Galileo SSI/NIMS spectra constrain silicate mineralogy and modest spectral-unit variation over observed surface',rep='FOOTPRINT_ONLY',region=rg[('IDA','IDA_FLYBY')],prod=prod['IDA'])
EA('R_IDA_OC','IDA','ORDINARY_CHONDRITE_AFFINITY','MODEL_INFERENCE','MODEL_DOMAIN','IDA_COMP','MODEL',text='spectral mineral ratios are consistent with ordinary-chondrite-like analogues; this is not a direct bulk assay',rep='MODEL_DOMAIN_ONLY')
EA('R_IDA_DACTYL','IDA','NATURAL_SATELLITE_RELATIONSHIP','REAL_EVIDENCE','BODY','IDA_DACTYL','DETECTION',text='Dactyl is a directly imaged natural satellite of Ida; its orbit constrains Ida mass/density',rep='BODY_REPRESENTATIVE')
