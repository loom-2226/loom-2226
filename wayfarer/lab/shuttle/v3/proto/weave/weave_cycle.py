"""Weave manoeuvring - decisive closed-cycle energy test (Sol review 595baf4, smallest test for option 3).
NON-CANON prototype lane. kT 2026-11-21: may challenge CANON II §7.1a/§7.1b; §18A doctrine waived for this lane.
ALL bodies. ALL sponsors. 2026-2226.

Rule S (canon as written): ENERGY-B arrival speed counted in the Sun-barycentric frame, Sun is the momentum partner.
Rule L (lane proposal): inside a body's sphere of influence the Weave's partner is that body; ENERGY-B is counted in its frame.
ENERGY-B (CANON II §7.1a): v_a^2 = |v_s|^2 + 2(Phi_s - Phi_a), direction carried by the local frames.
Cycle: hover at sea level -> metric up-hop 1 km -> ordinary fall 1 km with ideal harvest -> trim residual velocity -> start state.
A closed cycle must return zero net extractable work (CANON II §7.3) or it is a pump."""
import json, math, os
H = os.path.dirname(os.path.abspath(__file__))
G, M, DH = 9.81, 61e3, 1000.0
V_E = 29.78e3                                    # Earth heliocentric speed (hovering shuttle's Sun-frame speed, rotation ignored)
SOI_E = 9.25e8                                   # Earth sphere of influence radius (m)
def cycle(rule):
    out = dict(rule=rule)
    if rule == 'S':
        v_a = math.sqrt(V_E ** 2 - 2 * G * DH)                       # Sun-frame speed after the up-hop
        dv_rel = V_E - v_a                                           # residual velocity relative to Earth after the hop
        paid_hop = 0.0
        partner_impulse = M * dv_rel                                 # to the Sun
        partner_energy_earth_frame = partner_impulse * V_E           # Earth-frame energy delivered through the Sun exchange
    else:
        v_s = 0.0; arg = v_s ** 2 - 2 * G * DH                        # Earth-frame ENERGY-B: forbidden unless paid
        paid_hop = M * G * DH if arg < 0 else 0.0                    # bank/reactor pays the height
        dv_rel = 0.0; partner_impulse = 0.0; partner_energy_earth_frame = 0.0
    harvest = M * G * DH                                             # ideal regenerative brake on the 1 km fall
    trim = 0.5 * M * dv_rel ** 2                                     # Earth-frame energy to null the residual drift (can be harvested instead)
    net = harvest - paid_hop - trim
    out.update(residual_drift_ms=round(dv_rel, 4), paid_for_hop_MJ=round(paid_hop / 1e6, 1), harvested_MJ=round(harvest / 1e6, 1), trim_MJ=round(trim / 1e6, 4),
               net_extractable_MJ_per_cycle=round(net / 1e6, 1), partner_impulse_Ns=round(partner_impulse), source_of_net_energy='Sun-partner exchange, dp x v_rel(Sun-Earth)' if rule == 'S' else 'none (closed)',
               verdict='PUMP: violates CANON II §7.3 (hard kill if restored)' if net > 1e3 else 'CLOSED: zero net work (losses only)')
    return out
res = {'S (canon §7.1a/b as written)': cycle('S'), 'L (local partner inside sphere of influence)': cycle('L')}
# Rule L: free segments conserve E = v^2/2 + Phi in the partner frame (time-independent Phi), so any closed loop of dashes/turns nets zero.
# Sphere-of-influence hand-off: a free turn of v_inf near a planet changes heliocentric energy like a gravity assist (planet pays).
v_inf = 3e3
assist = dict(v_inf_ms=v_inf, free_180deg_turn_heliocentric_dv_ms=2 * v_inf, heliocentric_energy_change_GJ=round(M * V_E * 2 * v_inf / 1e9),
              note='IF the Weave could also rotate real velocity for free, a 180 deg turn of v_inf would be a gravity assist anywhere in the sphere of influence (planet pays): setting-scale. EXCLUDED by lane rule W-3, which keeps canon §7.1a: arrival direction is carried by the local frames and ordinary vector steering is paid by torch. The Weave changes POSITION; the torch owns VELOCITY.')
out = dict(header='ALL bodies. ALL sponsors. 2026-2226.', lane='PROTOTYPE (non-canon) Weave manoeuvring - closed-cycle test', doc=__doc__, cycle_1km=res, rule_L_theorem='with Phi time-independent in the partner frame, ENERGY-B segments + ordinary gravity conserve E_mech; net work of any closed cycle = paid - harvested = losses >= 0',
           soi_handoff=assist, sphere_of_influence_earth_m=SOI_E,
           rules=dict(W1='partner = dominant body inside its sphere of influence (departs §7.1b; lane-authorized)', W2='ENERGY-B counted in the partner frame; height gain paid from bank/reactor (powered channel, departs §7.1a; lane-authorized)', W3='arrival kinetic state = departure state carried by local frames (canon §7.1a kept): no free velocity steering', W4='doctrine §18A and near-body certification §6 waived for this lane (kT)'),
           verdict='Rule S pumps ~0.6 GJ per 1 km cycle for 61 t (source: Sun exchange at 29.8 km/s). Rule L closes. Weave near bodies is admissible only with Rule L, which is a scoped departure from §7.1b (authorized for this lane, not canon).')
json.dump(out, open(os.path.join(H, 'weave_cycle.json'), 'w'), indent=1)
if __name__ == '__main__':
    for k, v in res.items(): print(k, v)
    print(assist)
