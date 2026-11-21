"""W1 sweep: span x tank on #2643 and B5, alone and combined. ALL bodies. ALL sponsors. 2026-2226."""
import sys, os, json
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, '..', 'explorer'))
import engine as E, missions as MI
D = json.load(open(os.path.join(H, '..', 'explorer', 'explorer_results.json'))); by = {r['id']: r for r in D['results']}
rows = []
for name, base in (('B5', dict(E.B5)), ('#2643', dict(by[2643]['params']))):
    for wc in ('programmable', 'osteon_cautious', 'osteon_cautious+programmable', 'osteon_airframe+programmable'):
        for span in (14.0, 17.0, 20.0):
            for water in (18.0, 23.1):
                for L, seats in ((12.8, base['seats']), (14.3, 8)):
                    p = dict(base, wildcard=wc, span=span, chord=1.8, water_t=water, length=L, seats=seats)
                    r = E.evaluate(p); ms = {k: MI.evaluate(r, pr) for k, pr in MI.MJ['profiles'].items()}
                    rows.append(dict(base=name, wildcard=wc, span=span, water=water, length=L, seats=seats, feasible=r['feasible'], dry=r['dry_t'], docked=r['docked_t'],
                                     glide=r['glide_LD'], xr=r['crossrange_km'], turn=r['max_turn_dps'], ok=[k for k, m in ms.items() if m['ok']],
                                     hot_td=next((c['value'] for c in ms['hot']['checks'] if 'touchdown' in c['name']), None),
                                     fails={k: [c['name'][:28] for c in m['checks'] if not c['ok']] for k, m in ms.items() if not m['ok']}))
json.dump(dict(header='ALL bodies. ALL sponsors. 2026-2226.', lane='PROTOTYPE (non-canon)', model_version=E.MODEL_VERSION, rows=rows), open(os.path.join(H, 'w1_sweep.json'), 'w'), indent=1)
for r in rows:
    if len(r['ok']) >= 4: print(r['base'], r['wildcard'], r['span'], r['water'], r['length'], r['seats'], r['dry'], r['docked'], r['glide'], r['ok'], r['hot_td'], r['fails'])
