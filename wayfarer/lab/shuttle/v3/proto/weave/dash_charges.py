"""Finite Weave dash: conserved-charge ledger (energy E, momentum P, boost/centre-of-energy charge K = E X - c^2 P t).
NON-CANON physics exercise (SOL handoff e17fd62). ALL bodies. ALL sponsors. 2026-2226.

Premise (from Weave foundations §16): M2 is a parent action S[W,Phi] = S_R[W] + S_matter[Phi,W], delta S/delta W = J_Phi.
If that action is local and diffeomorphism-invariant and the exterior is asymptotically flat, then within a fixed global sector
Lambda (Metric, foundations §15) the Poincare charges (E, P, J, K) of ship + source + Weave field + environment are conserved,
changing only by flux through the boundary at infinity. This is a theorem of such theories (Noether + Bianchi), not a lane rule.
A Loom transition (Lambda_A -> Lambda_B) is outside this premise by construction (M1)."""
import os, json, math
H = os.path.dirname(os.path.abspath(__file__))
c, G = 2.998e8, 6.674e-11
m, v, DX, RAMP = 61e3, 100.0, 200.0, 1.0           # SOL test dash scale; dash distance from dash_ambient (1 s up, 1 s cruise, 1 s down)
M_E, V_ORB = 5.972e24, 29.78e3
p = m * v
ledger = dict(
  ship=dict(dP_net=0.0, dK=f'{m * c ** 2 * DX:.2e} J m (= m c^2 dX)', note='ship starts and ends at rest; centre of energy moved by dX'),
  verdict_isolated='INCONSISTENT: an isolated start-dash-stop that leaves the ship displaced and the field relaxed with nothing else changed violates K conservation. '
                   'SOL\'s note is right that no NET impulse is needed; it is incomplete because K is also conserved.',
  closures={
   'R1 radiation to infinity': dict(min_energy_J=f'{2 * p * c:.2e}', basis='each impulse p radiated costs >= p c (start and stop): >= 2 m v c', verdict='DERIVED bound; prohibitive (~3.7 PJ for this dash)'),
   'R2 exterior Weave field reaching environment matter (local partner)': dict(partner_impulse_Ns=round(p), transient_energy_J=f'{0.5 * m * v ** 2:.2e} (supplied at start, returnable at stop)',
        earth_displacement_m=f'{m * DX / M_E:.1e}', verdict='DERIVED structure; requires S_R to have exterior range (a compact, exterior-flat domain has no local channel)'),
   'R3 nonlocal exchange to a distant partner (canon §7.1b type)': dict(sun_frame_transient_J=f'+/-{p * V_ORB:.2e} (+ {0.5 * m * v ** 2:.1e})', basis='work in partner frame = dp . v_rel, v_rel ~ 29.8 km/s',
        verdict='needs M1 nonlocality; partner law UNDETERMINED; Sun partner near a planet harvests relative motion (see cycle)'),
   'R4 persistent field remnant (energy-dipole scar)': dict(dipole_J_m=f'{m * c ** 2 * DX:.2e}', comparison=f'SOL wall scale ~1.9e32 J x R ~ 1.9e33 J m: a ~{m * c ** 2 * DX / 1.9e33:.0e} asymmetry', verdict='mathematically allowed in an exotic sector; requires a permanent +/- energy separation of order m c^2 dX: physically extreme, M2 constitutive law UNDETERMINED'),
   'R5 Loom transition (change Lambda)': dict(verdict='outside Metric by construction (M1). A displacement that discharges K without flux is a Loom-type event, i.e. option 2 / Weave seams (foundations §19)')})
# velocity change (Metric, partner channel R2/R3)
vel = dict(statement='With a partner channel the final ship velocity is u_f = u_i + dP/m: velocity CAN change. Crew stay inertial (interior geodesic, SOL).',
           energy_in_partner_frame=[dict(case='start 0 -> 100 m/s', J=f'{0.5 * m * 100 ** 2:.2e}'), dict(case='stop 300 m/s -> 0 (absorb)', J=f'{0.5 * m * 300 ** 2:.2e}'),
                                    dict(case='start 0 -> 1 km/s', J=f'{0.5 * m * 1e3 ** 2:.2e}'), dict(case='Wayfarer 1168 t to 0.268c (canon NORMAL), local partner', J=f'{0.5 * 1168e3 * (0.268 * c) ** 2:.2e}')],
           canon_tension='Canon reaches 0.268c from a ~2 GJ bank. Under R2/R3 with immediate discharge that costs ~1/2 m v^2 ~ 4e21 J. Canon metric is therefore consistent with the charge theorem only via R4 or R5 (exotic remnant or M1 discharge), or by a partner law that is not yet written.',
           torch_monopoly='NOT derived: W3 ("torch owns velocity") was a lane rule. Under R2/R3 the Weave can change velocity at energy cost in the partner frame.')
# ENERGY-B frame (closed cycle)
gh = 9.81 * 1000
cyc = dict(test='metric up-hop 1 km with no source input, ordinary fall, trim (61 t)',
           conservation_says='with no source input the hop must conserve the ship\'s mechanical energy IN THE PARTNER FRAME: v_a^2 = v_s^2 + 2 dPhi there',
           partner_earth=dict(hover_up_hop='forbidden without source input; with input pays m g h = %.2f GJ; cycle net 0' % (m * gh / 1e9)),
           partner_sun=dict(cost='%.2f m/s of Sun-frame speed' % (gh / V_ORB), cycle_net_GJ=round(m * gh / 1e9, 2), meaning='energy-conserving harvest of Earth-Sun relative motion (not perpetual motion), unbounded in practice'),
           verdict='DERIVED: canon ENERGY-B counted in the Sun frame is equivalent to a Sun partner; near a planet it harvests orbital relative motion. A partner at rest in the local potential frame gives no closed-cycle gain.')
out = dict(header='ALL bodies. ALL sponsors. 2026-2226.', lane='NON-CANON physics', doc=__doc__, case=dict(m_kg=m, v_ms=v, dash_m=DX), ledger=ledger, velocity=vel, closed_cycle=cyc)
json.dump(out, open(os.path.join(H, 'dash_charges.json'), 'w'), indent=1)
if __name__ == '__main__':
    print(json.dumps(out['ledger']['closures'], indent=1)); print(json.dumps(vel, indent=1)); print(json.dumps(cyc, indent=1))
