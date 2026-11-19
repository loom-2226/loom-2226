"""B4 cabin options for more room, with the heat-shield fix, against the G8 docked-dry envelope (34.2 t).
NON-CANON research screen. ALL bodies. ALL sponsors. 2026-2226. Every factor is an ASSUMPTION (Claude, for kT).
Base: b4_mass_gate.py sampling of the 13 core components. Changes per option:
  TPS fix (all B4 options): base entry TPS x (heat load ratio)^n, n 0.5-1.0 (ablator thickness ~ heat load^0.5..1);
      Venus heat load B4/v1 = 1564/1191 (aero_results.json).
  A  one Ti capsule: ring-stiffened cylinder D 1.9 m with hemispherical heads, 6.5 m long (Komsomolets-class Ti hull
     precedent at ~1,000 m). Shell mass = twin-sphere shell x (capsule/twin-sphere ratio 2.6-3.6 from thin-shell sizing:
     spheres buckling-governed t/R~0.018, stiffened cylinder equivalent t 28-36 mm over 39 m2).
  B  split: a big light 1-bar cabin (composite, rated +-1 bar so Titan's 1.5 bar is fine) for all flying, and ONE 2.1 m Ti
     sphere as the Venus surface refuge and rover, carried in the detachable Venus/Titan kit (Gate A2: kit leaves docked dry).
     Cabin 30 m3, wall area ~55 m2 at 8-15 kg/m2 plus 0.2-0.4 t hatches/fittings. Pod and rover chassis move to the kit."""
import json, os, math, numpy as np
import b4_mass_gate as G
HERE = os.path.dirname(os.path.abspath(__file__))
A = json.load(open(os.path.join(HERE, 'aero_results.json')))
HL = A['entry']['Venus']['B4 double fold']['heat_load_MJm2'] / A['entry']['Venus']['v1 biconic']['heat_load_MJm2']
N = 200000; LIMIT = G.LIMIT
def run(opt, seed=7):
    rng = np.random.default_rng(seed); tot, parts = G.sample(N, True, rng); kit = np.zeros(N)
    tps_add = parts['base_entry_tps_core_t'] * (HL ** rng.uniform(.5, 1.0, N) - 1); tot = tot + tps_add
    vol = 2 * 4 / 3 * math.pi * .95 ** 3 + .4
    if opt == 'A':
        shell = parts['pressure_pod_titanium_shell_t']; tot = tot + shell * (rng.uniform(2.6, 3.6, N) - 1)
        tot = tot + parts['pressure_pod_fittings_seals_t'] * (rng.uniform(1.1, 1.4, N) - 1)    # one long hull, bigger hatch, no tunnel
        vol = math.pi * .95 ** 2 * (6.5 - 1.9) + 4 / 3 * math.pi * .95 ** 3
    if opt == 'B':
        pod = parts['pressure_pod_titanium_shell_t'] + parts['pressure_pod_fittings_seals_t']; rover = parts['folding_rover_chassis_t']
        tot = tot - pod - rover
        one = (parts['pressure_pod_titanium_shell_t'] / (2 * (1.9 / 2.5) ** 3)) * (2.1 / 2.5) ** 3 + (parts['pressure_pod_fittings_seals_t'] / (2 * (1.9 / 2.5) ** 2)) * (2.1 / 2.5) ** 2
        kit = one + rover
        cabin = 55 * rng.uniform(8, 15, N) / 1e3 + rng.uniform(.2, .4, N); tot = tot + cabin
        vol = 30.0
    pc = lambda a: {k: round(float(np.percentile(a, q)), 2) for k, q in (('p5', 5), ('mid', 50), ('p95', 95))}
    return dict(core_dry_t=pc(tot), pass_G8=round(float((tot <= LIMIT).mean()), 3), crew_pressurised_m3=round(vol, 1),
                tps_fix_add_t=pc(tps_add), kit_added_t=pc(kit) if opt == 'B' else None)
out = dict(header='ALL bodies. ALL sponsors. 2026-2226.', status='NON-CANON screen; all factors ASSUMPTIONS', G8_limit_t=LIMIT,
           heat_load_ratio_venus=round(HL, 3), v1=dict(core_dry_t={'mid': 30.02}, pass_G8=.958, crew_pressurised_m3=round(4 / 3 * math.pi * 1.25 ** 3, 1)),
           B4_twin_spheres_tps_fixed=run('0'), A_one_capsule=run('A'), B_split_cabin_venus_pod_in_kit=run('B'))
json.dump(out, open(os.path.join(HERE, 'b4_cabin_options.json'), 'w'), indent=1); print(json.dumps(out, indent=1))
