"""Pick named concept archetypes from the explorer results. ALL bodies. ALL sponsors. 2026-2226."""
import json
D = json.load(open('explorer_results.json')); R = [r for r in D['results'] if r.get('feasible')]
ref = next(r for r in D['results'] if r['id'] == 0)
def cap(r, k): return r['capabilities'][k]
def pick(name, why, pool, key):
    pool = [r for r in pool]; r = max(pool, key=key) if pool else None
    return dict(name=name, why=why, id=r['id'] if r else None)
earth = [r for r in R if cap(r, 'Earth sea-to-orbit (core)')]
A = [
 dict(name='B5 reference', why='the current recommendation', id=0),
 pick('Long reach', 'most crossrange from orbit (pick the landing zone late)', earth, lambda r: r['crossrange_km'] - 50 * max(0, r['touchdown_heavy_ms'] - 60)),
 pick('Flying boat', 'slowest heavy water landing', [r for r in earth if r['params']['seats'] >= 6], lambda r: -r['touchdown_heavy_ms'] + 0.002 * r['crossrange_km']),
 pick('Light courier', 'least mass on Wayfarer (dry + full water), still does Earth', [r for r in earth if r['params']['seats'] >= 6 and r['crossrange_km'] > 800], lambda r: -r['docked_t']),
 pick('Hot extraction', 'hot egress to orbit with the sprint kit, then turn and reach', [r for r in earth if cap(r, 'Hot egress to orbit (+sprint 5 t)')], lambda r: r['crossrange_km'] / 100 + r['max_turn_dps'] - r['touchdown_heavy_ms'] / 10),
 pick('Big cabin', '8 couches, best all-round', [r for r in earth if r['params']['seats'] == 8], lambda r: r['capability_count'] * 300 + r['crossrange_km'] - 10 * r['touchdown_heavy_ms']),
 pick('All-rounder', 'most capabilities, then reach and light', earth, lambda r: r['capability_count'] * 1000 + r['crossrange_km'] - 20 * r['docked_t']),
]
by = {r['id']: r for r in D['results']}
for a in A:
    r = by[a['id']]; p = r['params']
    a['summary'] = {k: r[k] for k in ('dry_t', 'docked_t', 'hull_m3', 'crossrange_km', 'glide_LD', 'touchdown_heavy_ms', 'touchdown_light_ms', 'earth_margin_t', 'hot_egress_water_t', 'max_turn_dps', 'capability_count', 'interior_margin_m3', 'fit_r_m')}
    a['params'] = p
    print(a['name'], a['id'], a['summary'], {k: p[k] for k in ('wing', 'span', 'chord', 'fan_m2', 'floats_m3', 'water_t', 'seats', 'rover', 'ridge', 'keel', 'chine_z', 'nose')})
D['archetypes'] = A
json.dump(D, open('explorer_results.json', 'w'))
