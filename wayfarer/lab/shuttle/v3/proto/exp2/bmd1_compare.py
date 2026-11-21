"""BMD-1 bounded comparison: H1 local-partner coupling vs H2 gravitational-coupling domain, at Earth, Titan and deep space.
NON-CANON prototype lane (kT 2026-11-21: may challenge CANON II §7.1a and §7.1b). ALL bodies. ALL sponsors. 2026-2226.
Newtonian bounding arithmetic only. No hardware, no simulation expansion, no canon change.
Two ledgers are kept apart: energy exchanged with the partner (closes by construction) vs energy the ONBOARD device must supply/store/absorb."""
import json, math, os
H = os.path.dirname(os.path.abspath(__file__))
GM = dict(sun=1.327e20, earth=3.986e14, moon=4.905e12, saturn=3.793e16, titan=8.978e12)
AU = 1.496e11; m = 61e3; T_LIFT = 9.0
PHI_GAL = 1.5e11      # J/kg, |galactic potential| at the Sun, from escape speed ~550 km/s [ASSUMPTION, order of magnitude]
ENV = {
 'Earth surface': dict(g_local=9.81, bodies=[('earth', 6.371e6, 0.0), ('sun', AU, 29.8e3), ('moon', 3.844e8, 1.02e3)]),
 'Titan surface': dict(g_local=1.352, bodies=[('titan', 2.575e6, 0.0), ('saturn', 1.222e9, 5.57e3), ('sun', 9.58 * AU, 9.6e3)]),
 'Deep space, 1 AU heliocentric (no planet)': dict(g_local=0.0, bodies=[('sun', AU, 29.8e3)]),
}
def weights(bodies, law):
    raw = [(GM[b] / r ** 2 if law == 'g' else 2 * GM[b] / r ** 3) for b, r, _ in bodies]; s = sum(raw)
    return [x / s for x in raw]
out = {}
for env, e in ENV.items():
    F = 1.5 * m * e['g_local'] if e['g_local'] else 0.15 * m * 9.81            # lift at 1.5 x local weight; deep space: a 0.15 g manoeuvre
    v_ship = 0.5 * (F / m - e['g_local']) * T_LIFT if e['g_local'] else 0.5 * F / m * T_LIFT   # mean speed of the 9 s manoeuvre, local frame
    h1 = {}
    for law in ('g', 'tidal'):
        w = weights(e['bodies'], law); vbar = sum(wi * v for wi, (_, _, v) in zip(w, e['bodies']))   # weighted partner velocity vs the dominant body
        h1[f'partner weighting by {law}'] = dict(weights={b: f'{wi:.2e}' for wi, (b, _, _) in zip(w, e['bodies'])}, partner_velocity_offset_ms=round(vbar, 4),
            device_power_MW_range=f'{F * max(v_ship - vbar, 0) / 1e6:.1f} to {F * (v_ship + vbar) / 1e6:.1f}',
            device_energy_GJ_range=f'{F * (v_ship - vbar) * T_LIFT / 1e9:+.3f} to {F * (v_ship + vbar) * T_LIFT / 1e9:+.3f}')
    if not e['g_local']:
        for law in h1: h1[law]['note'] = 'only the Sun: device power = F x heliocentric velocity, ~%.1f GW per MN at 29.8 km/s (cf. torch F x ve/2: 5-25 GW per MN)' % (29.8e3 * 1e6 / 1e9)
    # H2: switchable gravitational coupling k (passive = active to keep Newton III). Weight reduction: k 1 -> 0. Upward force: k 1 -> -0.5.
    phi = {b: GM[b] / r for b, r, _ in e['bodies']}; phi_sum = sum(phi.values())
    h2 = {}
    for label, dk in (('weight reduction (k 1 -> 0): floats, NO upward force', 1.0), ('actual upward force (k 1 -> -0.5): net 0.5 g up', 1.5)):
        h2[label] = dict(switch_energy_local_bodies_GJ=round(m * dk * phi_sum / 1e9, 1), switch_energy_incl_galaxy_PJ=round(m * dk * (phi_sum + PHI_GAL) / 1e15, 2),
                         lift_work_GJ=round(F * 0.5 * (F / m - e['g_local']) * T_LIFT ** 2 / 1e9, 3) if (e['g_local'] and dk > 1) else 0.0)
    # EP-violation drift: the shuttle stops sharing the free fall of its host in the external (uniform) fields
    ext = [(b, GM[b] / r ** 2) for b, r, _ in e['bodies'][1:]] if e['g_local'] else []
    drift = {b: dict(rel_accel_mm_s2=round(1.5 * a * 1e3, 3), drift_m_in_30s=round(0.5 * 1.5 * a * 900, 2), drift_km_in_1h=round(0.5 * 1.5 * a * 3600 ** 2 / 1e3, 1)) for b, a in ext}
    out[env] = dict(force_kN=round(F / 1e3), H1_local_partner=h1, H2_gravitational_coupling=dict(cases=h2, ep_drift_vs_host=drift,
        upward_force='only for k < 0 (repulsion). k between 0 and 1 reduces weight only: the shuttle can at best float; fans or torch must still lift it.' if e['g_local'] else 'no local field: no force at all'))
verdict = dict(
 better='H1 local-partner coupling, with partner weights set by the tidal field and force capacity bounded by the local environment',
 why=['Its onboard energy is the work in the partner frame, F . (v - v_partner): tens of MW for a 200 m lift at Earth and ~a few MW at Titan, with no dependence on absolute potentials.',
      'Weighting by tidal field (not raw g) respects the equivalence principle: a uniform external field (Sun at Earth, Saturn at Titan) is invisible to a freely falling domain, and the partner offset is mm/s at Earth and ~0.2 m/s at Titan. Raw-g weighting gives an 18 m/s offset at Earth and ~100 m/s at Titan: detectable and arbitrary.',
      'The partner then varies continuously with the gravitational environment; no named-planet rule is needed.'],
 H2_decisive_contradiction='Changing gravitational coupling changes the shuttle\'s interaction energy with EVERY mass that sources the potential: m dk |Phi|. At Earth that is ~4 TJ from Earth alone, ~58-87 TJ with the Sun, and ~9-14 PJ including the Galaxy (a Machian estimate would approach m c^2). '
    'Either the onboard device supplies/stores it (impossible) or the field holds it outside the device, in which case H2 has become a partner-coupling theory (H1) with extra assumptions. It also makes the domain stop sharing its host\'s free fall (observable drift: ~9 mm/s^2 sunward at Earth, ~38 mm/s^2 Saturnward at Titan for dk 1.5) - a direct equivalence-principle violation. '
    'And k between 0 and 1 gives no upward force at all.',
 H1_minimum_constitutive_property='A powered momentum-exchange law between a uniformly coupled domain and the surrounding mass distribution, with partner weights given by each body\'s contribution to the local tidal field, and force capacity that scales with that field (vanishing in deep space).',
 H1_conservation_consequences=['Local stress-energy and momentum close with the weighted partners; recoil negligible.',
      'Onboard device supplies F . v_rel when pushing along the relative velocity and must ABSORB it when pushing against it (descents, braking): storage or heat rejection, not free energy.',
      'Lift-lower cycles net to zero apart from losses; no orbital-energy mining because the Sun/Saturn weights are ~1e-8 to 1e-5.'],
 H1_decisive_unknowns=['How force capacity scales with the tidal field. If it is NOT bounded by the environment, H1 becomes deep-space propellantless propulsion at F x 30 km/s (GW per MN, comparable to the torch) - a setting-wide change far beyond a shuttle aid.',
      'Whether a tidal-weighted coupling can deliver a force that is not itself tidal (a uniform push on a 15 m domain from a field whose gradient is 3e-6 s^-2 at Earth): this is the place a hidden contradiction is most likely.',
      'Generator power and mass (not established by any closed ledger).'],
)
json.dump(dict(header='ALL bodies. ALL sponsors. 2026-2226.', lane='PROTOTYPE (non-canon) BMD-1 comparison', environments=out, verdict=verdict), open(os.path.join(H, 'bmd1_compare.json'), 'w'), indent=1)
if __name__ == '__main__':
    print(json.dumps(out, indent=1))
