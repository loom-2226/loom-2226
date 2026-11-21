"""Experiment 2, W3: a small metric displacement (50-100 m) - atmosphere vs vacuum, and the boundary unknown. NON-CANON.
ALL bodies. ALL sponsors. 2026-2226.
Three boundary hypotheses are kept apart; none is established. Ordinary aerodynamics is used ONLY for hypothesis 1, where the
hull (or a hull-sized region) actually moves through the air. Energy terms are separated: creation, transition, environment, recovery."""
import os, json, math
H = os.path.dirname(os.path.abspath(__file__))
G, RHO, P0, GAMMA = 9.81, 1.225, 101.3e3, 1.4
M = 60.0                                  # t, extraction mass
A_NOSE, A_SIDE = 10.0, 60.0               # m^2 frontal / broadside [GEOMETRY, rounded]
V_HULL = 77.0                             # m^3 hull (#2643-class) [GEOMETRY]
V_ENV = {'hull-hugging (0.3 m)': 110.0, 'canon-style 1.5 m clearance': 420.0}   # m^3 region volume [ASSUMPTION]

def conventional(d, glim=8.0):            # bang-bang lateral sidestep at the 8 g limit
    a = glim * G; return math.sqrt(4 * d / a)
def h1_aero(d, t, A, cd):                 # region moves through the air like a body: drag work + shock regime
    v = d / t; return dict(mean_speed_ms=round(v), mach=round(v / 340, 2), energy_MJ=round(0.5 * RHO * v * v * cd * A * d / 1e6, 1))
def h2_boundary(V):                       # air is neither carried nor swapped: vacate a volume at departure, displace one at arrival
    return round(2 * P0 * V / (GAMMA - 1) / 1e6, 0)    # upper bound: two volumes' worth of internal energy disturbed (MJ)
rows = []
for d in (50, 100):
    tc = conventional(d)
    for t in (0.1, 0.3, 1.0):
        rows.append(dict(displacement_m=d, metric_time_s=t, conventional_8g_time_s=round(tc, 2),
                         H1_nose_on=h1_aero(d, t, A_NOSE, 0.5), H1_broadside=h1_aero(d, t, A_SIDE, 1.2)))
h2 = {k: dict(bound_MJ=h2_boundary(v), tnt_kg_equiv=round(h2_boundary(v) / 4.184, 0)) for k, v in V_ENV.items()}
# endgame survival: interceptor at 30 g lateral, last t_go seconds; what lateral offset can it still null?
endgame = []
for tgo in (0.3, 0.5, 1.0):
    endgame.append(dict(t_go_s=tgo, interceptor_30g_can_null_m=round(0.5 * 30 * G * tgo ** 2, 1), shuttle_8g_jink_m=round(0.5 * 8 * G * tgo ** 2, 1),
                        verdict='a 50-100 m step inside t_go defeats the endgame' if 0.5 * 30 * G * tgo ** 2 < 50 else 'interceptor can still correct 50 m'))
out = dict(header='ALL bodies. ALL sponsors. 2026-2226.', lane='PROTOTYPE (non-canon) experiment 2, W3',
  correction='The lane note figure 0.2-0.9 GJ assumed a 1 km hop through air with a canon-style 1.5 m wall. It is conditional on hypothesis 1 or 2 below, not universal.',
  hypotheses={
   'H1 strong interaction (region moves through the air)': 'ordinary aerodynamics applies: a 100 m step in 1 s is subsonic and cheap (MJ); in 0.1 s it is Mach 3 with a sonic boom and tens of MJ to GJ. Applies only if the region physically sweeps the intervening air.',
   'H2 interaction only at the two boundaries': 'nothing in between is touched. Departure leaves a void, arrival must push air out: bounded by ~p0 V per event, a sharp bang (lightning-like) scaled by region volume. If the transition SWAPS the contents of the two volumes, the term falls toward zero: near-silent.',
   'H3 needs a cleared boundary / operating volume': 'the wall may not cut matter (canon domain continuity applied literally). Air is matter, so in atmosphere it fails unless the air is first expelled (~p0 V again); in practice VACUUM ONLY.'},
  energy_ledger=dict(field_creation='UNKNOWN (canon Wayfarer bank 2 GJ for a 1,900 m^2 boundary; a hull-sized region scales by an unknown law)',
                     transition='canon ENERGY-B: level displacement changes no ordinary mechanical energy; vertical steps owe m g dz (60 t: 0.06 GJ per 100 m)',
                     environment='H1: drag/shock work; H2: ~p0 V per boundary event, or ~0 if swapped; H3: zero in vacuum, impossible or p0 V in air',
                     recovery='UNKNOWN fraction of creation energy returned; heat rejected through the shuttle radiators'),
  displacement_rows=rows, H2_boundary_bound=h2, endgame=endgame,
  vacuum=dict(environment_term=0, value='a 50-100 m step with no velocity change and no crew load defeats terminal guidance of kinetic interceptors and breaks laser dwell; docking/debris uses too',
              canon_limits_superseded='§18A (metric not a close-combat dodge), §5/§9 ramp and path card, plant scale',
              invariants_kept='no momentum or energy from nothing: level step changes neither; no FTL; crew and hull remain inside one continuous domain'),
  decisive_unknown='What the field boundary does to matter during a transition: carries/swaps the arrival-volume contents, pushes them aside, or fails if matter is present. '
                   'This one property sets the atmospheric signature (silent / bang / impossible), whether a near-ground step is possible, and is the same unknown that decides whether a W2 field can start from a floating shuttle.')
json.dump(out, open(os.path.join(H, 'exp2_w3.json'), 'w'), indent=1)
if __name__ == '__main__':
    for r in rows: print(r)
    print(h2); print(endgame)
