"""Bay-length screen: the same 6+ couch feasible designs stretched in the parallel body (12.8 -> 14.3 -> 16.8 m),
with and without the Osteon central case. ALL bodies. ALL sponsors. 2026-2226."""
import json
import engine as E, missions as MI
from multiprocessing import Pool
def job(a):
    i, p = a
    try:
        r = E.evaluate(p); r['id'] = i; r['missions'] = {k: MI.evaluate(r, pr) for k, pr in MI.MJ['profiles'].items()}; return r
    except Exception as ex: return dict(id=i, params=p, feasible=False, fails=[str(ex)])
if __name__ == '__main__':
    D = json.load(open('explorer_results.json'))
    base = [r for r in D['results'] if r.get('feasible') and r['params']['seats'] >= 6]
    base = sorted(base, key=lambda r: r['docked_t'])[:300]
    out = {}
    for L in (12.8, 14.3, 16.8):
        for w in ('none', 'osteon_airframe'):
            jobs = [(r['id'], dict(r['params'], length=L, wildcard=w)) for r in base]
            with Pool(2) as pool: res = pool.map(job, jobs, chunksize=8)
            ok = [r for r in res if r.get('feasible')]
            cnt = {k: sum(r['missions'][k]['ok'] for r in ok) for k in MI.MJ['profiles']}
            allf = [r for r in ok if all(m['ok'] for m in r['missions'].values())]
            key = f'L{L}_{w}'
            out[key] = dict(n=len(base), feasible=len(ok), missions=cnt, all_five=len(allf), eight=sum(r['params']['seats'] == 8 for r in allf),
                            median_interior=sorted(r['interior_margin_m3'] for r in ok)[len(ok) // 2] if ok else None,
                            best=[dict(id=r['id'], seats=r['params']['seats'], wing=r['params']['wing'], span=r['params']['span'], dry=r['dry_t'], docked=r['docked_t'],
                                       xr=r['crossrange_km'], glide=r['glide_LD'], interior=r['interior_margin_m3'], hull=r['hull_m3']) for r in sorted(allf, key=lambda r: r['docked_t'])[:5]])
            print(key, out[key]['feasible'], cnt, 'all5', len(allf), flush=True)
    json.dump(dict(header='ALL bodies. ALL sponsors. 2026-2226.', model_version=E.MODEL_VERSION, note='same 300 lightest feasible 6+ couch designs (12.8 m population), parallel body stretched', results=out), open('bay_screen.json', 'w'), indent=1)
