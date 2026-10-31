"""Find the approximate 10-second terminal gate transition for original Wayfarer mounts.
Conditional 24 fixed non-axial engines; no claim about Isp, engine mass, or feasibility.
"""
import copy,json
from pathlib import Path
from lab import save_run
R=Path(__file__).resolve().parent
base=json.loads((R/'configs/wayfarer_original_mount_300k.json').read_text())
experiment=json.loads((R/'experiments/reversal10.json').read_text())
experiment['phases'][0]['post_hold_s']=4.
rows=[]
for force in (265,270,275):
    ship=copy.deepcopy(base)
    ship['name']=f'Wayfarer original mounts conditional {force} kN nonaxial'
    ship['provenance']['performance_only']='Fixed reference mass/inertia, nonaxial thrust rating changed only'
    for e in ship['rcs']:
        if not e['id'].endswith('_axial'):e['max_N']=force*1000.
    label=f'original_mount_{force}kN'
    p=R/'configs'/(label+'.json')
    p.write_text(json.dumps(ship,indent=2)+'\n')
    q=R/'experiments'/(label+'.json')
    q.write_text(json.dumps(experiment,indent=2)+'\n')
    r=save_run(p,q,R/'lab_results',.02,.1)
    ph=r['phases'][0]
    row={'nonaxial_kN':force,'pass_at_10s':r['qualification']['status']=='pass',
         'attitude_error_deg':ph['attitude_error_deg'],
         'angular_rate_deg_s':ph['rate_deg_s'],
         'uninterrupted_settle_entry_s':ph['gate_entry_s']}
    rows.append(row)
    (R/'lab_results/rcs_threshold_scan.json').write_text(json.dumps(rows,indent=2)+'\n')
    print('THRESHOLD',row,flush=True)
