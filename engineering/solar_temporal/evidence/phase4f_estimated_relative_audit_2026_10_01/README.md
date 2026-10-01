# Phase 4F estimated-relative independent audit

Status: AUDIT ONLY. No authority mutation.

Audited bodies: Proteus, Dactyl, Selam.

## Findings

- All three resolve at 2226 as ESTIMATED_RELATIVE, navigation_grade=false, with explicit uncertainty in public Inspector provenance.
- Dactyl and Selam use LOOM SPK_TARGET_ID identifiers. Their public provenance carries naif_identifier=null; they do not masquerade as NAIF identities.
- Proteus retains its genuine NAIF identity 808. Direct JPL/NAIF NEP098 authority ends at ET 6311304000.0. The Phase-4F estimate begins at that exact ET.
- The Proteus estimate is C0 position-continuous at the seam, not C1 state-continuous. Independent audit measured position mismatch 1.67e-11 km and velocity mismatch 0.012470684 km/s because the nominal circular model replaces the direct endpoint velocity.
- Replaying the same circular approximation wholly inside NEP098 truth produced sampled position errors of 48.01 km after 1 day, 276.22 km after 7 days, 181.82 km after 30 days, 170.64 km after 365 days, and 448.52 km after 3650 days. These are empirical samples, not an all-interval bound.
- Proteus declares 235526.635 km uncertainty (one nominal orbital diameter), Dactyl 180 km, Selam 6.2 km. These intentionally prevent precision interpretation.
- Dactyl and Selam game-epoch phase is explicitly unconstrained. Their products are nominal visualization/game-state geometry, not physical ephemerides or validated propagation.

## Verdict

The 110/110 closure is representational, not homogeneous physical authority. The three products are defensible only under the explicit ESTIMATED_RELATIVE class. They must not be promoted to DIRECT or PROPAGATED based on this closure.

The earlier evidence phrase that Proteus "anchors continuously" should be read as position continuity only; velocity is discontinuous at the source seam.
