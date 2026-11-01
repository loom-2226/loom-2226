# FQ12 | inbound Jupiter → Earth | ENERGY-B lab arrival

**ALL bodies. ALL sponsors. 2026–2226.** **DRAFT LAB ONLY, NON-CANON, NOT NAVIGATOR, DO NOT MERGE WITHOUT kT.** Baseline main `79c86eaba4ba651f81ddbee85a3a928a14eda21e` (merged PR #443); geometry `4d598212aeb46fab14b326a6023bb6d55e7d584599d91fe821ef8a2f2d837331`.

## Scope, sequence, and outcome

Standalone `run_fq12.py` loads source-stamped `FQ12_INPUT.json`, reads Wayfarer's current mass and CRUISE cards from the accepted fixture, and reports measured `FQ12_RESULT.json`. No Navigator or canon file, existing FQ1–FQ11 qualification output, ship card, or flight dynamics source is edited.

1. **No preburn:** start matched to Jupiter's source-epoch J2000 heliocentric state. Query `canonical_metric_operation` with that state; **HOLD remains intact**. Laboratory-only NORMAL Metric time is about 10,117 seconds, with Earth propagated under Sun-only gravity.
2. **Forward ENERGY-B** from the Jupiter state: Sun-frame, frozen Sun + endpoint-body half-Hill potentials, and local Sun radial/prograde/orbit-normal heading preservation. Do not inverse-solve a matched Earth arrival. Initial Earth-relative velocity mismatch is about **10.392 km/s**.
3. **Real RCS turn** over 220 seconds through unchanged `flightlab.run` at **0.2 s (5 Hz)**, guarded by the newly default-on cadence constraint. Aim using the **actual** source torch force vector through the current CG; it is nominally deflected 0.361° from body -X. Ignoring this generates an artificial ≈65 m/s out-of-plane residual over the long brake.
4. **Finite CRUISE braking** through the real flightlab thrust, mass and Sun gravity integrator, plus shutdown coast. Nominal burn is about **1,070 seconds**, consuming roughly **6.08 tonnes** of remass; negative is **1% shorter braking duration**.
5. **Real-state trim:** recompute the error to *moving Earth* after each actual burn. If error is already ≤1 m/s, do **not** invent a sub-pellet millisecond torch pulse. If above 1 m/s, run another **finite CRUISE torch phase** using the current mass, thrust geometry, target motion and remass ledger. The 1%-under-brake case must display a significantly larger pretrim miss and then recover to ≤1 m/s.

## Acceptance and epistemic limits

Pass: actual Earth-relative velocity error **≤1 m/s**, source-derived 5 t remass floor and closed finite-phase consumption ledger, source **4 g** acceleration limit, **actual capped CRUISE jet power** ≤ declared ceiling; 5 Hz RCS turn. Negative: 1% under-brake introduces a measured >50 m/s additional miss, real finite trim recovers. Report source nominal-card **4,025,000 W** rounding difference separately from **0 W actual over-ceiling**.

**FROZEN POTENTIAL CAVEAT:** planets move but gravitational potential is sampled only at endpoints; no exact global Killing energy or fully closed N-body work. The approximate Sun-barycentric counting frame and the Sun as the E/p/L momentum and torque partner are declared lab assumptions. Solar E/p/L balancing is **IDENTITY BY CONSTRUCTION**, not independent physical validation. The canonical Metric seam remains HOLD.

Sun gravity is modelled during actual conventional RCS/torch phases; Earth's local gravitational field during braking, full N-body dynamics, atmospheres, orbital capture, and physically qualified 0.5 Hill collapse are not. Stage calls carry position, velocity, mass, tank, attitude and angular rate but reset actuator internal lag at handoffs. Real torch fin thermal transient, reactor/RCS supply and pellet minimum pulse timing remain OPEN. Numerical 4 g and actual capped jet-power conformance do not validate hardware or human survivability.

## Replay

```bash
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 python wayfarer/lab/flight_qual/fq12_inbound_metric_energy_b_20261101/run_fq12.py
```

Only the three files in this FQ12 folder belong to this draft. No modifications to FQ1–FQ11 results, wayfarer geometry, canon, or Navigator.
