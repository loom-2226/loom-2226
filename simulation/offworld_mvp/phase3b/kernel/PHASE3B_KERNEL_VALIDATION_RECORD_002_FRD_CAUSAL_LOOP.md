# Phase 3B Kernel Validation Record 002 — FRD Causal Loop

**Status:** PASS FOR BUILD-2 AUTHORIZED DETERMINISTIC SLICE / PRE-CONTRACT / SINGLE-AUTHORITY
**Date:** 2026-10-04
**Branch:** `offworld-mvp-phase3`

## Purpose

Extend Kernel Slice 1 from accounting mechanics into the FRD causal architecture without crossing the gate into autonomous agent-engine implementation.

The build adds persistent MVP agent/world state and deterministic scripted action drivers for:

- public institutional agent;
- private sponsor/operator;
- private financier;
- emergent local/offworld financier;
- hidden scenario resource state;
- observations and agent-specific information/beliefs;
- financing request/decision;
- development and fixed-capital formation;
- extraction and resource depletion;
- explicit EARTH_MARKET sale counterparty;
- local retained proceeds and local reinvestment;
- population migration and colony state;
- causal events and deterministic replay.

EARTH_MARKET and ColonyState are deliberately not intelligent agents.

## Test execution

Executed on `quantifactus` from a fresh Git archive of `origin/offworld-mvp-phase3`.

`python3 -m unittest discover -s tests -v`

**10 tests executed; 10 passed.**

The original five accounting/kernel tests remain green. Five Build-2 tests additionally pass:

1. SPARSE full causal loop;
2. NULL blocks development;
3. pre-observation action identity across NULL/SPARSE/RICH;
4. deterministic replay;
5. epistemic separation.

## Scenario results

| Universe | First observation | Development | Remaining resource | Offworld population | Productive capital | Realized FCF |
|---|---|---|---:|---:|---:|---|
| NULL | NEGATIVE | rejected | 0 | 0 | 0 | none |
| SPARSE | POSITIVE | approved | 15 | 10 | 100 | 60 Earth-supplied + 40 local |
| RICH | POSITIVE | approved | 95 | 10 | 100 | 60 Earth-supplied + 40 local |

The SPARSE and RICH runs remain behaviorally identical after the coarse positive observation because the observation does not distinguish their quantities. Their hidden remaining resource differs because extraction acts on fixed scenario truth. This is intentional and demonstrates that hidden quantity does not directly drive agent decisions.

Run fingerprints:

- NULL: `02337f823ede860a2c43b82834316f2af7b699d113d4eec1aade8b0f17f02439`
- SPARSE: `9c17878cf80e96a697891706c97aa28299e890b01f1e0693fdb52d358c07eeb7`
- RICH: `eae29de39013b8556d8c7ac922daccbe368e678de01caed28ee7bd7af799371d`

## Causal trace now exercised

`PublicAgent -> Observation(public) -> Sponsor information/belief -> FinancingRequest -> PrivateFinancier -> FinancingDecision -> Commitment -> Disbursement -> Earth-supplied development expenditure -> offworld FCF -> productive asset -> PublicAgent migration -> Sponsor extraction -> resource depletion -> EARTH_MARKET sale -> realized proceeds -> local retained funds -> LocalFinancier -> local project financing -> local expenditure -> local FCF -> offworld infrastructure`

This is a deterministic validation loop, not a forecast and not autonomous behavior.

## FRD trace status

The build now has executable state paths for the six Phase-3 FRD trace subjects:

- money: financier -> project -> supplier and market -> operator -> local financier -> project;
- person: Earth -> offworld migration with system total conserved;
- resource: hidden initialized stock -> realized extraction -> remaining stock/inventory -> sale;
- observation: WORLD_SIM result -> observation object -> permitted agent information;
- belief: agent-local prior -> observation-conditioned agent-local update;
- action: scripted decision/request -> kernel transition -> causal event/state change.

## Known incompleteness

This is not yet the entire FRD MVP and does not close Phase 3B.

The Build-2 fixture deliberately still abstracts or omits:

- explicit exploration expenditure/accounting;
- remote versus surface observation fidelity beyond channel identity;
- transport cost/time/energy/risk/capacity effects;
- technology gating;
- accessible/recoverable/reserve dynamics beyond initialized hierarchy;
- explicit project failure/write-off paths;
- colony operating needs, imports and subsidy mechanics;
- births/deaths;
- endogenous price/demand;
- autonomous underwriting/operating policies;
- full causal snapshots of prior/new state;
- governed Earth-reference data ingestion.

These remain subsequent authorized kernel/fixture work. Full agent-engine implementation remains gated.

## Interpretation

The architecture now demonstrates that investment is given by an explicit financier to an explicit project operated by an explicit sponsor, and that realized proceeds can create an explicit local financier which funds subsequent local capital formation. The loop no longer depends on direct fixture calls from surplus to capital formation.

The agent decision policies are still scripted validation rules. That is intentional: the state and causal interfaces are being tested before autonomous decision logic is authorized.
