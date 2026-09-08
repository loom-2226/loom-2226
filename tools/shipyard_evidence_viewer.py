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
            raise RuntimeError("Target is not a Phase-6+ Shipyard ledger")
        state = con.execute("SELECT state_id,state_hash FROM design_state WHERE state_kind='PHASE6_REMASS_CANDIDATE_SCREEN_STATE' ORDER BY rowid DESC LIMIT 1").fetchone()
        if state is None:
            raise RuntimeError("No Phase-6 remass candidate screen state found")
        bounds = {r["source_id"]: json.loads(r["bound_json"]) for r in con.execute("SELECT source_id,bound_json FROM remass_feasibility_bound ORDER BY source_id")}
        models = {r["candidate_id"]: json.loads(r["model_json"]) for r in con.execute("SELECT candidate_id,model_json FROM remass_candidate_model ORDER BY candidate_id")}
        comparisons = []
        for row in con.execute("SELECT source_id,candidate_id,comparison_json,screen_status FROM remass_candidate_comparison WHERE state_id=? ORDER BY source_id,candidate_id", (state["state_id"],)):
            payload = json.loads(row["comparison_json"]); payload["screen_status"] = row["screen_status"]; payload["model"] = models[row["candidate_id"]]; comparisons.append(payload)
        tanks = [{"source_id": s, "bound": bounds[s], "comparisons": [r for r in comparisons if r["source_id"] == s]} for s in sorted(bounds)]
        out = {
            "state_id": state["state_id"],
            "state_hash": state["state_hash"],
            "authority_banner": AUTHORITY_BANNER,
            "tank_count": len(tanks),
            "candidate_count": len(models),
            "comparison_count": len(comparisons),
            "tanks": tanks,
        }
        if {"remass_water_closure_frontier", "remass_water_closure_probe"}.issubset(_tables(con)):
            p8 = con.execute("SELECT state_id,state_hash FROM design_state WHERE state_kind='PHASE8_WATER_CLOSURE_MAP_STATE' ORDER BY rowid DESC LIMIT 1").fetchone()
            if p8:
                frontiers = {r["source_id"]: json.loads(r["frontier_json"]) for r in con.execute("SELECT source_id,frontier_json FROM remass_water_closure_frontier WHERE state_id=?", (p8["state_id"],))}
                probes = [json.loads(r["probe_json"]) for r in con.execute("SELECT probe_json FROM remass_water_closure_probe WHERE state_id=? ORDER BY source_id,probe_id", (p8["state_id"],))]
                out["phase8"] = {"state_id": p8["state_id"], "state_hash": p8["state_hash"], "frontiers": frontiers, "probes": probes}
        return out
    finally:
        con.close()


def _short(model: dict) -> str:
    return {"H2O": "Water", "CH4": "Methane", "H2": "Hydrogen"}.get(model.get("material"), model.get("material", "?"))


def render_html(e: dict) -> str:
    cards = []
    p8 = e.get("phase8")
    for tank in e["tanks"]:
        b = tank["bound"]; max_len = float(b["max_centered_external_length_m"]); x=float(b["anchor_x_m"]); d=float(b["external_diameter_m"]); minrho=float(b["minimum_equivalent_bulk_density_kg_m3"])
        bars=[]; rows=[]
        for comp in tank["comparisons"]:
            name=_short(comp["model"]); util=float(comp["outer_volume_utilization_fraction"]); status="REJECTED" if comp["screen_status"].startswith("REJECT_") else "NOT REJECTED"; width=min(100,util*100)
            bars.append(f"<div class='barrow'><span>{html.escape(name)}</span><div class='track'><div class='bar' style='width:{width:.2f}%'></div></div><b>{util*100:.0f}%</b>{f'<em> +{util*100-100:.0f}% overflow</em>' if util>1 else ''}</div>")
            rows.append(f"<tr><td>{name}</td><td>{float(comp['screening_density_kg_m3']):.1f}</td><td>{float(comp['ideal_fluid_volume_m3']):.1f}</td><td>{max_len*util:.2f}</td><td>{util*100:.1f}%</td><td class='{status.lower().replace(' ','-')}'>{status}</td></tr>")
        closure=""
        if p8 and tank["source_id"] in p8["frontiers"]:
            f=p8["frontiers"][tank["source_id"]]; probes=[p for p in p8["probes"] if p["source_id"]==tank["source_id"]]
            ullages=sorted({float(p["ullage_fraction"]) for p in probes}); dias=sorted({float(p["internal_diameter_m"]) for p in probes}, reverse=True)
            matrix=[]
            for u in ullages:
                cells=[]
                for di in dias:
                    p=next(q for q in probes if abs(float(q["ullage_fraction"])-u)<1e-12 and abs(float(q["internal_diameter_m"])-di)<1e-12)
                    ok=p["geometric_budget_status"].startswith("FEASIBLE"); a=float(p["max_axial_end_allowance_m"])
                    cells.append(f"<td class='{'ok' if ok else 'bad'}'>{a:.2f} m</td>")
                matrix.append(f"<tr><th>{u*100:.0f}%</th>{''.join(cells)}</tr>")
            closure=f"""<div class='closure'><h3>Phase 8 — Water closure budget</h3><p>Ideal total volume penalty budget: <b>{float(f['max_total_volume_penalty_fraction'])*100:.1f}%</b>. Minimum internal diameter with zero ullage and zero end allowance: <b>{float(f['minimum_internal_diameter_m_at_zero_ullage_zero_end_allowance']):.3f} m</b>. Maximum geometric radial allocation at that zero-penalty edge: <b>{float(f['maximum_uniform_radial_allocation_m_at_zero_ullage_zero_end_allowance'])*1000:.0f} mm/side</b> — this is <u>not</u> wall thickness.</p><p>Cells show remaining total axial end allowance. Probe values are sensitivity points only, not admitted design assumptions.</p><table><thead><tr><th>Ullage</th>{''.join(f'<th>Di {di:.2f} m</th>' for di in dias)}</tr></thead><tbody>{''.join(matrix)}</tbody></table></div>"""
        cards.append(f"""<section class='tank'><h2>{tank['source_id']}</h2><div class='metrics'>anchor x={x:.2f} m | nominal OD={d:.2f} m | max centered length={max_len:.2f} m | density floor={minrho:.1f} kg/m³</div><div class='bound'>{''.join(bars)}</div><table><thead><tr><th>Candidate</th><th>ρ kg/m³</th><th>Ideal fluid m³</th><th>Ideal length m</th><th>Outer use</th><th>Screen</th></tr></thead><tbody>{''.join(rows)}</tbody></table>{closure}</section>""")
    phase8line = f"<div class='sub'>Phase-8 state: {html.escape(p8['state_id'])}</div>" if p8 else ""
    return f"""<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>LOOM Shipyard Evidence Viewer</title><style>
:root{{color-scheme:dark}}body{{font-family:system-ui,sans-serif;margin:0;background:#0d1117;color:#e6edf3}}main{{max-width:1100px;margin:auto;padding:16px}}.banner{{border:2px solid #f0b429;padding:10px;font-weight:800;margin:12px 0;background:#241d0d}}.sub,.metrics{{color:#9da7b3;font-size:.86rem}}.tank{{border:1px solid #30363d;border-radius:10px;padding:12px;margin:14px 0;background:#161b22}}table{{width:100%;border-collapse:collapse;font-size:.82rem}}th,td{{padding:7px;border-bottom:1px solid #30363d;text-align:right}}th:first-child,td:first-child{{text-align:left}}.rejected,.bad{{color:#ff7b72;font-weight:700}}.not-rejected,.ok{{color:#7ee787;font-weight:700}}.bound,.closure{{padding:10px;border:1px dashed #59636e;border-radius:8px;margin:10px 0}}.barrow{{display:grid;grid-template-columns:82px 1fr 55px auto;gap:8px;align-items:center;font-size:.78rem;margin:6px 0}}.track{{height:14px;background:#21262d;border:1px solid #59636e;overflow:hidden}}.bar{{height:100%;background:linear-gradient(90deg,#58a6ff,#7ee787)}}em{{color:#ff7b72;font-style:normal}}h3{{margin:.2rem 0 .5rem}}
</style></head><body><main><h1>LOOM 2226 — Computational Shipyard Evidence Viewer</h1><div class='sub'>Phase-6 state: {html.escape(e['state_id'])}</div>{phase8line}<div class='banner'>{AUTHORITY_BANNER}</div><p>The bars are evidence overlays, not physical tank geometry. Candidate screens and Phase-8 closure maps remain research evidence only. No material selection, wall thickness, ullage policy, end geometry or spatial envelope is admitted.</p>{''.join(cards)}</main></body></html>"""


def serve(db_path: Path, host: str, port: int) -> None:
    evidence=load_evidence(db_path); page=render_html(evidence).encode()
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path in ("/","/index.html"):
                self.send_response(200); self.send_header("Content-Type","text/html; charset=utf-8"); self.send_header("Content-Length",str(len(page))); self.end_headers(); self.wfile.write(page)
            elif self.path=="/evidence.json":
                data=json.dumps(evidence,indent=2,sort_keys=True).encode(); self.send_response(200); self.send_header("Content-Type","application/json; charset=utf-8"); self.send_header("Content-Length",str(len(data))); self.end_headers(); self.wfile.write(data)
            else:self.send_error(404)
        def log_message(self,fmt,*args):return
    server=ThreadingHTTPServer((host,port),Handler); print(f"SHIPYARD EVIDENCE VIEWER: http://{host}:{port}/"); print(AUTHORITY_BANNER); print("Ctrl-C to stop")
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()


def main() -> int:
    p=argparse.ArgumentParser(); p.add_argument("--db",type=Path,default=DEFAULT_DB); p.add_argument("--host",default=DEFAULT_HOST); p.add_argument("--port",type=int,default=DEFAULT_PORT); p.add_argument("--dump-html",type=Path); a=p.parse_args()
    if a.dump_html:a.dump_html.write_text(render_html(load_evidence(a.db)),encoding="utf-8"); print(a.dump_html); return 0
    serve(a.db,a.host,a.port); return 0


if __name__=="__main__": raise SystemExit(main())
