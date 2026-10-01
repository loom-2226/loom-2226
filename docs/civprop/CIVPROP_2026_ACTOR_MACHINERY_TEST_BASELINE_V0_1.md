# CIVPROP 2026 actor machinery-test baseline v0.1

Date: 2026-10-02. Class: `class:engineering`.
Status: **NON-CANON / MACHINERY TEST / NON-FINAL CALIBRATION**.

## Purpose

This fixture supplies the smallest heterogeneous actor population needed to test whether the existing CIVPROP physical/economic machinery can produce endogenous long-run activity from the 2026 Earth boundary. It is not a complete 2026 space-sector census, a forecast of institutional behavior, or a claim that the authored behavioral weights are empirical.

It extends, but does not replace, `CIVPROP_ACTOR_STATE_V1`. GAP-002 remains closed. Existing Actor State V1 rules continue to apply: actor budgets are not GDP, national capital stock or unscoped macro investment; capability/access remains scoped and evidence-backed; UNKNOWN is preserved.

Machine-readable fixture: `engineering/civprop/contracts/actor_machinery_test_baseline_v0_1.json`.

## Actor admission rule

Admit an organization when it gives the machinery test a materially distinct decision/capability path and there is 2026 evidence of relevant operational capability, development activity, or scoped procurement/access. Do not automatically promote all 80 modeled Earth economies into actors.

The v0.1 population contains 13 actors: NASA, CNSA, ESA, Roscosmos, ISRO, JAXA, SpaceX, Blue Origin, Rocket Lab, Firefly Aerospace, Intuitive Machines, Astrobotic and Isar Aerospace.

Public/multinational actors test state-supported and consortium-supported decisions. Commercial actors test revenue/capital feedback, procurement, provider competition and specialization. The set is intentionally incomplete.

## Country/economy linkage

Country is context, not actor identity.

```text
Earth economy/economies
        |
        v
support / market / member-contribution relationship
        |
        v
      actor
        |
        v
capacity -> available budget -> commitments -> projects
```

Public agencies link to their supporting Earth economy. ESA links to its 23 member economies as a multinational support basket; optional-programme participation is not inferred from membership alone. Commercial actors link to their principal economic/operational context but do not inherit national GDP, capital or investment.

For v0.1:
- NASA -> USA; CNSA -> CHN; Roscosmos -> RUS; ISRO -> IND; JAXA -> JPN.
- ESA -> its 23 current member states.
- SpaceX, Blue Origin, Firefly Aerospace, Intuitive Machines and Astrobotic -> USA.
- Isar Aerospace -> DEU.
- Rocket Lab -> USA and NZL, preserving corporate/economic and operational geography without implying national ownership.

## Budget/capacity semantics

Budget is a function of actor capacity, not a synonym for capacity.

```text
PUBLIC:
available_budget =
    public_support_capacity * allocation_rule
    - commitments
    - maintenance
    - replacement

MULTINATIONAL:
available_budget =
    sum(member_support_capacity * contribution_rule)
    - commitments
    - maintenance
    - replacement

COMMERCIAL:
available_budget =
    retained_actor_capacity
    + revenue
    + admitted_external_capital
    - commitments
    - operating_costs
    - maintenance
    - replacement
```

Maintenance, replacement and existing commitments are senior to discretionary growth investment. This intentionally connects GAP-013 lifecycle burden to future actor choice.

The v0.1 fixture does **not** invent comparable private-company budgets. Actual public appropriations may later seed actor allocations where scope/currency/base-year semantics are qualified. Macro GDP, capital, investment, market capitalization and private-company valuation are prohibited substitutes for spendable budget.

## Minimum behavioral variables

Only four authored behavioral weights are admitted:
- `investment_propensity`: willingness to allocate discretionary capacity to new CIVPROP opportunities.
- `risk_tolerance`: willingness to commit under modeled uncertainty.
- `exploration_weight`: relative weight on scientific/strategic/capability-building value.
- `commercial_weight`: relative weight on revenue/economic return.

Values are restricted initially to 0.25/0.50/0.75 (LOW/MEDIUM/HIGH). Every value is tagged `AUTHORED_MACHINERY_TEST_ASSUMPTION_V0_1`. They are sensitivity parameters, not empirical psychology.

Experience is not authored as a personality score. It is derived from run history. Successful and failed projects may both create experience; capability changes require explicit qualification/commissioning events.

## Initial behavior matrix

| Actor | Invest | Risk | Explore | Commercial |
|---|---:|---:|---:|---:|
| NASA | .75 | .50 | .75 | .25 |
| CNSA | .75 | .50 | .75 | .25 |
| ESA | .50 | .25 | .75 | .25 |
| Roscosmos | .50 | .50 | .50 | .25 |
| ISRO | .50 | .50 | .75 | .25 |
| JAXA | .50 | .25 | .75 | .25 |
| SpaceX | .75 | .75 | .50 | .75 |
| Blue Origin | .75 | .75 | .50 | .75 |
| Rocket Lab | .75 | .50 | .25 | .75 |
| Firefly Aerospace | .75 | .75 | .50 | .75 |
| Intuitive Machines | .75 | .75 | .50 | .75 |
| Astrobotic | .50 | .75 | .50 | .75 |
| Isar Aerospace | .75 | .75 | .25 | .75 |

## Capability vocabulary

The coarse machinery-test dimensions are `ORBITAL_LAUNCH`, `HEAVY_LAUNCH`, `CREWED_SPACEFLIGHT`, `SPACECRAFT_OPS`, `DEEP_SPACE`, `LUNAR_DELIVERY`, and `SURFACE_INFRASTRUCTURE`.

Cells use only `OPERATIONAL`, `DEVELOPMENT`, `ACCESS`, or `UNKNOWN`. These are v0.1 summary labels. They do not override the scoped USABLE/CONDITIONAL/UNUSABLE/UNKNOWN semantics of Actor State V1 at mission qualification time.

## Minimum interactions

Only four interaction mechanisms are required:
1. **BUY**: purchase a scoped service/capability. Resources transfer; only the contracted right transfers.
2. **PARTNER**: pool explicitly committed resources/capabilities for a project. Partnership does not transfer every capability.
3. **COMPETE**: independently pursue the same opportunity. No hostility/friendship score is needed.
4. **LEARN**: outcomes update experience; qualification/commissioning may change capability.

Seed edges are evidence-backed examples, not a complete alliance graph: NASA with SpaceX, Blue Origin, Firefly Aerospace, Intuitive Machines and Astrobotic; ESA with Isar Aerospace; JAXA with Rocket Lab. All other edges must arise from admitted access evidence or simulated transactions.

## Evidence anchors

Primary-source references establish the *kind* of capability/access used to seed the fixture; they do not validate the behavioral weights.

- NASA FY2026 budget/spending-plan materials: https://www.nasa.gov/fy-2026-budget-request/
- NASA HLS identifies SpaceX and Blue Origin as commercial lunar-lander development providers: https://www.nasa.gov/reference/human-landing-systems-2/
- NASA CLPS and provider material establishes commercial lunar-delivery relationships including Firefly, Intuitive Machines and Astrobotic: https://www.nasa.gov/reference/commercial-lunar-payload-services/ and https://www.nasa.gov/commercial-lunar-payload-services/clps-providers/
- ESA funding distinguishes mandatory GNP-linked contributions from optional programme participation: https://www.esa.int/About_Us/Corporate_news/Funding
- ESA's European Launcher Challenge establishes the commercial-launch procurement/support model and includes Isar Aerospace: https://www.esa.int/Enabling_Support/Space_Transportation/European_Launcher_Challenge
- ESA member-state list establishes the multinational membership basket: https://www.esa.int/content/view/full/481227
- ISRO 2025-26 annual reporting and 2026 Gaganyaan testing establish current programme/capability context: https://www.isro.gov.in/AnnualReports.html and https://www.isro.gov.in/ISRO_SOLVE.html
- Rocket Lab's launch record establishes operational Electron service and 2026 JAXA service: https://rocketlabcorp.com/missions/launches/
- Blue Origin documents operational New Glenn capability and lunar-development programmes: https://www.blueorigin.com/new-glenn
- Intuitive Machines documents lunar delivery, mobility, communications and infrastructure activity: https://www.intuitivemachines.com/missions/lunar
- ESA records Isar Aerospace reaching orbit with Spectrum on 5 September 2026: https://www.esa.int/Enabling_Support/Space_Transportation/Boost/Isar_Aerospace_achieves_first_launch_to_orbit_from_continental_Europe

CNSA, Roscosmos and some JAXA capability cells remain deliberately coarse in this machinery fixture. Before any claim of calibrated empirical actor state, each cell requires a bounded evidence packet under Actor State V1 rather than retrospective filling from general knowledge.

## Causal loop under test

```text
Earth economy
 -> actor support/capital/revenue
 -> actor capacity
 -> available budget
 -> decision
 -> mission/project
 -> facility
 -> power/transport/resources/production
 -> maintenance/replacement/lifecycle
 -> revenue/value/experience
 -> future actor capacity and capability
```

Actors choose and transact. Existing CIVPROP systems determine physical and economic consequences. Energy, transport, resources, production, maintenance and lifecycle are systems, not actors. A future utility, carrier or maintenance company may become an actor only if organizational agency itself matters.

## Deliberate omissions

v0.1 has no ideology, geopolitics score, sanctions model, election cycle, public-opinion model, generic alliance bonus, war model, organizational birth/death, merger model or actor mortality. It also does not force LOOM timeline/canon events.

These omissions are deliberate experimental controls, not claims that the omitted mechanisms are unimportant.

## Acceptance test

The first long-run actor experiment should:
1. start from the qualified 2026 Earth authority and this actor fixture;
2. make no hand-authored future project awards or forced canon events;
3. preserve deterministic replay for a fixed seed;
4. allow BUY/PARTNER/COMPETE/LEARN to alter future feasible choices;
5. charge maintenance/replacement before discretionary growth;
6. preserve UNKNOWN instead of inventing access/capability/budget;
7. run through 2226 without assistant intervention; and
8. sweep the four behavior weights across multiple seeds to identify parameter fragility.

Success is not matching a preferred 2226 future. Success is a causal, inspectable propagation in which projects, failures, partnerships, infrastructure and capability evolution arise from governed inputs and rules.

## Known limitations / next tuning

This baseline is intentionally non-exhaustive. Capability dimensions are coarse; public budget mappings are not yet normalized to CIVPROP project units; commercial finance is underdetermined; ESA optional-programme contribution structure is simplified; CNSA/Roscosmos organizational boundaries are simplified; and the initial actor population is held fixed for the machinery test.

If small changes to authored behavior weights dominate long-run outcomes, calibrate or replace those rules before treating the actor layer as explanatory. If physical/economic thresholds dominate across broad behavior sweeps, that robustness is itself a useful result.
