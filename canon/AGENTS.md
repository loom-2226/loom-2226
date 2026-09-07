# Canon subtree agent rules

Applies to `canon/**`.

## Authority

Current canon is changed only through the governing change-control process. A file being under `canon/current/` does not by itself authorize an agent to edit it.

Before mutation:

1. load root governance/workstate;
2. identify the governing canon source(s) and active baseline/amendment relationship;
3. verify an exact registered Canon Change Request exists when material canon change is proposed;
4. verify the CCR is `APPROVED_FOR_IMPLEMENTATION` before beginning the controlled canon implementation;
5. identify downstream engineering/runtime/data/3D/media invalidation using `governance/dependencies/component-map.yml`;
6. plan authority/baseline/hash/validation/compatibility/archive updates;
7. determine required WALTER assurance.

Formal CCR lifecycle:

- `governance/changes/README.md`
- `governance/changes/CCR_REGISTRY.yml`
- `governance/changes/CCR_SCHEMA_v1.0.yml`
- `governance/changes/CCR_TEMPLATE_v1.0.yml`

A GitHub CCR issue is intake/discussion. It is not by itself the durable approval record.

## Promotion boundary

`APPROVED_FOR_IMPLEMENTATION` means the canon change has been approved for controlled implementation.

It does **not** mean the proposed content is already governing canon.

The CCR becomes `IMPLEMENTED` only after the authorized canon implementation lands on authoritative `main` with required authority/baseline/hash/validation changes completed.

## Prohibitions

- do not promote research/simulation output directly into canon;
- do not rewrite canon to make a runtime/model result fit;
- do not silently overwrite/suppress superseded sources; archive them with explicit lineage;
- do not change M1/M2/M3, chronology, Mc-299m, ship constants, history or other governing claims from chat enthusiasm alone;
- do not treat anomaly, witness, xeno or LLM material as physical calibration unless the approved canon change explicitly and defensibly establishes that move;
- do not treat CCR approval as an upgrade of evidentiary status;
- do not implement a CCR beyond its approved claims/scope without returning to change control;
- do not approve a CCR that materially depends on a frozen/preregistered research result before that result is dispositioned under its frozen gate.

## Scoped amendments

A governing amendment must name its parent and scope. Outside that scope, the parent remains governing.

The existing Wayfarer v2.4a amendment is currently recorded as a scoped governing amendment pending baseline-registration reconciliation; do not alter that relationship casually.

## Tests / validation

Canon changes require the validation/hash/baseline work specified by change control and the CCR before promotion.

If no registered `APPROVED_FOR_IMPLEMENTATION` CCR exists, stop at a finding or CCR proposal.
