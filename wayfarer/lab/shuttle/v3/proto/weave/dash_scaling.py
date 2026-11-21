"""Does domain size / field geometry / ramp rate give the shuttle a genuinely different Metric envelope? (kT revised direction 2026-11-21)
NON-CANON physics. ALL bodies. ALL sponsors. 2026-2226.

Common physics for every craft: unit lapse, flat slices, shift beta = v(t) F(x - X(t)) (foundations §5, §7). With K_ij = 1/2(d_i beta_j + d_j beta_i):
  Eulerian energy density (Hamiltonian constraint)   rho_E = (c^2/16 pi G)(K^2 - K_ij K^ij)                       [DERIVED, exact]
  ramp-rate stress (evolution eq., part linear in a=dv/dt)   S^(a)_ij = (c^2/8 pi G) a * 1/2(d_i F_j + d_j F_i)      [DERIVED, exact term]
Integrated 'geometric demand' (what any source, M2 or otherwise, must supply as effective stress-energy):
  E_v = Int |rho_E| dV      and      S_a = Int ||S^(a)|| dV
Both are independent of the payload mass (interior is flat; G m/(R c^2) ~ 1e-22): DERIVED.
The mapping from geometric demand to actuator energy/hardware is NOT known (M2 has no constitutive law): ASSUMED/UNDETERMINED."""
import os, json, math
import numpy as np
H = os.path.dirname(os.path.abspath(__file__))
c, G = 2.998e8, 6.674e-11
def fields(kind, R, D, n=700):
    L = R + 8 * D; x = np.linspace(-L, L, n); rho = np.linspace(1e-3, L, n // 2); Xg, Pg = np.meshgrid(x, rho, indexing='ij')
    r = np.sqrt(Xg ** 2 + Pg ** 2); f = 0.5 * (1 - np.tanh((r - R) / D)); fp = -0.5 / D / np.cosh((r - R) / D) ** 2
    if kind == 'alcubierre': bx, br = f, 0 * f
    else: bx, br = f + 0.5 * fp * Pg ** 2 / r, -0.5 * fp * Xg * Pg / r          # Natario: curl(f e_x x r / 2), axisymmetric components
    dx, dp = x[1] - x[0], rho[1] - rho[0]
    Kxx = np.gradient(bx, dx, axis=0); Krr = np.gradient(br, dp, axis=1); Kff = br / Pg; Kxr = 0.5 * (np.gradient(bx, dp, axis=1) + np.gradient(br, dx, axis=0))
    tr = Kxx + Krr + Kff; KK = Kxx ** 2 + Krr ** 2 + Kff ** 2 + 2 * Kxr ** 2
    dV = 2 * np.pi * Pg * dx * dp
    return float(np.sum(np.abs(tr ** 2 - KK) * dV)), float(np.sum(np.sqrt(KK) * dV)), float(np.max(np.abs(tr)))
def demand(kind, R, D, v, a):
    I_e, I_s, divmax = fields(kind, R, D)
    return dict(E_v_J=c ** 2 * v ** 2 / (16 * math.pi * G) * I_e, S_a_J=c ** 2 * a / (8 * math.pi * G) * I_s, max_div_beta_per_unit_v=divmax)
# --- scaling fits
out = {'doc': __doc__}
for kind in ('alcubierre', 'natario'):
    Rs = np.array([3, 5, 8, 12, 18, 25.0]); Ds = np.array([0.5, 1, 2, 4, 8.0])
    eR = [demand(kind, R, 2.0, 1, 1) for R in Rs]; eD = [demand(kind, 10.0, D, 1, 1) for D in Ds]
    sR = np.polyfit(np.log(Rs), np.log([e['E_v_J'] for e in eR]), 1)[0]; sRa = np.polyfit(np.log(Rs), np.log([e['S_a_J'] for e in eR]), 1)[0]
    sD = np.polyfit(np.log(Ds[:3]), np.log([e['E_v_J'] for e in eD][:3]), 1)[0]; sDa = np.polyfit(np.log(Ds[:3]), np.log([e['S_a_J'] for e in eD][:3]), 1)[0]
    chk = demand(kind, 10.0, 2.0, 100.0, 0)
    out[kind] = dict(E_v_exponent_R=round(sR, 2), E_v_exponent_wall=round(sD, 2), S_a_exponent_R=round(sRa, 2), S_a_exponent_wall=round(sDa, 2),
                     SOL_case_E_v_J=f"{chk['E_v_J']:.2e}", max_div_beta=round(eR[3]['max_div_beta_per_unit_v'], 4))
# --- craft comparison (area-equivalent spheres; same wall; same v and a). Real hulls are not spheres: shape factor UNDETERMINED.
CRAFT = {'shuttle (284 m^2 envelope)': (284.0, 61e3), 'Wayfarer (1,900 m^2 domain, CANON II §12)': (1900.0, 1168e3)}
cmp_ = {}
for name, (A, m) in CRAFT.items():
    R = math.sqrt(A / (4 * math.pi)); d = demand('natario', R, 2.0, 100.0, 98.1)
    cmp_[name] = dict(area_m2=A, R_equiv_m=round(R, 2), mass_t=m / 1e3, E_v_at_100ms_J=f"{d['E_v_J']:.2e}", S_a_at_10g_J=f"{d['S_a_J']:.2e}",
                      mass_per_area_kg_m2=round(m / A), boost_charge_per_100m_Jm=f'{m * c ** 2 * 100:.2e}')
ratio_area = 1900 / 284; ratio_mpa = (1168e3 / 1900) / (61e3 / 284)
out['craft'] = cmp_
out['hardware_hypotheses'] = {
 'HW1 field capacity scales with domain area (L^2 candidate plant, same node density)': dict(agility_ratio_shuttle_vs_wayfarer=1.0,
      note='same achievable v^2 and a per unit capacity: size alone gives NO agility advantage; exchange demand per unit capacity is %.1fx lower for the shuttle (mass per area)' % ratio_mpa),
 'HW2 fixed absolute capacity (same hardware on both)': dict(agility_ratio_shuttle_vs_wayfarer=round(ratio_area, 1), note='a and v^2 scale as 1/area: shuttle %.1fx' % ratio_area),
 'HW3 prototype with k x the capacity per area (denser Mc / nodes / faster control)': dict(agility_ratio_shuttle_vs_wayfarer='k', note='speculative engineering; k is not derived')}
out['bandwidth'] = dict(light_crossing_s=f'{2 * math.sqrt(284 / (4 * math.pi)) / c:.1e}', adiabatic_ratio_at_0p1s=f'{0.1 / (2.0 / c):.1e}',
                        canon_screen_ratio='~5e8 (CANON II §8, 10 s ramp, 6 m wall)', note='causality and adiabaticity are not limiting at 0.01-0.1 s ramps: DERIVED. Real bandwidth = Mc/node/cryo response: UNDETERMINED (WCS §17).',
                        ramp_vs_velocity_stress='ramp term dominates when ramp time < wall / v (2 m / 100 m/s = 20 ms): DERIVED from the two terms')
json.dump(out, open(os.path.join(H, 'dash_scaling.json'), 'w'), indent=1)
if __name__ == '__main__':
    for k in ('alcubierre', 'natario'): print(k, out[k])
    for k, v in cmp_.items(): print(k, v)
    print(out['bandwidth'])
