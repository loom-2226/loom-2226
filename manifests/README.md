# LOOM Runtime Manifests

Release manifests pin the exact runtime artifacts distributed by the updater.

For each artifact, the manifest records its source, install group, required state, byte size where applicable, and SHA-256 digest. Repository and release-asset payloads must match these values exactly before installation.

The runtime manifest is a deployment integrity record. Canon authority is governed separately under `governance/` and `canon/`.
