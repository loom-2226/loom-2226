# LOOM 2226 — Governance Adoption Step 11 Audit

**Date:** 7 September 2026  
**Status:** STEP 11 IMPLEMENTATION PREPARED — OWNER ADMIN ACTIVATION PENDING  
**Target:** `main` only  
**Protection contract:** `governance/current/LOOM_MAIN_PROTECTION_POLICY.yml`

## Purpose

Apply the minimum repository protection necessary to make `main` a controlled promotion boundary without constraining frozen research, long-lived workstreams, planning branches, release branches or local development unnecessarily.

## Pre-activation observations

- Governance Baseline v1.0 is authoritative on `main` at merge commit `605b8cd3ea00c94ac78437b90f5e85fd841a085b`.
- Repository rulesets observed through the connected GitHub integration: none.
- `main` was observed unprotected immediately after Step 10.
- The connected GitHub App can mutate repository content/PRs but does **not** have repository administration permission for branch-protection writes; the branch-protection endpoint returns `403 Resource not accessible by integration`.

This is a connector permission boundary, not a governance failure. Step 11 cannot be declared complete until the owner activates the policy through GitHub administration and the resulting state is verified.

## Approved Step-11 protection contract

Protect **only** `main`.

Required:

- changes enter `main` through a pull request;
- status context `loom-gate` is required;
- PR conversations must be resolved before merge;
- force pushes are disabled;
- deletion of `main` is disabled.

Intentionally **not** required:

- second-human approval;
- CODEOWNERS approval;
- signed commits;
- branch-up-to-date requirement;
- linear-history requirement;
- successful deployments;
- protection on research/planning/feature/integration/release/workstream/archive branches.

This preserves the frozen-science model: a long-lived or preregistered branch is never forced to absorb new `main` merely to satisfy repository administration aesthetics.

## `loom-gate` enforcement decision

Kevin's explicit `go step 11` authorizes activation of the ten Step-9 historically validated deterministic hard-rule families when the protection boundary is activated.

The eight Step-9 advisory/rework rules remain nonblocking.

No LLM judgment participates in a hard gate.

## Owner activation checklist

In GitHub repository settings, create/enable a rule targeting branch `main` with the semantics in `LOOM_MAIN_PROTECTION_POLICY.yml`:

1. require pull requests before merge;
2. required status check: `loom-gate`;
3. require conversation resolution;
4. block force pushes;
5. block branch deletion;
6. required approvals: **0** / do not require a second reviewer;
7. do not require CODEOWNERS approval;
8. do not require signed commits;
9. do not require branches to be up to date before merge;
10. do not target any non-`main` branch.

The exact GitHub UI may expose these semantics through a repository ruleset or classic branch protection depending on account/repository configuration. The semantics above are authoritative; UI wording is not.

## Verification gate

After owner activation, Step 11 is complete only if repository state confirms:

- `main` is protected or an active ruleset targets `main`;
- PR-before-merge is active;
- `loom-gate` is required;
- conversation resolution is active;
- force push and deletion are disabled;
- no second-human approval requirement was accidentally enabled;
- no up-to-date/rebase requirement was accidentally enabled;
- no non-main workstream received Step-11 protection.

## Functional impact

None.

This step changes governance/control-plane settings only. It does not modify canon content, Navigator/GIS, production runtime, SQLite bytes/schema, media, launchers, Wayfarer 3D or frozen scientific source.

## Current disposition

**PENDING OWNER ADMIN ACTIVATION.**

Development and physics execution remain paused. Steps 12–14 do not begin until Step 11 activation is verified.
