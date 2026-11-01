# Wayfarer RCS attitude-control cadence | DERIVED LAB REQUIREMENT

**ALL bodies. ALL sponsors. 2026–2226.** Source: draft FQ11 Earth→Mars ENERGY-B finite flight, current geometry SHA256 `4d598212aeb46fab14b326a6023bb6d55e7d584599d91fe821ef8a2f2d837331`. **NON-CANON, LAB-ONLY, not independently qualified hardware.**

**Requirement WF-RCS-FQ11-01 (DERIVED):** The finite RCS attitude/translation controller used for this Wayfarer FQ11 qualification **shall update at ≥ 5 Hz** (`dt ≤ 0.2 s`) while commanding an `rcs_turn` or `rcs_translate`. The simulator's integrator timestep is also its feedback/actuator update timestep. This is a **numerically observed stable operating requirement for this controller and geometry**, not an independently established minimum hardware flight-computer frequency.

**Evidence:** [FQ11 timestep convergence](../lab/flight_qual/fq11_finite_metric_energy_b_20261101/RCS_TIMESTEP_CONVERGENCE.md) shows approximately 144/327 kg turn consumption at 0.1, 0.2 and 0.4 s, versus 20,276/30,238 kg at 0.5 s and 28,095/37,007 kg at 1.0 s. The sharp stability cliff at 0.4→0.5 s makes 5 Hz the **conservative adopted lab requirement**, with a factor-of-two margin in update rate to the observed threshold.

**Enforcement:** `flightlab.run` rejects RCS turn/translation phases if `dt > 0.2 s` **when** `experiment.require_rcs_control_min_hz=True`. FQ11 sets this flag on every staged run, including final correction; its negative test asserts rejection at 0.4 s. The opt-in gate is deliberate: historic exploratory flightlab cases (including an older combined test at 0.4 s) must not be silently invalidated or their evidence rewritten. Source FQ1–FQ10 at their accepted timesteps retain their qualification criteria and unchanged artifacts.

**Not a hardware certificate:** Further controller changes, RCS geometry changes, valve/lag/sampling changes or real flight instrumentation require renewed stability evidence. E/p/L Metric identities and transient torch/fin thermal closure are separate open questions.
