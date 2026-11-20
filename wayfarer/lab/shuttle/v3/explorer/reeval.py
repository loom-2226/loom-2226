"""Re-evaluate the existing explorer population with the current engine (same params, same ids),
add margins, mission results, a Pareto set and the site data file. ALL bodies. ALL sponsors. 2026-2226.
Pareto: feasible designs only; maximise crossrange_km, glide_LD, couches, interior headroom; minimise docked_t, touchdown_heavy_ms.
Capability count is NOT an objective."""
import json, os
import numpy as np
import engine as E, missions as MI
OBJ = [('crossrange_km', +1), ('glide_LD', +1), ('seats', +1), ('interior_headroom', +1), ('docked_t', -1), ('touchdown_heavy_ms', -1)]
def val(r, k):
    if k == 'seats': return r['params']['seats']
    if k == 'interior_headroom': return next(g['headroom'] for g in r['gates'] if g['name'].startswith('Interior'))
    return r[k]
def pareto(rs):
    V = np.array([[s * val(r, k) for k, s in OBJ] for r in rs]); keep = set()
    for i in range(len(rs)):
        if not (np.all(V >= V[i], 1) & np.any(V > V[i], 1)).any(): keep.add(rs[i]['id'])
    return keep
if __name__ == '__main__':
    old = json.load(open('explorer_results.json'))
    jobs = []
    for r in old['results']:
        p = dict(r['params']); p.setdefault('fan_venus', True); p.setdefault('desal', True); jobs.append((r['id'], p))
    from multiprocessing import Pool
    with Pool(2) as pool: res = pool.map(E._job, jobs, chunksize=8)
    gen = {r['id']: r.get('gen', 0) for r in old['results']}
    for r in res:
        r['gen'] = gen.get(r['id'], 0)
        if 'dry_t' in r: r['missions'] = {k: MI.evaluate(r, pr) for k, pr in MI.MJ['profiles'].items()}
    ok = [r for r in res if r.get('feasible')]; P = pareto(ok)
    for r in res: r['pareto'] = r['id'] in P
    D = dict(header=old['header'], doc=E.__doc__, model_version=E.MODEL_VERSION, space={k: (v if isinstance(v, list) else list(v)) for k, v in E.SPACE.items()},
             pareto_objectives=OBJ, thresholds=E.THRESH, evidence_classes=E.CLS, missions=MI.MJ, archetypes=old['archetypes'], n=len(res), results=res)
    json.dump(D, open('explorer_results.json', 'w'), default=lambda o: bool(o) if isinstance(o, np.bool_) else float(o))
    print('n', len(res), 'feasible', len(ok), 'pareto', len(P), 'version', E.MODEL_VERSION)
