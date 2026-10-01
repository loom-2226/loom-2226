# Phase 4F Pluto small-moon closure

Nix, Hydra, Kerberos and Styx now use direct JPL/NAIF PLU060 through its native endpoint and an explicit LOOM propagated estimate thereafter.

The continuation implements the published PLU060 six-body dynamical model using exact internal GMs from the JPL comment file, direct DE440 external forcing, and SciPy DOP853. Production uses rtol=1e-12 and max_step=10800 s, a step already demonstrated converged in the preserved 2180–2199 withheld-truth experiment.

Prior qualification:
- 2180–2199: worst annual-sampled error 13.265 m at 10800 s max step.
- 2013–2199 / 186 years: worst annual-sampled error 46.631 m.
These establish reproduction fidelity inside PLU060 truth, not direct truth after 2199.

Production serialization check:
- all four output SPKs cover through 2251-01-01 UTC projection;
- qualified propagated coverage begins exactly at the PLU060 authority seam;
- one-day overlap with PLU060 was retained only for serialization/seam checking;
- worst production-SPK overlap error was 0.006563 km (Nix).

Post-PLU060 authority is EMPIRICAL_PROPAGATED_2250 / PROPAGATED, navigation_grade=false, declared uncertainty 1000 km. It is never DIRECT.

At 2226-01-01 TDB the live governed Inspector resolves all 110 catalog objects: 90 DIRECT, 17 PROPAGATED, 3 ESTIMATED_RELATIVE, 0 unresolved.
