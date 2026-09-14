#!/usr/bin/env python3
"""Read-only LOOM Spatial Review companion.

This server is presentation only. It renders source-qualified/fixture geometry and
engineering decision context into native SVG + explanatory HTML. It has no mutation,
calculation-policy, campaign, Navigator, or database authority.
"""
from __future__ import annotations

import argparse
import html as html_lib
import math
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engineering.experience_one.qualification.e1_geometric_admissibility_relevance_audit import build_relevance_audit
from src.loom_neptune_mag_exact_sample_adapter import HistoricalMagneticFieldSample
from src.loom_neptune_spatial_atmosphere import NEPTUNE_REFERENCE_MEAN_RADIUS_KM

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8878


BASE_STYLE = '''
:root{--bg:#07111b;--panel:#0c1b29;--fg:#e6f1fa;--muted:#8fa9bb;--cyan:#45e6ff;--warn:#ffca70;--line:#315469;--green:#75e0a7;--red:#ff8e8e;--violet:#c9a7ff}
*{box-sizing:border-box} body{margin:0;background:var(--bg);color:var(--fg);font-family:system-ui,-apple-system,Segoe UI,sans-serif}
main{max-width:1180px;margin:auto;padding:18px}.panel{background:var(--panel);border:1px solid #24475d;border-radius:12px;padding:16px;margin-bottom:14px}
h1{font-size:24px;margin:0 0 6px}h2{font-size:18px;margin:0 0 8px}h3{font-size:15px;margin:14px 0 5px}p{line-height:1.48;margin:7px 0}.muted{color:var(--muted)}
.warning{color:var(--warn);font-weight:750}.chips{display:flex;gap:8px;flex-wrap:wrap;margin-top:10px}.chip{border:1px solid #315469;border-radius:999px;padding:5px 9px;font-size:12px}
.grid2{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:10px}.card{border:1px solid #284a60;border-radius:10px;padding:12px;background:#091723}.card strong{display:block;margin-bottom:4px}
svg{width:100%;height:auto;display:block;background:#061019;border-radius:8px;touch-action:pan-x pan-y pinch-zoom}text{fill:#e6f1fa;font-family:system-ui,sans-serif}.svg-muted{fill:#93aabc}.svg-warn{fill:#ffca70}
.legend{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:8px}.legend-item{border-left:5px solid #315469;padding:8px 10px;background:#091723;border-radius:6px}.legend-item.next{border-left-color:var(--green)}.legend-item.after{border-left-color:var(--cyan)}.legend-item.hold{border-left-color:var(--warn)}.legend-item.blocked{border-left-color:var(--violet)}.legend-item.context{border-left-color:#647585}
dl{margin:0}dt{font-weight:700;margin-top:9px}dd{margin:2px 0 0 0;color:#c2d3df;line-height:1.4}
'''


def _fixture() -> HistoricalMagneticFieldSample:
    return HistoricalMagneticFieldSample(
        body_id="NE",
        epoch_utc="1989-08-25T03:56:00Z",
        reference_frame="NEPTUNE_LONGITUDE_SYSTEM",
        position_km=(24765.0, 0.0, 0.0),
        magnetic_field_nt=(100.0, -20.0, 5.0),
        source_id="QUALIFICATION_FIXTURE_NOT_PDS_OBSERVATION",
        sample_cadence_s=12.0,
        coordinate_semantics="R_RADIAL_OUTWARD_PHI_EAST_LONGITUDINAL_THETA_COLATITUDINAL",
    )


def build_neptune_mag_exact_sample_review() -> str:
    sample = _fixture()
    radius = float(NEPTUNE_REFERENCE_MEAN_RADIUS_KM)
    sx, sy, _ = sample.position_km
    extent = max(radius * 1.18, abs(sx) * 1.14, abs(sy) * 1.14)
    vb = (-extent, -extent, 2 * extent, 2 * extent)
    scale_bar_km = 5000.0
    scale_x0 = -extent * 0.82
    scale_y = extent * 0.78
    scale_x1 = scale_x0 + scale_bar_km
    br, bp, bt = sample.magnetic_field_nt
    vmag = math.sqrt(br * br + bp * bp + bt * bt)
    arrow_len = extent * 0.26
    ax = sx + arrow_len * (br / vmag)
    ay = sy - arrow_len * (bp / vmag)
    narrative = (
        "We are qualifying a historical-sample adapter, not reconstructing Neptune's "
        "1989 field. The provider emits a magnetic vector only when body, epoch, frame "
        "and source position match exactly. The plotted point and vector are the synthetic "
        "qualification fixture used to prove that contract; they are not Voyager observations."
    )
    return f'''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>LOOM Spatial Review — Neptune MAG exact-sample adapter</title><style>{BASE_STYLE}
.body{{fill:#173e61;stroke:#71b9e8;stroke-width:180}}.sample{{fill:#45e6ff;stroke:white;stroke-width:120}}.axis{{stroke:#456679;stroke-width:70}}.dim{{stroke:#dbeaf4;stroke-width:100}}.vector{{stroke:#ffca70;stroke-width:180;fill:none}}
</style></head><body><main>
<section class="panel"><h1>LOOM Spatial Review · Neptune MAG exact-sample adapter</h1><p class="muted">Read-only presentation · port {DEFAULT_PORT}</p><p>{html_lib.escape(narrative)}</p><p class="warning">QUALIFICATION FIXTURE — NOT PDS OBSERVATION</p><div class="chips"><span class="chip">EXACT BODY / EPOCH / FRAME / POSITION</span><span class="chip">NO INTERPOLATION</span><span class="chip">NO 2226 PROPAGATION</span><span class="chip">ADMISSIBILITY AUTHORITY: ZERO</span></div></section>
<section class="panel"><h2>Physical geometry</h2><p class="muted">SVG coordinates are kilometres. View extent is fitted to the reviewed geometry.</p>
<svg viewBox="{vb[0]:.3f} {vb[1]:.3f} {vb[2]:.3f} {vb[3]:.3f}"><defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="#ffca70"/></marker></defs><line class="axis" x1="{-extent}" y1="0" x2="{extent}" y2="0"/><line class="axis" x1="0" y1="{-extent}" x2="0" y2="{extent}"/><circle class="body" cx="0" cy="0" r="{radius}"/><text x="{-radius*.55:.1f}" y="0" font-size="1250">Neptune</text><text class="svg-muted" x="{-radius*.55:.1f}" y="1700" font-size="800">mean reference radius {radius:,.0f} km</text><circle class="sample" cx="{sx}" cy="{sy}" r="480"/><line class="dim" x1="0" y1="-900" x2="{sx}" y2="-900"/><text x="{sx*.42:.1f}" y="-1500" font-size="760">24,765 km from center</text><line class="vector" x1="{sx}" y1="{sy}" x2="{ax:.2f}" y2="{ay:.2f}" marker-end="url(#arrow)"/><text class="svg-warn" x="{sx-7000:.1f}" y="3800" font-size="720">fixture B = (100, −20, 5) nT</text><line class="dim" x1="{scale_x0}" y1="{scale_y}" x2="{scale_x1}" y2="{scale_y}"/><text x="{scale_x0}" y="{scale_y-900}" font-size="680">Scale bar · 5,000 km</text></svg></section>
<section class="panel"><h2>What this proves</h2><p><strong>Adapter:</strong> source vector can be represented at an exact source state.</p><p><strong>It does not prove:</strong> a Neptune field model, 2226 field, Geometric Admissibility, or Loom coherence.</p></section></main></body></html>'''


def build_geometric_admissibility_relevance_review() -> str:
    """Explain why the next E1 work returns to local geometry before more sensor feeds."""
    report = build_relevance_audit()
    radius = float(NEPTUNE_REFERENCE_MEAN_RADIUS_KM)
    extent = radius * 1.28
    scale_bar_km = 5000.0
    sx0 = -extent * 0.80
    sy = extent * 0.75
    factor_cards = "".join(
        f'''<div class="card"><strong>{html_lib.escape(row["family"].replace("_", " ").title())}</strong>
        <span class="muted">{html_lib.escape(row["work_priority"].replace("_", " "))}</span>
        <p>{html_lib.escape(row["plain_language"])}</p></div>'''
        for row in report["factors"]
    )

    return f'''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>LOOM Spatial Review — Geometric Admissibility relevance audit</title><style>{BASE_STYLE}</style></head><body><main>
<section class="panel"><h1>LOOM Spatial Review · Geometric Admissibility relevance audit</h1><p class="muted">E1 Neptune arrival · read-only engineering explainer · port {DEFAULT_PORT}</p>
<h2>Problem statement</h2><p>We need to determine <strong>where Wayfarer can safely return to ordinary-space flight near Neptune</strong>. The current operational collapse seam works in the qualified Navigator solution, but that does not make it a fundamental physics boundary.</p>
<h2>Why we care</h2><p>If we choose the wrong physical boundary, Navigator can become internally precise about the wrong rule. Hill radius, sphere of influence, atmosphere, magnetic field, and other measurable quantities are not automatically the thing that controls metric collapse.</p>
<h2>How we are trying to solve it</h2><p>Start from the quantities that canon says Geometric Admissibility actually depends on, separate direct geometry from environmental inputs and unresolved Loom-specific physics, then work the highest-value term we can calculate without inventing a coupling law. That points us next to <strong>local curvature and tidal shear at the earned collapse endpoint</strong>.</p>
<p class="warning">NO NUMERIC IMPORTANCE SCORE · NO NEW COLLAPSE THRESHOLD · NO HILL/SOI POLICY</p></section>

<section class="panel"><h2>Physical context — true linear scale</h2><p class="muted">This diagram shows only Neptune's qualified mean reference geometry. The operational collapse seam is intentionally not drawn as a boundary because this audit does not re-qualify it as physics.</p>
<svg viewBox="{-extent:.3f} {-extent:.3f} {2*extent:.3f} {2*extent:.3f}" aria-label="True-scale Neptune reference geometry"><circle cx="0" cy="0" r="{radius}" fill="#173e61" stroke="#71b9e8" stroke-width="170"/><line x1="{-extent}" y1="0" x2="{extent}" y2="0" stroke="#315469" stroke-width="65"/><line x1="0" y1="{-extent}" x2="0" y2="{extent}" stroke="#315469" stroke-width="65"/><text x="{-radius*.40:.1f}" y="0" font-size="1300">Neptune</text><text class="svg-muted" x="{-radius*.40:.1f}" y="1800" font-size="780">mean radius {radius:,.0f} km</text><line x1="{sx0}" y1="{sy}" x2="{sx0+scale_bar_km}" y2="{sy}" stroke="#e6f1fa" stroke-width="110"/><text x="{sx0}" y="{sy-900}" font-size="700">Scale bar · 5,000 km</text></svg></section>

<section class="panel"><h2>Decision map — not a spatial-scale diagram</h2><p class="muted">This diagram is a work-priority map. Box position does not represent physical distance or numerical importance.</p>
<svg viewBox="0 0 1000 520" aria-label="Geometric Admissibility work priority map"><rect x="385" y="205" width="230" height="95" rx="14" fill="#153247" stroke="#e6f1fa" stroke-width="2"/><text x="500" y="240" text-anchor="middle" font-size="18">GEOMETRIC</text><text x="500" y="264" text-anchor="middle" font-size="18">ADMISSIBILITY</text><text x="500" y="287" text-anchor="middle" class="svg-muted" font-size="12">endpoint/domain compatibility</text>
<rect x="40" y="50" width="270" height="120" rx="12" fill="#123527" stroke="#75e0a7" stroke-width="3"/><text x="175" y="80" text-anchor="middle" font-size="16">NEXT ENGINEERING</text><text x="175" y="108" text-anchor="middle" font-size="14">curvature</text><text x="175" y="132" text-anchor="middle" font-size="14">curvature gradients / tidal shear</text>
<rect x="690" y="50" width="270" height="120" rx="12" fill="#102b3c" stroke="#45e6ff" stroke-width="3"/><text x="825" y="80" text-anchor="middle" font-size="16">AFTER LOCAL GEOMETRY</text><text x="825" y="108" text-anchor="middle" font-size="14">matter / stress-energy</text><text x="825" y="132" text-anchor="middle" font-size="14">causal structure</text>
<rect x="40" y="350" width="270" height="120" rx="12" fill="#3a2b13" stroke="#ffca70" stroke-width="3"/><text x="175" y="380" text-anchor="middle" font-size="16">HOLD — COUPLING NOT EARNED</text><text x="175" y="411" text-anchor="middle" font-size="14">electromagnetic conditions</text><text x="175" y="435" text-anchor="middle" class="svg-muted" font-size="12">more MAG data does not define coupling</text>
<rect x="690" y="350" width="270" height="120" rx="12" fill="#2e2340" stroke="#c9a7ff" stroke-width="3"/><text x="825" y="380" text-anchor="middle" font-size="16">PHYSICS BLOCKED</text><text x="825" y="410" text-anchor="middle" font-size="14">Loom coherence / lattice coherence</text><text x="825" y="434" text-anchor="middle" font-size="14">domain-size binding</text>
<line x1="310" y1="110" x2="385" y2="225" stroke="#75e0a7" stroke-width="3"/><line x1="690" y1="110" x2="615" y2="225" stroke="#45e6ff" stroke-width="3"/><line x1="310" y1="410" x2="385" y2="285" stroke="#ffca70" stroke-width="3"/><line x1="690" y1="410" x2="615" y2="285" stroke="#c9a7ff" stroke-width="3"/></svg></section>

<section class="panel"><h2>Legend</h2><div class="legend"><div class="legend-item next"><strong>NEXT ENGINEERING</strong><br>We can advance this now using grounded ordinary-spacetime inputs.</div><div class="legend-item after"><strong>AFTER LOCAL GEOMETRY</strong><br>Relevant, but do the direct geometry calculation first.</div><div class="legend-item hold"><strong>HOLD — COUPLING NOT EARNED</strong><br>Data may exist, but we do not yet know how it affects collapse.</div><div class="legend-item blocked"><strong>PHYSICS BLOCKED</strong><br>The governing observable or rule has not yet been earned.</div><div class="legend-item context"><strong>CONTEXT ONLY</strong><br>Useful for navigation or orientation; not an admissibility boundary.</div></div><p class="warning">Hill radius / SOI are context, not collapse boundaries.</p></section>

<section class="panel"><h2>Definitions</h2><dl><dt>Geometric Admissibility</dt><dd>Whether the full endpoint/domain state is compatible with the metric transition. It is not simply “gravity below X.”</dd><dt>Curvature</dt><dd>The local geometry of spacetime produced by gravitating matter/energy.</dd><dt>tidal shear</dt><dd>Differential gravity: how the gravitational field changes across a region, stretching or compressing separated points differently.</dd><dt>stress-energy</dt><dd>The matter, energy, momentum, and pressure content that sources spacetime geometry in relativistic gravity.</dd><dt>Coupling</dt><dd>The rule that says how one physical quantity actually affects another. Measuring a magnetic field is not enough unless the metric model tells us how that field enters admissibility.</dd><dt>fail closed</dt><dd>If required physics or authority is missing, do not invent a value or silently allow the transition.</dd></dl></section>

<section class="panel"><h2>Factor-by-factor status</h2><div class="grid2">{factor_cards}</div></section>
<section class="panel"><h2>What this step earns</h2><p>It earns an ordered work plan, not an admissibility law. The next bounded calculation is local curvature and tidal shear at the already-earned Neptune collapse endpoint. We still do <strong>not</strong> have authority to turn any result into a new collapse threshold.</p><div class="chips"><span class="chip">THRESHOLD AUTHORITY: ZERO</span><span class="chip">RUNTIME POLICY: ZERO</span><span class="chip">CAMPAIGN MUTATION: ZERO</span><span class="chip">LLM PHYSICS AUTHORITY: ZERO</span></div></section>
</main></body></html>'''


REVIEWS = {
    "neptune-mag-exact-sample": build_neptune_mag_exact_sample_review,
    "geometric-admissibility-relevance": build_geometric_admissibility_relevance_review,
}


class ReviewHandler(BaseHTTPRequestHandler):
    review_name = "neptune-mag-exact-sample"

    def do_GET(self):
        if self.path not in ("/", "/index.html"):
            self.send_error(404)
            return
        body = REVIEWS[self.review_name]().encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        print("SPATIAL REVIEW", self.address_string(), fmt % args)


def serve(review: str, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> None:
    if review not in REVIEWS:
        raise SystemExit(f"unknown review: {review}")
    handler = type("ConfiguredReviewHandler", (ReviewHandler,), {"review_name": review})
    print(f"LOOM SPATIAL REVIEW  READ ONLY  http://{host}:{port}/  review={review}")
    ThreadingHTTPServer((host, port), handler).serve_forever()


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--review", choices=sorted(REVIEWS), required=True)
    p.add_argument("--host", default=DEFAULT_HOST)
    p.add_argument("--port", type=int, default=DEFAULT_PORT)
    p.add_argument("--check", action="store_true")
    args = p.parse_args()
    if args.check:
        page = REVIEWS[args.review]()
        if "<svg" not in page or "LOOM Spatial Review" not in page:
            raise SystemExit(2)
        print(f"SPATIAL_REVIEW_CHECK=PASS review={args.review} port={args.port}")
        return
    serve(args.review, args.host, args.port)


if __name__ == "__main__":
    main()
