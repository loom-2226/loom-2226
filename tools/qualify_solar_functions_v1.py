#!/usr/bin/env python3
"""Checkpointed 2026-2250 Solar V1 continuous-function qualification campaign.

Work-unit boundaries are operational checkpoint partitions only. Governed
body/center source boundaries are hard representation boundaries. No work unit
may cross a governed source transition.
"""
import argparse, hashlib, json, math, os, sys, time
from pathlib import Path
REPO=Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path: sys.path.insert(0,str(REPO))
from src.loom_solar_inspector import Inspector
from src.loom_solar_function_compile import compile_adaptive
from src.loom_solar_state_runtime import PiecewiseStateFunction
from src.loom_solar_temporal_publish import DAY, center_for, tolerance

FRACTIONS=(0.017,0.071,0.193,0.337,0.503,0.677,0.829,0.941,0.991)

def atomic_json(path,obj):
    tmp=path.with_suffix(path.suffix+'.tmp')
    tmp.write_text(json.dumps(obj,sort_keys=True,separators=(',',':'))+'\n')
    os.replace(tmp,path)

def source_boundaries(I,body,center,start,end):
    cuts={float(start),float(end)}
    for target in {body,center}:
        for c in I.registry.coverage:
            if c.body_id==target and c.status=='QUALIFIED':
                for t in (float(c.coverage_start_et),float(c.coverage_end_et)):
                    if start < t < end: cuts.add(t)
    return sorted(cuts)

def tasks_for(I,bodies,start,end,max_days):
    max_s=max_days*DAY
    tasks=[]
    for body in bodies:
        center=center_for(I,body)
        cuts=source_boundaries(I,body,center,start,end)
        for a,b in zip(cuts,cuts[1:]):
            # checkpoint partitions; never cross an authority/source cut
            n=max(1,math.ceil((b-a)/max_s))
            for j in range(n):
                x=a+(b-a)*j/n; y=a+(b-a)*(j+1)/n
                key=hashlib.sha256(f'{body}|{center}|{x:.9f}|{y:.9f}'.encode()).hexdigest()[:20]
                tasks.append((body,center,x,y,key))
    return tasks

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--database',default='loom_dev')
    p.add_argument('--asset-root',default='/home/ubuntu/loom_solar_assets')
    p.add_argument('--output',default='/home/ubuntu/loom_solar_v1_function_qualification')
    p.add_argument('--start',default='2026 JAN 01 TDB')
    p.add_argument('--end',default='2251 JAN 01 TDB')
    p.add_argument('--max-work-days',type=float,default=256.0)
    p.add_argument('--bodies',nargs='*')
    p.add_argument('--limit',type=int)
    a=p.parse_args()
    out=Path(a.output); units=out/'units'; units.mkdir(parents=True,exist_ok=True)
    I=Inspector.connect(a.database,a.asset_root)
    start=I.time.parse(a.start); end=I.time.parse(a.end)
    bodies=sorted(a.bodies or I.bodies)
    tasks=tasks_for(I,bodies,start,end,a.max_work_days)
    if a.limit: tasks=tasks[:a.limit]
    print('LOOM SOLAR V1 FUNCTION QUALIFICATION',flush=True)
    print(f'interval_et={start}..{end} bodies={len(bodies)} work_units={len(tasks)} max_work_days={a.max_work_days}',flush=True)
    print(f'output={out}',flush=True)
    passed=skipped=failed=0; begun=time.time()
    for i,(body,center,s,e,key) in enumerate(tasks,1):
        dest=units/f'{body}__{key}.json'
        if dest.exists():
            try:
                old=json.loads(dest.read_text())
                if old.get('status')=='PASS' and old.get('start_et')==s and old.get('end_et')==e:
                    skipped+=1
                    print(f'[{i:05d}/{len(tasks):05d}] {body:<28} SKIP persisted',flush=True); continue
            except Exception: pass
        t0=time.time(); tol=tolerance(I,body)
        try:
            compiled=compile_adaptive(I,body,center,s,e,tol)
            f=PiecewiseStateFunction(compiled); worst=0.0
            # independent interior probes, distinct from compiler validation grid
            for q in FRACTIONS:
                t=s+q*(e-s); truth=I.at(body,t,center)
                if truth.get('resolution')!='RESOLVED' or 'relative' not in truth:
                    raise RuntimeError(f'unresolved independent truth at ET {t}')
                worst=max(worst,math.dist(f.state(t).position_km,truth['relative']['position_km']))
            if worst>tol: raise RuntimeError(f'independent error {worst} km > tolerance {tol} km')
            reps={z['representation'] for z in compiled['segments']}
            if reps!={'CHEBYSHEV_STATE_SEGMENT'}: raise RuntimeError(f'unexpected representations {reps}')
            # Compiler itself rejects mixed authority/source within segments.
            row={'schema':'loom.solar-v1-function-work-unit/1.0','status':'PASS','body_id':body,'center_id':center,
                 'start_et':s,'end_et':e,'work_partition_only':True,'tolerance_km':tol,
                 'independent_worst_error_km':worst,'segment_count':len(compiled['segments']),
                 'elapsed_s':time.time()-t0,'compiled':compiled}
            atomic_json(dest,row); passed+=1
            print(f'[{i:05d}/{len(tasks):05d}] {body:<28} PASS seg={len(compiled["segments"]):4d} worst={worst:.6g}km t={row["elapsed_s"]:.1f}s',flush=True)
        except Exception as exc:
            row={'schema':'loom.solar-v1-function-work-unit/1.0','status':'FAIL','body_id':body,'center_id':center,
                 'start_et':s,'end_et':e,'work_partition_only':True,'tolerance_km':tol,'elapsed_s':time.time()-t0,'reason':str(exc)}
            atomic_json(dest,row); failed+=1
            print(f'[{i:05d}/{len(tasks):05d}] {body:<28} FAIL {exc}',flush=True)
            print('FAIL-CLOSED: stop, preserve checkpoint, investigate before resume.',flush=True)
            break
    summary={'schema':'loom.solar-v1-function-campaign/1.0','start_et':start,'end_et':end,'body_count':len(bodies),
             'planned_work_units':len(tasks),'pass_this_run':passed,'skip_this_run':skipped,'fail_this_run':failed,
             'elapsed_s_this_run':time.time()-begun,'output':str(out)}
    atomic_json(out/'last_run_summary.json',summary)
    print(json.dumps(summary,indent=2,sort_keys=True),flush=True)
    raise SystemExit(2 if failed else 0)

if __name__=='__main__': main()
