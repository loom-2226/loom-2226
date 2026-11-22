"""Numbers for the 2026-11-21 comparative study (one place, reproducible). ALL bodies. ALL sponsors. 2026-2226."""
import sys, os, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..', 'explorer'))
import engine as E, missions as MI
D = json.load(open(os.path.join(HERE, '..', 'explorer', 'explorer_results.json'))); by = {r['id']: r for r in D['results']}
def run(p):
    r = E.evaluate(p); ms = {k: MI.evaluate(r, pr) for k, pr in MI.MJ['profiles'].items()}
    def worst(m):
        hs = [c['headroom'] for c in m['checks'] if isinstance(c['headroom'], (int, float))]
        return min(hs) if hs else None
    return dict(params=p, feasible=r['feasible'], fails=r['fails'], dry_t=r['dry_t'], docked_t=r['docked_t'], seats=p['seats'], length=p.get('length', 12.8),
                interior=r['interior_margin_m3'], crossrange=r['crossrange_km'], glide=r['glide_LD'], turn=r['max_turn_dps'], fit_r=r['fit_r_m'],
                osteon=r['osteon'], mass=r['mass_t'], missions={k: dict(ok=m['ok'], touchdown_mass_t=m['touchdown_mass_t'], worst_headroom=worst(m),
                fails=[(c['name'], c['value'], c['limit']) for c in m['checks'] if not c['ok']]) for k, m in ms.items()})
C = {
 'B5 reference': dict(E.B5),
 'B5 + Osteon central': dict(E.B5, wildcard='osteon_airframe'),
 '#2643 conventional': dict(by[2643]['params'], wildcard='none'),
 '#2643 Osteon cautious': dict(by[2643]['params'], wildcard='osteon_cautious'),
 '#2643 Osteon central': dict(by[2643]['params'], wildcard='osteon_airframe'),
 '#2643 Osteon optimistic': dict(by[2643]['params'], wildcard='osteon_optimistic'),
 '#2643 14.3 m, 8 couches, Osteon cautious': dict(by[2643]['params'], length=14.3, seats=8, wildcard='osteon_cautious'),
 '#2643 14.3 m, 8 couches, Osteon central': dict(by[2643]['params'], length=14.3, seats=8, wildcard='osteon_airframe'),
 '#2643 14.3 m, 8 couches, conventional': dict(by[2643]['params'], length=14.3, seats=8, wildcard='none'),
 '#2430 compact sea courier': dict(by[2430]['params']),
}
out = {k: run(p) for k, p in C.items()}
json.dump(dict(header='ALL bodies. ALL sponsors. 2026-2226.', model_version=E.MODEL_VERSION, candidates=out), open(os.path.join(HERE, 'study_numbers.json'), 'w'), indent=1, default=float)
for k, v in out.items(): print(k, v['feasible'], v['dry_t'], v['docked_t'], {m: (x['ok'], x['worst_headroom']) for m, x in v['missions'].items()}, v['osteon'] and v['osteon']['saved_t'])
