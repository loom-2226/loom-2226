# LOOM 2226 — Physical Design Requirements Compiler v0.1

**Date:** 2026-09-08  
**Status:** ENGINEERING / RESEARCH — NON-CANON — NON-PRODUCTION  
**Branch:** `research/physical-design-requirements-compiler-2026-09-08`  
**Parent:** Wayfarer S2 research head `7cb1dc0ac20b4d518ec656c4b332bafd69c2014f`

## 1. Purpose

Introduce a first-class Requirements Compiler / Mission Specification layer ahead of physical design synthesis.

The compiler separates:

1. **ship class / doctrine** — what kind of vehicle is being requested and how competing objectives should be prioritized;
2. **functional requirements** — what the vehicle must accomplish, such as cargo mass, cargo volume, passenger count, crew, endurance, acceleration, delta-v, docking interfaces and envelope limits;
3. **engineering derivation rules** — explicit, provenance-tagged relationships that convert functional demand into downstream engineering demand;
4. **OPEN derivations** — required outputs for which no admitted rule exists.

The layer exists so a user, economy, corporation, polity or scenario can request capability rather than manually place components.

## 2. Authority firewall

This increment does **not** make engineering conversions authoritative merely because they are convenient.

Examples:

- `passengers = 200` does not imply any automatic habitable volume;
- cargo tonnage does not imply structural mass without an admitted structural rule;
- endurance does not imply consumables mass without an admitted life-support/storage model;
- electrical demand does not imply radiator area without admitted power/thermal rules;
- delta-v does not imply remass without an admitted propulsion state/model.

If an expected engineering requirement lacks an admitted derivation rule, the compiler emits it as `OPEN` through `open_derivations`.

A derivation rule marked `OPEN` is never executed.

## 3. Architecture

```text
SHIP CLASS / DOCTRINE
        +
FUNCTIONAL REQUIREMENTS
        +
TECHNOLOGY / INDUSTRIAL / ENGINEERING RULE CONTEXT
        ↓
REQUIREMENTS COMPILER
        ↓
DIRECT REQUIREMENTS
DERIVED REQUIREMENTS
OPEN DERIVATIONS
        ↓
COMPONENT / MODULE SELECTION
        ↓
DESIGN GRAMMAR
        ↓
TOPOLOGY / PLACEMENT / SIZING
        ↓
PHYSICAL EVALUATION / OPTIMIZATION
```

The requirements compiler is upstream of the existing physical-design search/evaluator.

## 4. Ship class is doctrine, not geometry

A ship class request is represented as a `DoctrineProfile` containing:

- doctrine/class identifier;
- ordered objective priorities;
- required capability tags;
- authority status;
- provenance.

The compiler does not assume that a class named `FREIGHTER`, `COURIER`, `LINER`, `TUG` or any other label has a hidden shape, fixed component inventory, performance value or geometry.

Named classes should eventually live in governed data, not hard-coded solver branches.

Example doctrine:

```json
{
  "id": "EXAMPLE_INTERPLANETARY_FREIGHTER",
  "objective_priority": [
    "MINIMIZE_COST_PER_TONNE_KM",
    "MINIMIZE_DRY_MASS",
    "MINIMIZE_TURNAROUND_TIME"
  ],
  "required_capabilities": ["CARGO_TRANSFER", "DOCKING"]
}
```

Objective priorities remain explicit and ordered. v0.1 does not convert them into hidden scalar weights.

## 5. Functional request surface

The v0.1 ship adapter accepts the following direct request fields:

```text
cargo_mass_t
cargo_volume_m3
passengers
crew
endurance_days
normal_acceleration_g
emergency_acceleration_g
delta_v_km_s
docking_ports
planetary_landing_required
max_dry_mass_t
max_length_m
```

These are translated directly to typed solver-facing requirements with `MIN`, `MAX` or `EXACT` relations.

No additional physics is inferred during translation.

## 6. Engineering derivation rules

v0.1 deliberately supports only transparent one-input affine rules:

```text
output = input × coefficient + offset
```

Every rule records:

```text
rule_id
input_requirement_id
output_requirement_id
coefficient
offset
output_unit
output_relation
authority_status
provenance
```

This simple rule type is not intended to be the final multiphysics requirements engine. It is an auditable first step that proves the architecture without embedding hidden empirical assumptions.

Future compilers may support governed multi-input equations, catalog lookups, nonlinear physical models, discrete architecture rules and solver-backed derived requirements behind stable interfaces.

## 7. Determinism

The compiler:

- validates all values fail-closed;
- rejects negative/NaN inputs;
- rejects duplicate direct requirement IDs;
- rejects duplicate derivation-rule IDs;
- permits only one rule per derived output in v0.1;
- sorts canonical output deterministically;
- hashes canonical inputs;
- produces byte-equivalent canonical JSON for equivalent input ordering.

## 8. Input file

A complete request can be supplied as JSON using:

```text
qualification/synthesis/SHIP_DESIGN_REQUEST_EXAMPLE_FREIGHTER_v0.1.json
```

and compiled with:

```bash
python qualification/synthesis/ship_design_request.py qualification/synthesis/SHIP_DESIGN_REQUEST_EXAMPLE_FREIGHTER_v0.1.json
```

The checked-in example deliberately supplies no engineering derivation rules. Therefore requested downstream quantities such as habitable volume, life-support power, radiator area, power generation, remass and structural capacity remain explicit `OPEN` derivations.

That behavior is intentional.

## 9. Relationship to Wayfarer S1/S2

Wayfarer S1/S2 begin downstream with a largely fixed vehicle inventory and selected placement variables.

The Requirements Compiler adds the missing upstream chain:

```text
MISSION / CLASS REQUEST
        ↓
COMPILED ENGINEERING REQUIREMENTS
        ↓
COMPONENT SELECTION + DESIGN GRAMMAR
        ↓
WAYFARER-STYLE PHYSICAL SYNTHESIS
```

This increment does not retrofit Wayfarer S1/S2 or change their qualification result.

## 10. Next research increments

Before increasing component placement degrees of freedom substantially, the synthesis program should add governed adapters for:

1. component selection from compiled requirements;
2. technology-context engineering rules;
3. industrial-context availability/manufacturing constraints;
4. multi-input physical derivations;
5. capability satisfaction reporting;
6. requirement-to-component provenance chains;
7. Pareto/objective-set generation rather than one hidden scalar score.

Only then should broad translation, rotation, resizing, multiplicity and topology freedom be opened aggressively.

## 11. Classification

This increment is:

```text
EXTERNAL / INTERNAL ENGINEERING RESEARCH
NON_CANON
NON_PRODUCTION
NO_FLIGHT_DYNAMICS_AUTHORITY
NO_SHIPCLASS_PROMOTION
```

It changes the architecture of the research synthesizer only.
