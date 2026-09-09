# LOOM 2226 — Wayfarer S1 Procedural Layout Test Definition v0.1

**Status:** ENGINEERING / RESEARCH — QUALIFICATION CANDIDATE — NON-CANON — NON-PRODUCTION  
**Parent work plan:** `docs/LOOM_2226_Physical_Design_Synthesis_Work_Plan_2026-09-08.md`

## 1. Test question

Can a deterministic LOOM-owned solver place a reduced set of Wayfarer components inside the currently admitted physical packaging constraints, without replaying the existing full transform list, and produce a candidate whose mass, CoM and full candidate inertia are derived from the generated arrangement itself?

The result is a feasibility result only. It cannot replace governing Wayfarer authority.

## 2. Frozen source baseline

Use the current Wayfarer authority chain as input only:

1. `canon/current/LOOM_2226_CANON_II_Engineering_Ships_Operations_v2.4.md`
2. `canon/current/LOOM_2226_CANON_II_Wayfarer_Schematic_Amendment_v2.4a.md`
3. `geometry/wayfarer_geometry_seed.sql`
4. Phase-3 prototype Wayfarer seed/coupling overlay
5. Phase-4 qualification geometry overlay
6. Phase-5 qualification status and inertia audit

No test code may overwrite those sources.

## 3. Preserve exactly

The S1 extraction must preserve these reference values exactly unless the test explicitly changes configuration state:

```text
dry mass = 858,500 kg
wet mass = 1,158,500 kg
normal remass inventory = 250,000 kg
protected water = 50,000 kg
planetary launch = 33,000 kg when DOCKED
DOCKED wet CoM baseline = [26.676650841605525, 0, 0.14812257229175657] m
ABSENT wet mass baseline = 1,125,500 kg
ABSENT wet CoM baseline = [26.819635717458908, 0, 0] m
```

The generated S1 candidate is not required to reproduce the hand-authored baseline CoM if it deliberately moves admitted components. It **is** required to preserve total mass/accounting exactly and independently recompute its new CoM.

## 4. S1 fixed topology / packaging

Keep the following fixed as topology or physical regions:

```text
ship reference length             57 m
nominal main-body diameter        ~9 m
forward pressure hull             x = 0..14 m, trial diameter 8.6 m
major tank region                 x = 18..32 m
4 major tanks                     quadrature topology
nominal tank external diameter    3.0 m
tank center radius                2.7 m
4 principal longerons             topology fixed
launch-bay reservation            approximately x = 16..28 m
launch side                       +Z
docking/service side              -Z
relational envelope               x = 18..34 m, diameter 1.4 m
shadow-shield region              x = 38..43 m
reactor/torch machinery region    x = 43..50 m
nozzle                            x = 50..57 m
4 major radiator assemblies       count/topology fixed; panel geometry OPEN
```

Do not use OPEN radiator-panel dimensions or OPEN docking geometry as collision authority.

## 5. S1 mass inventory

Use the existing mass ledger unchanged:

```text
structure                       150,000 kg
armor/fixed shield              105,000 kg
habitation/life support          45,000 kg
relational plant                 88,000 kg
thermal/radiators                90,000 kg
propulsion                      160,000 kg
electrical                       55,000 kg
planetary launch                 33,000 kg
avionics/sensors/comms           20,000 kg
RCS/docking/service              25,000 kg
mission/courier systems          20,000 kg
engineering reserve              67,500 kg
normal remass store             250,000 kg
protected water store            50,000 kg
```

S1 must not double count the 250 t normal remass and 50 t protected water beyond the 300 t total working-fluid/water inventory.

## 6. S1 initial solver variables

The first solver should move only components for which a meaningful admissible region can be defined without inventing detailed geometry.

### 6.1 Strong S1 variables

#### Relational plant

```text
mass = 88,000 kg
admitted envelope form = axial cylinder equivalent
length = 16 m
diameter = 1.4 m
current region = x 18..34 m
```

For the first implementation, either keep its envelope inside x=18..34 or allow a narrower sub-range explicitly declared in test configuration. The equivalent cylinder is a candidate engineering body, not canon internal mass distribution.

#### Planetary launch longitudinal station

```text
mass = 33,000 kg
working envelope = 10.5 x 3.9 x 3.1 m
launch-bay reservation approximately x = 16..28 m
launch side = +Z
```

The first solver may vary longitudinal station only, preserving the +Z launch side and extraction semantics. The current detailed launch geometry is an engineering working envelope, not exact internal mass distribution.

#### Four-tank cluster common longitudinal station

Preserve:

```text
4 tanks
62,500 kg normal remass each at reference state
quadrature
center radius = 2.7 m
nominal diameter = 3.0 m
aggregate normal remass = 250,000 kg
```

The solver may shift the common tank-cluster x station within an admitted interval derived from the x=18..32 m region. It must preserve exact aggregate mass and zero transverse CoM of the four-tank store at reference fill.

### 6.2 Candidate S1 variables with conservative abstract envelopes

These may be introduced one at a time only after the evaluator supports explicit abstract packaging volumes:

- electrical — 55,000 kg;
- avionics/sensors/comms — 20,000 kg;
- mission/courier systems — 20,000 kg;
- RCS/docking/service — 25,000 kg.

Their current mass centroids alone do not define physical dimensions. Therefore S1 v0.1 should preferably model them as `PLACEMENT_POINT_WITH_KEEP_OUT` or similarly explicit qualification abstractions rather than pretending an exact solid geometry is known.

Such abstractions may influence CoM and connection distance but **must not contribute a claimed exact centroidal inertia tensor** unless a separately admitted equivalent envelope exists.

### 6.3 Do not optimize in S1 v0.1

Keep fixed or unresolved:

- primary structure — 150,000 kg;
- armor/fixed shield — 105,000 kg;
- habitation/life support — 45,000 kg;
- thermal/radiators — 90,000 kg;
- propulsion group — 160,000 kg;
- engineering reserve — 67,500 kg;
- protected water — 50,000 kg unless a containing envelope is separately admitted;
- radiator deployment geometry;
- docking collar dimensions;
- detailed RCS thruster geometry;
- detailed pressure-hull internal arrangement.

S1 can still carry fixed/abstract contributions for total mass and CoM, but unresolved centroidal inertia must remain explicitly classified.

## 7. Consequence for S1 inertia

A strict full-authority Wayfarer inertia tensor still cannot be produced from current data alone because several large fixed masses lack admitted centroidal mass-distribution geometry.

Therefore S1 has two legitimate modes:

### Mode A — feasibility-only generated partial authority

Generate layout and derive:

- exact total mass;
- exact generated CoM;
- full parallel-axis contribution;
- centroidal inertia for only those components with admitted equivalent bodies;
- unresolved centroidal-inertia mass fraction.

This mode must remain:

```text
flight_dynamics_authority = false
```

### Mode B — explicit qualification surrogate closure

For testing the optimizer/evaluator mechanics only, every unresolved mass may be assigned an overt `QUALIFICATION_SURROGATE` body with synthetic dimensions.

If used:

- surrogate dimensions must live in a dedicated S1 test fixture;
- they must not be sourced from renderer convenience;
- output must be labeled `SURROGATE_FULL_INERTIA_NOT_WAYFARER_AUTHORITY`;
- the resulting full tensor may test search behavior, SPD checks and dynamics coupling, but may not qualify Wayfarer flight physics.

S1 should implement Mode A first. Mode B is optional and only for algorithmic testing.

## 8. Initial objective vector

Use an inspectable vector rather than one hidden scalar:

```text
J1 = absolute transverse CoM offset
J2 = longitudinal CoM deviation from chosen target band
J3 = admitted rotational-control burden surrogate
J4 = remass-feed path surrogate
J5 = major power-path surrogate
J6 = packaging/collision penalty
J7 = launch extraction penalty
```

A deterministic lexicographic or explicit weighted policy may select among Pareto-equivalent candidates, but the complete objective vector must be retained in output.

Do not optimize toward arbitrary aesthetics in S1.

## 9. Minimal candidate representation

Each candidate should serialize at least:

```text
candidate_id
seed
component transforms
component active states
store decomposition
admitted equivalent bodies
abstract placement/keep-out objects
mass
CoM
parallel-axis tensor
admitted centroidal tensor contribution
candidate aggregate tensor
unresolved inertia mass fraction
hard constraint results
objective vector
provenance map
```

## 10. First hostile tests

The S1 verifier should include deliberately bad candidates:

1. launch placed outside the admitted bay region — reject;
2. tank cluster loses quadrature symmetry — reject;
3. total remass != 250,000 kg — reject;
4. total working-fluid/water != 300,000 kg — reject;
5. component collision — reject when both envelopes are physically admitted;
6. attempt to use OPEN radiator-panel geometry — reject;
7. non-deterministic replay under same seed — fail;
8. negative/NaN mass or geometry — fail closed;
9. synthetic surrogate accidentally marked flight authority — fail closed.

## 11. First useful result

The first genuinely informative experiment is smaller than a complete ship optimizer:

> Keep the existing fixed Wayfarer background mass ledger, then procedurally choose the longitudinal arrangement of the relational plant, launch and four-tank remass cluster inside their admitted regions while preserving all hard constraints.

This already lets LOOM test:

- deterministic search;
- candidate transforms;
- same-source mass/geometry coupling;
- generated CoM;
- generated parallel-axis inertia changes;
- objective tradeoffs;
- SHIPCLASSES-compatible export;
- compatibility with existing 3D output.

If this reduced problem cannot be made clean, generic ship synthesis should stop before becoming larger.

If it works, S1 can expand component-by-component rather than pretending the whole Wayfarer is already specified well enough for optimization.

## 12. Pass interpretation

A PASS means:

```text
PROCEDURAL_LAYOUT_FEASIBILITY = PASS
```

It does **not** mean:

```text
WAYFARER_FLIGHT_INERTIA = QUALIFIED
WAYFARER_CANON = CHANGED
PRODUCTION_SHIPCLASSES = UPDATED
```

Those require later governed transitions.

---

**END — WAYFARER S1 TEST DEFINITION v0.1**
