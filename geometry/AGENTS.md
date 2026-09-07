# Geometry / 3D subtree agent rules

Applies to `geometry/**` and authoritative geometry inputs consumed by Wayfarer 3D tooling.

## Authority

A mesh, render or generated JSON does not silently become ship canon.

Before changing geometry:

- identify governing canon/engineering dimensions and packaging constraints;
- identify whether the target is authoritative input, generated derivative or visual concept;
- declare Navigator/runtime/media impact where geometry feeds those systems;
- preserve recoverable predecessor state for material authoritative changes.

## Conflict rule

If 3D work reveals that the current ship cannot physically close—volume, access, radiator placement, propellant, machinery, decks, mass distribution—raise an engineering/canon finding.

Do not quietly resize the ship or hide the conflict in the mesh.

## Generated artifacts

Generated geometry outputs are non-authoritative unless explicitly registered otherwise. Regenerate from governing source rather than hand-editing derived outputs when possible.

## Adoption pause

Wayfarer 3D and geometry changes remain paused at the registered recovery point until the governance restart gate.