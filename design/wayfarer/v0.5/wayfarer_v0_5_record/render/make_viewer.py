"""Build the phone 3D viewer page for Wayfarer v0.5 -- ALL bodies. ALL sponsors. 2026-2226.
NON-GOVERNING SANDBOX, VISUAL REFERENCE. Inlines loomgl.js and the hashed geometry so the page
needs nothing from the network. Writes out/wayfarer_v05_viewer.html. Usage: python make_viewer.py"""
import hashlib, json, re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
geo_bytes = (ROOT / "out/wayfarer_v05_geometry.json").read_bytes()
SHA = hashlib.sha256(geo_bytes).hexdigest()
G = json.loads(geo_bytes)
R = json.loads((ROOT / "out/certification_report.json").read_text())
I = json.loads((ROOT / "inputs/wayfarer_v05_inputs.json").read_text())


def rnd(o):
    if isinstance(o, float):
        return round(o, 3)
    if isinstance(o, dict):
        return {k: rnd(v) for k, v in o.items()}
    if isinstance(o, list):
        return [rnd(v) for v in o]
    return o


keep = ("id", "name", "system", "mat", "tags", "shape")
geo = {"length_m": G["length_m"], "thrust_line_offset_m": G["thrust_line_offset_m"], "features": G["features"],
       "parts": [{k: p[k] for k in keep} for p in G["parts"]],
       "fluids_by_state": {"S1": [{k: p[k] for k in keep} for p in G["fluids_by_state"]["S1"]]}}
engine = (HERE / "loomgl.js").read_text()
engine = re.sub(r"^export\s+", "", engine, flags=re.M)
S1 = G["states"]["S1"]
gates = [{"g": g["gate"], "t": g["title"], "v": g["verdict"]} for g in R["gates"]]
g2 = next(g for g in R["gates"] if g["gate"] == "G2")
dv = next(c["value"] for c in g2["checks"] if c["name"].startswith("ECON"))
acc = next(c["value"] for c in g2["checks"] if c["name"].startswith("acceleration"))
nhv = next(g for g in R["gates"] if g["gate"] == "G7")["nhv_m3"]
stats = [("Length", f'{G["length_m"]:.1f}', "m"), ("Dry mass", f'{G["dry_t"]:,.1f}', "t"), ("Departure mass", f'{S1["mass_t"]:,.1f}', "t"),
         ("ECON reach", f"{dv:,.0f}", "km/s"), ("Cruise thrust", f"{acc:.2f}", "g"), ("Crew + guests", "6 + 4", ""),
         ("Living volume", f"{nhv:.0f}", "m³")]

html = r"""<title>Wayfarer v0.5 Viewer</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Montserrat:wght@200;300;400;500;600&display=swap">
<style>
/* Layout: one column; the ship fills the top, configuration chips and figures below, gate verdicts last. LOOM HUD look, dark only by design. */
:root{
  --void:#05070B; --deep:#0B1220; --midnight:#11182B; --slate:#1E2A3A; --nebula:#22364A;
  --ion:#00D1FF; --amber:#FF8703; --ice:#C7D3DF; --steel:#8A97A6; --white:#FFFFFF;
  --ok:#22C55E; --caution:#F59E0B; --crit:#EF4444; --hair:#00D1FF2E; --divider:#8A97A640;
  --font:Montserrat,"Avenir Next","Segoe UI",Roboto,system-ui,sans-serif;
  color-scheme:dark;
}
html,body{background:var(--void);color:var(--white)}
body{font-family:var(--font);font-size:15px;line-height:1.5;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));padding-block:16px 28px}
.wrap{max-width:1100px;margin:0 auto;display:flex;flex-direction:column;gap:18px}
header{display:flex;flex-direction:column;gap:4px}
.eyebrow{font-size:11px;font-weight:500;letter-spacing:.14em;text-transform:uppercase;color:var(--ion)}
h1{font-size:30px;font-weight:200;letter-spacing:.2em;text-transform:uppercase;margin:0;text-wrap:balance}
.sub{color:var(--ice);font-size:14px;max-width:62ch;margin:0}
.stage{position:relative;border:1px solid var(--hair);border-radius:12px;overflow:hidden;background:var(--void);touch-action:none}
canvas{display:block;width:100%;height:min(68vh,560px)}
.lab{position:absolute;transform:translate(-50%,-130%);font-size:11px;font-weight:500;letter-spacing:.06em;text-transform:uppercase;color:var(--white);background:#05070BCC;border:1px solid var(--hair);padding:2px 6px;border-radius:2px;white-space:nowrap;pointer-events:none}
.hint{position:absolute;left:12px;bottom:10px;font-size:11px;color:var(--steel);letter-spacing:.04em;pointer-events:none}
.reset{position:absolute;right:10px;top:10px;font:inherit;font-size:11px;letter-spacing:.08em;text-transform:uppercase;background:#05070BCC;color:var(--ice);border:1px solid var(--hair);border-radius:999px;padding:6px 12px;cursor:pointer}
.controls{display:flex;flex-direction:column;gap:10px}
.row{display:flex;flex-wrap:wrap;gap:8px}
.chip{font:inherit;font-size:12px;font-weight:500;letter-spacing:.08em;text-transform:uppercase;background:var(--slate);color:var(--ice);border:1px solid var(--divider);border-radius:999px;padding:8px 14px;cursor:pointer}
.chip[aria-pressed="true"]{background:var(--ion);color:var(--void);border-color:var(--ion)}
.chip:focus-visible,.reset:focus-visible{outline:2px solid var(--white);outline-offset:2px}
.mode-note{color:var(--ice);font-size:13px;margin:0;min-height:1.5em}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:1px;background:var(--divider);border:1px solid var(--divider);border-radius:12px;overflow:hidden}
.stat{background:var(--deep);padding:12px 14px;display:flex;flex-direction:column;gap:2px;min-width:0}
.stat .k{font-size:10.5px;font-weight:500;letter-spacing:.1em;text-transform:uppercase;color:var(--steel)}
.stat .v{font-size:22px;font-weight:300;color:var(--white);font-variant-numeric:tabular-nums}
.stat .u{font-size:12px;color:var(--ion);margin-left:4px;font-weight:400}
.stat.hero .v{color:var(--amber)}
h2{font-size:13px;font-weight:500;letter-spacing:.12em;text-transform:uppercase;color:var(--ion);margin:6px 0 0}
.gates{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:8px}
.gate{display:flex;align-items:center;gap:10px;background:var(--deep);border:1px solid var(--divider);border-radius:8px;padding:9px 12px;min-width:0}
.gate .id{font-size:12px;font-weight:600;color:var(--steel);font-variant-numeric:tabular-nums;width:2.6em;flex:none}
.gate .t{font-size:13px;color:var(--ice);flex:1;min-width:0}
.pill{font-size:10px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;border-radius:999px;padding:3px 8px;flex:none;border:1px solid}
.pill.PASS{color:var(--ok);border-color:var(--ok)}
.pill.DECL{color:var(--caution);border-color:var(--caution)}
.pill.OPEN{color:var(--steel);border-color:var(--steel);border-style:dashed}
.pill.FAIL{color:var(--crit);border-color:var(--crit)}
.legend{color:var(--steel);font-size:12px;margin:0}
footer{color:var(--steel);font-size:11px;letter-spacing:.03em;line-height:1.6;border-top:1px solid var(--divider);padding-top:12px;overflow-wrap:anywhere}
@media (max-width:520px){h1{font-size:22px;letter-spacing:.14em}.stat .v{font-size:19px}}
</style>
<div class="wrap">
<header>
  <span class="eyebrow">LOOM 2226 · Reference courier · Visual reference</span>
  <h1>Wayfarer v0.5</h1>
  <p class="sub">Drag to turn the ship, pinch or scroll to zoom, two fingers to pan. Every shape is built from the same geometry file the certification checks run on.</p>
</header>
<div class="stage" id="stage">
  <canvas id="cv" aria-label="3D model of Wayfarer v0.5"></canvas>
  <button class="reset" id="reset" type="button">Reset view</button>
  <div class="hint" id="hint">Bow at left · slot side up</div>
</div>
<div class="controls">
  <div class="row" role="group" aria-label="Configuration">
    <button class="chip" type="button" data-mode="cruise" aria-pressed="true">Coasting</button>
    <button class="chip" type="button" data-mode="metric" aria-pressed="false">Metric HARD</button>
    <button class="chip" type="button" data-mode="burn" aria-pressed="false">Torch burn</button>
    <button class="chip" type="button" data-mode="shuttle" aria-pressed="false">Shuttle out</button>
  </div>
  <div class="row" role="group" aria-label="Show">
    <button class="chip" type="button" data-tog="cut" aria-pressed="false">Cutaway</button>
    <button class="chip" type="button" data-tog="rooms" aria-pressed="true">Rooms</button>
    <button class="chip" type="button" data-tog="water" aria-pressed="true">Water</button>
    <button class="chip" type="button" data-tog="labels" aria-pressed="true">Labels</button>
  </div>
  <p class="mode-note" id="note"></p>
</div>
<div class="stats" id="stats"></div>
<h2>Certification gates</h2>
<div class="gates" id="gates"></div>
<p class="legend">PASS: computed and inside the limit. DECLARED: passes on an assumption kT must accept. OPEN: not yet run (G10 is Sol's Navigator run). Basis v0.1 is still a proposal; nothing here is canon.</p>
<footer id="foot"></footer>
</div>
<script type="module">
__ENGINE__
const GEO = __GEO__;
const STATS = __STATS__;
const GATES = __GATES__;
const SHA = "__SHA__";
const stage = document.getElementById("stage"), cv = document.getElementById("cv");
document.getElementById("stats").innerHTML = STATS.map((s, i) => `<div class="stat${i === 3 ? " hero" : ""}"><span class="k">${s[0]}</span><span class="v">${s[1]}<span class="u">${s[2]}</span></span></div>`).join("");
const cls = v => v === "PASS" ? "PASS" : v === "PASS-DECLARED" ? "DECL" : v === "OPEN" ? "OPEN" : "FAIL";
const word = v => v === "PASS-DECLARED" ? "Declared" : v[0] + v.slice(1).toLowerCase();
document.getElementById("gates").innerHTML = GATES.map(g => `<div class="gate"><span class="id">${g.g}</span><span class="t">${g.t}</span><span class="pill ${cls(g.v)}">${word(g.v)}</span></div>`).join("");
document.getElementById("foot").textContent = `VISUAL REFERENCE. Wayfarer v0.5, NON-GOVERNING sandbox design. Generated from wayfarer_v05_geometry.json, sha256 ${SHA}. ALL bodies. ALL sponsors. 2026-2226.`;
const MODES = {
  cruise: {strakeSpan: 0, note: "Coasting: radiator strakes stowed in their grooves, bay doors shut."},
  metric: {strakeSpan: 2, hot: 0.35, note: "Metric HARD: one 2 m pleat of each strake out, enough for 34.9 MW. Field geometry radius 6.5 m."},
  burn: {strakeSpan: 24, hot: 1.0, plume: true, note: "Torch burn: strakes at full 24 m span glowing at 1,300 K. Up to 5 g, everyone in a couch."},
  shuttle: {strakeSpan: 0, doorsOpen: true, shuttleLift: 8.5, note: "Shuttle out: doors stand up at the slot edges and the 12.8 m rover-drop shuttle rises straight out."},
};
const LABELS = [["Habitat", [7, 0, 4.6]], ["Docking collar", [16, 0, -4.8]], ["Tanks and bay", [25, 0, 4.6]], ["Shield", [36.8, 0, 2.9]], ["Reactor", [42.8, 0, 2.3]], ["Nozzle", [50, 0, 3.1]]];
const ROOM_LABELS = [["Command", [1.8, 2, 0]], ["Common", [4.4, 2.6, 0]], ["Quarters", [7.0, 2.6, 0]], ["Shelter", [9.6, 0, 3]], ["Mission", [12.2, 2.6, 0]], ["Shuttle", [25, 0, 0]], ["Plant", [15.5, 0, 0]]];
let st = {mode: "cruise", cut: false, rooms: true, water: true, labels: true};
let ship;
try { ship = new Ship(cv, GEO, {shadowSize: 2048}); } catch (e) { stage.insertAdjacentHTML("beforeend", `<p class="mode-note" style="padding:16px">This device could not start WebGL 2, so the 3D view is unavailable. The figures below still apply.</p>`); }
const hideExt = new Set(["room", "outfit", "floor", "core", "avionics", "pressure_hull", "bulkhead", "plant", "equipment", "manifold", "frame", "longeron", "tunnel", "drone", "water", "cargo"]);
function rebuild() {
  if (!ship) return;
  const m = MODES[st.mode];
  const show = st.cut ? (p => p.mat !== "outfit" && (st.rooms || !p.mat.startsWith("room_")))
                      : (p => !(p.tags || []).includes("room") && !hideExt.has(p.mat) && !p.mat.startsWith("room_"));
  ship.build({show, strakeSpan: m.strakeSpan, doorsOpen: !!m.doorsOpen, shuttleLift: m.shuttleLift || 0, plume: !!m.plume,
              fluids: st.cut && st.water ? GEO.fluids_by_state.S1 : [], features: !st.cut});
  document.getElementById("note").textContent = m.note + (st.cut ? " Cutaway: the port half is removed." : "");
  dirty = true;
}
const home = {az: -2.25, el: 0.38, dist: 88, tx: 26, ty: 0, tz: 0};
let cam = {...home}, dirty = true, first = true;
function fitDist() {
  const r = cv.getBoundingClientRect(), a = r.width / Math.max(r.height, 1);
  return Math.max(62, 31 / (Math.tan(19 * Math.PI / 180) * Math.min(a, 1.6)));
}
function resize() {
  const r = cv.getBoundingClientRect(), d = Math.min(window.devicePixelRatio || 1, 2);
  cv.width = Math.round(r.width * d); cv.height = Math.round(r.height * d);
  home.dist = fitDist(); if (first) { cam.dist = home.dist; first = false; }
  dirty = true;
}
function frame() {
  if (dirty && ship) {
    dirty = false;
    const m = MODES[st.mode];
    const eye = [cam.tx + cam.dist * Math.cos(cam.el) * Math.cos(cam.az), cam.ty + cam.dist * Math.cos(cam.el) * Math.sin(cam.az), cam.tz + cam.dist * Math.sin(cam.el)];
    ship.draw({eye, target: [cam.tx, cam.ty, cam.tz], fov: 38, sun: [-0.55, 0.62, 0.55], planet: true, planetC: [900, -500, -900], planetR: 1000,
               clip: st.cut ? [0, -1, 0, 0] : null, hot: m.hot || 0, exposure: 0.88, plumeI: 0.55});
    stage.querySelectorAll(".lab").forEach(e => e.remove());
    const placed = [];
    if (st.labels) for (const [t, at] of (st.cut ? ROOM_LABELS : LABELS)) {
      const [x, y, ok] = ship.project(...at); if (!ok) continue;
      const r = cv.getBoundingClientRect(); if (x < 20 || y < 24 || x > r.width - 20 || y > r.height) continue;
      const w = t.length * 7.5 + 16;
      if (placed.some(b => Math.abs(b[0] - x) < (b[2] + w) / 2 + 4 && Math.abs(b[1] - y) < 24)) continue;
      placed.push([x, y, w]);
      stage.insertAdjacentHTML("beforeend", `<div class="lab" style="left:${x}px;top:${y}px">${t}</div>`);
    }
  }
  requestAnimationFrame(frame);
}
const pts = new Map(); let last = null;
cv.addEventListener("pointerdown", e => { cv.setPointerCapture(e.pointerId); pts.set(e.pointerId, [e.clientX, e.clientY]); last = null; });
cv.addEventListener("pointerup", e => { pts.delete(e.pointerId); last = null; });
cv.addEventListener("pointercancel", e => { pts.delete(e.pointerId); last = null; });
cv.addEventListener("pointermove", e => {
  if (!pts.has(e.pointerId)) return;
  const prev = pts.get(e.pointerId); pts.set(e.pointerId, [e.clientX, e.clientY]);
  if (pts.size === 1) {
    cam.az -= (e.clientX - prev[0]) * 0.008; cam.el = Math.max(-1.45, Math.min(1.45, cam.el + (e.clientY - prev[1]) * 0.006)); dirty = true;
  } else if (pts.size === 2) {
    const [a, b] = [...pts.values()], d = Math.hypot(a[0] - b[0], a[1] - b[1]), c = [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2];
    if (last) {
      cam.dist = Math.max(14, Math.min(220, cam.dist * last.d / d));
      const k = cam.dist * 0.0016, rx = -Math.sin(cam.az), ry = Math.cos(cam.az);
      cam.tx -= (c[0] - last.c[0]) * k * rx; cam.ty -= (c[0] - last.c[0]) * k * ry; cam.tz += (c[1] - last.c[1]) * k;
      dirty = true;
    }
    last = {d, c};
  }
});
cv.addEventListener("wheel", e => { e.preventDefault(); cam.dist = Math.max(14, Math.min(220, cam.dist * Math.exp(e.deltaY * 0.001))); dirty = true; }, {passive: false});
document.getElementById("reset").addEventListener("click", () => { cam = {...home, az: st.cut ? -Math.PI / 2 - 0.35 : home.az, el: st.cut ? 0.25 : home.el}; dirty = true; });
document.querySelectorAll("[data-mode]").forEach(b => b.addEventListener("click", () => {
  st.mode = b.dataset.mode; document.querySelectorAll("[data-mode]").forEach(x => x.setAttribute("aria-pressed", x === b)); rebuild();
}));
document.querySelectorAll("[data-tog]").forEach(b => b.addEventListener("click", () => {
  const k = b.dataset.tog; st[k] = !st[k]; b.setAttribute("aria-pressed", st[k]);
  if (k === "cut" && st.cut) { cam.az = -Math.PI / 2 - 0.35; cam.el = 0.25; }
  rebuild();
}));
new ResizeObserver(resize).observe(cv);
resize(); rebuild(); requestAnimationFrame(frame);
window.__viewerReady = !!ship;
</script>
"""
html = (html.replace("__ENGINE__", engine).replace("__GEO__", json.dumps(rnd(geo), separators=(",", ":")))
        .replace("__STATS__", json.dumps(stats)).replace("__GATES__", json.dumps(gates)).replace("__SHA__", SHA))
out = HERE / "out/wayfarer_v05_viewer.html"
out.write_text(html)
man_p = HERE / "out/manifest.json"
man = json.loads(man_p.read_text())
man["files"] = [f for f in man["files"] if f["file"] != out.name] + [{"file": out.name, "kind": "viewer", "title": "Wayfarer v0.5 Viewer", "geometry_sha256": SHA}]
man_p.write_text(json.dumps(man, indent=1))
print(out, len(html) // 1024, "KB")
