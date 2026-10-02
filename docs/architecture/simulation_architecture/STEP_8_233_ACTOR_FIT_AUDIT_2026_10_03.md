# Step 8 — 233 Actor Fit Audit

**NON_CANON / PRE-INTEGRATION DESIGN REVIEW**

Candidate seed SHA-256: `9c8d3d39282240ac02e9b7b6cd4b7015c2446c88a6f2fe376e6835726028f82a`

## Executive finding

The roster is structurally valuable but is not a drop-in expansion of the current mission actor loop. All 233 candidates have UNKNOWN budgets and NON_CANON candidate authority. The safe integration model is adaptive, event-driven activation by institutional role. Only actors touched by a causal opportunity, relationship, contract, service, claim, policy, or information event should be promoted into active runtime state.

Loading 233 identities is cheap. Running all 233 through every annual characterization opportunity is both semantically wrong and computationally wasteful.

## Category fit

| Category | N | Fit | Engine type | Lag | Required treatment |
|---|---:|---|---|---|---|
| CAPITAL | 23 | NEW_ROLE | FINANCER | L2 | Needs financing/hurdle/reserve/mandate lane; must not become mission actor. |
| OFFTAKER | 14 | NEW_ROLE | INDUSTRIAL_BUYER | L1 | Needs procurement/offtake contract lane; demand/spec/price/window are distinct from mission EV. |
| INSURER | 11 | NEW_ROLE | ASSURER | L2 | Needs underwriting/risk-capacity lane; can gate transactions without owning mission. |
| CARRIER | 18 | PARTIAL | TRANSPORT_OPERATOR | L0 | Fits transport/service lane conceptually; should offer capacity, not evaluate science missions. |
| REGISTRY | 17 | NEW_ROLE | LEGAL_AUTHORITY | L3 | Needs legal/title/license/ruling state transitions and jurisdiction. |
| STATE | 12 | NEW_ROLE | STATE | L3 | Needs policy/budget/legal constraint events; category contract explicitly says never directly operate missions. |
| SETTLEMENT_LABOR | 10 | NEW_ROLE | COMMUNITY_OR_LABOR | L1 | Needs population/labor/governance interface; current migration lane is machinery-control only. |
| INFORMATION | 19 | NEW_ROLE | BROKER_OR_INTELLIGENCE | L1 | Needs belief transmission/sale/leak channels and lag; existing knowledge transmission is a useful primitive. |
| PROSPECTOR | 10 | PARTIAL | COMMERCIAL_OPERATOR | L0 | Closest direct fit to mission/opportunity machinery; still needs funding/carrier/insurance/buyer/title gates. |
| INCUMBENT_INDUSTRY | 22 | PARTIAL | INDUSTRIAL_INCUMBENT | L2 | Can own projects/facilities and transact; entry/partnership/acquisition logic is missing. |
| SUPPLIER_PRIME | 21 | PARTIAL | PRIME_OR_SUPPLIER | L1 | Fits project/provider transactions; needs funded-demand/bid/qualification adapter. |
| INFRASTRUCTURE | 18 | PARTIAL | SHARED_SERVICE_PROVIDER | L1 | Fits facility/service capacity and outage events; needs service-contract adapter. |
| SOFT_POWER | 13 | NEW_ROLE | STANDARDS_OR_ADVOCACY | L2 | Needs publication/adoption/credibility influence; cannot fund missions. |
| CERTIFICATION | 25 | PARTIAL | CERTIFIER_OR_CODE_BODY | L3 | Certification boundary exists; needs claim/evidence workflow and explicit jurisdictional authority before causal use. |

## Seed integrity and qualification

- 233 unique actor IDs and 233 unique names across 14 categories.
- Category counts: CAPITAL=23, OFFTAKER=14, INSURER=11, CARRIER=18, REGISTRY=17, STATE=12, SETTLEMENT_LABOR=10, INFORMATION=19, PROSPECTOR=10, INCUMBENT_INDUSTRY=22, SUPPLIER_PRIME=21, INFRASTRUCTURE=18, SOFT_POWER=13, CERTIFICATION=25.
- Confidence labels: HIGH=163, MEDIUM=70. Confidence is metadata, not authority.
- 52 rows carry verified_by_search=true; 181 do not. Search verification does not promote candidate authority.
- 73 actor rows carry an explicit verify note.
- 16 rows are terrestrial analogs; they must never silently become off-world institutions.
- 2 prospectors are explicitly HISTORICAL; 1 certification row is PROPOSAL_NOT_ADOPTED.
- All category budgets are UNKNOWN. None may commit funds until an independent budget/financing authority exists.
- 56 candidate relation edges span 47 relation kinds. 73 actors touch at least one edge; 160 are isolated in the seed graph.
- Relation confidence is HIGH=36, MEDIUM=14, LOW=6; 8 edges carry verify notes. Candidate edges are not legal/financial/information authority.

## Current compiler lossiness

The existing group_actor_integration_v0_3 compiler intentionally preserves only identity/category/type/lag/budget-status/confidence/search-verification. It currently drops fields that matter for adaptive execution: basis_2026 and narrative hook/twist on all 233 rows; 73 verify notes; 16 analog flags; 11 actor-specific decline additions; 6 lag overrides; 3 existing-actor links; 3 status_2026 values; 2 note_2026 values; and 2 seed_as historical-precedent markers. This was acceptable for Phase-10 compilation qualification but is not sufficient for production Step 8.

## Expected behavior if wired safely

At initial load all 233 identities should remain dormant candidate institutions. UNKNOWN budgets remain non-spendable. Candidate relationships do not activate actors by themselves. Most actors should do nothing in most years.

A causal trigger should select the smallest relevant neighborhood and promote only those actors into the resolution level required by the event. Examples: a resource characterization opportunity can activate prospectors plus reachable carriers/funders/insurers/offtakers/certifiers; a service outage activates the provider and affected contractual customers; a certification request activates only the claimant, competent/certifying authority and evidence chain; a policy event activates the relevant state/registry neighborhood. Actors demote after consequences and provenance are recorded.

With the current Step-7.7 authority state, merely loading the 233 should still produce almost no commitments. That is expected. The roster supplies potential agency and institutional heterogeneity, not free budgets, capability, transport or investment thresholds.

## Required improvements before full 233 run

1. **Replace the one-size mission actor loop with role-dispatched event interfaces.** Keep mission evaluation for genuine mission operators/prospectors only; add typed financing, procurement/offtake, underwriting, carrier/service, registry/policy, certification, information, supplier/project and labor/community interactions.
2. **Compile the full execution-relevant seed semantics.** Preserve analog/historical/proposal status, lag overrides, actor-specific decline codes, existing-actor links and verification/provenance metadata. Narrative hook/twist can remain presentation-only.
3. **Introduce an explicit activation state machine.** DORMANT_CANDIDATE -> RELEVANT -> ACTIVE_LIGHT -> ACTIVE_TRANSACTIONAL, with deterministic demotion. Candidate identity alone grants no action authority.
4. **Use relation edges only as scoped discovery hints until separately qualified.** Relation kind needs typed semantics: ownership is not information flow; investment is not spendable budget; membership is not certification authority; jurisdiction candidate is not license.
5. **Separate actor existence from actor authority.** A real 2026 institution can exist in the graph while every consequential fact set remains UNKNOWN. This matches the Step-7.6 purge discipline.
6. **Add institutional lifecycle events.** Historical/proposal rows must start inactive; mergers, acquisitions, splits, failures and successor identities require explicit events rather than 2026 identities persisting automatically to 2226.
7. **Do not materialize 233 x 344 x 201 disposition rows.** Adaptive activation plus compact reason summaries should preserve observability without creating roughly 16.1 million annual characterization records.
8. **Make belief lag operational only through declared channels.** L0-L3 are ordinal labels today, not durations. Do not invent year delays until a governed mapping exists.
9. **Preserve the Step-7.7 control as an ablation target.** Expansion-off must reproduce its exact causal result. Expansion-on with no earned actor authority should differ only in candidate/activation observability, not physical history.
10. **Qualify by category before the full ensemble.** Run hostile vertical slices for one representative actor/category, then mixed neighborhoods, then all 233. A single 200-year all-actor run is a poor debugging instrument.

## Recommended Step 8 sequence

8.0 durable candidate seed + schema/authority validation (this audit establishes the starting point). 8.1 adaptive actor registry and activation state. 8.2 preserve full seed semantics and typed relation discovery. 8.3 category adapters, starting with PROSPECTOR/CARRIER/CAPITAL/OFFTAKER/INSURER because together they can form a bounded commercial mission chain. 8.4 certification/registry/information gates. 8.5 supplier/infrastructure/incumbent project chain. 8.6 state and settlement/labor interfaces. 8.7 mixed-neighborhood closed-loop qualification. 8.8 full 233 load with expansion-off ablation and expansion-on deterministic replay.

## Hard acceptance conditions

- No global 233-actor annual heartbeat.
- No actor spends with UNKNOWN budget.
- No candidate relation grants authority merely by existing.
- No technology access follows from category or calendar date.
- No dormant actor emits decisions.
- Activation is deterministic and causally attributable.
- Expansion-off reproduces Step 7.7.
- Expansion-on preserves UNKNOWN rather than inventing behavior parameters.
- Physical consequences require the same transaction/project/service gates already qualified before Step 8.
- Hybrid remains reference-only and executes zero production path code.
