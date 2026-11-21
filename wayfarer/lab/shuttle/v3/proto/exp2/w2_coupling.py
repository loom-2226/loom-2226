"""W2 decisive question: can any KNOWN coupling give a finite, local, planet-referenced force of ~0.9 MN at 0-200 m?
NON-CANON prototype lane. ALL bodies. ALL sponsors. 2026-2226.
Bounding arithmetic only. Requirement: 1.5 x weight of a 61 t shuttle = 0.90 MN, over a ~67 m^2 planform (13.5 kPa), at heights up to 200 m."""
import json, math, os
H = os.path.dirname(os.path.abspath(__file__))
G, Gc, MU0, EPS0 = 9.81, 6.674e-11, 4e-7 * math.pi, 8.854e-12
F = 1.5 * 61e3 * G; A = 67.0; P = F / A; R_E = 6.371e6; B_E = 50e-6
rows = {
 'gravity: attracting mass 10 m above the ship': dict(value=f'{F / 61e3 * 100 / Gc:.1e} kg', verdict='impossible (an asteroid overhead)'),
 'gravity: negative mass below': dict(value='same magnitude, and negative mass is not known to exist', verdict='impossible in known physics'),
 'Lorentz force on a current across Earth\'s field (10 m conductor)': dict(value=f'{F / (10 * B_E):.1e} A', verdict='impossible; return current also carries the reaction'),
 'magnetic dipole in Earth\'s field gradient (~B/R_E)': dict(value=f'{F / (3 * B_E / R_E):.1e} A m^2 dipole', verdict='impossible'),
 'electrostatic pressure, capped by air breakdown (3 MV/m)': dict(value=f'{0.5 * EPS0 * 3e6 ** 2:.0f} Pa max vs {P:.0f} Pa needed', verdict=f'{P / (0.5 * EPS0 * 9e12):.0f}x short; attraction only unless the ground is charged'),
 'inductive repulsion over seawater (eddy-current maglev)': dict(value=f'B at the water surface ~{math.sqrt(2 * MU0 * P):.2f} T; a coil field falls ~1/r^3', verdict='works only within metres of the surface; strong fields over people; no 200 m reach'),
 'aerodynamic (fans, rotors)': dict(value='known; momentum to the air', verdict='possible but it IS downwash; not exhaust-free in the disturbance sense'),
}
out = dict(header='ALL bodies. ALL sponsors. 2026-2226.', lane='PROTOTYPE (non-canon)', requirement=dict(force_MN=round(F / 1e6, 2), pressure_kPa=round(P / 1e3, 1), reach_m=200),
  known_physics=rows,
  conclusion='No known coupling gives a ~1 MN planet-referenced force at 200 m. Gravity needs absurd masses; electromagnetic routes are capped by air breakdown or fall off within metres. '
             'So W2 cannot be an ordinary force. It is coherent only as an extension of the canon metric miracle (M2), where a declared nonlocal momentum partner already exists (CANON II §7.1b). '
             'Inside M2 it needs three things, all unknown: (1) a powered channel (ENERGY-B gives height only if paid), (2) a generator well below the canon-scaled estimate (~13 t at L^2 vs a ~3.5 t ceiling, ~4x short), '
             '(3) a boundary that can coexist with water, air and people (the W3 unknown). Outside M2 it would be a third miracle.')
json.dump(out, open(os.path.join(H, 'w2_coupling.json'), 'w'), indent=1)
if __name__ == '__main__':
    print(out['requirement'])
    for k, v in rows.items(): print(f'{k:62s} {v["value"]:45s} {v["verdict"]}')
