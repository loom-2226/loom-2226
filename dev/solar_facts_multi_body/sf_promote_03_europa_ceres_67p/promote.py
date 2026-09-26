"""Append a frozen ARP candidate to an already-qualified multi-body Solar Facts DB.

Only identity binding and explicit type/disposition adapters are inputs. All
candidate source assertions are retained byte-for-byte in the promotion ledger.
No science is inferred, selected, or strengthened here.
"""
from __future__ import annotations
import hashlib, importlib.util, json, os, shutil, sqlite3, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
BASE=ROOT/'dev/solar_facts_multi_body/sf_promote_02_ceres_67p/LOOM_SOLAR_FACTS_MULTI_BODY_SF_PROMOTE_02_CERES_67P.sqlite3'
CAMPAIGN=HERE/'inputs/ARP_QUAL_02_EUROPA_CAMPAIGN.json'
FROZEN=HERE/'inputs/ARP_QUAL_02_EUROPA_FROZEN_MANIFEST.json'
REPORT=HERE/'inputs/ARP_QUAL_02_EUROPA_QUALIFICATION.json'
OUT=HERE/'LOOM_SOLAR_FACTS_MULTI_BODY_SF_PROMOTE_03_EUROPA_CERES_67P.sqlite3'
EXPECTED_BASE_SHA='ed930b0453ec994712614bf0beb1a5ff8c93452db1b753884539fa510184b64f'
EXPECTED_67P='9e4139deb7182ce4c87176bc27e3510ffb075421e34cbca7bdb5a2a700ad9525'
EXPECTED_CERES='2c6ac5e1c6841122eb9b0b6ab27330eaf7f806b1ad9083e6b7c42860ee79e067'
EUROPA='EUROPA'
DISPOSITIONS={
 'eu-gm':('PROMOTE','Typed scalar GM in dynamical-inference class; units and uncertainty retained.'),
 'eu-radius':('PROMOTE','Typed mean-radius reference parameter; not a local figure or terrain model.'),
 'eu-orbit':('HOLD','Mean-element vector is retained in the ledger; no ephemeris or epoch-free orbit fact is asserted.'),
 'eu-rotation':('PROMOTE','NAIF BODY502 orientation coefficients map to the generic orientation-model table; coefficient units and model scope remain explicit.'),
 'eu-geology':('PROMOTE','USGS global geologic-map product is represented as a global model product; regional coverage limitation retained.'),
 'eu-surface-age':('SCHEMA_LIEN','Qualitative crater-age interpretation is retained in the ledger; no scalar global surface age is inserted.'),
 'eu-mag-field':('PROMOTE','Instrument-footprint Galileo magnetic measurement represented as a scoped observation.'),
 'eu-ocean-inference':('SCHEMA_LIEN','No existing typed property/epistemic structure distinguishes magnetic induction measurement from model-dependent conductive-layer/ocean interpretation; exact chain remains in ledger.'),
 'eu-plume-galileo-candidate':('PROMOTE','Candidate activity entry linked to E12 MAG/PWS observation; no permanent/global activity asserted.'),
 'eu-plume-hst-candidate':('PROMOTE','Candidate activity entry scoped to reported south-polar HST epoch.'),
 'eu-plume-hst-nondetect':('PROMOTE','HST nondetection retained as an observation; no absence inference.'),
 'eu-plume-sparks':('PROMOTE','HST multi-epoch candidate evidence retained as an instrument-footprint observation.'),
 'eu-plume-subaru':('PROMOTE','Subaru nondetection retained with observation-time/sensitivity limit.'),
 'eu-plume-alma-limit':('SCHEMA_LIEN','Species/model-dependent upper limits retained in full ledger; typed observation alone cannot represent conditional limits.'),
 'eu-oxygen-atmos':('SCHEMA_LIEN','Existing typed vocabulary cannot preserve atomic-oxygen emission separately from interpreted molecular-O2 exosphere without adding a semantic property; exact claim remains in ledger.'),
 'eu-nacl-surface':('PROMOTE','Regional material record permits unknown abundance and HST/STIS evidence; no global/ocean inventory is implied.'),
 'eu-juno-shell':('SCHEMA_LIEN','Competing model scope/assumptions plus 19–39 km interval remain in ledger; no global scalar or single winning shell model is inserted.')
}

def digest_module():
 d=ROOT/'dev/solar_facts_multi_body/sf_promote_02_ceres_67p'
 sys.path.insert(0,str(d));previous=sys.modules.pop('promote',None)
 try:
  spec=importlib.util.spec_from_file_location('_sf02_qualify',d/'qualify.py')
  m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
 finally:
  if previous is not None:sys.modules['promote']=previous
 return m

def sha(path):
 h=hashlib.sha256();n=0
 with Path(path).open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b);n+=len(b)
 return h.hexdigest(),n

def j(x):return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False,default=str)
def insert(c,t,r):
 cols=list(r);c.execute(f"INSERT INTO {t} ({','.join(cols)}) VALUES ({','.join('?' for _ in cols)})",[r[x] for x in cols])
def rows(c,t):
 c.row_factory=sqlite3.Row;return [dict(r) for r in c.execute(f'SELECT * FROM {t}')]

def validate_envelope(campaign,body_id=EUROPA,authority_system='loom_solar.body',authority_identifier='EUROPA'):
 errors=[]
 if campaign.get('campaign_id')!='ARP-QUAL-02-EUROPA': errors.append('wrong campaign identity')
 if campaign.get('qualification_state')!='ARP_QUAL_02_EUROPA_PASS_WITH_LIENS': errors.append('campaign is not Gate-A qualified')
 if campaign.get('knowledge_cutoff')!='2025-12-31T23:59:59Z': errors.append('wrong cutoff')
 if authority_system!='loom_solar.body' or authority_identifier!=body_id: errors.append('identity authority mismatch')
 ids={a['assertion_id'] for a in campaign.get('assertions',[])}
 if ids!=set(DISPOSITIONS): errors.append('candidate/disposition set mismatch')
 source_ids={s['source_id'] for s in campaign.get('sources',[])}
 artifact_map={a['artifact_id']:a for a in campaign.get('artifacts',[])}
 for a in campaign.get('assertions',[]):
  if a['source_id'] not in source_ids: errors.append(f"source mismatch:{a['assertion_id']}")
  artifact=artifact_map.get(a['artifact_id'])
  if artifact is None or artifact['source_id']!=a['source_id']:errors.append(f"artifact/source mismatch:{a['assertion_id']}")
  if a['status']!='CANDIDATE':errors.append(f"candidate status mismatch:{a['assertion_id']}")
 if errors:raise ValueError('; '.join(errors))
 return True

def build(destination=OUT,lab_root=None):
 destination=Path(destination);actual_base,_=sha(BASE)
 if actual_base!=EXPECTED_BASE_SHA:raise RuntimeError(f'SF-PROMOTE-02 hash mismatch: {actual_base}')
 dm=digest_module();pre67=dm.body_digest(BASE,'COMET_67P');prece=dm.body_digest(BASE,'CERES')
 if pre67!=EXPECTED_67P or prece!=EXPECTED_CERES:raise RuntimeError('SF-PROMOTE-02 body digest mismatch')
 campaign=json.loads(CAMPAIGN.read_text());frozen=json.loads(FROZEN.read_text());qual=json.loads(REPORT.read_text())
 validate_envelope(campaign)
 campaign_bytes=CAMPAIGN.read_bytes();campaign_sha=hashlib.sha256(campaign_bytes).hexdigest()
 if campaign_sha!=frozen['campaign_sha256']:raise RuntimeError('frozen research campaign hash mismatch')
 if qual['verdict']!='ARP_QUAL_02_EUROPA_PASS_WITH_LIENS':raise RuntimeError('qualification report mismatch')
 lab_root=Path(lab_root) if lab_root else (Path(os.environ['ARP_EUROPA_LAB_ROOT']) if os.environ.get('ARP_EUROPA_LAB_ROOT') else None)
 if lab_root:
  for a in campaign['artifacts']:
   p=lab_root/'projects/arp_qual_02_europa'/a['local_path'];got,n=sha(p)
   if got!=a['sha256'] or n!=a['byte_count']:raise RuntimeError(f"external raw artifact mismatch: {a['artifact_id']}")
 destination.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(BASE,destination)
 c=sqlite3.connect(destination);c.execute('PRAGMA foreign_keys=OFF')
 try:
  source_by={s['source_id']:s for s in campaign['sources']};artifact_by={a['artifact_id']:a for a in campaign['artifacts']}
  asserted_source_ids={a['source_id'] for a in campaign['assertions']};used_sources={k:v for k,v in source_by.items() if k in asserted_source_ids}
  used_artifacts={a['artifact_id']:a for a in artifact_by.values() if a['source_id'] in asserted_source_ids}
  with c:
   if c.execute('SELECT count(*) FROM body WHERE body_id=?',(EUROPA,)).fetchone()[0]:raise RuntimeError('duplicate Solar Facts Europa body row')
   if c.execute('SELECT count(*) FROM body_authority WHERE authority_system=? AND authority_identifier=?',('loom_solar.body','EUROPA')).fetchone()[0]:raise RuntimeError('duplicate loom_solar.body identity link')
   insert(c,'body',{'body_id':EUROPA,'canonical_name':'Europa','body_class':'NATURAL_SATELLITE','parent_body_id':None,'status':'CANDIDATE'})
   insert(c,'body_authority',{'body_id':EUROPA,'authority_system':'loom_solar.body','authority_identifier':'EUROPA','authority_class':'PHASE4_IDENTITY_REFERENCE'})
   next_sid=c.execute('SELECT coalesce(max(source_id),0)+1 FROM source').fetchone()[0];sid_map={}
   lab_commit=frozen.get('research_lab_commit','6492be6b11dd4cd3fa77f017ca98bdd2d1e2406c')
   for i,(old,s) in enumerate(sorted(used_sources.items()),0):
    sid=next_sid+i;sid_map[old]=sid
    st=s['source_type'];typ='PREPRINT' if s['locator'].startswith('https://arxiv.org/') else ('PEER_REVIEWED' if st=='PEER_REVIEWED_PRIMARY' else ('DATA_PRODUCT' if 'ARCHIVE' in st else 'OFFICIAL_REFERENCE'))
    doi=s.get('doi') or next((x for x in [s.get('persistent_identifier','')] if x.startswith('DOI ')),None)
    if doi:doi=doi.removeprefix('DOI ')
    art=next(a for a in used_artifacts.values() if a['source_id']==old)
    insert(c,'source',{'source_id':sid,'source_type':typ,'provider':s['provider'],'title':s['title'],'authors':None,'journal':None,'doi':doi,'url':s['locator'],'publication_date':s.get('publication_date'),'product_name':s.get('source_type'),'product_version':s.get('persistent_identifier'),'persistent_identifier':s.get('persistent_identifier'),'retrieved_at':art['retrieved_at'],'citation_text':s['title'],'notes':f"ARP {campaign['campaign_id']}; authority domain {s['authority_domain']}; original type {st}; primary source artifact."})
   for aid,a in sorted(used_artifacts.items()):
    rel=f"repo://loom-2226/loom-research-lab@{lab_commit}/projects/arp_qual_02_europa/{a['local_path']}"
    insert(c,'source_artifact',{'artifact_id':f"EUROPA:{aid}",'source_id':sid_map[a['source_id']],'locator':a['locator'],'local_path':rel,'retrieved_at':a['retrieved_at'],'sha256':a['sha256'],'byte_count':a['byte_count'],'media_type':a['media_type'],'original_filename':a['original_filename'],'version':a.get('version')})
   # Numeric/displayable facts only; qualitative model and interpretation facts are kept in the same epistemic class.
   A={a['assertion_id']:a for a in campaign['assertions']}; fact_map={};obs_map={};region_map={}
   next_region=c.execute('SELECT coalesce(max(region_id),0)+1 FROM body_region').fetchone()[0]
   for offset,(name,rtype,desc,srcid) in enumerate([('Leading hemisphere','HEMISPHERE','Qualitative leading-hemisphere region named by source; no coordinate bounds asserted.', 'trumbo19'),('Tara Regio','REGIO','Named chaos terrain region; no coordinate bounds asserted.','trumbo19'),('South polar plume observation region','REPORTED_REGION','Qualitatively reported HST plume-location region; no coordinate bounds asserted.','roth14')]):
    rid=next_region+offset;region_map[name]=rid
    insert(c,'body_region',{'region_id':rid,'body_id':EUROPA,'parent_region_id':region_map.get('Leading hemisphere') if name=='Tara Regio' else None,'region_type':rtype,'canonical_name':name,'latitude_min_deg':None,'latitude_max_deg':None,'longitude_min_deg':None,'longitude_max_deg':None,'reference_frame':None,'description':desc,'confidence_class':'UNKNOWN','source_id':sid_map[srcid],'notes':'Names/association from cited source; boundaries intentionally not fabricated.'})
   obs_specs=[
    ('eu-mag-field','Galileo MAG','MAG field measurements at Europa encounters','INSTRUMENT_FOOTPRINT','1990s'),
    ('eu-plume-galileo-candidate','Galileo MAG/PWS','E12 signatures interpreted as consistent with a plume under a modeled interaction','SITE','E12 flyby; source article does not establish continuous activity'),
    ('eu-plume-hst-candidate','HST/STIS','Reported transient south-polar FUV emission; paired nondetection evidence is separate','SITE','2012-11 through 2012-12'),
    ('eu-plume-hst-nondetect','HST/STIS','Apocenter water-vapor plume nondetection at stated sensitivity','INSTRUMENT_FOOTPRINT','2014 epoch'),
    ('eu-plume-sparks','HST/STIS','Ten observations; three epochs where plume activity could be implicated','INSTRUMENT_FOOTPRINT','Published 2016'),
    ('eu-plume-subaru','Subaru/IRCS','Water-emission nondetection within sensitivity and observation time','INSTRUMENT_FOOTPRINT','2024 observations'),
    ('eu-plume-alma-limit','ALMA','Molecular spectral maps and model-dependent upper limits','INSTRUMENT_FOOTPRINT','Four epochs, May–June 2021'),
    ('eu-oxygen-atmos','HST/FUV','Atomic oxygen emission observed; O2 atmosphere is interpretation','GLOBAL','Published 1995'),
    ('eu-nacl-surface','HST/STIS','Visible spectra, 300–1000 nm; broad absorption near 450 nm','GLOBAL_COVERAGE_WITH_REGIONAL_SIGNAL','Four HST visits, 2017-05-23 through 2017-08-06'),
    ('eu-juno-shell','Juno/MWR','Subsurface microwave observation; thickness is an idealized-model result','INSTRUMENT_FOOTPRINT','2022-09-29')]
   for ix,(aid,instrument,notes,scope,epoch) in enumerate(obs_specs):
    a=A[aid];oid=c.execute('SELECT coalesce(max(observation_id),0)+1 FROM observation').fetchone()[0]
    region=region_map['South polar plume observation region'] if aid=='eu-plume-hst-candidate' else (region_map['Leading hemisphere'] if aid=='eu-nacl-surface' else None)
    start={'eu-plume-hst-candidate':'2012-11','eu-nacl-surface':'2017-05-23','eu-juno-shell':'2022-09-29'}.get(aid)
    end={'eu-plume-hst-candidate':'2012-12','eu-nacl-surface':'2017-08-06','eu-juno-shell':'2022-09-29'}.get(aid)
    insert(c,'observation',{'observation_id':oid,'body_id':EUROPA,'region_id':region,'mission':{'Juno/MWR':'Juno','Galileo MAG':'Galileo','Galileo MAG/PWS':'Galileo','HST/STIS':'Hubble Space Telescope','Subaru/IRCS':'Subaru Telescope','ALMA':'Atacama Large Millimeter/submillimeter Array','HST/FUV':'Hubble Space Telescope'}[instrument],'spacecraft':{'Juno/MWR':'Juno','Galileo MAG':'Galileo','Galileo MAG/PWS':'Galileo','HST/STIS':'Hubble Space Telescope','Subaru/IRCS':None,'ALMA':None,'HST/FUV':'Hubble Space Telescope'}[instrument],'instrument':instrument,'observation_product_id':aid,'observation_time_start':start,'observation_time_end':end,'observation_method':a['method_type'],'spatial_context':scope,'source_id':sid_map[a['source_id']],'notes':f"{notes}; source temporal context: {epoch}. {a.get('notes') or ''}",'spatial_resolution_value':None,'spatial_resolution_unit':None,'spatial_resolution_semantics':None,'vertical_sensitivity_min':None,'vertical_sensitivity_max':None,'vertical_sensitivity_unit':None})
    obs_map[aid]=oid
   for aid in ('eu-gm','eu-radius'):
    a=A[aid];fid=c.execute('SELECT coalesce(max(fact_id),0)+1 FROM fact').fetchone()[0];fact_map[aid]=fid
    is_scalar=a.get('normalized_value') is not None and isinstance(a.get('normalized_value'),(int,float))
    value= a.get('normalized_value') if is_scalar else None
    sem='scalar' if is_scalar else 'qualitative_interpretation'
    text=None if is_scalar else (a.get('notes') or '')
    uncertainty=a.get('normalized_uncertainty') if is_scalar and isinstance(a.get('normalized_uncertainty'),(int,float)) else None
    region=region_map['Leading hemisphere'] if aid=='eu-nacl-surface' else None
    insert(c,'fact',{'fact_id':fid,'body_id':EUROPA,'region_id':region,'property_code':a['property_code'],'value_semantics':sem,'value_numeric':value,'value_min':None,'value_max':None,'value_boolean':None,'value_text':text,'uncertainty_plus':uncertainty,'uncertainty_minus':uncertainty,'canonical_unit':a.get('normalized_unit') if is_scalar else None,'reported_value_text':str(a.get('reported_value')) if is_scalar else None,'reported_unit':a.get('reported_unit') if is_scalar else None,'evidence_class':a['evidence_class'],'measurement_method':a['method_type'],'spatial_context':a['scope_type'],'temporal_context':a.get('temporal_context'),'confidence_class':'UNKNOWN','fact_status':'CANDIDATE','knowledge_valid_from':None,'knowledge_valid_until':None,'supersedes_fact_id':None,'created_at':frozen['frozen_at'],'notes':a.get('notes')})
    insert(c,'source_assertion',{'fact_id':fid,'source_id':sid_map[a['source_id']],'assertion_role':'PRIMARY','source_locator':a['artifact_id'],'notes':f"Frozen ARP assertion {aid}; exact candidate remains in promotion ledger."})
   # Link qualitative material evidence only with unknown abundance and a bounded region.
   a=A['eu-nacl-surface'];mid=c.execute('SELECT coalesce(max(material_evidence_id),0)+1 FROM material_evidence').fetchone()[0]
   insert(c,'material_evidence',{'material_evidence_id':mid,'body_id':EUROPA,'region_id':region_map['Leading hemisphere'],'material_family':'chloride_salt','material_species':'sodium chloride (NaCl), interpreted spectral constituent','physical_form':None,'host_material':'surface material / water-ice terrain','location_context':'Leading hemisphere; strongest reported signal in Tara Regio','evidence_class':'EARTH_REMOTE','abundance_semantics':'UNKNOWN','abundance_value':None,'abundance_min':None,'abundance_max':None,'abundance_unit':None,'reported_abundance':None,'depth_min':None,'depth_max':None,'depth_unit':None,'thickness_min':None,'thickness_max':None,'thickness_unit':None,'areal_extent':None,'areal_extent_unit':None,'estimated_volume':None,'estimated_volume_unit':None,'spatial_heterogeneity':'Regional spectral detection/interpretation; no global abundance inference.','measurement_resolution':'HST/STIS spatially resolved visible spectra; see source artifact.','measurement_method':a['method_type'],'confidence_class':'UNKNOWN','fact_status':'CANDIDATE','observation_id':obs_map['eu-nacl-surface'],'source_id':sid_map[a['source_id']],'notes':a['notes']})
   # Candidate activity is epoch-bounded and never represented as a permanent property.
   for aid in ('eu-plume-galileo-candidate','eu-plume-hst-candidate','eu-plume-sparks'):
    a=A[aid];activity_id=c.execute('SELECT coalesce(max(activity_id),0)+1 FROM activity_fact').fetchone()[0]
    obsid=obs_map[aid]
    region=region_map['South polar plume observation region'] if aid=='eu-plume-hst-candidate' else None
    time={'eu-plume-hst-candidate':('2012-12','2012-12'),'eu-plume-sparks':(None,None),'eu-plume-galileo-candidate':(None,None)}[aid]
    insert(c,'activity_fact',{'activity_id':activity_id,'body_id':EUROPA,'region_id':region,'activity_type':'PLUME_CANDIDATE_EVIDENCE','description':a['notes'],'observed_from':time[0],'observed_until':time[1],'evidence_class':a['evidence_class'],'confidence_class':'UNKNOWN','observation_id':obsid,'source_id':sid_map[a['source_id']],'notes':'Candidate-only, scoped to the cited observation/epoch; no continuous or global plume property.'})
   # The USGS map itself is a global synthesis product, not blanket high-resolution coverage.
   a=A['eu-geology'];mp=c.execute('SELECT coalesce(max(model_product_id),0)+1 FROM body_model_product').fetchone()[0]
   art=artifact_by[a['artifact_id']]
   insert(c,'body_model_product',{'model_product_id':mp,'body_id':EUROPA,'region_id':None,'model_type':'GLOBAL_GEOLOGIC_MAP','model_name':'USGS Global Geologic Map of Europa, SIM 3513','model_version':'2024','reference_frame':None,'resolution_description':'Global synthesis; USGS states entire surface not yet observed at regional scale (<250 m/pixel).','source_id':sid_map[a['source_id']],'persistent_identifier':'DOI 10.3133/sim3513','product_url':source_by[a['source_id']]['locator'],'sha256':art['sha256'],'byte_count':art['byte_count'],'notes':a['notes']})
   # Generic orientation model fields contain the exact NAIF PCK coefficients and preserve their distinct units in notes.
   a=A['eu-rotation'];v=a['normalized_value'];om=c.execute('SELECT coalesce(max(orientation_model_id),0)+1 FROM orientation_model').fetchone()[0]
   insert(c,'orientation_model',{'orientation_model_id':om,'body_id':EUROPA,'model_name':'NAIF BODY502 PCK orientation model','model_version':'pck00011.tpc (2022-12-27)','model_authority':'NAIF/JPL','reference_frame':'IAU_EUROPA / SPICE PCK convention','reference_epoch':'J2000 polynomial convention','pole_ra_deg':v['pole_ra_deg'],'pole_dec_deg':v['pole_dec_deg'],'pole_ra_rate':v['pole_ra_rate_deg_per_century'],'pole_dec_rate':v['pole_dec_rate_deg_per_century'],'prime_meridian_deg':v['prime_meridian_deg'],'prime_meridian_rate':v['prime_meridian_rate_deg_per_day'],'rotation_period_seconds':None,'rotation_state':None,'libration_model':'NAIF PCK nutation/precession coefficients retained in source kernel; not independently interpreted here.','source_id':sid_map[a['source_id']],'persistent_identifier':'NAIF PCK00011','product_url':source_by[a['source_id']]['locator'],'validity_notes':'PCK constants/model only; no claim of directly measured libration or tidal response.','notes':a['notes']})
   # Every campaign assertion receives exactly one explicit review disposition and complete raw envelope.
   next_pid=c.execute('SELECT coalesce(max(promotion_assertion_id),0)+1 FROM promotion_assertion').fetchone()[0]
   for n,a in enumerate(campaign['assertions']):
    disp,reason=DISPOSITIONS[a['assertion_id']];raw=j(a);pid=next_pid+n
    art=artifact_by[a['artifact_id']]
    insert(c,'promotion_assertion',{'promotion_assertion_id':pid,'campaign_id':campaign['campaign_id'],'assertion_id':a['assertion_id'],'body_id':EUROPA,'source_id':sid_map[a['source_id']],'artifact_id':f"EUROPA:{a['artifact_id']}",'property_code':a['property_code'],'claim_kind':a['claim_kind'],'evidence_class':a['evidence_class'],'scope_type':a.get('scope_type'),'region_id':None,'method_type':a.get('method_type'),'independent_lineage_id':a.get('independent_evidence_lineage_id'),'reported_value_json':j(a.get('reported_value')),'reported_unit':a.get('reported_unit'),'reported_uncertainty_json':j(a.get('reported_uncertainty')),'normalized_value_json':j(a.get('normalized_value')),'normalized_unit':a.get('normalized_unit'),'normalized_uncertainty_json':j(a.get('normalized_uncertainty')),'normalization_method':a.get('normalization_method'),'resolution_json':j(a.get('resolution',{})),'temporal_context':a.get('temporal_context'),'status':'CANDIDATE','raw_assertion_json':raw,'raw_sha256':hashlib.sha256(raw.encode()).hexdigest(),'notes':a.get('notes')})
    insert(c,'promotion_review',{'promotion_assertion_id':pid,'disposition':disp,'reviewer':'SF-PROMOTE-03 deterministic typed-fit review','reason':reason})
   # Preserve explicit derivation lineage where interpretation uses measurement; no cross-body inputs are allowed.
   pids={r['assertion_id']:r['promotion_assertion_id'] for r in rows(c,'promotion_assertion') if r['campaign_id']==campaign['campaign_id']}
   for aid,inputs,notes in [('eu-ocean-inference',['eu-mag-field'],'Interpretation depends on Europa Galileo induced-field measurements; does not imply direct ocean observation.'),('eu-plume-galileo-candidate',['eu-mag-field'],'Candidate is derived from same Galileo E12 MAG event plus PWS; same lineage, not independent confirmation.')]:
    insert(c,'promotion_lineage',{'promotion_assertion_id':pids[aid],'input_assertion_ids_json':j(inputs),'notes':notes})
   for f in campaign['epistemic_frontier']:
    c.execute('INSERT INTO epistemic_frontier(campaign_id,variable,phase,research_coverage,state_at_cutoff,evidence_class,limitation) VALUES(?,?,?,?,?,?,?)',(campaign['campaign_id'],f['variable'],f['phase'],f['research_coverage'],f['state_at_cutoff'],f.get('evidence_class'),f.get('limitation')))
   for s in sorted(used_sources.values(),key=lambda x:x['source_id']):
    source_key=sid_map[s['source_id']]
    c.execute('INSERT INTO knowledge_event(event_key,event_type,event_time,target_source_id,source_id,notes) VALUES(?,?,?,?,?,?)',(f"EUROPA:SOURCE_PUBLICATION:{source_key}",'PUBLISHED',s.get('publication_date') or s.get('release_date') or '2025-12-31',source_key,source_key,'Bibliographic/catalog publication date from frozen ARP source record; not spacecraft observation time.'))
   manifest={
    'campaign_id':campaign['campaign_id'],'research_lab_repository':'loom-2226/loom-research-lab','research_lab_commit':lab_commit,
    'research_campaign_sha256':campaign_sha,'research_frozen_manifest_sha256':hashlib.sha256(FROZEN.read_bytes()).hexdigest(),
    'arp_qualification_report_sha256':hashlib.sha256(REPORT.read_bytes()).hexdigest(),'knowledge_cutoff':campaign['knowledge_cutoff'],
    'body_authority':'loom_solar.body:EUROPA','naif_identifier':'502','parent_body_reference':'loom_solar.body:JUPITER_SYSTEM_BARYCENTER (reference only; no fourth Solar Facts body row)','preferred_fact_count':'0','facts_status':'CANDIDATE_ONLY',
    'promotion_disposition_counts':json.dumps({d:sum(1 for a in campaign['assertions'] if DISPOSITIONS[a['assertion_id']][0]==d) for d in sorted({v[0] for v in DISPOSITIONS.values()})},sort_keys=True),
    'campaign_source_ids':json.dumps(sorted(sid_map.values())),
    'campaign_artifact_ids':json.dumps(sorted('EUROPA:'+x for x in used_artifacts)),
    'raw_artifacts':'Hash/size frozen in campaign; bytes reside in Research Lab commit, not duplicated in upstream tree.',
    'raw_artifact_byte_verification':'PASS' if lab_root else 'FROZEN_MANIFEST_ONLY',
    'schema_change':'NONE','phase4_writes':'0'}
   for k,v in manifest.items():c.execute('INSERT OR REPLACE INTO promotion_manifest VALUES(?,?)',(k,str(v)))
   c.execute("UPDATE meta SET value=? WHERE key='schema_name'",('LOOM_SOLAR_FACTUAL_ENRICHMENT_MULTI_BODY_v0.3-R1',))
   c.execute("UPDATE meta SET value=? WHERE key='qualification_case'",('SF-PROMOTE-03_EUROPA_CERES_67P',))
   c.execute("INSERT OR REPLACE INTO meta VALUES('schema_version','MULTI_BODY_v0.3-R1')")
   c.execute("INSERT OR REPLACE INTO meta VALUES('authority_boundary','DEV_ONLY_CANDIDATE_PROMOTION')")
   c.execute("UPDATE meta SET value=? WHERE key='created_utc'",(frozen['frozen_at'],))
  c.execute('PRAGMA foreign_keys=ON')
  fk=list(c.execute('PRAGMA foreign_key_check'))
  if fk:raise RuntimeError(f'foreign key failures {fk[:5]}')
  if c.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise RuntimeError('SQLite integrity failure')
  if c.execute('SELECT count(*) FROM preferred_fact').fetchone()[0]!=0:raise RuntimeError('preferred fact firewall failed')
  for aid,(disp,_) in DISPOSITIONS.items():
   if c.execute('SELECT count(*) FROM promotion_review r JOIN promotion_assertion p USING(promotion_assertion_id) WHERE p.assertion_id=? AND p.body_id=? AND r.disposition=?',(aid,EUROPA,disp)).fetchone()[0]!=1:raise RuntimeError(f'review disposition mismatch for {aid}')
 finally:c.close()
 return destination
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--lab-root',type=Path);p.add_argument('--output',type=Path,default=OUT);a=p.parse_args();build(a.output,a.lab_root)
