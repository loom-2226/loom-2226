"""Compact explorer rows for the web page (used by build_site.py and, in the browser, by Pyodide).
ALL bodies. ALL sponsors. 2026-2226."""
METRICS = ['dry_t', 'docked_t', 'hull_m3', 'inner_m3', 'crossrange_km', 'glide_LD', 'touchdown_heavy_ms', 'touchdown_light_ms',
           'earth_water_t', 'earth_margin_t', 'hot_egress_water_t', 'venus_water_t', 'max_turn_dps', 'capability_count',
           'interior_margin_m3', 'fit_r_m', 'hyper_LD', 'peak_heat_Wcm2', 'buoyancy_total_m3', 'buoyancy_need_m3']
PARAMS = ['wing', 'span', 'chord', 'fan_m2', 'floats_m3', 'water_t', 'seats', 'rover', 'fan_venus', 'ridge', 'shoulder_z', 'shoulder_y',
          'keel', 'chine_z', 'belly_w', 'nose', 'base']
def g3(g): return [g['name'], g['value'], g['limit'], g['sense'], g['headroom'], g['rel'], g['cls']]   # sources: data.json gate_sources
def row(r, full=True):
    p = r['params']
    o = dict(i=r['id'], f=int(bool(r['feasible'])), pa=int(bool(r.get('pareto', False))), g=r.get('gen', 0), x=r['fails'],
             m=[r.get(k) for k in METRICS], p=[p.get(k) for k in PARAMS], c=[int(bool(v)) for v in r['capabilities'].values()],
             lim=r.get('limiting'), ih=r.get('input_hash'), mv=r.get('model_version'))
    if full:
        o.update(ms=r['mass_t'], fan=r['fans']['MWe'], gt=[g3(g) for g in r['gates']], cm=[g3(g) for g in r['capability_margins']], d=r['draw'],
                 mi={k: dict(ok=int(m['ok']), wr=m['water_required_t'], wc=m['water_carried_t'], pe=m['people'],
                             ch=[[c['name'], c['value'], c['limit'], c['sense'], c['unit'], int(c['ok']), c['headroom']] for c in m['checks']]) for k, m in r.get('missions', {}).items()})
    return o
