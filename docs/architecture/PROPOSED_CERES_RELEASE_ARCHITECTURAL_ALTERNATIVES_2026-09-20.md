# Ceres release architecture — proposed alternatives and feasibility checks

Date: 2026-09-20  
Class: engineering (proposal only)  
Authority: NON-GOVERNING / NON-RELEASE / NO IMPLEMENTATION APPROVAL  
Source: Kevin's discussion with Claude and Sol, Claude's `LOOM_ARCHITECTURE_v2.md` dated 2026-09-20, subsequent hostile review and Claude response. This synthesis is not a verbatim copy of Claude's full proposal. Retain that external review as source material outside this document.  
Scope: propose Ceres development, CI, container provenance, rehearsal, release, rollback, recovery. No canon, data, runtime, `.github`, permissions, production, Tailscale or PR-state mutation. No new governance authority. Existing governing GitHub documents outrank this proposal.

## Decision state

**No architecture selected; no production release authorized.** Preserve distinct alternatives and test their differentiating claims. No automatic deployment, merge, public ingress, Sydney access, infrastructure provisioning or relaxation of PR #257's freeze is implied. PR #258 is an implementation candidate, not an approved release. Production authorization remains separate and must identify the exact artifact, target and scope.

## Current blockers and evidence boundary

- PR #258: `https://github.com/loom-2226/loom-2226/pull/258`; observed open/unmerged, head `520af8926fddf5bcfd32f8937dfe92b37d55b33e`. Its description reports a dry-run-first digest-pinned Sydney release tool, real-container-preserving rollback logic, and local test results. Those self-reported results are not equivalent to independent Docker qualification.
- Historical LOOM Gate run `35467604951` was reported successful against the implementation commit; it is **not** Phase 3 functional CI or production qualification. The separate Phase 3 workflow was added to PR #258's base branch, with commits `b308b96cbeead611d4f5a88fb556e2ff921ca5f9` and `b3491ed956b3c35c74decd40f32b8f0754d1ce30`; a Phase 3 run was not observed in previous checks. Recheck live runs before claiming status.
- The workflow compares `git diff --name-only EXPECTED_BASE EXPECTED_HEAD` despite the workflow being added only to the advanced base; it could flag its own base-only `.github` file as a forbidden deletion. A merge-base diff should be reviewed before interpreting a failure. This is a finding, **not authorization to change the workflow**.
- Historical GHCR package API 403 and attestation 404 remain unresolved. These alone do not prove that private-repository plan limitations caused the failure. Actual repository visibility checked via the GitHub connection on 2026-09-20: **PUBLIC** (`get_repo`, `loom-2226/loom-2226`). Correct the earlier hypothetical claim that LOOM itself is private. Plan, token permissions, the historical image's attestation and registry access remain unverified.
- Real Docker replacement, forced failure, exact-object rollback, Sydney access, and production release remain unqualified / not undertaken in this review.

## Shared principles, not yet enforced everywhere

GitHub is authoritative for source and approvals; the Pixel is a control surface; AI can prepare changes but has no standing production authority; build one immutable image and deploy the identical digest; application releases do not change WORLD/CIVSTATE/MEDIA; no production secrets in untrusted PR execution; no public Ceres ingress, Funnel, or new open ports; dry-run and failure-closed qualification precede separately approved live deployment; record evidence by exact source SHA, workflow revision, digest and run. Existing LOOM governance and `loom-gate` remain authoritative; proposed `scope-guard`/`settings-check` additions are **options**, not present controls or approvals.

## Alternative A — Pixel + Codex Cloud + GitHub-native execution (Claude v2)

Pixel directs Codex Cloud and reviews GitHub PRs; routine work is branch-based; GitHub Actions runs CI, builds one image, stores it in GHCR, rehearses replace/rollback in disposable Docker; a separate human-initiated release workflow invokes a narrowly scoped fixed command on Sydney over a private route; Sydney verifies preflight, deploys and rolls back. No permanent development VM. A PC/WSL or on-demand VM is introduced only when measured requirements exceed Cloud + hosted runners.

Strengths: fewer standing machines; routine automated tests and versioned builds; low Pixel burden; smaller custom release surface. Open questions: GitHub Actions trigger semantics and permissions, Codex GitHub capabilities, GHCR credentials, exact provenance model, reproducibility of hosted runner versus Sydney Docker/network/mount setup, suitable private release transport and scoped caller identity, resource limits and interactive debugging. Claude's proposed branch protection, CODEOWNERS, token privileges, environment restrictions and Tailscale ACLs are **design requirements, not verified configuration**.

## Alternative B — Dedicated separate Linux development VM + local Codex + Docker (Sol's original)

Use a dedicated non-production Linux VM with Git worktrees, local Codex, Python and real Docker; Pixel remotes into it. GitHub remains canonical source and CI; a container registry holds pinned images; production promotion crosses an independently authenticated approval/release boundary. Keep Sydney distinct from the development VM; never give unrestricted Codex a production Docker socket or administrative SSH.

Strengths: interactive reproducibility, Docker debugging, native filesystem, large or iterative test suites, representative failure injection. Costs: additional machine management, patching, spend and drift; a VM alone cannot fix GitHub provenance, release authorization or exact rollback. Do **not** assume a VM is necessary until capability tests show hosted execution fails a concrete requirement.

## Alternative C — On-demand hybrid (preserve option)

Use Alternative A for routine tasks and CI. Provision an isolated on-demand VM or PC/WSL only when hosted runners cannot perform an identified test, exceed measured CPU/RAM/time constraints, require hands-on Docker investigation, or need interactive real-data qualification. Capture failures after the rehearsal before deciding. This combines Claude's default cost discipline with Sol's stronger debugging option without committing to permanent infrastructure.

## Deployment mechanism choices (orthogonal to A/B/C)

1. Existing Sydney host + constrained fixed `loom-release` command through the existing private route: preferred candidate to *test*, not selected or authorized. A forced SSH command and narrowly scoped Tailscale ACL might work, but test identity/credential boundaries, no shell escape, digest scope and negative permissions. Tailscale Serve remains private; Funnel forbidden.
2. AWS Systems Manager: investigate eligibility and operational overhead for the specific Lightsail host; **not presumed native**. Do not enroll, grant IAM or open access during a read-only probe.
3. Docker Compose: possible declarative host configuration, but Compose's recreation and functional rollback are NOT proof of exact original-container-object restoration. Preserve PR #258's old-ID/rename/stop/restart approach until user explicitly changes the rollback requirement; require full config, mount, network, port, data identities and health checks.
4. Amazon ECR vs GHCR: GHCR initially; ECR only if actual access or policy problems justify IAM/OIDC complexity. Registry choice does not substitute for an approved release identity.
5. ECS/Fargate, Lightsail container service, Kamal, Portainer: evaluation options, not approved migrations. ECS changes host/network/data mechanics and rollback semantics; Kamal's proxy may conflict with loopback + Tailscale Serve; Portainer is a UI rather than a provenance/release authority. Avoid adopting any until requirements warrant it.

## Open design contracts requiring explicit choice

**Provenance:** When native GitHub attestations work for the actual repo and plan, verify subject digest, source commit, workflow identity and run. Record-based provenance is a weaker fallback: trusted CI emits a digest manifest bound to the successful build run and immutable commit, and release verifies manifest and registry digest without silently calling this a cryptographic attestation. Cosign or another signed mechanism is a future option. A successful job or text note alone cannot prove registry image identity.

**Approval:** a human-triggered `workflow_dispatch` with digest input, typed digest prefix and triggering identity is a candidate control, not complete authorization by itself. Enforce trusted workflow source/ref, permitted actor, immutable digest, eligible build/rehearsal, target and one-use or narrowly scoped release authorization that Sydney can authenticate independently. GitHub plan-specific protected-environment reviewer behavior must be checked; a button click alone is not a protected approval gate.

**Rollback:** exact original container ID must survive staging and be restarted on failure with its original configuration/mounts/ports/network and unchanged database identities, followed by health checks; failure to restore is distinct `FAILED_ROLLBACK` with preserved evidence. This is not a zero-downtime promise. Changing to functional digest-only rollback requires a separate explicit decision.

**Data:** WORLD, CIVSTATE and MEDIA are separate read-only runtime assets. App release checks schema compatibility and representative queries; an authoritative coherent *triple* of databases must be established by LOOM's existing data-authority process, not inferred from three independent hashes. Backups and WAL-safe restoration qualify separately; no live-database copies for CI.

## Evidence-driven acceptance sequence (shared five steps)

| Stage | Test and required evidence | Stop condition |
|---|---|---|
| 0. Read-only capability probe | GitHub repo visibility/plan; actual main ruleset, Actions configuration, Codex permissions, GHCR credential type and testable read-only package access; Sydney Docker version, DB journal modes, RAM/disk, Tailscale features **only when separately authorized Sydney read access exists**. Record unknown rather than invent. | No mutation or secret exposure. |
| 1. Exact-SHA CI | Pin head SHA and workflow SHA; confirm actual run and logs, merge-base PR file list, test results. Avoid PR close/reopen or workflow changes without explicit scope. | Unobserved/skipped/incorrect SHA is NOT PASS. |
| 2. Build and identify image | Single build, resulting digest and source SHA; attestation verify or qualified trusted-run manifest + registry digest check; demonstrate release runner can read image. | 403/404 or digest ambiguity fails closed. |
| 3. Disposable Docker rehearsal | Representative config; old ID/config captured; success update; deliberately bad candidate; exact ID and configuration restored and healthy, DB hashes unchanged; record inability of Codex/Actions to perform tasks. | Failure stops promotion; need for on-demand VM established by measured evidence only. |
| 4. Separately authorized release | Confirm actor/digest/target authorization, private route, preflight, data compatibility, backup/recovery, health and rollback evidence, release record. | No Sydney operation or production promotion based solely on this proposal. |

Backups, cross-database coherent recovery and public-ingress architecture are separate approval/qualification lanes; don't conflate them with code-deploy success. Do not invent cost estimates or plan features: verify current account entitlements before design selection.

## Read-only capability checks performed while drafting (2026-09-20)

- `get_repo`: `loom-2226/loom-2226`, default branch `main`, **visibility PUBLIC**, current account reports push/admin access. This falsifies the premise that the observed attestation 404 must be caused by a *private* LOOM repository.
- `branches/main`: head `391b1f0a8cf9846ef2fbbad64b5ead0547c2a3c5`, protected true; branch protection endpoint's compact legacy field is not a substitute for actual ruleset inspection.
- `rulesets/22419925`: enforcement active, applies to `main`; requires a PR, resolved review threads and `loom-gate`; zero approvals mandated; no bypass actors; non-fast-forward and deletion prohibited. No `scope-guard`, code-owner approval or separate Phase 3 context appears as a required main check in that ruleset. Do not infer all repository Actions/app settings from this one read.
- PR #258 metadata: open, unmerged, head `520af8926fddf5bcfd32f8937dfe92b37d55b33e`; PR metadata's `base_sha` returned `d639cc39c364d9f2e624bc83aacb4a8d22c49d8c` despite previously verified workflow commits on the named base branch. Independently re-read base branch ref before taking action; connector snapshot may be stale.
- Outstanding: plan/account entitlements, app permissions, GHCR private credentials and attestation existence, Sydney Docker/journal/Tailscale. No actual Docker/host functional test executed. The two concrete read-only checks of repo visibility and ruleset **passed as information gathering**, not release qualification.

## Non-scope, review and disposition

This document is an architectural alternatives record only; no new governance policy, current `main` promotion, merged PR, workflow change, permission change, Docker deployment, image publication, credential handling, migration, public exposure, network change or Sydney access. PR #257 frozen, PR #258 unchanged. Evaluate both cloud-first and VM-first alternatives against the same tests; record what hosted execution cannot do after stage 3. Promotion requires its own governed work item, tests and Kevin's distinct approval.
