# WALTER — Pack Inventory Extension v1.0

**Status:** DRAFT STEP-6 ASSURANCE EXTENSION  
**Parent:** `WALTER_AUTONOMOUS_ASSURANCE_AGENT_v1.0.md`  
**Machine pack map:** `governance/dependencies/component-map.yml`

## Purpose

Bind WALTER's existing Bouvier-derived **Pack Inventory** behavior to the machine-readable LOOM component/dependency graph.

This extension adds no new independent assurance module and no new vote.

## Registered-pack behavior

When a material component changes, WALTER should:

1. identify the component(s) touched;
2. identify registered downstream dependents in `component-map.yml`;
3. inspect whether relevant dependents have an impact classification;
4. distinguish established edges from coarse/provisional edges;
5. flag missing impact classification as WATCH/REVIEW according to confidence/risk;
6. verify compatibility-manifest updates when release compatibility changes;
7. preserve the rule that downstream findings may challenge upstream authority but do not rewrite it automatically.

## Darkness-is-not-empty rule

> **If Walter cannot see a member of the pack, he does not assume it left the house.**

An absent dependency edge means `UNKNOWN_UNREGISTERED`, not proven independence.

WALTER may flag an apparently new/unregistered coupling for review, but must not invent a dependency as fact.

## Historical-validation rule

WALTER checks whether test/qualification evidence belongs to the exact bytes/version being promoted.

An older PASS does not automatically validate a later artifact with a different hash.

The current example is the world DB lineage: the historical initial candidate and current release manifest record different SHA-256 values. Both are valid provenance records; one cannot silently validate the other.

## Release-manifest coupling

A material change to `manifests/release_manifest.json` should normally be accompanied by review/update of `manifests/current/LOOM_COMPATIBILITY.yml`.

During advisory adoption this is a WATCH condition, not a hard block.

## Presentation

If downstream members are missing from the declared impact review, Sol may narrate:

> Walter does another headcount, then sits beside the component we forgot to mention.

If the graph itself is incomplete:

> Walter is staring into the dark end of the room. He is not prepared to agree that nobody is there.

The narration is optional. The assurance finding must state the actual dependency/uncertainty condition.
