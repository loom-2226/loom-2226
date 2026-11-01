# Moving crown sector experiment: rigid hinged petal | 28 October 2026

**RESEARCH · NON-CANON · NON-RUNTIME · NON-GOVERNING · NOT CERTIFIED**

Source: live `loom-2226/loom-2226`, PR #432 source head `3485830a56dfead79b2ef8bba031a595b536fbb5`. All work isolated to `research/wayfarer-nose-l1-search-20261028`, with no modification of source Wayfarer coordinates, canon or runtime.

## Narrow objective

Construct and **move** one protective crown sector in real metre coordinates; compare precisely the same hinge concept on (1) Rev 7's original ellipsoidal nose and 2.8 m crown, (2) the +0.8 m / 35° / 3.2 m angular nose, and (3) the +1.2 m / 50° / 3.5 m angular nose.

**Mechanism tested:** a rigid protective petal comprising 1/16 of the full radial crown aperture, azimuthal width 22.5°, thickness equivalent to 27 g/cm² at the armour ledger's effective density (0.1963 m). The entire sector follows the original outer-ellipsoid or new flat/conical facet profile when closed. One straight hinge axis is tangent to the crown rim at the middle of the sector. A rotation is applied to 48 radius × 9 azimuth × 3 material-depth samples (1,296 panel-material points per angular step), every 5° from 0 to ±180°. The same rule is repeated visually 16 times in the standalone viewer.

The source actually declared **tambour slats on meridian tracks**, not rigid hinged petals. This is an *alternative* mechanism test, not evidence that its original tracks are solved.

## Tested obstacles

- Original ellipsoidal pressure head, continuing into the aft pressure cylinder.
- Fixed original or faceted exterior armour **outside the glazing aperture**.
- Original annular bow-sensor part, including the four 14° azimuthal gaps and its actual x/radial bounds.
- Sixteen ring-zero Metric-node faces in their original positions, screened as 0.35 m diameter spherical exclusion markers.

No sensor or Metric node was moved. The 0.35 m node face is not a complete node/mount/field clearance model.

## Results

| At −60° (forward-open) | Rev 7 | Compact angular | Panoramic angular |
|---|---:|---:|---:|
| Pressure / fixed armour / bow sensor / node sample collisions | 0 | **0** | **0** |
| Furthest radial extent | 2.83 m | **3.41 m** | **4.29 m** |
| Most forward petal coordinate x | −2.16 m | **−2.86 m** | **−3.33 m** |
| Pilot/NAV 60° cone directions directly intercepted by petal mesh | 1.34% / 1.34% | **0% / 0%** | **0% / 0%** |
| Within closed hull radius 4.5 m while open at this angle? | yes | **yes** | **yes** |
| Within +2.0 m forward-extension rule measured from the *original* bow x=0 while open? | **no** | **no** | **no** |

The cone occlusion computation is a second independent triangle/ray screen: 16 moving thin petal meshes and 224 test directions per Pilot/NAV eye. It is **direct petal obstruction only**; it does not include fixed frame, glazing obstruction or sensor effects already calculated in the prior L1 visibility study. Zero in that metric is not 100% complete operational visibility. Note the important distinction between *the ship's closed structural length* and its *forward protrusion when petals are deployed*. If the +2.0 m allowance applies to deployed mechanisms, −60° is **out of bounds for all three**.

**Aft-fold direction:** both angular noses first intersect the pressure/fixed armour envelope at approximately +15° (compact) or +15–20° (panoramic); the sensors enter the swept envelope later (first sampled contact +45° compact and +55° panoramic). The aft-fold rigid hinge does **not** provide retracting storage.

**Rev 7 zero-angle nuance:** with an idealised 0.1963 m *normal inward* slab attached exactly to the declared original exterior, the source ellipsoid registers some nominal pressure intersections at 0° and −5/−10°. This is an inconsistency between our simple armour-slab construction and the source's non-concentric, radially specified 0.20 m armour shell, not a demonstrated manufacturing failure of Rev 7. By −15° the forward sweep has no sampled pressure collisions.

**Angular forward opening:** both angular designs have no sampled pressure, armour, sensor or node collisions over the 0 to −90° tested arc, but beyond −60° the panoramic petals exceed the 4.5 m reference radius; compact petals exceed it by −90° (4.61 m).

## What this actually demonstrates

**A single-sector forward-opening hinged petal is kinematically promising, especially on the angular candidates, and it exposes a workable *open position* without requiring inward radial shutter storage.** It does not hide the armour: all 16 panels remain physically extended forward around the nose like a flower when the crown is exposed. This may be acceptable only in the already-declared low-speed/bow-out-of-dust operational condition. It is also visually and operationally different from the source's retractable tambour.

**Not yet demonstrated:** physical hinge brackets and torque, sealing at a curved ring, collision among neighbouring gores (the visual repeats identical panel paths but the collision screen tests one), full continuous swept-solid collision, closure impact resistance, debris spall, panel structural stiffness, motor failure, and forward visual obstruction from the real frame or fully reconstructed L1 deck. In particular, a straight tangential hinge at the middle of a curved 22.5° crown sector does not automatically mate every point of the curved rim without a bracket or compliant connection.

No mechanism has earned physical closure. That is the correct boundary of this experiment; avoid assigning a PASS to the entire nose.

## Reproduction / interactive viewing

- `command/l1_single_gore_sweep.py`: direct 3D sector movement and point sampled intersections; output `command/l1_single_gore_sweep_results.json`.
- `command/l1_gore_occlusion.py`: 16-part triangle ray interception of the Pilot/NAV forward 60° cone; output `command/l1_gore_occlusion_results.json`.
- `render/make_gore_motion_viewer.py`: produces self-contained `render/out/nose_gore_motion_viewer.html`. Open offline in an Android browser; select three noses, move angle from −90° to +90°, rotate/zoom, show/hide sensor/nodes, and read actual sampled obstacle counts.

**Stopping point:** a credible moving hypothesis exists, but its extended open envelope, hinge seals and inter-petal contacts remain the concrete blockers. No redesign of pressure hull, sensor ring or L1 stations is authorised by this result.
