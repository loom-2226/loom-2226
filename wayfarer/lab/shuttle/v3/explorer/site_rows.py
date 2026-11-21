"""Compact explorer rows for the web page (used by build_site.py and, in the browser, by Pyodide).
Repeated strings are replaced by indexes into NAMES / MASSKEYS (unknown strings pass through as text).
ALL bodies. ALL sponsors. 2026-2226."""
METRICS = ['dry_t', 'docked_t', 'hull_m3', 'inner_m3', 'crossrange_km', 'glide_LD', 'touchdown_heavy_ms', 'touchdown_light_ms',
           'earth_water_t', 'earth_margin_t', 'hot_egress_water_t', 'venus_water_t', 'max_turn_dps', 'capability_count',
           'interior_margin_m3', 'fit_r_m', 'hyper_LD', 'peak_heat_Wcm2', 'buoyancy_total_m3', 'buoyancy_need_m3', 'refill_h']
PARAMS = ['wing', 'span', 'chord', 'fan_m2', 'floats_m3', 'water_t', 'seats', 'rover', 'fan_venus', 'desal', 'ridge', 'shoulder_z', 'shoulder_y',
          'keel', 'chine_z', 'belly_w', 'nose', 'base', 'wildcard', 'length']
NAMES = ['Bay fit radius (stowed hull only)', 'Dry mass', 'Earth trip water: required vs carried', 'Interior: usable vs allocated',
         'Buoyancy: hull + floats vs 1.5 x displaced', 'Buoyancy: hull alone vs displaced',
         'Light water landing (2 m waves)', 'Heavy water landing (~1 m waves)', 'Hot egress water vs tank + sprint', 'Venus water vs tank + kit water',
         'Moon water (vacuum kit) vs tank', 'Mars water vs tank',
         'Water required vs carried', 'Water required vs carried (incl. sprint kit)', 'Water touchdown, light (refill at sea)', 'Seawater refill time',
         'Heavy water touchdown (climb water aboard)', 'Reach from orbit', 'Max turn at 8 g', 'Seats for evacuees (couches - crew)', 'Rover',
         'Torch thrust meets every leg', 'Water touchdown at mission mass (refill at sea)', 'Water touchdown at mission mass (climb water aboard)',
         'Seawater refill time (conditional: reactor + unit throughput)']
MASSKEYS = ['hull_structure', 'entry_tps', 'wings', 'cabin', 'water_tank', 'rover', 'torch', 'belly_rcs', 'power_dist', 'custody', 'avionics',
            'gear_door', 'crash_mounts', 'floats', 'desal', 'fans_reactor', 'cabin_wall']
_IX = {n: i for i, n in enumerate(NAMES)}
def nm(s): return _IX.get(s, s)
def g3(g): return [nm(g['name']), g['value'], g['limit'], g['sense'], g['headroom'], g['rel'], g['cls']]   # sources: data.json gate_sources
def r2(x): return round(float(x), 2)
def row(r, full=True):
    p = r['params']
    o = dict(i=r['id'], f=int(bool(r['feasible'])), pa=int(bool(r.get('pareto', False))), g=r.get('gen', 0), x=r['fails'],
             m=[r.get(k) for k in METRICS], p=[p.get(k) for k in PARAMS], c=[int(bool(v)) for v in r['capabilities'].values()],
             lim=nm(r.get('limiting')), ih=r.get('input_hash'), mv=r.get('model_version'))
    if full:
        d = r['draw']
        o.update(ms=[r['mass_t'].get(k, 0.0) for k in MASSKEYS], fan=r['fans']['MWe'], gt=[g3(g) for g in r['gates']], cm=[g3(g) for g in r['capability_margins']],
                 d={k: [[r2(a), r2(b)] for a, b in v] for k, v in d.items()},
                 os=r.get('osteon'), cv=r.get('caveats'), ks=r.get('kit_status'), ld=r.get('land'),
                 mi={k: dict(ok=int(m['ok']), tm=m.get('touchdown_mass_t'), kt=m.get('kits'), wr=m['water_required_t'], wc=m['water_carried_t'], pe=[m['people']['couches'], m['people']['crew'], m['people']['passengers']],
                             ch=[[nm(c['name']), c['value'], c['limit'], c['sense'], c['unit'], int(c['ok'])] for c in m['checks']]) for k, m in r.get('missions', {}).items()})
    return o
