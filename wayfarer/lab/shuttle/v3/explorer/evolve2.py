"""Second-round evolution on the re-evaluated population, using reeval's objectives (no capability count)
and adding mission results to every new design. ALL bodies. ALL sponsors. 2026-2226.
python3 evolve2.py --gens 2 --pop 400 --seed 11"""
import json, random, argparse
import numpy as np
import engine as E, missions as MI, reeval as RV
from evolve import mutate
if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--gens', type=int, default=2); ap.add_argument('--pop', type=int, default=400); ap.add_argument('--seed', type=int, default=11)
    a = ap.parse_args(); rng = random.Random(a.seed)
    D = json.load(open('explorer_results.json')); res = D['results']; nid = max(r['id'] for r in res) + 1
    from multiprocessing import Pool
    for g in range(a.gens):
        ok = [r for r in res if r.get('feasible')]; P = RV.pareto(ok); front = [r for r in ok if r['id'] in P]
        # also seed from designs passing the most missions with 6+ couches
        good = sorted([r for r in ok if r['params']['seats'] >= 6], key=lambda r: -sum(m['ok'] for m in r['missions'].values()))[:60]
        parents = front + good; print('gen', g, 'parents', len(parents))
        kids = [(nid + i, mutate(rng.choice(parents)['params'], rng)) for i in range(a.pop)]; nid += a.pop
        for _, p in kids: p.setdefault('fan_venus', True); p.setdefault('desal', True)
        with Pool(2) as pool: new = pool.map(E._job, kids, chunksize=8)
        for r in new:
            r['gen'] = 100 + g + 1
            if 'dry_t' in r: r['missions'] = {k: MI.evaluate(r, pr) for k, pr in MI.MJ['profiles'].items()}
        res += new; print('  feasible new', sum(r.get('feasible', False) for r in new))
    ok = [r for r in res if r.get('feasible')]; P = RV.pareto(ok)
    for r in res: r['pareto'] = r['id'] in P
    D['results'] = res; D['n'] = len(res)
    json.dump(D, open('explorer_results.json', 'w'), default=lambda o: bool(o) if isinstance(o, np.bool_) else float(o))
    print('total', len(res), 'feasible', len(ok), 'pareto', len(P))
