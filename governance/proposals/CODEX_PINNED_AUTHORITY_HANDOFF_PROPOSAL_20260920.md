# PROPOSAL ONLY — Codex authority handoff for offline checkouts (2026-09-20)

Classification: `class:governance`. Status: **DRAFT / NOT APPROVED / NOT AUTHORITATIVE**. Proposed separately from Phase 3 implementation PR #256. Source: authoritative `main` at `391b1f0a8cf9846ef2fbbad64b5ead0547c2a3c5`. Related: issue #255, parent PR #251, successor PR #256, the two Codex `Stopped Before Mutation` responses, and `docs/ceres/PHASE3_GITHUB_AUTHORITY_HANDOFF_20260920.md` on PR #256. This proposal does not override `LOOM_START_HERE.md`, `AGENTS.md`, change control, or the actual PR #255 contract.

## Problem and current boundary

Codex Cloud has a repository snapshot at the correct local commit but its ephemeral `work` checkout has no `origin`, no independent `main` ref and no authenticated GitHub CLI access; attempts to read the issue and parent PR contract returned HTTP 401. Both assignments properly stopped before editing. A chat statement or unverified copied document is not live GitHub authority. There is no implementation or test result to publish. No change to Sydney or environment security is authorized.

## Proposed solution requiring explicit governed approval

Define a limited, auditable **two-party verification** procedure: (1) a connected reviewer reads `main` governance at a stated immutable commit, independently checks relevant live PR heads, work item and binding contract through authenticated GitHub, and records the immutable SHA, path/blob identities, scope, timestamps and links in a checked-in handoff; (2) the offline Codex task validates the handoff contents against its own local exact HEAD and parent ancestry, loads the pinned governance and scope materials made available in its checkout, and confirms no contradictions. The reviewer rechecks live heads and authoritative `main` before publishing any resulting task-local commit via manual `Update branch`; if anything changed, STOP/review/rebootstrap. This is **not** permission to substitute a model's assertion for source evidence, silently infer `main` from a PR checkout, or treat a branch-local handoff as standing policy.

Before this exception can operate, define and test how Codex receives complete immutable `main` governance contents, `AGENTS.md` and nearest scoped rules, issue #255 and the binding PR #251 comment; a list of URLs, hashes or a reviewer summary alone is insufficient to satisfy content review. Explicitly specify reviewer authentication, exact content capture and provenance, freshness/revalidation window, change detection, and who can approve this exception. Any unverified or absent document, divergent SHA, stale branch, conflicting policy, invalid digest, missing review, or failed test remains a fail-closed STOP. Establish how these controls are enforced and logged without secrets or increased network access. Do not modify hard `loom-gate` semantics, freezes, promotion controls, or existing scientific protocols.

## Acceptance criteria before use

- Written governance disposition and Kevin's separate explicit approval of the final protocol; required tests/review under current change control, then promotion to protected `main` through normal review and `loom-gate` before relying on it.
- Demonstration that a deliberately stale main SHA, moved PR head, missing governance document, altered handoff, nonexistent issue/contract, and mistaken task-local HEAD each fail closed.
- Demonstration that a correct handoff can support **offline preparation only** and that GitHub publication still requires independent authenticated reviewer revalidation, normal CI, and separate merge/deploy authority.
- No GitHub credentials, tokens or secrets added to Codex; no internet setting or repository permission changes; no automatic deployment or direct Sydney mutation.

## Explicit non-effects

This PR is review material, **not** a governance waiver and **not** Phase 3 implementation authorization. PR #256 remains blocked for substantive Codex mutation unless existing current governance is independently satisfied or a new protocol is approved and promoted. Do not invoke `@codex` for substantive Phase 3 work on the strength of this proposal. No changes to `main`, parent PR #251, Sydney, Tailscale, ports, databases, workflow permissions, or production are authorized here.
