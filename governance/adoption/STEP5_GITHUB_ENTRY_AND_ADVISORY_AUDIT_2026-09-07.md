# LOOM 2226 — Governance Adoption Step 5 Audit

**Date:** 7 September 2026  
**Status:** STEP 5 COMPLETE — PR CONTRACT / ISSUE FORMS / INITIAL WALTER ADVISORY WORKFLOW  
**Branch:** `governance/repository-control-baseline-v1`  
**PR:** #24

## Purpose

Make governance part of the normal repository entry path without yet imposing blocking controls on active development.

Step 5 adds structured pull-request/issue contracts and the first live, read-only WALTER GitHub Actions check.

## Files added

### Pull-request contract

- `.github/PULL_REQUEST_TEMPLATE.md`

The PR contract requires a primary change class, work item/workstream, mutation scope, explicit non-scope, authority/canon impact, dependency invalidation, runtime/data/schema impact, asset/3D impact, frozen-state impact, test/qualification class, vendor/AI/black-box assurance, recovery/rollback and #LOOMSAFE acknowledgement.

### Issue forms

- `.github/ISSUE_TEMPLATE/config.yml`
- `.github/ISSUE_TEMPLATE/work_item.yml`
- `.github/ISSUE_TEMPLATE/experiment.yml`
- `.github/ISSUE_TEMPLATE/canon_change.yml`
- `.github/ISSUE_TEMPLATE/defect.yml`
- `.github/ISSUE_TEMPLATE/governance.yml`
- `.github/ISSUE_TEMPLATE/assurance_finding.yml`
- `.github/ISSUE_TEMPLATE/exception.yml`

These provide explicit entry paths for ordinary work, scientific/preregistered experiments, Canon Change Requests, defects/inconsistencies, governance changes, WALTER assurance findings and formal governance exceptions.

Blank issues are disabled so substantive work begins from a structured record rather than a memory-only/chat-only instruction.

## Initial WALTER workflow

Added:

- `.github/workflows/loom-governance-advisory.yml`

Trigger:

- pull request opened;
- reopened;
- synchronized/updated;
- edited;
- marked ready for review.

Permissions are read-only:

- `contents: read`
- `pull-requests: read`

The workflow currently checks advisory signals including:

- missing recognizable LOOM change class;
- `canon/current/**` change without `class:canon`;
- canon change without detected CCR language;
- PR #19 branch moving from its frozen SHA;
- PR #16 preregistered branch moving from its recorded SHA;
- deploy/release changes without recovery/compatibility language;
- SQLite/schema-like changes without migration/compatibility/recovery language;
- canon mixed with engineering/geometry in one PR;
- dependency-definition change without vendor/dependency assurance language;
- research and current canon changed together.

### Enforcement state

**ADVISORY ONLY.**

The workflow always exits `0` and cannot block a merge in Step 5.

This is deliberate. Historical validation and false-positive review must occur before any check earns HOLD/BLOCK authority.

## Live acceptance runs

The workflow executed repeatedly on PR #24 during Step 5.

Observed results:

1. The first job completed successfully and the inspection script ran.
2. It emitted the expected advisory warning that PR #24 did not yet contain a recognizable primary change-class token because PR #24 predated the new PR contract.
3. No canon/freeze/data/release authority violation was reported.
4. The initial YAML job name `WALTER / #LOOMSAFE advisory` was parsed as `WALTER /` because the unquoted `#` started a YAML comment. The job still ran correctly. This presentation bug was fixed by quoting the job name.
5. The initial run used `actions/checkout@v4`, which emitted GitHub's Node-20 deprecation warning. The workflow was updated to `actions/checkout@v5`.
6. A subsequent run confirmed the full job name `WALTER / #LOOMSAFE advisory` and `actions/checkout@v5` executed successfully.
7. PR #24 was then updated to declare `class:governance`. The edited-body run completed successfully with **zero advisory warnings**.

This is a useful proof of the advisory-first model: even governance itself gets tested by the real platform before it earns enforcement authority.

## WALTER evolution in Step 5

The assurance architecture now has structured historical record types:

- `WAF` — WALTER Assurance Finding;
- `GEX` — Governance Exception.

A WAF distinguishes deterministic, missing-evidence, LLM-assisted and human-review bases. LLM-assisted findings remain advisory unless a separate deterministic rule establishes authority.

A GEX is additive: it may authorize an allowed future exception but cannot rewrite the original finding, failed test, frozen SHA, provenance or release history.

## Deliberate omissions

Step 5 does **not** add CODEOWNERS approval requirements or second-human approval requirements. Kevin is currently the sole human project-intent authority; mandatory self-review would create governance theater rather than independent assurance.

Step 5 does **not** make the WALTER workflow a required status check.

Step 5 does **not** enable branch protection/rulesets.

Those belong later, after advisory validation.

## Stability result

No gameplay, Navigator/GIS/HUD, runtime behavior, SQLite bytes/schema, media assets, launcher/updater semantics, Wayfarer geometry/3D, canon content or scientific experiment source was intentionally modified by Step 5.

## Acceptance result

**PASS.** Structured repository entry contracts exist, the first autonomous WALTER advisory workflow executed successfully, its platform issues were corrected, and the final governed PR-body run completed with zero advisory findings.

## Next permitted action

**Step 6 only:** encode the machine-readable dependency graph and compatibility model for canon, engineering, runtime/data, Navigator/GIS, media, Wayfarer 3D, Pixel/Windows deployment and release artifacts.
