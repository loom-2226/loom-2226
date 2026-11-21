"""Refine the explorer: mutate the non-dominated feasible designs (simple evolutionary loop).
ALL bodies. ALL sponsors. 2026-2226. Run after engine.py: python3 evolve.py --gens 2 --pop 400"""
import json, random, argparse, os
import numpy as np
import engine as E
OBJ = [('crossrange_km', +1), ('glide_LD', +1), ('capability_count', +1), ('docked_t', -1), ('touchdown_heavy_ms', -1), ('interior_margin_m3', +1)]
def vec(r): return np.array([s * r[k] for k, s in OBJ], float)
def pareto(rs):
    V = np.array([vec(r) for r in rs]); keep = []
    for i in range(len(rs)):
        dom = np.all(V >= V[i], 1) & np.any(V > V[i], 1)
        if not dom.any(): keep.append(rs[i])
    return keep
def mutate(p, rng, rate=0.12):
    q = dict(p)
    for k, v in E.SPACE.items():
        if isinstance(v, list):
            if rng.random() < 0.15: q[k] = rng.choice(v)
        else:
            lo, hi = v; q[k] = round(min(hi, max(lo, q[k] + rng.gauss(0, rate * (hi - lo)))), 3)
    if q['wing'] == 'fold': q['span'] = min(q['span'], 9.0)
    if q['wing'] == 'none': q['span'], q['chord'] = 4.26, 0.0
    elif q['chord'] == 0.0: q['chord'] = 1.6
    return q
if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--gens', type=int, default=2); ap.add_argument('--pop', type=int, default=400); ap.add_argument('--seed', type=int, default=7)
    a = ap.parse_args(); rng = random.Random(a.seed)
    D = json.load(open('explorer_results.json')); res = D['results']; nid = max(r['id'] for r in res) + 1
    from multiprocessing import Pool
    for g in range(a.gens):
        front = pareto([r for r in res if r.get('feasible')]); print('gen', g, 'front', len(front))
        kids = [(nid + i, mutate(rng.choice(front)['params'], rng)) for i in range(a.pop)]; nid += a.pop
        with Pool(2) as pool: new = pool.map(E._job, kids, chunksize=8)
        for r in new: r['gen'] = g + 1
        res += new; print('  feasible new', sum(r.get('feasible', False) for r in new))
    front = pareto([r for r in res if r.get('feasible')])
    for r in res: r['pareto'] = False
    ids = {r['id'] for r in front}
    for r in res:
        if r['id'] in ids: r['pareto'] = True
    D['results'] = res; D['n'] = len(res); D['objectives'] = OBJ
    json.dump(D, open('explorer_results.json', 'w'), default=lambda o: bool(o) if isinstance(o, np.bool_) else float(o))
    print('total', len(res), 'feasible', sum(r.get('feasible', False) for r in res), 'pareto', len(front))
