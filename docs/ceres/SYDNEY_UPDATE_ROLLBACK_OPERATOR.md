# Sydney Ceres immutable update and exact rollback

**Primary class:** `class:runtime`. This is manual, offline-first tooling for Issue
#255. It is not deployment approval and has not contacted Sydney.

## Boundary and compatibility

The implementation is limited to `deploy/ceres_sydney_release.py` and its tests.
It does not change schemas, database bytes, media, the Ceres image, launchers,
updaters, workflows, Tailscale, ingress, secrets, or infrastructure. WORLD,
CIVSTATE, and MEDIA remain external immutable/read-only inputs. Pixel and Windows
are `UNCHANGED_COMPATIBLE`; the private container release path is
`REVALIDATION_REQUIRED` for every candidate. GitHub/GHCR and Docker remain the
existing external dependencies; no new dependency is introduced.

The current topology is one container on one loopback port. Replacement therefore
requires a separately approved maintenance window. The bounded reversible action
is: retain the old image and backups, stop/remove the old container, start the
candidate on the same loopback port, qualify it, and on any failure recreate the
old digest with the captured configuration. The tool must stop if rollback itself
fails. It never invents a second port, proxy, hostname, or public listener.

## Release file (nonsecret)

Create a task-local JSON file outside Git with:

```json
{
  "schema_version": 1,
  "target": "SYDNEY",
  "approval": "I APPROVE THE SYDNEY CERES RELEASE DESCRIBED BY THIS FILE",
  "source_sha": "<40 lowercase hex>",
  "image": "ghcr.io/loom-2226/ceres-atlas@sha256:<64 lowercase hex>",
  "successful_ci_run_ids": [123456789],
  "provenance": {"source_sha": "<same SHA>", "image": "<same digest reference>"},
  "hostname": "<existing CERES_ALLOWED_HOSTS value>",
  "minimum_free_bytes": 2147483648,
  "databases": {
    "CERES_WORLD_DB": {"container_path": "/data/world.sqlite3", "sha256": "<hash>", "uid": 1000, "gid": 1000, "backup": {"sha256": "<same hash>", "restore_tested": true}},
    "CERES_CIVSTATE_DB": {"container_path": "/data/civstate.sqlite3", "sha256": "<hash>", "uid": 1000, "gid": 1000, "backup": {"sha256": "<same hash>", "restore_tested": true}},
    "CERES_MEDIA_DB": {"container_path": "/data/media.sqlite3", "sha256": "<hash>", "uid": 1000, "gid": 1000, "backup": {"sha256": "<same hash>", "restore_tested": true}}
  },
  "checks": {"world_identity": "CER", "civstate_identity": "BODY:CERES:CERES@2226", "media_path": "/assets/ceres-world-hero.png", "media_sha256": "<approved blob hash>"}
}
```

The approval is per file/release: changing the target, source, image, CI evidence,
data identity, hostname, or checks requires a new explicit approval. Tags and
`latest` are rejected. Never put a token, password, registry credential, database,
or backup in either JSON file.

## Evidence and offline dry run

An operator-owned collector must produce nonsecret JSON from `docker inspect`,
local file hash/stat checks, free-space checks, registry manifest/OCI source-label
verification, successful CI records, `tailscale serve status --json`, listener
inspection, and HTTP/body/media checks. The format is intentionally the direct
input checked by `validate_provenance`, `validate_runtime`, and `validate_health`;
the unit-test fixture is the executable format example. Do not copy Docker auth or
environment secrets. Funnel must be false, Serve must target
`http://127.0.0.1:8768`, and ports 80/443/8768 must not be publicly listening.

```sh
python -B deploy/ceres_sydney_release.py \
  --release /secure/operator/release.json \
  --evidence /secure/operator/evidence.json
```

A pass prints redacted `DRY_RUN_PASS` with `mutation_performed: false`. It proves
only deterministic validation of supplied offline evidence—not its freshness,
Sydney access, registry authentication, browser behavior, or release qualification.

## Future maintenance invocation

`replace()` is the executable stop/replace/rollback primitive and accepts an
injected verifier. Only during a separately authorized maintenance window, run the
same command with `--execute --timeout <seconds>`. The tool requires the operator
to retype the complete candidate digest before stopping anything. After candidate
startup and again after rollback if needed, its live verifier checks all of:

1. `/healthz` and `/` content, not status alone;
2. representative WORLD `CER` and CIVSTATE `BODY:CERES:CERES@2226` results;
3. approved MEDIA bytes, length, and SHA-256;
4. explicit operator confirmation after checking the existing private browser path
   through Tailscale Serve (the offline suite cannot fake this gate);
5. timeout handling and exact prior digest/config restoration.

If candidate verification fails, `replace()` removes it and recreates the prior
immutable image using the captured loopback binding, allowlist, mounts, read-only
root, tmpfs, and restart policy. If recreation or restored verification fails it
raises `ROLLBACK FAILED; preserve evidence`; stop, retain images/backups/logs, and
do not reopen access. No automatic SSH or CI deployment exists.

## Offline qualification

```sh
python -B -m pytest -p no:cacheprovider tests/test_ceres_sydney_release.py -q
```

The suite covers a positive dry run; approval/digest/provenance/registry failures;
absent or writable mounts; wrong identities, ownership, and permissions; public
binding and Funnel; disk; root, health, WORLD, CIVSTATE, MEDIA, and private-browser
failures; timeout; candidate rollback; and failed rollback. Mocks exercise state
transitions only and are not end-to-end Sydney qualification.

## Blocking-review corrections

The release tool now requires independently authenticated provenance flags for the
source commit, registry digest and successful CI runs. Self-consistent release and
evidence JSON without those authenticated checks fails closed.

`--execute` performs a local read-only refresh immediately before stopping the
container: `docker inspect`, free disk, listening sockets, and `tailscale serve
status --json` are re-read and compared byte-for-byte to the reviewed evidence.
Any drift aborts before mutation. This is deliberately local-only; it does not
contact Sydney.

Rollback accepts only the complete supported runtime shape: the expected read-only
root, restart policy, tmpfs, loopback binding, three read-only database binds, and
exactly the approved environment variables. Unsupported Docker options, extra
mounts, or extra environment variables fail closed before replacement. Therefore
`exact_run_args` is an exact reconstruction of the admitted canonical shape; the
tool does not claim rollback for an unrecognized configuration.
