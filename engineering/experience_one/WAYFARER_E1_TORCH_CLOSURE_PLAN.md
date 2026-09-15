# Wayfarer E1 Torch — Interface Closure Plan

**Status:** ENGINEERING WORK PLAN / NON-CANON / NON-CERTIFICATION  
**Purpose:** Drive the Wayfarer remass-consuming primary torch from the current accumulated working specification to an E1-qualified engineering interface without pretending to certify a physically unrealized 2226 fusion reactor.

## Closure target

E1 torch closure means E1 has a bounded, testable propulsion interface whose earned inputs, outputs, invariants, operating exclusions and unresolved technology holds are explicit. It does **not** mean component-level reactor/nozzle hardware certification.

The final E1 review should answer:

> Does E1 know everything it legitimately needs to know about the torch, while every item that cannot be physically closed from current authority/research is represented as an explicit hold rather than an implicit assumption?

## Already earned

- one axial fusion torch / magnetic-nozzle vehicle topology;
- 1,158.5 t wet reference mass, 858.5 t dry excluding fluid/water, 300 t working-fluid/water inventory;
- 250 t normal remass and protected 50 t water reserve;
- six working performance cards from ECON through LIMIT;
- exact `F = ma`, `mdot = F/ve`, `Pjet = 0.5 F ve` relationships and depletion model;
- torch/high-metric simultaneous-operation prohibition;
- source-power realizability equations and explicit technology hold;
- research-bounded reactor/nozzle family trade;
- energy-partition/deposition model framework without invented defaults;
- remass-coupling/nozzle envelope without invented efficiencies;
- physical plume/external-clearance requirement;
- working-fluid/feed trade and light-remass leading research analogue without species selection;
- fixed- and multi-segment mission constraints, exact remass chaining and hostile formal proofs;
- generated exact torch-card formal library;
- ship-level Z3 integration checkpoint preserved separately.

## Remaining E1 closure increments

### T1 — E1 torch interface contract

Create a machine-readable and human-readable interface separating:

- **required/earned inputs**: mode, vehicle mass, normal remass state, protected reserve state;
- **derived outputs**: acceleration target/card, exhaust velocity, thrust, mdot, direct kinetic jet power, remass depletion;
- **state invariants**: one primary torch, protected reserve exclusion, torch/high-metric exclusion;
- **physical-closure parameters that may remain OPEN**: source directed fraction, fusion gain/Q definition and value, specific power, deposition partitions, nozzle efficiency/coupling, selected remass species/feed hardware;
- **holds** that prevent component certification but need not prevent E1 interface qualification.

No OPEN physical parameter receives a hidden default.

### T2 — Source / energy / thermal hold envelope

Consolidate the existing source-power and deposition work into a single E1-facing hold envelope. The interface must distinguish:

- direct kinetic jet power;
- source fusion output;
- external driver/input power where applicable;
- vehicle electrical load;
- vehicle waste heat;
- neutron/photon/intercepted-particle deposition;
- transient thermal storage/rejection requirements.

E1 may carry unresolved values, but it must know which outputs are unavailable until those values are supplied.

### T3 — Remass / feed / nozzle interface envelope

Close what E1 needs without selecting unsupported hardware:

- exact required mdot range across cards;
- allowed normal-remass inventory and protected-water exclusion;
- candidate working-fluid family status/provenance;
- required feed controllability/dynamic response interface;
- nozzle expansion/detachment/divergence/interception requirements;
- explicit OPEN coupling/efficiency/species/storage/feed implementation.

Do not select H/He/water/metallic remass merely to obtain closure.

### T4 — Structural / plume / operational integration envelope

Bind the torch interface to the vehicle without claiming detailed component certification:

- axial thrust envelope through LIMIT;
- candidate aft packaging envelope clearly marked candidate;
- four-longeron thrust-frame interface;
- plume/external-hardware exclusion interface;
- RCS integration holds;
- radiator/thermal interface requirements;
- operating-state exclusions and transition preconditions.

Structural design factor, dynamic amplification, side load, fatigue spectrum and local reinforcement remain OPEN unless separately earned.

### T5 — Integrated E1 torch qualification review

Run a hostile review across the complete interface and classify every item as:

- `E1_INTERFACE_CLOSED`;
- `E1_INTERFACE_CLOSED_WITH_TECHNOLOGY_HOLD`;
- `OPEN_BLOCKING_E1`;
- `OPEN_BLOCKING_COMPONENT_CERTIFICATION_ONLY`.

Qualification should include Python numerical tests, Z3 invariant/configuration proofs where appropriate, repository Gate, and independent exact-head Pixel qualification.

If no `OPEN_BLOCKING_E1` items remain, freeze the E1 torch **interface** and move E1 engineering onward. Do not rename that result as reactor, nozzle, shield, magnet or propulsion-hardware certification.

## Explicit component-certification holds carried forward

At minimum, preserve these until physically earned:

1. source/reactor realizability: gain/Q, specific power, source mass and required source output;
2. directed-energy / remass-coupling partition;
3. neutron, photon, leakage, interception and secondary deposition;
4. working-fluid species/storage/feed implementation;
5. magnetic-nozzle coupling, expansion, detachment, divergence and interception;
6. shield/magnet/thermal lifetime;
7. thrust-frame dynamics, local load path and fatigue;
8. quantitative plume/external-hardware clearance;
9. RCS integration holds already recorded in the primary propulsion specification.

## Work discipline

- GitHub authority first.
- Tests before substantive executable changes.
- Python owns numerical/physical calculations.
- Z3 owns exact algebraic/configuration/invariant verification where suitable.
- No nonlinear physics is approximated merely to fit SMT.
- No candidate/research value becomes authority because it makes a model close.
- Successful SAT/numerical execution is not physical realizability.
- Full E2E qualification is reserved for T5 or a risk-specific earlier need.

## Deferred parallel lane

The Computational Shipyard Z3 lane is intentionally checkpointed at `engineering/verification/z3/COMPUTATIONAL_SHIPYARD_CONTINUATION.md`. Resume it after the E1 torch interface reaches the T5 review or when a torch closure increment specifically needs shipyard synthesis.
