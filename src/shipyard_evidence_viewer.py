#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
import sqlite3
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

DEFAULT_DB = Path("/storage/emulated/0/Download/LOOM_SHIPYARD/shipyard_design_ledger.sqlite3")
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 2228
AUTHORITY_BANNER = "RESEARCH EVIDENCE ONLY — NO SPATIAL ENVELOPE ADMITTED"


def _tables(con: sqlite3.Connection) -> set[str]:
    return {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}


def load_evidence(db_path: Path = DEFAULT_DB) -> dict:
    db_path = db_path.expanduser().resolve()
    if not db_path.is_file():
        raise RuntimeError(f"Shipyard editing ledger not found: {db_path}")
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    try:
        needed = {"design_state", "remass_feasibility_bound", "remass_candidate_model", "remass_candidate_comparison"}
        if not needed.issubset(_tables(con)):
            raise RuntimeError("Target is not a Phase-6 Shipyard ledger")
        state = con.execute(
            "SELECT state_id,state_hash FROM design_state WHERE state_kind='PHASE6_REMASS_CANDIDATE_SCREEN_STATE' ORDER BY rowid DESC LIMIT 1"
        ).fetchone()
        if state is None:
            raise RuntimeError("No Phase-6 remass candidate screen state found")
        bounds = {}
        for row in con.execute("SELECT source_id,bound_json FROM remass_feasibility_bound ORDER BY source_id"):
            bounds[row["source_id"]] = json.loads(row["bound_json"])
        models = {}
        for row in con.execute("SELECT candidate_id,model_json FROM remass_candidate_model ORDER BY candidate_id"):
            models[row["candidate_id"]] = json.loads(row["model_json"])
        comparisons = []
        for row in con.execute(
            "SELECT source_id,candidate_id,comparison_json,screen_status FROM remass_candidate_comparison WHERE state_id=? ORDER BY source_id,candidate_id",
            (state["state_id"],),
        ):
            payload = json.loads(row["comparison_json"])
            payload["screen_status"] = row["screen_status"]
            payload["model"] = models[row["candidate_id"]]
            comparisons.append(payload)
        if len(bounds) != 4 or len(comparisons) != 12:
            raise RuntimeError(f"Unexpected Phase-6 evidence cardinality: bounds={len(bounds)} comparisons={len(comparisons)}")
        by_tank = []
        for source_id in sorted(bounds):
            bound = bounds[source_id]
            rows = [r for r in comparisons if r["source_id"] == source_id]
            by_tank.append({"source_id": source_id, "bound": bound, "comparisons": rows})
        return {
            "state_id": state["state_id"],
            "state_hash": state["state_hash"],
            "authority_banner": AUTHORITY_BANNER,
            "tank_count": len(by_tank),
            "candidate_count": len(models),
            "comparison_count": len(comparisons),
            "tanks": by_tank,
        }
    finally:
        con.close()


def _status_label(status: str) -> str:
    return "REJECTED" if status.startswith("REJECT_") else "NOT REJECTED"


def _candidate_short(model: dict) -> str:
    mat = model.get("material", "?")
    state = model.get("storage_state", "")
    if mat == "H2O":
        return "Water"
    if mat == "CH4":
        return "Methane"
    if mat == "H2":
        return "Hydrogen"
    return f"{mat} {state}".strip()


def render_html(evidence: dict) -> str:
    tank_cards = []
    for tank in evidence["tanks"]:
        b = tank["bound"]
        max_len = float(b["max_centered_external_length_m"])
        max_vol = float(b["max_idealized_outer_cylinder_volume_m3"])
        min_density = float(b["minimum_equivalent_bulk_density_kg_m3"])
        x = float(b["anchor_x_m"])
        d = float(b["external_diameter_m"])
        candidate_rows = []
        bars = []
        for comp in tank["comparisons"]:
            model = comp["model"]
            name = _candidate_short(model)
            density = float(comp["screening_density_kg_m3"])
            fluid_vol = float(comp["ideal_fluid_volume_m3"])
            util = float(comp["outer_volume_utilization_fraction"])
            ideal_len = max_len * util
            status = _status_label(comp["screen_status"])
            candidate_rows.append(
                f"<tr><td>{html.escape(name)}</td><td>{density:.1f}</td><td>{fluid_vol:.1f}</td><td>{ideal_len:.2f}</td><td>{util*100:.1f}%</td><td class='{status.lower().replace(' ','-')}'>{status}</td></tr>"
            )
            width = min(100.0, util * 100.0)
            overflow = max(0.0, util * 100.0 - 100.0)
            bars.append(
                f"<div class='barrow'><span>{html.escape(name)}</span><div class='track'><div class='bar' style='width:{width:.2f}%'></div></div><b>{util*100:.0f}%</b>{f'<em> +{overflow:.0f}% overflow</em>' if overflow else ''}</div>"
            )
        tank_cards.append(f"""
<section class='tank'>
  <h2>{html.escape(tank['source_id'])}</h2>
  <div class='metrics'>anchor x={x:.2f} m &nbsp;|&nbsp; nominal OD={d:.2f} m &nbsp;|&nbsp; max centered length={max_len:.2f} m &nbsp;|&nbsp; ideal outer volume={max_vol:.1f} m³ &nbsp;|&nbsp; density floor={min_density:.1f} kg/m³</div>
  <div class='bound'><div class='axis'>18 m <span>allowed centered outer-envelope bound</span> 32 m</div>{''.join(bars)}</div>
  <table><thead><tr><th>Candidate</th><th>ρ kg/m³</th><th>Ideal fluid m³</th><th>Ideal fluid-only length m</th><th>Outer-volume use</th><th>Screen</th></tr></thead><tbody>{''.join(candidate_rows)}</tbody></table>
</section>""")
    return f"""<!doctype html>
<html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>
<title>LOOM Shipyard Evidence Viewer</title>
<style>
:root{{color-scheme:dark}}body{{font-family:system-ui,sans-serif;margin:0;background:#0d1117;color:#e6edf3}}main{{max-width:1100px;margin:auto;padding:16px}}h1{{font-size:1.45rem;margin:.3rem 0}}h2{{font-size:1.1rem}}.banner{{border:2px solid #f0b429;padding:10px;font-weight:800;margin:12px 0;background:#241d0d}}.sub{{color:#9da7b3;font-size:.9rem}}.tank{{border:1px solid #30363d;border-radius:10px;padding:12px;margin:14px 0;background:#161b22}}.metrics{{font-size:.86rem;color:#b8c1cc;margin-bottom:10px}}table{{width:100%;border-collapse:collapse;font-size:.82rem}}th,td{{padding:7px;border-bottom:1px solid #30363d;text-align:right}}th:first-child,td:first-child{{text-align:left}}.rejected{{color:#ff7b72;font-weight:700}}.not-rejected{{color:#7ee787;font-weight:700}}.bound{{padding:10px;border:1px dashed #59636e;border-radius:8px;margin:8px 0 12px}}.axis{{display:flex;justify-content:space-between;color:#9da7b3;font-size:.75rem;margin-bottom:8px}}.barrow{{display:grid;grid-template-columns:82px 1fr 55px auto;gap:8px;align-items:center;font-size:.78rem;margin:6px 0}}.track{{height:14px;background:#21262d;border:1px solid #59636e;overflow:hidden}}.bar{{height:100%;background:linear-gradient(90deg,#58a6ff,#7ee787)}}em{{color:#ff7b72;font-style:normal}}footer{{font-size:.75rem;color:#8b949e;margin:18px 0}}
</style></head><body><main>
<h1>LOOM 2226 — Computational Shipyard Evidence Viewer</h1>
<div class='sub'>Phase-6 state: {html.escape(evidence['state_id'])}<br>hash: {html.escape(evidence['state_hash'])}</div>
<div class='banner'>{html.escape(evidence['authority_banner'])}</div>
<p>This view shows why candidate storage media survive or fail the current <b>idealized</b> tank packaging bound. The bars are evidence overlays, not physical tank geometry. 100% is the entire currently available outer-cylinder bound; real walls, heads, ullage, plumbing, insulation and structure can only reduce usable fluid volume.</p>
{''.join(tank_cards)}
<footer>Deterministic read-only view of the local Shipyard SQLite ledger. Candidate non-rejection is not selection, admission, canon, structural qualification or flight authority.</footer>
</main></body></html>"""


def serve(db_path: Path, host: str, port: int) -> None:
    evidence = load_evidence(db_path)
    page = render_html(evidence).encode("utf-8")

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path in ("/", "/index.html"):
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(page)))
                self.end_headers()
                self.wfile.write(page)
            elif self.path == "/evidence.json":
                data = json.dumps(evidence, indent=2, sort_keys=True).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
            else:
                self.send_error(404)

        def log_message(self, fmt, *args):
            return

    server = ThreadingHTTPServer((host, port), Handler)
    print(f"SHIPYARD EVIDENCE VIEWER: http://{host}:{port}/")
    print(AUTHORITY_BANNER)
    print("Ctrl-C to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


def main() -> int:
    p = argparse.ArgumentParser(description="Read-only LOOM Shipyard Phase-6 visual evidence viewer")
    p.add_argument("--db", type=Path, default=DEFAULT_DB)
    p.add_argument("--host", default=DEFAULT_HOST)
    p.add_argument("--port", type=int, default=DEFAULT_PORT)
    p.add_argument("--dump-html", type=Path)
    args = p.parse_args()
    if args.dump_html:
        args.dump_html.write_text(render_html(load_evidence(args.db)), encoding="utf-8")
        print(args.dump_html)
        return 0
    serve(args.db, args.host, args.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
