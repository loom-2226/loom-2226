"""Mission-profile evaluation on top of engine results. ALL bodies. ALL sponsors. 2026-2226.
Profiles and thresholds live in missions.json and are ASSUMPTIONS, editable in the explorer.
Corrections 2026-11-21 (Sol review): touchdown mass is computed per mission (dry + mission payload + the water still
needed after landing, or a reserve if it refills at sea); a leg whose demanded acceleration the 7.7 GW torch cannot
give fails the mission; kits are listed as carried / not demonstrated."""
import os, sys, json, math
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..'))
import engine as E
MJ = json.load(open(os.path.join(HERE, 'missions.json')))

def _land_index(legs):
    for i, (dv, a, g) in enumerate(legs):
        if a >= 1.0 and g > 1.0: return i          # first powered leg in a gravity field = landing
    return None

def touchdown(r, m_t):
    L = r.get('land')
    if not L: return None
    W = m_t * 1e3 * 9.81 - L['static_kN'] * 1e3
    return round(math.sqrt(2 * max(W, 1.0) / (1.225 * L['S'] * L['clmax'])), 1)

def evaluate(r, prof, mj=MJ):
    p = r['params']; seats = p['seats']; crew = prof['crew']; pax = max(seats - crew, 0)
    dry = r['dry_t'] + (mj['rover_kit_t']['value'] if prof['rover_needed'] and not p['rover'] else 0.0)
    pay = prof['payload_t'] + prof['t_per_person'] * seats
    legs = [tuple(x) for x in mj['legs'][prof['legs']]['dv']]
    need, short = E.water_chk(dry, pay, legs); carried = p['water_t'] + prof['sprint_t']
    C = prof['checks']; out = []
    def chk(name, val, lim, sense, unit):
        ok = val <= lim if sense == '<=' else val >= lim
        out.append(dict(name=name, value=round(val, 2), limit=lim, sense=sense, unit=unit, ok=bool(ok),
                        headroom=round((lim - val) if sense == '<=' else (val - lim), 2)))
    chk('Water required vs carried' + (' (incl. sprint kit)' if prof['sprint_t'] else ''), need, round(carried, 2), '<=', 't')
    out.append(dict(name='Torch thrust meets every leg', value='yes' if not short else 'short on leg ' + ', '.join(str(i + 1) for i in short),
                    limit='', sense='', unit='', ok=not short, headroom=''))
    li = _land_index(legs); m_td = None
    if C.get('heavy_landing_max_ms', 999) < 999 and li is not None and legs[li][2] > 9:
        refill = prof.get('seawater_refill', False) and r.get('refill_h') is not None
        after = 1.0 if refill else E.water_chk(dry, pay, legs[li + 1:])[0] + 1.0
        m_td = round(dry + pay + after, 2); v = touchdown(r, m_td)
        chk('Water touchdown at mission mass' + (' (refill at sea)' if refill else ' (climb water aboard)'), v, C['heavy_landing_max_ms'], '<=', 'm/s')
        if refill: chk('Seawater refill time (conditional: reactor + unit throughput)', r['refill_h'], C.get('refill_max_h', 2.0), '<=', 'h')
    if C.get('crossrange_min_km', 0) > 0: chk('Reach from orbit', r['crossrange_km'], C['crossrange_min_km'], '>=', 'km')
    if C.get('turn_min_dps', 0) > 0: chk('Max turn at 8 g', r['max_turn_dps'], C['turn_min_dps'], '>=', 'deg/s')
    if 'evacuees_min' in C: chk('Seats for evacuees (couches - crew)', pax, C['evacuees_min'], '>=', 'people')
    kits = []
    if prof['sprint_t']: kits.append('sprint water %.1f t: carried, fit/deploy NOT demonstrated' % prof['sprint_t'])
    if prof['rover_needed']: kits.append('rover: ' + ('in core' if p['rover'] else 'kit +%.2f t from Wayfarer, fit demonstrated for B4-S well only' % mj['rover_kit_t']['value']))
    return dict(profile=prof['name'], people=dict(couches=seats, crew=crew, passengers=pax), dry_for_mission_t=round(dry, 2),
                payload_t=round(pay, 2), touchdown_mass_t=m_td, water_required_t=need, water_carried_t=round(carried, 2),
                thrust_short_legs=short, kits=kits, checks=out, ok=all(c['ok'] for c in out))
