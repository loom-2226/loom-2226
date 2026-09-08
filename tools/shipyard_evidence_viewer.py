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


def _latest_state(con: sqlite3.Connection, kind: str):
    return con.execute(
        "SELECT state_id,state_hash FROM design_state WHERE state_kind=? ORDER BY rowid DESC LIMIT 1",
        (kind,),
    ).fetchone()


def load_evidence(db_path: Path = DEFAULT_DB) -> dict:
    db_path = db_path.expanduser().resolve()
    if not db_path.is_file():
        raise RuntimeError(f"Shipyard editing ledger not found: {db_path}")
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    try:
        tables = _tables(con)
        needed = {"design_state", "remass_feasibility_bound", "remass_candidate_model", "remass_candidate_comparison"}
        if not needed.issubset(tables):
            raise RuntimeError("Target is not a Phase-6+ Shipyard ledger")
        state = _latest_state(con, "PHASE6_REMASS_CANDIDATE_SCREEN_STATE")
        if state is None:
            raise RuntimeError("No Phase-6 remass candidate screen state found")
        bounds = {
            r["source_id"]: json.loads(r["bound_json"])
            for r in con.execute("SELECT source_id,bound_json FROM remass_feasibility_bound ORDER BY source_id")
        }
        models = {
            r["candidate_id"]: json.loads(r["model_json"])
            for r in con.execute("SELECT candidate_id,model_json FROM remass_candidate_model ORDER BY candidate_id")
        }
        comparisons = []
        for row in con.execute(
            "SELECT source_id,candidate_id,comparison_json,screen_status FROM remass_candidate_comparison WHERE state_id=? ORDER BY source_id,candidate_id",
            (state["state_id"],),
        ):
            payload = json.loads(row["comparison_json"])
            payload["screen_status"] = row["screen_status"]
            payload["model"] = models[row["candidate_id"]]
            comparisons.append(payload)
        tanks = [
            {"source_id": s, "bound": bounds[s], "comparisons": [r for r in comparisons if r["source_id"] == s]}
            for s in sorted(bounds)
        ]
        out = {
            "state_id": state["state_id"],
            "state_hash": state["state_hash"],
            "authority_banner": AUTHORITY_BANNER,
            "tank_count": len(tanks),
            "candidate_count": len(models),
            "comparison_count": len(comparisons),
            "tanks": tanks,
        }

        if {"remass_water_closure_frontier", "remass_water_closure_probe"}.issubset(tables):
            p8 = _latest_state(con, "PHASE8_WATER_CLOSURE_MAP_STATE")
            if p8:
                frontiers = {
                    r["source_id"]: json.loads(r["frontier_json"])
                    for r in con.execute(
                        "SELECT source_id,frontier_json FROM remass_water_closure_frontier WHERE state_id=?",
                        (p8["state_id"],),
                    )
                }
                probes = [
                    json.loads(r["probe_json"])
                    for r in con.execute(
                        "SELECT probe_json FROM remass_water_closure_probe WHERE state_id=? ORDER BY source_id,probe_id",
                        (p8["state_id"],),
                    )
                ]
                out["phase8"] = {"state_id": p8["state_id"], "state_hash": p8["state_hash"], "frontiers": frontiers, "probes": probes}

        if {"remass_feed_demand", "remass_architecture_candidate", "remass_architecture_gate"}.issubset(tables):
            p9 = _latest_state(con, "PHASE9_REMASS_ARCHITECTURE_GATE_STATE")
            if p9:
                demands = [
                    json.loads(r["demand_json"])
                    for r in con.execute(
                        "SELECT demand_json FROM remass_feed_demand WHERE state_id=? ORDER BY mode_id",
                        (p9["state_id"],),
                    )
                ]
                architectures = [
                    json.loads(r["candidate_json"])
                    for r in con.execute(
                        "SELECT candidate_json FROM remass_architecture_candidate WHERE state_id=? ORDER BY architecture_id",
                        (p9["state_id"],),
                    )
                ]
                gate_row = con.execute(
                    "SELECT gate_json FROM remass_architecture_gate WHERE state_id=? ORDER BY rowid DESC LIMIT 1",
                    (p9["state_id"],),
                ).fetchone()
                out["phase9"] = {
                    "state_id": p9["state_id"],
                    "state_hash": p9["state_hash"],
                    "demands": demands,
                    "architectures": architectures,
                    "gate": json.loads(gate_row[0]) if gate_row else None,
                }

        if {"remass_feed_buffer_probe", "remass_feed_topology_candidate"}.issubset(tables):
            p10 = _latest_state(con, "PHASE10_REMASS_FEED_DECOMPOSITION_STATE")
            if p10:
                probes = [
                    json.loads(r["probe_json"])
                    for r in con.execute(
                        "SELECT probe_json FROM remass_feed_buffer_probe WHERE state_id=? ORDER BY mode_id,probe_id",
                        (p10["state_id"],),
                    )
                ]
                topologies = [
                    json.loads(r["candidate_json"])
                    for r in con.execute(
                        "SELECT candidate_json FROM remass_feed_topology_candidate WHERE state_id=? ORDER BY topology_id",
                        (p10["state_id"],),
                    )
                ]
                out["phase10"] = {
                    "state_id": p10["state_id"],
                    "state_hash": p10["state_hash"],
                    "buffer_probes": probes,
                    "topologies": topologies,
                }

        if {"remass_inertial_head_bound", "remass_hydraulic_power_probe"}.issubset(tables):
            p11 = _latest_state(con, "PHASE11_REMASS_FEED_PHYSICS_BOUNDS_STATE")
            if p11:
                heads = [
                    json.loads(r["bound_json"])
                    for r in con.execute(
                        "SELECT bound_json FROM remass_inertial_head_bound WHERE state_id=? ORDER BY mode_id,source_id",
                        (p11["state_id"],),
                    )
                ]
                hydraulics = [
                    json.loads(r["probe_json"])
                    for r in con.execute(
                        "SELECT probe_json FROM remass_hydraulic_power_probe WHERE state_id=? ORDER BY mode_id,probe_id",
                        (p11["state_id"],),
                    )
                ]
                state_json = con.execute("SELECT state_json FROM design_state WHERE state_id=?", (p11["state_id"],)).fetchone()
                interpretation = None
                if state_json:
                    interpretation = json.loads(state_json[0]).get("phase11_interpretation")
                out["phase11"] = {
                    "state_id": p11["state_id"],
                    "state_hash": p11["state_hash"],
                    "inertial_heads": heads,
                    "hydraulic_probes": hydraulics,
                    "interpretation": interpretation,
                }
        return out
    finally:
        con.close()


def _short(model: dict) -> str:
    return {"H2O": "Water", "CH4": "Methane", "H2": "Hydrogen"}.get(model.get("material"), model.get("material", "?"))


def _phase9_html(p9: dict | None) -> str:
    if not p9:
        return ""
    demand_rows = "".join(
        f"<tr><td>{html.escape(str(d['mode_id']))}</td><td>{float(d['acceleration_g']):.2f} g</td><td>{float(d['exhaust_velocity_m_s'])/1000:.0f} km/s</td><td>{float(d['derived_total_remass_flow_kg_s']):.2f} kg/s</td></tr>"
        for d in p9["demands"]
    )
    arch_rows = "".join(
        f"<tr><td>{html.escape(a['family'])}</td><td>{html.escape(a['gate_status'])}</td><td>{int(a['blocker_count'])}</td></tr>"
        for a in p9["architectures"]
    )
    peak = max(float(d["derived_total_remass_flow_kg_s"]) for d in p9["demands"]) if p9["demands"] else 0.0
    return f"""<section class='panel'><h2>Phase 9 — Remass architecture gate</h2><div class='sub'>{html.escape(p9['state_id'])}</div><p>Derived total-feed demand envelope only. Peak current research point: <b>{peak:.2f} kg/s</b>. This is total propulsion demand, not an equal per-tank feed split.</p><table><thead><tr><th>Mode</th><th>Accel</th><th>vₑ</th><th>Total remass flow</th></tr></thead><tbody>{demand_rows}</tbody></table><h3>Architecture families</h3><table><thead><tr><th>Family</th><th>Gate</th><th>Open blockers</th></tr></thead><tbody>{arch_rows}</tbody></table><p class='warn'>No tank architecture selected. Heritage evidence ranks research only.</p></section>"""


def _phase10_html(p10: dict | None) -> str:
    if not p10:
        return ""
    topo_rows = "".join(
        f"<tr><td>{html.escape(t['family'])}</td><td>{html.escape(t['research_priority'])}</td><td>{html.escape(t['gate_status'])}</td></tr>"
        for t in p10["topologies"]
    )
    mode_order = ["ECON", "CRUISE", "EXPEDITE", "FAST", "HARD", "LIMIT"]
    grouped = []
    for mode in mode_order:
        rows = [p for p in p10["buffer_probes"] if p.get("mode_id") == mode]
        if rows:
            cells = "".join(
                f"<td>{float(p['buffer_duration_s']):g}s → {float(p['transient_buffer_mass_kg']):.1f} kg / {float(p['ideal_liquid_buffer_volume_m3']):.3f} m³</td>"
                for p in rows
            )
            grouped.append(f"<tr><th>{mode}</th>{cells}</tr>")
    return f"""<section class='panel'><h2>Phase 10 — Feed decomposition</h2><div class='sub'>{html.escape(p10['state_id'])}</div><p>The Shipyard separates bulk storage from transient acquisition/conditioning. Probe durations are sensitivity points, not burn durations or admitted header sizes.</p><table><thead><tr><th>Topology family</th><th>Research priority</th><th>Gate</th></tr></thead><tbody>{topo_rows}</tbody></table><h3>Transient buffer sensitivity</h3><div class='scroll'><table><tbody>{''.join(grouped)}</tbody></table></div><p class='warn'>No feed topology or header size selected.</p></section>"""


def _phase11_html(p11: dict | None) -> str:
    if not p11:
        return ""
    max_head = max((float(r["maximum_inertial_pressure_span_pa"]) for r in p11["inertial_heads"]), default=0.0)
    max_power = max((float(r["ideal_hydraulic_power_w"]) for r in p11["hydraulic_probes"]), default=0.0)
    by_mode = []
    for mode in ("ECON", "CRUISE", "EXPEDITE", "FAST", "HARD", "LIMIT"):
        heads = [r for r in p11["inertial_heads"] if r.get("mode_id") == mode]
        hyd = [r for r in p11["hydraulic_probes"] if r.get("mode_id") == mode]
        if not heads or not hyd:
            continue
        head = max(float(r["maximum_inertial_pressure_span_pa"]) for r in heads)
        max_probe = max(hyd, key=lambda r: float(r["pressure_rise_probe_pa"]))
        by_mode.append(
            f"<tr><td>{mode}</td><td>{head/1e6:.3f} MPa</td><td>{float(max_probe['pressure_rise_probe_pa'])/1e6:.1f} MPa</td><td>{float(max_probe['ideal_hydraulic_power_w'])/1e6:.3f} MW</td></tr>"
        )
    interp = p11.get("interpretation") or {}
    priority = html.escape(str(interp.get("research_priority", "OPEN")))
    return f"""<section class='panel accent'><h2>Phase 11 — Feed physics bounds</h2><div class='sub'>{html.escape(p11['state_id'])}</div><div class='kpis'><div><b>{max_head/1e6:.3f} MPa</b><span>max inertial-head bound</span></div><div><b>{max_power/1e6:.3f} MW</b><span>largest ideal hydraulic-power probe</span></div></div><table><thead><tr><th>Mode</th><th>ρaL head bound</th><th>Pressure-rise probe</th><th>Ideal hydraulic power</th></tr></thead><tbody>{''.join(by_mode)}</tbody></table><p><b>Current research priority:</b> <code>{priority}</code></p><p class='warn'>Pressure-rise probes are not propulsion inlet requirements; pump efficiency, pressure, architecture and geometry remain OPEN.</p></section>"""


def render_html(e: dict) -> str:
    cards = []
    p8 = e.get("phase8")
    for tank in e["tanks"]:
        b = tank["bound"]
        max_len = float(b["max_centered_external_length_m"])
        x = float(b["anchor_x_m"])
        d = float(b["external_diameter_m"])
        minrho = float(b["minimum_equivalent_bulk_density_kg_m3"])
        bars = []
        rows = []
        for comp in tank["comparisons"]:
            name = _short(comp["model"])
            util = float(comp["outer_volume_utilization_fraction"])
            status = "REJECTED" if comp["screen_status"].startswith("REJECT_") else "NOT REJECTED"
            width = min(100, util * 100)
            bars.append(
                f"<div class='barrow'><span>{html.escape(name)}</span><div class='track'><div class='bar' style='width:{width:.2f}%'></div></div><b>{util*100:.0f}%</b>{f'<em> +{util*100-100:.0f}% overflow</em>' if util>1 else ''}</div>"
            )
            rows.append(
                f"<tr><td>{name}</td><td>{float(comp['screening_density_kg_m3']):.1f}</td><td>{float(comp['ideal_fluid_volume_m3']):.1f}</td><td>{max_len*util:.2f}</td><td>{util*100:.1f}%</td><td class='{status.lower().replace(' ','-')}'>{status}</td></tr>"
            )
        closure = ""
        if p8 and tank["source_id"] in p8["frontiers"]:
            f = p8["frontiers"][tank["source_id"]]
            probes = [p for p in p8["probes"] if p["source_id"] == tank["source_id"]]
            ullages = sorted({float(p["ullage_fraction"]) for p in probes})
            dias = sorted({float(p["internal_diameter_m"]) for p in probes}, reverse=True)
            matrix = []
            for u in ullages:
                cells = []
                for di in dias:
                    p = next(q for q in probes if abs(float(q["ullage_fraction"]) - u) < 1e-12 and abs(float(q["internal_diameter_m"]) - di) < 1e-12)
                    ok = p["geometric_budget_status"].startswith("FEASIBLE")
                    a = float(p["max_axial_end_allowance_m"])
                    cells.append(f"<td class='{'ok' if ok else 'bad'}'>{a:.2f} m</td>")
                matrix.append(f"<tr><th>{u*100:.0f}%</th>{''.join(cells)}</tr>")
            closure = f"""<div class='closure'><h3>Phase 8 — Water closure budget</h3><p>Ideal total volume penalty budget: <b>{float(f['max_total_volume_penalty_fraction'])*100:.1f}%</b>. Minimum internal diameter with zero ullage and zero end allowance: <b>{float(f['minimum_internal_diameter_m_at_zero_ullage_zero_end_allowance']):.3f} m</b>. Maximum geometric radial allocation at that zero-penalty edge: <b>{float(f['maximum_uniform_radial_allocation_m_at_zero_ullage_zero_end_allowance'])*1000:.0f} mm/side</b> — this is <u>not</u> wall thickness.</p><p>Cells show remaining total axial end allowance. Probe values are sensitivity points only, not admitted design assumptions.</p><div class='scroll'><table><thead><tr><th>Ullage</th>{''.join(f'<th>Di {di:.2f} m</th>' for di in dias)}</tr></thead><tbody>{''.join(matrix)}</tbody></table></div></div>"""
        cards.append(
            f"""<section class='tank'><h2>{tank['source_id']}</h2><div class='metrics'>anchor x={x:.2f} m | nominal OD={d:.2f} m | max centered length={max_len:.2f} m | density floor={minrho:.1f} kg/m³</div><div class='bound'>{''.join(bars)}</div><div class='scroll'><table><thead><tr><th>Candidate</th><th>ρ kg/m³</th><th>Ideal fluid m³</th><th>Ideal length m</th><th>Outer use</th><th>Screen</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div>{closure}</section>"""
        )
    phase_lines = []
    for n in (8, 9, 10, 11):
        p = e.get(f"phase{n}")
        if p:
            phase_lines.append(f"<div class='sub'>Phase-{n} state: {html.escape(p['state_id'])}</div>")
    later = _phase9_html(e.get("phase9")) + _phase10_html(e.get("phase10")) + _phase11_html(e.get("phase11"))
    return f"""<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>LOOM Shipyard Evidence Viewer</title><style>
:root{{color-scheme:dark}}body{{font-family:system-ui,sans-serif;margin:0;background:#0d1117;color:#e6edf3}}main{{max-width:1100px;margin:auto;padding:16px}}.banner{{border:2px solid #f0b429;padding:10px;font-weight:800;margin:12px 0;background:#241d0d}}.sub,.metrics{{color:#9da7b3;font-size:.86rem}}.tank,.panel{{border:1px solid #30363d;border-radius:10px;padding:12px;margin:14px 0;background:#161b22}}.accent{{border-color:#58a6ff}}table{{width:100%;border-collapse:collapse;font-size:.82rem}}th,td{{padding:7px;border-bottom:1px solid #30363d;text-align:right;white-space:nowrap}}th:first-child,td:first-child{{text-align:left}}.rejected,.bad,.warn{{color:#ff7b72}}.not-rejected,.ok{{color:#7ee787;font-weight:700}}.bound,.closure{{padding:10px;border:1px dashed #59636e;border-radius:8px;margin:10px 0}}.barrow{{display:grid;grid-template-columns:82px 1fr 55px auto;gap:8px;align-items:center;font-size:.78rem;margin:6px 0}}.track{{height:14px;background:#21262d;border:1px solid #59636e;overflow:hidden}}.bar{{height:100%;background:linear-gradient(90deg,#58a6ff,#7ee787)}}em{{color:#ff7b72;font-style:normal}}h3{{margin:.6rem 0 .5rem}}.scroll{{overflow-x:auto}}.kpis{{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:10px;margin:12px 0}}.kpis div{{padding:12px;border:1px solid #30363d;border-radius:8px;background:#0d1117}}.kpis b{{font-size:1.25rem;display:block}}.kpis span{{font-size:.78rem;color:#9da7b3}}code{{white-space:normal;color:#79c0ff}}
</style></head><body><main><h1>LOOM 2226 — Computational Shipyard Evidence Viewer</h1><div class='sub'>Phase-6 state: {html.escape(e['state_id'])}</div>{''.join(phase_lines)}<div class='banner'>{AUTHORITY_BANNER}</div><p>All displays below are evidence overlays and analytic research artifacts. They are not physical tank geometry, material selection, pump selection, feed architecture, propulsion inlet requirements, canon, production authority or flight qualification.</p>{later}<h2>Bulk tank geometry evidence</h2>{''.join(cards)}</main></body></html>"""


def serve(db_path: Path, host: str, port: int) -> None:
    evidence = load_evidence(db_path)
    page = render_html(evidence).encode()

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path in ("/", "/index.html"):
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(page)))
                self.end_headers()
                self.wfile.write(page)
            elif self.path == "/evidence.json":
                data = json.dumps(evidence, indent=2, sort_keys=True).encode()
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
    p = argparse.ArgumentParser()
    p.add_argument("--db", type=Path, default=DEFAULT_DB)
    p.add_argument("--host", default=DEFAULT_HOST)
    p.add_argument("--port", type=int, default=DEFAULT_PORT)
    p.add_argument("--dump-html", type=Path)
    a = p.parse_args()
    if a.dump_html:
        a.dump_html.write_text(render_html(load_evidence(a.db)), encoding="utf-8")
        print(a.dump_html)
        return 0
    serve(a.db, a.host, a.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
