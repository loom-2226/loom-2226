# Wayfarer viewer: publication and design handoff

Class: `class:asset-media`. Status: draft PR #246, not publication approval. This page is a read-only presentation, not canon or engineering authority.

## Preserved design search

Keep active four redesigned normal remass envelopes (250 t total), historical four 14 m × 3 m cylinders, six-smaller and two-paired alternatives, and separately protected 50 t reserve. The reserve vessel location, fluid density/fill fraction, capacity, ullage, tank mass, longeron collision, feed routing, cabin/shuttle preservation and any local shell widening remain unqualified. PR #240 is an engineering source pointer, not an automatically imported approval. Never relabel a candidate as qualified when exporting a GLB or render.

## Publication procedure

1. Work on feature branch and PR; classify changes as asset/media and verify governing main, scoped AGENTS and relevant engineering refs. Preserve Ceres and Inspector.
2. For source-only HTML changes, perform static and mobile/desktop UI checks. For new assets, separately review source identity, SHA-256, rights/public disclosure, coordinate frame, geometry status, naming, dimensions, and asset provenance; register only approved files. No raw SQLite/CIVSTATE or private data in `docs/`.
3. Run current-head `loom-gate`, inspect complete Pages preview artifact, confirm all `docs/` sections preserved. No PR preview is live publication.
4. Merge via protected main, then explicitly authorize the existing manual `.github/workflows/inspector-pages-deploy.yml` publication confirmation. The workflow downloads the immutable pinned media release, validates 182 approved assets, builds Inspector and uploads all `docs/`.
5. Smoke test live `/inspector/`, `/ceres/`, `/ships/` on Android and desktop; record commit, workflow run, hashes and results. Roll back by reverting source through PR and explicitly republishing. Never assume rerunning current main restores an older version.

## Current limitation

`docs/ships/index.html` currently provides conceptual schematic, cross-section, alternative register and empty 3D/render slots. It does not load a GLB. The existing Inspector preview triggers do not include `docs/ships/**`; a separate workflow improvement is required before treating ship-only PRs as automatically previewed. The existing manual deployment must not be silently automated or dispatched without its explicit publication authorization.
