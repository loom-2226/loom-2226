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

Dimensions used (metres): hull 12.8 x 3.8 biconic (resized v1, kT 2026-11-03,
the certified shuttle outline); Wayfarer bay bore 13.8 x 4.8; crew pod 2.5 OD,
3 crew; tip-jet rotor 12 diameter, four blades folding two
forward and two aft along the spine; water tank 23.1 t. Readout figures quote
the resized sizer reports (research/shuttle-v1-resize-20261103, PR #463) and
the PR #460 integration run (Wayfarer geometry 293a4e90).

Dependency: three.js r128 from cdnjs (MIT). Unlike `../loomgl.js`, it is not
vendored; porting to the in-repo renderer is a later option.

Stowed radial extent as drawn: every stowed part stays inside the 1.9 m hull
line (outer edges: intake ~1.88 m, hub ~1.87 m, belly nozzles ~1.85 m, folded
blades ~1.82 m, wheels ~1.81 m), so the drawing keeps the G8 0.5 m bay clearance. That holds only because the hub
and blades are drawn recessed in a spine groove with assumed sizes; real mast
and hub dimensions are unknown and G8 full fit stays OPEN.

Open items this model makes visible (see `wayfarer/lab/shuttle/OPEN_ITEMS.md`):
bay fit with mast and hub; forward blades lying over the tapered nose cone,
outside its surface though inside the 3.8 m cylinder line, with groove and
support not established; continuous blades drawn, while hold stowage assumes segmented
blades with hot-gas joints; mast drawn at mid-length, not at a computed CG;
door and ramp swept volume not checked; whether the belly heat shield is core
or part of the detachable kit; aft-face plume heating from the flush magnetic
nozzle.

Pixel check: kT loaded the published viewer on the Pixel on 2026-11-03
(all states loaded). Frame rate not measured.
