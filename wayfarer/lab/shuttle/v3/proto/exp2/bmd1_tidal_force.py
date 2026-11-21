"""BMD-1 single question (review 2026-11-21): can a tidal-field-dependent coupling give a nonzero centre-of-mass force on a finite,
internally uniform domain without violating local stress-energy conservation? Newtonian weak-field limit, full tidal tensor.
NON-CANON. ALL bodies. ALL sponsors. 2026-2226.

Derivation (y = position relative to the domain's centre of mass, T_ij = d_i g_j the tidal tensor, g_j the external field):
 (1) Ordinary coupling, or ANY force density linear in T acting on positive density through position: f_i = rho (g_i(c) + T_ij y_j + O(y^2)).
     The T term integrates to T_ij * Int(rho y_j) = 0 EXACTLY, for any shape, because the first moment about the centre of mass vanishes.
     The residual is the quadrupole term ~ M g (L/R)^2.
 (2) A force linear in T needs an internal vector instead of y: f_i = T_ij P_j (P = dipole-moment density). Net force F = T . p, where p = Int P dV.
     For gravity this is a MASS DIPOLE (+q and -q a distance L apart): it is the only way to get a non-tidal net force from a tidal field.
 (3) Energy of a mass dipole in the external field (reference-INDEPENDENT, because total charge is zero): U = q Phi(top) - q Phi(bottom) = p . grad Phi.
     For lift at a body's surface (radial dipole) F = 2 g p / R and U = p g, so U = F R / 2 independent of shape and of the potential's zero.
 (4) Newton III holds only if the dipole is also an ACTIVE source (its field pulls on the planet). That needs negative active mass at one pole:
     exotic stress-energy (energy-condition violation), i.e. inside the class M2 already declares, but at a stated amount."""
import json, math, os
H = os.path.dirname(os.path.abspath(__file__))
Gc = 6.674e-11; m = 61e3; L = 15.0
BODIES = {'Earth': (3.986e14, 6.371e6), 'Titan': (8.978e12, 2.575e6), 'Moon': (4.905e12, 1.737e6), '1 km asteroid (rho 2000)': (Gc * 2000 * 4 / 3 * math.pi * 500 ** 3, 500.0),
          'Deep space, 1 AU (Sun tide)': (1.327e20, 1.496e11)}
rows = {}
for name, (GM, R) in BODIES.items():
    g = GM / R ** 2; T = 2 * GM / R ** 3
    W = m * g if 'Deep' not in name else 0.0
    F = 1.5 * W if W else 0.15 * m * 9.81
    quad = m * g * (L / R) ** 2 if W else 0.0
    p = F / T; q = p / L
    rows[name] = dict(surface_g=round(g, 5), tidal_radial_s2=f'{T:.2e}', force_needed_kN=round(F / 1e3, 1), ordinary_tidal_residual_N=f'{quad:.1e}',
                      dipole_needed_kg_m=f'{p:.2e}', pole_mass_equivalent_t_at_15m=f'{q / 1e3:.2e}', pole_mass_over_shuttle=f'{q / m:.1e}',
                      holding_energy_U_eq_pg=('n/a (no lift)' if not W else f'{p * g / 1e12:.3g} TJ'), mgh_200m_GJ=round(W * 198.7 / 1e9, 3) if W else None)
out = dict(header='ALL bodies. ALL sponsors. 2026-2226.', lane='PROTOTYPE (non-canon) BMD-1, tidal-force question', derivation=__doc__.split('\n\n', 1)[1].strip(), cases=rows,
  answer=dict(
    ordinary_or_position_coupling='NO. Any coupling linear in the tidal tensor acting on positive density gives exactly zero centre-of-mass force at first order (any shape); the residual is ~M g (L/R)^2, a few micronewtons at Earth.',
    with_new_law='YES only with an engineered gravitational DIPOLE moment p (an internal vector coupled to T): F = T . p, F/W = 2 q L /(m R).',
    scaling='At a body\'s surface T = (8 pi/3) G rho_body: set by density, not size. Required pole mass ~0.75 m R / L (3e5 x the shuttle at Earth, 1e5 at Titan, ~25 at a 1 km asteroid). Deep space: effectively zero capacity.',
    energy='U = p g = F R / 2, reference-independent: ~2.9 TJ to hold a 0.9 MN lift at Earth (16,000x the 0.18 GJ lift work), ~0.16 TJ at Titan. Stored and recoverable, but it must be held somewhere.',
    conservation='Local stress-energy closes in the Newtonian limit only if the dipole is also an active source, which needs negative active mass at one pole: exotic stress-energy of order 1e7 t per pole at Earth.',
    consequence_for_H1='The tidal field can serve as a partner SELECTOR (weights) but not as the force SOURCE at planetary scale. If BMD-1 keeps the tidal weighting, the 0.9 MN must come from a separately POSTULATED nonlocal exchange. That is a chosen fictional law, not a derivation.'),
  H2_revision='The review is right: m dk |Phi| depended on an implicit zero at infinity, so the TJ-PJ figures are not a decisive contradiction. Correct framing: a change in k that does not conserve total gravitational charge makes the energy ledger reference-DEPENDENT, which is itself the defect. '
              'A charge-conserving version must move the compensating charge somewhere; putting it close by makes a mass dipole, which is case (2) above with the same reference-independent cost U = F R / 2. '
              'So H2 is unsupported and needs a reference-independent energy law. It is not proven impossible, and in its minimal-energy form it converges on the dipole.')
json.dump(out, open(os.path.join(H, 'bmd1_tidal_force.json'), 'w'), indent=1)
if __name__ == '__main__':
    for k, v in rows.items(): print(k, v)
