SS=SM_SOURCE_IDS
def SR(b,k,n,t,notes=None): return db.execute('insert into region(body_id,region_key,region_name,region_type,notes) values(?,?,?,?,?)',(b,k,n,t,notes)).lastrowid
def SP(b,r,k,t,title,src,scope='REGION',frame=None): return db.execute('insert into spatial_product(body_id,region_id,product_key,product_type,title,coordinate_frame,source_id,scope,status) values(?,?,?,?,?,?,?,?,?)',(b,r,k,t,title,frame,SS[src],scope,'CANDIDATE')).lastrowid
def SO(b,r,k,method,scope,src,start=None,end=None,prod=None,notes=None,vtype=None,vmin=None,vmax=None,vunit=None,vdatum=None):
 return db.execute('''insert into observation(body_id,region_id,spatial_product_id,observation_key,measurement_method,scope,observation_time_start,observation_time_end,vertical_coordinate_type,vertical_min,vertical_max,vertical_unit,vertical_datum,source_id,notes) values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',(b,r,prod,k,method,scope,start,end,vtype,vmin,vmax,vunit,vdatum,SS[src],notes)).lastrowid
def SA(key,b,prop,ont,scope,src,kind='TEXT',num=None,text=None,unit=None,rep='UNKNOWN',region=None,obs=None,prod=None,start=None,end=None,notes=None,vtype=None,vmin=None,vmax=None,vunit=None,vdatum=None):
 db.execute('''insert into scientific_assertion(assertion_key,body_id,property_code,ontology,scope,region_id,observation_id,spatial_product_id,value_kind,value_numeric,value_text,unit,vertical_coordinate_type,vertical_min,vertical_max,vertical_unit,vertical_datum,epistemic_class,representativeness,valid_time_start,valid_time_end,source_id,admission_status,preferred,origin,notes) values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',(key,b,prop,ont,scope,region,obs,prod,kind,num,text,unit,vtype,vmin,vmax,vunit,vdatum,'MEASURED' if ont=='REAL_EVIDENCE' else ('DERIVED' if ont=='DERIVED' else 'MODEL_INFERENCE'),rep,start,end,SS[src],'CANDIDATE',0,'NEW_CHATGPT_RESEARCH',notes))
R={}
for x in [
('MIMAS','MIM_GLOBAL','Mimas global surface','REGION'),('MIMAS','HERSCHEL','Herschel crater','IMPACT_STRUCTURE'),
('ENCELADUS','ENC_GLOBAL','Enceladus global surface','REGION'),('ENCELADUS','ENC_SPT','South polar terrain','POLAR_TERRAIN'),('ENCELADUS','TIGER','Tiger stripe fractures','FRACTURE_SYSTEM'),
('TETHYS','TET_GLOBAL','Tethys global surface','REGION'),('TETHYS','ODYSSEUS','Odysseus crater','IMPACT_STRUCTURE'),('TETHYS','ITHACA','Ithaca Chasma','CHASMA'),
('DIONE','DIO_GLOBAL','Dione global surface','REGION'),('DIONE','DIO_WISPY','Wispy terrain / fracture systems','TECTONIC_TERRAIN'),
('RHEA','RHE_GLOBAL','Rhea global surface','REGION'),
('TITAN','TIT_GLOBAL','Titan global surface','REGION'),('TITAN','TIT_NORTH','Titan north polar lake district','POLAR_REGION'),('TITAN','KRAKEN','Kraken Mare','SEA'),('TITAN','LIGEIA','Ligeia Mare','SEA'),('TITAN','PUNGA','Punga Mare','SEA'),('TITAN','TIT_DUNES','Equatorial dune fields','DUNE_TERRAIN'),('TITAN','HUYGENS','Huygens landing region','LANDING_REGION'),
('IAPETUS','IAP_LEAD','Leading hemisphere / Cassini Regio','HEMISPHERE'),('IAPETUS','IAP_TRAIL','Bright trailing hemisphere','HEMISPHERE'),('IAPETUS','IAP_RIDGE','Equatorial ridge','RIDGE')]:
 R[(x[0],x[1])]=SR(*x)
P={}
for x in [
('MIMAS','MIM_GLOBAL','MIM_CASSINI','GLOBAL_IMAGERY','Cassini global Mimas imaging/topography','MIM_LIB'),
('ENCELADUS','ENC_SPT','ENC_SPT_MAP','THERMAL_GEOLOGY','Cassini south-polar fracture/thermal/plume mapping','ENC_GEO'),
('TETHYS','TET_GLOBAL','TETH_CASSINI','GLOBAL_IMAGERY','Cassini Tethys geology/imaging','TETH_GEO'),
('DIONE','DIO_GLOBAL','DIONE_CASSINI','GLOBAL_IMAGERY','Cassini Dione geology/imaging','DIO_GEO'),
('RHEA','RHE_GLOBAL','RHEA_CASSINI','GLOBAL_IMAGERY','Cassini Rhea geology/imaging','RHEA_GEO'),
('TITAN','TIT_GLOBAL','TIT_RADAR_GLOBAL','RADAR_MAPPING','Cassini SAR/radiometry Titan surface mapping','TIT_SEAS'),
('TITAN','TIT_NORTH','TIT_NORTH_SEAS','RADAR_MAPPING','Cassini radar northern lakes and seas','TIT_SEAS'),
('TITAN','TIT_DUNES','TIT_DUNE_RADAR','RADAR_MAPPING','Cassini RADAR equatorial dune fields','TIT_DUNES'),
('IAPETUS','IAP_LEAD','IAP_CASSINI_REGIO','REGIONAL_IMAGERY','Cassini imaging of Cassini Regio and equatorial ridge','IAP_IMG'),
('IAPETUS','IAP_LEAD','IAP_MICROWAVE','THERMAL_MAP','Microwave leading/trailing hemisphere measurements','IAP_MICRO')]:
 P[x[2]]=SP(x[0],R[(x[0],x[1])],x[2],x[3],x[4],x[5],'REGION','IAU_'+x[0])
# observations
mimlib=SO('MIMAS',None,'MIMAS_CASSINI_LIB','CASSINI_ISS_LIBRATION','BODY','MIM_LIB','2004','2017',notes='Measured physical libration; interior/ocean interpretation separate')
encpl=SO('ENCELADUS',R[('ENCELADUS','TIGER')],'ENC_CASSINI_PLUME','CASSINI_INMS_CDA_IMAGING','REGION','ENC_GEO','2005','2015',prod=P['ENC_SPT_MAP'],notes='Repeated plume/jet observations tied to south-polar fractures; variability retained')
ench2=SO('ENCELADUS',R[('ENCELADUS','ENC_SPT')],'ENC_H2_OBS','CASSINI_INMS','FOOTPRINT','ENC_H2','2015-10-28','2015-10-28',notes='INMS plume flythrough composition; not bulk-ocean direct measurement')
rheaexo=SO('RHEA',None,'RHEA_EXO_OBS','CASSINI_INMS','FOOTPRINT','RHEA_EXO','2010','2010',notes='Flyby exosphere detection; epoch/footprint limited')
titatm=SO('TITAN',None,'TITAN_HUYGENS_HASI','HUYGENS_HASI_DESCENT','FOOTPRINT','TIT_HASI','2005-01-14','2005-01-14',notes='Vertical atmospheric profile during descent',vtype='ALTITUDE',vmin=0,vmax=1400,vunit='km',vdatum='TITAN_REFERENCE_SURFACE')
titgc=SO('TITAN',R[('TITAN','HUYGENS')],'TITAN_HUYGENS_GCMS','HUYGENS_GCMS_DESCENT_SURFACE','LOCAL_SITE','TIT_GCMS','2005-01-14','2005-01-14',notes='Descent and landing-site chemistry; local site not global',vtype='ALTITUDE',vmin=0,vmax=146,vunit='km',vdatum='TITAN_REFERENCE_SURFACE')
titsea=SO('TITAN',R[('TITAN','TIT_NORTH')],'TITAN_CASSINI_SEAS','CASSINI_RADAR','REGION','TIT_SEAS','2006','2017',prod=P['TIT_NORTH_SEAS'],notes='Epoch-bounded radar geometry of northern lake/sea systems')
iapobs=SO('IAPETUS',R[('IAPETUS','IAP_LEAD')],'IAPETUS_CASSINI_DICHOTOMY','CASSINI_ISS_VIMS','REGION','IAP_DICH','2004','2007',prod=P['IAP_CASSINI_REGIO'],notes='Regional leading/trailing asymmetry; not homogeneous body composition')
# Mimas
SA('R_MIM_CRATER','MIMAS','CRATERED_SURFACE_HERSCHEL','REAL_EVIDENCE','REGION','MIM_LIB','DETECTION',text='heavily cratered ice-rich surface dominated by Herschel basin',rep='REGION_REPRESENTATIVE',region=R[('MIMAS','HERSCHEL')],prod=P['MIM_CASSINI'])
SA('R_MIM_LIB','MIMAS','PHYSICAL_LIBRATION','REAL_EVIDENCE','BODY','MIM_LIB','DETECTION',text='Cassini imaging measures forced physical libration larger than a simple homogeneous frozen-body prediction',rep='BODY_REPRESENTATIVE',obs=mimlib)
SA('R_MIM_OCEAN','MIMAS','SUBSURFACE_OCEAN_MODEL','MODEL_INFERENCE','MODEL_DOMAIN','MIM_OCEAN','MODEL',text='combined libration and orbital-precession modeling favors a geologically young ocean beneath an ice shell, but remains an interior inference rather than direct liquid detection',rep='MODEL_DOMAIN_ONLY')
SA('R_MIM_ALT','MIMAS','NON_OCEAN_INTERIOR_ALTERNATIVES','MODEL_INFERENCE','MODEL_DOMAIN','MIM_LIB','MODEL',text='elongated/heterogeneous solid-core and alternative interior explanations form part of the historical admissible model family and constrain interpretation of libration',rep='MODEL_DOMAIN_ONLY')
SA('R_MIM_THERM','MIMAS','SURFACE_THERMAL_HETEROGENEITY','REAL_EVIDENCE','REGION','MIM_THERM','DETECTION',text='Cassini thermal observations show spatially heterogeneous surface temperatures/thermal inertia including the Pac-Man anomaly',rep='REGION_REPRESENTATIVE',region=R[('MIMAS','MIM_GLOBAL')])
# Enceladus
SA('R_ENC_SPT','ENCELADUS','ACTIVE_SOUTH_POLAR_TERRAIN','REAL_EVIDENCE','REGION','ENC_GEO','DETECTION',text='south polar terrain contains tiger-stripe fractures, anomalous heat, tectonic resurfacing and active jets',rep='REGION_REPRESENTATIVE',region=R[('ENCELADUS','ENC_SPT')],prod=P['ENC_SPT_MAP'])
SA('R_ENC_PLUME','ENCELADUS','PLUME_ACTIVITY','REAL_EVIDENCE','REGION','ENC_GEO','DETECTION',text='repeated Cassini observations directly detect water-rich plume/ice-grain jets sourced from south-polar fractures with temporal variability',rep='REGION_REPRESENTATIVE',region=R[('ENCELADUS','TIGER')],obs=encpl,start='2005',end='2015')
for key,prop,src,txt in [
('R_ENC_SALT','PLUME_SALTS','ENC_SALT','sodium salts detected in plume/E-ring ice grains'),
('R_ENC_SILICA','PLUME_SILICA','ENC_SILICA','nanometer silica particles detected in Saturn E-ring material linked to Enceladus'),
('R_ENC_H2','PLUME_HYDROGEN','ENC_H2','molecular hydrogen measured by INMS during plume flythrough'),
('R_ENC_P','PLUME_PHOSPHATE','ENC_P','phosphates identified in Enceladus-derived ice grains'),
('R_ENC_ORG','PLUME_ORGANICS','ENC_ORG','complex/macromolecular organic material detected in Enceladus-derived ice grains')]:
 SA(key,'ENCELADUS',prop,'REAL_EVIDENCE','FOOTPRINT',src,'DETECTION',text=txt+'; detection does not equal bulk-ocean abundance',rep='FOOTPRINT_ONLY',obs=ench2 if key=='R_ENC_H2' else encpl)
SA('R_ENC_OCEAN','ENCELADUS','GLOBAL_SUBSURFACE_OCEAN_MODEL','MODEL_INFERENCE','MODEL_DOMAIN','ENC_OCEAN','MODEL',text='libration, gravity, geology and plume evidence support a global subsurface liquid-water ocean model; depth/thickness/salinity remain inferred',rep='MODEL_DOMAIN_ONLY')
SA('R_ENC_HYDRO','ENCELADUS','HYDROTHERMAL_ACTIVITY_INTERPRETATION','MODEL_INFERENCE','MODEL_DOMAIN','ENC_SILICA','MODEL',text='silica particle properties and H2/plume geochemistry support water-rock interaction and hydrothermal interpretations; hydrothermal system geometry is not observed',rep='MODEL_DOMAIN_ONLY')
SA('R_ENC_CHEM','ENCELADUS','OCEAN_CHEMISTRY_FROM_PLUME_MODEL','MODEL_INFERENCE','MODEL_DOMAIN','ENC_P','MODEL',text='plume grains constrain possible ocean chemistry through transport/geochemical models; plume concentration is not silently copied to bulk ocean composition',rep='MODEL_DOMAIN_ONLY')
# Tethys
SA('R_TET_GEO','TETHYS','SURFACE_GEOLOGY','REAL_EVIDENCE','REGION','TETH_GEO','DETECTION',text='heavily cratered icy terrain includes Odysseus basin, Ithaca Chasma and smoother plains units',rep='REGION_REPRESENTATIVE',region=R[('TETHYS','TET_GLOBAL')],prod=P['TETH_CASSINI'])
SA('R_TET_ICE','TETHYS','ICE_RICH_SURFACE','REAL_EVIDENCE','BODY','TETH_GEO','DETECTION',text='low density and spectroscopy support an ice-rich body/surface with spatially varying regolith properties',rep='BODY_REPRESENTATIVE')
SA('R_TET_EVOL','TETHYS','THERMAL_TIDAL_EVOLUTION_MODELS','MODEL_INFERENCE','MODEL_DOMAIN','TETH_GEO','MODEL',text='tectonic history and orbital evolution constrain past thermal/tidal scenarios; no present ocean is asserted',rep='MODEL_DOMAIN_ONLY')
# Dione
SA('R_DIO_GEO','DIONE','SURFACE_GEOLOGY','REAL_EVIDENCE','REGION','DIO_GEO','DETECTION',text='cratered terrain and bright wispy tectonic fracture networks record extension and resurfacing history',rep='REGION_REPRESENTATIVE',region=R[('DIONE','DIO_WISPY')],prod=P['DIONE_CASSINI'])
SA('R_DIO_OCEAN','DIONE','SUBSURFACE_OCEAN_MODEL','MODEL_INFERENCE','MODEL_DOMAIN','DIO_OCEAN','MODEL',text='gravity/topography and interior modeling admit a present subsurface ocean beneath an ice shell; evidence is indirect and competing models remain',rep='MODEL_DOMAIN_ONLY')
SA('R_DIO_ACTIVITY','DIONE','PRESENT_ACTIVITY_STATUS','DERIVED','BODY','DIO_GEO','TEXT',text='tectonic geology demonstrates past activity, while evidence for current endogenic activity is limited/uncertain',rep='BODY_REPRESENTATIVE')
# Rhea
SA('R_RHE_GEO','RHEA','SURFACE_GEOLOGY','REAL_EVIDENCE','REGION','RHEA_GEO','DETECTION',text='ancient cratered terrain with tectonic fractures and regional resurfacing relationships',rep='REGION_REPRESENTATIVE',region=R[('RHEA','RHE_GLOBAL')],prod=P['RHEA_CASSINI'])
SA('R_RHE_EXO','RHEA','O2_CO2_EXOSPHERE','REAL_EVIDENCE','FOOTPRINT','RHEA_EXO','DETECTION',text='Cassini detected tenuous oxygen and carbon-dioxide exosphere during flyby; not a timeless uniform atmosphere',rep='FOOTPRINT_ONLY',obs=rheaexo,start='2010',end='2010')
SA('R_RHE_INTERIOR','RHEA','INTERIOR_DIFFERENTIATION_MODELS','MODEL_INFERENCE','MODEL_DOMAIN','RHEA_GEO','MODEL',text='density/gravity/thermal evolution constrain ice-rock interior and degree of differentiation; present internal activity remains weakly constrained',rep='MODEL_DOMAIN_ONLY')
# Titan
SA('R_TIT_ATM_PROFILE','TITAN','ATMOSPHERIC_PRESSURE_TEMPERATURE_PROFILE','REAL_EVIDENCE','FOOTPRINT','TIT_HASI','DETECTION',text='Huygens directly measured pressure, temperature and density through the atmosphere during descent; profile is epoch/trajectory specific',rep='FOOTPRINT_ONLY',obs=titatm,start='2005-01-14',end='2005-01-14',vtype='ALTITUDE',vmin=0,vmax=1400,vunit='km',vdatum='TITAN_REFERENCE_SURFACE')
SA('R_TIT_ATM_COMP','TITAN','ATMOSPHERIC_COMPOSITION_PROFILE','REAL_EVIDENCE','FOOTPRINT','TIT_GCMS','DETECTION',text='Huygens GCMS measured nitrogen-dominated atmosphere with methane and trace constituents along descent; composition varies vertically',rep='FOOTPRINT_ONLY',obs=titgc,start='2005-01-14',end='2005-01-14',vtype='ALTITUDE',vmin=0,vmax=146,vunit='km',vdatum='TITAN_REFERENCE_SURFACE')
SA('R_TIT_HAZE','TITAN','ATMOSPHERIC_HAZE_CHEMISTRY','REAL_EVIDENCE','BODY','TIT_GCMS','DETECTION',text='photochemical haze/aerosols and complex organic chemistry are empirically established atmospheric components; detailed production pathways remain modeled',rep='BODY_REPRESENTATIVE')
SA('R_TIT_HYDRO','TITAN','METHANE_HYDROLOGICAL_CYCLE','DERIVED','BODY','TIT_HYDRO','TEXT',text='clouds, rainfall evidence, channels, evaporation, lakes/seas and seasonal atmospheric methane together establish an active methane hydrological cycle with strong spatial/temporal variability',rep='BODY_REPRESENTATIVE')
SA('R_TIT_SEAS','TITAN','POLAR_LAKES_SEAS','REAL_EVIDENCE','REGION','TIT_SEAS','DETECTION',text='Cassini radar maps stable and changing liquid-hydrocarbon lakes/seas concentrated at high latitudes; measured geometry does not imply global inventory',rep='REGION_REPRESENTATIVE',region=R[('TITAN','TIT_NORTH')],obs=titsea,prod=P['TIT_NORTH_SEAS'],start='2006',end='2017')
SA('R_TIT_KRAKEN','TITAN','KRAKEN_MARE','REAL_EVIDENCE','REGION','TIT_SEAS','DETECTION',text='Kraken Mare is a spatially resolved northern hydrocarbon sea',rep='REGION_REPRESENTATIVE',region=R[('TITAN','KRAKEN')],obs=titsea)
SA('R_TIT_LIGEIA','TITAN','LIGEIA_MARE','REAL_EVIDENCE','REGION','TIT_SEAS','DETECTION',text='Ligeia Mare is a spatially resolved northern hydrocarbon sea',rep='REGION_REPRESENTATIVE',region=R[('TITAN','LIGEIA')],obs=titsea)
SA('R_TIT_PUNGA','TITAN','PUNGA_MARE','REAL_EVIDENCE','REGION','TIT_SEAS','DETECTION',text='Punga Mare is a spatially resolved northern hydrocarbon sea',rep='REGION_REPRESENTATIVE',region=R[('TITAN','PUNGA')],obs=titsea)
SA('R_TIT_DUNES','TITAN','EQUATORIAL_DUNES','REAL_EVIDENCE','REGION','TIT_DUNES','DETECTION',text='Cassini radar maps extensive equatorial longitudinal dunes formed from mobile organic-rich sediment',rep='REGION_REPRESENTATIVE',region=R[('TITAN','TIT_DUNES')],prod=P['TIT_DUNE_RADAR'])
SA('R_TIT_HUY_SITE','TITAN','HUYGENS_LANDING_SITE_SURFACE','REAL_EVIDENCE','LOCAL_SITE','TIT_GCMS','DETECTION',text='Huygens directly sampled/imaged a locally damp, rounded-pebble/organic-bearing landing environment; properties are SITE_ONLY',rep='SITE_ONLY',region=R[('TITAN','HUYGENS')],obs=titgc)
SA('R_TIT_OCEAN','TITAN','SUBSURFACE_OCEAN_MODEL','MODEL_INFERENCE','MODEL_DOMAIN','TIT_OCEAN','MODEL',text='gravity/tidal/rotational constraints support families with an internal liquid-water-rich ocean beneath an ice shell; ocean properties and high-pressure ice architecture are model-dependent',rep='MODEL_DOMAIN_ONLY')
SA('R_TIT_INTERIOR','TITAN','DIFFERENTIATED_INTERIOR_MODEL_FAMILY','MODEL_INFERENCE','MODEL_DOMAIN','TIT_OCEAN','MODEL',text='rocky core, ice shell, ocean and possible high-pressure ice layers admit multiple interior realizations consistent with geodesy',rep='MODEL_DOMAIN_ONLY')
# Iapetus
SA('R_IAP_DARK','IAPETUS','LEADING_HEMISPHERE_DARK_MATERIAL','REAL_EVIDENCE','REGION','IAP_IMG','DETECTION',text='Cassini Regio is a low-albedo, water-ice-poor leading-hemisphere terrain with compositional and thermal properties distinct from bright terrain',rep='REGION_REPRESENTATIVE',region=R[('IAPETUS','IAP_LEAD')],obs=iapobs,prod=P['IAP_CASSINI_REGIO'])
SA('R_IAP_BRIGHT','IAPETUS','TRAILING_HEMISPHERE_BRIGHT_ICE','REAL_EVIDENCE','REGION','IAP_DICH','DETECTION',text='trailing hemisphere and poles are substantially brighter and water-ice-rich relative to Cassini Regio',rep='REGION_REPRESENTATIVE',region=R[('IAPETUS','IAP_TRAIL')])
SA('R_IAP_RIDGE','IAPETUS','EQUATORIAL_RIDGE','REAL_EVIDENCE','REGION','IAP_IMG','DETECTION',text='ancient equatorial ridge system reaches extreme relief and crosses Cassini Regio',rep='REGION_REPRESENTATIVE',region=R[('IAPETUS','IAP_RIDGE')])
SA('R_IAP_MIG','IAPETUS','THERMAL_ICE_MIGRATION_MODEL','MODEL_INFERENCE','MODEL_DOMAIN','IAP_DICH','MODEL',text='exogenic dark dust deposition plus thermal feedback and water-ice migration explains much of hemispheric dichotomy; detailed source/thickness remain constrained but not uniquely fixed',rep='MODEL_DOMAIN_ONLY')
SA('R_IAP_MICRO','IAPETUS','HEMISPHERIC_SUBSURFACE_THERMAL_CONTRAST','REAL_EVIDENCE','REGION','IAP_MICRO','DETECTION',text='microwave observations resolve leading/trailing differences in emissivity/subsurface structure, reinforcing nonhomogeneous regional conditioning',rep='REGION_REPRESENTATIVE',region=R[('IAPETUS','IAP_LEAD')],prod=P['IAP_MICROWAVE'])
