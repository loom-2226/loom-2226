# Build 8 G2: authenticated WORLD identity and GENESIS-only epoch
class: engineering
Status: PROPOSAL FIRST / DRAFT PR / NON-CANON / NOT QUALIFICATION
Base: 19377b854c529e74afc61202d9eb2e780c5b4884

## Exact permission
Only install/reopen a genuinely generated 2026 WORLD in a disposable
pinned PostgreSQL 18.6 instance, bind its authenticated scenario identity
into authored G1 BEFORE final opening identity, persist one GENESIS-only
first epoch via unchanged run_epoch / stage_epoch, reconstruct and
verify ALREADY_MATCHED. No decision, mission, payment, observation,
belief update, WALTER, frozen edit or compiler copy.

## Authored experiment input contract
All choices live in a single hashed Build 8 scenario, including origin
and effective value of inherited inputs. Hash and print the full
non-secret scenario and resolved parameter values. WORLD seed is only
an authored reference plus SHA-256 digest, never raw seed in scenario,
command logs, worker wire, PR, report or user response. A trusted local
resolver must produce exactly those private bytes and check the digest.
No invented scenario UUID or authentication claim. Resolve the WORLD
scenario ID from the actually installed generator result, assert its
installed identity, bind BEFORE computing final run identity.

## Disposable database preflight
Exactly the digest-pinned postgres:18.6 image from #414:
sha256:5a5a84b19854a9ffaa54082c166ff4ec27473a361e496e5ea167f298f2da9722
No substitute if unavailable. Separate temporary container, filesystem
and service file, local-only unused port, ephemeral role credentials,
unchanged migrations, never connect to preexisting databases. Check
exact database and session principal. Cleanup even after failures.

## PASS
- Authenticated installed 2026 WORLD + consistent body catalog, no
  sealed truth exposure and no seed exposure.
- Single source-backed G1 private SPN opening; all effective parameters
  and pins printed, seed only redacted reference+digest.
- GENESIS-only original envelope, no dummy scheduled action, receipt,
  decision, transaction or observation.
- Unchanged compiler returns full first-epoch row batch with genuine
  terminal originals; store reports COMMITTED.
- Rebuild from same authored scenario and authenticated WORLD, exact
  run identity and same original hashes; unchanged store reports
  ALREADY_MATCHED; persisted row count and trace head unchanged.
- Isolated PostgreSQL removed including credentials and service file.
- Total new executable and focused tests about 350 lines or fewer.

## FAIL / STOP
If pinned image unavailable; any need to invent WORLD ID, binding,
seed, receipt or dummy transition; source/seed digest mismatch; policy
or schema PIN mismatch; changed frozen file; compiler copy; any sealed
WORLD data in logs/reports; first rejected compiler/store contract
cannot be met narrowly; replay differs. Record only error identifier
and public structural counts; stop without initiating Gate B/C.
