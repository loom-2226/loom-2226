# Rev 7 Wayfarer flight laboratory: qualification gaps (27 October 2026)

**Status: independent-review handoff. NOT CERTIFIED, NOT CANON, NOT RUNTIME.**
This document summarizes recorded lab results and live-repository engineering context. It does not modify those original results or decide spacecraft canon.

## 1. What is numerically demonstrated

- **55/55** local regression tests and **25/25** Rev 7 G10 engineering checks passed. G10's 25 checks are *not* Navigator mission tests.
- 11 baseline experiments and 14 advanced scenarios executed, including deliberate failures and canonical metric INDETERMINATE cases; **18/18** additional Wayfarer six-mode/three-axis/translation sweeps passed numerical criteria.
- **9/9** historical Astra fixed-RCS reference cases reproduced; the successful 300 kN arrangement is **24 non-axial thrusters uprated in their original mounts plus eight retained 25 kN axial thrusters**, not an eight-engine-only replacement.
- Original 25 kN RCS 180° reversal: 40 s PASS, 10 s FAIL. Hypothetical fixed 300 kN: 10 s terminal PASS, *sustained* gate entry 10.62 s, cluster-out 10 s FAIL. Separate eight-added-gimbal architecture: 10 s FAIL, 12 and 14 s PASS.
- All six torch modes passed modeled 120-second burns; HARD and LIMIT preserve the **4 g instantaneous crew cap**. Normal remass used: ECON 136.33 kg, CRUISE 681.66 kg, EXPEDITE 2,726.64 kg, FAST 5,564.57 kg, HARD 12,150.87 kg, LIMIT 18,178.89 kg.
- NASA 42 replay of realized commands differed by at most ~6.99e-6° over 700 samples. GMAT R2026a 600 s torque-free *surrogate* differed by ~0.00232 m position and ~1.30e-6 m/s velocity. These comparisons validate numerical integrator behavior under stated assumptions, **not** installed Wayfarer hardware or its controller independently.
- Canonical metric operating requests pass sequence validation but **HOLD** at \`METRIC_RAMP\` with unresolved physical arrival and conservation ledgers; experimental coordinate maps remain NON-CANON.

See \`full_flight_20261027/FLIGHT_TEST_REPORT.md\`, \`RCS_300KN_REPRODUCTION.md\` and \`CANON_METRIC_OPERATIONAL_RESULTS.md\` for exact test qualifications.

## 2. What is not qualified

**A. Configuration and integration:** Rev 7 candidate S1 is ~1,167.68 t and uses 32 fixed 25 kN RCS. The separately governed E1 RCS vehicle model uses **16 vectored hardpoints**, configuration-dependent mass/CG/full tensor, and ~1,158.5 t with a docked launch. They are distinct engineering configurations. On main, \`src/wayfarer_mass_inertia_authority.py\` provides a functioning E1 engineering mass/inertia model; it does **not** silently qualify Rev 7's entire installation. Reconcile before selecting a flight-authority model. The old engineering-priority text labels complete inertia OPEN, while later E1 RCS engineering documents qualify a narrower configuration-aware rigid-body envelope. Do not erase this distinction.

**B. RCS propulsion hardware:** No selected physical thruster model, installed upgraded engine mass/inertia, working fluid, Isp/exhaust velocity, feed/pump/header/transient capacity, duty/valve response, minimum impulse bit or finite installed propellant accounting. RCS impulse is known from the lab, but consumption is **null/unknown**, not zero.

**C. Installation limits:** No rated local bracket/fastener/load path, sufficient installation reinforcement, thermal/duty ratings or actual plume geometry/impingement/clearance. Common-mount modeled peaks are ~25.0 kN original, ~300.001 kN hypothetical fixed upgrade and ~324.632 kN added gimbals; the CRUISE torch demand is ~11.361 MN. The seven hardware scenarios all remain overall **HOLD** regardless of scoped numerical PASS/FAIL.

**D. Torch physical integration:** Existing modes, force/remass constraints, thermal budgets and idealized thrust vector trim have numerical evidence. Installed feed transients, radiator endurance, thermal interface and load-path verification are still assumptions or missing evidence, not demonstrated physical hardware certification.

**E. Mission integration:** Rev 7 G10's E1, FR-01B-R and MV-01 end-to-end Navigator flights were **deferred as non-gating follow-up** under the proposed v0.5 certification basis. No authoritative, executable mission fixtures or card import demonstrate the complete E1 cross-scale mission. This should not be disguised as 25/25 mission PASS.

**F. Real-world certification:** Supplier/material acceptance, assembled-hardware tests, thermal cycling, fatigue, plume measurements, flow/transient tests and physical component qualification are not present. They cannot be conjured from software traces. Whether LOOM gameplay needs component-level fidelity is a separate modeling decision.

## 3. Minimum prioritized follow-up

1. **Select/reconcile one candidate configuration** against existing E1 mass/CG/inertia and RCS authority; explicitly record the differences. Do not build a second general mass engine.
2. **Fly one continuous conventional Wayfarer scenario** using existing code, from explicit initial state through torch/coast/RCS/finite remass, with no reset. This is the next highest-information experiment, not a new architecture project.
3. For the configuration actually being considered, **declare the smallest defensible RCS feed/propellant envelope** to close conservation and duty in that mission. Carry engineering assumptions as such.
4. Use existing \`hardware_assess.py\` to check **mount, plume and thermal constraints** of that same configuration; leave unbacked capacities HOLD. Explore 300 kN or gimbal installation only if the mission shows the standard architecture is insufficient.
5. If integrated Navigator qualification is desired, identify the **specific existing fixture/import boundary** and perform a narrow E1/FR-01B-R/MV-01 experiment only for regimes that have defined physics. Never synthesize metric arrival state to force an end-to-end PASS.

**Stop once a coherent conventional mission and justified engineering operating envelope are demonstrated.** Do not escalate to comprehensive FEA/thermal CFD/valve fabrication without a consequential observed limitation.

## 4. Intentionally parked

- Calibrated canonical \`U^M_\gamma\`, metric environment correction, finite wake/energy/momentum exchanges and terminal arrival matching.
- Physical hardware certification without independent evidence.
- Detailed Loom formation/domain-fit and unrequested comprehensive qualification machinery.
- Canon or runtime promotion. The candidate report's \`certified=false\` and existing PR #432 remain unchanged.

## Sources to review in order

1. \`full_flight_20261027/FLIGHT_TEST_REPORT.md\`
2. \`HARDWARE_QUALIFICATION_RESULTS.md\`
3. \`RCS_300KN_REPRODUCTION.md\`
4. \`CANON_METRIC_OPERATIONAL_RESULTS.md\`
5. \`source_manifest.json\`, \`configs/\`, \`experiments/\`, \`flightlab.py\`, \`hardware_assess.py\`, \`test_*.py\`
6. Exact Rev 7 candidate [PR #432](https://github.com/loom-2226/loom-2226/pull/432) at \`3485830a56dfead79b2ef8bba031a595b536fbb5\`
7. Main repository \`engineering/experience_one/WAYFARER_E1_RCS_FLIGHT_DYNAMICS_GEOMETRY_INTERFACE.md\` and \`src/wayfarer_mass_inertia_authority.py\`

**Review standard:** distinguish numerical PASS, declared engineering assumptions, missing physical evidence, deferred mission fixtures, and deliberately parked science. Never turn one class into another.
