# LOOM Metric-Domain Routing Sequence v0.1

**Primary class:** RUNTIME  
**Base:** merged metric-domain seam from PR #117.  
**Scope:** prepare deterministic traffic-aware routing without choosing metric-radius physics or building detours.

## Sequence implemented

1. Preserve ephemeris/navigation authority for moving domain geometry.
2. Allow an authorized origin-domain transition on the first metric leg only.
3. Allow an authorized destination-domain transition on the final metric leg only.
4. Check every leg of a multi-segment metric route.
5. Return deterministic blocker diagnostics: domain, exclusion class, leg index, closest fraction/epoch, minimum distance, and clearance.

These exemptions do not permit arbitrary traversal. Encountering the origin later in the route or the destination before the final leg remains a blocker.

## Still deliberately absent

- no A/B/C candidate radius selected;
- no copied boundary centers or ephemeris in Mara;
- no new ephemeris implementation;
- no automatic detour generation;
- no HUD/UI changes;
- no campaign mutation;
- no LLM calculation or state authority.

## Next bounded seam

Hydrate aligned `MovingDomainSegment` values from the authoritative ephemeris/body-domain provider. Once that provider is real, a simple detour generator can consume blocker diagnostics, propose a small number of bypass waypoints, and re-use this exact checker to qualify them.
