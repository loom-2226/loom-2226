# LOOM CIVSTATE HEL Allocator v2 Design Contract v0.1

**Class:** ENGINEERING DESIGN / NON-MUTATING  
**Scope:** heliocentric infrastructure materialization only  
**Database mutation authority:** ZERO

## Problem earned by qualification

Qualified audits #140–#144 established that several distinct HEL infrastructure subjects became broad state twins across governance, influence, infrastructure, texture, place DNA, social state/pressure, and transport. The duplication is therefore not a texture-only defect. At the same time, the full ten-node HEL set retains meaningful variation in infrastructure, ownership/operator, influence, social and texture state.

This contract defines what a replacement allocator may and may not use before any row mutation is attempted.

## Locked constraints

### A20 — conservation
All lower-resolution population, workforce and economic allocations must conserve against parent totals; residual economy may remain outside named infrastructure.

Hard-conserved allocator outputs:
- resident population;
- workforce;
- annual value added;
- capital stock;
- replacement value.

Operational quantities such as power, capacity, cargo, passengers and ship calls are preserve-by-default quantities. Changing their parent aggregate requires a separately qualified derivation.

### A08 — orthogonality
Resident population, economic throughput and strategic importance remain separate quantities. Allocator v2 may not collapse them into one generic importance score.

## Admissible upstream structural drivers

The first design pass may inspect only stored structural fields with a plausible upstream relationship to allocation:
- governance primary owner/operator;
- corporate proxy governance;
- influence actor, domain, weight, control class and basis;
- census-zone identity/basis code where it carries actual structural distinction.

Variation is evidence, not automatic causal authority. Coefficients still require separate qualification.

## Forbidden circular inputs

The allocator may not use its own downstream behavioral/texture consequences as causal inputs:
- `civ_node_texture_overlay`;
- `civ_place_dna`;
- `civ_social_pressure`;
- `civ_social_state`.

These layers may be regenerated or evaluated after allocation, but cannot be used to justify the allocation that creates them.

## Forbidden shortcuts

- no display-name/NLP role inference;
- no random jitter;
- no cosmetic uniqueness target;
- no forced difference between nodes whose authoritative upstream drivers are identical;
- no invented coefficients;
- no silent absorption of parent residuals into named nodes.

## Normalization boundary

Any future score or weighting system must normalize only within an explicitly identified parent allocation pool. Global Solar normalization is not assumed. Every output difference must be traceable to stored upstream differences and a qualified deterministic rule.

## Acceptance tests for an implementation PR

1. Parent hard totals conserved to explicit numeric tolerance.
2. Parent residual accounting preserved.
3. A08 population/throughput/strategic separation preserved.
4. No display-name or random-jitter dependency.
5. No downstream texture/place/social feedback used as allocator input.
6. Deterministic replay from identical authoritative inputs yields identical outputs.
7. Distinct outputs require traceable upstream-driver differences.
8. Identical outputs remain legal when authoritative drivers are identical.
9. Every new allocation carries derivation/provenance metadata.
10. Existing qualified baseline can be reproduced or compared before promotion.

## Current evidence boundary

The previously duplicate HEL pairs shared full influence signatures and broad state envelopes. The design probe must therefore explicitly test whether the currently admissible upstream structural drivers can distinguish those pairs. If they cannot, allocator v2 must report insufficient differentiation and stop rather than infer function from names.

## Next qualification

Qualify upstream-driver coverage and identify the exact parent allocation pool(s) and conserved totals before implementing any reallocation logic.
