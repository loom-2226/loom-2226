# Phase 3B Methodology Research Basis — 2026-10-04

**Status:** EXTERNAL_RESEARCH_SYNTHESIS / PRE-CONTRACT / NON-QUALIFICATION
**Purpose:** Preserve the research basis for the methodology-hardening pass after Build 4.

This file records why the Offworld MVP adopted the methodology changes implemented after the frozen Build 4 baseline. The cited literature informs design; it does not create LOOM authority or validate LOOM outputs.

## 1. ODD and executable model documentation

Grimm et al. (2020), *The ODD protocol for describing agent-based and other simulation models: A second update to improve clarity, replication, and structural realism*, Journal of Artificial Societies and Social Simulation, DOI: 10.18564/JASSS.4259.

Design consequence for LOOM:

- add an ODD-aligned executable specification;
- explicitly document entities/state/scales, process overview and scheduling, initialization, input data and submodels;
- tie documentation closely to actual executable names/interfaces;
- separate model description from claims of validity.

Implemented in:

- `OFFWORLD_MVP_ODD_ALIGNED_SPEC_0_1.md`.

## 2. Multi-level / multi-resolution modeling

Brugière, Nguyen-Ngoc and Drogoul (2022), *Handling multiple levels in agent-based models of complex socio-environmental systems: A comprehensive review*, Frontiers in Applied Mathematics and Statistics 8:1020353, DOI: 10.3389/fams.2022.1020353.

Pierzchała and Czuba (2019), *Machine Learning-Based Open Framework for Multiresolution Multiagent Simulation*, DOI: 10.1007/978-3-030-43890-6_17.

Design consequence for LOOM:

- do not force every modeled process into one microscopic level;
- make levels/resolution explicit;
- treat aggregation/disaggregation as a state transformation requiring consistency;
- make time scales and cross-level couplings explicit rather than hidden in object structure.

Implemented in:

- SYSTEM / AGGREGATE / AGENT / ENTITY_ASSET classification;
- explicit AGGREGATE -> AGENT reconciliation fixture;
- scheduler/coupling contract.

## 3. Verification and validation

Klügl (2008), *A validation methodology for agent-based simulations*, ACM Symposium on Applied Computing, DOI: 10.1145/1363686.1363696.

Fagiolo, Guerini, Lamperti, Moneta and Roventini (2019), *Validation of agent-based models in economics and finance*, DOI: 10.1007/978-3-319-70766-2_31.

Design consequence for LOOM:

- distinguish verification, calibration, sensitivity analysis and empirical validation;
- passing software/invariant tests is not empirical model validation;
- track validation standing by subsystem and purpose;
- disclose calibration-target reuse and parameter-space exploration.

Implemented in:

- `PHASE3B_VERIFICATION_VALIDATION_UNCERTAINTY_PROTOCOL_0_1.md`;
- executable `ValidationManifest` firewall.

## 4. TRACE-like model evaluation record

Johnston et al. (2018), *Towards better modelling and decision support: Documenting model development, testing, and analysis using TRACE*, DOI: 10.25334/q4d71v.

Design consequence for LOOM:

- retain development rationale, testing, limitations and evaluation records alongside the executable model;
- do not use the ODD description as a substitute for validation evidence.

LOOM's existing design/validation records already perform much of this function; the methodology pass makes the distinction explicit.

## 5. Stock-flow/accounting consistency

Caiani et al., *Agent Based-Stock Flow Consistent Macroeconomics: Towards a Benchmark Model*, DOI: 10.2139/SSRN.2664125.

Reissl, Fierro, Lamperti and Roventini, *The DSK-SFC stock-flow consistent agent-based integrated assessment model*, SSRN DOI: 10.2139/ssrn.4766122 and later research versions.

Design consequence for LOOM:

- preserve explicit stocks, flows, counterparties and balance-sheet/ownership identities;
- do not mistake a reference investment flow for liquid financing;
- state clearly that the current MVP accounting boundary is not a complete macrofinancial system.

Implemented in:

- financing/recursive-FCF architecture;
- Build 4 accounting hard cases;
- `PHASE3B_MVP_ACCOUNTING_BOUNDARY_CANDIDATE_0_1.md`.

## 6. Deep uncertainty and long horizons

Marchau, Walker, Bloemen and Popper, eds. (2019), *Decision Making under Deep Uncertainty: From Theory to Practice*, Springer, DOI: 10.1007/978-3-030-05252-2.

Design consequence for LOOM:

- a 2026–2226 run is initially a conditional scenario trajectory, not a privileged point forecast;
- evaluate ensembles across scenario, parameter, uncertainty and stochastic axes;
- seek robustness, divergence drivers and thresholds;
- do not assign probabilities to scenarios merely because they are sampled.

Implemented in:

- deterministic `EnsembleHarness`;
- FRD long-horizon uncertainty requirements;
- validation status defaults to NOT_EMPIRICALLY_VALIDATED.

## 7. LOOM position after the pass

The research supports the architecture direction already taken: hybrid mechanism + aggregate + explicit institutional-agent modeling is defensible and often preferable to universal microscopic autonomy.

The research does **not** establish that LOOM's behavioral models are valid. The current strength is verification, accounting, information separation, lineage and reproducibility infrastructure. Empirical calibration/validation remains future work.
