from __future__ import annotations

import json
import os
import shutil
import sqlite3
import subprocess
import sys
import threading
import webbrowser
import zipfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

APP_VERSION = "LOOM_COMPUTATIONAL_SHIPYARD_PIXEL_v0.1"
DEFAULT_PORT = 2227
LEDGER_NAME = "shipyard_design_ledger.sqlite3"
SOURCE_LEDGER_NAMES = ("wayfarer_phase1_design_ledger.sqlite3", LEDGER_NAME)
VIEWER_NAME = "wayfarer_governed_synthesis.html"


def downloads_root() -> Path:
    override = os.environ.get("LOOM_SHIPYARD_DOWNLOADS")
    if override:
        return Path(override).expanduser().resolve()
    termux = Path.home() / "storage" / "downloads"
    if termux.exists():
        return termux.resolve()
    android = Path("/storage/emulated/0/Download")
    if android.exists():
        return android
    return Path.cwd().resolve()


def runtime_root() -> Path:
    override = os.environ.get("LOOM_SHIPYARD_HOME")
    root = Path(override).expanduser() if override else downloads_root() / "LOOM_SHIPYARD"
    return root.resolve()


def _valid_ledger(path: Path) -> bool:
    if not path.is_file():
        return False
    try:
        con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
        try:
            tables = {row[0] for row in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            return {"design_run", "design_state", "discipline_result", "dependency_graph", "derived_artifact"}.issubset(tables)
        finally:
            con.close()
    except sqlite3.Error:
        return False


def discover_ledger() -> Path | None:
    here = Path(__file__).resolve().parent
    roots = (here, downloads_root(), runtime_root())
    for root in roots:
        for name in SOURCE_LEDGER_NAMES:
            candidate = root / name
            if _valid_ledger(candidate):
                return candidate
    for root in roots:
        if not root.exists():
            continue
        for zpath in sorted(root.glob("*.zip")):
            try:
                with zipfile.ZipFile(zpath) as zf:
                    for member in sorted(zf.namelist()):
                        if Path(member).name not in SOURCE_LEDGER_NAMES:
                            continue
                        out_dir = runtime_root() / "import"
                        out_dir.mkdir(parents=True, exist_ok=True)
                        out = out_dir / "wayfarer_phase1_design_ledger.sqlite3"
                        with zf.open(member) as src, out.open("wb") as dst:
                            shutil.copyfileobj(src, dst)
                        if _valid_ledger(out):
                            return out
            except (zipfile.BadZipFile, OSError):
                continue
    return None


def active_ledger_path() -> Path:
    return runtime_root() / LEDGER_NAME


def activate_baseline(source: Path | None = None) -> Path:
    source = source or discover_ledger()
    if source is None:
        raise FileNotFoundError("No Phase-1 design ledger found in this package or Downloads")
    target = active_ledger_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    if source.resolve() != target.resolve():
        shutil.copy2(source, target)
    if not _valid_ledger(target):
        raise RuntimeError("Activated ledger failed schema validation")
    return target


def _connect(path: Path | None = None) -> sqlite3.Connection:
    path = path or active_ledger_path()
    if not _valid_ledger(path):
        raise FileNotFoundError("No active Shipyard ledger. Choose option 1 first.")
    con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    return con


def current_design(path: Path | None = None) -> dict:
    con = _connect(path)
    try:
        row = con.execute("SELECT state_id,candidate_id,state_kind,state_hash,state_json FROM design_state ORDER BY rowid DESC LIMIT 1").fetchone()
        if row is None:
            return {}
        state = json.loads(row["state_json"])
        disciplines = [dict(r) for r in con.execute("SELECT discipline_id,model_id,model_version,fidelity_class,result_status,authority_status FROM discipline_result WHERE state_id=? ORDER BY discipline_id", (row["state_id"],))]
        return {
            "state_id": row["state_id"], "candidate_id": row["candidate_id"], "state_kind": row["state_kind"], "state_hash": row["state_hash"],
            "structure_qualification": state.get("structure", {}).get("qualification_status", "OPEN"),
            "packaging_open": list(state.get("packaging", {}).get("open_items", [])),
            "disciplines": disciplines,
        }
    finally:
        con.close()


def dependency_graph(path: Path | None = None) -> dict:
    con = _connect(path)
    try:
        row = con.execute("SELECT graph_json FROM dependency_graph ORDER BY rowid DESC LIMIT 1").fetchone()
        return json.loads(row[0]) if row else {}
    finally:
        con.close()


def design_history(path: Path | None = None) -> list[dict]:
    con = _connect(path)
    try:
        return [dict(r) for r in con.execute("SELECT state_id,candidate_id,parent_state_id,state_kind,state_hash FROM design_state ORDER BY rowid")]
    finally:
        con.close()


def open_items(path: Path | None = None) -> list[str]:
    out = []
    state = current_design(path)
    out.extend(state.get("packaging_open", []))
    graph = dependency_graph(path)
    for edge in graph.get("edges", []):
        if edge.get("status") == "OPEN":
            out.append(f"DEPENDENCY::{edge.get('edge_id')}::{edge.get('quantity')}")
    for row in state.get("disciplines", []):
        if row.get("result_status") == "OPEN":
            out.append(f"DISCIPLINE::{row.get('discipline_id')}")
    return out


def viewer_path() -> Path | None:
    here = Path(__file__).resolve().parent
    for candidate in (here / VIEWER_NAME, runtime_root() / VIEWER_NAME, downloads_root() / VIEWER_NAME):
        if candidate.is_file():
            return candidate
    return None


def _open_url(url: str) -> None:
    try:
        subprocess.run(["termux-open-url", url], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return
    except FileNotFoundError:
        pass
    webbrowser.open(url)


def serve_viewer(path: Path, port: int = DEFAULT_PORT) -> None:
    content = path.read_bytes()
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path in ("/", "/index.html"):
                self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8"); self.send_header("Content-Length", str(len(content))); self.end_headers(); self.wfile.write(content)
            elif self.path == "/favicon.ico":
                self.send_response(204); self.end_headers()
            else:
                self.send_error(404, "Not found")
        def log_message(self, fmt, *args):
            print("[SHIPYARD HTTP] " + (fmt % args))
    server = ThreadingHTTPServer(("127.0.0.1", int(port)), Handler)
    url = f"http://127.0.0.1:{int(port)}/"
    print(f"VIEWER: {path}")
    print(f"LOCAL URL: {url}")
    print("NETWORK: loopback only; no internet required")
    _open_url(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nViewer stopped.")
    finally:
        server.server_close()


def _print_current() -> None:
    state = current_design()
    if not state:
        print("No design state found."); return
    print(f"STATE: {state['state_id']}")
    print(f"CANDIDATE: {state['candidate_id']}")
    print(f"KIND: {state['state_kind']}")
    print(f"HASH: {state['state_hash']}")
    print(f"STRUCTURE: {state['structure_qualification']}")
    print(f"PACKAGING OPEN: {len(state['packaging_open'])}")
    for row in state["disciplines"]:
        print(f"DISCIPLINE: {row['discipline_id']} | {row['fidelity_class']} | {row['result_status']} | {row['model_id']} {row['model_version']}")


def _print_graph() -> None:
    graph = dependency_graph()
    print(f"GRAPH: {graph.get('graph_id', 'NONE')}")
    print(f"COUPLED PHYSICS: {graph.get('coupled_physics_status', 'OPEN')}")
    for edge in graph.get("edges", []):
        print(f"{edge['status']:8} {edge['source_node_id']} -> {edge['target_node_id']} | {edge['quantity']}")


def menu() -> None:
    while True:
        print("\nLOOM COMPUTATIONAL SHIPYARD")
        print("===========================")
        print(f"{APP_VERSION} | RESEARCH / NON-CANON / NON-PRODUCTION")
        print(f"HOME: {runtime_root()}")
        print("1. Activate / refresh Wayfarer Phase-1 baseline")
        print("2. Inspect current design state")
        print("3. Show engineering dependency graph")
        print("4. Show OPEN engineering items")
        print("5. Show design history")
        print("6. Launch 3D viewer")
        print("7. Exit")
        choice = input("> ").strip()
        try:
            if choice == "1": print(f"ACTIVE LEDGER: {activate_baseline()}")
            elif choice == "2": _print_current()
            elif choice == "3": _print_graph()
            elif choice == "4":
                rows = open_items(); print(f"OPEN ITEMS: {len(rows)}"); [print(f"- {x}") for x in rows]
            elif choice == "5":
                for row in design_history(): print(f"{row['state_id']} | {row['candidate_id']} | parent={row['parent_state_id']} | {row['state_kind']}")
            elif choice == "6":
                vp = viewer_path()
                if vp is None: print("3D viewer not found beside launcher or in Downloads.")
                else: serve_viewer(vp)
            elif choice == "7": return
            else: print("Choose 1-7.")
        except Exception as exc:
            print(f"SHIPYARD ERROR: {type(exc).__name__}: {exc}")


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv == ["--status"]:
        source = discover_ledger()
        print(json.dumps({"version": APP_VERSION, "downloads": str(downloads_root()), "runtime": str(runtime_root()), "ledger_source": str(source) if source else None, "active_ledger": str(active_ledger_path()), "viewer": str(viewer_path()) if viewer_path() else None}, sort_keys=True))
        return 0
    menu(); return 0


if __name__ == "__main__":
    raise SystemExit(main())
