# LOOM Metric-Domain Routing Seam v0.1

**Class:** ENGINEERING
**Status:** narrow implementation seam; candidate domain-radius physics remains unselected.

## Decision

Keep the architecture small:

1. Ephemeris/navigation authority owns moving celestial-body state.
2. Domain policy is paired to body identity and defines whether a body/system is a `METRIC_ENTRY` domain or `LOCAL_ONLY` nested domain.
3. Navigator combines ephemeris state + selected domain policy to obtain moving exclusion geometry and routes metric flight around excluded domains.
4. Mara supplies semantic target/preferences only. Mara does not calculate boundaries, trajectories, collision checks, collapse points, or operating modes.
5. Physical exclusions are never overridable by player/model intent.
6. Regulatory exclusions are obeyed by default; an explicit override request may relax regulatory policy only. Navigator remains the authority that determines whether a route is physically admissible.

## Example

`EUROPA` resolves semantically to:

- requested/local target: `EUROPA`
- metric-entry domain: `JUPITER_SYSTEM`

Navigator then plans metric flight to the moving Jupiter-system boundary, avoiding every other applicable metric-exclusion domain, collapses at the qualified boundary state, and continues through ordinary-space/local navigation to Europa.

## Geometry contract

Do not persist copied boundary-center coordinates for Mara.

At epoch `t`:

`boundary(body,t) = ephemeris_position(body,t) + selected_domain_geometry(body)`

Candidate A/B/C radii remain diagnostic inputs until governed physics selects an active rule.

## Route legality

A candidate metric trajectory is admissible only when it does not intersect an applicable physical exclusion volume during the metric segment. Regulatory exclusions add policy constraints on top of physical admissibility.

This document does not specify the trajectory obstacle solver. It establishes the typed semantic seam required before that solver is added.
