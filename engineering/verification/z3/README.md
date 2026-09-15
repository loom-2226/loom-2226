# LOOM Z3 specialist verification — Wayfarer mass/state POC v0.1

Status: ENGINEERING VERIFICATION POC / NON-CANON / DOES NOT REPLACE QUALIFICATION.

## Selected family

The first formal constraint family is Wayfarer torch mass/remass inventory plus torch/high-metric operating-state compatibility. It is deliberately small and exact: authoritative Python engineering artifacts expose rational mass identities, inventory limits, a protected-water rule, and a Boolean mutual-exclusion rule with little translation ambiguity.

Nonlinear burn integration and logarithmic delta-v remain in Python and are not approximated here.

## Authority/provenance

Authoritative `main` inputs are `src/wayfarer_torch_baseline_recovery.py` and `src/wayfarer_torch_performance_remass_envelope.py`: reference wet mass 1158.5 t; dry mass excluding working fluid/water 858.5 t; combined inventory 300 t; normal remass 250 t; protected water 50 t; post-normal-remass mass 908.5 t; torch/high-metric mutual exclusion; and normal remass stops before protected reserve.

SMT values use exact rational arithmetic and masses are metric tonnes.

Expected hostile checks: baseline SAT; forced 251 t remass consumption UNSAT with named core; simultaneous torch/high-metric activation UNSAT with named core.

Native Pixel invocation:

```bash
bash engineering/verification/z3/run_wayfarer_mass_state_z3.sh
```

A SAT result establishes only that the encoded constraints have a satisfying model. It does not certify physical completeness, correctness, optimality, reactor physics, or the spacecraft.
