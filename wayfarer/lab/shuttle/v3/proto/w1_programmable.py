"""Prototype lane W1: programmable materials (shape/stiffness-changing structure). NON-CANON sensitivity.
Evaluated ALONE first (no Osteon, 12.8 m), then combined. ALL bodies. ALL sponsors. 2026-2226."""
import sys, os, json
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, '..', 'explorer'))
import engine as E, missions as MI
D = json.load(open(os.path.join(H, '..', 'explorer', 'explorer_results.json'))); by = {r['id']: r for r in D['results']}
def run(p):
    r = E.evaluate(p); ms = {k: MI.evaluate(r, pr) for k, pr in MI.MJ['profiles'].items()}
    td = {k: next((c['value'] for c in m['checks'] if 'touchdown' in c['name']), None) for k, m in ms.items()}
    return dict(feasible=r['feasible'], fails=r['fails'], dry_t=r['dry_t'], docked_t=r['docked_t'], wing_t=r['mass_t']['wings'], glide=r['glide_LD'],
                crossrange=r['crossrange_km'], turn=r['max_turn_dps'], light_ms=r['touchdown_light_ms'], touchdown=td,
                missions={k: m['ok'] for k, m in ms.items()}, fail_detail={k: [(c['name'][:40], c['value'], c['limit']) for c in m['checks'] if not c['ok']] for k, m in ms.items() if not m['ok']})
b5 = dict(E.B5); g = dict(by[2643]['params'])
cases = {
 'B5 baseline': b5,
 'B5 + programmable, 14 m span': dict(b5, wildcard='programmable'),
 'B5 + programmable, 20 m span': dict(b5, wildcard='programmable', span=20.0, chord=1.8),
 '#2643 baseline': g,
 '#2643 + programmable, 20 m span': dict(g, wildcard='programmable', span=20.0, chord=1.8),
 '#2643 + programmable 20 m, 14.3 m hull, 8 couches': dict(g, wildcard='programmable', span=20.0, chord=1.8, length=14.3, seats=8),
}
out = {k: run(p) for k, p in cases.items()}
json.dump(dict(header='ALL bodies. ALL sponsors. 2026-2226.', lane='PROTOTYPE (non-canon)', model_version=E.MODEL_VERSION, note=E.WILDCARDS['programmable']['note'], results=out),
          open(os.path.join(H, 'w1_programmable.json'), 'w'), indent=1)
for k, v in out.items(): print(k, v['feasible'], v['dry_t'], v['docked_t'], v['glide'], v['light_ms'], v['touchdown'], v['missions'], v['fail_detail'])
