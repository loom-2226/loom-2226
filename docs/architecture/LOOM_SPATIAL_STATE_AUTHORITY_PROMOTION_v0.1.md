# LOOM Spatial-State Authority Promotion v0.1

**Class:** engineering

## Purpose

Promote only the reusable celestial-state authority needed by Navigator metric-domain routing from the qualified Navigation Physics / Earth-Luna lineage. This is deliberately not a merge of the old HUD branch or PR #103.

## Authority

`HybridCelestialStateService.resolve(entity_id, epoch_utc)` returns a typed physical state containing position, velocity, epoch, canonical frame, provenance, uncertainty and navigation-grade status.

Rules preserved from the source lineage:

- canonical inertial frame is `J2000/ECLIPTIC`;
- direct authoritative state is preferred;
- direct provider must return the requested body, epoch and canonical frame;
- declared parent-centric Kepler propagation is an explicit fallback;
- propagated fallback is always `navigation_grade=False` and carries provenance/uncertainty;
- missing bodies and parent cycles fail closed.

## Deliberate non-scope

- no HUD/GIS/presentation code;
- no Earth-Luna facility/orbit registry;
- no SQLite celestial adapter yet;
- no metric-domain radius policy;
- no route planning or detour solver;
- no campaign mutation;
- no Mara/LLM numerical authority.

## Next seam

After this authority is green and merged, promote/adapt the read-only SQLite celestial catalogue separately so production body states can hydrate metric-domain centers. The metric-domain checker merged in PR #118 then consumes those aligned moving centers without owning ephemeris.
