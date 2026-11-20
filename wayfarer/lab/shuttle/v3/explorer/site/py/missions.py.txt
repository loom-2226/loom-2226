"""Mission-profile evaluation on top of engine results. ALL bodies. ALL sponsors. 2026-2226.
Profiles and thresholds live in missions.json and are ASSUMPTIONS, editable in the explorer."""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..'))
import step2_propulsion as S2
MJ = json.load(open(os.path.join(HERE, 'missions.json')))

def evaluate(r, prof, mj=MJ):
    """r: engine result (needs dry_t, params, touchdown_heavy_ms, crossrange_km, max_turn_dps). Returns checks with margins."""
    p = r['params']; seats = p['seats']; crew = prof['crew']; pax = max(seats - crew, 0)
    dry = r['dry_t'] + (mj['rover_kit_t']['value'] if prof['rover_needed'] and not p['rover'] else 0.0)
    pay = prof['payload_t'] + prof['t_per_person'] * seats
    legs = [tuple(x) for x in mj['legs'][prof['legs']]['dv']]
    need = S2.water(dry, pay, legs)[0]; carried = p['water_t'] + prof['sprint_t']
    C = prof['checks']; out = []
    def chk(name, val, lim, sense, unit):
        ok = val <= lim if sense == '<=' else val >= lim
        out.append(dict(name=name, value=round(val, 2), limit=lim, sense=sense, unit=unit, ok=bool(ok),
                        headroom=round((lim - val) if sense == '<=' else (val - lim), 2)))
    chk('Water required vs carried' + (' (incl. sprint kit)' if prof['sprint_t'] else ''), need, round(carried, 2), '<=', 't')
    if C.get('heavy_landing_max_ms', 999) < 999:
        refill = prof.get('seawater_refill', False) and r.get('refill_h') is not None
        if refill:
            chk('Water touchdown, light (refill at sea)', r['touchdown_light_ms'], C['heavy_landing_max_ms'], '<=', 'm/s')
            chk('Seawater refill time', r['refill_h'], C.get('refill_max_h', 2.0), '<=', 'h')
        else:
            chk('Heavy water touchdown (climb water aboard)', r['touchdown_heavy_ms'], C['heavy_landing_max_ms'], '<=', 'm/s')
    if C.get('crossrange_min_km', 0) > 0: chk('Reach from orbit', r['crossrange_km'], C['crossrange_min_km'], '>=', 'km')
    if C.get('turn_min_dps', 0) > 0: chk('Max turn at 8 g', r['max_turn_dps'], C['turn_min_dps'], '>=', 'deg/s')
    if 'evacuees_min' in C: chk('Seats for evacuees (couches - crew)', pax, C['evacuees_min'], '>=', 'people')
    if prof['rover_needed']: out.append(dict(name='Rover', value='in core' if p['rover'] else f"kit +{mj['rover_kit_t']['value']} t from Wayfarer", ok=True, limit='', sense='', unit='', headroom=''))
    return dict(profile=prof['name'], people=dict(couches=seats, crew=crew, passengers=pax), dry_for_mission_t=round(dry, 2),
                payload_t=round(pay, 2), water_required_t=need, water_carried_t=round(carried, 2), checks=out, ok=all(c['ok'] for c in out))
