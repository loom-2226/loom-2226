# LOOM 2226 — Wayfarer 3D Geometry and Physical Packaging Plan v0.1

**Status:** ACTIVE ENGINEERING WORK PLAN / NON-GOVERNING EXCEPT WHERE REFERENCED TO CURRENT CANON  
**Platform target:** Pixel / Termux / local browser WebGL  
**Geometry authority:** deterministic parameter model; generated imagery is visual reference only

## 1. Objective

Build a deterministic, inspectable 3D model of the reference courier Wayfarer from canon and explicitly tagged engineering decisions. The model shall separate `CANON`, `DESIGN_BASELINE`, `DERIVED`, and `OPEN` variables and shall not infer topology from AI-generated images.

Primary phone workflow:

```text
GitHub repository
  -> Termux
  -> Python + SQLite / JSON geometry compiler
  -> local HTTP server
  -> Chrome / Three.js WebGL viewer
```

The same parameter schema should remain usable later by desktop CadQuery / Blender tooling without changing geometry authority.

## 2. Locked reference-courier schematic grammar

- ~57 m mothership overall length; ~9 m nominal main-body diameter.
- Four axial longerons.
- Four major working-fluid/remass tanks in quadrature.
- Four major deployable radiator assemblies in quadrature.
- One primary axial fusion-torch / magnetic-nozzle system.
- Cylindrical/rounded pressure vessel inside separate faceted protective armor.
- Dedicated atmospheric courier launch carried in a semi-recessed, unpressurized launch bay integrated into the primary structure.
- Launch bay is substantially enclosed/protected when stowed; it is not a large pressurized hangar.
- One standard mothership docking collar remains independent of the launch bay.
- Fundamental engineering remains thrust-axis symmetric; mission hardware may introduce controlled asymmetry.

## 3. Phase 2 — physical packaging

### Phase 2A — axial skeleton

Current design-baseline station map:

| X station | Primary function | Status |
|---|---|---|
| 0.0–14.0 m | Forward inhabited pressure-hull complex | LEGACY-COMPATIBLE / DESIGN |
| 14.0–18.0 m | Aft pressure bulkhead, transfer/service transition | DERIVED |
| 18.0–32.0 m | Four major tanks + distributed relational plant + central technical core | DERIVED |
| 32.0–38.0 m | Thermal machinery / four radiator roots and manifold | DERIVED |
| 38.0–43.0 m | Shield / propulsion-isolation region | DERIVED |
| 43.0–50.0 m | Reactor / torch machinery / thrust frame | DERIVED |
| 50.0–57.0 m | Magnetic-nozzle / torch structure | DERIVED |

Additional reservations:

```text
COURIER LAUNCH BAY:       x ~= 16–28 m, one side, exact geometry OPEN
RELATIONAL PLANT:         principal distributed envelope x ~= 18–34 m
RADIATOR ROOT REGION:     x ~= 33–38 m, fourfold quadrature
```

The x=16–28 m launch reservation is now an **integrated semi-recessed bay reservation**, not an external sidecar hardpoint. The launch is modeled as `DOCKED` or `ABSENT`; its carried mass and attachment state must feed CoM and relational-domain calculations when those are implemented.

Phase 2A does **not** yet freeze exact cross-sections, tank dimensions, radiator dimensions, launch dimensions, docking-collar location, or final CoM. Those are downstream closures.

### Phase 2B — forward pressure hull and armor

Solve the 0–14 m inhabited pressure vessel and separate protective armor envelope together with deck stack, net habitable volume, shielding annulus, windows, circulation, life support and launch-transfer interface. Preserve multiple protected human-scale windows without turning the bow into an aircraft cockpit.

### Phase 2C — four-tank geometry and inventory closure

Determine the four major tank envelopes around the central structural/technical core. Preserve the governing 300 t working-fluid/water inventory and 250 t normal remass relationship without assuming all 300 t occupy four identical ambient-water tanks. Distinguish major tanks from smaller header/reserve/conditioning volumes.

### Phase 2D — machinery and mission systems

Place the distributed ~88 t relational plant, thermal machinery, four radiator assemblies and deployment arcs, shield/isolation zone, reactor/thrust frame, torch/nozzle, integrated courier launch bay, standard docking collar, RCS and restrained sensor/comms hardware. Check mechanical interference and access.

### Phase 2E — deterministic geometry payload

Generate `wayfarer_geometry.json` from SQLite / parameter records. Every geometry-driving value carries provenance and units. Geometry consumers do not hard-code duplicated dimensional constants.

### Phase 2F — Pixel viewer

Serve the model from Termux to a local Three.js viewer in Chrome. Required first viewer capabilities:

- orbit / pan / zoom;
- fixed side/top/front/aft/three-quarter views;
- component visibility toggles;
- radiator `STOWED / DEPLOYED`;
- courier launch `DOCKED / ABSENT`;
- component metadata inspection;
- provenance debug display;
- local/offline Three.js dependency;
- deterministic regeneration after parameter changes.

## 4. Pixel / Termux workflow

```text
cd ~/loom-2226
git pull
python src/wayfarer_geometry_server.py
# open http://127.0.0.1:8000 in Chrome
```

After inspection and approved changes:

```text
git status
git add .
git commit -m "Update Wayfarer geometry"
git push
```

Platform-specific launch helpers are allowed, but the geometry compiler and schema should remain platform-neutral.

## 5. Current engineering rule

Interior and exterior packaging are solved together. If a geometry choice creates a real tradeoff in crew volume, mass distribution, shielding, access, thermal deployment, launch operations or relational-domain configuration, do not silently optimize it away. Surface the tradeoff and resolve it explicitly before promotion.
