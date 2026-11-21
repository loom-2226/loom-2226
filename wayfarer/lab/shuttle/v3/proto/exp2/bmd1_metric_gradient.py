"""Hypothesis A (kT 2026-11-21): metric-gradient assistance - engineer the shuttle's geodesic, not a force on it.
Test (kT): derive the metric, derive the stress-energy it requires, see whether the numbers close. Near Earth and in deep space.
NON-CANON prototype lane. ALL bodies. ALL sponsors. 2026-2226.

Two GR routes to "the shuttle free-falls upward relative to the planet":
 (S) static: a comoving potential bump whose gradient cancels g and adds 0.5 g up inside the domain (weak field, Poisson).
     Minimal source for a UNIFORM interior field g' in a sphere of radius R: surface density sigma = (3 g'/4 pi G) cos(theta)
     (gravitational analogue of a uniformly polarised sphere). Positive pole mass = 3 g' R^2 / (4 G); the other pole is NEGATIVE.
 (D) dynamic: a warp-type shift-vector bubble carrying a free-falling interior at v relative to the planet.
     Alcubierre-class energy, order of magnitude (Pfenning-Ford): E ~ -(1/12)(v/c)^2 (R^2/Delta) c^4/G.
     Bobrick & Martire (2021): an accelerating warp metric must still obey 4-momentum conservation - 'any warp drive requires propulsion'.
"""
import json, math, os
H = os.path.dirname(os.path.abspath(__file__))
G, c = 6.674e-11, 2.998e8; m = 61e3; g = 9.81
R, DELTA, v = 10.0, 1.0, 44.1
gp = 1.5 * g
static = dict(interior_field_ms2=gp, pole_mass_kg=f'{3 * gp * R ** 2 / (4 * G):.2e}', pole_mass_over_shuttle=f'{3 * gp * R ** 2 / (4 * G) / m:.1e}',
              note='needs NEGATIVE mass at one pole; a +/- mass pair self-accelerates (Bondi 1957): reactionless in appearance, works anywhere - no planetary limit')
dyn = dict(speed_ms=v, radius_m=R, wall_m=DELTA, energy_J=f'{-(1 / 12) * (v / c) ** 2 * R ** 2 / DELTA * c ** 4 / G:.1e}',
           mass_equivalent_kg=f'{(1 / 12) * (v / c) ** 2 * R ** 2 / DELTA * c ** 2 / G:.1e}', sign='negative (exotic) in Alcubierre form; positive-energy subluminal shells need very large ADM mass (Fuchs et al. 2024)',
           momentum='changing v changes the bubble 4-momentum: a partner is still required')
# The law that closes, IF the canon M2 miracle's stress-energy waiver is extended: 'gravity steering'
# Field may impose on its free-falling interior a uniform acceleration up to k * g_P, g_P = Newtonian field of the partner P
# (the body whose Hill sphere contains the domain). Reaction momentum -> P. Onboard energy = F . v_rel(P).
ENV = {'Earth surface': (9.81, 0.0), 'LEO 400 km (vs Earth)': (8.69, 7.67e3), 'Moon surface': (1.62, 0.0), 'Mars surface': (3.71, 0.0),
       'Titan surface': (1.352, 0.0), '1 km asteroid surface': (2.8e-4, 0.0), 'Deep space 1 AU (partner Sun)': (5.93e-3, 29.8e3)}
k = 1.5
steer = {}
for name, (gP, vrel) in ENV.items():
    F = k * m * gP
    steer[name] = dict(g_partner=gP, max_force_kN=round(F / 1e3, 3), max_accel_g=round(k * gP / g, 4),
                       hover_power='~0 (v_rel = 0): losses only' if vrel == 0 else None,
                       power_at_max_force_GW_if_moving_with_v_rel=round(F * vrel / 1e9, 2) if vrel else None)
out = dict(header='ALL bodies. ALL sponsors. 2026-2226.', lane='PROTOTYPE (non-canon) hypothesis A, metric-gradient', derivation=__doc__.split('\n', 3)[3].strip(),
  GR_static=static, GR_dynamic=dyn,
  GR_verdict='Numbers do NOT close in GR. Static route: ~1.7e13 kg per pole (3e8 x the shuttle), with negative mass, and it is universal (no planetary limit). '
             'Dynamic route: ~1e31 J (~1e14 kg) of exotic energy just to move at 44 m/s, and it still needs a momentum partner to accelerate. '
             'Steering the path instead of the force is a change of description, not of bookkeeping.',
  canon_note='Canon M2 already waives GR stress-energy pricing for Wayfarer (0.268c from a ~2 GJ bank, CANON II §5). A closes only if that waiver extends to small, near-body, powered domains. That is a canon-policy choice, not physics.',
  gravity_steering_law=dict(statement='Domain imposes on its free-falling interior a uniform acceleration up to k x g_P (k ~ 1.5), where g_P is the Newtonian field of the partner P whose Hill sphere contains it. Reaction momentum to P; onboard energy F . v_rel(P).',
                            environments=steer,
                            properties=['interior stays locally inertial (crew ~0 g during lift)', 'momentum closes with P; energy local and reference-independent',
                                        'natural planetary limit: capacity ~1.5 g at Earth, ~0.2 g at Titan, 0.0009 g in deep space at 1 AU - no remass revolution',
                                        'cheap to hover and lift slowly near a body (v_rel ~ 0); expensive to change fast velocities (LEO: ~7 GW at max force) - the inverse of a rocket'],
                            caveats=['g_P is not a local observable (equivalence principle): the law is NONLOCAL by construction, like canon §7.1b',
                                     'stress-energy is NOT derived; it rides on the M2 waiver',
                                     'boundary vs water/air remains open (lift from a floating shuttle)']),
  other_branches=dict(B_path_shortening='a change of spatial geometry between endpoints: belongs with W3 (displacement), not W2',
                      C_isolation_plus_fans='fans need momentum exchange with the air; isolation removes drag, not weight. Dropped.'))
json.dump(out, open(os.path.join(H, 'bmd1_metric_gradient.json'), 'w'), indent=1)
if __name__ == '__main__':
    print(static); print(dyn)
    for k_, v_ in steer.items(): print(k_, v_)
