# Ceres Sydney update and rollback — Phase 3 implementation plan

Status: proposal / offline implementation only. Primary change class: `class:runtime`.

Parent Docker qualification: PR #251. Work item and acceptance criteria: issue #255, https://github.com/loom-2226/loom-2226/issues/255. Binding deployment contract: https://github.com/loom-2226/loom-2226/pull/251#issuecomment-5741292212.

This successor branch is deliberately separate from PR #251. Its initial base is the qualified parent branch commit `625e139a32f3461068e2b84192725e79f42a4c89`; verify both branch heads and current `main` governance before any substantive work. This document creates a reviewable diff; it does not establish deployment readiness.

Implement and qualify an offline/dry-run-capable, manually invoked update-and-rollback procedure under issue #255. Preserve immutable digest and source/CI provenance, explicit per-release approval, loopback-only `127.0.0.1:8768`, private Tailscale Serve with Funnel OFF, the existing host allowlist, three external read-only database mounts, existing image/configuration and backup recovery points. Fail closed on unexpected public binding, incompatible data, missing credentials or registry access, bad health/media, timeout, and failed rollback. Test without accessing Sydney. Preserve Pixel/Windows updater behavior.

No live Sydney operation, image publication, automatic deployment, merge, production promotion, public ingress, database mutation, credential disclosure, repository-permission change, or security-control relaxation is authorized by this plan. If the branch/base or a safe rollback mechanism cannot be verified, stop for review rather than improvising.
