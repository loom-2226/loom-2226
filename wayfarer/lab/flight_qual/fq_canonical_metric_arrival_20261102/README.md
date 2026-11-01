# Canon II Metric arrival-velocity seam (CCR-2026-0003)

ALL bodies. ALL sponsors. 2026-2226.

DRAFT LAB. Source baseline main 092206902bce2f6a94bb8466ac1497782d068a33. No Navigator or governing canon edits.

The canonical operation computes natural arrival velocity **only** for a phase
explicitly declaring arrival_rule=ENERGY_ORBIT_RELATIVE_B and
canon_arrival.regime=ORDINARY_SOLAR_SYSTEM, with declared Sun/body snapshots,
GM, mass and solar reflex. Actual pre-Metric velocity and position are mapped
forward through ENERGY speed and transported Sun-local heading B.

Execution status ARRIVAL_VELOCITY_RESOLVED includes natural velocity, mismatch,
transit time and declared Sun E/p/L identities by construction. The destination
center is a reference only. All environmental, path, collapse certification,
and capture questions remain HOLD, including physical terminal position.
The generic flightlab refuses to resume ordinary motion from this unresolved
position. Unspecified/out-of-regime requests HOLD; ENERGY-forbidden outward
requests fail closed. No false crew-rated qualification.

FQ11 Earth-Mars nominal and 1% underburn, and FQ12 Jupiter-Earth nominal and
1% underbrake, now obtain forward-B velocity from the canonical operation,
not separate calculations. SEAM_PARITY.json compares replay numbers against
the previously merged qualification evidence (1e-6 absolute tolerance).
Historical FQ11/FQ12 result JSON remains byte-for-byte unchanged.

FQ1-FQ10 source, qualified fixtures, and evidence remain pinned and unchanged.
New tests check explicit scope, velocity-only dispatch, forbidden outward leg,
unknown collapse and certification gates. No Navigator, ship cards, or canon
text change.

Frozen-potential and approximate barycentric frame, no full N-body work/torque,
physical collapse, capture, planetary gravity in long burns, real thermal
qualification. E/p/L balances are algebraic identity entries, not evidence
for a physically derived Metric coupler. Stage-to-stage actuator internal
states remain reset in the existing FQ11/FQ12 flight-lab runners.

STOP at draft PR for kT review.
