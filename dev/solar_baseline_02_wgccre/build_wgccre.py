#!/usr/bin/env python3
"""Offline deterministic WGCCRE table adapter for existing Solar Baseline bodies."""
from __future__ import annotations
import hashlib,json,re,sqlite3,sys,time,shutil,os
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[2]; HERE=Path(__file__).resolve().parent; RAW=HERE/'raw'
INPUT=ROOT/'dev/solar_baseline_01/LOOM_SOLAR_BASELINE_01_CANDIDATE_V20.sqlite3'
OUTPUT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else HERE/'LOOM_SOLAR_BASELINE_02_WGCCRE_CANDIDATE_V10.sqlite3'
REPORT=HERE/'reports'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def stable(obj):return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def fold(s):return re.sub(r'\s+',' ',s).strip()
if OUTPUT.exists():raise SystemExit(f'refusing to overwrite {OUTPUT}')
main=RAW/'WGCCRE_2015_report_USGS_d9wret.txt'
source_freeze=json.loads((REPORT/'source_acquisition.json').read_text())
source_by_doi={x.get('doi'):x for x in source_freeze['sources']}
text=main.read_text(); db=sqlite3.connect(INPUT);db.row_factory=sqlite3.Row
bodies={r['body_id']:dict(r) for r in db.execute('select * from authority_body_ref')}
# Each table is isolated before any name-based parsing; exact table boundaries are frozen source structure.
t1_start=text.index('Sun           α0')
t1=text[t1_start:text.index('Table 2 Recommended values')]
t2_start=text.index('Earth:              Moon',text.index('Table 2 Recommended values'))
t2=text[t2_start:text.index('3 The lunar coordinate system',t2_start)]
t3_title=text.index('Table 3 Recommended rotation values')
t3_start=text.index('(1) Ceres',t3_title)
t3=text[t3_start:text.index('Table 4 Size and shape parameters',t3_start)]
# Canonical property labels retain complete equations; no formula evaluation occurs.
label_re=re.compile(r'(?m)(?<![\w])\s*(α\s*0|α0|α\s*[XYZ]|δ\s*0|δ0|δ\s*[XYZ]|δ\s*=|W\s*\u0307?\s*=)')
def records_in_segment(seg,allowed,table):
    hits=[]
    # Exact canonical body names for satellites/planets. Minor-body report rows are separately protected by numeric designation.
    for bid,b in allowed.items():
        nm=b['canonical_name']
        if b['body_class']=='NATURAL_SATELLITE': aliases=[nm]
        elif b['body_class'] in ('PLANET','STAR'): aliases=[nm]
        else:
            ids=[r[0] for r in db.execute("select identifier_value from body_identifier_ref where body_id=? and authority='NAIF' and identifier_type='NAIF_ID' and identifier_status='ACTIVE'",(bid,))]
            nums=[int(v)-20_000_000 for v in ids if v.isdigit() and 20_000_001<=int(v)<=29_999_999]
            m=re.match(r'^(\d+)\s+',nm)
            if nums and b['body_class'] not in ('COMET',): aliases=[f'({nums[0]}) '+(nm.split(' ',1)[1] if m else nm)]
            else:
             if b['body_class']=='DWARF_PLANET' and nm=='Pluto': aliases=['(134340) Pluto']
             elif b['body_class']=='COMET' and '/' in nm: aliases=[nm.split('/',1)[0]]
             else: aliases=[]
        for alias in aliases:
            pat=re.compile(r'(?<![\w])'+re.escape(alias)+r'(?![\w])',re.I)
            for match in pat.finditer(seg):
                line_start=seg.rfind('\n',0,match.start())+1; prefix=seg[line_start:match.start()].strip()
                if table=='TABLE_1' and prefix: continue
                if table=='TABLE_2' and prefix and not re.fullmatch(r'(?:(?:Earth|Mars|Jupiter|Saturn|Uranus|Neptune)\s*:?\s*(?:[IVXLCDM]+)?|[IVXLCDM]+)',prefix,re.I): continue
                if table=='TABLE_3' and prefix and not re.fullmatch(r'(?:\(\d+\)\s*Pluto\s*:\s*I|\(\d+\))',prefix,re.I): continue
                hits.append((match.start(),match.end(),bid,alias))
    hits.sort()
    result={}
    for i,(start,end,bid,alias) in enumerate(hits):
        # Only accept a table row if an orientation field follows the matched identity before the next recognized identity.
        stop=hits[i+1][0] if i+1<len(hits) else min(len(seg),start+1800)
        if table=='TABLE_3':
            blank=re.search(r'\n\s*\n',seg[end:stop])
            if blank:stop=min(stop,end+blank.start())
        block=seg[end:stop]
        if not re.search(r'(?m)(?<![\w])\s*(?:α\s*0|α0|δ\s*0|δ0|δ\s*=|W\s*=)',block):continue
        # Exclude prose references; retain first true row for this identity.
        if bid not in result:result[bid]=(alias,block,start)
    return result
allowed={k:v for k,v in bodies.items() if v['body_class'] in ('PLANET','STAR','NATURAL_SATELLITE','ASTEROID','NEAR_EARTH_ASTEROID','TROJAN_ASTEROID','BINARY_ASTEROID_PRIMARY','COMET','DWARF_PLANET','CENTAUR','TRANS_NEPTUNIAN_OBJECT','INTERSTELLAR_OBJECT')}
rows={}
for tab,sub in [('TABLE_1',t1),('TABLE_2',t2),('TABLE_3',t3)]:
 # satellites are parent-scoped and exact canonical name is required. Minor bodies use numbered designations.
 if tab=='TABLE_1': selection={k:v for k,v in allowed.items() if v['body_class'] in ('PLANET','STAR')}
 elif tab=='TABLE_2': selection={k:v for k,v in allowed.items() if v['body_class']=='NATURAL_SATELLITE'}
 else: selection={k:v for k,v in allowed.items() if v['body_class'] in ('ASTEROID','NEAR_EARTH_ASTEROID','TROJAN_ASTEROID','BINARY_ASTEROID_PRIMARY','COMET','DWARF_PLANET','CENTAUR','TRANS_NEPTUNIAN_OBJECT','INTERSTELLAR_OBJECT') or k=='CHARON'}
 parsed_records=records_in_segment(sub,selection,tab)
 for bid,(alias,block,match_start) in parsed_records.items():
  if bid in rows: continue
  # Row-boundary guard requires source expression for at least two fields. Whole field continuation is kept as opaque text.
  fields=[]
  matches=list(label_re.finditer(block))
  for j,m in enumerate(matches):
   label=re.sub(r'\s+','',m.group(1))
   prop={'α0':'POLE_RIGHT_ASCENSION_MODEL','α':'POLE_RIGHT_ASCENSION_MODEL','δ0':'POLE_DECLINATION_MODEL','δ':'POLE_DECLINATION_MODEL','W=':'PRIME_MERIDIAN_MODEL','Ẇ=':'PRIME_MERIDIAN_RATE_MODEL'}.get(label)
   if prop is None: continue
   end=matches[j+1].start() if j+1<len(matches) else len(block)
   raw=block[m.end():end]
   raw=re.split(r'\n\s*\([a-z]\)\s+(?:The|Since|Although|Values|These)\b',raw)[0]
   raw=re.split(r'(?i)\s+EPOXI\s+Closest\s+Approach',raw)[0]
   raw=re.split(r'(?i)\s+123\s+\d+\s+Page\b',raw)[0]
   raw=re.split(r'(?i)\s+Table\s+[123]\s+continued',raw)[0]
   raw=fold(raw.strip(' =:;\n\r'))
   raw=re.sub(r'\s+\([a-z]\)\s*$','',raw)
   raw=re.sub(r'\s+(?:I|II|III|IV|V|VI|VII|VIII|IX|X|XI|XII|XIII|XIV|XV|XVI)\s*$','',raw)
   if not raw:continue
   fields.append((prop,raw))
  seen={}
  for prop,raw in fields:
   if prop not in seen:seen[prop]=raw
   elif bid=='TEMPEL1' and prop=='PRIME_MERIDIAN_MODEL':seen[prop]=seen[prop]+'; SECOND EPOCH MODEL: '+raw
  if bid=='TEMPEL1' and 'PRIME_MERIDIAN_MODEL' in seen:
   seen['PRIME_MERIDIAN_MODEL']='Complete two-epoch Table 3 row: '+fold(block).lstrip('/ ')
   if 'PRIME_MERIDIAN_RATE_MODEL' in seen:seen['PRIME_MERIDIAN_RATE_MODEL']='Complete two-epoch rotation-rate context: '+fold(block).lstrip('/ ')
  # For Table 3 comets with partial orientation, retain only actual supplied model components; >=1 qualifies.
  if tab=='TABLE_2':
   body=bodies[bid]; parent_id=body['parent_body_id']
   if not parent_id: continue
   parent=bodies.get(parent_id,{}).get('canonical_name','').replace(' system barycenter','')
   headings=list(re.finditer(r'(?mi)^\s*(Earth|Mars|Jupiter|Saturn|Uranus|Neptune)\s*:?\s*(?:[IVXLCDM]+)?',sub[:match_start]))
   if not headings or headings[-1].group(1).casefold()!=parent.casefold(): continue
  if seen and (bid not in rows or len(seen)>len(rows[bid]['fields'])):
   rows[bid]={'table':tab,'alias':alias,'fields':seen,'raw_block':block[:1600]}
# Correction explicitly supersedes the legacy Phobos prime-meridian equation.
# Keep 2015 source assertion as historical HOLD and add the corrected equation as candidate.
# A separate 2019 source artifact preserves the correction lineage.
correction_excerpt=(HERE/'derived/WGCCRE_2019_Phobos_correction_excerpt.txt').read_text()
corrected=re.search(r'(?ms)^W\s*=\s*(.*?)\n\nSource:',correction_excerpt)
if not corrected: raise ValueError('frozen 2019 Phobos correction excerpt formula not found')
corrected_phobos=fold(corrected.group(1))
shutil.copy2(INPUT,OUTPUT)
c=sqlite3.connect(OUTPUT);c.execute('pragma foreign_keys=on')
pdf_main=RAW/'WGCCRE_2015_report_USGS_d9wret.pdf';main_source=source_by_doi['10.1007/s10569-017-9805-5'];correction_source=source_by_doi['10.1007/s10569-019-9925-1']
main_id=sha(pdf_main);corr_id=correction_source['acquired_artifact_sha256']
if main_id!=main_source['sha256']:raise ValueError('WGCCRE 2015 report hash differs from frozen acquisition manifest')
if sha(HERE/'derived/WGCCRE_2019_Phobos_correction_excerpt.txt')!=correction_source['frozen_derivative_sha256']:raise ValueError('frozen corrigendum excerpt hash differs from source manifest')
c.execute('insert into source_artifact values(?,?,?,?,?,?,?,?,?)',(main_id,'IAU WGCCRE / USGS Astrogeology','Report of the IAU Working Group on Cartographic Coordinates and Rotational Elements: 2015; official USGS public-domain reprint','https://www.usgs.gov/media/files/report-iau-working-group','2015 report; reprint as PDF; doi:10.1007/s10569-017-9805-5',main_source['acquired_at_utc'],main_id,pdf_main.stat().st_size,'application/pdf'))
c.execute('insert into source_artifact values(?,?,?,?,?,?,?,?,?)',(corr_id,'IAU WGCCRE / Springer','Correction to: Report of the IAU Working Group on Cartographic Coordinates and Rotational Elements: 2015','https://link.springer.com/article/10.1007/s10569-019-9925-1','published 2019-12-02; doi:10.1007/s10569-019-9925-1',correction_source['acquired_at_utc'],corr_id,correction_source['acquired_bytes'],'application/pdf'))
crosswalks=[]; assertions=[]; rejected=[]
def add_record(body,table,alias,fields,artifact,edition,corrected=False,source_context=''):
 b=bodies[body]; match_basis={'TABLE_1':'exact WGCCRE planet/star label + LOOM class','TABLE_2':'exact satellite canonical label + matching WGCCRE parent heading + LOOM parent identity','TABLE_3':('explicit Pluto satellite label + existing Charon identity and Pluto parent' if b['body_class']=='NATURAL_SATELLITE' else 'explicit MPC-numbered designation in report matched to active LOOM NAIF extended asteroid number; or exact comet designation/name + body class')}[table]
 external=f'{table}:{alias}'
 cross_id=stable({'artifact':artifact,'scheme':'WGCCRE_TABLE_ROW','external':external,'body':body,'basis':match_basis})
 c.execute('insert or ignore into identity_crosswalk values(?,?,?,?,?,?,?,?)',(cross_id,artifact,'WGCCRE_TABLE_ROW',external,body,match_basis,'MATCH','Table row identity reconciled to existing loom_solar.body snapshot; no body identity was created.'))
 crosswalks.append({'body_id':body,'table':table,'source_row':alias,'crosswalk_id':cross_id,'match_basis':match_basis,'disposition':'MATCH'})
 for prop,reported in fields.items():
  aid=artifact; status='CANDIDATE'
  if body=='PHOBOS' and table=='TABLE_2' and prop=='PRIME_MERIDIAN_MODEL' and not corrected: status='HOLD'
  lineage=f'WGCCRE:2015:{table}:{body}:{prop}' + (';CORRIGENDUM:2019' if corrected else '')
  normalized=fold(reported)
  scope='EPOCH_SCOPED_MODEL' if b['body_class']=='COMET' else 'BODY_FRAME_MODEL'
  payload={'loom_body_id':body,'wgccre_table':table,'wgccre_row_identity':alias,'equation_as_published':reported,'source_row_context':source_context or correction_excerpt,'normalization':'Unicode/source text retained; deterministic whitespace fold only; no equation evaluation.','reporting_epoch':'per row: see WGCCRE epoch fields; standard epoch J2000.0 / JD 2451545.0 TDB where specified','lineage_parent':'WGCCRE-2015' if not corrected else 'WGCCRE-2015 corrected by WGCCRE-2019','identity_crosswalk_id':cross_id,'correction_applied':corrected,'model_scope':scope}
  ref=f'WGCCRE-2015 {table}; table page { {"TABLE_1":8,"TABLE_2":10,"TABLE_3":15}[table]}' if not corrected else 'WGCCRE 2019 correction, corrected Table 2, page 4 (PDF page 4)'
  if body=='PHOBOS' and corrected: ref='WGCCRE 2019 correction, Table 2, PDF page 4; published correction to 2015 Table 2'
  if body=='PHOBOS' and corrected and prop=='PRIME_MERIDIAN_MODEL': ref='WGCCRE 2019 Phobos corrigendum: W0=35.18774440 and final −1.143 sin(M5) term'
  assertion_id=stable({'body':body,'property':prop,'artifact':aid,'lineage':lineage,'reported':reported,'status':status})
  unit='deg/day; see WGCCRE equation epoch/variable definitions' if prop=='PRIME_MERIDIAN_RATE_MODEL' else 'deg; see WGCCRE equation epoch/variable definitions'
  c.execute('insert into candidate_assertion values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',(assertion_id,body,prop,reported,unit,None,normalized,unit,None,'deterministic opaque model text; whitespace folding only; no conversion/evaluation','PHYSICAL_MODEL','MODEL_COEFFICIENT',scope,aid,lineage,ref,json.dumps(payload,sort_keys=True,ensure_ascii=False),'CANDIDATE',0,status))
  assertions.append({'assertion_id':assertion_id,'body_id':body,'property_code':prop,'status':status,'source_artifact_id':aid,'source_lineage':lineage})
for body,r in sorted(rows.items(),reverse=os.environ.get('LOOM_WGCCRE_REVERSE')=='1'):
 add_record(body,r['table'],r['alias'],r['fields'],main_id,'2015',False,r['raw_block'])
# The 2019 corrigendum preserves the 2015 row but supersedes its Phobos W expression.
add_record('PHOBOS','TABLE_2','Phobos (corrected prime-meridian equation)',{'PRIME_MERIDIAN_MODEL':corrected_phobos},corr_id,'2019',True)
# The source's numbered asteroid (52) Europa has no corresponding asteroid identity in this 110-body catalog;
# the only exact-name LOOM body is Jupiter's natural satellite. Preserve this as an explicit unresolved collision.
collision_id=stable({'artifact':main_id,'scheme':'WGCCRE_TABLE_ROW','external':'TABLE_3:(52) Europa','body':None,'disposition':'HOLD'})
c.execute('insert into identity_crosswalk values(?,?,?,?,?,?,?,?)',(collision_id,main_id,'WGCCRE_MPC_NUMBER','52',None,'numbered asteroid designation conflicts with the only exact-name LOOM identity, EUROPA (a natural satellite); no asteroid 52 identity exists in the frozen 110-body population','HOLD','Retained as an explicit unmatched identity collision; no candidate assertion assigned.'))
crosswalks.append({'body_id':None,'table':'TABLE_3','source_row':'(52) Europa','match_basis':'numbered asteroid designation conflicts with only exact-name LOOM identity EUROPA (natural satellite)','disposition':'HOLD'})
# Update only existing lanes; candidate values never receive preference.
for body,prop in c.execute("select body_id,property_code from candidate_assertion where source_artifact_id in (?,?) group by body_id,property_code",(main_id,corr_id)).fetchall():
 count=c.execute("select count(*) from candidate_assertion where body_id=? and property_code=? and disposition='CANDIDATE'",(body,prop)).fetchone()[0]
 changed=c.execute('update coverage set disposition=?,reason=?,assertion_count=? where body_id=? and property_code=?',('SUPPORTED','WGCCRE 2015/2019 candidate cartographic/orientation model evidence added; preferred_fact remains 0',count,body,prop)).rowcount
 if not changed:c.execute('insert into coverage values(?,?,?,?,?)',(body,prop,'SUPPORTED','WGCCRE supplies an explicit candidate rotation-rate model; lane added additively, preferred_fact remains 0',count))
c.commit()
if c.execute('select count(*) from authority_body_ref').fetchone()[0]!=110:raise ValueError('existing LOOM body population changed')
if c.execute('select count(*) from candidate_assertion where preferred_fact<>0').fetchone()[0]:raise ValueError('preferred fact firewall violated')
if c.execute('pragma foreign_key_check').fetchall():raise ValueError('foreign key violation')
print('rows',len(rows),{x:sum(r['table']==x for r in rows.values()) for x in ('TABLE_1','TABLE_2','TABLE_3')},'assertions',len(assertions))
