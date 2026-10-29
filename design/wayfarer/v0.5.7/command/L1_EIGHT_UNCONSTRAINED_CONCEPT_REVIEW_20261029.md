# Wayfarer L1 — eight unrestricted command-deck concepts
**2026-10-29 · RESEARCH · NON-CANON · NON-RUNTIME · UNQUALIFIED**

## Design freedom authorized

This exploration **does not** impose source Rev 7 constraints for hull, ladders, flight-deck elevation, standing-station site, plan footprint, station ring, number of tiers, furniture orientation, controls, or canopy. The **only imposed continuity** is six crew-operating functions and six contoured acceleration-capable *concept* work seats:
Pilot, Navigator, Captain/Command, Engineering, Sensors/EW, and Mission Operations.

All concepts also sketch a **possible** anchored low-g standing command workpoint, but neither its existence nor location is a search-space constraint. The earlier 37-panel outer protection / seamless double pressure dome and optogel are optional *reference overlays* in the 3D viewer, not fit restrictions. The actual Wayfarer hull is **not** modeled as a constraint in these concepts.

**Axial reference:** Ship X points aft; the bow is toward -X. On these diagrams, a seat at a smaller X has its back mounting farther toward the bow. 'Behind' for the raised Captain in F1 means behind in the diagram's transverse YZ *crew configuration*, while 'elevated' is an X-level change. The final body/thrust direction and actual relation to a physically continuous deck need later resolution, not hand-waving. The 3D models illustrate layouts, not ergonomically qualified acceleration geometry.

## Eight authored concepts

| ID | Command-deck arrangement | What it optimizes for | Main trade-off |
|---|---|---|---|
| F1 | **Tiered command**: Pilot/NAV forward and lower, Captain centred behind and raised | Captain flight oversight with compact command trio | Captain sightlines and tier access need a real test |
| F2 | **Triangular cluster**: Pilot, NAV, Captain in close working triangle | Very rapid three-person coordination and shared guidance | Busy primary station cluster |
| F3 | **Horseshoe bridge**: all roles around an open command area | Everyone sees one another and shared information | Large lateral distances; less privileged Captain position |
| F4 | **Amphitheatre**: forward flight, middle Captain, further elevated specialists | Distinct tier hierarchy and access to common presentations | Multiple decks complicate mobility and structure |
| F5 | **Mission pods**: paired specialist groups | Independent engineering/mission workflows | Distributed attention and siloing |
| F6 | **Split-level bridge**: flight group separate from elevated command gallery | Spatial separation of specialized flight vs command work | Emergency movement between levels |
| F7 | **Central command well**: Captain at centre, flight/navigation spread out | Command-centric crew information flow | Pilot/NAV less coupled as a pair |
| F8 | **Panoramic observation arc**: distributed external-facing crescent | Direct human observation and sense of place | Command conversations across long span |

These are eight different **author-designed topologies** intended for visual comparison. No claim that an arbitrary optimiser discovered them. The previous 500-candidate numerical search was *one narrow seat-ring architecture* and is intentionally not used to choose among these unrestricted options.

## Visual model delivered

The self-contained WebGL2 file `render/out/wayfarer_l1_eight_unconstrained_3d.html` is a working interactive **research concept viewer**. It has:
- eight distinct selectable 3D layouts, each with six contoured, segmented Kazbek-style illustration seats and six associated screen/control volumes;
- **new authored multi-platform floor geometry for each design**, including visibly separate tiers, rather than a fixed source L1 mezzanine;
- visible comparative same-scale YZ floorplan thumbnails with individual station labels and X tier values;
- a physically represented, repositioned low-g standing workpoint;
- crew-eye / standing-eye / orbit cameras, plus a direct redraw on selection;
- historical source canopy research layers *off by default* and only optional for conceptual context.

Prior source L1 hull and ladder parts are intentionally not present. None of the eight concepts can claim physical fit into the existing 8.6m source hull or usable 4g seat protection until the selected arrangement is actually subjected to meaningful physical screening.

## What the first assessment supports

**Tentative shortlist: F1, F3, F6**, to preserve very different design philosophies:
- F1 is the user-suggested raised Captain behind the Pilot and Navigator;
- F3 keeps all six crew directly engaged in one shared work environment;
- F6 creates a true distinct command level above the immediate flight task.

This is **qualitative choice for exploration**, not a ranking established by task performance. In particular, **none** has yet been verified for prolonged 4g posture, six-person anthropometry and mounting, canopy sightlines, actual crew movement, ship integration, or scenario play. Those criteria become relevant after selection, not as retrospective restrictions on creativity.

## Reproduction and stop

`render/make_l1_unconstrained_8_concepts.py` regenerates both the data file `command/L1_EIGHT_FREEFORM_2226_CONCEPTS_20261029.json` and the interactive HTML. It extends the existing LOOM WebGL2 renderer as a standalone local file, without changing the renderer implementation, canonical geometry, Rev7, PR#432, canon, or runtime.

**Stop after authentic concept comparison.** Select a topology, then exercise actual crew-task and vehicle fit only if it makes a meaningful difference. No new simulator framework, giant scoring pipeline, or premature qualification apparatus.
