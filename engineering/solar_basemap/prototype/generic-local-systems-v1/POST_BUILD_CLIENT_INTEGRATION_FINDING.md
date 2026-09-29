# Post-build client integration finding

The first complete product build (`856ee022a82bc62cdc7454cc2c596a17d1948a6b41e4c45fc189e7127703515e`)
passed immutable product validation with 32/32 requested curves. The Mars
touch-route regression then found that the accepted generic client could not
present Mars parent context after changing local anchors from prototype primary
aliases to governed system barycenters.

The renderer's existing generic parent-context path resolves a local node's
parent arc by matching the node's `anchor_id` to a Sun-relative curve's
`feature_id`. The first successor product correctly included Mars-relative
Phobos and Deimos curves anchored at `MARS_SYSTEM_BARYCENTER`, but did not
include the barycenter's own Sun-relative curve. No physical or identity
relationship should be inferred to substitute Mars for that governed anchor.

The generic generation policy now includes a Sun-relative curve for each
resolved local anchor that has at least one generated local-member curve. This
uses the anchor's own governed identity/source and enables the already accepted
client path. Anchors for families with no supported local-member curve do not
receive a curve under this rule. This produces six additional governed Solar
curves in the current catalog; expected inventory is 38 requested curves, of
which 14 are Sun-relative and 24 are parent-relative. A full rebuild and both
browser routes are required after this correction.

The failed browser assertion is retained as a qualification finding, not a
passing record. `MARS_PHYSICAL_PIXEL_PASS` remains the inherited human gate for
PR #320; this finding concerns successor product integration only.

The corrected product (`9450c32ba2c4b9635b86d988651f682006a294d853b728658e9cf8ca72e66f4e`)
passed validation and exposed both exact Solar anchor arcs and parent-relative
moon curves. The Mars route then passed, reaching the governed Mars barycenter
parent arc plus Phobos and Deimos, with the original pan, focal pinch, yaw/pitch,
LOD, scale and no-authority-call assertions intact.

The progressive browser benchmark then found that putting all six extra
barycenter arcs in the initial root raised the manifest-plus-root transfer above
the existing 49,920-byte budget. Those same governed curves now remain in
progressive Solar chunks and the root carries empty segment lists for their
curve metadata. The renderer displays them as local parent-context ink after
Solar refinement. A fresh deterministic build and qualification are required.

The first build with deferred anchor segments (`ffccc55d224b772565271f089470a933132673137b5e71fb72c4182357ee63f4`)
completed all 38 curve audits but exposed an independent-validator mismatch:
the contract still expected every Sun-anchored curve in the embedded root LOD.
The validator now derives the embedded Solar inventory from all Sun-anchored
curves minus the explicit `solar_parent_context_curve_ids` inventory. It also
fails if those context IDs are not Sun-anchored. The next full build and
independent validation are required because the failed build correctly removed
its unpromoted staging directory.

The corrected full build (`ffccc55d224b772565271f089470a933132673137b5e71fb72c4182357ee63f4`)
passed independent validation with 38/38 curves, 110 catalog features,
103 resolved and 7 unresolved identities. Manifest plus root transfer is
41,616 gzip bytes, under the 49,920-byte bootstrap limit. Mars and Jupiter
touch routes passed: the Mars context contains the governed barycenter and
Phobos/Deimos, and the Jupiter route exposes Io while preserving all seven
explicit omissions and making no authority calls.

The full progressive browser benchmark then exposed two inherited QA
assumptions: raster predicates still searched for mint/amber orbit pixels,
while the passed Navigator cartography uses subdued steel ink; and the
close-up error report applied local projection to the cropped, faint Solar
parent-context arc rather than the parent-relative refinement curves. Raster
diagnostics and predicates now measure the existing steel orbital ink. QA
continues to report the parent context arc and its global Solar LOD error, but
marks it `LOCAL_PARENT_CONTEXT_ONLY` and excludes it from the close-up local
refinement error budget. Solar overview LOD and visible parent-relative curve
errors remain under their existing acceptance checks. The Mars-only progressive
browser trial passed; full progressive trial qualification is in progress.

Final progressive qualification on the final deterministic build passed both
unthrottled and 10 Mbps / 80 ms / 4x CPU trials. Each run fetched only the
current manifest, immutable root, and policy-selected progressive resources;
bootstrap manifest+root remained 41,616 gzip bytes. Earth, Mars and Pluto
routes passed their geometry, identity reconciliation, scale-error and
interaction assertions; warm visits redownloaded zero immutable chunks. The
trial recorded zero authority calls. In this software-WebGL environment the
maximum frame interval was 2,874 ms unthrottled and 8,428 ms under throttling,
so the recorded route/acceptance checks pass while frame pacing is a visible
qualification limitation, not a claim of smooth benchmark performance.

Final regressions passed: 15 compiler/contract unit tests, JavaScript syntax
checks, `git diff --check`, the full progressive browser trial, the inherited
Mars pixel-touch route (including `MARS_PHYSICAL_PIXEL_PASS`), and a Jupiter
pixel-touch route. Jupiter selected `system:JUPITER_SYSTEM_BARYCENTER`, drew Io
and the other three governed moon curves after seven bounded pinches, preserved
seven unresolved omissions, and made no authority calls. Final product build
ID is `ffccc55d224b772565271f089470a933132673137b5e71fb72c4182357ee63f4`.
