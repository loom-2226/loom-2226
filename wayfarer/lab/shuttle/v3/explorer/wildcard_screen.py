"""Screen the tech wildcards over the feasible 6+ couch population (same params, wildcard swapped).
ALL bodies. ALL sponsors. 2026-2226."""
import json
import engine as E, missions as MI
from multiprocessing import Pool
D = json.load(open('explorer_results.json'))
base = [r for r in D['results'] if r.get('feasible') and r['params']['seats'] >= 6]
def job(a):
    i, p = a
    try:
        r = E.evaluate(p); r['id'] = i; r['missions'] = {k: MI.evaluate(r, pr) for k, pr in MI.MJ['profiles'].items()}; return r
    except Exception as ex: return dict(id=i, params=p, feasible=False, fails=[str(ex)])
if __name__ == '__main__':
    out = {}
    for w in ['none', 'osteon_cautious', 'osteon_airframe', 'osteon_optimistic']:
        jobs = [(r['id'], dict(r['params'], wildcard=w)) for r in base]
        with Pool(2) as pool: res = pool.map(job, jobs, chunksize=8)
        ok = [r for r in res if r.get('feasible')]
        cnt = {k: sum(r['missions'][k]['ok'] for r in ok) for k in MI.MJ['profiles']}
        allf = [r for r in ok if all(m['ok'] for m in r['missions'].values())]
        out[w] = dict(n=len(base), feasible=len(ok), missions=cnt, all_five=len(allf),
                      all_five_8=sum(r['params']['seats'] == 8 for r in allf),
                      best=sorted([dict(id=r['id'], seats=r['params']['seats'], wing=r['params']['wing'], span=r['params']['span'], fan=r['params']['fan_m2'],
                                        floats=r['params']['floats_m3'], water=r['params']['water_t'], rover=r['params']['rover'], dry=r['dry_t'], docked=r['docked_t'],
                                        th=r['touchdown_heavy_ms'], hot=r['hot_egress_water_t'], xr=r['crossrange_km'], turn=r['max_turn_dps'],
                                        interior=r['interior_margin_m3'], lim=r['limiting'], osteon=r.get('osteon'), td={k: m['touchdown_mass_t'] for k, m in r['missions'].items()}, fails={k: [c['name'] for c in m['checks'] if not c['ok']] for k, m in r['missions'].items()}) for r in allf], key=lambda x: x['docked'])[:8],
                      near=sorted([dict(id=r['id'], seats=r['params']['seats'], docked=r['docked_t'], dry=r['dry_t'], ok=[k for k, m in r['missions'].items() if m['ok']], fails={k: [(c['name'], c['value'], c['limit']) for c in m['checks'] if not c['ok']] for k, m in r['missions'].items() if not m['ok']}) for r in ok], key=lambda x: (-len(x['ok']), x['docked']))[:6])
        print(w, out[w]['feasible'], cnt, 'all5', out[w]['all_five'], '8c', out[w]['all_five_8'], flush=True)
    json.dump(dict(header='ALL bodies. ALL sponsors. 2026-2226.', model_version=E.MODEL_VERSION, wildcards={k: v.get('note', '') for k, v in E.WILDCARDS.items()}, results=out),
              open('wildcard_screen.json', 'w'), indent=1)
