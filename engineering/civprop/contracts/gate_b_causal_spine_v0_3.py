"""Gate B qualification contract for the LOOM timeline -> Solar decision spine.

This is deliberately a qualification adapter, not production actor-adoption or
GAP-016 transport physics.  It proves the existing runtime gates are connected:
a validated scenario frontier cannot grant access; an explicit actor capability
event plus an explicitly feasible positive-control service can.

The positive control is marked NON_CANON_QUALIFICATION_CONTROL everywhere.
"""
from __future__ import annotations
import csv, gzip, hashlib, json
from pathlib import Path

FORMAT="LOOM_GATE_B_CAUSAL_SPINE_V0_3"
VERSION="0.3.0"
CAPTURE_SHA="a6a61c2806b25b33290df8af932be9e3e2cbba4d406101db1bc6f47a41f8ed41"
TIMELINE_SNAPSHOT="timeline-v0-1-0232bf23494f-20260925"
FRONTIER_IDS=(
 "TRN-MOD-HEAVY","TRN-MOD-NEP","ENE-MOD-INDUSTRIAL","ENE-MOD-FUSION-GRID",
 "EXT-MOD-LUNAR-PILOT","EXT-MOD-REFINING","EXT-MOD-ASTEROID","MFG-MOD-PARTS",
 "MFG-MOD-STRUCTURES","CON-MOD-ROBOTIC","CON-MOD-LOCAL","AUT-MOD-OUTPOST",
 "AUT-MOD-GENERAL","HAB-MOD-OUTPOST","HAB-MOD-FOOD","COM-MOD-LUNAR",
 "MED-MOD-RADIATION","MED-MOD-GENERATIONS","SOC-MOD-SYNTH-LEGAL-RECOGNITION",
 "SPEC-MOD-TORCH","SPEC-MOD-MC299M","SPEC-MOD-METRIC-LAB",
 "SPEC-MOD-METRIC-SHIP","SPEC-MOD-LOOM-PROBE",
)
# Gate-B transport capability is a qualification control. It is NOT inferred
# from a timeline milestone and is NOT a physical transport model.
CONTROL_TECH="GATE_B_SOLAR_RECON_TRANSPORT_CONTROL"

def _read_timeline(capture:Path):
 p=capture/'postgres'/'timeline_milestone.csv.gz'
 with gzip.open(p,'rt',newline='') as f: return list(csv.DictReader(f))

def timeline_frontier_from_capture(capture:Path)->list[dict]:
 manifest=json.loads((capture/'MANIFEST.json').read_text())
 actual=hashlib.sha256((capture/'MANIFEST.json').read_bytes()).hexdigest()
 if actual != CAPTURE_SHA: raise ValueError(f"Gate A capture SHA mismatch: {actual}")
 if manifest['snapshot_ids']['timeline'] != TIMELINE_SNAPSHOT: raise ValueError('timeline snapshot mismatch')
 by={x['milestone_id']:x for x in _read_timeline(capture)}
 missing=set(FRONTIER_IDS)-set(by)
 if missing: raise ValueError(f"missing Gate B timeline frontiers: {sorted(missing)}")
 out=[]
 for mid in FRONTIER_IDS:
  x=by[mid]
  if x['authority_class']!='PROVISIONAL_SIMULATION_SCAFFOLD':
   raise ValueError(f"frontier is not scenario scaffold: {mid}")
  out.append({'tech_id':mid.replace('-','_'),'frontier_year':int(x['start_year']),
   'source_milestone_id':mid,'authority_class':x['authority_class'],
   'epistemic_status':x['epistemic_status'],
   'frontier_semantics':'CONSIDERATION_ANCHOR_NOT_ACHIEVEMENT',
   'provenance_refs':[TIMELINE_SNAPSHOT,f'GATE_A_CAPTURE:{CAPTURE_SHA}']})
 return out

def apply_gate_b_qualification(s:dict,capture:Path,*,positive_control:bool=False,actor_id='NASA')->dict:
 """Inject timeline frontiers and optional explicit positive-control capability.

 The normal arm never creates actor access. The positive-control arm does so
 explicitly, so a resulting Solar decision proves the downstream lane is alive.
 """
 frontiers=timeline_frontier_from_capture(capture)
 # Preserve V0.2 frontier IDs because project archetypes still reference them.
 existing={x['tech_id']:x for x in s['technology_frontier']}
 for x in frontiers:
  existing[x['tech_id']]={'tech_id':x['tech_id'],'frontier_year':x['frontier_year']}
 # Qualification control is not a timeline technology and must never be confused
 # with one. Its 2026 frontier exists only to let actor_tech_status evaluate the
 # explicit CAPABILITY_SET event.
 existing[CONTROL_TECH]={'tech_id':CONTROL_TECH,'frontier_year':2026}
 s['technology_frontier']=[existing[k] for k in sorted(existing)]

 # Solar recon missions require explicit transport capability. Empty required-tech
 # lists were the Phase-2 hole that made capability appear USABLE.
 for m in s['mission_knowledge_v1']['missions']:
  if m['mission_archetype_id'].startswith('SOLAR_RECON::'):
   m['required_tech']=[CONTROL_TECH]

 # Accessibility receives the same capability state. Placeholder service remains
 # UNKNOWN in the normal arm. Positive control makes it explicitly FEASIBLE while
 # retaining its nonphysical diagnostic cost and qualification-only provenance.
 for svc in s['accessibility_v1']['service_paths']:
  if svc['mission_class']=='ROBOTIC_RESOURCE_RECONNAISSANCE' and svc['service_id'].endswith('_SOLAR_V03'):
   svc['required_technology_ids']=[CONTROL_TECH]
   svc['limiting_constraints']=[] if positive_control else ['REQUIRED_TRANSPORT_TECHNOLOGY_UNKNOWN']
   if positive_control and svc['actor_id']==actor_id:
    svc['status']='FEASIBLE'
    svc['generalized_cost']={'status':'KNOWN','value':0.0,'unit':'QUALIFICATION_CONTROL_ONLY','uncertainty':None}
    svc['provenance_refs']=list(dict.fromkeys(svc['provenance_refs']+['NON_CANON_QUALIFICATION_CONTROL:GATE_B','WARNING:NOT_PHYSICAL_TRANSPORT']))

 if positive_control:
  events=s['actor_state_v1']['events']
  events.append({'event_id':f'{actor_id}_GATE_B_SOLAR_RECON_CONTROL_2026','year':2026,'actor_id':actor_id,
   'event_type':'CAPABILITY_SET','payload':{'capability_id':CONTROL_TECH,'status':'USABLE'},
   'provenance':{'class':'NON_CANON_QUALIFICATION_CONTROL','ref':'GATE_B_POSITIVE_CONTROL_EXPLICIT_ACTOR_ACCESS'}})
  # Make one actor's budget large enough that affordability cannot hide a dead lane.
  events.append({'event_id':f'{actor_id}_GATE_B_BUDGET_CONTROL_2026','year':2026,'actor_id':actor_id,
   'event_type':'BUDGET_ALLOCATION_SET',
   'payload':{'amount':1000000.0,'unit':'USD_2026_billion','scope':'GATE_B_POSITIVE_CONTROL_ONLY'},
   'provenance':{'class':'NON_CANON_QUALIFICATION_CONTROL','ref':'GATE_B_POSITIVE_CONTROL_BUDGET'}})

 s.setdefault('authority_context',{})['gate_b_causal_spine']={
  'format':FORMAT,'version':VERSION,'gate_a_capture_sha256':CAPTURE_SHA,
  'timeline_snapshot_id':TIMELINE_SNAPSHOT,'timeline_frontiers_loaded':len(frontiers),
  'timeline_frontier_grants_actor_access':False,'positive_control':positive_control,
  'control_actor_id':actor_id if positive_control else None,
  'control_technology_id':CONTROL_TECH,
  'classification':'NON_CANON_INTEGRATION_QUALIFICATION'}
 return s
