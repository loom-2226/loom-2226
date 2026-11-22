"""Torchless Tic Tac from the relational foundations up (Sol, after 743d4b2; forwarded by kT). NON-CANON screen.
ALL bodies. ALL sponsors. 2026-2226.

Sol's question: can the continuous active hull sustain a directional-W2 ascent through an exchange with relational topography,
while the visible world keeps consistent local conservation and the whole process avoids free-work cycles? Record physical
energy and momentum changes, environmental response, and whether the relational configuration changes. Assign no joule
reservoir to the relational domain. If the theory cannot answer, stop.

Part 1 (formal, no numbers): visible local conservation vs an energy inflow from outside spacetime.
Part 2 (numbers): what the existing R1 route already allows when the partner is a moving body, e.g. the Sun as in canon
sec. 7.1b. The previous screen's reactor came from booking the field's work in Earth's frame (an Earth-fixed partner)."""
import os, json, math
H = os.path.dirname(os.path.abspath(__file__))
A = json.load(open(os.path.join(H, 'directional_w2_ascent.json')))
GM_E, RE, W_E = 3.986e14, 6.371e6, 7.292e-5
V_E = 29.78e3                                   # Earth's heliocentric speed
h = 200e3; r = RE + h; v_orb = math.sqrt(GM_E / r); v0 = W_E * RE; m = A['mass_t'] * 1e3
dPhi = GM_E * (1 / RE - 1 / r)

part1 = dict(
    statement='Local conservation in the visible world means div T_visible = 0 everywhere. Then any energy or momentum reaching the hull arrives as a flux through spacetime from a physical sector or body (routes R1 partner, R2 radiation, R3 screened package of the source closure). If instead the relational domain feeds the hull directly, the visible equations acquire a source term, div T_visible = J_relational != 0, wherever the field acts.',
    result='The two requirements in the question are mutually exclusive as posed: visible local conservation AND energy entering from outside spacetime cannot both hold. Option (i) keeps div T = 0 and is ordinary joule accounting with a partner. Option (ii) is a visible-sector source term, which is exactly what canon sec. 7.3 (div T = 0) forbids for physical sectors.',
    noether='Treating the relational configuration as an external, non-dynamical background in the visible action gives div T_visible = -(dL/d background) d(background): energy is pumped by the background\'s time dependence, like a driven oscillator. That is the precise form of "energy emergent": it is option (ii), and it needs a sec. 7.3 amendment and Research Lab work (relational-topography programme), not a shuttle screen.',
    stop='The existing theory cannot answer whether option (ii) avoids free-work cycles: that requires the relational action S_R, which is unspecified. Stop on Part 1.')

# ---------------------------------------------------------------- Part 2: R1 with a moving partner (canon precedent)
# A partner of effectively infinite mass absorbs momentum but no energy in its own rest frame. So the field does no net work
# in the partner frame: W_partner = d(1/2 m v_p^2) + m dPhi = 0 (v_p = velocity relative to the partner).
# Earth-fixed partner (previous screens): W = KE gain + PE = 1.56 TJ in Earth's frame -> needs an onboard source.
# Earth-spin partner (rotating Earth): energy available = Omega * dL.
dL = A['fast_0p4g']['angmom_to_partner']; E_spin = W_E * m * (r * v_orb - RE * v0)
# Sun partner: heliocentric energy unchanged. Condition per kg: 1/2(v_f^2 - v_0^2) + V_E.(v_f - v_0) + dPhi = 0
need_proj = -(0.5 * (v_orb ** 2 - v0 ** 2) + dPhi)          # required V_E . dv (per kg)
dv = v_orb - v0; cos_ang = need_proj / (V_E * dv); ang = math.degrees(math.acos(cos_ang))
E_earth_orbit = V_E * abs(need_proj / V_E) * m             # energy drawn from Earth's orbital motion if the momentum ends in Earth (e.g. later aerobraking)
part2 = dict(
    earth_fixed_partner=dict(onboard_energy_TJ=round(A['fast_0p4g']['field_work_TJ'], 2), note='previous screens: the reactor and its waste heat'),
    earth_spin_partner=dict(energy_available_TJ=round(E_spin / 1e12, 3), fraction_of_need=round(E_spin / (A['fast_0p4g']['field_work_TJ'] * 1e12), 2), note='insufficient alone'),
    sun_partner=dict(required_angle_between_dv_and_earth_orbital_velocity_deg=round(ang, 1), required_projection_ms=round(need_proj / V_E, 0),
                     onboard_energy_TJ=0.0, local_dissipation='no source losses: no reactor; only whatever the field itself dissipates (unknown, not booked)',
                     geometry='reach orbital speed where the new velocity points ~98 deg from Earth\'s orbital motion: near the dawn/dusk terminator for an equatorial orbit (sense set by the side)',
                     energy_comes_from='heliocentric bookkeeping: the hull\'s heliocentric speed is unchanged (a redirect, as in a gravity assist). If the vehicle later dumps that momentum into Earth (aerobraking), the 1.5 TJ is ultimately drawn from Earth\'s orbital energy: a finite physical reservoir, not a free-work cycle',
                     earth_orbital_energy_drawn_per_cycle_TJ=round(E_earth_orbit / 1e12, 2), canon='same law as canon sec. 7.1b (Metric: Sun partner, ENERGY-B heading-dependent arrival); for the prototype it is option B, which kT did not choose at step 4 (A: partner UNKNOWN)'),
    rule='With a moving partner the field\'s energy is set by the frame of the partner, not of the Earth. The reactor requirement was an artefact of an Earth-fixed partner.')
verdict = dict(
    relational_source='Not answerable and, as posed, contradictory with visible local conservation (Part 1). Stop: Research Lab question (S_R, sec. 7.3).',
    better_route='Inside existing physics and canon precedent: R1 with the Sun as partner makes the ascent reactor-free and heat-free, subject to a heading/timing rule (insert near the terminator). Costs: choosing option B for the prototype (a CCR revision), and a timing constraint on every velocity change.',
    for_kT=['keep the torch (design unchanged)', 'adopt the Sun-partner law for the prototype (CCR option B): reactorless, heatless, timing-constrained',
            'send the "energy emergent" hypothesis to the Research Lab as a sec. 7.3 / S_R question'])
out = dict(header='ALL bodies. ALL sponsors. 2026-2226.', doc=__doc__, part1_formal=part1, part2_moving_partner=part2, verdict=verdict)
json.dump(out, open(os.path.join(H, 'relational_energy_screen.json'), 'w'), indent=1)
print(json.dumps(part2, indent=1))
