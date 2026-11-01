"""Narrow source-consistent FQ1–FQ4 rerun on current Wayfarer geometry.
Retains old FQ engine/RCs law (unchanged by I4), but rebuilds rigid-body base
mass, centroid, inertia from CURRENT SOURCE. Historical case logs remain untouched.
No Navigator and no Metric simulation. Not a new flight engine.
"""
from pathlib import Path
import json,hashlib,subprocess,sys,copy,math
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
SOURCE=ROOT/'results/out/wayfarer_v05_geometry.json'
G=json.loads(SOURCE.read_text());sha=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
HIST=HERE/'fq_20261031/wayfarer_fq_water_rcs_1960.json'
ship=copy.deepcopy(json.loads(HIST.read_text()))
base=G['states']['S4']
# Option C moved source-body mass/CG; check current source explicitly rather than pinning PR435 obsolete mass
assert base['mass_t']>0,'S4 current no-remass mass must be positive'
assert base['remass_t']==0,'S4 must be remass-empty base'
ship['base']={'mass_kg':base['mass_t']*1000,'cg_m':base['cg_m'],'inertia_kg_m2':base['inertia_kg_m2']}
ship['provenance']={'authority':'NON-GOVERNING current geometry numerical FQ1–FQ4 only',
    'geometry_sha256':sha,'engine_fixture':'fq_20261031/wayfarer_fq_water_rcs_1960.json',
    'body_source':'S4: no remass rigid-body inertia + S1 fuel tank at unchanged location',
    'scope':'FQ1–FQ4, full/half remass, no Metric, no Navigator, no hardware qualification'}
# Full state mass and cg must agree to source geometry at fixed-volume fuel tank.
m=ship['base']['mass_kg']+ship['tanks'][0]['initial_kg']
cg=[(ship['base']['mass_kg']*ship['base']['cg_m'][k]+ship['tanks'][0]['initial_kg']*ship['tanks'][0]['cg_m'][k])/m for k in range(3)]
src=G['states']['S1']
assert abs(m-src['mass_t']*1000)<1e-4
assert max(abs(cg[k]-src['cg_m'][k]) for k in range(3))<.03,('CG mismatch',cg,src['cg_m'])
out=HERE/'fq_current_option_c_20261101'
out.mkdir(exist_ok=True)
# A failed worker must never be masked by a previous passing results JSON.
for st in ('full','half'):
    (out/f'fq_matrix_{st}_0p2_all.json').unlink(missing_ok=True)
fixture=out/'current_fq1_fq4_fixture.json';fixture.write_text(json.dumps(ship,indent=1)+'\n')
print('FQ1-FQ4 INPUT',sha,'S4 base mass',ship['base']['mass_kg'],'S1 cg diff',max(abs(cg[k]-src['cg_m'][k]) for k in range(3)),flush=True)
runner=HERE/'fq_20261031/run_fq_matrix.py'
jobs=[]
for st in ['full','half']:
    cmd=[sys.executable,str(runner),'--state',st,'--dt','0.2','--subset','all','--fixture',str(fixture),'--out-dir',str(out)]
    fp=(out/f'{st}.stdout.txt').open('w')
    jobs.append((st,subprocess.Popen(cmd,stdout=fp,stderr=subprocess.STDOUT),fp))
    print('RUN',st,flush=True)
rows=[]
for st,job,fp in jobs:
    rc=job.wait();fp.close()
    if rc:
        raise RuntimeError(f'FQ {st} worker failed ({rc}); see {st}.stdout.txt; no stale evidence accepted')
    data=json.loads((out/f'fq_matrix_{st}_0p2_all.json').read_text())
    assert data['geometry_sha256']==sha and data['state']==st and data['dt']==.2, 'FQ result has stale/wrong source state'
    assert len(data['results'])==39, 'Incomplete FQ case matrix'
    rows.extend(data['results'])
    print(st,'EXIT',rc,'CASES',len(data['results']),'PASS',sum(x['status']=='PASS' for x in data['results']),flush=True)
summary={'geometry_sha256':sha,'source_state':'S4 no-remass mass/CG/inertia + unchanged tank','dt_s':.2,
  'total':len(rows),'passed':sum(x['status']=='PASS' for x in rows),
  'by_gate':{fq:{'total':sum(x['fq']==fq for x in rows),'passed':sum(x['fq']==fq and x['status']=='PASS' for x in rows)} for fq in ['FQ1','FQ2','FQ3','FQ4']},
  'status':'PASS_NUMERICAL' if len(rows)==78 and all(x['status']=='PASS' for x in rows) else 'HOLD',
  'constraints':'two water propellant states on OPTION C current mass tensor, no Metric/Navigator; not FQ5–FQ10 nor physical flight certificate',
  'failures':[{'gate':x['fq'],'case':x['case'],'state':x['state'],'status':x['status'],'error':x.get('error')} for x in rows if x['status']!='PASS']}
(out/'FQ1_FQ4_CURRENT_SUMMARY.json').write_text(json.dumps(summary,indent=1)+'\n')
print('FQ1-FQ4',summary['status'],summary['by_gate'],flush=True)
if summary['status']!='PASS_NUMERICAL':sys.exit(2)
