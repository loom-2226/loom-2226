# LOOM 2226 — Governance Adoption Step 11 Audit

**Date:** 7 September 2026  
**Status:** STEP 11 COMPLETE — MAIN PROTECTION ACTIVE AND VERIFIED  
**Target:** `main` only  
**Protection contract:** `governance/current/LOOM_MAIN_PROTECTION_POLICY.yml`  
**Ruleset:** `LOOM main protection v1` (`22419925`)

## Purpose

Apply the minimum repository protection necessary to make `main` a controlled promotion boundary without constraining frozen research, long-lived workstreams, planning branches, release branches or local development unnecessarily.

## Activation history

After Governance Baseline v1.0 became authoritative on `main`, the connected GitHub App was unable to write repository administration/branch-protection settings. Kevin therefore activated the approved ruleset manually through GitHub administration.

The resulting repository ruleset was then read back through GitHub and verified against the machine policy.

## Verified active contract

GitHub reports an **active** branch ruleset named `LOOM main protection v1` targeting exactly:

`refs/heads/main`

Verified rules:

- branch deletion restricted;
- non-fast-forward / force-push blocked;
- pull request required before merge;
- required approving reviews = **0**;
- no CODEOWNERS review requirement;
- no last-push approval requirement;
- conversation resolution required;
- no additional unattributed-Copilot approval requirement;
- allowed merge methods: merge, squash, rebase;
- required status check: `loom-gate`;
- strict/up-to-date status-check policy = **false**;
- no bypass actors;
- current user cannot bypass the ruleset.

## Governance result

**PASS.** The active GitHub repository state matches `LOOM_MAIN_PROTECTION_POLICY.yml`.

No second-human approval, signed-commit, linear-history, deployment, or branch-up-to-date requirement was accidentally introduced.

No non-`main` branch is targeted by this Step-11 ruleset.

## `loom-gate`

The deterministic gate is already in `ENFORCE` mode for the ten Step-9 historically validated hard-rule families.

The eight Step-9 advisory/rework rules remain WATCH-only.

No LLM judgment participates in a hard result.

## Functional impact

None.

No canon content, Navigator/GIS behavior, production runtime, SQLite bytes/schema, media, launchers, Wayfarer 3D, PR #19 experiment source, or PR #16 preregistration changed in Step 11.

## Disposition

**STEP 11 CLOSED.**

The next permitted adoption action is:

**Step 12 — governance sync/review of preserved active workstreams.**

Development and physics execution remain paused until Step 14.
