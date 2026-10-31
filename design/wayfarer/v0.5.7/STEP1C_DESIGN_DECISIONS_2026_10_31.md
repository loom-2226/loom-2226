# Wayfarer Step 1c — kT I4 couch/crawl/S4 decisions (2026-10-31)

ALL bodies. ALL sponsors. 2026–2226.

**NON-GOVERNING • DRAFT/HOLD PR #435 • not ship physical qualification.**

## Exact source geometry and allowed change

- Input predecessor: `92905754eec2cae2ea50083803b419c830de7849ef69194e3a863c8a8efa03f1`.
- Current source-built geometry SHA256: `ea1fcb59f1e0a127cd48dc4e0321e7d42247e3f2e445cf89893bdefadb793266`.
- The hash changed because kT ordered an actual S4 station relocation in Rev7 source coordinates, rather than a mere evidence refresh. This DOES NOT overwrite the pinned Rev7 PR #432 source `3485830a`.
- S4 nominal centre Y,Z: `(2.45, −2.00)m → (2.20, −1.70)m`. Seat head `(2.1541,−1.2675) → (1.9041,−0.9675)m`; feet `(2.7459,−2.7325) → (2.4959,−2.4325)m`. All 32 RCS/torch mounts, pressure hull, annular L1 floor, ceramic crown and closing Strata gores unchanged.
- One geometry rebuild was run for this S4 relocation. Dry mass remains `867.681453466738 t`. New S1 wet mass `1167.681453466738 t`; S1 CG `(24.4004859082, +0.0245558633, −0.3571403253)m`. Full inertia tensor and other mass states preserved in hashed geometry JSON.
- kT couch rule: I4 nominal **1.58m contoured couches**, **NOT** the 2.10m full-length flat berth screen. This establishes only a plan-layout proxy. Custom occupant liner, raised knees, 4g restraint load, feet-clearance/headroom and 99th-percentile suited accommodation remain physical HOLD.
- kT terrace crawl rule: **1.20m minimum** bare axial crown-envelope clearance, not 2.10m standing. Worst original rectangular terrace corner `1.339m`, passes only this bounded rule. An optional 0.5m corner chamfer analytically gains 0.135m to 1.473m and is **not built**.
- Conservative nominal corridor check: source annular L1 outer radius 4.15m, 0.8m clear route to each floor station, two source ladder landings clear and connected on a 0.1m grid. Actual raised Pilot/Captain and Navigator transfer, human torso sweep and physical hatch/ladder escape remain HOLD.

## G1–G12 status on new geometry

Single non-promotional `certify.py` rerun follows a full `habitat/hab_overlay_checks.py` radiation rerun (36 points, 600 directions, 2cm step) and `command/l1_i4_checks.py` evidence renewal.
- G5 **PASS-DECLARED**: four lowered terrace column members screen at 7.5g ultimate and 0.5g lateral; actual joint/deck structure HOLD.
- G6 **PASS-DECLARED**: armour-equivalent node-face case min 40.38g/cm²; open-bore sensitivity 14.78g/cm²; node placement PR #184 HOLD.
- G7 **PASS-DECLARED**: all seven accepted *bounded* I4 couch/crawl/annulus/route checks pass. No true 3D occupant/4g/sightline qualification.
- G12 **FAIL**: stale geometry-stamped images, held intentionally. **No renders executed.**
- Other source G verdicts remain unchanged; **certified=false**.

## RCS fuel and power pending

kT ACCEPTS **unprotected 250t remass water** as RCS feed. The separate 50t protected reservoir is not propellant. The exhaust velocity is a **VARIABLE**; 1.00 and 1.96km/s are screening cases, not fixed hardware certifications. No new RCS nozzle, mount, control, feed system or tank is built.

Include **2.6MJ/kg** water conditioning/boiling plus **0.5 × ve²** ideal kinetic energy:
- 25kN at 1.00km/s: 25kg/s, 77.50MW **minimum** combined power.
- 25kN at 1.96km/s: 12.755kg/s, 57.663MW **minimum** combined power.

Actual plant availability, heater efficiency, additional superheat losses, plumbing, heat rejection and water-store recharge are not closed. **kT decision pending: A on-demand plant heat or B precharged hot-water store.** No free/available energy is silently credited.

## Stop / review

This Step 1c configuration and the FQ1–FQ10 evidence are in PR #435's existing draft branch only. The source geometry hash changed from the prior lock for an authorized reason and all revised evidence uses the new hash. No render, Navigator, Metric, repo migration, release, canon promotion or merged main.
