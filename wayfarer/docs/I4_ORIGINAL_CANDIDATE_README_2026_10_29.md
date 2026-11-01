# Wayfarer L1-I4 Command Commons — candidate deck snapshot

**Status:** CANDIDATE L1 · NON-CANON · NON-GOVERNING · NON-RUNTIME · NOT QUALIFIED.  
**Change class:** `class:asset-media`. **As-of:** 2026-10-31.  
**Disposition:** source-preserving candidate/media archive on upstream LOOM, not a spacecraft baseline, not an approval to adopt it in Rev7 or Rev8.

## Identity and source provenance

This is the **29 October 2026 source-annulus-constrained I4** candidate, rather than the earlier unconstrained rectangular-floor I4. It retains the six functional crew stations, paired Pilot/Captain elevated command terrace, lower distinct Navigator station, central command point, mission table, independent workbench, original annular floor and ladder openings, and a *research-only* 37-panel visual canopy. No departure from the source ship's pressure hull is approved.

- Source repository: [LOOM](https://github.com/loom-2226/loom-2226)
- Exact source branch / commit: [`research/wayfarer-nose-l1-search-20261028` at `7240dc21e6ad2e94cd0933419e10b8d4ae49c2f0`](https://github.com/loom-2226/loom-2226/tree/7240dc21e6ad2e94cd0933419e10b8d4ae49c2f0/design/wayfarer/v0.5.7)
- Source full-canopy viewer: [original self-contained HTML](https://github.com/loom-2226/loom-2226/blob/7240dc21e6ad2e94cd0933419e10b8d4ae49c2f0/design/wayfarer/v0.5.7/render/out/wayfarer_l1_i4_full_trapezoid_dome_constrained_android.html)
- Geometric ancestry: [Rev7 archive PR #432](https://github.com/loom-2226/loom-2226/pull/432), specifically source geometry pinned by the implementation brief at `3485830a56dfead79b2ef8bba031a595b536fbb5`. PR is non-governing.
- Separate research-lab [experimental L1-I4 Android WebGL walk branch](https://github.com/loom-2226/loom-research-lab/tree/9001ffc3eb694132fab6c3e58882c132629a25d4/experiments/wayfarer/l1-i4) at `9001ffc3eb694132fab6c3e58882c132629a25d4` is **not part of this mirror**, has its own provenance and has not been disposed into LOOM under the Lab-to-LOOM intake procedure.

The copied HTML, JSON, code and research brief are byte-identical source snapshots. The two scripts may still expect the original branch directory/source geometry and are **not** an independently installed ship-building or certification system.

## What is here

- [`viewer.html`](viewer.html): single-file, offline, Canvas2D interactive L1 viewer with fallback image, independent hull/dome/panel/sensor/crew/deck controls.
- [`scene.json`](scene.json): candidate I4 source-constrained scene and presentation geometry.
- [`fit_screen_results.json`](fit_screen_results.json): bounded plan-view overlap/hole/ladder results, **not** 3D accommodation verification.
- [`SOURCE_IMPLEMENTATION_BRIEF.md`](SOURCE_IMPLEMENTATION_BRIEF.md): rationale, source dimensional constraints, reproduced test claims and documented unknowns.
- [`l1_i4_constrained_fit_screen.py`](l1_i4_constrained_fit_screen.py) and [`make_l1_i4_full_fit_and_canopy.py`](make_l1_i4_full_fit_and_canopy.py): copied generator/checker provenance; original source geometry and supporting files remain on pinned source branch.

## Bidirectional relationship to Wayfarer revisions

The [Rev7/Rev8 candidate-relation index](../../REV7_REV8_L1_CANDIDATE_LINKAGE.md) links back to this L1 snapshot from **both** revision records; this file provides the reciprocal forward references.

| Revision | Relationship | What it **does not** mean |
|---|---|---|
| **[Rev7](https://github.com/loom-2226/loom-2226/pull/432)** | I4 is a candidate L1 *alternative* fitted in plan against Rev7's documented L1 annulus/ladder locations, with Rev7 geometry as its source reference. Rev7 has not adopted I4. | Rev7's six station arrangement, L1 baseline, certified results or PR head are not modified. |
| **Rev8, proposed design direction** | I4 is available for Rev8 L1 selection/design review. **No independently versioned Rev8 GitHub design/PR was verified as of 2026-10-31.** The index records the prospective link pending a real Rev8 source. | No Rev8 design is invented, adopted, merged or certified by this association. |

## Qualification boundary

**Bounded checks passed:** plan-view seat/furniture bounding footprints against L1 floor outer radius `4.15m`, central opening `0.9m`, original two ladder centres `Y=±1.4m` with source diameter `0.8m` and stated margin. The original rectangular floor is replaced with the source annulus in this candidate.

**Open / HOLD:** actual ship forward axis versus the illustrative I4 viewer axes; full swept human bodies, seated reach, clearances, three-dimensional ladders and egress, real structure/seat mounts, 4g biological loads, headroom, optical glazing and ballistic/damage/pressure shell protection, exterior panel strength, thermal/radiation interfaces and physical sensor accommodation. Research panes/domes/optogel are not canonical protection technology. No claim of hardware certification or ship readiness.

The original brief reports Chromium desktop/mobile viewport and offline-render checks; this PR is a **source-copy and relationship change only** and does not claim fresh Pixel, runtime, functional or qualification tests. All original source results remain labeled as such.

## Downstream / rollback

- Canon, physics, geometry compilers, runtime, release, Navigator, SQLite, protected Rev7 PRs: **UNCHANGED_COMPATIBLE** because they are neither edited nor pointed at this candidate as a governing source.
- Any future Rev8 package or L1 source geometry selection: **REVIEW_REQUIRED**, then full 3D/4g and physical qualification before acceptance.
- Roll back by reverting the dedicated asset-media archive PR; pinned source branches and existing Rev7 remain unchanged.
