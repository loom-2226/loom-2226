# LOOM 2226 — Wayfarer Project State and Pixel Handoff v0.2

**Status:** ACTIVE ENGINEERING SNAPSHOT / NON-GOVERNING  
**Date:** 2026-09-06  
**Purpose:** Preserve the complete current Wayfarer geometry/packaging/runtime state, written project decisions, Pixel workflow, implementation file map, and immediate engineering direction in one recoverable GitHub source.

---

## 1. Governing-source hierarchy

For Wayfarer engineering, use this authority order:

1. `canon/current/LOOM_2226_CANON_II_Engineering_Ships_Operations_v2.4.md` — governing baseline.
2. `canon/current/LOOM_2226_CANON_II_Wayfarer_Schematic_Amendment_v2.4a.md` — governing schematic/physical-packaging amendment for the integrated launch bay and associated exterior arrangement.
3. Current engineering plans in `engineering/current/` — non-governing design baselines unless explicitly promoted.
4. `canon/archive/LOOM_2226_Ship_Operations_Courier_Canon_Compendium_v1.0.md` and older manuals — legacy/reference only where non-conflicting.

No engineering visualization, Blender model, Three.js primitive, or generated image is permitted to silently override governing canon.

---

## 2. Current project objective

The project is creating a deterministic, inspectable physical model of the inherited interplanetary/interstellar courier **Wayfarer**. The geometry is intended to support:

- physical packaging checks;
- deck/habitation/launch-bay planning;
- tank, structure, thermal, propulsion and relational-plant placement;
- configuration-state inspection;
- mass and center-of-mass checks;
- future interference/sweep-envelope checks;
- a browser-native Pixel engineering viewer;
- a later Blender high-detail model and render pipeline;
- future export to more formal CAD/geometry tooling without changing the underlying authority model.

Generated imagery is visual reference only. The deterministic parameter model is the geometry authority.

---

## 3. Geometry authority and provenance model

The working geometry pipeline is:

`SQL parameters -> Python geometry compiler -> wayfarer_geometry.json -> Three.js Pixel viewer / Blender builder`

Every parameter or component should carry provenance. Current provenance classes are:

- `CANON`
- `DESIGN_BASELINE`
- `DERIVED`
- `LEGACY_COMPATIBLE`
- `VISUAL_REFERENCE`
- `OPEN`
- `CANON_MASS_DESIGN_POSITION` where a canon mass is paired with a non-canon working centroid.

The purpose is to make it impossible to confuse a trial dimension with a canon lock.

---

## 4. Coordinate convention

Current geometry convention:

- **X** runs forward to aft.
- Bow datum is **x = 0 m**.
- Aftmost permanent nozzle structure is **x = 57 m**.
- **Y** is transverse.
- **Z** is transverse.
- **+Z** is the integrated planetary-launch bay side.
- **-Z** is the standard docking side.

Decks remain perpendicular to the torch axis. Under torch acceleration, aft is down.

---

## 5. Current governing Wayfarer ship values

Reference courier baseline:

- Main body: approximately **57 m long x 9 m nominal main diameter**.
- Normal crew: **6**.
- Payload target: **50 t**.
- Working fluid/water inventory: **300 t**.
- Normal remass: **250 t**, contained within the 300 t inventory and not an additional mass.
- Protected water reserve: **50 t**.
- Dry mass excluding working fluid/water: **858.5 t**.
- Wet mass: **1,158.5 t**.
- Mass after expenditure of the normal 250 t remass inventory: **908.5 t**.
- Unified relational plant: approximately **88 t**.
- Relational Mc-299m inventory: **10.0 kg**.
- Active tiles: **100 x 100 g**.
- Distributed boundary/metric nodes: **208**.
- Shared reversible field bank: **2 GJ**.
- Cryogenic chain: **20 K class**.
- Certified cold load: up to approximately **136 kW**.
- Electrical input in HARD metric operation: up to approximately **23.9 MW**.
- High-drive rejection interface: **900 K**.

Metric radiator equivalent area at 900 K:

- NORMAL: **106 m²**
- FAST: **202 m²**
- EXPEDITE: **336 m²**
- HARD: **719 m²**

The **719 m² value is an equivalent area requirement for HARD metric operation at the stated interface condition, not a mandate that the physical radiator panels total exactly 719 m².** Physical radiator topology and total physical emitting area remain open.

Current torch exhaust-velocity cards:

- ECON: **3,000 km/s**
- CRUISE: **2,000 km/s**
- EXPEDITE: **1,000 km/s**
- FAST: **700 km/s**
- HARD: **450 km/s**
- LIMIT: **300 km/s**

Major torch burn and high metric operation are mutually exclusive thermal/field configurations.

---

## 6. Frozen topology already treated as governing

Current design must preserve:

- four major working-fluid/remass tanks;
- four principal axial longerons;
- four major deployable radiator assemblies in quadrature;
- one axial primary fusion-torch / magnetic-nozzle system;
- a semi-recessed, substantially enclosed integrated planetary-launch bay rather than an exposed sidecar;
- pressure-tight crew transfer between ship and launch;
- primary-frame attachment for the launch bay;
- lateral launch extraction from the +Z side;
- no artificial-gravity ring;
- no mothership wings or landing gear;
- no naval-hull styling, fighter styling, decorative fins, extra main engines, or decorative weapons architecture.

Detailed tank shells, radiator folding topology, hull contour, launch dimensions, bay door topology, ground vehicle dimensions, detailed reactor internals, shield construction and plume geometry remain open unless separately promoted.

---

## 7. Current axial packaging baseline

Working axial stations:

- **x 0-14 m:** habitat / pressure hull
- **x 14-18 m:** service / transfer region
- **x 18-32 m:** four major tanks plus relational mass-center region
- **x 32-38 m:** thermal/radiator manifold region
- **x 38-43 m:** directional shield / isolation region
- **x 43-50 m:** reactor / thrust frame region
- **x 50-57 m:** magnetic nozzle / torch region

Additional current envelopes:

- Integrated launch bay: approximately **x 16-27.5 m**, +Z.
- Principal relational-plant envelope: approximately **x 18-34 m**.
- Radiator root region: approximately **x 33-38 m**.
- Standard docking collar working station: approximately **x 16 m**, on -Z.

---

## 8. Habitat and forward-body design baseline

Current pressure-vessel trial:

- approximately **8.6 m outside diameter**;
- approximately **14 m axial length**;
- target approximately **270 m³ net habitation volume** for six.

Five principal deck zones are currently used for arrangement studies:

1. D1 — command / navigation
2. D2 — common / galley / observation
3. D3 — quarters
4. D4 — medical / life support / storm shelter
5. D5 — mission / EVA / planetary-launch transfer

Working habitat central core: approximately **1.8 x 1.8 m**.

Window direction:

- target total approximately **10-16 meaningful engineering-constrained windows**;
- windows should be distributed according to actual deck function;
- D4 storm-shelter/medical region should have no windows;
- no cockpit canopy treatment.

The pressure vessel and the external armor/MMOD shell are conceptually distinct and should eventually be modeled separately.

Legacy-compatible physical guidance still usable where non-conflicting:

- pure-vacuum mothership;
- reactor aft behind directional shadow shielding;
- approximately 20 m class separation between reactor region and occupied forward spaces;
- no rotating habitat.

---

## 9. Four-tank / four-longeron cross-section

Current design-baseline cross-section:

- nominal main body diameter: **9.0 m**;
- radius: **4.5 m**;
- four major tanks: approximately **3.0 m external diameter** each;
- tank centers clocked at **45°, 135°, 225°, 315°**;
- tank-center radius: approximately **2.7 m** from thrust axis;
- four principal longerons at **0°, 90°, 180°, 270°**;
- longeron radial station: approximately **2.45 m**;
- central technical core: approximately **1.4 m diameter**.

The grammar is intentionally alternating: four tanks on diagonals, four structural longerons on cardinals. This preserves clean structural paths and creates distinct service/core corridors.

---

## 10. Integrated planetary launch and bay

Current working launch envelope:

- approximately **10.5 m long**;
- approximately **3.9 m wide**;
- approximately **3.1 m high**;
- working configured mass approximately **33 t**;
- normal occupants **2-4**;
- maximum occupants **6**.

Current bay envelope:

- x approximately **16-27.5 m**;
- clear transverse width approximately **4.4 m**;
- radial depth approximately **3.5 m**;
- inner floor radius approximately **3.6 m** from ship axis;
- launch extraction laterally in **+Z**;
- bay is vacuum / unpressurized around the launch;
- pressure-tight crew transfer is through ship-side transfer infrastructure;
- launch is treated as a fitted holstered vehicle integrated into the structural envelope.

Current local overall width with bay blister is approximately **11.5-12 m**.

Compact ground-vehicle placeholder:

- length approximately **2.7-3.0 m**;
- width approximately **1.5-1.7 m**;
- height approximately **1.3-1.5 m**;
- mass approximately **1.2-1.8 t**;
- electric.

The exact launch aerodynamic body, landing gear, atmospheric propulsion, bay-door topology and final bay blister contour are not yet canonized.

---

## 11. Aft propulsion and thermal baseline

Current aft physical sequence:

- four radiator roots tied close to the four longerons;
- x approximately **38-43 m** directional shadow-shield envelope;
- shadow-shield transverse envelope approximately **5-6 m class**, with current working diameter **5.5 m**;
- x approximately **43-50 m** reactor/torch machinery envelope;
- reactor/torch working diameter approximately **4.25 m**;
- x approximately **48-50 m** annular thrust-frame convergence region;
- four principal longerons converge loads into the single axial propulsion system;
- x approximately **50-57 m** one magnetic nozzle;
- working nozzle aperture/support diameter approximately **6.0 m**.

The exact reactor internals, shield layering, radiator panel mechanism, nozzle magnetic-coil geometry, thermal plumbing and plume envelope are intentionally OPEN.

---

## 12. Radiator model status

Exactly **four** major radiator assemblies are frozen in quadrature and should align structurally with the four-longeron grammar.

Current Three.js and Blender geometry uses placeholder radiator slabs only. These are not final engineering solutions.

Required eventual behavior:

- STOWED
- DEPLOYING
- DEPLOYED
- explicit root hinge geometry
- explicit swept-volume envelope
- collision/interference checks against launch extraction, docking, RCS and other deployed systems
- high-temperature refractory visual language rather than solar-panel visual language

Physical panel dimensions and folding topology remain OPEN.

---

## 13. Current dry-mass design ledger

The current provisional dry ledger closes exactly to **858.5 t**:

- primary structure: **150 t** @ x ~28 m
- armor / fixed shield: **105 t** @ x ~9.5 m
- habitation / life support: **45 t** @ x ~8 m
- relational plant: **88 t** @ x ~26 m
- thermal / radiators: **90 t** @ x ~35 m
- propulsion: **160 t** @ x ~46.5 m
- electrical: **55 t** @ x ~31 m
- planetary launch + associated vehicle allowance: **33 t** @ x ~21.8 m, z ~+5.2 m for a conservative trim check
- avionics / sensors / comms: **20 t** @ x ~12 m
- RCS / docking / service: **25 t** @ x ~28 m
- mission / courier systems: **20 t** @ x ~17 m
- explicit engineering reserve: **67.5 t** @ x ~28 m

Current computed center-of-mass results from the design ledger:

- docked dry CoM x approximately **27.99 m**;
- docked wet CoM x approximately **26.68 m**;
- launch lateral contribution approximately **z = +0.20 m dry** and **+0.15 m wet** before trim.

The Pixel viewer now exposes current wet/dry mass and wet CoM and can update them when the planetary launch is changed from DOCKED to ABSENT.

---

## 14. Relational/Loom-domain geometry calibration

Current calibrated values used for regression/visual engineering:

- normal controlled boundary target: approximately **1,900 m²**;
- extended mature-route target: approximately **2,430 m²**;
- normal effective patch target: **971**;
- boundary authority: **670**;
- distributed nodes: **208**.

The Phase-3 geometry compiler uses a deliberately simple surrogate: 57 x 9 m capped-cylinder enclosing area plus a launch-bay blister increment. Current result is approximately **1,821.6 m²**, within the ±10% working regression tolerance of the 1,900 m² normal target.

This is a **regression surrogate only**, not a literal Loom-domain solution. Physical radiator surface area is intentionally excluded. Controlled boundary area must never be interpreted as ordinary material skin area.

---

## 15. Configuration-state model

Current state vocabulary:

### Launch
- DOCKED
- EXTRACTING
- ABSENT

### Radiators
- STOWED
- DEPLOYING
- DEPLOYED

### Docking
- FREE
- APPROACH
- SOFT_CAPTURE
- HARD_DOCKED

### Torch
- OFF
- SAFE
- ACTIVE

A key engineering rule is that configuration changes are physically meaningful. Docking/attachment/domain membership changes can invalidate a committed flight/field solution and require recertification/recalculation.

---

## 16. Pixel Geometry Lab implementation

Current phone-native workflow runs locally on a Pixel using:

- Termux
- Python
- SQLite
- local HTTP server
- Chrome
- classic Three.js WebGL

Repository clone path currently used on Android shared storage:

`/storage/emulated/0/Documents/LOOM_GIT`

Termux path:

`~/storage/shared/Documents/LOOM_GIT`

Git shared-storage safety exception already required:

`git config --global --add safe.directory /storage/emulated/0/Documents/LOOM_GIT`

Normal update/run workflow:

```bash
cd ~/storage/shared/Documents/LOOM_GIT
git pull
python src/wayfarer_geometry_server.py
```

Viewer URL:

`http://127.0.0.1:8000/`

Do not use `/tmp/wayfarer.log` on the Pixel. If logging is needed, write a local repo log and remove it afterward.

---

## 17. Geometry Lab v0.2 current features

Current phone viewer capabilities:

- 3/4, side, top, front and aft views;
- orbit by pointer drag;
- wheel/pinch-compatible browser zoom behavior through the rendered camera implementation;
- launch state DOCKED / ABSENT;
- radiator state STOWED / DEPLOYED;
- OPEN-geometry visibility toggle;
- dismissible component metadata panel;
- close button on the metadata panel;
- tap empty scene to close metadata;
- tap the selected component again to close metadata;
- mobile-sized metadata panel;
- CUTAWAY mode;
- engineering ZONES overlay;
- 0-57 m axial station/ruler visualization;
- wet center-of-mass marker;
- current dry/wet mass display;
- state-dependent launch mass / CoM display;
- provenance-aware component information rather than relying on visual appearance;
- validation PASS/FAIL indicator.

The screenshot validated on the Pixel on 2026-09-06 shows Geometry Lab v0.2 successfully rendering the Wayfarer with CUTAWAY, ZONES, CoM and OPEN geometry active and the docked/stowed configuration. The displayed docked reference mass is 1,158.5 t wet / 858.5 t dry and wet CoM x ~26.68 m.

---

## 18. Current implementation file map

Core deterministic geometry:

- `geometry/wayfarer_geometry_seed.sql`
- `src/wayfarer_geometry.py`
- `src/wayfarer_geometry_server.py`
- generated local `geometry/wayfarer_geometry.json` at runtime

Pixel/browser viewer:

- `web/index.html`
- `web/viewer.js`
- cached local classic Three.js at `web/three/three.min.js` after bootstrap

Blender path:

- `src/wayfarer_blender_builder.py`

Tests:

- `tests/test_wayfarer_geometry.py`
- `tests/test_wayfarer_blender_builder.py`
- broader repository regression in `tests/test_loom_update.py`

Engineering documentation:

- `engineering/current/LOOM_2226_Wayfarer_3D_Geometry_and_Physical_Packaging_Plan_v0.1.md`
- `engineering/current/LOOM_2226_Wayfarer_Phase_3_Implementation_v0.1.md`
- this file
- companion canon-candidate specification

Relevant governing canon:

- `canon/current/LOOM_2226_CANON_II_Engineering_Ships_Operations_v2.4.md`
- `canon/current/LOOM_2226_CANON_II_Wayfarer_Schematic_Amendment_v2.4a.md`

Relevant archive/reference:

- `canon/archive/LOOM_2226_Ship_Operations_Courier_Canon_Compendium_v1.0.md`

Project-wide baseline/history:

- `docs/LOOM_PROJECT_HISTORY_ARCHITECTURE_PIXEL_BASELINE_2026-09-06.md`

---

## 19. Blender builder role

Blender is a desktop/laptop stage, not the Android runtime target.

The Blender builder is intentionally downstream of the same deterministic geometry payload used by the Pixel viewer. It should never become an independent geometric authority.

The intended split is:

- **Three.js / Pixel:** engineering inspection, configuration checks, state visualization, rapid geometry validation.
- **Blender / desktop:** higher-detail physical modeling, materials, lighting, cutaways, animation, surface treatment and reference rendering.

When geometry changes in SQL or the compiler, Blender should regenerate rather than require manual correction of a separate hand-built ship.

---

## 20. Visual design language to preserve during refinement

Reference imagery has converged on:

- blunt forward crew pressure/shielding body;
- off-white ceramic/composite armor language;
- meaningful small windows rather than a cockpit canopy;
- dense industrial midship machinery;
- exactly four tanks / four longerons / four major radiators;
- one dominant axial fusion torch and one magnetic nozzle;
- integrated semi-recessed launch bay;
- precision metrology / cryogenic / field-hardware appearance for the relational plant rather than magical or decorative effects;
- dark refractory radiator surfaces, not solar panels.

Avoid:

- atmospheric mothership wings;
- landing gear on the mothership;
- artificial-gravity ring;
- naval-hull styling;
- fighter-aircraft styling;
- decorative fins;
- extra main engines;
- ungrounded weapons or visible 'greeble for greeble's sake'.

---

## 21. Immediate safe engineering sequence after v0.2

Recommended next geometry sequence:

1. Separate pressure vessel from armor/MMOD shell.
2. Replace simple forward cylinder with a more realistic blunt/faceted armored pressure-hull envelope while preserving 57 m total length and current pressure-volume trial.
3. Replace tank cylinders with physically plausible tank shells/endcaps while keeping tank count, clocking and current envelope.
4. Refine integrated launch-bay blister and explicitly model door/clearance geometry as OPEN design-baseline elements.
5. Improve the four-longeron aft thrust cage and annular convergence structure.
6. Replace the primitive nozzle with visible magnetic-nozzle coil/support architecture while preserving one axial nozzle.
7. Begin radiator hinge/folding studies without promoting any one topology to canon until area, sweep, interference and thermal packaging close.
8. Add RCS station bands / dead-zone inspection, especially around launch extraction and radiator sweeps.
9. Add selected hull/internal-system visibility filters.
10. Later add relational-domain/configuration overlays tied to the current physical configuration rather than a static decorative bubble.

---

## 22. Known open questions

The following should remain explicitly unresolved until tested:

- exact pressure-hull contour;
- exact external armor/MMOD segmentation;
- exact tank head shape and tank-wall/insulation geometry;
- exact tank plumbing topology;
- exact relational-plant physical packaging within x ~18-34 m;
- exact radiator physical area and fold topology;
- exact radiator hinge and root mechanism;
- exact launch-bay door topology;
- exact launch aerodynamic form;
- exact launch atmospheric propulsion / landing arrangement;
- exact rover/ground-vehicle dimensions;
- exact docking collar diameter/details;
- exact RCS count/nozzle geometry;
- exact shadow-shield materials/layering;
- exact reactor internals;
- exact magnetic-nozzle coil geometry;
- exact thermal plumbing;
- exact torch plume envelope;
- exact hull exterior contour outside the now-frozen topology rules.

---

## 23. Preservation rule

This snapshot exists so the Wayfarer work can be reconstructed even if a chat thread is lost. New work should update the deterministic model and written engineering record before visual polishing. When a design-baseline choice becomes sufficiently defensible, promote it deliberately through the canon process rather than allowing it to become de facto canon because it appears in a render.
