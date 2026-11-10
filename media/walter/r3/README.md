# WALTER R3: 1:12 figure (Project Walter)

**Change class:** `class:asset-media`
**Authority status:** NON-CANON, purely visual and representational. It consumes and updates no authoritative engineering parameters.
**Approved by:** Kevin (kT), 10 Nov 2026, as the Project Walter R3 design (the AI design competition), with design review by Archer and Sol.

This is a printable physical figure and design concept for Walter, the crew's nonverbal utility robot.

- It does **not** amend `characters/current/**` or any canon.
- Walter remains nonverbal, as defined in the current character source.
- Capability figures are design estimates. They are not canon performance values.
- Any promotion to canon or engineering requires a Canon Change Request under `governance/current/LOOM_CHANGE_CONTROL_v1.0.md`.
- Wayfarer is unchanged. The design uses only Wayfarer's existing hull-crawler docks, attachment points, grapple fixtures and EVA rails.
- Character firewall (`characters/AGENTS.md`): this figure depicts the in-universe Walter character. It has no effect on the WALTER governance assurance agent.

Supporting research: the [Walter R2 Engineering Research Review](https://claude.ai/artifact/L2WuJDie1DtcLGdpTVFJnf) records the sources behind the R3 changes.

This is a 1:12 utility quadruped in an alert rest. The geometry is real and printable; the renders are traced from the same field the STL came from.

**Size:** L 100.6 × W 55.1 × H 58.3 mm. The real machine is about 1.2 m long folded. Mass is roughly 70–80 kg, estimated from the 0.115 m³ solid volume at 0.6–0.7 times the density of water. It follows the equipment rather than being a target.

## Design rationale

- **Chassis:** a machined box with chamfered long edges. It has bolted flank panels, a top access panel, small crew-safe edge radii and belly skids. The battery sits low in the centre with the compute beside it. There's no vault and no radiator fins: the skin radiates the heat.
- **Legs:** knees-back, as in R2, but each knee motor now lives in the hip stack and drives the knee through a visible pushrod. That keeps the legs light and puts the motor heat in the body, which matters in vacuum. The knees are slim pins with wear pads that carry the rest load.
- **Feet:** each foot is a two-jaw latching clamp on an active ankle, with a rubber sole for deck walking. For EVA the jaws close on rails and crawler attachment points. Folded flat, the two jaws read as toes.
- **Arm:** chassis-mounted and folded flat along the spine, between the handrails. The gripper carries a wrist camera and lights. It's the fifth anchor on the hull, using grapple fixtures and EVA rails. No manipulation load goes through the head.
- **Head:** a sensor pod (stereo cameras, lidar/thermal window, sun visor) on a light 3-axis gimbal mast. The mast height gives the navigation sensors a viewpoint over obstacles. The roll axis levels the cameras on curved hull and sloped decks.
- **Docked tail:** the tether fairlead boom. The tether has to leave the body clear of the hind legs, so it exits through a short articulated stub at the rear top, which also carries a rear camera and status lamp. Its angle tells you what he's doing: up for alert, flat for working, down for resting.
- **History:** the front-left shank is a later-batch replacement in bare titanium.

**How he talks without words:** through head pan, tilt and roll; tail angle; chassis pitch (sitting up versus flat); and where the arm is stowed. The pose shown has the rear de-loaded on its skids, the front lifted 5°, the head turned 30° and tilted 11°, and the tail up. That reads as: I'm comfortable, I've noticed you, go on.

## What changed from R2, and why

| R2 | R3 | Why |
|---|---|---|
| Rounded, organic hull | Chamfered box, bolted panels | Archer's critique; this is how flight hardware is actually built |
| Forward radiation vault | Removed; battery and compute low and central | The shielding was invented to make a silhouette |
| Dorsal radiator fins | Removed | The chassis skin can reject the heat |
| Gripper under the sensor head | Arm folded on the back, wrist camera | Keeps manipulation loads off the sensor neck |
| Big knee drums | Knee motor at the hip, pushrod | Lighter legs, and the heat goes to the body |
| Puck feet with microspines | Latching jaw feet, active ankles | Friction doesn't hold in microgravity; the feet need positive attachment |
| Heavy head on a short neck | Light gimbal head on a mast | It's sensors only now, and still expressive |
| No tail | Tether fairlead tail | Required by the brief, and earned by the tether |

**Kept from R2:** the knees-back layout, belly skids, handrails, the tether and the replacement shank.

**Magnets:** none modelled. Any magnetic capability would be an optional foot insert, used only on verified ferromagnetic structure.

## Print notes

- **Mesh checks:** 768,652 triangles, 1 shell, watertight, 0 non-manifold edges, 0 degenerate faces. STL, OBJ and GLB were each reloaded and checked.
- **Through-holes:** genus 10. These are the handrail, drag-handle, fairlead and linkage loops.
- **Orientation:** base down. About 640 mm² touches the plate (four soles, four knee pads, the rear skid), so it stands without a brim.
- **Supports:**
  - Under the head pod and the gripper fingers.
  - At the jaw-tip curls.
  - The belly between the skids is a short bridge of about 11 mm.
  - On FDM, use tree supports touching the plate only. On resin, 6–8 light supports.
- **Thin features:** less than 0.5% of the volume is under 0.8 mm (seams and fastener recesses). It suits a 0.4 mm nozzle at 0.12–0.16 mm layers. In resin, hollow it with a 2 mm wall and drain holes between the skids.

## Files

| Path | Contents |
|---|---|
| `models/Walter_R3_1-12.stl` | Print master: binary STL, mm, Z up |
| `models/Walter_R3_1-12.obj` + `.mtl` | Plain-text OBJ, mm, Z up, one group per material |
| `models/Walter_R3_1-12.glb` | Basic glTF 2.0: metres, Y up, one primitive per material, no extensions or compression |
| `models/SHA256SUMS` | Hashes of the four model files |
| `models/mesh_validation_report.json` | Machine-generated mesh checks (topology, overhangs, support islands, thin features, reload results) |
| `renders/` | Concept render, low view, rear view, dimensioned orthographic sheet |
| `source/` | Generator code: `sdf.py` (SDF kit), `model3.py` (the design), `build3.py` (voxel grid, cleanup, marching cubes), `export3.py` (validation and exports) |

**Regenerating:** with numpy, scipy and scikit-image installed, copy `source/` into an empty working directory, create `out3/`, then run `python3 build3.py` followed by `python3 export3.py`. `export3.py` also writes a colour 3MF (a zip container), which is not stored here.

**Verified 10 Nov 2026:** a clean rebuild from `source/` reproduced the STL, OBJ and GLB byte-for-byte, matching `SHA256SUMS`. Toolchain: Python 3.13.18, numpy 2.5.3, scipy 1.18.1, scikit-image 0.26.0. Other library versions may produce slightly different meshes.

Renders were made with a separate ray-marching renderer that isn't included. It reads the same voxel field that produced the STL.
