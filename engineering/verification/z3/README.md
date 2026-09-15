# LOOM Z3 specialist verification — Wayfarer mass/state POC v0.1

Status: ENGINEERING VERIFICATION POC / NON-CANON / DOES NOT REPLACE QUALIFICATION.

## Selected family

The first formal constraint family is Wayfarer torch mass/remass inventory plus torch/high-metric operating-state compatibility. It is deliberately small and exact: the authoritative Python engineering artifacts already expose rational mass identities, inventory limits, a protected-water rule, and a Boolean mutual-exclusion rule with little translation ambiguity.

Nonlinear burn integration and logarithmic delta-v remain in Python and are not approximated here.

## Authority/provenance

Authoritative `main` inputs:

- `src/wayfarer_torch_baseline_recovery.py`
  - reference wet mass 1158.5 t
  - dry mass excluding working fluid/water 858.5 t
  - combined working-fluid/water inventory 300 t
  - normal remass 250 t
  - protected water reserve 50 t
  - post-normal-remass reference mass 908.5 t
  - torch/high-metric thermal-field mutual exclusion
- `src/wayfarer_torch_performance_remass_envelope.py`
  - normal remass envelope stops before protected 50 t reserve
  - numerical burn/delta-v relationships remain Python authority

SMT values use exact rational arithmetic and masses are explicitly metric tonnes.

## Expected hostile checks

`wayfarer_mass_state_v0.1.smt2` => `sat`.

`wayfarer_mass_state_negative_remass_v0.1.smt2` => `unsat`, with a core containing the 250 t inventory/consumption-limit constraint and the forced 251 t contradiction.

`wayfarer_mass_state_negative_mode_v0.1.smt2` => `unsat`, with a core containing mutual exclusion plus both forced-active states.

## Pixel

Native Z3 is invoked directly; Python bindings are not required:

```bash
bash engineering/verification/z3/run_wayfarer_mass_state_z3.sh
```

A SAT result establishes only that the encoded constraints have a satisfying model. It does not certify physical completeness, correctness, optimality, reactor physics, or the spacecraft.
