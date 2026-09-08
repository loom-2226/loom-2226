from __future__ import annotations

import json
import os
import shutil
import sqlite3
import subprocess
import sys
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

APP_VERSION = "LOOM_COMPUTATIONAL_SHIPYARD_PIXEL_PHASE2_v0.1"
DEFAULT_PORT = 2227
LEDGER_NAME = "shipyard_design_ledger.sqlite3"
SOURCE_LEDGER_NAMES = ("wayfarer_phase2_design_ledger.sqlite3", LEDGER_NAME, "wayfarer_phase1_design_ledger.sqlite3")
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
            tables = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            return {"design_run","design_state","discipline_result","dependency_graph","derived_artifact"}.issubset(tables)
        finally:
            con.close()
    except sqlite3.Error:
        return False


def discover_ledger() -> Path | None:
    here = Path(__file__).resolve().parent
    for root in (here, downloads_root(), runtime_root()):
        for name in SOURCE_LEDGER_NAMES:
            p = root / name
            if _valid_ledger(p):
                return p
    return None


def active_ledger_path() -> Path:
    return runtime_root() / LEDGER_NAME


def activate_baseline(source: Path | None = None) -> Path:
    source = source or discover_ledger()
    if source is None:
        raise FileNotFoundError("No Shipyard design ledger found beside launcher or in Downloads")
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


def current_design() -> dict:
    con = _connect()
    try:
        row = con.execute("SELECT state_id,candidate_id,parent_state_id,state_kind,state_hash,state_json FROM design_state ORDER BY rowid DESC LIMIT 1").fetchone()
        if not row:
            return {}
        state = json.loads(row["state_json"])
        discs = [dict(r) for r in con.execute("SELECT discipline_id,model_id,model_version,fidelity_class,result_status,authority_status FROM discipline_result ORDER BY rowid")]
        return {"state_id":row["state_id"],"candidate_id":row["candidate_id"],"parent_state_id":row["parent_state_id"],"state_kind":row["state_kind"],"state_hash":row["state_hash"],"structure_qualification":state.get("structure",{}).get("qualification_status","OPEN"),"packaging_open":list(state.get("packaging",{}).get("open_items",[])),"phase2_count":len(state.get("phase2_functional_regions",[])),"disciplines":discs}
    finally:
        con.close()


def dependency_graph() -> dict:
    con = _connect()
    try:
        row = con.execute("SELECT graph_json FROM dependency_graph ORDER BY rowid DESC LIMIT 1").fetchone()
        return json.loads(row[0]) if row else {}
    finally:
        con.close()


def functional_regions() -> list[dict]:
    con = _connect()
    try:
        tables = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if "functional_region_contract" not in tables:
            return []
        return [dict(r) for r in con.execute("SELECT source_id,function_class,spatial_status,anchor_json,contract_json FROM functional_region_contract ORDER BY source_id")]
    finally:
        con.close()


def history() -> list[dict]:
    con = _connect()
    try:
        return [dict(r) for r in con.execute("SELECT state_id,candidate_id,parent_state_id,state_kind,state_hash FROM design_state ORDER BY rowid")]
    finally:
        con.close()


def open_items() -> list[str]:
    out = list(current_design().get("packaging_open", []))
    graph = dependency_graph()
    for edge in graph.get("edges", []):
        if edge.get("status") == "OPEN":
            out.append(f"DEPENDENCY::{edge.get('edge_id')}::{edge.get('quantity')}")
    return out


def viewer_path() -> Path | None:
    here = Path(__file__).resolve().parent
    for p in (here/VIEWER_NAME, runtime_root()/VIEWER_NAME, downloads_root()/VIEWER_NAME):
        if p.is_file():
            return p
    return None


def _open_url(url: str) -> None:
    try:
        subprocess.run(["termux-open-url", url], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return
    except FileNotFoundError:
        webbrowser.open(url)


def serve_viewer(path: Path, port: int = DEFAULT_PORT) -> None:
    content = path.read_bytes()
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path in ("/", "/index.html"):
                self.send_response(200); self.send_header("Content-Type","text/html; charset=utf-8"); self.send_header("Content-Length",str(len(content))); self.end_headers(); self.wfile.write(content)
            elif self.path == "/favicon.ico": self.send_response(204); self.end_headers()
            else: self.send_error(404,"Not found")
        def log_message(self, fmt, *args): print("[SHIPYARD HTTP] " + (fmt % args))
    server = ThreadingHTTPServer(("127.0.0.1", int(port)), Handler)
    url=f"http://127.0.0.1:{port}/"; print(f"VIEWER: {path}\nLOCAL URL: {url}\nNETWORK: loopback only; no internet required")
    _open_url(url)
    try: server.serve_forever()
    except KeyboardInterrupt: print("\nViewer stopped.")
    finally: server.server_close()


def print_current() -> None:
    s=current_design(); print(f"STATE: {s.get('state_id','NONE')}\nCANDIDATE: {s.get('candidate_id','NONE')}\nPARENT: {s.get('parent_state_id')}\nKIND: {s.get('state_kind')}\nHASH: {s.get('state_hash')}\nSTRUCTURE: {s.get('structure_qualification')}\nFUNCTIONAL REGIONS: {s.get('phase2_count',0)}\nPACKAGING OPEN: {len(s.get('packaging_open',[]))}")
    for r in s.get("disciplines",[]): print(f"DISCIPLINE: {r['discipline_id']} | {r['fidelity_class']} | {r['result_status']} | {r['model_id']} {r['model_version']}")


def print_regions() -> None:
    rows=functional_regions(); print(f"FUNCTIONAL REGIONS: {len(rows)}")
    if not rows: print("No Phase-2 functional-region contracts in active ledger."); return
    for r in rows:
        c=json.loads(r["contract_json"]); anchor=json.loads(r["anchor_json"])
        print(f"\n{r['source_id']} | {r['function_class']} | {r['spatial_status']}")
        print(f"  anchor={anchor}")
        print(f"  functions={', '.join(c['required_functions'])}")
        print(f"  adjacency={', '.join(c['adjacency_requirements']) or 'NONE'}")
        print(f"  unresolved={', '.join(c['unresolved_sizing_inputs'])}")


def menu() -> None:
    while True:
        print("\nLOOM COMPUTATIONAL SHIPYARD\n===========================")
        print(f"{APP_VERSION} | RESEARCH / NON-CANON / NON-PRODUCTION\nHOME: {runtime_root()}")
        print("1. Activate / refresh Phase-2 Wayfarer baseline\n2. Inspect current design state\n3. Show engineering dependency graph\n4. Show OPEN engineering items\n5. Show Phase-2 functional regions\n6. Show design history\n7. Launch 3D viewer\n8. Exit")
        choice=input("> ").strip()
        try:
            if choice=="1": print(f"ACTIVE LEDGER: {activate_baseline()}")
            elif choice=="2": print_current()
            elif choice=="3":
                g=dependency_graph(); print(f"GRAPH: {g.get('graph_id','NONE')}\nCOUPLED PHYSICS: {g.get('coupled_physics_status','OPEN')}"); [print(f"{e['status']:8} {e['source_node_id']} -> {e['target_node_id']} | {e['quantity']}") for e in g.get('edges',[])]
            elif choice=="4":
                rows=open_items(); print(f"OPEN ITEMS: {len(rows)}"); [print(f"- {x}") for x in rows]
            elif choice=="5": print_regions()
            elif choice=="6": [print(f"{r['state_id']} | {r['state_kind']} | parent={r['parent_state_id']}") for r in history()]
            elif choice=="7":
                vp=viewer_path(); print("3D viewer not found.") if vp is None else serve_viewer(vp)
            elif choice=="8": return
            else: print("Choose 1-8.")
        except Exception as exc: print(f"SHIPYARD ERROR: {type(exc).__name__}: {exc}")


def main(argv=None) -> int:
    argv=list(sys.argv[1:] if argv is None else argv)
    if argv==["--status"]:
        src=discover_ledger(); print(json.dumps({"version":APP_VERSION,"source":str(src) if src else None,"active":str(active_ledger_path()),"viewer":str(viewer_path()) if viewer_path() else None},sort_keys=True)); return 0
    menu(); return 0


if __name__ == "__main__": raise SystemExit(main())
