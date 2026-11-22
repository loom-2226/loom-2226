"""Is a Tic Tac (capsule) redesign of the Weave shuttle materially worth it? Same-rules comparison. NON-CANON.
ALL bodies. ALL sponsors. 2026-2226.

Selected shuttle: 13.02 m lifting body, run through closure_v2 / closure_screen / step 5 (as committed).
Tic Tac: 12.8 m x 3.8 m capsule (hemispherical ends), run through the SAME rules where they apply:
  - hull structure scales with wetted area from the host's post-Osteon value; entry TPS with entry planform (engine.evaluate rules)
  - no wings, no lift fans; floats only if the hull alone does not give the W2 1.5x reserve
  - power unit for cooling / flywheel recharge kept: ASSUMPTION 1.0 t (the host's fan reactor was 3.8 t, sized for fan lift)
  - field-off fallback without wings: torch-only, or parachutes (ASSUMPTION ~3.5% of landing mass, typical of large capsule chutes)
  - same module (9.0 t installed), flywheel iterated on lift-off mass, same 23.1 t tank, cushion ascent profile
  - hypersonic Newtonian L/D, Earth entry crossrange / peak heat with aero_test.entry, as the engine does for the host
Not done: capsule afloat stability (W6, a round hull rolls), structural detail, render."""
import os, sys, json, math
import numpy as np
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
import closure_v2 as V2, closure_screen as CS
E = CS.E; AT = E.AT
OUT = {}
# ---------------------------------------------------------------- baseline (selected shuttle)
v = V2.run(4.0, length=13.02); r, M = CS.mass_close(); g = CS.gates(r, M); S5 = json.load(open(os.path.join(H, 'step5_geometry.json')))['lengths']['13.02']
OUT['shuttle'] = dict(length=13.02, hull_m3=r['hull_m3'], inner_m3=r['inner_m3'], swet_m2=r['swet_m2'], planform_m2=r['planform_m2'], dry_t=M['dry_t'],
                      margin_t=M['margin_t'], water_t=g['earth_and_hot_egress_with_cushion_t']['value'], buoyancy=(g['buoyancy_total_m3']['value'], g['buoyancy_total_m3']['limit']),
                      interior_spare_m3=S5['layout']['water_margin_m3'], hyper_LD=r['hyper_LD'], crossrange_km=r['crossrange_km'], peak_heat=r['peak_heat_Wcm2'],
                      field_max_radius=S5['field_clearance']['flight']['max_radius_m'], fallback='wings + fans: field-off landing at <= 50 m/s heavy (4.5% uplift), aero recovery from airspeed',
                      bay='needs the 0.22 m collar; docked aft clearance 0.28 m', mass_items=r['mass_t'])
# ---------------------------------------------------------------- capsule mesh
Lc, Rc = 12.8, 1.9
def capsule(n_th=48, n_x=40, n_cap=12):
    V = []; T = []
    xs = np.r_[[Rc - Rc * math.cos(t) for t in np.linspace(0, math.pi / 2, n_cap)], np.linspace(Rc, Lc - Rc, n_x)[1:-1], [Lc - Rc + Rc * math.sin(t) for t in np.linspace(0, math.pi / 2, n_cap)]]
    rs = [math.sqrt(max(Rc ** 2 - (Rc - x) ** 2, 0)) if x < Rc else (math.sqrt(max(Rc ** 2 - (x - (Lc - Rc)) ** 2, 0)) if x > Lc - Rc else Rc) for x in xs]
    th = np.linspace(0, 2 * math.pi, n_th, endpoint=False)
    rings = [np.c_[np.full(n_th, x), r_ * np.cos(th), r_ * np.sin(th)] for x, r_ in zip(xs, rs)]
    for k in range(len(rings) - 1):
        A, B = rings[k], rings[k + 1]
        for i in range(n_th):
            j = (i + 1) % n_th; T += [(A[i], B[i], A[j]), (A[j], B[i], B[j])]
    T = np.array(T); n, a = AT.geom(T); keep = a > 1e-9
    return T[keep]
T = capsule(); n, A = AT.geom(T); Swet = float(A.sum())
Vh = math.pi * Rc ** 2 * (Lc - 2 * Rc) + 4 / 3 * math.pi * Rc ** 3; ri = Rc - 0.12; Vin = math.pi * ri ** 2 * (Lc - 2 * Rc) + 4 / 3 * math.pi * ri ** 3
plan = 2 * Rc * (Lc - 2 * Rc) + math.pi * Rc ** 2                                # broadside entry planform
# ---------------------------------------------------------------- capsule mass (same rules)
mi = dict(r['mass_t'])
cap = dict(mi, hull_structure=mi['hull_structure'] * Swet / r['swet_m2'], entry_tps=mi['entry_tps'] * plan / r['planform_m2'], wings=0.0, fans_reactor=1.0)
pay = M['payload_t']; tank = 23.1
def close(m_items, floats_m3, chutes):
    host = sum(v for k, v in m_items.items() if k != 'floats') + 0.03 * floats_m3; fly = 0.0
    for _ in range(30):
        lift = host + CS.MODULE['installed_t'] + fly + pay + tank; Es, P, fn = CS.cushion_energy(lift)
        ch = 0.035 * (host + CS.MODULE['installed_t'] + fn + pay + 2.0) if chutes else 0.0
        if abs(fn - fly) < 1e-7: break
        fly = fn
    dry = host + CS.MODULE['installed_t'] + fly + ch
    return dict(dry_t=round(dry, 2), flywheel_t=round(fly, 3), chutes_t=round(ch, 2), host_t=round(host, 2))
res = {}
for label, chutes in (('torch-only fallback', False), ('+ parachutes', True)):
    c = close(cap, 0.0, chutes); disp = (c['dry_t'] + pay + tank) / 1.025
    floats = max(0.0, 1.5 * disp - Vh); c = close(cap, floats, chutes) if floats > 0 else c
    dv_h = CS.climb_dv(2e3)[0]; legs = [(200, .1, 1), (round(3000 - dv_h), 1.4, 9.81), (6400, .8, 9.81), (400, .1, 1)]
    w, sh = E.water_chk(c['dry_t'], pay, legs); w_torch_land, _ = E.water_chk(c['dry_t'], pay, [(150, 1.3, 9.81)])
    res[label] = dict(c, floats_m3=round(floats, 1), margin_t=round(52.5 - c['dry_t'], 2), water_t=w, water_ok=w <= tank and not sh,
                      buoyancy=(round(Vh + floats, 1), round(1.5 * disp, 1)), torch_landing_water_t=w_torch_land)
# interior need with the same allocations (cabin, water, well, aft without fan power, avionics) + module, flywheel, install, chutes 1 m3
need = 21.0 + 1.05 * tank + 6.0 + 7.0 + 0.04 * 6.0 + 3.0 + 2.0 + res['+ parachutes']['flywheel_t'] / 2 + 0.3
# aero: hypersonic L/D (side-on at incidence) and Earth entry, same call as the engine
hyp = max((float(np.divide(*AT.newtonian(T, plan, Swet, a, 1.2))), a) for a in range(10, 56, 5))
m_entry = res['torch-only fallback']['dry_t'] + pay + 0.8 * tank
vv = dict(T=T, S_body=plan, S_wing=0.0, span=2 * Rc, Swet=Swet, Abase=math.pi * Rc ** 2, sharp=False, rn=Rc)
e = AT.entry(vv, 'Earth', m_entry * 1e3, 40); e_best = AT.entry(vv, 'Earth', m_entry * 1e3, hyp[1])
OUT['tictac'] = dict(length=Lc, diameter=2 * Rc, hull_m3=round(Vh, 1), inner_m3=round(Vin, 1), swet_m2=round(Swet, 1), planform_m2=round(plan, 1),
                     interior_need_m3=round(need, 1), interior_spare_m3=round(Vin - need, 1), cases=res,
                     hyper_LD=round(hyp[0], 3), hyper_LD_alpha=hyp[1], crossrange_km_a40=round(e['crossrange_km']), crossrange_km_best=round(e_best['crossrange_km']),
                     peak_heat_a40=round(e['peak_q_Wcm2']), peak_g_a40=round(e['peak_g'], 2), field_max_radius=6.4,
                     bay='12.8 m: no collar; width = the 3.8 m exit limit exactly (0.5 m each side, no further margin)',
                     fallback='no wings or fans: field-off = torch (needs altitude, water) or parachutes; no aero recovery, no gliding landing',
                     mass_items=cap)
OUT['header'] = 'ALL bodies. ALL sponsors. 2026-2226.'; OUT['doc'] = __doc__
json.dump(OUT, open(os.path.join(H, 'tictac_vs_shuttle.json'), 'w'), indent=1, default=float)
print(json.dumps({k: {kk: vv_ for kk, vv_ in v_.items() if kk != 'mass_items'} for k, v_ in OUT.items() if k in ('shuttle', 'tictac')}, indent=1, default=float))
