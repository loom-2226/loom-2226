# Wayfarer E1 — Drivetrain Spatial Closure Workplan v0.1

**Date:** 2026-09-17  
**Class:** ENGINEERING  
**Status:** DRAFT / PROPOSED / NON-CANON  
**Campaign mutation:** ZERO  
**LLM calculation authority:** ZERO  
**Torch vehicle interface:** frozen input; no redesign  
**Component certification:** NOT CLAIMED

## 1. Objective and definition of done

Complete the unresolved four-tank, protected-reserve, remass-feed, conditioning, mounting and drivetrain spatial installation around the existing Wayfarer E1 engineering baseline. Generate a **separate, deterministic drivetrain GLB** that mates to the supplied standalone torch GLB in the common ship frame, plus a derivative integrated review GLB generally contained within the current ship shell. Deliver RCS-style separate specification sheets and a traceable qualification/holds report.

Done means: reproducible standalone geometry; exact, audited mating transform to the unchanged torch; complete inventory and interface accounting; no unexplained hard clashes or duplicated systems; measured remaining courier/crew envelope; explicit disposition for every unsatisfied fit requirement or physical-technology hold. If fit fails, report BLOCKED and quantified alternatives, not a fictional success. This is spatial/interface closure, **not** physical hardware certification.

## 2. Source and authority hierarchy

1. Live governing repository executable and governed data authority, including torch T1–T5 and deterministic geometry producers; identify exact paths and commits in PR A.
2. Frozen torch handoff: `WAYFARER_E1_TORCH_PROPULSION_INTEGRATION_GEOMETRY_INTERFACE.md` (user-supplied, 2026-09-17); reconcile to live governing source before using a numerical claim.
3. User-supplied reference GLBs: `WAYFARER_E1_TORCH_STANDALONE.glb`, `wayfarer_with_system_rcs.glb`, `wayfarer_e1_metric_integration_candidate.glb`. PR A must record SHA-256, bytes, coordinate transforms, node identities and authoritative/derivative roles; attachments are **not assumed present in GitHub**. Acquire through approved source workflow and do not fabricate hashes or commit binary files merely by name.
4. Prior Computational Shipyard Phase 9–11 tank/feed findings, PR #176, #182, #184, torch closure PRs, metric closure PR #239, and existing verification/Z3 work: locate and cite exact artifacts in PR A. PR descriptions are discovery leads, not substitutes for executable evidence.
5. This plan is a proposed execution contract; it does not change canon or certify any candidate.

Authority tags required on each component/value: `GOVERNED_VEHICLE_INTERFACE`, `INTERFACE_GEOMETRY`, `CANDIDATE_ENVELOPE`, `DERIVED_WITH_INPUTS`, `UNRESOLVED_ALLOCATION`, `TECHNOLOGY_HOLD`. Never promote a GLB mesh, visualization or research analogue to physical certification.

## 3. Frozen inputs and constraints

- One axial torch; six governed modes ECON–LIMIT; torch/high-metric operation mutually exclusive.
- Governed mass reference: wet 1,158.5 t; dry 858.5 t; normal remass 250 t; protected water 50 t; post-normal-remass 908.5 t. Reconcile any later authoritative revisions rather than silently overriding.
- Required remass flow approximately 1.1361004025–284.025100625 kg/s, 250:1 turndown; exact executable values control.
- Four-tank, four-longeron, four-radiator baseline grammar. Four longerons converge into one aft thrust frame/nozzle; preserve connectivity.
- Torch handoff candidate packaging: shield X 38–43 m, source/frame X 43–50 m, convergence X 48–50 m, nozzle X 50–57 m. These are candidate envelopes, not certified component dimensions. Standalone GLB is immutable for this initiative unless a separately governed change is authorized.
- 57 m main-body length and 9 m diameter are the handoff basis. Report any 57 m/58 m bounds discrepancy by source, node, local/world transform and whether it is hull, marker or external extension; do not rescale or trim silently.
- Working-fluid species, density/storage phase, feed pressure, hardware, transient dynamics, source physics, deposition, physical plume and component lifetime remain open unless earned evidence closes them. Do not invent a plume cone, torch radiator area or tank volume.
- Courier-first, comfort-second: preserve an inspectable courier deployment envelope and quantify remaining contiguous space. The earlier 24 m courier reservation is a **planning sensitivity**, not a frozen station or proven minimum; crew may be compacted but not by sacrificing safety.

## 4. Outputs and file conventions

Plan directory: `engineering/experience_one/drivetrain_spatial_closure/`.

Planned documentation: `BASELINE_AND_AUTHORITY_REGISTER.md`, `REQUIREMENTS_TRACEABILITY.md`, `GEOMETRY_AND_INTERFACE_CONTRACT.md`, `CANDIDATE_TRADE_AND_SELECTION.md`, `SPATIAL_COLLISION_REGISTER.md`, `COMPONENT_HOLDS_REGISTER.md`, `QUALIFICATION_AND_RELEASE_REPORT.md`.

Separate specifications under `specifications/`: `TANK_SYSTEM_SPEC.md`, `REMASS_FEED_SPEC.md`, `CONDITIONING_AND_SERVICES_SPEC.md`, `STRUCTURAL_INSTALLATION_SPEC.md`, `SPATIAL_INTEGRATION_SPEC.md`, `VERIFICATION_AND_RELEASE_SPEC.md`. Each must include authority/status, inputs, interfaces, equations/derivations, geometry, evidence, tests and open holds.

Expected generated products (final paths selected in PR A according to existing build conventions): `WAYFARER_E1_DRIVETRAIN_STANDALONE.glb` and `WAYFARER_E1_DRIVETRAIN_INTEGRATED_CANDIDATE.glb`, plus manifest, numerical verification report and artifact hashes. Geometry is generated from version-controlled typed data/producers; GLBs are derivatives. Avoid a competing compiler or hard-coded field/timeline names; use schemas/adapters.

## 5. Seven bounded implementation PRs

### PR A — Authority and geometry recovery [START HERE]
**Inputs:** live main, relevant prior PR diffs and Shipyard source, three user-supplied GLBs, torch handoff.  
**Tasks:** identify exact executable authority and geometry producers; audit reference GLB bytes/hashes and transformed component bounds; identify tank placeholders, torch and metric/RCS node identity; compare frame, origin, units and 57/58 m extents; identify existing tests and GLB export route; document access to uploaded binaries versus repo.  
**Outputs:** baseline/authority register, machine-readable manifest schema or existing-schema adapter, discrepancy register, reference fixture strategy, targeted baseline tests.  
**Gate:** reproducible geometry/source mapping; every discrepancy classified with disposition; no geometry modification. If reference binaries cannot be acquired in the implementation environment, mark binary comparison BLOCKED rather than claiming it passed.

### PR B — Remass/feed requirements contract [depends A]
**Tasks:** consume torch T1–T5 authoritative mode outputs; encode six-mode flow/turndown, inlet-state interface, inventory/reserve separation, operational exclusions, shutdown/fault and transitions with open dynamics clearly marked. Separate fixed requirements from candidate species/pressure/conditioning.  
**Outputs:** typed requirements and interfaces, traceability, feed specification draft, tests.  
**Gate:** authoritative mode and inventory reproduction; no unsupported fluid or equipment constants.

### PR C — Four-tank architecture [depends B; parallel with D where interface-stable]
**Tasks:** evaluate parameterized tank candidates inside shell/longeron exclusions; explicitly parameterize density, phase, insulation, ullage, wall/mount allowances; define protected-reserve segregation alternatives; calculate full/partial/depleted CoM and inertia with known vs assumed masses distinguished.  
**Outputs:** candidate geometry producer, tank spec, trade matrix and selected *spatial* candidate.  
**Gate:** four-tank topology unless separately approved; 250 t + 50 t reconciliation, fit and mass-property checks. No certified tank volume without earned storage properties.

### PR D — Feed/conditioning/service installation [depends B; converge with C]
**Tasks:** collectors, headers, isolation, trunks, conditioning and instrumentation allocations; typed connection graph to torch interface; service/removal routes; mode, shutdown and fault cases. Unknown machinery represented by explicitly labeled allocation envelopes, not false detail.  
**Outputs:** feed geometry producer, interface graph, feed and conditioning/service specs.  
**Gate:** traceable tank-to-torch connectivity and reserve isolation; no fabricated pressure, response or pump performance.

### PR E — Structural and cross-system spatial integration [depends C+D]
**Tasks:** preserve longeron load path; mounting/load interfaces, access, tank depletion mass migration; interference against hull, torch, RCS, metric nodes, radiators stowed/deployed, docking and launch corridor. Distinguish hard collisions, intended joints, nested envelopes, placeholders, deployment conflicts and unknown plume clearance. Quantify recovered *contiguous usable* space rather than adding overlapping longitudinal lengths.  
**Outputs:** structural/spatial specs, collision and access registers, ship station/volume report, quantified fit alternatives.  
**Gate:** zero unexplained hard clashes, preserved frozen geometry/identity and explicit dispositions for every hold. If shell containment fails, report measured overrun and candidate changes; do not silently stretch ship.

### PR F — Standalone and integrated GLB generation [depends E]
**Tasks:** deterministic source-to-GLB export; separate drivetrain asset; assemble derivative reference ship+RCS+metric+one torch+one drivetrain; preserve source provenance, node identities, transforms and authority metadata; compare world-space mating coordinates and bounds; validate viewer interoperability including Android/browser where feasible.  
**Outputs:** two GLBs, manifests, hashes, repeat-build tests and assembly instructions.  
**Gate:** no hand-alignment, rescale, duplicated tanks/torch or geometry drift; byte-stable or geometry-equivalent deterministic rebuild as documented.

### PR G — Verification, specification and release [depends F]
**Tasks:** reconcile six specs to executable sources; targeted tests during PRs and full applicable end-to-end regression at release; assess inventory, flow, transforms, clashes, structure, mass properties, provenance, export reproducibility and existing torch/RCS/metric suites.  
**Outputs:** qualification report, holds register, installation instructions and release manifest.  
**Gate:** `SPATIAL_CANDIDATE_CLOSED_WITH_COMPONENT_HOLDS` only if evidence supports; otherwise `BLOCKED_WITH_MEASURED_GAPS`. Neither is physical hardware certification.

Dependency DAG: `A → B → (C || D) → E → F → G`. Documentation evolves during each PR; final release in G. Each PR must state source SHA, tests run, numerical results, remaining holds and downstream interfaces.

## 6. Acceptance matrix and non-negotiable tests

1. **Inventory:** 250 t normal remass + 50 t protected reserve; no silent reserve consumption or double count.
2. **Mode/feed:** reproduce all six authoritative mode cards and 250:1 flow turndown.
3. **Torch:** immutable input GLB hash and vehicle interface; exact frame mating; no torch internals redesign.
4. **Identity:** one instance each of torch, four tanks and existing RCS/metric components; no silent rename or duplicate.
5. **Geometry:** finite transforms, source/world bounds, units, station reconciliation, containment or measured overrun, no unexplained hard collision.
6. **Structure:** four-longeron topology and aft-frame connectivity; do not invent FEA safety factors.
7. **Thermal/RCS:** preserve four radiators and RCS hardpoints; explicit stowed/deployed and physical-plume holds.
8. **Mass properties:** full/partial/depleted CoM/inertia with assumption ledger.
9. **Provenance:** every numerical and spatial claim classified and linked to source or derivation.
10. **Rebuild/regression:** deterministic output, tests before substantive code changes, targeted functional tests per PR and full E2E at G.

## 7. Kickoff checklist — PR A executable tasks

- [ ] Record main HEAD and inspect existing workplans/engineering conventions.
- [ ] Read PR #176/#182/#184 and relevant torch/metric closure diffs and Shipyard Phase 9–11 actual files; extract authoritative paths and unresolved decisions.
- [ ] Locate source-of-truth geometry and GLB generation scripts, schemas and tests; map source→GLB.
- [ ] Obtain the three reference GLB bytes in the working environment; SHA-256, file sizes, node paths, transforms and world-space bounding boxes. Record missing access as blocker.
- [ ] Compare torch standalone geometry and integration geometry without changing torch; classify 57/58 m issue.
- [ ] Identify four tank placeholders and whether they duplicate across reference assemblies.
- [ ] Define reference asset manifest and fixture strategy without committing large binaries unnecessarily.
- [ ] Add baseline-only tests first; run and report results.
- [ ] Publish audit with decisions/holds and a precise PR B handoff. **Do not change tank or torch geometry in PR A.**

## 8. Change control and exclusions

No canon, Navigator, campaign state, frozen torch performance, RCS architecture or metric physics mutation. No assumption that 24 m courier reservation is actual available volume. No fake pump/tank material certification, plume, source gain, heat deposition or radiator area. All changes to frozen vehicle interfaces require a separate governed change and explicit review. User-provided reference GLBs are inputs, not automatically committed repository artifacts. This workplan itself may be merged as planning authority only; PR A evidence is still pending.
