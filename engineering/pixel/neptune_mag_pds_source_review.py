from __future__ import annotations

from src.loom_neptune_mag_pds_source_contract import NEPTUNE_MAG_PDS_SOURCE_CONTRACT as c


def build_review() -> str:
    return f'''<!doctype html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>LOOM Spatial Review — Neptune MAG source pairing</title>
<style>
:root{{--bg:#07111b;--panel:#0c1b29;--fg:#e6f1fa;--muted:#8fa9bb;--cyan:#45e6ff;--gold:#ffca70;--green:#7ce3a1;--line:#315469;}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--bg);color:var(--fg);font-family:system-ui,-apple-system,Segoe UI,sans-serif}}
main{{max-width:1100px;margin:auto;padding:18px}} .panel{{background:var(--panel);border:1px solid #24475d;border-radius:12px;padding:16px;margin-bottom:14px}}
h1{{font-size:25px;margin:0 0 8px}} h2{{font-size:18px;margin:0 0 8px}} p,li,dd{{line-height:1.48}} .muted{{color:var(--muted)}}
.chips{{display:flex;gap:8px;flex-wrap:wrap}} .chip{{border:1px solid var(--line);border-radius:999px;padding:5px 9px;font-size:12px}}
svg{{width:100%;height:auto;display:block;background:#061019;border-radius:8px}} .mag{{fill:var(--cyan);stroke:white;stroke-width:2}} .traj{{fill:var(--gold);stroke:white;stroke-width:2}} .join{{stroke:var(--green);stroke-width:4}} .reject{{stroke:#ff7373;stroke-width:4;stroke-dasharray:10 8}} text{{fill:var(--fg);font-family:system-ui,sans-serif}}
dl{{margin:0}} dt{{font-weight:750;margin-top:10px}} dd{{margin-left:0;color:var(--muted)}}
</style></head><body><main>
<section class="panel"><h1>LOOM Spatial Review · Neptune MAG source pairing</h1>
<p class="muted">Read-only review · historical Voyager 2 source contract · port 8878</p>
<div class="chips"><span class="chip">12-second cadence</span><span class="chip">EXACT EPOCH JOIN</span><span class="chip">NO INTERPOLATION</span><span class="chip">2226 AUTHORITY: ZERO</span></div></section>
<section class="panel"><h2>Problem statement</h2>
<p>The magnetic-field readings and the spacecraft-position readings live in separate historical PDS products. A magnetic vector is only spatially meaningful if we know where Voyager 2 was when that exact reading was taken. Joining nearby-but-not-identical times would silently invent a position we did not actually read from the source.</p></section>
<section class="panel"><h2>How we are trying to solve it</h2>
<p>Use the 12-second magnetic-field collection and the 12-second Neptune trajectory collection as a pair. For each MAG row, expose it only when a trajectory row exists at the <strong>same timestamp</strong>. If the exact epoch is missing, reject the sample. Do not interpolate, extrapolate, or transform coordinate frames implicitly.</p></section>
<section class="panel"><h2>Pairing diagram</h2>
<svg viewBox="0 0 1000 430" role="img" aria-label="Exact epoch join between magnetic field and spacecraft trajectory samples">
<text x="70" y="55" font-size="28">MAG product</text><text x="690" y="55" font-size="28">Trajectory product</text>
<text x="70" y="95" font-size="18">magnetic field vector</text><text x="690" y="95" font-size="18">spacecraft position</text>
<circle class="mag" cx="220" cy="190" r="18"/><text x="70" y="196" font-size="20">03:56:00</text>
<circle class="traj" cx="800" cy="190" r="18"/><text x="835" y="196" font-size="20">03:56:00</text>
<line class="join" x1="240" y1="190" x2="780" y2="190"/><text x="405" y="170" font-size="20">accepted: exact epoch</text>
<circle class="mag" cx="220" cy="310" r="18"/><text x="70" y="316" font-size="20">03:56:12</text>
<circle class="traj" cx="800" cy="345" r="18"/><text x="835" y="351" font-size="20">03:56:24</text>
<line class="reject" x1="240" y1="310" x2="780" y2="345"/><text x="390" y="300" font-size="20">rejected: timestamps differ</text>
</svg></section>
<section class="panel"><h2>Legend</h2>
<p><span style="color:#45e6ff">●</span> MAG sample — a magnetic-field measurement row. &nbsp; <span style="color:#ffca70">●</span> Trajectory sample — Voyager 2 position relative to Neptune. &nbsp; <span style="color:#7ce3a1">━</span> exact accepted join. &nbsp; <span style="color:#ff7373">┄</span> rejected non-exact join.</p></section>
<section class="panel"><h2>Definitions</h2><dl>
<dt>Epoch</dt><dd>The timestamp attached to a measurement or position sample.</dd>
<dt>Exact epoch</dt><dd>The MAG row and trajectory row carry the same timestamp; no time estimate is inserted between them.</dd>
<dt>12-second cadence</dt><dd>The source products are sampled at nominal 12-second intervals.</dd>
<dt>Coordinate frame</dt><dd>The coordinate system used to describe vector direction or spacecraft position. Different frames are not treated as interchangeable.</dd>
<dt>Interpolation</dt><dd>Estimating a value between measured samples. This contract gives interpolation authority ZERO.</dd>
<dt>Fail closed</dt><dd>If required source evidence is missing or mismatched, LOOM rejects the sample instead of guessing.</dd>
</dl></section>
<section class="panel"><h2>What this step earns</h2>
<p>It freezes the source-pairing rule and the authority boundary before parser implementation. It does <strong>not</strong> claim that a real PDS row has been parsed yet, and it earns no 2226 Neptune field, Geometric Admissibility, or Loom-coherence result.</p>
<p class="muted">MAG: {c.mag_collection_lidvid} · DOI {c.mag_collection_doi} · coverage {c.mag_time_start_utc} to {c.mag_time_stop_utc}</p></section>
</main></body></html>'''
