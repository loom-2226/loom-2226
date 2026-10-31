# Wayfarer conventional laboratory qualification — Phase 1 main-branch integration candidate

ALL bodies. ALL sponsors. 2026–2226.

**class:engineering · INTEGRATION CANDIDATE · NOT MERGED · NOT CANON OR PHYSICAL FLIGHTWORTHINESS.**

## Authority and provenance

- **Base:** current `main` `f07354f57244d62e7c1932cacddd0f996d45e941`, already includes the I4 candidate from PR #434. This is a new main-based integration branch, not a retarget or merge of PR #435 against the Rev7 archive.
- **Accepted source:** PR #435 `d290edb10cdd675e7b019322cafbe81a9920a949`; earlier Rev7 source pin PR #432 `3485830a56dfead79b2ef8bba031a595b536fbb5`. Claude independent SIGN-OFF reported by kT as a review conclusion; GitHub approvals and deterministic loom-gate remain independent checks.
- **Integration:** copied accepted `design/wayfarer/v0.5.7` subtree verbatim; no edits to `canon/current`, `src`, `geometry`, Navigator code, runtime, release manifests or scientific frozen branches. Existing main I4 candidate and Rev7/Rev8 relationship index remain historical records (not silently rewritten).
- **Exact source geometry SHA256:** `5d73cdd1d7893b75637fc3b2e8bf2d9b786b792fede277e759561643f4ee0256`. No geometry rebuild/change is authorised except reproducibility testing that yields identical bytes.
- **Main dependency impact:** `REVIEW_REQUIRED` for any future Navigator/runtime/card adoption; existing downstream source modules `UNCHANGED_COMPATIBLE` because unmodified; visual and tests non-governing. New qualified lab baseline is engineering authority within its declared scope only.
- **Frozen impact:** PRs #19 and #16 unchanged. No active research Lab responsibility transferred.

## G1–G12 certified predicate reproduced

- `python3 design/wayfarer/v0.5.7/certify.py`: 12/12 gates PASS or PASS-DECLARED, **18/18 declared assumptions ACCEPTED**, machine `certified=true`. This is declared conventional laboratory certification, not a hardware certificate.
- `G12` current manifest/17 images/viewer/two-scene GLB uses hash `5d73cdd1d7893b75637fc3b2e8bf2d9b786b792fede277e759561643f4ee0256` (G12 PASS-DECLARED).
- **Metric arrival HOLD**; no arrival dynamics/remass/terminal state qualification.
- **Navigator EXCLUDED**; no mission integration/runtime payload migration.
- **RCS heating source OPEN** (idle torch reactor vs separate supply; no ship electrical/heat budget). Routine RCS flips 120s, 40s fast flips emergency only; charged hot-water store option B.
- **FQ10 conditional:** idealised 0.20s stuck-TVC detection, throttle then cut. No physical FDIR certification.

## FQ1–FQ10 evidence provenance

- Historical full FQ1–FQ10 matrix in PR #435 was run on predecessor geometry `ea1fcb59...`. These outputs remain historical; they are not relabelled as current-geometry passes.
- **Current-geometry evidence:** one authorised 40s RCS pitch flip on `5d73cdd1d7893b75637fc3b2e8bf2d9b786b792fede277e759561643f4ee0256` with recorded 9 simultaneously firing nozzles, ~244.46MW thrust-weighted ideal floor, ~518.97MW 9-nozzle nameplate concurrency allowance and 1,845.22MW all-nozzles ceiling (NOT observed).
- **Phase 1 replay:** independently reconstruct current S1/S4 mass, CG and full inertia (tensor error <1e-5 kg m²) and run non-governing conventional FQ1–FQ10 replay at the same SHA; fully replayed final-hash results indexed under `flight_qual/integration_20261101/`. Current-hash replay has **93/93 timestep-parity verdict pairs**, 78/78 fueled-state PASS per timestep and 15 expected empty-tank FAIL per timestep; FQ5 FQ8 FQ9 FQ10 checks PASS in their bounded/conditional sense. See [replay report](flight_qual/integration_20261101/FQ1_FQ10_REPLAY_5D73_2026_11_01.md). A replay is evidence, not automatic adoption of PR #433 or PR #436 source into production.

## Integration-only Python defect repair

- Historical `command/l1_bore_check.py` inherited an unterminated module docstring from PR #435 (not part of active I4 qualification). Closed **only** the documentation string so all 29 Python sources compile. No executable law, geometry, mass, render or FQ method changed. Archive PR #435 untouched.

## Required integration gate / recovery

- Required `loom-gate` deterministic CI on a new PR targeting `main`, under `class:engineering`. No bypass, no policy changes.
- Independent sign-off supplied by kT for the **lab scope**; GitHub review and protected-main merge by kT remain separate. PR remains unmerged by Sol.
- **Rollback:** close/unmerge this PR or revert its integration commit; main remains at its previous unchanged I4/Rev7-linkage state. No direct deployment or compatibility shims.

## Phase 2 (strictly later, NOT HERE)

- Only after kT merges Phase 1, open a separate main-based PR for one `wayfarer/` home with exactly `config/`, `lab/`, `render/`, `results/`, `docs/`. No compatibility shims; perform actual moves, fix all imports, delete old paths and rerun consumers and tests.
- Include PR #433 historical flight lab and PR #436 non-governing cards under `wayfarer/lab/`, without automatically promoting Metric cards or physics.
- Close PRs #429, #430, #432 **without deleting archive branches** only after a documented merge/migration disposition. Do not close them in Phase 1.
- No Navigator or Metric arrival integration during either phase without separate approval.
