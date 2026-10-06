"""Exactly one governed SQLite snapshot -> lossless raw archive and typed projections.

The row plan is temporary ETL staging, never a runtime entity or science store.
"""
from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
import csv, hashlib, json, math, sqlite3, struct, uuid
from .store import stable_uuid, length_prefixed, IntegrityFailure, _complete_columns

ROOT=Path(__file__).resolve().parents[2]
DOMAIN=ROOT/'data/world_authority'
SOURCE_SHA='72ddfab0eb35fb5a86ecfd50d4bc939a982ffc1fe3362108036082298a57b777'
SOURCE_COMMIT='acd0eb9fada60a0d2509de6af8c23ec3df6c28d6'
SOURCE_PATH='simulation/offworld_mvp/world_science/lab_v0_1/LOOM_SOLAR_WORLD_SCIENCE_LAB_v0_1.sqlite3'
REV='SQLITE_SHA256:'+SOURCE_SHA
AUTH='LOOM_WORLD_SCIENCE_SQLITE_V1'


def canonical(value):
    def encode(v):
        if isinstance(v,Decimal):return str(v)
        if isinstance(v,uuid.UUID):return str(v)
        if type(v).__module__.startswith('psycopg') and type(v).__name__=='Range':return {'range_lower':v.lower,'range_upper':v.upper,'range_bounds':v.bounds,'range_empty':v.isempty}
        if isinstance(v,(bytes,bytearray,memoryview)):return {'bytea_hex':bytes(v).hex()}
        raise TypeError(type(v).__name__)
    return json.dumps(value,sort_keys=True,ensure_ascii=True,separators=(',',':'),allow_nan=False,default=encode).encode('utf8')


def digest(value):return hashlib.sha256(canonical(value)).hexdigest()


def scalar(value,ordinal):
    v={'ordinal':ordinal}
    if value is None:v['storage_class']='NULL'
    elif isinstance(value,int):v.update(storage_class='INTEGER',integer_lexeme=str(value))
    elif isinstance(value,float):
        if not math.isfinite(value):raise IntegrityFailure('SOURCE_NONFINITE')
        v.update(storage_class='REAL',ieee754_be64=struct.pack('>d',value).hex(),display_lexeme=repr(value))
    elif isinstance(value,str):v.update(storage_class='TEXT',utf8_hex=value.encode('utf8').hex(),text=value)
    elif isinstance(value,bytes):v.update(storage_class='BLOB',bytes_hex=value.hex())
    else:raise IntegrityFailure('SOURCE_STORAGE_CLASS')
    return v


def canonical_legacy_row(columns,values):
    obj={name:scalar(v,i) for i,(name,v) in enumerate(zip(columns,values,strict=True))}
    return obj,canonical(obj),digest(obj)


def decode_scalar(v):
    k=v['storage_class']
    if k=='NULL':return None
    if k=='INTEGER':return int(v['integer_lexeme'])
    if k=='REAL':return struct.unpack('>d',bytes.fromhex(v['ieee754_be64']))[0]
    if k=='TEXT':return bytes.fromhex(v['utf8_hex']).decode('utf8')
    if k=='BLOB':return bytes.fromhex(v['bytes_hex'])
    raise IntegrityFailure('RAW_STORAGE_CLASS')


def number(v):return Decimal(repr(v)) if isinstance(v,float) else v


@dataclass(frozen=True)
class TargetRow:
    table:str
    values:dict

@dataclass(frozen=True)
class ImportPlan:
    source_file:Path
    source_sha256:str
    snapshot_id:uuid.UUID
    rows:tuple[TargetRow,...]
    counts:dict
    source_schema:dict
    source_rows:dict
    crosswalk:tuple[dict,...]
    plan_hash:str


def inspect_source_schema(connection,expected):
    """Production source-integrity/schema checks, separately hostile-testable."""
    if connection.execute('PRAGMA integrity_check').fetchone()!=('ok',) or list(connection.execute('PRAGMA foreign_key_check')):
        raise IntegrityFailure('SOURCE_INTEGRITY')
    tables=[t for t, in connection.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")]
    schema={t:[list(v) for v in connection.execute('PRAGMA table_info("'+t+'")')] for t in tables}
    if schema!=expected:raise IntegrityFailure('SOURCE_SCHEMA_DRIFT')
    for table in ('generation_model','generation_policy','world_realization','world_constraint_binding','hidden_world_state','project_site','deposit'):
        if connection.execute('SELECT count(*) FROM "'+table+'"').fetchone()[0]:raise IntegrityFailure('NONEMPTY_WORLD_SKELETON')
    return schema


def plan_sqlite_import(path,expected_sha=SOURCE_SHA,*,source_commit=SOURCE_COMMIT,source_path=SOURCE_PATH):
    path=Path(path).resolve()
    if source_commit!=SOURCE_COMMIT or source_path!=SOURCE_PATH:raise IntegrityFailure('SOURCE_DRIFT')
    if hashlib.sha256(path.read_bytes()).hexdigest()!=expected_sha or expected_sha!=SOURCE_SHA or path.stat().st_size!=1056768:raise IntegrityFailure('SOURCE_DRIFT')
    if any(Path(str(path)+suffix).exists() for suffix in ('-wal','-journal','-shm')):raise IntegrityFailure('SOURCE_JOURNAL_DEPENDENCY')
    schema_expected=json.loads((DOMAIN/'SOURCE_SCHEMA_V1.json').read_text())
    schema={};data={};raw={};source_keys={};cross=[];rows=[]
    with sqlite3.connect(path.as_uri()+'?mode=ro&immutable=1',uri=True) as c:
        schema=inspect_source_schema(c,schema_expected)
        tables=sorted(schema)
        for t in tables:
            cols=[v[1] for v in schema[t]];pks=[v[1] for v in sorted(schema[t],key=lambda v:v[5]) if v[5]]
            # Empty assertion_input has no SQLite PK; its pinned natural tuple is all five fields.
            if t=='assertion_input':pks=cols
            q='SELECT '+','.join('"'+v+'"' for v in cols)+' FROM "'+t+'" ORDER BY '+','.join('"'+v+'"' for v in pks)
            data[t]=[]
            for vals in c.execute(q):
                obj,_,h=canonical_legacy_row(cols,vals);key='ROWKEY_V1:'+canonical([obj[k] for k in pks]).decode()
                r=dict(zip(cols,vals));r['_key']=key;r['_digest']=h;data[t].append(r);raw[(t,key)]=obj
                source_keys[(t,key)]=key
    dispositions=list(csv.DictReader((DOMAIN/'SQLITE_TO_POSTGRES_DISPOSITION_MATRIX_V1.csv').open()))
    if {(r['sqlite_table'],r['sqlite_concept_or_column']) for r in dispositions if r['sqlite_table'] in schema and r['sqlite_concept_or_column']!='TABLE'}!={(t,c[1]) for t,cs in schema.items() for c in cs}:raise IntegrityFailure('SOURCE_COLUMN_DISPOSITION_GAP')
    counts={t:len(v) for t,v in data.items()}
    expected=json.loads((DOMAIN/'SOURCE_COUNTS_V1.json').read_text())
    if counts!=expected or sum(counts.values())!=2726:raise IntegrityFailure('SOURCE_ROW_DRIFT')
    sid=stable_uuid('SOURCE_SNAPSHOT','loom-2226/loom-2226',SOURCE_PATH,REV)
    def add(t,**v):
        v=_complete_columns(t,{k:number(z) for k,z in v.items()});rows.append(TargetRow(t,v));return v
    def ident(kind,r,key=None):return stable_uuid(kind,AUTH,r[key] if key else r['_key'],REV)
    ids={}
    specs={'source':('source_id','SOURCE','source_key'),'source_artifact':('artifact_id','SOURCE_ARTIFACT','artifact_key'),'sample':('sample_id','SAMPLE','sample_key'),'spatial_product':('spatial_product_id','SPATIAL_PRODUCT','product_key'),'observation':('observation_id','OBSERVATION','observation_key'),'scientific_assertion':('assertion_id','ASSERTION','assertion_key'),'material_evidence':('material_evidence_id','MATERIAL_EVIDENCE',None),'coverage':('coverage_id','COVERAGE',None),'reconciliation':('reconciliation_id','RECONCILIATION',None),'ephemeris_source':('ephemeris_source_id','NAV_PRODUCT',None)}
    for t,(pk,kind,key) in specs.items():
        for r in data[t]:ids[(t,r[pk])]=ident(kind,r,key);cross.append({'table':t,'source_key':r['_key'],'target_id':str(ids[(t,r[pk])])})
    for r in data['body']:ids[('body',r['body_id'])]=stable_uuid('BODY','LOOM_BODY_V1',r['body_id'],'IDENTITY_V1')
    for r in data['region']:ids[('region',r['region_id'])]=stable_uuid('LOCATION','LOOM_LOCATION_V1',length_prefixed(r['body_id'],r['region_key']).decode(),'IDENTITY_V1')
    def fk(t,v):return None if v is None else ids[(t,v)]
    def ref(t,r):return 'SOURCE_ROW:'+SOURCE_SHA+':'+t+':'+r['_key']
    source_parent=path.parent
    add('wa_meta.source_snapshot',snapshot_id=sid,semantic_key=SOURCE_PATH,repository='loom-2226/loom-2226',git_commit=SOURCE_COMMIT,source_path=SOURCE_PATH,byte_sha256=SOURCE_SHA,byte_count=path.stat().st_size,schema_ref='WorldScienceSchemaV0_1:'+hashlib.sha256((source_parent/'SCHEMA.sql').read_bytes()).hexdigest(),authority_class='PRE_CONTRACT_EXPERIMENTAL_NON_CANON',original_manifest=(source_parent/'SOURCE_MANIFEST.json').read_bytes())
    for (t,k),obj in sorted(raw.items()):add('wa_meta.legacy_row',snapshot_id=sid,table_name=t,source_key=k,original_columns=obj,row_digest=digest(obj))
    units=set()
    for t in ('scientific_assertion','material_evidence','sample','observation','spatial_product'):
        for r in data[t]:
            for k,v in r.items():
                if (k=='unit' or k.endswith('_unit')) and v is not None:
                    if not v:raise IntegrityFailure('EMPTY_SUPPLIED_UNIT')
                    units.add(v)
    def unit(v):return None if v is None else 'SRC_UNIT:'+hashlib.sha256(v.encode()).hexdigest()
    for v in sorted(units):add('wa_meta.unit',unit_key=unit(v),source_lexeme=v,dimension_ref=None,canonical_unit_ref=None,conversion_profile_ref=None,interpretation_state='UNCHARACTERIZED')
    def helper(kind,t,r,purpose):return stable_uuid(kind,AUTH,length_prefixed(t,r['_key'],purpose).decode(),REV)
    def temporal(t,r,purpose,instant=None,start=None,end=None,required=False):
        if instant is None and start is None and end is None and not required:return None
        x=helper('TIME_SUPPORT',t,r,purpose);add('wa_geo.time_support',time_id=x,kind='UNKNOWN' if instant is None and start is None and end is None else 'LEXICAL',time_lexeme=instant,start_lexeme=start,end_lexeme=end,calendar_ref=None,timescale_ref=None,instant_utc=None,interval_utc=None,parsing_warrant_ref=None);return x
    times={};verticals={};supports={}
    for t in ('scientific_assertion','material_evidence','observation','spatial_product'):
        for r in data[t]:
            k=r.get('vertical_coordinate_type');lo=r.get('vertical_min');hi=r.get('vertical_max');u=r.get('vertical_unit');d=r.get('vertical_datum')
            if any(v is not None for v in (k,lo,hi,u,d)):
                if k not in ('NONE','UNKNOWN','ALTITUDE','DEPTH_BELOW_SURFACE','PRESSURE_LEVEL'):raise IntegrityFailure('VERTICAL_ALIAS')
                x=helper('VERTICAL_SUPPORT',t,r,'vertical');verticals[(t,r['_key'])]=x;add('wa_geo.vertical_support',vertical_id=x,coordinate_kind=k,lower_value=lo,upper_value=hi,unit_key=unit(u),datum_ref=d,original_coordinate_lexeme=k)
            if t=='scientific_assertion':times[(t,r['_key'])]=temporal(t,r,'valid',start=r['valid_time_start'],end=r['valid_time_end'])
    for r in data['body']:add('wa_geo.body',body_id=fk('body',r['body_id']),semantic_key=r['body_id'],canonical_name=r['canonical_name'],body_class=r['body_class'],parent_body_id=fk('body',r['parent_body_id']),status_lexeme=r['status'],original_ref=ref('body',r))
    for r in data['body_identifier']:add('wa_geo.body_identifier',body_id=fk('body',r['body_id']),authority=r['authority'],identifier_type=r['identifier_type'],identifier_value=r['identifier_value'],status_lexeme=r['status'])
    kinds={'LOCAL_SITE':'SITE','SAMPLE_SITE':'SITE','MODEL_DOMAIN':'MODEL_DOMAIN','FOOTPRINT':'FOOTPRINT','ATMOSPHERIC_DOMAIN':'ATMOSPHERIC_DOMAIN','INTERIOR_DOMAIN':'INTERIOR_DOMAIN'}
    ordinary={'ASSOCIATED_STRUCTURE','CHAOS_TERRAIN','CHASMA','CORONA_TERRAIN','DUNE_TERRAIN','FRACTURE_SYSTEM','HEMISPHERE','IMPACT_STRUCTURE','LANDING_REGION','OBSERVED_HEMISPHERE','PLAIN','POLAR_REGION','POLAR_TERRAIN','REGION','REPORTED_REGION','RIDGE','SEA','TECTONIC_TERRAIN','TERRAIN_CLASS','VOLCANIC_REGION'}
    for r in data['region']:
        k=r['region_type'];kind=kinds.get(k,'REGION' if k in ordinary else None)
        if kind is None:raise IntegrityFailure('REGION_ALIAS')
        add('wa_geo.location',location_id=fk('region',r['region_id']),body_id=fk('body',r['body_id']),system_id=None,semantic_key=r['region_key'],name=r['region_name'],location_kind=kind,original_region_type=k,origin_kind='SCIENTIFIC_MODEL_DOMAIN' if k in ('MODEL_DOMAIN','INTERIOR_DOMAIN') else 'EMPIRICALLY_IDENTIFIED',geometry_id=None,source_ref=ref('region',r),notes=r['notes'])
    for r in data['region']:
        if r['parent_region_id'] is not None:add('wa_geo.location_relation',from_location_id=fk('region',r['parent_region_id']),to_location_id=fk('region',r['region_id']),relation_kind='CONTAINS',warrant_ref=ref('region',r))
    sources={};artifacts={}
    for r in data['source']:
        sources[r['source_id']]=add('wa_science.source',source_id=fk('source',r['source_id']),semantic_key=r['source_key'],revision=REV,title=r['title'],authority=r['authority'],source_type=r['source_type'],url=r['url'],doi=r['doi'],publication_time_id=temporal('source',r,'publication',instant=r['publication_date']),acquired_time_id=temporal('source',r,'acquired',instant=r['acquired_at']),notes=r['notes'],snapshot_id=sid)
    for r in data['source_artifact']:
        artifacts[r['artifact_id']]=add('wa_science.source_artifact',artifact_id=fk('source_artifact',r['artifact_id']),source_id=fk('source',r['source_id']),semantic_key=r['artifact_key'],revision=REV,local_path_lexeme=r['local_path'],retrieval_url=r['retrieval_url'],byte_sha256=r['sha256'],byte_count=r['byte_count'],acquired_time_id=temporal('source_artifact',r,'acquired',instant=r['acquired_at']),custody_kind=r['origin_kind'])
    for r in data['sample']:add('wa_science.sample',sample_id=fk('sample',r['sample_id']),body_id=fk('body',r['body_id']),location_id=fk('region',r['region_id']),semantic_key=r['sample_key'],sample_name=r['sample_name'],collection_site_lexeme=r['collection_site'],collection_method=r['collection_method'],collection_time_id=temporal('sample',r,'collection',start=r['collection_time_start'],end=r['collection_time_end']),mass_value=r['mass_value'],mass_unit_key=unit(r['mass_unit']),source_id=fk('source',r['source_id']),notes=r['notes'])
    for t in ('scientific_assertion','material_evidence','observation','spatial_product'):
        for r in data[t]:
            s=r['scope'];l=fk('region',r['region_id']);sample=fk('sample',r.get('sample_id')) if s=='SAMPLE' else None
            x=helper('SUPPORT',t,r,'support');supports[(t,r['_key'])]=add('wa_science.support',support_id=x,body_id=fk('body',r['body_id']),scope_kind=s,location_id=None if s in ('BODY','SAMPLE') else l,sample_id=sample,geometry_id=None,support_resolution='IDENTIFIED' if (s=='BODY' or (s=='SAMPLE' and sample is not None) or (s not in ('BODY','SAMPLE') and l is not None)) else 'UNRESOLVED',vertical_id=verticals.get((t,r['_key'])),valid_time_id=times.get((t,r['_key'])),representativeness_lexeme=r.get('representativeness') if r.get('representativeness') is not None else 'SOURCE_NOT_SUPPLIED',scope_warrant_ref=ref(t,r))
    def support(t,r):return supports[(t,r['_key'])]['support_id']
    for r in data['spatial_product']:add('wa_science.spatial_product',product_id=fk('spatial_product',r['spatial_product_id']),body_id=fk('body',r['body_id']),support_id=support('spatial_product',r),semantic_key=r['product_key'],product_type=r['product_type'],title=r['title'],source_id=fk('source',r['source_id']),horizontal_resolution_value=r['horizontal_resolution_value'],horizontal_resolution_unit_key=unit(r['horizontal_resolution_unit']),vertical_sensitivity_min=r['vertical_sensitivity_min'],vertical_sensitivity_max=r['vertical_sensitivity_max'],vertical_sensitivity_unit_key=unit(r['vertical_sensitivity_unit']),geometry_ref_lexeme=r['geometry_ref'],coordinate_frame_lexeme=r['coordinate_frame'],status_lexeme=r['status'])
    for r in data['observation']:add('wa_science.observation',observation_id=fk('observation',r['observation_id']),body_id=fk('body',r['body_id']),support_id=support('observation',r),product_id=fk('spatial_product',r['spatial_product_id']),semantic_key=r['observation_key'],measurement_method=r['measurement_method'],observation_time_id=temporal('observation',r,'observation',instant=r['observation_time'],start=r['observation_time_start'],end=r['observation_time_end']),source_id=fk('source',r['source_id']),horizontal_resolution_value=r['horizontal_resolution_value'],horizontal_resolution_unit_key=unit(r['horizontal_resolution_unit']),vertical_sensitivity_min=r['vertical_sensitivity_min'],vertical_sensitivity_max=r['vertical_sensitivity_max'],vertical_sensitivity_unit_key=unit(r['vertical_sensitivity_unit']),notes=r['notes'])
    for r in data['scientific_assertion']:
        if r['preferred'] not in (0,1):raise IntegrityFailure('PREFERRED_NOT_BOOLEAN')
        vals=dict(assertion_id=fk('scientific_assertion',r['assertion_id']),semantic_key=r['assertion_key'],revision=REV,body_id=fk('body',r['body_id']),support_id=support('scientific_assertion',r),property_code=r['property_code'],ontology=r['ontology'],world_context='REAL',observation_id=fk('observation',r['observation_id']),sample_id=fk('sample',r['sample_id']),product_id=fk('spatial_product',r['spatial_product_id']),value_kind=r['value_kind'],value_numeric=number(r['value_numeric']),value_text=None if r['value_kind']=='UNKNOWN' else r['value_text'],value_min=number(r['value_min']),value_max=number(r['value_max']),bound_operator=r['bound_operator'],unit_key=unit(r['unit']),unit_state='NOT_SUPPLIED' if r['unit'] is None else 'SUPPLIED',uncertainty_numeric=number(r['uncertainty_numeric']),uncertainty_text=r['uncertainty_text'],epistemic_class_lexeme=r['epistemic_class'],measurement_method=r['measurement_method'],confidence_lexeme=r['confidence'],knowledge_time_id=temporal('scientific_assertion',r,'knowledge',instant=r['knowledge_date']),source_id=fk('source',r['source_id']),source_artifact_id=fk('source_artifact',r['source_artifact_id']),source_locator=r['source_locator'],lineage_lexeme=r['lineage'],initial_standing=r['admission_status'],preferred_lexeme=bool(r['preferred']),origin_lexeme=r['origin'],notes=r['notes'])
        meta={'source_payload_disposition':{'value_text':'FORENSIC_ONLY_EXPLANATORY_TEXT_WHEN_VALUE_KIND_UNKNOWN'} if r['value_kind']=='UNKNOWN' and r['value_text'] is not None else {},'schema':'SCIENCE_ASSERTION_METADATA_JSON_V1','source_snapshot_sha256':SOURCE_SHA,'sqlite_table':'scientific_assertion','source_key':r['_key'],'forensic_row_digest':r['_digest'],'assertion':vals,'support':supports[('scientific_assertion',r['_key'])],'source':sources[r['source_id']],'source_artifact':artifacts.get(r['source_artifact_id'])}
        mb=canonical(meta);add('wa_science.assertion',**vals,metadata_bytes=mb,metadata_sha256=hashlib.sha256(mb).hexdigest())
    for r in data['material_evidence']:add('wa_science.material_evidence',evidence_id=fk('material_evidence',r['material_evidence_id']),body_id=fk('body',r['body_id']),support_id=support('material_evidence',r),observation_id=fk('observation',r['observation_id']),sample_id=fk('sample',r['sample_id']),material_family=r['material_family'],material_species=r['material_species'],phase_lexeme=r['phase'],physical_form_lexeme=r['physical_form'],evidence_class_lexeme=r['evidence_class'],abundance_semantics_lexeme=r['abundance_semantics'],value=r['abundance_value'],value_min=r['abundance_min'],value_max=r['abundance_max'],unit_key=unit(r['abundance_unit']),legacy_depth_min=r['depth_min'],legacy_depth_max=r['depth_max'],legacy_depth_unit_key=unit(r['depth_unit']),source_id=fk('source',r['source_id']),initial_standing=r['admission_status'],origin_lexeme=r['origin'],notes=r['notes'])
    for r in data['coverage']:add('wa_science.coverage',coverage_id=fk('coverage',r['coverage_id']),body_id=fk('body',r['body_id']),domain_lexeme=r['domain'],property_or_class_lexeme=r['property_or_class'],state_lexeme=r['state'],origin_lexeme=r['origin'],reason=r['reason'])
    for r in data['reconciliation']:add('wa_science.reconciliation',reconciliation_id=fk('reconciliation',r['reconciliation_id']),body_id=fk('body',r['body_id']),property_code=r['property_code'],assertion_a=fk('scientific_assertion',r['assertion_a']),assertion_b=fk('scientific_assertion',r['assertion_b']),classification_lexeme=r['classification'],reason=r['reason'],status_lexeme=r['status'])
    for r in data['ephemeris_source']:add('wa_nav.product',product_id=fk('ephemeris_source',r['ephemeris_source_id']),semantic_key=r['_key'],provider=r['provider'],product_name=r['product_name'],product_version=r['product_version'],asset_filename=r['asset_filename'],byte_sha256=r['sha256'],byte_count=r['byte_count'],source_url=r['source_url'],acquired_time_id=temporal('ephemeris_source',r,'acquired',instant=r['acquired_at']),status_lexeme=r['status'])
    for r in data['ephemeris_coverage']:add('wa_nav.coverage',product_id=fk('ephemeris_source',r['ephemeris_source_id']),body_id=fk('body',r['body_id']),coverage_key=r['_key'],valid_time_id=temporal('ephemeris_coverage',r,'valid',start=r['valid_from'],end=r['valid_until'],required=True),frame_id=None,original_frame_lexeme=r['reference_frame'],units_lexeme=r['units'],coverage_class=r['coverage_class'],status_lexeme=r['status'])
    order=['wa_meta.source_snapshot','wa_meta.legacy_row','wa_meta.unit','wa_geo.time_support','wa_geo.vertical_support','wa_geo.body','wa_geo.body_identifier','wa_geo.location','wa_geo.location_relation','wa_science.source','wa_science.source_artifact','wa_science.sample','wa_science.support','wa_science.spatial_product','wa_science.observation','wa_science.assertion','wa_science.material_evidence','wa_science.coverage','wa_science.reconciliation','wa_nav.product','wa_nav.coverage']
    # Column/PK inventory is closed at implementation, not inferred from arbitrary input.
    from .store import TABLE_KEYS
    rows.sort(key=lambda r:(order.index(r.table),canonical([r.values[k] for k in TABLE_KEYS[r.table]])))
    counts_target={t:sum(r.table==t for r in rows) for t in order}
    if len(rows)!=7126 or counts_target['wa_meta.unit']!=25 or counts_target['wa_geo.time_support']!=639 or counts_target['wa_geo.vertical_support']!=17 or counts_target['wa_science.support']!=997:raise IntegrityFailure('NORMALIZED_HELPER_COUNT_MISMATCH:'+str(counts_target))
    if hashlib.sha256(path.read_bytes()).hexdigest()!=SOURCE_SHA:raise IntegrityFailure('SOURCE_CHANGED_DURING_PLAN')
    ph=digest({'profile':'WA_IMPORT_PLAN_V1','source':SOURCE_SHA,'rows':[(r.table,r.values) for r in rows],'schema':schema,'ddl_sha256':hashlib.sha256((DOMAIN/'migrations/001_world_authority_v1.sql').read_bytes()).hexdigest(),'implementation_sha256':hashlib.sha256(Path(__file__).read_bytes()+(Path(__file__).parent/'store.py').read_bytes()).hexdigest(),'dispositions_sha256':hashlib.sha256((DOMAIN/'SQLITE_TO_POSTGRES_DISPOSITION_MATRIX_V1.csv').read_bytes()).hexdigest()})
    return ImportPlan(path,SOURCE_SHA,sid,tuple(rows),counts,schema,data,tuple(cross),ph)
