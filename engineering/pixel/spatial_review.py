#!/usr/bin/env python3
"""Read-only LOOM Spatial Review companion."""
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

from src.loom_neptune_mag_exact_sample_adapter import HistoricalMagneticFieldSample
from src.loom_neptune_spatial_atmosphere import NEPTUNE_REFERENCE_MEAN_RADIUS_KM
from engineering.pixel.neptune_mag_pds_source_review import build_review as _build_pds_source_review

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8878


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
        "We are qualifying a historical-sample adapter, not reconstructing Neptune's 1989 field. "
        "The provider emits a magnetic vector only when body, epoch, frame and source position match exactly. "
        "The plotted point and vector are the synthetic qualification fixture used to prove that contract; they are not Voyager observations."
    )
    return f'''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>LOOM Spatial Review</title>
<style>:root{{--bg:#07111b;--panel:#0c1b29;--fg:#e6f1fa;--muted:#8fa9bb;--warn:#ffca70}}*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--fg);font-family:system-ui,sans-serif}}main{{max-width:1180px;margin:auto;padding:18px}}.panel{{background:var(--panel);border:1px solid #24475d;border-radius:12px;padding:16px;margin-bottom:14px}}h1{{font-size:24px}}p{{line-height:1.45}}.muted{{color:var(--muted)}}.warning{{color:var(--warn);font-weight:750}}svg{{width:100%;height:auto;display:block;background:#061019;border-radius:8px}}.body{{fill:#173e61;stroke:#71b9e8;stroke-width:180}}.sample{{fill:#45e6ff;stroke:white;stroke-width:120}}.axis{{stroke:#456679;stroke-width:70}}.dim{{stroke:#dbeaf4;stroke-width:100}}.vector{{stroke:#ffca70;stroke-width:180;fill:none}}text{{fill:#e6f1fa;font-family:system-ui,sans-serif}}</style></head><body><main>
<section class="panel"><h1>LOOM Spatial Review · Neptune MAG exact-sample adapter</h1><p class="muted">Read-only presentation · port {DEFAULT_PORT}</p><p>{html_lib.escape(narrative)}</p><p class="warning">QUALIFICATION FIXTURE — NOT PDS OBSERVATION</p><p>EXACT BODY / EPOCH / FRAME / POSITION · NO INTERPOLATION · NO 2226 PROPAGATION · ADMISSIBILITY AUTHORITY: ZERO</p></section>
<section class="panel"><h2>Physical geometry</h2><p class="muted">SVG coordinates are kilometres. Scale bar is physical.</p>
<svg viewBox="{vb[0]:.3f} {vb[1]:.3f} {vb[2]:.3f} {vb[3]:.3f}"><defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 L10 5 L0 10 z" fill="#ffca70"/></marker></defs><line class="axis" x1="{-extent}" y1="0" x2="{extent}" y2="0"/><line class="axis" x1="0" y1="{-extent}" x2="0" y2="{extent}"/><circle class="body" cx="0" cy="0" r="{radius}"/><text x="{-radius*.55}" y="0" font-size="1250">Neptune</text><text x="{-radius*.55}" y="1700" font-size="800">mean reference radius {radius:,.0f} km</text><circle class="sample" cx="{sx}" cy="{sy}" r="480"/><line class="dim" x1="0" y1="-900" x2="{sx}" y2="-900"/><text x="{sx*.42}" y="-1500" font-size="760">24,765 km from center</text><line class="vector" x1="{sx}" y1="{sy}" x2="{ax:.2f}" y2="{ay:.2f}" marker-end="url(#arrow)"/><text x="{sx-7000}" y="3800" font-size="720">fixture B = (100, −20, 5) nT</text><line class="dim" x1="{scale_x0}" y1="{scale_y}" x2="{scale_x1}" y2="{scale_y}"/><text x="{scale_x0}" y="{scale_y-900}" font-size="680">Scale bar · 5,000 km</text></svg></section>
<section class="panel"><h2>What this proves</h2><p><strong>Adapter:</strong> source vector can be represented at an exact source state.</p><p><strong>It does not prove:</strong> a Neptune field model, interpolation, temporal evolution, a 2226 field, Geometric Admissibility, or Loom coherence.</p></section></main></body></html>'''


def build_neptune_mag_pds_source_contract_review() -> str:
    return _build_pds_source_review()


REVIEWS = {
    "neptune-mag-exact-sample": build_neptune_mag_exact_sample_review,
    "neptune-mag-pds-source-contract": build_neptune_mag_pds_source_contract_review,
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
        if "<svg" not in page:
            raise SystemExit(2)
        print(f"SPATIAL_REVIEW_CHECK=PASS review={args.review} port={args.port}")
        return
    serve(args.review, args.host, args.port)


if __name__ == "__main__":
    main()
