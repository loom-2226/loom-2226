# Wayfarer shuttle v1 viewer

`wayfarer_shuttle_v1_viewer.html` is a standalone, rotatable 3D concept model of
the Wayfarer planetary shuttle from the shuttle v1 research baseline
(`wayfarer/lab/shuttle/`, merged at `7c6b9b4`).

Status: **NON-CANON, representational only.** It does not consume or change
authoritative Wayfarer geometry, packaging inputs or the sizer. The internal
layout (pod, tank, torch, kit reactor, mast and blade stowage) is a notional
arrangement drawn from the sizer's dimensions, not a qualified design.

States: docked in the bay, Venus rotor flight, Venus landed with ground vent,
pod rover out, and Moon/Mars/polar Mercury on belly thrusters. View toggles:
cutaway, Venus kit fitted, labels, 1.8 m scale figure.

Dimensions used (metres): hull 12.8 x 4.3 biconic; Wayfarer bay bore 13.8 x
4.8; crew pod 2.8 OD; tip-jet rotor 12 diameter, four blades folding two
forward and two aft along the spine; water tank 23.1 t. Readout figures quote
the merged Stage 1-3 sizer reports.

Dependency: three.js r128 from cdnjs (MIT). Unlike `../loomgl.js`, it is not
vendored; porting to the in-repo renderer is a later option.

Open items this model makes visible (see `wayfarer/lab/shuttle/OPEN_ITEMS.md`):
bay fit with mast and hub; forward blades lying over the nose cone, outside
the hull line but inside the bay envelope; aft-face plume heating from the
flush magnetic nozzle.
