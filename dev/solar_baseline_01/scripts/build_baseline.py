#!/usr/bin/env python3
"""Offline deterministic baseline build from frozen JPL/NAIF artifacts."""
import csv,hashlib,json,re,sqlite3,sys,time,os
from datetime import datetime,timezone
from decimal import Decimal,InvalidOperation
from html.parser import HTMLParser
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; RAW=ROOT/'raw'; REPORTS=ROOT/'reports'
OUT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else ROOT/'LOOM_SOLAR_BASELINE_01_CANDIDATE_V17.sqlite3'
REVERSE=os.environ.get('LOOM_BASELINE_REVERSE')=='1'
NAIF_NAMES_TEXT=(RAW/'naif_ids_required_reading.html').read_text(errors='replace') if (RAW/'naif_ids_required_reading.html').exists() else ''
NAIF_BARYCENTER_IDS={m.group(1) for m in re.finditer(r"(?m)^\s*(\d+)\s+'[^']*BARYCENTER[^']*'",NAIF_NAMES_TEXT,re.I)}
def ordered(xs):
    return list(reversed(xs)) if REVERSE else list(xs)
SMALL={'ASTEROID','NEAR_EARTH_ASTEROID','TROJAN_ASTEROID','BINARY_ASTEROID_PRIMARY','COMET','DWARF_PLANET','CENTAUR','TRANS_NEPTUNIAN_OBJECT','INTERSTELLAR_OBJECT'}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def canon(x): return re.sub(r'\s+',' ',x.strip()).casefold()
def parse_numeric(raw):
    s=raw.strip().replace(',','')
    m=re.search(r'(?P<op><=|>=|<|>|≤|≥)?\s*(?P<v>[+-]?(?:\d+\.?\d*|\.\d+)(?:[Ee][+-]?\d+)?)',s)
    if not m:return None,None
    sig=re.search(r'(?:±|\\pm)\s*([+-]?(?:\d+\.?\d*|\.\d+)(?:[Ee][+-]?\d+)?)',s)
    return (m.group('op') or '')+str(Decimal(m.group('v'))), (str(Decimal(sig.group(1))) if sig else None)
class Tables(HTMLParser):
    def __init__(self): super().__init__();self.inrow=False;self.incell=False;self.buf='';self.cells=[];self.rows=[]
    def handle_starttag(self,t,a):
        if t=='tr':self.inrow=True;self.cells=[]
        elif t in ('td','th') and self.inrow:
            # The live SSD pages contain omitted closing </td> tags. HTML's
            # table parser implicitly closes a cell when its successor starts.
            if self.incell:self.cells.append(' '.join(self.buf.split()))
            self.incell=True;self.buf=''
    def handle_data(self,d):
        if self.incell:self.buf+=d
    def handle_endtag(self,t):
        if t in ('td','th') and self.incell:self.cells.append(' '.join(self.buf.split()));self.incell=False
        elif t=='tr' and self.inrow:
            if self.cells:self.rows.append(self.cells)
            self.inrow=False
def load_identities():
    rows=[]
    for l in (RAW/'loom_solar_identity_snapshot.tsv').read_text().splitlines():
        x=l.split('|')
        if len(x)!=9:raise ValueError('identity snapshot row width')
        rows.append(dict(body_id=x[0],canonical_name=x[1],body_class=x[2],parent_body_id=x[3] or None,body_status=x[4],authority=x[5],identifier_type=x[6],identifier_value=x[7],identifier_status=x[8]))
    b={}
    for r in rows:b.setdefault(r['body_id'],{k:r[k] for k in ('body_id','canonical_name','body_class','parent_body_id','body_status')}).setdefault('identifiers',[]).append({k:r[k] for k in ('authority','identifier_type','identifier_value','identifier_status')})
    return b
bodies=load_identities()
naif={}
for b in bodies.values():
    for i in ordered(b['identifiers']):
        if i['authority']=='NAIF' and i['identifier_type']=='NAIF_ID' and i['identifier_status']=='ACTIVE':
            naif.setdefault(i['identifier_value'],[]).append(b['body_id'])
def stable_id(payload):return hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
if OUT.exists():raise SystemExit(f'refusing to overwrite {OUT}')
c=sqlite3.connect(OUT);c.execute('pragma foreign_keys=on')
c.executescript('''
CREATE TABLE meta(key TEXT PRIMARY KEY,value TEXT NOT NULL);
CREATE TABLE authority_body_ref(body_id TEXT PRIMARY KEY,canonical_name TEXT NOT NULL,body_class TEXT NOT NULL,parent_body_id TEXT,authority TEXT NOT NULL,source_snapshot_sha256 TEXT NOT NULL);
CREATE TABLE body_identifier_ref(body_id TEXT NOT NULL REFERENCES authority_body_ref(body_id),authority TEXT NOT NULL,identifier_type TEXT NOT NULL,identifier_value TEXT NOT NULL,identifier_status TEXT NOT NULL,PRIMARY KEY(body_id,authority,identifier_type,identifier_value));
CREATE TABLE source_artifact(artifact_id TEXT PRIMARY KEY,authority TEXT NOT NULL,product TEXT NOT NULL,source_url TEXT NOT NULL,version TEXT,acquired_at_utc TEXT NOT NULL,sha256 TEXT NOT NULL,byte_count INTEGER NOT NULL,media_type TEXT NOT NULL);
CREATE TABLE identity_crosswalk(crosswalk_id TEXT PRIMARY KEY,source_artifact_id TEXT NOT NULL REFERENCES source_artifact(artifact_id),external_id_scheme TEXT NOT NULL,external_id TEXT NOT NULL,body_id TEXT REFERENCES authority_body_ref(body_id),match_basis TEXT NOT NULL,disposition TEXT NOT NULL,notes TEXT NOT NULL);
CREATE TABLE candidate_assertion(assertion_id TEXT PRIMARY KEY,body_id TEXT NOT NULL REFERENCES authority_body_ref(body_id),property_code TEXT NOT NULL,reported_value TEXT NOT NULL,reported_unit TEXT,reported_uncertainty TEXT,normalized_value TEXT,normalized_unit TEXT,normalized_uncertainty TEXT,normalization_method TEXT,epistemic_class TEXT NOT NULL CHECK(epistemic_class IN ('DIRECT_SAMPLE','IN_SITU_DIRECT','IN_SITU_REMOTE','EARTH_REMOTE','DYNAMICAL_INFERENCE','ANALOG_INFERENCE','PHYSICAL_MODEL','THEORETICAL_EXPECTATION','DERIVED','UNKNOWN')),source_value_kind TEXT NOT NULL,scope TEXT NOT NULL,source_artifact_id TEXT NOT NULL REFERENCES source_artifact(artifact_id),source_lineage TEXT NOT NULL,source_reference TEXT,source_payload_json TEXT NOT NULL CHECK(json_valid(source_payload_json) AND json_extract(source_payload_json,'$.loom_body_id')=body_id),fact_status TEXT NOT NULL CHECK(fact_status='CANDIDATE'),preferred_fact INTEGER NOT NULL CHECK(preferred_fact=0),disposition TEXT NOT NULL CHECK(disposition IN ('CANDIDATE','HOLD','REJECT')));
CREATE TABLE coverage(body_id TEXT NOT NULL REFERENCES authority_body_ref(body_id),property_code TEXT NOT NULL,disposition TEXT NOT NULL,reason TEXT NOT NULL,assertion_count INTEGER NOT NULL,PRIMARY KEY(body_id,property_code));
CREATE INDEX candidate_assertion_body_property_idx ON candidate_assertion(body_id,property_code);
''')
snapshot_sha=sha(RAW/'loom_solar_identity_snapshot.tsv')
for b in ordered(sorted(bodies.values(),key=lambda x:x['body_id'])):
    c.execute('insert into authority_body_ref values(?,?,?,?,?,?)',(b['body_id'],b['canonical_name'],b['body_class'],b['parent_body_id'],'loom_solar.body',snapshot_sha))
    for i in ordered(b['identifiers']):c.execute('insert into body_identifier_ref values(?,?,?,?,?)',(b['body_id'],i['authority'],i['identifier_type'],i['identifier_value'],i['identifier_status']))
# frozen artifact metadata. Acquisition times are file capture times from this run.
artifacts={}
def add_artifact(file,authority,product,url,version,media):
    p=RAW/file
    if not p.exists():return None
    aid=sha(p)
    if aid not in artifacts:
        artifacts[aid]={'file':file,'authority':authority,'product':product,'url':url,'version':version,'acquired':datetime.fromtimestamp(p.stat().st_mtime,timezone.utc).isoformat(),'sha':aid,'size':p.stat().st_size,'media':media}
        c.execute('insert into source_artifact values(?,?,?,?,?,?,?,?,?)',(aid,authority,product,url,version,artifacts[aid]['acquired'],aid,p.stat().st_size,media))
    return aid
def assertion(body,prop,reported,unit,unc,normalized,nunit,nunc,method,epistemic,scope,aid,lineage,ref,payload,disp='CANDIDATE'):
    # Preserve an explicit body binding in every source envelope. If a caller
    # supplied a contradictory binding, the table CHECK constraint rejects it.
    payload=dict(payload)
    payload.setdefault('loom_body_id',body)
    p={'body':body,'property':prop,'source_artifact':aid,'lineage':lineage,'reported':reported,'source_ref':ref}
    aidrow=stable_id(p)
    source_kind='MODEL_COEFFICIENT' if epistemic=='PHYSICAL_MODEL' else ('DERIVED_PARAMETER' if epistemic=='DERIVED' else ('REFERENCE_CONSTANT' if epistemic=='DYNAMICAL_INFERENCE' or prop=='TRIAXIAL_RADII' else 'COMPILED_REFERENCE_PARAMETER'))
    c.execute('insert or ignore into candidate_assertion values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',(aidrow,body,prop,str(reported),unit,unc,normalized,nunit,nunc,method,epistemic,source_kind,scope,aid,lineage,ref,json.dumps(payload,sort_keys=True,ensure_ascii=False), 'CANDIDATE',0,disp))
def resolve_naif(idv):
    v=str(idv); owners=naif.get(v,[])
    if owners:
        out=[]
        for body in owners:
            b=bodies[body]
            if ((b['body_class']=='BINARY_ASTEROID_PRIMARY' and 20_000_001<=int(v)<=49_999_999) or (v in NAIF_BARYCENTER_IDS and b['body_class']!='BARYCENTER')):
                out.append((body,'EXACT_NAIF_ID','HOLD','NAIF identifier semantics denote a system barycenter; LOOM body class is not BARYCENTER'))
            else:out.append((body,'EXACT_NAIF_ID','MATCH','exact NAIF identifier'))
        return out
    n=int(v)
    legacy=None
    if 20_000_001<=n<=49_999_999:legacy=str(2_000_000+(n-20_000_000))
    elif 2_000_001<=n<=2_999_999:legacy=str(20_000_000+(n-2_000_000))
    if legacy:
        out=[]
        for body in naif.get(legacy,[]):
            if bodies[body]['body_class']!='BINARY_ASTEROID_PRIMARY':
                out.append((body,'NAIF_NUMBERED_ASTEROID_LEGACY_EXTENDED_ALIAS','MATCH','arithmetic alias explicitly defined by NAIF; exact object identifier validated'))
        return out
    return []
def add_crosswalk(aid,scheme,eid,body,basis,disp='MATCH',notes=''):
    key=stable_id({'artifact':aid,'scheme':scheme,'external_id':str(eid),'body':body,'basis':basis,'disposition':disp})
    c.execute('insert or ignore into identity_crosswalk values(?,?,?,?,?,?,?,?)',(key,aid,scheme,str(eid),body,basis,disp,notes))
def add_spice(file):
    aid=add_artifact(file,'JPL/NAIF','generic PCK/GM text kernel',f'https://naif.jpl.nasa.gov/pub/naif/generic_kernels/pck/{file}', 'pck00011-n0066' if file.startswith('pck') else 'DE440 GM kernel','text/plain')
    text=(RAW/file).read_text(errors='replace')
    pat=re.compile(r'^\s*BODY(-?\d+)_([A-Z0-9_]+)\s*=\s*(\([^)]*\)|[^\n]+)',re.M|re.S)
    known={'RADII':('TRIAXIAL_RADII','km','UNKNOWN','VECTOR_IDENTITY'),'GM':('GM','km^3/s^2','DYNAMICAL_INFERENCE','SCALAR'),'POLE_RA':('POLE_RIGHT_ASCENSION_MODEL','deg','PHYSICAL_MODEL','VECTOR_IDENTITY'),'POLE_DEC':('POLE_DECLINATION_MODEL','deg','PHYSICAL_MODEL','VECTOR_IDENTITY'),'PM':('PRIME_MERIDIAN_MODEL','component-specific angular/time units; see source kernel definition','PHYSICAL_MODEL','VECTOR_IDENTITY'),'LONG_AXIS':('LONG_AXIS','deg','PHYSICAL_MODEL','SCALAR')}
    for m in ordered(list(pat.finditer(text))):
        bid=m.group(1);var=m.group(2);raw=m.group(3).strip()
        if var not in known:continue
        resolutions=resolve_naif(bid)
        if len(resolutions)!=1:continue
        body,basis,disp,reason=resolutions[0]
        add_crosswalk(aid,'NAIF_ID',bid,body,basis,disp,reason)
        prop,unit,eclass,normmode=known[var]
        value=raw[1:-1].strip() if raw.startswith('(') and raw.endswith(')') else raw
        vals=re.findall(r'[+-]?(?:\d+\.?\d*|\.\d+)(?:[Ee][+-]?\d+)?',value)
        nv=(str(Decimal(vals[0])) if prop=='GM' and len(vals)==1 else json.dumps([str(Decimal(x)) for x in vals],separators=(',',':'))) if vals and len(' '.join(vals))==len(' '.join(value.split())) else None
        assertion(body,prop,raw,unit,None,nv,None if prop in ('POLE_RIGHT_ASCENSION_MODEL','POLE_DECLINATION_MODEL','PRIME_MERIDIAN_MODEL') else unit,None,'parse numeric tuple without unit conversion' if nv else 'none',eclass,'BODY_IDENTITY',aid,f'NAIF:{file}:{bid}:{var}',None,{'loom_body_id':body,'naif_id':bid,'kernel_variable':var,'reported_expression':raw,'normalized_coefficients':json.loads(nv) if nv else None},'HOLD' if disp=='HOLD' else 'CANDIDATE')
add_artifact('loom_solar_identity_snapshot.tsv','LOOM/PostgreSQL','loom_solar.body + body_identifier identity snapshot','local governed PostgreSQL loom_dev; source authority is current main migration-backed identity state','origin/main d85b260e51ffebd936cb83b85d0594fd07b9405c','text/tab-separated-values')
add_artifact('naif_ids_required_reading.html','JPL/NAIF','NAIF Integer ID codes Required Reading','https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/C/req/naif_ids.html','revised 2021-12-10','text/html')
add_artifact('jpl_sbdb_api_doc.html','NASA/JPL SSD','SBDB API documentation','https://ssd-api.jpl.nasa.gov/doc/sbdb.html','published API docs; live signature recorded separately','text/html')
add_artifact('jpl_sbdb_query_api_doc.html','NASA/JPL SSD','SBDB Query API documentation','https://ssd-api.jpl.nasa.gov/doc/sbdb_query.html','published API docs; live signature recorded separately','text/html')
add_artifact('jpl_sbdb_api_field_metadata.json','NASA/JPL SSD','SBDB API field metadata','https://ssd-api.jpl.nasa.gov/sbdb_query.api?info=field','live response signature 1.3','application/json')
add_artifact('jpl_sbdb_api_count_snapshot.json','NASA/JPL SSD','SBDB API count snapshot','https://ssd-api.jpl.nasa.gov/sbdb_query.api?info=count','live response signature 1.3','application/json')
add_spice('pck00011_n0066.tpc');add_spice('gm_de440.tpc')
# SBDB. Only phys_par fields; orbit remains untouched raw source context.
m=json.loads((REPORTS/'sbdb_identity_crosswalk.json').read_text())
for rec in ordered(m['records']):
    file=rec['artifact'];aid=add_artifact(file,'NASA/JPL SSD','SBDB API exact-SPK object response',rec.get('source_url') or rec.get('url'),'1.3','application/json')
    obj=json.loads((RAW/file).read_text()); body=rec['body_id']
    if str((obj.get('object') or {}).get('spkid'))!=str(rec.get('object_spkid') or rec.get('spk_id')):raise ValueError('SBDB response identity mismatch')
    add_crosswalk(aid,'NAIF_ID',rec['spk_id'],body,rec.get('crosswalk_basis','EXACT_NAIF_ID'),rec.get('crosswalk_disposition','MATCH'),rec.get('hold_reason') or rec.get('first_pass') or '')
    sbdb_disposition='HOLD' if rec.get('crosswalk_disposition')=='HOLD' else 'CANDIDATE'
    for x in ordered(obj.get('phys_par') or []):
        name=x.get('name');raw=x.get('value')
        if raw is None:continue
        mapping={'H':('ABSOLUTE_MAGNITUDE',None),'G':('MAGNITUDE_SLOPE_PARAMETER',None),'M1':('COMET_MAGNITUDE_PARAMETER',None),'K1':('COMET_MAGNITUDE_PARAMETER',None),'M2':('COMET_MAGNITUDE_PARAMETER',None),'K2':('COMET_MAGNITUDE_PARAMETER',None),'PC':('COMET_MAGNITUDE_PARAMETER',None),'diameter':('EFFECTIVE_DIAMETER','km'),'extent':('TRIAXIAL_DIMENSIONS','km'),'GM':('GM','km^3/s^2'),'density':('BULK_DENSITY','g/cm^3'),'rot_per':('ROTATION_PERIOD','h'),'pole':('POLE_ORIENTATION','deg'),'albedo':('GEOMETRIC_ALBEDO',None),'spec_T':('SPECTRAL_CLASS','text'),'spec_B':('SPECTRAL_CLASS','text'),'BV':('COLOR_INDEX','mag'),'UB':('COLOR_INDEX','mag'),'IR':('COLOR_INDEX','mag')}
        if name not in mapping:continue
        prop,defaultunit=mapping[name];unit=x.get('units') or defaultunit
        norm,unc=parse_numeric(raw)
        if name in ('extent','spec_T','spec_B','pole'):norm=None
        norm_unc=parse_numeric(x.get('sigma') or '')[0] if x.get('sigma') and name not in ('extent','spec_T','spec_B','pole') else None
        ref=x.get('ref');lineage=f"SBDB:{rec['spk_id']}:{ref or 'unreferenced'}:{name}"
        epistemic='UNKNOWN'
        assertion(body,prop,raw,unit,x.get('sigma'),norm,unit,norm_unc,'decimal parse, reported unit retained' if norm else 'none',epistemic,'BODY',aid,lineage,ref,x,sbdb_disposition)
# Planet/dwarf table: deterministic exact canonical-name + class match; only these two classes.
planet_file='jpl_planet_physical_parameters.html'; aid=add_artifact(planet_file,'NASA/JPL SSD','Planetary Physical Parameters HTML', 'https://ssd.jpl.nasa.gov/planets/phys_par.html','mutable page snapshot','text/html')
p=Tables();p.feed((RAW/planet_file).read_text(errors='replace'))
propmap={'Equatorial Radius':('EQUATORIAL_RADIUS','km'),'Mean Radius':('MEAN_RADIUS','km'),'Mass':('MASS','10^24 kg or 10^18 kg, table section specific'),'Bulk Density':('BULK_DENSITY','g/cm^3'),'Sidereal Rotation Period':('ROTATION_PERIOD','d'),'V(1,0)':('ABSOLUTE_VISUAL_MAGNITUDE_V1_0','mag'),'Geometric Albedo':('GEOMETRIC_ALBEDO',None)}
headers=[];section=None
for row in p.rows:
    if 'Planet' in row[0] or 'Dwarf Planet' in row[0]:
        section='DWARF_PLANET' if 'Dwarf' in row[0] else 'PLANET'
        headers=row;continue
    if not row or len(row)<8:continue
    name=row[0];owners=[b for b in bodies.values() if canon(b['canonical_name'])==canon(name) and b['body_class']==section]
    if len(owners)!=1:continue
    body=owners[0]['body_id']
    add_crosswalk(aid,'JPL_CANONICAL_NAME_AND_BODY_CLASS',name,body,'exact canonical name + source table class','MATCH','Planetary table has names but no body code; class bounds collision risk')
    for idx,h in enumerate(ordered(list(enumerate(headers[1:],start=1))),start=0):
        idx,h=h
        h=re.sub(r'\s+','',h).casefold()
        hmap={'equatorialradius':'Equatorial Radius','meanradius':'Mean Radius','mass':'Mass','bulkdensity':'Bulk Density','siderealrotationperiod':'Sidereal Rotation Period','v(1,0)':'V(1,0)','geometricalbedo':'Geometric Albedo'}
        h=hmap.get(h,h)
        if h not in propmap or idx>=len(row):continue
        raw=row[idx]
        if not raw.strip() or raw.strip() in ('—','–','n/a'):continue
        prop,unit=propmap[h];norm,unc=parse_numeric(raw)
        if prop=='MASS':unit='10^24 kg' if section=='PLANET' else '10^18 kg'
        ep='DERIVED' if prop=='BULK_DENSITY' else 'UNKNOWN'
        assertion(body,prop,raw,unit,unc,norm,unit,unc,'deterministic table scalar parse; original section unit retained without scale conversion' if norm else 'none',ep,'BODY',aid,f'JPL:PLANET_PHYS:{name}:{h}',re.search(r'\[([^\]]+)\]',raw).group(1) if re.search(r'\[([^\]]+)\]',raw) else None,{'row':row,'column':h,'reported_cell':raw,'table_header':headers,'section':section,'source_unit':unit})
# Satellite physical parameter table: match only its numeric NAIF code field.
sat_file='jpl_satellite_physical_parameters.html'; sat_aid=add_artifact(sat_file,'NASA/JPL SSD','Planetary Satellite Physical Parameters HTML','https://ssd.jpl.nasa.gov/sats/phys_par/','mutable page snapshot','text/html')
s=Tables();s.feed((RAW/sat_file).read_text(errors='replace'))
for row in ordered(s.rows):
    if len(row)<12 or not row[2].strip().isdigit():continue
    resolutions=resolve_naif(row[2])
    if len(resolutions)!=1:continue
    body,basis,disp,reason=resolutions[0]
    add_crosswalk(sat_aid,'NAIF_SATELLITE_CODE',row[2],body,basis,disp,reason)
    # code, GM value/sigma/ref, radius value/sigma/ref, density value/sigma/ref
    for prop,value,sigma,unit,ref in [('GM',row[3],row[4],'km^3/s^2',row[5]),('MEAN_RADIUS',row[6],row[7],'km',row[8]),('BULK_DENSITY',row[9],row[10],'g/cm^3',row[11])]:
        if not value or value.strip() in ('n/a','—','–'):continue
        norm,lim_unc=parse_numeric(value)
        reported_unc=sigma if sigma and sigma.lower()!='n/a' else lim_unc
        ep='DERIVED' if prop=='BULK_DENSITY' else ('DYNAMICAL_INFERENCE' if prop=='GM' else 'UNKNOWN')
        assertion(body,prop,value,unit,reported_unc,norm,unit,reported_unc,'deterministic scalar parse; reported uncertainty retained' if norm else 'none',ep,'BODY',sat_aid,f'JPL:SAT_PHYS:{row[2]}:{prop}:{ref}',ref,{'row':row,'reported_value':value,'reported_sigma':reported_unc,'reference':ref},'HOLD' if disp=='HOLD' else 'CANDIDATE')
# coverage matrix
properties=['GM','MASS','VOLUME','EFFECTIVE_DIAMETER','MEAN_RADIUS','EQUATORIAL_RADIUS','TRIAXIAL_DIMENSIONS','TRIAXIAL_RADII','BULK_DENSITY','GEOMETRIC_ALBEDO','ABSOLUTE_MAGNITUDE','ABSOLUTE_VISUAL_MAGNITUDE_V1_0','ROTATION_PERIOD','POLE_ORIENTATION','POLE_RIGHT_ASCENSION_MODEL','POLE_DECLINATION_MODEL','PRIME_MERIDIAN_MODEL','SPECTRAL_CLASS']
assertions=c.execute("select body_id,property_code,sum(case when disposition='CANDIDATE' then 1 else 0 end),count(*) from candidate_assertion group by body_id,property_code").fetchall()
counts={(b,p):(accepted,total) for b,p,accepted,total in assertions}
for body,b in ordered(sorted(bodies.items())):
    cls=b['body_class']; identifiers=b['identifiers']
    naif_ids=[i['identifier_value'] for i in identifiers if i['authority']=='NAIF' and i['identifier_type']=='NAIF_ID' and i['identifier_status']=='ACTIVE']
    id_state='AMBIGUOUS_IDENTITY' if c.execute("select count(*) from identity_crosswalk where body_id=? and disposition='HOLD'",(body,)).fetchone()[0]>0 else ('SOURCE_NOT_FOUND' if not naif_ids else None)
    for prop in properties:
        accepted,total=counts.get((body,prop),(0,0))
        n=total
        if accepted:disp='SUPPORTED';reason='one or more authoritative candidate assertions acquired; any held alternatives remain separately dispositioned'
        elif total:disp='AMBIGUOUS_IDENTITY';reason='evidence retained, but source identity is held and is not attributed to this body'
        elif id_state:disp=id_state;reason='identity crosswalk incomplete or ambiguous'
        elif cls in SMALL and prop in ('GM','MASS','VOLUME','EFFECTIVE_DIAMETER','TRIAXIAL_DIMENSIONS','BULK_DENSITY','ROTATION_PERIOD','POLE_ORIENTATION','SPECTRAL_CLASS','ABSOLUTE_MAGNITUDE','GEOMETRIC_ALBEDO'):disp='SOURCE_NOT_PRESENT';reason='exact-ID source response/artifact was acquired, but this field was not present in its returned data'
        elif cls=='NATURAL_SATELLITE' and prop in ('GM','MASS','VOLUME','MEAN_RADIUS','BULK_DENSITY','TRIAXIAL_RADII','POLE_RIGHT_ASCENSION_MODEL','POLE_DECLINATION_MODEL','PRIME_MERIDIAN_MODEL'):disp='SOURCE_NOT_PRESENT';reason='acquired JPL/NAIF products do not contain this body/property field'
        elif cls in ('PLANET','DWARF_PLANET') and prop in ('GM','MASS','VOLUME','MEAN_RADIUS','EQUATORIAL_RADIUS','BULK_DENSITY','ROTATION_PERIOD','GEOMETRIC_ALBEDO','ABSOLUTE_MAGNITUDE','POLE_RIGHT_ASCENSION_MODEL','POLE_DECLINATION_MODEL','PRIME_MERIDIAN_MODEL'):disp='SOURCE_NOT_PRESENT';reason='selected JPL reference product does not contain a value for this field'
        elif cls in ('BARYCENTER','SPACECRAFT','STAR'):disp='NOT_APPLICABLE';reason='baseline physical-body parameter mapping is not applicable to barycenter/spacecraft/star identity'
        else:disp='SOURCE_DOES_NOT_COVER_BODY_CLASS';reason='no selected corpus provides this class/property pairing'
        c.execute('insert into coverage values(?,?,?,?,?)',(body,prop,disp,reason,n))
# audit and metadata
c.execute('insert into meta values(?,?)',('mission_id','SOLAR-BASELINE-01'))
c.execute('insert into meta values(?,?)',('source_identity_authority','loom_solar.body; live loom_dev snapshot'))
c.execute('insert into meta values(?,?)',('identity_snapshot_sha256',snapshot_sha))
c.execute('insert into meta values(?,?)',('promoted_sf03_database_sha256','f25681e27ec3beb320c4983f4a59436f8471e8322208157039be0d21ecea6f53'))
c.execute('insert into meta values(?,?)',('promoted_sf03_semantic_digest','382f7871cdfc42526eddcc84bd17fcfdd1a6a78cafa129c5feb21546cdfa8581'))
c.commit()
# reports
art_meta=[dict(artifact_id=k,**v) for k,v in artifacts.items()]
assertion_total=c.execute('select count(*) from candidate_assertion').fetchone()[0]
coverage_counts={f'{cls}:{prop}:{disp}':n for cls,prop,disp,n in c.execute('select b.body_class,c.property_code,c.disposition,count(*) from coverage c join authority_body_ref b using(body_id) group by 1,2,3 order by 1,2,3')}
class_counts={cls:{'bodies':n,'bodies_with_candidate_assertions':c.execute("select count(distinct x.body_id) from candidate_assertion x join authority_body_ref b using(body_id) where b.body_class=? and x.disposition='CANDIDATE'",(cls,)).fetchone()[0],'bodies_with_held_assertions':c.execute("select count(distinct x.body_id) from candidate_assertion x join authority_body_ref b using(body_id) where b.body_class=? and x.disposition='HOLD'",(cls,)).fetchone()[0]} for cls,n in c.execute('select body_class,count(*) from authority_body_ref group by body_class order by body_class')}
prop_counts={prop:{'assertions':n,'bodies':b} for prop,n,b in c.execute('select property_code,count(*),count(distinct body_id) from candidate_assertion group by property_code order by property_code')}
for prop in properties:prop_counts.setdefault(prop,{'assertions':0,'bodies':0})
db_sha=sha(OUT)
report={'mission_id':'SOLAR-BASELINE-01','verdict':'CANDIDATE_BUILD_PENDING_QUALIFICATION','baseline_path':OUT.name,'database_sha256':db_sha,'identity':{'body_count':len(bodies),'all_active_body_ids_matched_to_snapshot':len(bodies),'external_id_coverage':'NAIF/MPC identifiers preserved exactly','source_identity_snapshot_sha256':snapshot_sha,'unresolved_exact_identities':['DIDYMOS','EURYBATES','KLEOPATRA','PATROCLUS']},'by_body_class':class_counts,'by_property':prop_counts,'coverage_dispositions_by_class_property':coverage_counts,'candidate_assertions':assertion_total,'accepted_assertions':c.execute("select count(*) from candidate_assertion where disposition='CANDIDATE'").fetchone()[0],'held_assertions':c.execute("select count(*) from candidate_assertion where disposition='HOLD'").fetchone()[0],'rejected_assertions':c.execute("select count(*) from candidate_assertion where disposition='REJECT'").fetchone()[0],'preferred_fact_total':0,'source_artifacts':art_meta,'source_artifact_count':len(art_meta),'insertion_order':'REVERSE' if REVERSE else 'CANONICAL','schema_change':'NONE','phase4_ephemeris_ingested':False,'identity_crosswalk_count':c.execute('select count(*) from identity_crosswalk').fetchone()[0],'identity_crosswalk_dispositions':{r[0]:r[1] for r in c.execute('select disposition,count(*) from identity_crosswalk group by disposition order by disposition')},'all_facts_status':'CANDIDATE','note':'The authority identity snapshot is a frozen reference, not a new or competing body identity authority.'}
(REPORTS/'baseline_build_report.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
print(json.dumps({'database':str(OUT),'sha256':db_sha,'bodies':len(bodies),'assertions':assertion_total,'artifacts':len(art_meta),'classes':class_counts,'properties':prop_counts},sort_keys=True))
c.close()
