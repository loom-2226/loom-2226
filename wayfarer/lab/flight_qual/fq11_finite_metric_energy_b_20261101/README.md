# FQ11 finite flight: Earth → Mars | lab ENERGY-B | 2026-11-01

**ALL bodies. ALL sponsors. 2026–2226.**

**DRAFT QUALIFICATION / NON-CANON / NOT NAVIGATOR.** Base `main` `096796311afba04b71294558b360dd09bd11112b`, geometry `4d598212aeb46fab14b326a6023bb6d55e7d584599d91fe821ef8a2f2d837331`. Requires FQ11-CALC from PR #442 for an **initial guess only**, not acceptance evidence.

### Real-state path

1. Run pre-jump CRUISE torch + shutdown coast through the original `flightlab.run` rigid-body, mass, throttle, TVC, RCS and gravity integrator. The actual position, velocity, mass, attitude, angular rate and remass become the handoff. The preburn nominal setpoint is from FQ11-CALC, but the actual end state is **not imposed**.
2. Call `canonical_metric_operation` with that **measured** end state. The canonical seam still returns **HOLD**, as it should. Only this separate lab FQ11 runner uses the kT-approved ENERGY-B law **forward** from that state, with Sun-only moving planetary ephemerides and NORMAL mode time. No early return or production/default canonical Metric replacement.
3. Measure the mismatch against moving Mars at collapse, then command the real RCS turn (direct axis command), finite CRUISE torch trim and shutdown coast using the existing flightlab dynamics. If the residual exceeds 1 m/s, run an actual final RCS translation and **measure** its final error against moving Mars. With the enforced 0.2 s RCS update, neither test case needs that final correction. Preserve source mass/tank, quaternion, position, velocity and angular rate between staged calls.
4. Replay 1% short preburn. Verify larger mismatch appears and finite trim recovers inside 1 m/s. Negative Earth→Jupiter without preburn must be ENERGY-forbidden (`v² < 0`).

### Evidence and acceptance

`run_fq11_finite.py` produces `FQ11_RESULT.json`. Nominal and 1% underburn both satisfy **measured** preburn, measured nonzero forward mismatch, trim within CRUISE rocket-equation Δv derived from current remaining remass above the protected 5-tonne floor, 5-tonne reserve, independently summable remass depletion, source-mode 4 g acceleration limit and **actual capped jet-power ceiling**, and final moving-Mars match within **1 m/s**. E/p/L identities close with the Sun as declared exchange partner, but **are identities by construction, NOT independent pass evidence or a demonstrated physical coupler**.

The **nominal uncapped CRUISE card** computes 11.361004025 TW against a rounded 11.361000 TW ceiling, a **4.025 MW (0.0000354%) source-card rounding difference**. The actual integrator's `torch_force()` caps thrust at 11,361,000 N, so **actual capped jet-power over ceiling = 0 W**, computed from the realized force after enforcing the same source ceiling. The raw float multiplication may read 0.00195 W above 11.361 TW, which is explicitly reported as numerical roundoff, not a physical exceedance. This is a card/interface check only; real fins' transient temperatures, coupling, fuel and radiation remain OPEN. No 1 ppm allowance is needed for actual capped power.

### Derived controller requirement and convergence

[**Wayfarer WF-RCS-FQ11-01**](../../../docs/RCS_CONTROL_LOOP_DERIVED_REQUIREMENT_2026_11_01.md) is **DERIVED LAB**, `>=5 Hz` for RCS feedback/actuator update, **not** hardware canon. [Five-point convergence evidence](RCS_TIMESTEP_CONVERGENCE.md) covers dt 0.1/0.2/0.4/0.5/1.0 s. FQ11 uses dt **0.2 s** for every RCS stage; `flightlab.run` rejects **all RCS turns and translations at dt >0.2 s by default** (negative test at dt 0.4 s). Only deliberate sensitivity studies may set `allow_coarse_rcs_dt_for_sensitivity_study=True`; FQ11 does not use it for qualification. The legacy combined flightlab test now runs at 0.2 s, with FQ1–FQ10 unchanged.

**Measured with 0.2 s:** nominal/1% under-burn RCS turns use **144.053/327.135 kg**; total remass **2.983/3.172 t**; final Mars-relative velocity error **0.121/0.481 m/s**. No final RCS translation needed. This contrasts with coarse-step controller chatter and 30.933/60.647 t water use; those are retained in the convergence evidence, not overwritten in earlier FQ records.

### Scope and limits

- **FROZEN-POTENTIAL CAVEAT:** no exact global Killing energy for moving Sun/planets; simulated moving endpoints are Sun-only Kepler propagation and endpoint `Sun + local-body half-Hill` potential is frozen for the Metric ENERGY jump.
- Gravity **during the finite burns** is Sun gravity through existing `flightlab.run`; local Earth/Mars gravity and full N-body tidal work during burns are **not closed**. Bodies' source-epoch centers are used as the reference endpoints; half-Hill is a diagnostic potential/arrival shell, **not physical collapse policy**.
- Metric transit is relational, **not ordinary XYZ motion**. The canonical seam's HOLD remains in force outside this explicitly approved lab comparison. The Sun's E/p/L work, impulse and angular transport are declared bookkeeping for the miracle; independent physical closure remains OPEN.
- **Staged implementation limitation:** each finite conventional segment calls original `flightlab.run` with the exact carried physical state but resets internal actuator command/lag state at a stage boundary. All stage endpoints, tanks, and actual energy/momentum/angular ledger declarations are preserved. This is **not** one continuous hardware flight/controller execution.
- The available trim Δv is calculated from the actual carried mass, source CRUISE exhaust velocity, and remass above the 5-tonne floor, **not** an invented numerical budget threshold. Source 4 g and jet-power bounds do not validate all structural/crew/thermal hardware.
- No orbital capture, planet-centered navigation, or reliable geometric admissibility qualification. FQ1–FQ10 source/cases/results remain unchanged.

### Execute

```bash
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 python wayfarer/lab/flight_qual/fq11_finite_metric_energy_b_20261101/run_fq11_finite.py
```

**If the measured result fails any acceptance criterion, the FQ11 report becomes HOLD.** No acceptance threshold is changed to hide numerical or control failure. No canon or Navigator changes authorized.
