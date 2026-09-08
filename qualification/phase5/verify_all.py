from __future__ import annotations

import hashlib
import io
import json
import platform
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parents[1]
OUT = ROOT / "output"
OUT.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(REPO_ROOT))

from portable_dynamics import EffectorCommand, MassProperties, VehicleState, propagate


def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(65536),b''):
            h.update(chunk)
    return h.hexdigest()


def diag(a,b,c): return ((a,0.0,0.0),(0.0,b,0.0),(0.0,0.0,c))


def run_suite():
    suite=unittest.defaultTestLoader.discover(str(ROOT), pattern='test_phase5_*.py')
    stream=io.StringIO()
    result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
    return result, stream.getvalue()


def scenario_summary():
    s0=VehicleState(0.0,(0.0,0.0,0.0),(0.0,0.0,0.0),(1.0,0.0,0.0,0.0),(0.0,0.0,0.0),10.0)
    def mp_fixed(s): return MassProperties(1000.0,(0.0,0.0,0.0),diag(2000.0,3000.0,4000.0))
    def axial(s,mp): return [EffectorCommand(force_N_N=(500.0,0.0,0.0))]
    a=propagate(s0,4.0,0.01,mp_fixed,axial)[-1]
    def mp_var(s): return MassProperties(900.0+s.resource_kg,(0.0,0.0,0.0),diag(2000.0,3000.0,4000.0))
    def burn(s,mp):
        return [] if s.resource_kg <= 0 else [EffectorCommand(force_N_N=(1000.0,0.0,0.0),mass_flow_kg_s=2.0)]
    trace=propagate(s0,10.0,0.01,mp_var,burn)
    return {
        'axial_final_r_N_m': list(a.r_N_m),
        'axial_final_v_N_m_s': list(a.v_N_m_s),
        'depletion_final_resource_kg': trace[-1].resource_kg,
        'depletion_v_at_5s_m_s': trace[500].v_N_m_s[0],
        'depletion_v_at_10s_m_s': trace[-1].v_N_m_s[0],
        'trace_samples': len(trace),
    }


def main() -> int:
    required=[
        ROOT/'portable_dynamics.py',
        ROOT/'test_phase5_dynamics.py',
        ROOT/'wayfarer_phase5_adapter.py',
        ROOT/'test_phase5_wayfarer_guardrail.py',
    ]
    checks={'required_files': all(p.exists() for p in required)}
    result, _log=run_suite()
    checks['unit_suite']=result.wasSuccessful()
    summary=scenario_summary()
    checks['axial_known_answer']=(abs(summary['axial_final_r_N_m'][0]-4.0)<=1e-10 and abs(summary['axial_final_v_N_m_s'][0]-2.0)<=1e-11)
    checks['depletion_event_cutoff']=(summary['depletion_final_resource_kg']==0.0 and abs(summary['depletion_v_at_5s_m_s']-summary['depletion_v_at_10s_m_s'])<=1e-9)
    checks['wayfarer_inertia_guardrail']=result.wasSuccessful()
    payload={
        'schema':'loom.phase5_dynamics_verification.v0.1',
        'status':'PASS' if all(checks.values()) else 'FAIL',
        'environment':{'python':platform.python_version(),'platform':platform.platform(),'machine':platform.machine(),'offline_required':True},
        'checks':checks,
        'numerics':summary,
        'unit_suite':{
            'tests_run':result.testsRun,
            'failures':[str(x[0]) for x in result.failures],
            'errors':[str(x[0]) for x in result.errors],
            'skipped':[str(x[0]) for x in result.skipped],
            'passed':result.wasSuccessful(),
        },
        'input_sha256':{p.name:sha256(p) for p in required if p.exists()},
        'limitations':[
            'No external NASA/NESC/Basilisk hostile-reference vectors are included yet.',
            'Wayfarer full rotational 6DOF remains fail-closed because complete governed inertia authority is OPEN.',
            'This verifier qualifies the portable mechanics kernel and authority guardrail only; Phase 5 remains open.',
        ],
    }
    out=OUT/'phase5_verification_result.json'
    out.write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print('SHA256 phase5_verification_result.json',sha256(out))
    print(json.dumps(payload,indent=2,sort_keys=True))
    print('LOOM_PHASE5_VERIFY:',payload['status'])
    return 0 if payload['status']=='PASS' else 1


if __name__=='__main__': raise SystemExit(main())
