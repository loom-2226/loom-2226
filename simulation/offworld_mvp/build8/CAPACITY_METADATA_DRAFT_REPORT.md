# Build 8 capacity metadata and opt-in authored defaults

Status: RESEARCH / NONCANON / NOT BASELINE 0. Change class: `class:engineering`.

- `capacity_tiers_descriptive.json` holds all 75 supplied actor/category rows with tier, original evidence-basis label, and note. Every tier is an **inference** even when the supporting historical observation is measured. Tier does **not** determine slots, price, selection, success, or failure.
- `capacity_authored_defaults.json` is a **separate, authored, OFF-BY-DEFAULT** file. Flat capacity fallback = **1 slot**. Quote fallback = **BUILD 1.70**, **LAND 3.00** model units. These are authored assumptions, not researched offers. LAUNCH deliberately has **no** price fallback because a compatible reference mission was not established; TRANSPORT/RUN/EXTRACT also have no price fallback.
- `capacity_options.py` exposes three independent switches: `tiers`, `slots`, `prices`, all false by default. The existing yearly driver accepts those switches. Tiers are audit-only. Slot and price fallbacks apply only when the respective authored input is absent. An explicit authored quote or slot always wins.
- Existing frozen yearly scenarios already supply BUILD and LAND prices and capacity. Thus toggling slots/prices on them **correctly does nothing**; it does not prove that defaults influence a new scenario. The resolver is separately tested with missing values. Tier-only mode emits descriptive audit events without altering transactions.
- No slot = tier assumption, no tier-based price, no launch pricing, no capacity-dependent failure probability, no cast-wide scheduling or selection changes.
- Baseline 0 has **not** been run. These switches are ready for isolated trials when a Baseline 0 scenario with missing authored inputs exists. Do not mistake these fallback numbers for measured firm capability.
- The original master cast and frozen baseline snapshots remain unchanged. Known CAST/Sierra and Chinese lander cast gaps are not silently repaired in this slice.
