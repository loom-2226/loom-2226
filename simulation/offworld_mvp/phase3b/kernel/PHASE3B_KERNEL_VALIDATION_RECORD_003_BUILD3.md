# Phase 3B Kernel Validation Record 003 — Exploration, Stock Binding, Failure and Disposition

**Status:** PASS FOR BUILD-3 AUTHORIZED DETERMINISTIC SLICE / PRE-CONTRACT / SINGLE-AUTHORITY
**Date:** 2026-10-04
**Branch:** `offworld-mvp-phase3`

## Purpose

Close the most consequential falsification gaps identified after Build 2 without crossing into autonomous agent-engine implementation.

Build 3 adds:

1. paid exploration;
2. EXPLORATION_WIP -> KNOWLEDGE_ASSET or WRITE_OFF resolution;
3. keyed deterministic noisy observations;
4. a deterministic NULL false-positive path;
5. stock-binding extraction;
6. matched Earth-market resource inventory;
7. an explicit ENCLAVE versus SETTLEMENT surplus-disposition choice;
8. a synthetic Earth-reference FCF resource-allocation ceiling with reservation;
9. run fingerprint identity including universe/version, input-snapshot identity, code-contract identity and explicit Build-3 parameters.

## Validation

Executed on `quantifactus` from a fresh Git archive of `origin/offworld-mvp-phase3`.

`python3 -m unittest discover -s tests -v`

**17 tests executed; 17 passed.**

Seven Build-3 tests pass in addition to the ten earlier tests:

- paid exploration and knowledge-asset resolution;
- stock-binding extraction;
- keyed false positive and write-off;
- matched market resource inventory;
- disposition can reject local reinvestment;
- Earth-reference proxy ceiling;
- fingerprint run-identity/parameter sensitivity and deterministic replay.

## Key falsification cases

### Paid exploration

The public agent's exploration no longer creates information for free.

The deterministic fixture:

`public funds -> exploration project cash -> Earth supplier expenditure -> EXPLORATION_WIP -> observation -> KNOWLEDGE_ASSET or WRITE_OFF`

The 10-unit exploration expenditure is also reserved against and consumed from the synthetic Earth FCF resource-allocation proxy. It contributes to the explicit Earth-impact displacement ledger under the current `lambda=1` MVP abstraction.

### Stock binding

A fixture plants **2 resource units** and requests extraction of **5**.

Result:

- requested: 5;
- extracted: 2;
- remaining hidden stock: 0;
- realized offworld inventory added: 2.

The transition therefore binds realized output to remaining recoverable stock rather than allowing the scripted request to manufacture material.

### Keyed false positive and write-off

The NULL false-positive fixture uses:

- universe id: `NULL_FP_1`;
- universe version: `v1`;
- false-positive rate: 0.20;
- keyed draw: `0.1138276042139907156982951697`.

The remote observation is therefore POSITIVE despite zero hidden resource.

The scripted financier approves development **because the fixture policy consumes the positive observation**. Development capital is formed. Subsequent extraction yields zero. Resolution writes off the exploration WIP/knowledge path and removes the failed productive development asset.

This is a deterministic failure-path test, not a calibrated sensor-error model.

### Matched Earth-market resource inventory

A sale of 5 resource units now causes:

- offworld inventory -5;
- Earth market resource inventory +5;
- Earth market monetary account -100;
- seller monetary account +100.

The market remains an MVP abstraction/non-agent, but the commodity no longer disappears on sale.

### Disposition

The same 80-unit surplus can now be sent through two explicit deterministic disposition rules:

- ENCLAVE -> 80 returned to Earth, 0 retained locally;
- SETTLEMENT -> 0 returned in this fixture, 80 transferred to local reinvestment funds.

This proves the state/transition layer can say **no** to local reinvestment. It does not yet prove an autonomous agent can choose between those modes.

### Synthetic Earth-reference allocation ceiling

Build 3 creates a synthetic reference FCF value of 1000 and authored allocation fraction 0.10, yielding a 100-unit ceiling. Reservation of 100 succeeds; an additional 0.01 is rejected.

This validates reservation/deferral mechanics only. It is **not governed Earth-reference ingestion**, and reference FCF is not treated as cash or empirical supplier capacity.

## Fingerprint

Build-3 fingerprint now composes the prior state fingerprint with:

- universe id;
- universe version;
- input snapshot id;
- code-contract identity;
- explicit Build-3 parameter tuple;
- matched market resource inventories;
- Earth resource-constraint state including reference value, allocation fraction, reserved and spent amounts;
- exploration-resolution state.

Changing universe identity changes the fingerprint; replaying the same Build-3 initial state produces the same fingerprint.

This is materially stronger than the Build-2 fingerprint but is still not a final qualification/replay manifest.

## Epistemic claim boundary

Build 3 does **not** claim autonomous-policy epistemic isolation.

What is established is narrower:

- hidden resource state is distinct from observation objects;
- observations can disagree with hidden truth;
- agent information/belief state receives observation content rather than a hidden quantity field;
- scripted downstream financing can therefore be made to fail because the observation was wrong.

When autonomous policies are authorized, hidden-state access must be retested at the policy/API boundary.

## Still open

Build 3 does not yet establish:

- calibrated observation error distributions;
- surface-versus-remote sensor physics;
- depreciation above zero;
- multi-year WIP construction;
- transport cost/time/energy/risk/capacity effects;
- technology gating;
- dynamic accessibility/recoverability/reserve conversion;
- colony operating needs/imports/subsidies;
- births/deaths;
- endogenous price/demand;
- autonomous underwriting, exploration, operating or disposition policies;
- governed Earth-reference ingestion;
- complete code/data artifact hashes in a qualification-grade replay manifest.

Full agent-engine implementation remains gated.
