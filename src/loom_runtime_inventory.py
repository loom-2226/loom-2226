#!/usr/bin/env python3
"""LOOM 2226 runtime inventory v1.0.

Read-only forensic inventory of a LOOM installation. Produces JSON + Markdown.
No database writes, no file modifications except the requested output files.
"""
from __future__ import annotations
import argparse, hashlib, json, os, platform, sqlite3, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

VERSION = "1.0"
DEFAULT_EXCLUDE_DIRS = {".loom_backups", ".git", "__pycache__", "ephemeris_cache"}
DEFAULT_EXCLUDE_SUFFIXES = {".pyc"}
DB_SUFFIXES = {".sqlite", ".sqlite3", ".db"}


def sha256_file(path: Path, chunk: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def safe_git(root: Path, *args: str):
    if not (root / ".git").exists():
        return None
    try:
        p = subprocess.run(["git", "-C", str(root), *args], text=True,
                           capture_output=True, timeout=20)
        return {"returncode": p.returncode, "stdout": p.stdout.strip(),
                "stderr": p.stderr.strip()}
    except Exception as e:
        return {"error": repr(e)}


def sqlite_summary(path: Path) -> dict:
    out = {"path": str(path), "tables": [], "error": None}
    try:
        uri = f"file:{path.as_posix()}?mode=ro"
        con = sqlite3.connect(uri, uri=True)
        try:
            tables = [r[0] for r in con.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")]
            for name in tables:
                q = 'SELECT COUNT(*) FROM "' + name.replace('"', '""') + '"'
                try:
                    count = con.execute(q).fetchone()[0]
                except Exception as e:
                    count = None
                    count_error = repr(e)
                else:
                    count_error = None
                cols = []
                try:
                    for r in con.execute('PRAGMA table_info("' + name.replace('"', '""') + '")'):
                        cols.append({"name": r[1], "type": r[2], "notnull": bool(r[3]),
                                     "default": r[4], "pk": bool(r[5])})
                except Exception:
                    pass
                row = {"name": name, "row_count": count, "columns": cols}
                if count_error:
                    row["count_error"] = count_error
                out["tables"].append(row)
        finally:
            con.close()
    except Exception as e:
        out["error"] = repr(e)
    return out


def iter_files(root: Path, include_backups: bool):
    for base, dirs, files in os.walk(root):
        basep = Path(base)
        excluded = set(DEFAULT_EXCLUDE_DIRS)
        if include_backups:
            excluded.discard(".loom_backups")
        dirs[:] = sorted(d for d in dirs if d not in excluded)
        for name in sorted(files):
            p = basep / name
            if p.suffix.lower() in DEFAULT_EXCLUDE_SUFFIXES:
                continue
            yield p


def inventory(root: Path, source_root: Path | None, hash_all: bool, include_backups: bool) -> dict:
    root = root.resolve()
    now = datetime.now(timezone.utc).isoformat()
    files = []
    dbs = []
    total = 0
    for p in iter_files(root, include_backups):
        try:
            st = p.stat()
            rel = p.relative_to(root).as_posix()
            rec = {"path": rel, "size_bytes": st.st_size,
                   "mtime_utc": datetime.fromtimestamp(st.st_mtime, timezone.utc).isoformat()}
            # Hash authoritative/deployable material by default; --hash-all hashes everything.
            should_hash = hash_all or rel.startswith(("src/", "data/", "deploy/", "manifests/")) or p.name.startswith("LOOM_STATE")
            if should_hash:
                rec["sha256"] = sha256_file(p)
            files.append(rec)
            total += st.st_size
            if p.suffix.lower() in DB_SUFFIXES:
                dbs.append(sqlite_summary(p))
        except Exception as e:
            files.append({"path": str(p), "error": repr(e)})

    manifest = None
    for candidate in (root / "manifests" / "release_manifest.json", root / ".loom_install_state.json"):
        if candidate.exists():
            try:
                manifest = {"path": str(candidate), "content": json.loads(candidate.read_text(encoding="utf-8"))}
                break
            except Exception as e:
                manifest = {"path": str(candidate), "error": repr(e)}

    src = source_root.resolve() if source_root else None
    return {
        "inventory_format": "LOOM_RUNTIME_INVENTORY_V1",
        "tool_version": VERSION,
        "generated_utc": now,
        "runtime_root": str(root),
        "source_root": str(src) if src else None,
        "host": {"platform": platform.platform(), "python": sys.version,
                 "machine": platform.machine()},
        "release_or_install_state": manifest,
        "runtime_git": safe_git(root, "status", "--short", "--branch"),
        "source_git_status": safe_git(src, "status", "--short", "--branch") if src else None,
        "source_git_head": safe_git(src, "rev-parse", "HEAD") if src else None,
        "file_count": len(files),
        "total_bytes": total,
        "files": files,
        "sqlite_databases": dbs,
        "exclusions": sorted(DEFAULT_EXCLUDE_DIRS if not include_backups else DEFAULT_EXCLUDE_DIRS - {".loom_backups"}),
        "notes": [
            "Inventory is read-only except for its output files.",
            "Excluded caches/backups are not evidence of absence; they are intentionally omitted unless requested.",
            "SQLite schemas/counts are obtained using read-only connections.",
        ],
    }


def markdown(inv: dict) -> str:
    lines = ["# LOOM Runtime Inventory", "", f"Generated: `{inv['generated_utc']}`",
             f"Runtime root: `{inv['runtime_root']}`", f"Source root: `{inv['source_root']}`",
             f"Files inventoried: **{inv['file_count']}**", f"Bytes inventoried: **{inv['total_bytes']:,}**", ""]
    state = inv.get("release_or_install_state")
    if state:
        lines += ["## Release / install state", "", f"Source: `{state.get('path')}`", ""]
        c = state.get("content", {})
        for k in ("release_id", "source_ref", "release_state", "civstate_schema"):
            if k in c:
                lines.append(f"- **{k}:** `{c[k]}`")
        lines.append("")
    lines += ["## SQLite databases", ""]
    for db in inv.get("sqlite_databases", []):
        lines.append(f"### `{db['path']}`")
        if db.get("error"):
            lines.append(f"Error: `{db['error']}`")
        else:
            lines.append(f"Tables: **{len(db['tables'])}**")
            lines.append("")
            lines.append("| Table | Rows |")
            lines.append("|---|---:|")
            for t in db["tables"]:
                lines.append(f"| `{t['name']}` | {t['row_count']} |")
        lines.append("")
    lines += ["## Files", "", "| Path | Bytes | SHA-256 |", "|---|---:|---|"]
    for f in inv["files"]:
        lines.append(f"| `{f.get('path','')}` | {f.get('size_bytes','')} | `{f.get('sha256','')}` |")
    return "\n".join(lines) + "\n"


def main():
    script_root = Path(__file__).resolve().parent.parent
    ap = argparse.ArgumentParser(description="Create a read-only LOOM runtime inventory")
    ap.add_argument("--root", default=str(script_root), help="Installed LOOM runtime root")
    ap.add_argument("--source-root", help="Optional Git/source checkout root")
    ap.add_argument("--out-dir", help="Output directory; default <root>/inventory")
    ap.add_argument("--hash-all", action="store_true", help="SHA-256 every included file")
    ap.add_argument("--include-backups", action="store_true", help="Include .loom_backups")
    a = ap.parse_args()
    root = Path(a.root)
    out = Path(a.out_dir) if a.out_dir else root / "inventory"
    out.mkdir(parents=True, exist_ok=True)
    inv = inventory(root, Path(a.source_root) if a.source_root else None, a.hash_all, a.include_backups)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    jp = out / f"LOOM_RUNTIME_INVENTORY_{stamp}.json"
    mp = out / f"LOOM_RUNTIME_INVENTORY_{stamp}.md"
    jp.write_text(json.dumps(inv, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    mp.write_text(markdown(inv), encoding="utf-8")
    print("LOOM RUNTIME INVENTORY v" + VERSION)
    print("ROOT", root)
    print("FILES", inv["file_count"])
    print("BYTES", inv["total_bytes"])
    print("DATABASES", len(inv["sqlite_databases"]))
    print("JSON", jp)
    print("MARKDOWN", mp)

if __name__ == "__main__":
    main()
