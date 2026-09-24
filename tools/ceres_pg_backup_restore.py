#!/usr/bin/env python3
"""Dump and restore the development Ceres slice into a disposable PostgreSQL database."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import tempfile
from pathlib import Path

import ceres_pg

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ("loom_control", "loom_world", "loom_civ", "loom_media", "loom_ceres")


def command(*args: str) -> str:
    result = subprocess.run(args, text=True, capture_output=True, check=False)
    if result.returncode:
        raise RuntimeError(f"{args[0]} failed: {result.stderr.strip()}")
    return result.stdout.strip()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", default="loom_dev")
    parser.add_argument("--media-db", type=Path, default=ceres_pg.SOURCE_PATHS["MEDIA"])
    parser.add_argument("--backup", type=Path, default=Path("/tmp/loom_ceres_dev_backup.dump"))
    parser.add_argument("--report", type=Path, default=ROOT / "docs/database_semantics/LOOM_CERES_POSTGRES_DEV_BACKUP_RESTORE_v0.1.json")
    args = parser.parse_args()
    if args.database.startswith("loom_ceres_restore_test_"):
        raise RuntimeError("Source database cannot be a disposable restore target")
    spec = ceres_pg.contract()
    paths = {**ceres_pg.SOURCE_PATHS, "MEDIA": args.media_db}
    ceres_pg.validate_inputs(spec, paths)
    selected, manifest = ceres_pg.selected_rows(spec, paths)
    backup = args.backup.resolve()
    backup.parent.mkdir(parents=True, exist_ok=True)
    dump_args = ["pg_dump", "-Fc", "-d", args.database, "-f", str(backup)]
    for schema in SCHEMAS:
        dump_args += ["-n", schema]
    command(*dump_args)
    command("pg_restore", "-l", str(backup))
    restore_db = f"loom_ceres_restore_test_{os.getpid()}"
    created = False
    try:
        owner = ceres_pg.psql(args.database, "SELECT current_user")
        try:
            command("createdb", "-T", "template0", restore_db)
        except RuntimeError as error:
            if "permission denied to create database" not in str(error):
                raise
            # The development role owns loom_dev but does not have CREATEDB.
            # Local admin creates only this disposable database, owned by that role.
            command("sudo", "-n", "-u", "postgres", "createdb", "-O", owner,
                    "-T", "template0", restore_db)
        created = True
        command("pg_restore", "--no-owner", "--no-acl", "--exit-on-error", "-d", restore_db, str(backup))
        with tempfile.TemporaryDirectory(prefix="loom_ceres_restore_") as directory:
            coverage = ceres_pg.verify(restore_db, spec, paths, selected, manifest,
                                       ceres_pg.snapshot_id(spec), Path(directory) / "coverage.json")
        if coverage["status"] != "PASS":
            raise RuntimeError(f"Restored snapshot coverage failed: {coverage['discrepancies']}")
        result = {"status": "PASS", "source_database": args.database,
                  "restored_database": restore_db, "restored_database_disposition": "dropped after verification",
                  "backup_path": str(backup), "backup_sha256": ceres_pg.sha256(backup),
                  "backup_size_bytes": backup.stat().st_size,
                  "snapshot_id": coverage["snapshot_id"],
                  "restored_atlas_payload_exact_match": coverage["atlas_payload"]["exact_match"],
                  "restored_source_row_lineage": coverage["row_lineage"]["source_rows"],
                  "restored_foreign_keys_validated": coverage["referential_integrity"]["all_validated"]}
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result, indent=2) + "\n")
        print(json.dumps(result))
    finally:
        if created:
            command("dropdb", restore_db)


if __name__ == "__main__":
    main()
