# Phase 3 — externally verified GitHub authority handoff (2026-09-20)

**Classification:** `class:runtime` documentation / evidence only; NON-DEPLOYMENT, NON-APPROVAL, NON-QUALIFICATION. This record does not supersede current GitHub `main`, repository governance, Issue #255 or the binding PR #251 contract. It is not permission to bypass the mandatory authority check, and a GitHub push of this document alone is not an implementation.

## Verified through the connected GitHub reader before this document was created

- Repository `loom-2226/loom-2226`, authoritative `main` at `391b1f0a8cf9846ef2fbbad64b5ead0547c2a3c5` (GitHub branches/main GET). This is a *point-in-time* observation, not a promise that main remains there.
- PR #251: base of stacked PR #256, `engineering/ceres-atlas-docker-qualification-20260919` at `625e139a32f3461068e2b84192725e79f42a4c89` as reported by the live PR #256 metadata; independently recheck PR #251 before implementation or publishing.
- PR #256: OPEN DRAFT, base branch above, head `engineering/ceres-sydney-update-rollback-20260919` at `a0c647f052ece20f8445b498d45650ebb10095e3` before this documentation commit. Its previous diff consisted of a planning file only. The head changes when this document is committed: obtain the NEW head from GitHub, do not reuse this earlier SHA as current.
- Read live-main `LOOM_START_HERE.md` (blob `42b90814173ec686221e2074558e0dcad55d8ca6`), `governance/current/LOOM_CURRENT_WORKSTATE.yml` (`3acb8604904c6cffc7cd527a637de735d07ac928`), `governance/current/LOOM_PROJECT_STATUS_2026-09-12.yml` (`775dcbc692a6435b6880c97e3b31fde1deb23041`), and root `AGENTS.md` (`c06254cf9158b82ec6114c1becc503e8d1787b12`). These source blobs were actually retrieved from `main`, not inferred from the PR checkout. Remaining authority-model, change-control, research-boundary, scoped agent, dependency/compatibility, and release documents still require inspection before executable changes.
- Issue #255 was retrieved directly through authenticated GitHub and remains OPEN. It authorizes ONLY a separately reviewable proposal for offline/dry-run tooling and tests, **not** deployment, publication, merge, Sydney access, public exposure, secrets, repository settings, or edits to PR #251. Binding contract: PR #251 comment `5741292212`, which must also be retrieved/read in full before implementing.

## Required entry points (full governing text remains at these sources)

- `LOOM_START_HERE.md` → `governance/current/LOOM_CURRENT_WORKSTATE.yml` → `governance/current/LOOM_PROJECT_STATUS_2026-09-12.yml` → governance baseline, authority model, change control, research authority boundary → `AGENTS.md` → nearest scoped `AGENTS.md`.
- Work item: https://github.com/loom-2226/loom-2226/issues/255
- Binding contract: https://github.com/loom-2226/loom-2226/pull/251#issuecomment-5741292212
- Existing draft proposal: https://github.com/loom-2226/loom-2226/pull/256

## Access blocker and fail-closed handoff

Two Codex Cloud attempts stopped BEFORE mutation: task checkout had only a local `work` ref, no Git remote or `main`, `gh` was unauthenticated, and private issue/contract fetches returned 401. Neither attempt made an implementation commit or ran tests. An externally reported SHA, this committed handoff, or an `@codex` comment **does not itself satisfy** Codex's required independent verification of current authority; do not claim otherwise. No secrets, PAT, agent-internet enablement, remote reconfiguration or weakened governance are authorized.

A reviewer with the authenticated GitHub connection must independently revalidate the live main/head SHAs, governing files, Issue #255, binding contract, change-class/dependencies/tests and targeted scoped instructions immediately before each authoritative code mutation and before any publication. If Codex's environment cannot independently access that material and the governing rules do not explicitly permit a reviewer-attested, version-pinned handoff in lieu of direct access, STOP executable changes and escalate that specific access/authority question for governed disposition. Preparing non-authoritative analysis without mutation is allowed. Do not summon Codex into an identical doomed rerun based solely on this document.

**Absolute boundaries:** offline implementation only; no host contact, Sydney modification, database writes, secrets, new PR or branch, parent-PR changes, merge, deployment, image publication, Tailscale/Funnel/public-port changes, automatic CI deployment or release promotion. A future task-local implementation commit, if validly authorized and tested, may use the established manual `Update branch` flow, followed by independent GitHub SHA/diff/CI verification; this file creates no such commit.
