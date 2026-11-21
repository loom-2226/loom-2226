"""Torchless Tic Tac screen (Sol brief, 2026-11-22). NON-CANON. ALL bodies. ALL sponsors. 2026-2226.

Question: can the existing W2 + Weave configuration take the Tic Tac from Earth's surface to a velocity-matched rendezvous
with Wayfarer in low orbit without conventional thrust? Only existing field behaviour, conservation and established exchange
assumptions. No new exchange mechanism. If it cannot close, name the precise missing capability and stop.

Established behaviour used (lane reports):
  Weave shift (zero-expansion shift, N = 1): slow geodesic L = 1/2|xdot - b|^2  =>  dw_i/dt = -w_j d_i b_j with w = xdot - b
      (WEAVE_GEOMETRY_COMPARE, sign-corrected). The law is linear and homogeneous in w: w = 0 stays 0 for ANY b(x, t).
      A hull that starts at rest relative to the exterior is carried (xdot = b) and is left at rest when b -> 0. Galilean
      invariance makes this frame-independent: the shift never changes the hull's velocity relative to the exterior.
  W2 cushion: a lapse-type potential that cancels gravity inside the field and, as booked in the lane, adds net climb at
      (1.4 - 1) g to 2 km in ~20 s, energy paid from the flywheel at eta 0.6 (proto/metric_wildcards.cushion; closure_screen).
      It DOES change ordinary velocity (vertical) and so already exchanges net momentum with a partner.
  Exchange: R1 (external partner) is the only consistent route; the exchange law and partner are UNKNOWN (source closure;
      CCR-2026-0005 sec. 7.1b option A). Conservation in full; sec. 7.3 binds.
"""
import os, json, math
H = os.path.dirname(os.path.abspath(__file__))
T = json.load(open(os.path.join(H, 'tictac_v1.json')))
GM, RE, G0, W_E = 3.986e14, 6.371e6, 9.81, 7.292e-5
h = 200e3; r = RE + h
m = T['mass']['dry_t'] * 1e3 + 1.1e3                    # torchless ascent mass without remass (upper bound on savings: torch kept as-is here)
v_orb = math.sqrt(GM / r); v_rot = W_E * RE               # due east from the equator (best case)
dv = v_orb - v_rot
KE = 0.5 * m * (v_orb ** 2 - v_rot ** 2); PE = GM * m * (1 / RE - 1 / r); E = KE + PE
eta = 0.6                                                  # lane cushion efficiency (assumption carried over)
dp = m * dv; dL = m * (r * v_orb - RE * v_rot)
a_net = 0.4 * G0                                           # the lane's booked cushion net acceleration
t_burn = dv / a_net; P_peak = m * a_net * v_orb / eta
L_earth = 8.04e37 * W_E                                    # I_earth * omega
out = dict(header='ALL bodies. ALL sponsors. 2026-2226.', doc=__doc__,
           shift=dict(result='CANNOT', reason='dw/dt = -w.grad(b) is homogeneous in w: a hull starting at rest relative to the exterior is left at rest when the field ends, in any frame',
                      status='DERIVED from the lane\'s established slow-geodesic law (not a property of the chosen dash profile)'),
           cushion=dict(result='CAN in principle (same field type, same bookkeeping), but only vertical is established',
                        established='vertical, (1.4-1) g net, ~2 km in ~20 s, ~3 GJ from the flywheel, partner unknown'),
           requirement=dict(mass_t=round(m / 1e3, 1), v_orbit_ms=round(v_orb), v_rot_ms=round(v_rot), dv_ms=round(dv),
                            energy_TJ=round(E / 1e12, 2), source_energy_TJ_at_eta=round(E / eta / 1e12, 2), momentum_Ns=f'{dp:.2e}', angular_momentum=f'{dL:.2e}',
                            earth_spin_fraction=f'{dL / L_earth:.1e}', burn_at_0p4g_s=round(t_burn), burn_at_0p4g_min=round(t_burn / 60, 1),
                            ground_track_km=round(0.5 * a_net * t_burn ** 2 / 1e3), peak_source_power_GW=round(P_peak / 1e9, 2),
                            flywheel_GJ=T['mass']['cushion_GJ'], flywheel_fraction=f"{T['mass']['cushion_GJ'] * 1e9 / (E / eta):.1e}"),
           missing=['DIRECTIONAL CUSHION: the cushion acceleration must be commandable along the horizontal (not tied to local gravity), '
                    'at ~0.4 g for ~31 min, delivering ~3.4e8 N s and ~2.2e15 kg m2/s to a partner. Established only vertically, to 2 km.',
                    'ENERGY SOURCE: ~1.5 TJ delivered, ~2.5 TJ at the lane efficiency, peaking ~2.4 GW. The flywheel holds ~3 GJ (~0.1%). '
                    'Only the torch reactor (7.7 GW) is in that class: a torchless Tic Tac keeps the reactor and drops the nozzle and the water.',
                    'EXCHANGE LAW: unchanged gap (R1 law and partner). Using the cushion as main propulsion with an UNKNOWN partner is a new '
                    'capability claim beside sec. 7.3 / sec. 21 ("independently commandable" momentum source), so it needs explicit CCR text.'],
           consequences=['On airless bodies (Moon, Europa) a field failure would leave no fallback at all: no parachutes, no torch.',
                         'Wayfarer-supplied velocity (option 2) is not credible: Wayfarer cannot match a vehicle at zero orbital speed.'],
           verdict='Does not close with established behaviour. Precise missing capability: a directional (non-vertical) cushion mode used as main propulsion, '
                   'powered by a GW-class reactor, with the exchange partner still undeclared. Stop here: kT decides whether to grant it.')
json.dump(out, open(os.path.join(H, 'torchless_screen.json'), 'w'), indent=1)
print(json.dumps(out['requirement'], indent=1)); print(out['verdict'])
