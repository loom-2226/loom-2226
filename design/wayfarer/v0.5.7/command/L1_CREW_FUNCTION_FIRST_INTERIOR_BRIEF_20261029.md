# Wayfarer L1 — crew-function-first interior brief
**2026-10-29 · RESEARCH / NON-CANON / NON-RUNTIME · FUNCTIONAL DESIGN SEED, NOT GOVERNING GEOMETRY**

## Authority and what is actually fixed

Authoritative repository: `loom-2226/loom-2226` PR #432, source head `3485830a56dfead79b2ef8bba031a595b536fbb5` at review. The existing v0.5.7 Rev 7 `SPEC.md` and `render/out/l1_scene.json` are NON-GOVERNING design materials. They establish six normal crew, six L1 couches (Pilot and NAV on the raised front deck; four supports around the rim), two ladderways, displays, bow sensors, and acceleration doctrine of 4g sustained / 5g structural design. `STAND` in the 3D viewer is only an eye/camera preset, not an actual workstation.

Prior LOOM Ship Building and Piloting v0.2 doctrine distinguishes *minimum operational*, *normal*, and *surge* crew. It calls for physical captain/flight, engineering, tactical/mission, damage-control authority; expertise in pilot, engineering, medicine, sensors/EW, astrogation/Loom, mission work, with overlap. Foundational Canon v1.2 makes crew persistent people with judgment, legal/personhood boundaries and the ability to disagree. These sources do NOT dictate exactly six titles or permanently assigned crew names.

**Design intent:** Fully equipped L1 as a working command/watch space, not six sleeping couches pointed at a window.

## Primary mission functions, NOT yet personnel assignments

| Functional domain | What the operator must actually do | Needed L1 interface |
|---|---|---|
| Flight handling | Attitude, docking, thrust-vector/flight-envelope control, manual abort/degraded modes | Pilot primary controls; direct vehicle state; limited-time physical fallback |
| Navigation / Loom | Route choice, state estimation uncertainty, reachability, Metric/Loom readiness/sequence and abort | Navigator path/uncertainty displays, validated plan review, independent cross-check with Pilot |
| Command / authority | Authorise burns/translations, accept mission risk, prioritize alarms, coordinate crew, contracts and decisions | Captain station with shared mission timeline and authorization controls; movable standing work point for normal coast |
| Engineering / damage control | Reactor, torch/remass/thermal, power and cooling, hull/pressure integrity and repair triage | Engineering condition and fault-isolation screen, access to procedure/diagnostic detail, local damage-control authority |
| Sensors / communications / EW | Contacts, passive/active sensing, emissions, external communications, identity and uncertainty | Sensor fusion and signal intelligence screen, contact history, emissions controls and evidence provenance |
| Mission operations | Shuttle/drones, EVA, landing/inspection work, mission science/sampling, cargo and specialist coordination | Payload/robotics screens, field team coordination, telemetry, task timelines |
| Medical / life support (cross-qualified) | Crew condition, environmental alarms, casualty response, wellbeing | Accessible alarm/triage access from command and engineering; the actual medical facility remains L4 |

Six full-time crew does NOT mean seven permanent roles; medical/damage control and other skills overlap. Normal watch may involve fewer than six active bridge operators. Synthetic/automation assistance does not replace human command and lawful authorization.

## Operating situations to fit

1. **Low-g coast / routine watch:** one or a few operators active, other crew working elsewhere. Captain can *stand/anchor* at a shared station for collaboration, briefings and viewing the panorama.
2. **Approach, docking, sensors/mission work:** Flight + NAV together with sensors and mission operator as needed; captain oversees decisions.
3. **Sustained torch acceleration to 4g:** ALL SIX personnel who remain on L1 are restrained in proper acceleration couches; standing station vacated and secured. Critical control remains reachable with restrained hands.
4. **Metric/Loom transition or emergency:** Cockpit supports independent flight/Nav verification, explicit authorization, engineering/thermal/condition monitoring, communications; rapid seat access and casualty/ladderway egress.

The captain need not personally occupy the central standing console during every operation. This is a **secondary work location**, not a seventh crash-rated occupant position.

## Chair correction: Soyuz/Kazbek *principle*, not an antique literal copy

Replace current straight **2.1m full-body box-like couches** with compact **contoured, semi-supine shell seats**: fitted/removable individual inserts; back/head/hip/thigh support; **bent knees and raised, supported feet**; harness; left/right hand controls where needed; structural acceleration load path into deck and hull. Seat shape must orient the body's supported back to the **effective aftward acceleration load** during forward torch thrust rather than carrying 4g primarily through the spine/feet. These seats are **workstations**, not sleep berths, and are adaptable to a population rather than individually inaccessible.

Reference real Kazbek-U Soyuz couches: custom-molded liners and shock-absorbing frames, see Smithsonian [Kazbek-U couch liner](https://www.si.edu/object/nasm_A19970070000) and [National Space Centre Kazbek-U](https://www.spacecentre.co.uk/collections/categories/space-oddities/kazbek-u-shock-absorbing-couch/). NASA [Orion crew seats](https://www.nasa.gov/reference/crew-systems/) demonstrate modern adjustable seats/restraints, reach and work postures. Do not pretend historical chair geometry itself is certified for Wayfarer's 4g prolonged burn.

## Standing workstation: build one, not a ceremonial lectern

A real **central/aft working location** near Pilot/NAV and the four other functions, out of main paths to both ladders. It should provide:
- foot restraints + handholds appropriate to microgravity, and a supportive lean/perch for ordinary low-g operation;
- shared status/map/navigation wall or floating display and physical/tactile urgent controls;
- ability for command and navigation staff to collaborate face-to-face, without large opaque console surfaces blocking the canopy;
- immediate safe stow/securing before sustained high-g operations.

A person under steady 4g does NOT stand to command the bridge. At zero-g "standing" means foot restraint or tethered anchored pose, not gravity carrying body weight.

## What to design next (bounded)

First make a **functional L1 arrangement** rather than a sweeping redesign:
- Keep source L1 hull, six crew, flight deck, two exits and bow sensors.
- Keep held **37 separate outer protective tiles + two seamless inner pressure domes + optogel** as NON-CANON visual canopy candidate, not yet pressure qualified or timeline-authoritative.
- Replace only couch geometry and local display/control mounts, add one real tethered standing workstation and shared mission/engineering/status surfaces.
- Score practical use in a **Ceres → Neptune approach scenario**: reachability restrained and at standing watch, glance angles and neck motion, shared display sightlines, ladderway egress, interference, canopy obstruction and exact positions.
- Stop when all six functions can be worked in normal flight, and all six crew can be secured for high-g operations, with one walkable/anchorable captain work point. Do not add a seventh seat, duplicate control rooms or a broad software architecture without observed need.

**Disposition:** This brief is a proposal for the next 3D furniture pass, NOT a claim the current rendered L1 already contains the station or six realistic seats. No source PR, governing geometry, ship runtime or canon is changed.
