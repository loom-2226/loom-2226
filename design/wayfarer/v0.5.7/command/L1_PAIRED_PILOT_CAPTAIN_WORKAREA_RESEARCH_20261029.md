# Wayfarer L1 — paired Pilot/Commander elevated tier and independent mission workspace
**2026-10-29 | RESEARCH · NON-CANON · NON-RUNTIME · CONCEPT GEOMETRY ONLY**

## User-directed revision
Starting from the eight unconstrained command-deck families, revise F1 tiered command:

- **Pilot and Captain/Commander** are now side by side on a **shared raised two-seat level**. Each retains a distinct contoured acceleration work seat and primary display.
- **Navigator** moves to the **lower forward station**. This departs intentionally from the previous Pilot/NAV pair and should be exercised for actual pilot-navigation handoffs before preferred.
- **Engineering** and **Sensors/EW** remain distinct side specialists.
- The **original S4 Mission Ops position**, approximately plan Y=0, Z=-3m in F1, becomes a genuinely separate **anchored low-g mission work area**. It has a 1.35m-width workbench, local display, physical controls, handholds, foot restraints and equipment storage. It is not a seventh high-g seat.
- **S4 Mission Ops' acceleration seat** is relocated to the aft/right specialist wing, retaining **six occupied acceleration seats total**.
- The separate central command standing/anchored location remains available.
- Front/back/elevation is represented using the F1 conceptual ship-X stepped platforms. These are non-canon concept coordinates, not a measured fit in the source 8.6m pressure hull.

## Coordinates and evidence
The generator `render/make_l1_tier_command_pilot_captain_workarea.py` produces `command/L1_PAIRED_PILOT_CAPTAIN_STANDALONE_WORKAREA_20261029.json` and a standalone HTML view `render/out/wayfarer_l1_pilot_captain_raised_mission_workarea.html`.

Relevant illustrative base-x tier levels (metres):
- Pilot: **1.89**, Captain: **1.89** (same raised command tier)
- Navigator: **2.76** (lower flight level)
- Engineering 3.29, Sensors 3.29, Mission Ops 3.32 (specialist work areas)
- Independent mission bench at X=3.39, Y=0, Z=-3, replacing S4's former chair site.

The viewer contains a **before/after switch**, revised layout selected by default. The new workbench has its own visible geometry and label. A desktop Chromium WebGL render checked all six seats plus workbench with `gl.getError()=0`; the two versions produced different rendered image hashes on desktop and on **412px mobile browser emulation** with zero browser errors. This is a rendered mock-up, not a physical test.

## What this design gains and costs
Benefits: unambiguous Pilot/Commander paired command tier; Navigator still retains a dedicated flight/navigation position; mission work now has a genuine separate low-g area while six high-g seats remain; creates roles for both formal seated command and casual working/observation.

Open questions: the Pilot/NAV separation may hamper immediate collaboration; both raised seats' direct canopy sightlines and restricted physical reach must be checked; proposed multiple tier decks, pressure vessel fit, floor continuity/egress, acceleration vector and sustained 4g structural/load ergonomics remain **unverified**. The previous outer 37 transparent protection panels, inner double pressure domes and speculative optogel are optional overlays, not constraints applied to this layout.

## Authority
This is isolated research only. Source PR #432 (`3485830a56dfead79b2ef8bba031a595b536fbb5` at bootstrap), governing Rev 7, Technology Timeline, canon and runtime remain unchanged. **Do not claim the 3D view is buildable or qualified.**
