# LOOM 2226 — Governance Adoption Sprint — Step 2 Branch Bootstrap

**Date:** 7 September 2026  
**Status:** STEP 2 — GOVERNANCE IMPLEMENTATION BRANCH CREATED  
**Branch:** `governance/repository-control-baseline-v1`  
**Exact base commit:** `36c21d1d13bcb441316bdb8b6f944b8a1cc2cba7`  
**Source authority at branch creation:** frozen `main` captured in Step 1

## Purpose

Create a dedicated implementation branch for LOOM repository governance without modifying any in-flight game, research, canon, runtime, data, media, release, launcher, SQLite, or 3D workstream.

This branch is the only branch authorized to receive Governance Adoption Sprint implementation work until the explicit restart gate.

## Stability contract

During the adoption sprint this branch may add or change only governance/control-plane material such as:

- `governance/**`
- future root `AGENTS.md`
- future `LOOM_START_HERE.md`
- future `.github/**` governance templates/workflows
- future machine-readable dependency, authority, compatibility and workstate manifests

The following remain forbidden until their own controlled work resumes:

- `canon/current/**` content changes;
- Navigator / GIS behavior changes;
- production runtime changes;
- SQLite schema or payload changes;
- media asset or media-library behavior changes;
- Android/Windows launcher or updater-root changes;
- Wayfarer geometry / Blender / 3D changes;
- physics/research execution or tuning;
- any mutation, rebase, merge-from-main, or cleanup of frozen PR #19;
- any mutation of PR #16 Stage-A preregistration.

## Relationship to Step 1

Step 1 recovery refs remain the authoritative pre-governance recovery points. This branch does not replace, reinterpret or move them.

If governance implementation exposes a contradiction in current LOOM authority, the contradiction is recorded for later reconciliation. Governance must not silently repair working source material during adoption.

## Next step

Step 3 will define the LOOM authority hierarchy, change classes, promotion model, amendment/supersession rules, dependency invalidation, frozen-experiment rules, and current-workstate contract.

Walter's assurance role is separately defined under `governance/roles/` as a governance-layer persona and does not alter his in-universe character canon.
