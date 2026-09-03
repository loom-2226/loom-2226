# LOOM 2226 — SOLAR-CIVPROP Next-Thread Seed v1.2
## Historical Civilizational Propagation, Economic Geography, Workforce, Traffic, and Ephemeris Coupling

**Status:** Planning / architecture handoff, revised v1.2. Non-canon. Does not alter governing LOOM canon or the production WORLD database.

**Prepared:** 2026-08-30

**Revision v1.2:** Integrates the scaffolding work plan, calibration/PRR governance, fit-vs-identification reporting, capital-continuity correction, macro-to-node allocation contract, institutional boundary state, regional background state, and node-tier preregistration controls developed during architecture review.

**Purpose:** Seed the next dedicated modeling thread with the complete working direction agreed in the Solar GIS thread. The next thread should turn the existing scattered LOOM demographic, economic, traffic, technology, institutional, and propagation work into one defensible, reproducible 2026→2226 civilizational simulation architecture.

---

# 1. Freeze point before modeling work

The Solar GIS should be frozen **before** the experimental historical-propagation schema work.

## Frozen production candidate

- Source build: `LOOM_Solar_GIS_v0.12.0_RC9_Context_Fast_Stats_Pixel.py`
- Frozen copy: `LOOM_Solar_GIS_v0.12.0_FROZEN_PRE_CIVPROP_Pixel.py`
- SQLite schema: **12**
- SHA-256: `99e628b471bd78eda64096d9f1d2d2def636a7e23ed808caa665faf4c0bbf9a9`
- Frozen copy is byte-for-byte identical to RC9.
- Revalidated before handoff with Python compile and deterministic `--demo --scene-out` build.

## Experimental build NOT to promote/run against production yet

- `LOOM_Solar_GIS_v0.13.0_RC1_Historical_Propagation_Foundation_Pixel.py`
- SQLite schema: 13 experimental spike
- This spike demonstrated useful concepts but its schema is **not yet adequate for the full model** and it contains some older economic assumptions as current historical anchors that should instead be retained as superseded model lineage.

**Decision:** Do **not** migrate the live WORLD DB to schema 13 from that spike. Redesign schema 13 properly first.

---

# 2. Why this model is being built

The GIS has become a strong visualization and exploration environment. It now exposes:

- physically grounded Solar geometry;
- planets, moons, infrastructure, and selected small bodies;
- 127 canonical major infrastructure nodes;
- institutional/authority narratives;
- place-level narratives;
- political actor profiles;
- generic relationship highlighting (corporations, authorities, blocs, etc.);
- relationship-type filtering;
- qualitative TRAFFIC overlay;
- quantitative POPULATION overlay;
- population bio/synthetic composition;
- contextual fast statistics;
- physical scale/light-time ladder;
- enriched Atlas content.

The next problem is no longer map presentation. It is **derivation**.

LOOM has accumulated many independently developed quantitative and procedural models for:

- population;
- age/cohort demography;
- migration;
- Luna and Mars settlement trajectories;
- habitat capacity;
- remote and asynchronous workforce;
- recognized synthetic persons;
- energy demand;
- automation/task share;
- workweek/labor assumptions;
- traffic/order-of-magnitude freight;
- passenger/commercial accessibility;
- metric fleet/Mc constraints;
- political/corporate/security influence propagation;
- technology thresholds;
- orbital accessibility;
- institutional morphology;
- strategic materials;
- shipbuilding and industrial geography.

The goal is to **consolidate these into one reproducible civilizational engine** that can explain how the 2226 world could emerge from 2026, while preserving canon as constraints rather than secretly hard-coding every endpoint.

Long-term visualization goal:

> Start at 2026, press PLAY, and watch the Solar civilization emerge: orbital industry, Luna, Mars, the Belt, outer-system settlements, institutions, traffic, corporations, technology diffusion, fleet growth, Metric mobility, and finally Loom — all while planets and destinations move on physically correct ephemerides.

A second, separate long-term visualization should eventually show **model lineage**: how LOOM’s own models evolved, which values were superseded, and why.

---

# 3. Core modeling philosophy

## 3.1 This is a constrained generative reconstruction, not a literal 200-year forecast

We know some 2026 facts empirically. We know some 2226 facts because they are governing canon. We know some chronology thresholds because canon explicitly fixes them.

Therefore the simulator should support two distinct modes:

### Forward mode
Start with 2026 observations and physical/technology assumptions, propagate forward, and observe what 2226 emerges.

### Canon-reconciliation mode
Treat selected 2226 canon facts as hard or soft calibration targets and search for plausible parameter combinations that reproduce them without violating:

- conservation;
- physics;
- chronology;
- resource constraints;
- demographic plausibility;
- capital construction lead times;
- transport constraints;
- institutional constraints.

This gives a strong test of canon itself:

> If reaching canon repeatedly requires implausible fertility, migration, habitat construction, automation, resource, energy, or transport assumptions, the model should flag the canon target for review rather than silently distort the simulator.

## 3.2 Do not optimize history

Do not assume a globally rational planner optimizes civilization. History must remain:

- path-dependent;
- politically fragmented;
- institutionally constrained;
- imperfectly informed;
- locally rational;
- vulnerable to shocks;
- sometimes inefficient.

Optimization models are useful for engineering subproblems and capacity-expansion benchmarks, but not as the master theory of history.

## 3.3 Do not agent-model eight billion people

Use aggregated/cohort/choice models Solar-wide. Reserve agent-based or discrete-event detail for local systems where it adds value, such as:

- Earth–Luna traffic;
- busy ports;
- queues;
- route congestion;
- emergency/recovery operations.

## 3.4 Do not reduce everything to system dynamics either

Stock-flow feedback is essential, but LOOM also needs:

- real spatial geography;
- real ephemerides;
- trade networks;
- institutional actors;
- ownership;
- jurisdiction;
- technology-specific engineering constraints.

## 3.5 Preferred hybrid architecture

> **Stock-flow macro model + cohort demography + multiregional input-output economy + discrete-choice migration/industrial location + time-dependent orbital transport network + selective ABM/discrete-event simulation.**

---

# 4. Ephemeris must be first-class

A key new requirement is that economic geography be tied to **actual moving Solar geometry**.

The simulation should not store a fixed Earth→Mars distance and use it for 200 years.

## 4.1 Physical clock

For every relevant celestial/spatial node `i` at time `t`:

\[
E_i(t) = [\mathbf r_i(t), \mathbf v_i(t)]
\]

Use the existing LOOM/JPL state-vector authority model: epoch, target, observer, frame, aberration setting, position, velocity, provenance, coverage, propagation status.

The backend supplies geometry. The browser never invents orbital mechanics.

## 4.2 Accessibility is the bridge between ephemeris and civilization

Ephemeris should affect society **through accessibility and transport cost**, not directly through arbitrary population multipliers.

For origin `i`, destination `j`, mode/ship `m`:

\[
T_{ijm}(t) = F(E_i(t), E_j(t), ship_m, terminal\ geometry, traffic\ state)
\]

Eventually Navigator should supply this route solution.

Generalized transport cost:

\[
C_{ijm}(t) = p_{direct} + v_tT_{ijm}(t) + p_{risk} + p_{cert} + p_{inventory} + p_{unreliability} + p_{legal} + p_{info}
\]

This is intentionally broader than distance or cruise time.

## 4.3 Civil-year accessibility statistics

Population and capital do not need daily integration. For each civil year `y`, derive accessibility summaries from the continuously moving geometry:

\[
A_{ijm,y} = \{median(C), P10(C), P90(C), min(C), window\ frequency, window\ duration, variance\}
\]

This captures economic differences between:

- consistently accessible routes;
- routes with periodic excellent windows;
- routes with rare high-value windows;
- metric routes where classical orbital distance matters differently;
- routes dominated by terminal/certification/access constraints.

## 4.4 Civilizational clock

Initial macro timestep: **annual**.

\[
X_{y+1} = F(X_y, A_y, \Theta_y, \epsilon_y)
\]

where:

- `X_y` = civilization state;
- `A_y` = ephemeris-derived accessibility;
- `Θ_y` = technology/institutional parameters;
- `ε_y` = shocks/stochastic processes.

For smooth GIS playback at fractional years, interpolate continuous annual state variables while treating discrete commissioning/events correctly. Planet positions remain physically correct for the exact displayed epoch.

---

# 5. Existing LOOM work that must be inventoried and preserved

The next thread should begin with a **formal model inventory**, not new equations from scratch.

Important existing sources/modules include:

- Governing CANON I/II/III v2.4 set.
- Current Technical Paper Series v1.0.
- Earth/Solar System Canon Atlas v3.2.
- Earlier Solar System demographic/audit models.
- Lunar propagation model(s), including capacity/transients/remote workforce.
- Mars propagation model(s), including local and asynchronous workforce.
- Earth-orbit annual propagation work.
- Technology-epoch indices / chronology.
- Political/corporate/security propagation model.
- TRAFFIC-OOM traffic work.
- ACCESS-COMM passenger/commercial accessibility work.
- Master/relational hull and metric fleet work where still governing.
- Economic red-team / workweek / automation / energy sensitivity calculations.
- Strategic materials and industrial geography.
- Institution/organization register and current CANON I consolidation.
- Current 127-node infrastructure/jurisdiction registry.
- Current Solar GIS SQLite schema-12 data.

Important known lineage issue:

- Earlier economic calibration around ~9.9B biological population, ~4.5–5.0B labor force, ~84% machine-executable task share, ~19.6-hour paid workweek, and ~46.5 TW electrical demand was useful work but is **superseded as the current endpoint**.
- Current promoted biological population: **8,571,824,600**.
- Current promoted recognized synthetic persons: **214,068,429**.
- Current working civilization electricity estimate is closer to **~66.8 TW**, but remains provisional/non-canon.
- Current machine-executable task-hour range: **82–90%, central ~86%**, provisional.
- Mature-Earth paid workweek: **20–24 h, central ~22 h**, provisional.
- Labor-income share and reproducible basket cost remain provisional.

Do not delete old models. Store them as historical/superseded model runs with provenance.

---

# 6. Core mathematical modules

The following modules should be designed explicitly, with inputs, equations, outputs, uncertainty, calibration role, and provenance.

## 6.1 Biological demography

Use cohort-component demography rather than a single population-growth coefficient.

For region `r`, cohort age `a`:

\[
P_{r,a+1,t+1} = P_{r,a,t}(1-q_{r,a,t}) + M_{r,a,t}
\]

Births:

\[
B_{r,t} = \sum_a f_{r,a,t} P^F_{r,a,t}
\]

Migration must be source-debited/conserved:

\[
\sum_r M_{r,a,t} = 0
\]

apart from births/deaths/other explicitly modeled stock changes.

Key variables:

- age-specific fertility;
- age-specific mortality;
- longevity/rejuvenation availability and adoption;
- reproductive lifespan;
- ectogenesis access/cost;
- desired family size;
- family-support policy;
- cohort health;
- migration propensity;
- travel cost/accessibility;
- family-capable habitat capacity;
- institutional/cultural settlement attractiveness.

## 6.2 Recognized synthetic-person demography

Synthetic persons are persons/labor, **not automation capital**.

\[
S_{r,t+1} = S_{r,t} + I_{r,t} - R_{r,t} + M^S_{r,t}
\]

Potential drivers:

- compute availability;
- substrate production;
- power/cooling;
- legal-recognition regime;
- individuation rate;
- migration rights;
- retirement/death/divergence/reconciliation;
- replication restrictions;
- local skill demand;
- cultural preferences.

Keep non-person automation in a separate machine-task stock.

## 6.3 Habitat / settlement capital

Off-Earth population must be capital constrained.

\[
K^H_{r,t+1} = (1-\delta_H)K^H_{r,t} + I^H_{r,t-L}
\]

with construction/commissioning lag `L`.

Do not reduce habitat capacity to one number only. Track where feasible:

- pressure-rated capacity;
- family-capable capacity;
- surface vs artificial-g capacity;
- shielding;
- habitable volume;
- power;
- thermal rejection;
- water/volatile reserves;
- food/recycling capacity;
- medical capability;
- emergency margin;
- industrial vs residential capacity.

Hard constraint:

\[
P_{r,t} \le K^{hab}_{r,t}
\]

## 6.4 Workforce

Headcount alone is inadequate.

Biological labor supply:

\[
L^H_{r,t} = \sum_a P_{r,a,t} p^{participation}_{r,a,t} h_{r,a,t}
\]

Synthetic-person labor:

\[
L^S_{r,t}
\]

Non-person machine task capacity:

\[
M_{r,t}
\]

Distinguish:

- resident workers;
- physically present rotational workers;
- remote synchronous workers;
- remote asynchronous workers;
- synthetic-person workers;
- non-person automated task-hours.

For organizations, store both person headcount and annual paid person-hours. A 2226 "FTE" based on a 2026 workweek will be misleading.

Earlier Luna work is particularly important because it showed effective remote workforce can greatly exceed resident workforce.

## 6.5 Production / reduced input-output economy

Do not start by inventing GDP.

Initial reduced sector set:

1. energy
2. bulk materials
3. precision materials
4. compute
5. habitats
6. ships
7. medicine
8. transport
9. certification/metrology
10. services

Input-output identity:

\[
\mathbf x = A\mathbf x + \mathbf f
\]

or

\[
\mathbf x = (I-A)^{-1}\mathbf f
\]

Use hard/Leontief-like bottlenecks for genuinely non-substitutable engineering inputs, and CES-style substitution only where physically plausible.

Example:

\[
Y_{r,s} = \min\left[\frac{E}{a_E}, \frac{B}{a_B}, \frac{P}{a_P}, F(K,L_H,L_S,M)\right]
\]

This prevents a model from substituting AI for missing structural material, reactor capacity, radiator area, or certified Mc hardware.

## 6.6 Capital accumulation

\[
K_{r,k,t+1} = (1-\delta_k)K_{r,k,t} + I_{r,k,t}
\]

Separate capital classes:

- habitat;
- industrial/machine;
- robotic;
- shipyard;
- fleet;
- energy;
- compute;
- metrology/certification;
- medical;
- relational/Mc;
- route-information/communications capital where useful.

Path dependence should emerge from accumulated capital rather than narrative fiat.

## 6.7 Technology diffusion

Technology needs more than a binary invention year.

Track:

- invention/discovery;
- technical readiness;
- reliability;
- capital cost;
- operating cost;
- regulatory acceptance;
- manufacturing capacity;
- learning-by-doing;
- geographic diffusion;
- prerequisite infrastructure;
- installed base.

Adoption curve can begin with logistic forms:

\[
s(t) = \frac{1}{1+e^{-k(t-t_{50})}}
\]

Learning curve:

\[
c(Q) = c_0\left(\frac{Q}{Q_0}\right)^{-b}
\]

Torch/Metric/Loom should change underlying mechanisms, not directly multiply outcomes.

### Torch
Changes:

- travel time;
- freight cost;
- reliability;
- rescue geometry;
- inventory requirements;
- capital accessibility;
- viable settlement geography.

### Metric
Primarily changes generalized cost for:

- urgency;
- people;
- command;
- high-value cargo;

while remaining constrained by:

- fleet size;
- Mc availability;
- certification;
- terminal/environment rules;
- capital cost.

It does not replace torch bulk logistics by fiat.

### Loom
Arrives too late to be the first-order cause of the mature 2226 Solar population. It should strongly affect information/strategic topology after its emergence, but its demographic first-order weight at 2226 should remain low unless later canon changes.

## 6.8 Energy

Track by region/sector:

- installed capacity by technology;
- firm capacity;
- utilization/capacity factor;
- storage;
- delivered electricity;
- direct process heat;
- industrial heat;
- propulsion energy separately;
- compute/cooling demand;
- habitat life-support demand;
- industrial demand;
- losses;
- reserve margin.

Do not accept a single top-down TW figure without sector construction.

## 6.9 Resource geography

For resource/material `m`:

\[
R_{r,m,t} = recoverable\ stock
\]

Track:

- reserve/resource distinction;
- grade;
- extraction energy;
- purification requirements;
- depletion;
- recycling;
- substitution;
- transport cost;
- certification constraints;
- strategic/political restrictions.

High-value LOOM resources include:

- water/reaction mass;
- bulk structural feedstock;
- precision materials;
- isotopes;
- helium-3 if retained;
- Mc-299m;
- compute substrates;
- biological inputs.

Resource presence should not automatically create industrial dominance; it interacts with access, capital, institutions, skill, energy, and certification.

## 6.10 Migration / settlement choice

Use discrete-choice/location utility rather than deterministic migration shares.

\[
P(r\mid h) = \frac{e^{V_{hr}}}{\sum_j e^{V_{hj}}}
\]

Example utility:

\[
V_{hr} = \beta_1 jobs + \beta_2 wages - \beta_3 housing\ cost - \beta_4 travel\ cost + \beta_5 family\ capacity + \beta_6 amenities + \beta_7 safety + \beta_8 institutions + \beta_9 gravity/health + \dots
\]

Potential settlement variables:

- jobs/wages;
- habitat cost/availability;
- accessibility to family/home;
- family suitability;
- gravity/health burden;
- environmental hazard;
- political/legal rights;
- culture/amenities;
- education/healthcare;
- institutional stability;
- migration incentives;
- career specialization.

## 6.11 Firm / industrial location choice

\[
P(r\mid s) \propto e^{\gamma_1 A_r + \gamma_2 G_r + \gamma_3 R_r + \gamma_4 L_r + \gamma_5 I_r - \gamma_6 C_r - \gamma_7 H_r}
\]

where:

- `A` accessibility;
- `G` agglomeration/supplier networks;
- `R` resources;
- `L` labor/skills;
- `I` institutions/certification;
- `C` operating/transport cost;
- `H` hazard.

This should help produce Asteria/Axiom/etc. geography rather than simply hard-coding all locations forever. Canon locations remain calibration/constraint targets.

## 6.12 Origin-destination demand

For commodity/mission sector `s`:

\[
D_{ij,s,t} = F(Y_i,Y_j,IO_{ij},P_i,P_j,C_{ij},inventory,institutions)
\]

A gravity-style first approximation is acceptable:

\[
D_{ij} \propto M_i^\alpha M_j^\beta e^{-\lambda C_{ij}}
\]

but the target is freight/passenger demand generated from economic and demographic state.

## 6.13 Mode choice

Torch / Metric / Loom choice:

\[
P(m\mid i,j,s) = \frac{e^{-\mu_s C_{ijm}}}{\sum_k e^{-\mu_s C_{ijk}}}
\]

This should naturally produce:

- bulk cargo preference for torch;
- increased metric share for urgent/high-value cargo/people;
- scarce metric capacity due to Mc/fleet/certification constraints.

Governing derivation order should remain:

> demographics/industry → OD demand → generalized cost/mode choice → fleet/Mc constraints → route assignment → port/corridor capacity → queues/disruption/accessibility.

Never tune propulsion backwards to obtain desired traffic density.

## 6.14 Fleet stock

\[
F_{c,r,t+1} = (1-\delta_c)F_{c,r,t} + B_{c,r,t} - L_{c,r,t}
\]

Fleet construction constrained by:

- yard capacity;
- materials;
- energy;
- capital;
- skilled labor;
- Mc inventory;
- certification/metrology capacity;
- demand/utilization.

## 6.15 Ports and queues

First approximation can use utilization/queue models:

\[
\rho = \lambda/\mu
\]

Queue delay should rise sharply near capacity.

Later use discrete-event simulation for high-value systems (especially Earth–Luna) while preserving coarse aggregation elsewhere.

---

# 7. Variables to explicitly add to the register

External research and LOOM review identified several variables that are easy to omit but materially change outcomes.

## Construction lead time
Capital cannot appear instantly when demand rises.

## Capital depreciation / maintenance
Habitats, yards, fleets, reactors, radiators, and compute infrastructure age.

## Capacity utilization
Installed capacity and actually used capacity are different.

## Inventory / safety stock
Important for routes with long/variable transit and interruption risk.

## Reliability / recovery time
Mean travel time is not enough; variance and disruption matter economically.

## Learning-by-doing
Yards, Mc handling, certification, habitat construction, and propulsion should improve with cumulative experience.

## Skilled-labor pools
At least distinguish:

- general services;
- industrial trades;
- engineering;
- medical;
- scientific;
- metrology/certification;
- high-risk operations;
- governance/security.

## Remote-work latency
Earth–Moon telepresence and Earth–Saturn asynchronous work are not equivalent.

## Family-capable habitat capacity
Transient labor population is not the same as a self-reproducing society.

## Age structure
Same total population can imply radically different labor/fertility futures.

## Ownership
Production geography and household welfare diverge if capital ownership diverges.

## Fixed-location rent
Energy abundance does not eliminate scarcity of:

- desirable Earth land;
- orbital slots;
- high-value transfer geometry;
- certified yards;
- strategic anchorage locations;
- limited habitats with preferred gravity/environment.

## Institutional transaction cost
Investment/flow should respond to:

- certification delay;
- insurance;
- contract enforceability;
- legal burden;
- authority reliability;
- security risk.

## Information age / staleness
LOOM has no magical independent FTL communications.

\[
a_I = t_{local} - t_{source}
\]

Price, legal, command, scientific, and engineering information can have economic age/staleness costs.

## Shocks
Need a general event/shock mechanism for:

- war/security disruption;
- epidemic;
- habitat accident;
- industrial loss;
- resource discovery;
- resource depletion surprise;
- Mc production shock;
- route closure;
- political restriction;
- fertility-policy shift;
- technology breakthrough;
- major corporate/institutional failure.

Do not add shocks for drama; add them because resilience and path dependence are part of economic geography.

---

# 8. Outside simulation frameworks researched and what to borrow

The previous thread reviewed these mature frameworks. The new thread should revisit primary documentation as needed rather than treating this summary as source authority.

## UN World Population Prospects / cohort-component demography
Borrow:

- cohort fertility;
- mortality;
- migration;
- probabilistic parameter ranges.

## World3 / system dynamics
Borrow:

- stocks and flows;
- feedback;
- delay;
- overshoot;
- path dependence.

Do not borrow overly aggregated global geography.

## GCAM
Borrow:

- modular coupled sector structure;
- dynamic-recursive evolution;
- energy/resource/economy feedback.

## MESSAGEix
Borrow:

- technology lifetimes;
- installed capacity;
- investment;
- technical constraints;
- capacity expansion.

## REMIND
Borrow:

- learning-by-doing;
- capital/technology path dependence;
- trade/investment insights.

Do not make a global social planner the master historical actor.

## UrbanSim
Highly relevant for:

- households/jobs/development;
- accessibility-sensitive migration;
- annual location choice;
- development responding to demand/capacity.

## MATSim
Use selectively for:

- agent-based local route choice;
- congestion;
- detailed busy-system transport.

Do not simulate every Solar citizen as an agent.

## GTAP / OECD ICIO
Borrow:

- multiregional input-output structure;
- production/consumption/investment/trade linkage.

## MIT SpaceNet
Especially relevant.

Borrow:

- time-dependent space logistics networks;
- moving orbital nodes;
- dynamically feasible transport edges;
- inventories;
- supply interruption;
- consumption/degradation;
- time-expanded network thinking.

## NASA SPICE / JPL Horizons
Use for:

- authoritative time-dependent geometry;
- state vectors;
- ephemeris coverage/provenance.

## NASA Equivalent System Mass / human-systems engineering
Borrow the principle that space settlement capacity is multidimensional:

- mass;
- volume;
- power;
- cooling;
- crew time;
- logistics.

## Bayesian calibration / model discrepancy / hindcasting
Borrow:

- parameter uncertainty;
- model discrepancy;
- posterior ensembles;
- holdout validation;
- hindcasting against observed history.

## IEA / learning curves
Borrow:

- cumulative-experience cost reductions;
- lock-in/path dependence;
- explicit technology learning assumptions.

---

# 9. Validation strategy

A defensible simulator must not merely reproduce its calibration targets.

## 9.1 Use ensembles

For uncertain parameter vector `θ`:

\[
\theta \sim p(\theta)
\]

Run ensembles rather than one magic scenario.

## 9.2 Calibration hierarchy

Calibrate against:

1. empirical 2026 observations;
2. observed historical data where available;
3. canon chronology constraints;
4. selected promoted 2226 canon targets.

Reserve some values as **validation holdouts**.

If every 2226 value is used to tune the model, matching 2226 proves almost nothing.

## 9.3 Hindcasting

Before trusting 2180 outputs, test Earth modules historically.

Example:

- initialize 1980 or 2000;
- feed known historical exogenous technology/policy conditions;
- see whether demography, energy, labor, and capital modules broadly reproduce 2026.

Failure to reproduce recent history should lower confidence in far-future precision.

## 9.4 Conservation tests

At minimum:

- biological population source-debited migration;
- synthetic-person stock reconciliation;
- mass/material accounting where modeled;
- energy accounting;
- capital stock accumulation/depreciation;
- fleet stock accounting;
- Mc production/inventory/use accounting;
- trade flow balancing where applicable.

## 9.5 Causal integrity tests

Examples:

- Loom cannot cause mature 2180 population.
- Traffic cannot drive propulsion calibration backwards.
- A facility cannot employ more physical workers than plausible housing/rotation/transport allows without remote labor accounting.
- A settlement cannot exceed family-capable capacity without an explicit transient/rotational explanation.
- Synthetic persons cannot be silently counted as machine capital.

---

# 10. Epistemic, control, and calibration schema

Every numerical record must know both **what kind of knowledge it represents** and **how the simulator is allowed to treat it**.

These are separate axes.

## 10.1 Epistemic role

Recommended controlled vocabulary:

- `OBSERVED`
- `PHYSICAL_CONSTANT`
- `CANON_ASSERTED`
- `CANON_HARD_CONSTRAINT`
- `CANON_SOFT_TARGET`
- `VALIDATION_HOLDOUT`
- `EMPIRICAL_PRIOR`
- `MODEL_DERIVED`
- `SUPERSEDED`
- `PROVISIONAL`
- `DERIVED_CANON`

## 10.2 Control / mutability class

Recommended controlled vocabulary:

- `FIXED`
- `UNCERTAIN_EXOGENOUS`
- `SCENARIO_CONTROLLED`
- `CALIBRATION_ELIGIBLE`
- `MODEL_DISCREPANCY`
- `ENDOGENOUS_OUTPUT`

A physical constant and a canon assertion may both be fixed for a run, but they are **not epistemically equivalent**. Likewise, an observed 2026 value and a model-derived 2226 value may share units but must never share authority merely because both live in SQLite.

Every important value should additionally carry, directly or through provenance/run linkage:

```text
value
unit
uncertainty / scenario envelope where applicable
source / provenance
model_version
run_id
status / promotion state
```

Unclassified parameters default to the restrictive state: they cannot silently become calibration knobs.

---

# 11. Bitemporal/model-lineage requirement

The DB needs **two different notions of time/history**.

## In-universe simulation time

`sim_time`: 2026→2226 and possibly earlier for hindcasting.

## LOOM model-development lineage

`model_version` / `run_id` / promotion status.

Example:

- 2226 Lunar population = 11.72M, from older propagation model, superseded.
- 2226 Lunar population = 14.96M, from later promoted conserving model.

Both should remain queryable, with no ambiguity about which is current canon.

This enables eventual visualization of:

### WORLD HISTORY
How the fictional Solar civilization develops over time.

### MODEL LINEAGE
How LOOM’s own numerical model evolved over real development time.

---

# 12. Proposed schema-13 direction

Do not implement this blindly; review it first against the model inventory and the contracts below.

RC1's generic `historical_metrics` concept can survive as a reporting/audit layer, but the simulation engine should use typed state/flow tables.

## Provenance / run spine

```text
model_versions
simulation_scenarios
simulation_runs
simulation_parameters
simulation_constraints
calibration_targets
provenance_sources
model_dependencies
parameter_reclassification_requests
review_sessions
```

## Physical / ephemeris layer

```text
ephemeris_state
ephemeris_accessibility
route_solution_cache
```

## Demographic layer

```text
demographic_cohorts
demographic_flows
migration_flows
synthetic_population_state
synthetic_population_flows
```

## Capital / habitat / technology

```text
habitat_capital_state
habitat_commissioning
capital_state
capital_flows
technology_state
technology_adoption
technology_learning
```

## Energy / resources

```text
energy_capacity_state
energy_flow
resource_state
resource_flow
```

## Economy / workforce

```text
sector_state
sector_output
io_coefficients
workforce_state
workforce_flow
skill_pool_state
ownership_state
price_index_state
```

## Fleet / transport

```text
fleet_state
fleet_flow
od_demand
transport_cost
mode_choice
route_flow
port_capacity_state
queue_state
```

## Actors / institutions

```text
actor_state
actor_capabilities
actor_ownership
jurisdiction_state
institutional_state
actor_influence_state
```

## Spatial allocation / materialized GIS layer

```text
node_allocation_state
regional_background_state
entity_year_snapshot
historical_metrics
historical_events
```

Every generated row should have, directly or through `run_id`:

```text
run_id
entity_id / region_id / node_id / actor_id
sim_time
model_id/version
scenario_id
epistemic_role
control_class
uncertainty / scenario envelope where applicable
source/provenance
promotion/status
```

---

# 13. GIS materialization strategy

The browser should **not** run the civilization model.

The simulation backend produces an accepted run and materializes annual/yearly GIS snapshots.

Example `entity_year_snapshot` fields:

```text
run_id
year
entity_id
population_bio
population_synth
population_total
workforce_bio_present
workforce_bio_remote
workforce_synth
machine_task_hours
family_capable_capacity
habitat_capacity
power_average
power_capacity
sector_activity_index / selected sector outputs
traffic_class / realized traffic metrics
fleet_presence
port_utilization
commercial influence
civil authority
administrative authority
security authority
accessibility indices
technology maturity flags
uncertainty/status
```

Named infrastructure nodes do **not** need to absorb all regional civilization. A legitimate `regional_background_state` must preserve distributed/non-node population, economy, temporary sites, diffuse settlements, and other activity that does not belong to a canonical infrastructure node.

Conservation at the materialization boundary therefore follows:

```text
Σ named-node state
+ regional_background_state
= macro-region total
```

The current schema-12 tables such as:

- `entity_demographic_profiles`
- `entity_economic_profiles`
- `entity_transport_profiles`
- `entity_authorities`

can remain useful as **current-2226 materialized views / compatibility projections** from the promoted run.

They should no longer be treated as the sole model authority.

---

# 14. Integrated scaffolding and development work plan v1.2

The scaffolding objective is not to implement all civilizational equations immediately. It is to create a reproducible machine in which bad assumptions, hidden calibration, broken conservation, and model lineage are visible before large amounts of history are generated.

## 14.1 Protected development boundary

Throughout scaffolding:

- schema-12 Solar GIS remains frozen;
- RC9 / `FROZEN_PRE_CIVPROP` remains the production reference;
- governing canon remains authoritative until deliberately revised;
- Navigator remains the route/flight authority where integrated;
- WORLD production data is not migrated to experimental schema 13.

SOLAR-CIVPROP development occurs against a separate experimental database/run directory.

## 14.2 Scaffolding MVP acceptance gate

Phase 0 does **not** require every historical LOOM calculation ever performed to be reconstructed before executable work begins.

Scaffolding may move into runtime development once:

1. all models materially affecting the first Earth–Earth Orbit–Luna vertical slice are inventoried;
2. major governing/superseded contradictions affecting core types are identified;
3. canonical IDs, units, time types, epistemic roles, and control classes exist;
4. the initial spatial hierarchy is frozen;
5. the civilization-state contract exists;
6. run/scenario/provenance contracts exist;
7. calibration/reconciliation governance exists;
8. the empty annual orchestrator can execute deterministic no-op runs;
9. conservation and contract tests pass.

The broader historical model inventory continues as later domains are activated.

This prevents Phase 0 from becoming indefinite archaeology.

---

# 15. Scaffold A — evidence, model inventory, and contracts

## 15.1 Model inventory and lineage registry

Build a machine-readable registry of existing LOOM quantitative/procedural models.

Initial domains:

- biological demography;
- synthetic persons;
- migration;
- habitat;
- workforce;
- automation;
- energy;
- production/economy;
- resources;
- technology;
- accessibility;
- freight/passenger demand;
- fleet;
- Mc/Metric constraints;
- institutions;
- ownership;
- actor influence;
- node/spatial allocation.

Each registry entry should contain:

```text
model_id
name
domain
version
status
source
inputs
outputs
units
time_resolution
space_resolution
dependencies
validation_status
supersedes
superseded_by
notes
```

Statuses include:

```text
GOVERNING
PROVISIONAL
SUPERSEDED
EXPERIMENTAL
UNKNOWN
```

Deliverables:

- `SOLAR-CIVPROP Model Inventory v1.0`
- `Contradiction/Supersession Register v1.0`
- `Dependency Graph v1.0`

## 15.2 Common type system

Create validated identifiers:

```text
entity_id
region_id
node_id
actor_id
technology_id
resource_id
sector_id
mode_id
ship_class_id
model_id
scenario_id
run_id
```

Create explicit time classes:

```text
SimulationYear
SimulationEpoch
ModelVersion
RunTimestamp
ReviewSessionID
```

Create validated dimensional quantities for at least:

- people;
- person-hours;
- mass;
- power;
- energy;
- volume;
- distance;
- velocity;
- capacity;
- fraction;
- probability;
- flow rate;
- monetary/value indices.

No untyped cross-module floating-point payloads.

## 15.3 Spatial hierarchy contract

Initial hierarchy:

```text
SOL
├── EARTH_SYSTEM
│   ├── EARTH_SURFACE
│   ├── EARTH_ORBIT
│   ├── LUNA
│   └── CISLUNAR_FREE_SPACE
├── MERCURY_SYSTEM
├── VENUS_SYSTEM
├── MARS_SYSTEM
├── BELT
├── JUPITER_SYSTEM
├── SATURN_SYSTEM
├── URANUS_SYSTEM
├── NEPTUNE_SYSTEM
└── KUIPER
```

Later levels may include:

```text
system
→ body
→ regional civilization state
→ settlement/industrial zone
→ canonical infrastructure node
```

Every level must support aggregation and conservation without double counting.

## 15.4 Civilization-state contract

Define the complete annual state before defining every transition equation.

```text
CivilizationState
    physical
    accessibility
    demographics
    synthetic_population
    habitat
    capital
    workforce
    energy
    resources
    technology
    economy
    transport
    fleet
    institutions
    ownership
```

Important semantic separations:

- synthetic persons ≠ automation capital;
- resident population ≠ present workforce;
- remote workforce ≠ physical workforce;
- installed power ≠ delivered energy;
- habitat capacity ≠ family-capable capacity;
- commercial influence ≠ sovereignty;
- administrative authority ≠ civil sovereignty.

## 15.5 Module interface contract

Each module consumes declared state and returns explicit state/flows rather than mutating unrelated domain dictionaries.

Conceptually:

```python
result = module.step(
    prior_state,
    upstream_outputs,
    parameters,
    scenario,
    rng
)
```

Result:

```text
new_state
flows
diagnostics
constraint_violations
provenance
```

All domain dependencies are registered.

No consumer hard-codes another module's internal field names or timeline/mode codes.

---

# 16. Calibration and canon-reconciliation governance

Calibration controls are part of the scaffold, not something added after the model is capable of cheating.

## 16.1 Calibration adjacency

Every `CALIBRATION_ELIGIBLE` parameter declares:

- causal mechanism;
- permitted target families;
- prior/bounds;
- provenance.

A real mechanism may legitimately affect multiple target families. Unexplained adjacency is prohibited.

## 16.2 DOF screening

Use:

```text
independent targets ≥ 2 × calibration parameters
```

as an inexpensive structural **admission screen**.

Passing this screen does **not** establish identifiability. Correlated targets may contain far less independent information than their raw count suggests. Equifinality and sensitivity diagnostics remain separately required.

## 16.3 Prior discipline

Because LOOM canon is already known, true blinding is impossible.

Therefore:

> Calibration bounds must be justified by target-independent empirical, analogue, engineering, or theoretical evidence and frozen before optimization/calibration uses the relevant canon target.

No prior may be widened simply because a target failed.

## 16.4 Hard constraints, soft targets, and holdouts

### Hard constraints

Feasibility conditions. Violation invalidates a run.

Prefer hard constraints for genuinely definitional facts:

- physics;
- chronology;
- known infrastructure existence;
- certified capabilities;
- explicit engineering impossibilities.

Endogenous quantities such as population, traffic, or economic output are **not automatically hard constraints merely because canon states an exact number**.

### Soft targets

Enter calibration/scoring with declared tolerances.

### Validation holdouts

Never influence calibration. Used only after parameters are frozen. Holdouts are preregistered.

## 16.5 Two-axis reconciliation verdict

Separate:

### Canon fit

```text
CONSISTENT
TENSION
INCOMPATIBLE
```

from:

### Structural identification

```text
IDENTIFIED
WEAK
EQUIFINAL
NOT_ASSESSED
```

Example:

```text
Lunar population:
    canon fit = CONSISTENT
    identification = EQUIFINAL
```

Matching canon does not itself establish that the simulator discovered the correct historical mechanism.

## 16.6 Parameter Reclassification Requests — anti-curve-fitting gate

When a target becomes `TENSION` or `INCOMPATIBLE`, allowed responses are:

1. review/revise canon;
2. retain visible `MODEL_DISCREPANCY`;
3. file a formal Parameter Reclassification Request (PRR) based on independent evidence.

A failed target does not authorize immediate creation of another free parameter.

A PRR requires:

- explicit justification;
- target-independent evidence/mechanism;
- dependency/DOF re-evaluation;
- regression against previously consistent targets;
- model/version lineage update.

### Cooling-off gate

A PRR may be drafted when a failure is discovered but may **not** be approved or used in recalibration during the same registered calibration/review session.

Every failing result records a `failure_event_id` and `review_session_id`. An accepted PRR must reference that failure and carry a later `review_session_id`.

This applies to changes in:

- parameter class;
- prior bounds;
- target-family adjacency;
- causal specification;
- coefficient granularity;
- any other change that increases model flexibility.

Same-session approval invalidates the subsequent calibration run.

The purpose is a decision boundary, not an arbitrary elapsed-time delay.

Repeated knob-unlocking is prohibited.

## 16.7 Uncertainty and presentation precision

Early scaffold runs may use:

```text
low
central
high
```

as a **scenario envelope**, not a probabilistic confidence interval.

Later ensemble runs may generate statistical uncertainty intervals.

Unexpected contraction of uncertainty with simulation time triggers review. Contraction is allowed when justified by explicit mechanisms such as:

- hard physical limits;
- saturation;
- strong convergence;
- later hard constraints;
- other documented causal structure.

Presentation precision follows epistemic uncertainty.

Model-derived outputs must not display more significant figures than their uncertainty supports.

Exact canon values may remain exact when shown explicitly as canon assertions.

GIS/export formatting should eventually enforce this automatically.

---

# 17. Institutional and inherited-capital boundary state

Institutions must exist from Phase 1 even though full actor/corporate evolution can wait.

Initial institutional state should be a small vector rather than one flattened scalar:

```text
civil_stability
administrative_capacity
security_reliability
certification_access
migration_property_regime
```

These begin as:

- canon-derived exogenous values;
- empirical/analogue assumptions;
- scenario-controlled values.

Later, actor/ownership/institution models can replace those inputs with endogenous outputs without changing downstream interfaces.

Likewise, full ownership evolution may wait, but industrial geography already depends on inherited access to:

```text
capital_access
legacy_industrial_network
```

These begin as coarse exogenous state and later become actor/ownership outputs.

---

# 18. Macro-to-node allocation contract

Node disaggregation is not plumbing. It is a spatial model and must obey the same calibration and provenance discipline as the macro simulator.

## 18.1 Stocks are not reallocated

Existing node capital remains where previously constructed:

```text
K_node(t+1)
=
K_node(t)
- depreciation/loss
+ newly commissioned investment
```

Only **new capital investment flows** undergo location choice.

This preserves physical continuity and path dependence.

## 18.2 Capital/population feedback

Avoid a flat one-way rule of `capital → population`.

Use the lagged causal loop:

```text
existing capital enables settlement
→ population/jobs generate expected demand
→ expected demand affects new investment location
→ construction lag
→ new capacity
→ future population/activity
```

Construction lag breaks the circularity without pretending settlement demand cannot influence investment.

## 18.3 Allocation mechanism

Use layered allocation.

### Layer A — utility/suitability

For class `k` at node `n`:

```text
V(n,k,t) = Σ β_i × attribute_i
```

Potential attributes:

- accessibility;
- gravity/environment;
- existing capital;
- resources;
- skilled labor;
- hazard;
- family suitability;
- certification;
- institutions;
- agglomeration;
- capital access.

Capacity is normally a constraint, not merely a utility bonus.

### Layer B — constrained choice

Translate utility into provisional shares using discrete-choice logic.

Apply hard capacity constraints. Overflow reallocates only to feasible alternatives.

### Layer C — conservation reconciliation

Use the simplest balancing method appropriate to the dimensional problem:

- proportional normalization for simple one-margin allocation;
- constrained balancing for moderate problems;
- RAS/IPF where multiple marginal constraints genuinely require it.

Reconciliation exists to enforce conservation, not to optimize resemblance to canon.

## 18.4 Coefficient governance

No arbitrary node-specific fudge factors.

Coefficient structure may be hierarchical:

```text
global base
→ population-class coefficient set
→ sector-class coefficient set
→ environmental/regime class where justified
```

Class distinctions should be few and mechanistic. The existence of heterogeneous outcomes is **not itself evidence** that a new coefficient class exists.

Each coefficient retains its own epistemic/control class; coefficients are not automatically calibration eligible.

### Coefficient-granularity governance

The coefficient hierarchy is preregistered as part of the model specification.

Splitting an existing coefficient into additional population, sector, environmental, institutional, or regime classes increases model degrees of freedom and is therefore governed as a **PRR**.

A new split requires:

- a later `review_session_id` than any failure motivating reconsideration;
- target-independent causal or empirical justification;
- recalculation of the DOF admission screen;
- regression testing against previously consistent target families;
- versioning of the coefficient schema.

A coefficient class may not be introduced solely because a particular node, region, or canon target fits poorly.

Post-split DOF screening must still pass, but passing does not establish identification; equifinality/sensitivity diagnostics remain independently required.

## 18.5 Canonical node tiers

Node facts are classified before calibration.

### Tier A — hard/definitional

Examples:

- node physically exists;
- location is canon-fixed;
- particular infrastructure exists;
- jurisdiction or technology chronology is definitional.

### Tier B — soft target

Examples:

- major shipyard;
- population magnitude;
- traffic significance;
- industrial prominence.

### Tier C — validation holdout

Selected node role/output facts withheld from calibration.

A Tier-B node may not be promoted to Tier-A merely because the model cannot reproduce it.

### Tier preregistration gate

Every canonical node fact used as a hard constraint, soft target, or validation holdout must have its tier assignment recorded against the governing canon baseline **before** the applicable calibration/allocation run.

Tier changes after results are observed are model-governance changes and require explicit versioning and justification.

A Tier-B or Tier-C fact may not be converted to Tier-A in response to poor fit from the same model version.

## 18.6 Regional/background civilization state

Do not call everything outside named infrastructure a residual error.

Represent:

```text
regional_background_state
```

as a legitimate modeled component.

Example:

```text
EARTH_SURFACE
    canonical major nodes
    +
    distributed/non-node civilization
```

Likewise Belt/free-space civilization may include:

- named infrastructure;
- diffuse settlements;
- temporary sites;
- mobile/rotational activity;
- other background population/economic stock.

## 18.7 Emergent-node mechanism

Later candidate sets may extend beyond the 127 canonical nodes.

If noncanonical sites become attractive, the simulation reports them as:

```text
EMERGENT_CANDIDATE
```

They do not automatically become canon.

Promotion into the canonical GIS registry is a deliberate canon act.

The simulator must not suppress potential sites merely because they are absent from the current atlas.

---

# 19. Scaffold B — reproducibility, provenance, and diagnostics

Every run records:

```text
run_id
scenario_id
model_set_version
code_version
canon_baseline
parameter_set
random_seed
start_year
end_year
creation_time
status
```

Initial scenario categories:

```text
BASELINE_2026
FORWARD_REFERENCE
CANON_RECONCILIATION
HINDCAST
SENSITIVITY
STRESS
```

Suggested runtime structure:

```text
runs/
    <run_id>/
        manifest.json
        parameters.json
        diagnostics.json
        results.sqlite3
```

Every output must be traceable to the run that created it.

Scaffold B work order:

1. run/scenario/provenance framework;
2. parameter registry;
3. dependency graph;
4. diagnostics/error contract;
5. validation/test framework.

---

# 20. Scaffold C — persistence and empty runtime

Schema 13 is finalized only after Scaffold A/B contracts are sufficiently stable.

Then build:

1. experimental schema-13 database;
2. schema contract tests;
3. empty annual orchestrator;
4. materialization layer;
5. schema-12 compatibility projection.

Before meaningful propagation equations are introduced, the engine should already be able to execute:

```text
load prior state
↓
load physical/ephemeris state
↓
derive accessibility
↓
run registered modules
↓
reconcile coupled constraints
↓
validate
↓
commit new annual state
↓
materialize reporting snapshot
↓
advance year
```

The first successful 2026→2226 run may intentionally produce nearly unchanged civilization.

That is acceptable.

The goal is proving the machinery before filling it with history.

---

# 21. Initial dependency order

Provisional sequence:

```text
1 physical / ephemeris
2 accessibility
3 technology availability
4 institutional boundary state
5 demographics
6 synthetic population
7 existing habitat/capital
8 workforce
9 energy/resources
10 production/economy
11 migration/location choice
12 new capital-investment location
13 OD demand
14 fleet/transport
15 ownership/actor effects where active
16 reconciliation
17 validation
18 materialization
```

Some later modules will require inner iteration.

The dependency graph must make those feedback cycles explicit rather than hiding them inside module code.

---

# 22. First scientific vertical slice — Earth–Earth Orbit–Luna

Do **not** build all Solar modules horizontally first.

Exercise the complete scaffold on:

```text
EARTH_SURFACE
EARTH_ORBIT
LUNA
CISLUNAR_FREE_SPACE
```

Initial causal slice:

```text
2026 baseline
→ demography
→ habitat/capital
→ workforce
→ energy
→ institutional constraints
→ accessibility
→ migration
→ new capital allocation
→ annual state
```

Initially defer:

- full corporations;
- full ownership evolution;
- Metric;
- Mc;
- complex freight economy;
- all 127 nodes;
- full ensemble calibration;
- detailed queues.

The slice must nevertheless use the real contracts so later expansion does not require architectural replacement.

---

# 23. Testing architecture and acceptance gates

## Contract tests

Every module receives/returns valid types.

## Conservation tests

At minimum:

```text
population migration
synthetic-person stock
capital accumulation
energy
materials where modeled
fleet
Mc when activated
regional→node allocation
```

## Invariant tests

Examples:

```text
population <= habitable capacity
family population <= family-capable capacity
no negative resource stock
no technology before availability
no new capital before construction lag
no unexplained node-specific coefficient
```

## Calibration-governance tests

At minimum:

- every parameter has exactly one declared control class;
- calibration adjacency is registered before use;
- hard constraints are enforced as feasibility gates;
- validation holdouts never enter calibration loss/constraints;
- DOF admission screening is performed before calibration;
- PRRs reference a prior failure and a later `review_session_id`;
- PRR-driven coefficient splits receive the same governance as prior/class changes;
- parameter/coefficient changes trigger regression testing;
- canon-fit and identification verdicts are separately reported;
- tier assignments predate the applicable allocation/calibration run;
- no poorly fitting Tier-B/C fact is promoted to Tier-A within the same model version to suppress a failure;
- model-derived output precision does not exceed its uncertainty basis.

## Regression tests

Fixed seed + fixed model set + fixed parameters must reproduce deterministic reference results.

Reference horizons:

```text
2026→2036
2026→2050
2026→2100
2026→2226
```

For LOOM code releases:

- run unit regression before sending a new Python release;
- when changes are substantively functional, run unit regression plus functional tests;
- reserve full end-to-end regression for finalization immediately before production promotion/run.

---

# 24. Revised development sequence

Execute in this order.

## Scaffold A — evidence and contracts

1. Model inventory for Earth–Luna-relevant domains.
2. Contradiction/supersession register.
3. Epistemic/control classification system.
4. Canonical IDs and quantity types.
5. Spatial hierarchy.
6. 2026 baseline contract.
7. 2226 hard/soft/holdout registry.
8. Civilization-state contract.
9. Module-interface contract.
10. Calibration/reconciliation governance.

## Scaffold B — reproducibility

11. Run/scenario/provenance framework.
12. Parameter registry.
13. Dependency graph.
14. Diagnostics/error contract.
15. Validation/test framework.

## Scaffold C — persistence/runtime

16. Final schema-13 contract.
17. Experimental schema-13 database.
18. Empty annual orchestrator.
19. Materialization layer.
20. Schema-12 compatibility projection.

## First scientific vertical slice

21. Earth surface.
22. Earth orbit.
23. Luna.
24. Cislunar free-space.
25. Demographics.
26. Habitat/capital.
27. Workforce.
28. Energy.
29. Institutional vector.
30. Accessibility.
31. Migration.
32. Simple new-capital location choice.

## Validation

33. Conservation tests.
34. Scenario-envelope runs.
35. Canon reconciliation.
36. Fit-vs-identification diagnostics.
37. Historical hindcasting where useful.

## Expansion

38. Mars.
39. Whole-Solar macro regions.
40. Sector economy/resource closure.
41. Transport/fleet.
42. Major-system subdivision.
43. Macro→node allocation.
44. Full 127-node layer.
45. Emergent candidate sites.
46. Actors/ownership/institutional evolution.
47. Full GIS playback integration.

---

# 25. Immediate next work

The next active task is:

> **Build the SOLAR-CIVPROP Model Inventory and Contradiction/Supersession Register for the modules required by the first Earth–Earth Orbit–Luna vertical slice.**

At the same time, extract the minimum shared type vocabulary exposed by those models.

Do not write schema-13 migration code yet.

Do not write historical propagation equations yet.

The first architecture milestone is reached when a typed, provenance-aware, calibration-governed empty simulator can reproducibly run annual states from 2026 to 2226 without touching production.

At that point, every subsequent civilizational mechanism is installed into a functioning machine rather than joined to a growing pile of independent calculations.

---

# 26. Key project guardrails

- Physics first.
- Browser renders supplied geometry; does not infer orbital mechanics.
- No fake missing orbits.
- No invented precision.
- Canon, provisional model, and superseded model must remain distinguishable.
- Synthetic persons are persons, not automation capital.
- Commercial power is not sovereignty.
- Administrative authority is not civil sovereignty.
- Economic output is not automatically GDP.
- Resource abundance is not automatically industrial dominance.
- Traffic must be derived from demographics/economy/accessibility, not chosen aesthetically.
- Technology must alter mechanisms/constraints, not directly multiply desired outcomes.
- Loom is too late to explain mature 2226 Solar demography.
- Migration must be conserved/source-debited.
- Off-Earth population must respect habitat/family-capable capacity.
- Remote workforce and resident workforce are distinct.
- Exact route accessibility must depend on ephemeris and ship/mode.
- Existing capital cannot teleport between nodes; only new investment is location-allocated.
- Named canonical nodes do not exhaust regional civilization.
- Institutional boundary state exists before full endogenous actor simulation.
- No node-specific calibration fudge coefficients.
- Coefficient-class proliferation is a governed model change.
- Matching canon and identifying the correct mechanism are separate claims.
- Full model runs must be versioned and reproducible.
- Superseded models are retained as lineage, never silently used as fallbacks.
- Calibration targets and validation holdouts must be explicit.
- A failed target cannot cause same-session knob unlocking.
- Tier-B/C node facts cannot be promoted to hard constraints merely to suppress a bad fit.

---

# 27. Suggested opening prompt for the implementation thread

> We are starting the LOOM SOLAR-CIVPROP implementation thread from `LOOM_SOLAR_CIVPROP_Next_Thread_Seed_v1.2.md`. Treat the schema-12 Solar GIS baseline as frozen production and do not migrate the production database. Begin with Scaffold A: inventory every existing LOOM quantitative/procedural model materially required for the Earth–Earth Orbit–Luna vertical slice; identify governing, provisional, superseded, and conflicting values; build the contradiction/supersession register and dependency graph; and extract the canonical IDs, quantity types, epistemic roles, control classes, and annual state interfaces those models require. Calibration governance, PRR cooling-off, fit-vs-identification reporting, and node-tier preregistration are part of the scaffold, not later polish. Do not write historical propagation equations or schema-13 migration code until the contracts are coherent enough to support a deterministic empty 2026→2226 orchestration run. Ephemeris remains a first-class physical input through accessibility, and all outputs must preserve provenance/model lineage.

---

# 28. Web research references reviewed in the prior thread

These were used as architectural analogues, not as LOOM canon:

- UN World Population Prospects / cohort-component projection — https://population.un.org/wpp/
- GCAM documentation — https://jgcri.github.io/gcam-doc/
- MESSAGEix framework — https://docs.messageix.org/
- REMIND documentation — https://rse.pik-potsdam.de/doc/remind/
- UrbanSim documentation — https://cloud.urbansim.com/docs/
- MATSim — https://www.matsim.org/
- OECD Inter-Country Input-Output tables — https://www.oecd.org/en/data/datasets/inter-country-input-output-tables.html
- MIT Space Logistics / SpaceNet — https://strategic.mit.edu/spacelogistics/
- NASA NAIF/SPICE — https://naif.jpl.nasa.gov/
- JPL Horizons — https://ssd.jpl.nasa.gov/horizons/
- NASA human-systems / Equivalent System Mass literature
- IEA learning curves — https://www.iea.org/reports/experience-curves-for-energy-technology-policy
- Kennedy & O'Hagan, Bayesian calibration of computer models — DOI 10.1111/1467-9868.00294

The implementation thread should verify current primary documentation as needed before adopting specific mathematical assumptions.

---

# END STATE

The target is not merely a database of 2226 values.

The target is a model that can answer:

- **What is this place like in 2226?**
- **Why did it become important?**
- **When did it become important?**
- **Which technologies made it possible?**
- **Which demographic/capital/resource/transport constraints shaped it?**
- **Which actors accumulated power there and why?**
- **How did orbital geometry affect its accessibility over time?**
- **What parts are canon, what parts are model-derived, and how uncertain are they?**
- **Could the 2226 canon plausibly emerge from 2026 without violating the model's own assumptions?**
- **If the simulator matches canon, did it actually identify a defensible mechanism, or merely one of several equifinal paths?**

And, eventually, the GIS should be able to show the answer by simply pressing **PLAY**.
