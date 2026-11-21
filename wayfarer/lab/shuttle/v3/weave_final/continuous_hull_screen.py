"""Continuous active hull hypothesis: narrow screen (kT + Sol brief, 2026-11-22). NON-CANON research.
ALL bodies. ALL sponsors. 2026-2226.

Question (stopping condition): does a continuous field-generating hull change the existing field's controllable
behaviour, or is it only a different means of generating the same field? Specifically: can surface-controlled asymmetry
give lasting ordinary velocity after shutdown, with conservation intact? Existing physics only.

Existing model (lane): fields are prescribed geometry on flat slices, slow limit, c = 1 units where convenient.
  shift  b(x, t): matter law  L = 1/2 |xdot - b|^2      ->  dw_i/dt = -w_j d_i b_j,   w = xdot - b
  lapse/potential Phi(x, t) (the W2 cushion type; the lane's "lapse dash"): xddot = -grad Phi (acceleration field)
  Required stress-energy (3+1): for the shift, E = -K^2/16pi with K_ij = -1/2 (d_i b_j + d_j b_i): nonzero only where b varies.
Three checks:
  A. Where must the field's GR source sit for the Tic Tac's R 15 / d 2 field? (hull skin vs wall shell)
  B. Asymmetric shift (any profile, surface-steered): final ordinary velocity of a hull starting at rest.
  C. Asymmetric potential (directional gradient): final ordinary velocity, and the field's own momentum (conservation).
"""
import os, json, math
import numpy as np
H = os.path.dirname(os.path.abspath(__file__))
R_F, D_F, HULL_R = 15.0, 2.0, 6.4                     # field radius / wall (lane), hull max radius from the field centre (Tic Tac)
def F(r): return 0.5 * (np.tanh((r + R_F) / D_F) - np.tanh((r - R_F) / D_F))
def Fp(r): return 0.5 / D_F * (1 / np.cosh((r + R_F) / D_F) ** 2 - 1 / np.cosh((r - R_F) / D_F) ** 2)

# ---------------------------------------------------------------- A. source location for the symmetric field
# zero-expansion shift magnitude ~ V F(r); |K| ~ V |F'(r)|: energy density ~ K^2 -> radial profile of the required source
r = np.linspace(0, 25, 2501); K2 = Fp(r) ** 2
w_shell = K2 * r ** 2                                  # per unit radius (spherical shell weighting)
frac_inside_hull = float(np.trapezoid(w_shell[r <= HULL_R], r[r <= HULL_R]) / np.trapezoid(w_shell, r))
frac_wall = float(np.trapezoid(w_shell[(r >= R_F - 2 * D_F) & (r <= R_F + 2 * D_F)], r[(r >= R_F - 2 * D_F) & (r <= R_F + 2 * D_F)]) / np.trapezoid(w_shell, r))
A = dict(required_source_fraction_within_hull_radius=f'{frac_inside_hull:.1e}', required_source_fraction_in_wall_shell_11_19m=round(frac_wall, 4),
         reading='The stress-energy the field needs sits in the wall shell 9-13 m outside the hull, whoever generates it. A skin source is no closer to it than the 8 t module was: both need the relational sector to act at a distance (S_R unspecified).',
         wall_at_skin='Moving the wall onto the skin is a different field, not a better generator: the lane shows a shift wall cutting the hull strains it exponentially (158 g case).')

# ---------------------------------------------------------------- B. asymmetric, surface-steered shift
rng = np.random.default_rng(7)
def b_field(x, t, prm):                                # arbitrary asymmetric, time-dependent, spatially varying shift (field centre moves with X(t))
    X = prm['X0'] + prm['amp'] * (1 - np.cos(2 * np.pi * t / prm['T'])) / 2 * prm['dir']
    rr = np.linalg.norm(x - X); env = F(rr) * np.sin(np.pi * t / prm['T']) ** 2
    skew = 1 + prm['k'] * np.tanh((x - X) @ prm['axis'] / 3.0)      # surface-steered asymmetry across the field
    return prm['V'] * env * skew * prm['dir'] + prm['V2'] * env * np.cross(prm['axis'], prm['dir'])
def run_shift(prm, n=4000):
    x = np.zeros(3) + prm['x0']; w = np.zeros(3); T = prm['T']; dt = T / n
    for i in range(n):
        t = i * dt; b = b_field(x, t, prm); eps = 1e-4
        J = np.array([(b_field(x + eps * e, t, prm) - b_field(x - eps * e, t, prm)) / (2 * eps) for e in np.eye(3)])   # J[i, j] = d_i b_j
        w = w + dt * (-(J @ w)); x = x + dt * (b + w)
    return float(np.linalg.norm(w)), float(np.linalg.norm(x - prm['x0']))
B_rows = []
for k in range(6):
    d = rng.normal(size=3); d /= np.linalg.norm(d); ax = rng.normal(size=3); ax /= np.linalg.norm(ax)
    prm = dict(V=rng.uniform(5, 120), V2=rng.uniform(-30, 30), k=rng.uniform(-0.8, 0.8), T=rng.uniform(1, 6), amp=rng.uniform(0, 200), dir=d, axis=ax,
               X0=np.zeros(3), x0=rng.normal(size=3) * 2.0)
    wf, disp = run_shift(prm); B_rows.append(dict(final_ordinary_speed_ms=f'{wf:.1e}', displacement_m=round(disp, 1)))
B = dict(cases=B_rows, result='w stays 0 to rounding in every random asymmetric, time-dependent profile: the hull is displaced and left at its original velocity',
         reason='dw/dt = -(grad b) w is linear and homogeneous in w: no shift geometry, however finely the surface controls it, gives lasting velocity')

# ---------------------------------------------------------------- C. directional potential (lapse/cushion type)
# compact potential with a uniform interior gradient along u (the lane's lapse dash shape): Phi = -a (x.u) F(r) s(t)
def run_potential(a, u, T, n=4000, comoving=True):
    x = np.zeros(3); v = np.zeros(3); dt = T / n; imp = np.zeros(3)
    for i in range(n):
        t = i * dt; s = np.sin(np.pi * t / T) ** 2; eps = 1e-4
        X = x.copy() if comoving else np.zeros(3)                # field carried by the vehicle (module or skin) vs fixed in space
        Phi = lambda y: -a * ((y - X) @ u) * F(np.linalg.norm(y - X)) * s
        g = -np.array([(Phi(x + eps * e) - Phi(x - eps * e)) / (2 * eps) for e in np.eye(3)])
        v = v + dt * g; x = x + dt * v; imp += g * dt
    return v, x
u = np.array([1.0, 0.0, 0.0]); a = 0.4 * 9.81; Tp = 20.0
v_end, x_end = run_potential(a, u, Tp); v_fix, x_fix = run_potential(a, u, Tp, comoving=False)
# the field's own (ADM) momentum is zero for a compact field on flat slices (lane, source closure): the hull's gain must be exchanged (R1)
C = dict(interior_accel_g=0.4, ramp_s=Tp, fixed_field_final_speed_ms=round(float(np.linalg.norm(v_fix)), 2), fixed_field_note='a field fixed in space: the hull leaves through the reverse walls (integral of grad Phi = 0) and loses the gain; the field must travel with the vehicle', final_ordinary_speed_ms=round(float(np.linalg.norm(v_end)), 2), expected_ms=round(a * Tp / 2, 2), displacement_m=round(float(np.linalg.norm(x_end)), 1),
         result='YES: a directional potential gives lasting ordinary velocity after shutdown while the hull stays inside the field (the cushion mechanism, pointed sideways)',
         already_in_lane='WEAVE_GEOMETRY_COMPARE_2026_11_21: the lapse dash is exactly a horizontal potential push (uniform interior push with reverse walls, peak wall strength 2.6-11.5x the interior). The W2 cushion is the vertical case. Direction is not constrained by the model; "vertical only" was an operating booking, not physics.',
         conservation='Field momentum (ADM) is identically zero for a compact field on flat slices, so the hull\'s momentum must go to an external partner (R1). Same unresolved exchange law and partner as the vertical cushion and the dash; energy is booked by assumption (eta), not derived.',
         in_air='a potential push moves the hull through the air (drag, wake, boom), unlike the shift: horizontal acceleration to orbital speed belongs above the atmosphere')

verdict = dict(
    stopping_condition='The continuous active hull is a different means of generating the same fields. In the existing model it does not change controllable behaviour: the model prescribes field geometry directly, has no generator-to-field law (S_R unspecified), and the required source sits in the wall shell 9-13 m off the hull either way.',
    what_does_give_lasting_velocity='Not hull continuity but field TYPE: shift never (theorem of the adopted law); potential/lapse type always could, in any direction (already in the lane). Directional acceleration is therefore a capability-and-energy booking decision, independent of the hull hypothesis.',
    precise_missing=['constitutive law of the relational sector: which potential fields are attainable, at what energy cost, power and duration (S_R)',
                     'R1 exchange law and partner (unchanged)'],
    correction_to_torchless_screen='80ade29 said the cushion is "established only vertically". More precisely: the model already contains the horizontal potential push (lane lapse dash); only the energy/operating booking is vertical. The torchless verdict is unchanged: it still needs a TJ-class source and an explicit capability grant.',
    hypothesis_value='Strong as LOOM narrative and as a candidate form for the missing constitutive law (surface-sourced relational sector); not testable in this model.')
out = dict(header='ALL bodies. ALL sponsors. 2026-2226.', doc=__doc__, A_source_location=A, B_asymmetric_shift=B, C_directional_potential=C, verdict=verdict)
json.dump(out, open(os.path.join(H, 'continuous_hull_screen.json'), 'w'), indent=1)
print(json.dumps(A, indent=1)); print(json.dumps(B, indent=1)); print(json.dumps({k: C[k] for k in ('final_ordinary_speed_ms', 'expected_ms', 'displacement_m', 'fixed_field_final_speed_ms')}))
