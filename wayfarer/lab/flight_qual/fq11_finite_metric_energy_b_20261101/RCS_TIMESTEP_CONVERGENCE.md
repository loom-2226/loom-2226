# FQ11 RCS timestep convergence | frozen, read-only diagnostic

**ALL bodies. ALL sponsors. 2026–2226.** Original draft PR #443, head `bf39e700d3f4785557c08372cf7b5f6ded22d4d4`, geometry `4d598212…`. Source: unchanged FQ11 finite flight model and source RCS controller; only the RCS-stage timestep changes. Historical ≥0.4-second runs were performed **before** installing the scoped 5 Hz guard, which correctly rejects them now. No FQ1–FQ10 evidence is modified.

| RCS integration/control dt | Nominal 94.06° turn remass | 1% under-burn 158.70° turn remass | Final RCS translate | Comment |
|---|---:|---:|---|---|
| 0.1 s | 144.051 kg | 327.130 kg | Not needed | Reference convergence |
| 0.2 s | 144.053 kg | 327.135 kg | Not needed | **FQ11 selected; 5 Hz** |
| 0.4 s | 144.068 kg | 327.166 kg | Not needed | Numerically stable, but only 2.5 Hz |
| 0.5 s | 20,276.384 kg | 30,238.123 kg | Under-burn 17,538.391 kg | Feedback instability |
| 1.0 s | 28,094.833 kg | 37,006.923 kg | Under-burn 20,797.481 kg | Controller chatter/saturation |

**Original 1.0 s trace diagnosis:** 65/75 net turn-torque sign changes; 215/225 and 214/225 allocation-limited steps; some simultaneous opposing jets. Ideal finite-220-s symmetric impulse benchmarks: 153.6 kg (nominal), 349.0 kg (under-burn), using current inertia, constrained nozzle arm and source `v_e=1960 m/s`. The previous 3.09 m/s translation ideal was about 1,786 kg; large one-second controller usage is not an exhaust-card or tank bookkeeping defect. FQ1–FQ9 comparable cases used much finer steps and consumed near expected impulse budgets.

**Selected 0.2 s FQ11 results:** measured post-trim moving-Mars velocity errors 0.12078 and 0.48099 m/s, corresponding whole-sequence water 2.9828 and 3.1717 tonnes. No additional final RCS translation. Nominal/under-burn forward B raw mismatches remain 19.431 and 77.740 m/s. FQ11 source/geometry unchanged; only the RCS update resolution changed.

**Requirement and limitations:** [WF-RCS-FQ11-01](../../../docs/RCS_CONTROL_LOOP_DERIVED_REQUIREMENT_2026_11_01.md), minimum 5 Hz **DERIVED LAB**, not hardware. Timestep and controller frequency are coupled within this numerical integrator; these data do not separately establish real valve dynamics or thermal/fins qualification. The 0.4 s result being stable does not imply hardware at 2.5 Hz is acceptable.
