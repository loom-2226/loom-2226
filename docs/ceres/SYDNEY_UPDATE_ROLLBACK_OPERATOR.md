# Sydney Ceres controlled update and retained-container rollback

**Primary class:** `class:runtime`. Issue #255 / PR #258; implementation and
offline qualification only. This document does not authorize Sydney access or a
release. No database, schema, campaign state, launcher, updater, workflow,
Tailscale setting, credential, image publication or infrastructure changes.
Pixel and Windows remain `UNCHANGED_COMPATIBLE`. The manual Linux release path is
`REVALIDATION_REQUIRED`. Existing external dependencies remain GitHub/GHCR,
GitHub CLI, Docker and Tailscale; the Python implementation uses the standard
library and existing Atlas read-only SQL/media verifier.

## Trust and compatibility

Offline evidence is untrusted input. A successful default invocation reports
`OFFLINE_PLAN_ONLY`, `provenance: UNVERIFIED`, `mutation_performed: false`.
It does **not** mean that a host, image or release is qualified. The old
`authentication.*_verified` and registry assertions have no authority.

Before execution the tool itself:

1. Authenticates to `github.com` through the existing `gh` credential context,
   resolves the exact source SHA, checks the actual GHCR package metadata is
   private and bound to `loom-2226/loom-2226`, and fetches every approved CI run.
   Each must belong to that repository, use `ceres-atlas-docker.yml`, run on the
   exact approved SHA, and be completed/successful (`push` or manual dispatch).
2. Invokes `gh attestation verify oci://<digest>` with the exact repository,
   signer workflow, source SHA, signer SHA, GitHub OIDC issuer and hosted-runner
   restriction. It additionally requires a verified SLSA v1 subject containing
   the approved digest and an invocation of one approved successful run attempt.
   This binds registry bytes, source and CI; labels or matching JSON strings alone
   are insufficient. No offline-bundle or unsigned fallback exists.
3. Pulls the approved digest, inspects both images, validates the prior image ID
   and inherited configuration, writes a new durable recovery record, and runs
   fresh local host checks **after** pull, prompts and record persistence.

See the [GitHub CLI verification contract](https://cli.github.com/manual/gh_attestation_verify).
The CLI must support all supplied flags. Existing authentication needs read access
to the private package and attestations; this tool never creates credentials,
logs in, changes scopes or prints command output on failure.

**Known publication gap:** the historical publication run `35415378704` has
workflow head `466dd71b9db57fc8574ade54d8d7579fa2774bdb`, while its recorded image
source is `5263648fe39efe8e7588998b9f7f92e2cf0e3bca`. That record is not accepted as
the required signed qualification binding. During this correction the digest
attestation endpoint returned HTTP 404 and package metadata returned HTTP 403
(`read:packages` unavailable). These responses do not prove absence or privacy.
The existing published image is **not qualified by this correction**. Missing
proof blocks execution; obtaining an approved signed qualification/publication
record requires separate authorization outside this PR's allowed files. No
`.github/` changes or publication are made here.

## Nonsecret release and evidence files

Prepare a reviewed release JSON outside Git with the existing schema-version 1
fields: `target: SYDNEY`, the literal approval
`I APPROVE THE SYDNEY CERES RELEASE DESCRIBED BY THIS FILE`, exact `source_sha`,
immutable `image` (`ghcr.io/loom-2226/ceres-atlas@sha256:...`),
`successful_ci_run_ids`, matching `provenance.source_sha` / `provenance.image`,
existing private `hostname` / `CERES_ALLOWED_HOSTS`, and `minimum_free_bytes`.
The redundant provenance fields remain consistency checks, never authentication.

Additional required fields:

- `host_identity`: the exact existing host's OS hostname, independently approved.
- `window_end_unix`: finite UTC Unix deadline for this approved maintenance window.
- `databases`: exactly `CERES_WORLD_DB`, `CERES_CIVSTATE_DB`, `CERES_MEDIA_DB`.
  Each has a distinct `/data/<filename>` `container_path`, approved SHA-256,
  numeric `uid`/`gid`, and `backup` with independent absolute `path`, the same
  SHA-256 and the existing `restore_tested` declaration. That declaration is not
  trusted: actual copies are restored and checked during every preflight.
- `checks`: existing verified `world_identity` (`CER`), `civstate_identity`
  (the actual `subject_id`, `BODY:CERES:CERES`, **without an epoch suffix**),
  approved `media_path` and `media_sha256`.

The nonsecret reviewed evidence includes the complete `docker inspect` object,
file hashes/owners/permissions, backup/restore records, current health evidence,
`disk_free_bytes`, raw `ss -H -ltn` output in `listeners`, and the actual
`tailscale serve status --json` object in `tailscale`. Do not use the previous
synthetic `funnel`/`serve_target` summary. The executable test fixtures document
the JSON shape; their example identities and run IDs are not real authorization.
No credentials belong in either input or a recovery record.

## Live checks and admitted runtime profile

Docker operations explicitly use the **local** Unix socket
`/var/run/docker.sock`; Docker context/remote-host environment cannot select Sydney
or another remote daemon. There is no SSH implementation.

Preflight verifies actual container identity and full persistent configuration,
read-only database binds, owner/mode/hash, absence of SQLite sidecars, disk,
Tailscale Serve targeting `http://127.0.0.1:8768`, and Funnel OFF. It checks all
three actual databases and independently copied backups through the existing
Atlas SQL and six-asset media verifier, then repeats file and host checks.
Supplied snapshots detect drift; they never replace the live checks. Concurrent
administration must be excluded throughout the approved maintenance window; this
tool cannot lock out root or another Docker administrator.

The socket parser requires `127.0.0.1:8768`. It rejects other Ceres interfaces,
IPv4/IPv6 wildcard bindings, IPv6 loopback, malformed evidence and drift in the
complete listener set. Kernel listeners on 80/443 fail closed, including private
interfaces not separately qualified here; userspace Tailscale Serve is inspected
separately. A different legitimate Serve representation needs explicit
qualification, not a permissive parser exception.

The candidate uses the existing three `:ro` binds, loopback port, allowlist,
read-only root, `/tmp:rw,nosuid,nodev,size=64m`, and `unless-stopped` policy.
The [Docker inspect schema](https://docs.docker.com/reference/api/engine/version/v1.47/)
contains many default fields. The tool admits explicitly enumerated defaults,
image-inherited environment/configuration and the above overrides. Unknown or
nondefault HostConfig options, custom network settings/hostname, extra secrets,
extra mounts, image-config overrides and `AutoRemove` fail **before stop**.
A daemon whose representation differs is unsupported until tested. Do not edit
evidence to hide fields. This is deliberately fail-closed compatibility, not a
claim that every Docker version/profile is supported.

## Commands and recovery

Offline inspection, no host/network operations:

```sh
python -B deploy/ceres_sydney_release.py \
  --release /secure/operator/release.json \
  --evidence /secure/operator/evidence.json
```

Add `--verify-provenance` for authenticated read-only GitHub/GHCR verification;
it still performs no host mutation. That flag is not deployment approval.

Only after **separate explicit release authorization**, in the approved host's
interactive terminal, the execution form adds:

```text
--execute --timeout 60 --recovery-record /secure/operator/recovery-UNIQUE.json
```

The recovery directory must be operator-owned and private (0700). The record is
created exclusively (0600), fsynced along with its directory, and never overwritten
or removed by failure handling. It preserves the prior image digest, image ID,
complete prior inspection, database/backup evidence and authenticated provenance.
The operator must retype the exact candidate digest. Noninteractive input and CI
execution (`CI` or `GITHUB_ACTIONS`) are rejected. CI tests use injected process
simulators only. An expired/insufficient window fails before stop.

Replacement stops and renames the **original container ID** to
`ceres-atlas-rollback-<original-ID-prefix>`, then starts the candidate on the same
loopback port. It never removes or reconstructs the original. The original remains
stopped after success, preserving its configuration and image reference. Existing
recovery names block a subsequent release until independently reviewed.

Candidate verification checks local health/root, representative WORLD/CIVSTATE,
approved MEDIA SHA-256 and bounded operator confirmation of private browser access.
On failure, only an identified candidate may be removed. The original is checked
for configuration drift, renamed back and restarted by its original ID. Its full
persistent inspect state is compared again, followed by health/private-access
verification. The comparison excludes runtime state/restart counters and ephemeral
network endpoints; requested network configuration remains checked. All opaque
persistent fields, Config, HostConfig, mounts, labels, image and container IDs
remain in the comparison. This preserves configuration instead of reconstructing
a subset of CLI options.

Rollback failure is a hard stop. Retain the original object, images, backups and
recovery JSON. Do not prune or force-delete a rollback object. Independent manual
recovery must compare the retained object's ID/configuration with that record,
resolve the specific failing condition, and then restore the original name and
start the same object under a new approved window. If Docker itself cannot restart
that object, exact restoration is unverified; do not recreate a subset of options
and call it exact. No ingress, Tailscale or database changes are a recovery shortcut.

## Qualification evidence and limits

Offline regression commands:

```sh
python -B -m pytest -p no:cacheprovider tests/test_ceres_sydney_release.py -q
python -B -m pytest -p no:cacheprovider tests/test_ceres_atlas_server.py tests/test_ceres_browser_tap.py tests/test_database_data_dictionary.py -q
node --test tests/ceres_atlas_model.test.mjs tests/ceres_atlas_browser.test.mjs
```

At the correction based on PR head `cfb31e8d239c4f88e00d564ac189c15b0e951db2`,
the combined Python command passed **162 tests** (101 Phase 3 regressions plus
61 existing Ceres/data-dictionary tests), with no failures or skips. Node reported
**26 passes, zero failures, seven skips**. Python AST syntax and `git diff --check`
passed. These are local results, not a successful GitHub qualification run.

Coverage includes forged provenance, authenticated record/digest/source/run/attempt
mismatches, authentication failure, package privacy failure, valid loopback and
invalid IPv4/IPv6/malformed listeners, fresh host drift, database/backup integrity,
actual SQL and media checks on disposable copies, unsupported Docker options,
image/config overrides, retained-container success, failed candidate, exact
rollback, failed rollback and preserved recovery records. Process-boundary mocks
are explicitly offline simulations, not cryptographic or Docker integration proof.

Docker is unavailable in this Termux environment; real daemon stop/rename/start
behavior and the actual Sydney configuration are unverified. Playwright is not
installed: seven browser tests remain skipped/unverified. No Sydney access,
release, merge, deployment, publication, credentials or Tailscale changes occurred.
A future independently authorized Linux qualification must test the exact Docker
version/profile, valid authenticated artifact and private browser path before
production use. This correction does not declare Phase 3 production-qualified.
