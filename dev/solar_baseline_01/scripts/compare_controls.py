#!/usr/bin/env python3
"""Compare overlapping candidate values to SF-PROMOTE-03 without modifying controls."""
import json,sqlite3,sys
from decimal import Decimal
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
candidate=Path(sys.argv[1]); control=Path(sys.argv[2])
ca=sqlite3.connect(candidate);ca.row_factory=sqlite3.Row
co=sqlite3.connect(control);co.row_factory=sqlite3.Row
unit_factor={'km^3/s^2':('km^3/s^2',Decimal(1)),'m^3/s^2':('km^3/s^2',Decimal('1e-9')),'g/cm^3':('kg/m^3',Decimal(1000)),'kg/m^3':('kg/m^3',Decimal(1)),'10^18 kg':('kg',Decimal('1e18')),'10^24 kg':('kg',Decimal('1e24')),'km':('km',Decimal(1)),'h':('s',Decimal(3600)),'d':('s',Decimal(86400)),'s':('s',Decimal(1))}
rows=[]
for r in ca.execute("select * from candidate_assertion where disposition='CANDIDATE' order by body_id,property_code,source_lineage"):
 b=r['body_id']
 for f in co.execute('select * from fact where body_id=? and property_code=?',(b,r['property_code'])):
  if r['normalized_value'] is None or f['value_numeric'] is None or r['reported_unit'] not in unit_factor:continue
  targetunit,factor=unit_factor[r['reported_unit']]
  if targetunit!=f['canonical_unit']:continue

  try:cv=Decimal(r['normalized_value'].strip('<>≤≥'))*factor
  except Exception:
   try:
    import json as _json; vals=_json.loads(r['normalized_value'])
    if not isinstance(vals,list) or len(vals)!=1:continue
    cv=Decimal(str(vals[0]))*factor
   except Exception:continue
  fv=Decimal(str(f['value_numeric']))
  cunc=Decimal(r['normalized_uncertainty']) * factor if r['normalized_uncertainty'] else None
  f_unc=[Decimal(str(x)) for x in (f['uncertainty_plus'],f['uncertainty_minus']) if x is not None]
  if cv==fv:
   status='UNCERTAINTY_DIFFERENCE' if cunc is not None or f_unc else 'EXACT_MATCH'
  elif cunc is not None and abs(cv-fv)<=cunc or f_unc and abs(cv-fv)<=max(f_unc):status='UNCERTAINTY_DIFFERENCE'
  elif abs(cv-fv)<=max(abs(fv)*Decimal('1e-12'),Decimal('1e-12')):status='SEMANTIC_MATCH'
  else:status='SUPPORTED_DIFFERENCE'
  rows.append({'body_id':b,'property_code':r['property_code'],'candidate_value':r['reported_value'],'candidate_unit':r['reported_unit'],'candidate_uncertainty':r['reported_uncertainty'],'candidate_normalized':str(cv),'control_value':f['reported_value_text'],'control_unit':f['reported_unit'],'control_normalized':str(fv),'classification':status,'candidate_lineage':r['source_lineage'],'control_fact_id':f['fact_id']})
summary={k:sum(x['classification']==k for x in rows) for k in ('EXACT_MATCH','SEMANTIC_MATCH','SUPPORTED_DIFFERENCE','SOURCE_VERSION_DIFFERENCE','UNCERTAINTY_DIFFERENCE','SEMANTICALLY_DISTINCT','CONFLICT_REQUIRES_REVIEW','IDENTITY_ERROR','NORMALIZATION_ERROR')}
out={'control_database_sha256':__import__('hashlib').sha256(control.read_bytes()).hexdigest(),'overlaps':rows,'classification_counts':summary,'mutated_controls':False,'method':'only same body + exact same property + deterministic source-unit equivalence; no cross-body inference; no changed SF-PROMOTE-03 values'}
(ROOT/'reports/control_comparison.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
print(json.dumps({'overlaps':len(rows),'classification_counts':summary},sort_keys=True))
