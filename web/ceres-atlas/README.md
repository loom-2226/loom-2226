# Private Ceres Atlas — Prototype 08R

**Primary class:** `class:runtime`

**Affected read-only boundaries:** `class:data` (WORLD and CIVSTATE queries) and
`class:asset-media` (approved MEDIA blobs). No schema, migration, canon, frozen
research, public Inspector, release, deployment, or design-system files are changed.

The private launcher exposes a fixed Ceres dossier projection at
`/atlas-data.json`. The browser cannot submit SQL or access SQLite files. The
server opens WORLD, CIVSTATE, and MEDIA through SQLite URI `mode=ro&immutable=1`.
Missing databases, rows, or verified images remain unavailable; repository image
fallbacks and stale analytical values are not used.

## Runtime source boundary

| Atlas area | Runtime source | Status |
| --- | --- | --- |
| World identity and physical environment | WORLD `entities`, `celestial_properties`, `celestial_dynamics` | Live; derived diameter, gravity, and escape speed are identified in the view |
| Facility identity | WORLD `infrastructure_nodes` | Live for the verified `CER-P01`–`CER-P05` set |
| People and census zones | CIVSTATE `civ_demographic_state`, `civ_subject`, `civ_census_node_relation` | Live; age denominators and zone reconciliation remain qualified |
| Economy and workforce | CIVSTATE `civ_economic_state`, `civ_workforce_state` | Live; monetary-unit definition remains qualified |
| Transit node measures | CIVSTATE `civ_infrastructure_state` | Live; origin–destination corridors remain unsupported pending endpoint validation |
| Systems | CIVSTATE `civ_infrastructure_state` | Live |
| Institutions | CIVSTATE `civ_subject` and `v_graph_civstate_influence_edges` | Live typed facility/institution edges |
| Society | CIVSTATE `civ_social_state`, `civ_social_pressure` | Live fictional model indices and pressure records |
| Facility runtime context | CIVSTATE `civ_runtime_place_context` plus the source tables above | Live |
| World resources and historical observation through 2026 | No approved bounded runtime projection identified | Explicitly unavailable |
| Approved imagery | WORLD `image_assets` identity + MEDIA `media_assets.original_blob` | Live after approval, identity, length, and SHA-256 verification |

All analytical rows retain their source IDs, epoch, source NULLs, derivation IDs,
and original numeric values in the server response. Body, census-zone, and
facility-node grains stay separate. The client formats values for display but
does not turn NULL into zero. Facility and institution navigation uses typed
`NODE:*` and `NOUN:*` identifiers from the CIVSTATE relationship view.

The fixed approved-media manifest remains an allowlist for the Ceres HERO and five
facility HERO identities. Its SHA-256 is
`6ae473bf6b6063b17a08e876d7b0057166135d397ce56e276423d319a44ccd81`.

## Launch on Pixel

From the repository root in Termux:

```sh
python -B tools/serve_ceres_atlas.py \
  --world-db data/LOOM_2226.sqlite3 \
  --civstate-db data/LOOM_2226_CIVSTATE.sqlite3 \
  --media-db /storage/emulated/0/Download/LOOM_TEST/data/LOOM_2226_media.sqlite3
```

Open `http://127.0.0.1:8768/` in Chrome. Keep Termux running; Ctrl+C stops the
server. `--port 8769` selects another loopback port. Database paths are command-line
configuration and no Pixel path is embedded in application logic. No internet
connection is required.

## Container qualification

The Docker image is a private qualification artifact. It contains the Python
server, UI, LOOM wordmark, and verified identity manifest only. It does not
contain WORLD, CIVSTATE, MEDIA, repository PNGs, credentials, or campaign state.
Mount all three databases read-only and keep the database paths configurable:

```sh
docker build --tag loom-ceres-atlas:qualification .
docker run --rm --read-only --tmpfs /tmp:rw,nosuid,nodev,size=64m \
  --publish 8768:8768 \
  --volume /path/to/world.sqlite3:/data/world.sqlite3:ro \
  --volume /path/to/civstate.sqlite3:/data/civstate.sqlite3:ro \
  --volume /path/to/media.sqlite3:/data/media.sqlite3:ro \
  --env CERES_WORLD_DB=/data/world.sqlite3 \
  --env CERES_CIVSTATE_DB=/data/civstate.sqlite3 \
  --env CERES_MEDIA_DB=/data/media.sqlite3 \
  loom-ceres-atlas:qualification
```

The image uses the pinned Python base digest recorded in `Dockerfile`, performs
fail-closed startup verification with `--verify-startup`, and exposes `/healthz`.
The dedicated GitHub Actions job builds this image, inspects its contents, mounts
disposable representative databases, runs the existing Python/JavaScript checks,
and runs all seven Playwright cases against the running container. It has
`contents: read` only and does not push to GHCR or deploy Pages.

## Validation

```sh
python -B -m pytest -p no:cacheprovider \
  tests/test_ceres_atlas_server.py \
  tests/test_ceres_browser_tap.py \
  tests/test_database_data_dictionary.py -q
node --test tests/ceres_atlas_model.test.mjs
node --test tests/ceres_atlas_browser.test.mjs
```

The server suite covers representative SQL values, typed joins, NULL and numeric
zero preservation, missing databases/rows, all six MEDIA blobs, read-only source
hashes, and a disposable CIVSTATE-copy mutation that changes the HTTP response
without a frontend edit. The browser suite is real verification only when all seven
tests execute; local skips are recorded as unverified in `VALIDATION.md`.

## Existing semantic coverage discrepancy

`tests/test_database_semantic_coverage.py:34` expects `tables` to be a list of
records with `database`, `table`, and `schema_columns`. The committed semantic
index instead contains a database-name to table-name-list mapping. Its `main()` is
not collected by pytest. This unrelated registry/checker discrepancy remains
outside the Atlas runtime change and is not treated as semantic-coverage acceptance.
