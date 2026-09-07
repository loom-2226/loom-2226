# Manifest subtree agent rules

Applies to `manifests/**`.

## Purpose

Manifests connect source commits, data/artifact hashes, release state and compatibility. Treat them as auditable control records, not casual documentation.

Before mutation:

- identify the source commit/ref the manifest describes;
- distinguish repository files from release assets;
- verify hashes/sizes rather than copying remembered values;
- identify compatibility/schema requirements;
- preserve predecessor manifest history where the lifecycle requires it.

## Prohibitions

- do not claim an artifact hash without verification;
- do not infer deployed bytes from a source branch when the artifact is a release asset;
- do not silently update a manifest to make mismatched artifacts look consistent;
- do not treat a generated artifact as governing source solely because the manifest lists it.

## WALTER

`WALTER.RELEASE` should treat manifest/source/hash disagreement as a material assurance condition.