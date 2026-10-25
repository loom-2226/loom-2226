"""Build the phone 3D viewer page for Wayfarer v0.5 -- ALL bodies. ALL sponsors. 2026-2226.
NON-GOVERNING SANDBOX, VISUAL REFERENCE. Inlines loomgl.js and the hashed geometry so the page
needs nothing from the network. Writes out/wayfarer_v05_viewer.html. Usage: python make_viewer.py"""
import hashlib, json, re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BASE = ROOT / "compare/v0.5.6"    # the accepted v0.5.6 package, kept for side-by-side comparison


def rnd(o):
    if isinstance(o, float):
        return round(o, 3)
    if isinstance(o, dict):
        return {k: rnd(v) for k, v in o.items()}
    if isinstance(o, list):
        return [rnd(v) for v in o]
    return o


keep = ("id", "name", "system", "mat", "tags", "shape")


def version_pack(geo_p, rep_p, cmd_p, hab_p, check_scene=True):
    gb = geo_p.read_bytes()
    sha = hashlib.sha256(gb).hexdigest()
    G = json.loads(gb)
    R = json.loads(rep_p.read_text())
    geo = {"version": G["version"], "window_bore": G.get("window_bore"), "crown": G.get("crown"), "length_m": G["length_m"], "thrust_line_offset_m": G["thrust_line_offset_m"], "features": G["features"],
           "parts": [{k: p[k] for k in keep} for p in G["parts"]],
           "fluids_by_state": {"S1": [{k: p[k] for k in keep} for p in G["fluids_by_state"]["S1"]]}}
    cmd = json.loads(cmd_p.read_text())
    hab = json.loads(hab_p.read_text())
    if check_scene:
        assert cmd["geometry_sha256"] == sha, "l1_scene.json is stale: run command/l1_study.py"
    S1 = G["states"]["S1"]
    gates = [{"g": g["gate"], "t": g["title"], "v": g["verdict"]} for g in R["gates"]]
    g2 = next(g for g in R["gates"] if g["gate"] == "G2")
    dv = next(c["value"] for c in g2["checks"] if c["name"].startswith("ECON"))
    acc = next(c["value"] for c in g2["checks"] if c["name"].startswith("acceleration"))
    nhv = next(g for g in R["gates"] if g["gate"] == "G7")["nhv_m3"]
    lon = [p for p in G["parts"] if "longeron" in p.get("tags", [])]
    res = G.get("ledger_reserve_t")
    nwin = len([f for f in G["features"] if f["kind"] == "window"])
    nb = len([f for f in G["features"] if f.get("berth")])
    stats = [("Length", f'{G["length_m"]:.1f}', "m"), ("Dry mass", f'{G["dry_t"]:,.1f}', "t"), ("Departure mass", f'{S1["mass_t"]:,.1f}', "t"),
             ("ECON reach", f"{dv:,.0f}", "km/s"), ("Cruise thrust", f"{acc:.2f}", "g"), ("Crew + guests", "6 + 4", ""),
             ("Living volume", f"{nhv:.0f}", "m³"), ("Longerons", f"{len(lon)} · {sum(p['mass_t'] for p in lon):.1f}", "t"),
             ("Windows", f"{nwin - nb}" + (f" + {nb}" if nb else ""), "berth" if nb else "")]
    return {"ver": G["version"], "sha": sha, "geo": rnd(geo), "cmd": rnd(cmd), "hab": rnd(hab), "stats": stats, "gates": gates, "certified": R.get("certified")}


NEW = version_pack(ROOT / "out/wayfarer_v05_geometry.json", ROOT / "out/certification_report.json", HERE / "out/l1_scene.json", HERE / "out/hab_scene.json")
VERS = {NEW["ver"]: NEW}
if BASE.exists():
    OLD = version_pack(BASE / "wayfarer_v05_geometry.json", BASE / "certification_report.json", BASE / "l1_scene.json", BASE / "hab_scene.json")
    VERS = {OLD["ver"]: OLD, NEW["ver"]: NEW}
SHA = NEW["sha"]
engine = (HERE / "loomgl.js").read_text()
engine = re.sub(r"^export\s+", "", engine, flags=re.M)

html = r"""<title>Wayfarer Compare Viewer</title>
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
.stage.big canvas{height:88svh}
.expand{position:absolute;right:10px;top:48px;font:inherit;font-size:11px;letter-spacing:.08em;text-transform:uppercase;background:#05070BCC;color:var(--ice);border:1px solid var(--hair);border-radius:999px;padding:6px 12px;cursor:pointer}
.row[hidden]{display:none}
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
.stat .was{font-size:11px;color:var(--steel)}
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
.changes{margin:0;padding-left:18px;color:var(--ice);font-size:13.5px;display:flex;flex-direction:column;gap:6px}
.changes b{color:var(--white);font-weight:500}
.legend{color:var(--steel);font-size:12px;margin:0}
footer{color:var(--steel);font-size:11px;letter-spacing:.03em;line-height:1.6;border-top:1px solid var(--divider);padding-top:12px;overflow-wrap:anywhere}
@media (max-width:520px){h1{font-size:22px;letter-spacing:.14em}.stat .v{font-size:19px}}
</style>
<div class="wrap">
<header>
  <span class="eyebrow">LOOM 2226 · Reference courier · Visual reference</span>
  <h1 id="vtitle">Wayfarer v__VER__</h1>
  <p class="sub">Drag to turn the ship, pinch or scroll to zoom, two fingers to pan. Every shape is built from the same geometry file the certification checks run on.</p>
</header>
<div class="stage" id="stage">
  <canvas id="cv" aria-label="3D model of Wayfarer v0.5"></canvas>
  <button class="reset" id="reset" type="button">Reset view</button>
  <button class="expand" id="expand" type="button" aria-pressed="false">Expand</button>
  <div class="hint" id="hint">Bow at left · slot side up</div>
</div>
<div class="controls">
  <div class="row" role="group" aria-label="Version" id="verrow">__VERCHIPS__</div>
  <div class="row" role="group" aria-label="Configuration">
    <button class="chip" type="button" data-mode="cruise" aria-pressed="true">Coasting</button>
    <button class="chip" type="button" data-mode="metric" aria-pressed="false">Metric HARD</button>
    <button class="chip" type="button" data-mode="burn" aria-pressed="false">Torch burn</button>
    <button class="chip" type="button" data-mode="shuttle" aria-pressed="false">Shuttle out</button>
    <button class="chip" type="button" data-mode="cmd" aria-pressed="false">Command deck</button>
    <button class="chip" type="button" data-mode="hab" aria-pressed="false">Habitat decks</button>
    <button class="chip" type="button" data-mode="structure" aria-pressed="false">Structure</button>
  </div>
  <div class="row" role="group" aria-label="View from" id="lookrow" hidden>
    <button class="chip" type="button" data-look="orbit" aria-pressed="true">Orbit</button>
    <button class="chip" type="button" data-look="PILOT" aria-pressed="false">Pilot</button>
    <button class="chip" type="button" data-look="NAV" aria-pressed="false">Navigator</button>
    <button class="chip" type="button" data-look="S1" aria-pressed="false">Support 1</button>
    <button class="chip" type="button" data-look="S3" aria-pressed="false">Support 3</button>
    <button class="chip" type="button" data-look="STAND" aria-pressed="false">Standing (1 g)</button>
  </div>
  <div class="row" role="group" aria-label="Crown dome" id="petrow">
    <button class="chip" type="button" data-pet="1" aria-pressed="false">Dome + shutters open</button>
    <button class="chip" type="button" data-pet="0" aria-pressed="true">All closed</button>
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
<h2>What changed in v0.5.7</h2>
<ul class="changes">
  <li><b>Four longerons, sized.</b> Five members (3 planks, 2 sills; 36.9 t at 65 MPa against 400) become four 0.40 m CFRP tubes in an X, matching canon. 21.2 t goes back to the engineering reserve. Tap <i>Structure</i>, then switch versions.</li>
  <li><b>Joints counted.</b> 8 titanium end fittings, a node-mount and hatch allowance (location open: the longeron lines sit under the stowed strakes), 4 bay-corner doublers: 3.3 t.</li>
  <li><b>Berth viewports.</b> One 0.35 m viewport at the outer end of every berth (10). Acrylic plugs carry the armour's and the ring's g/cm², so the berths stay storm-shelter grade with the shutter open. Tap <i>Habitat decks</i>.</li>
  <li><b>Crown dome replaces the 8 nose windows.</b> 25 m² of ceramic glazing inside r 2.8 m on an Osteon frame (8 roots forking into 16 edge-on blades round a clear 2.3 m centre pane); 16 tambour gores close it flush and stow in the brow ring. Pilots see 75% of the forward sky (was 22%). Use <i>Dome open / closed</i>; in <i>Command deck</i> try View from: Pilot or Standing.</li>
  <li><b>Viewports everywhere (rev 3).</b> A panoramic band round the L2 common deck (19 m², 1.6 m tall in the lounge) on Osteon titanium mullions; berth viewports up to 0.5 m; medical 2, storm shelter 2 (the plug continues through the water jacket), suit room 1, workshop 2. Every opening below the crown has an acrylic shield plug and a Strata shutter. ~48 m² of glazing in all. Tap <i>Dome + shutters open</i>.</li>
  <li><b>Concepts, not in the build:</b> external spines and visor sketches, Osteon longeron joints.</li>
</ul>
<h2>Certification gates</h2>
<div class="gates" id="gates"></div>
<p class="legend">PASS: computed and inside the limit. DECLARED: passes on an assumption kT must accept. OPEN: not yet run (G10 is Sol's Navigator run). Basis v0.1 is still a proposal; nothing here is canon.</p>
<footer id="foot"></footer>
</div>
<script type="module">
__ENGINE__
const VERS = __VERS__;
let VER = "__VER__";
let GEO = VERS[VER].geo, CMD = VERS[VER].cmd, HAB = VERS[VER].hab, STATS = VERS[VER].stats, GATES = VERS[VER].gates, SHA = VERS[VER].sha;
const stage = document.getElementById("stage"), cv = document.getElementById("cv");
const cls = v => v === "PASS" ? "PASS" : v === "PASS-DECLARED" ? "DECL" : v === "OPEN" ? "OPEN" : "FAIL";
const word = v => v === "PASS-DECLARED" ? "Declared" : v[0] + v.slice(1).toLowerCase();
function panels() {
  const o = VERS[Object.keys(VERS)[0]];
  document.getElementById("stats").innerHTML = STATS.map((s, i) => { const b = o.stats[i], diff = VER !== o.ver && b && b[1] !== s[1];
    return `<div class="stat${i === 3 ? " hero" : ""}"><span class="k">${s[0]}</span><span class="v">${s[1]}<span class="u">${s[2]}</span></span>${diff ? `<span class="was">v${o.ver}: ${b[1]} ${b[2]}</span>` : ""}</div>`; }).join("");
  document.getElementById("gates").innerHTML = GATES.map(g => `<div class="gate"><span class="id">${g.g}</span><span class="t">${g.t}</span><span class="pill ${cls(g.v)}">${word(g.v)}</span></div>`).join("");
  document.getElementById("vtitle").textContent = `Wayfarer v${VER}`;
  document.getElementById("foot").textContent = `VISUAL REFERENCE. Wayfarer v${VER}, NON-GOVERNING sandbox design. Generated from wayfarer_v05_geometry.json, sha256 ${SHA}. ALL bodies. ALL sponsors. 2026-2226.`;
}
panels();
const MODES = {
  cruise: {strakeSpan: 0, note: "Coasting: radiator strakes stowed in their grooves, bay doors shut."},
  metric: {strakeSpan: 2, hot: 0.35, note: "Metric HARD: one 2 m pleat of each strake out, enough for 34.9 MW. Field geometry radius 6.5 m."},
  burn: {strakeSpan: 4, finSpan: 28, hot: 1.0, plume: true, note: "Torch burn: four hot fins unfolded aft at 1,750 K carry the torch's 1.4 GW; the strakes open 4 m for the magnet coils' cooling. Up to 5 g, everyone in a couch."},
  shuttle: {strakeSpan: 0, doorsOpen: true, shuttleLift: 8.5, note: "Shuttle out: doors stand up at the slot edges and the 12.8 m rover-drop shuttle rises straight out."},
  hab: {strakeSpan: 0, hab: true, cmd: true, note: "Habitat decks: cut along the axis, bow up, walls left out so rooms show as coloured floors. Ten 2.10 m berths, one per person; a casualty moves at 0 g down the port ladder shaft into the medical bay (yellow litter). v0.5.7 adds a 0.35 m viewport at the outer end of every berth."},
  structure: {strakeSpan: 0, structure: true, note: "Structure: skin, tanks and machinery hidden. Longerons in amber, ring frames and the thrust cone in grey. v0.5.6: five members (three flat planks outside the tank, two round sills beside the bay slot). v0.5.7: four 0.40 m tubes in an X, the upper pair edging the slot."},
  cmd: {strakeSpan: 0, cmd: true, note: "Command deck, layout D: bow up, port side cut away. PILOT and NAV lie on a flight deck 1.78 m up, eyes 0.55 m below their nose windows; four support couches lie along the rim. Everyone faces the bow, so thrust presses them into the couch."},
};
const CMD_CLIP = [0, -1, 0, -1.0];
const HAB_CLIP = [0, 0.174, 0.985, 0];
const HAB_LABELS = [["Berths", [7.6, -1.2, -3.4]], ["Berth viewport", [7.55, -1.16, -4.35]], ["Port shaft", [5.2, -1.4, 0]], ["Medical bay", [10.2, -3.0, 0]], ["L4/L5 hatch", [10.8, -1.4, -0.3]], ["Trunk", [9.0, 0, 0]]];
const habHome = {az: 1.396, el: 0.45, dist: 15, tx: 9.0, ty: -1.6, tz: -0.6};
const CMD_LABELS = [["PILOT", [0.8, 0.45, 0.2]], ["NAV", [0.8, -0.45, 0.2]], ["Flight deck", [1.3, 0, -1.4]], ["Nose windows", [0.1, 0, 0.9]], ["Sensors", [1.5, 0, 3.45]],
                    ["S1", [2.55, 1.4, 2.9]], ["S4", [2.55, 2.9, -1.4]], ["Ladder to L2", [2.4, 1.4, 0]]];
const cmdHome = {az: -2.875, el: 0.30, dist: 8.5, tx: 1.2, ty: 0.25, tz: 0.15};
function cmdFit() {   // keep the deck's width in frame on a tall phone screen
  const r = cv.getBoundingClientRect(), a = r.width / Math.max(r.height, 1);
  return Math.max(8.5, 3.1 / (Math.tan(20 * Math.PI / 180) * a));
}
const LABELS = [["Habitat", [7, 0, 4.6]], ["Docking collar", [16, 0, -4.8]], ["Tanks and bay", [25, 0, 4.6]], ["Shield", [36.8, 0, 2.9]], ["Reactor", [42.8, 0, 2.3]], ["Nozzle", [50, 0, 3.1]]];
const ROOM_LABELS = [["Command", [1.8, 2, 0]], ["Common", [4.4, 2.6, 0]], ["Quarters", [7.0, 2.6, 0]], ["Shelter", [9.6, 0, 3]], ["Mission", [12.2, 2.6, 0]], ["Shuttle", [25, 0, 0]], ["Plant", [15.5, 0, 0]]];
let look = {id: "orbit", yaw: 0, pitch: 0, fov: 90};
let st = {petals: 0, mode: "cruise", cut: false, rooms: true, water: true, labels: true};
let ship;
try { ship = new Ship(cv, GEO, {shadowSize: 2048}); } catch (e) { stage.insertAdjacentHTML("beforeend", `<p class="mode-note" style="padding:16px">This device could not start WebGL 2, so the 3D view is unavailable. The figures below still apply.</p>`); }
const hideExt = new Set(["room", "outfit", "floor", "core", "avionics", "pressure_hull", "bulkhead", "plant", "equipment", "manifold", "frame", "longeron", "tunnel", "drone", "water", "cargo"]);
const crownOf = (open) => GEO.crown ? {...GEO.crown, open} : null;
function rebuild() {
  if (!ship) return;
  const m = MODES[st.mode];
  if (m.hab) {
    ship.build({show: p => p.mat !== "outfit" && p.id !== "core_racks" && !p.id.startsWith("room_L1"), strakeSpan: 0, fluids: GEO.fluids_by_state.S1,
                features: false, windowFrames: true, roomsAsFloors: true, hab: HAB, litter: true, cmdClip: HAB_CLIP});
    document.getElementById("note").textContent = m.note;
    dirty = true; return;
  }
  if (m.cmd) {
    const inside = look.id !== "orbit";
    ship.build({show: p => p.mat !== "outfit" && p.id !== "room_L1-command" && p.id !== "core_racks" && (st.rooms || !p.mat.startsWith("room_")), strakeSpan: 0, fluids: [],
                features: false, windowFrames: true, bore: {wall_m: 0.23, armour_m: 0.2, splay_deg: 12}, cmd: CMD, cmdClip: inside ? null : CMD_CLIP,
                cmdHideCrew: inside ? [look.id] : [], crown: crownOf(st.petals), shuttersClosed: !st.petals});
    document.getElementById("note").textContent = (GEO.crown ? m.note.replace("eyes 0.55 m below their nose windows", "under the crown dome") : m.note) + (GEO.crown ? " v0.5.7: the crown dome replaces the 8 nose windows; pilot displays ride on flight-deck arms. Dome open / closed below." : "");
    dirty = true; return;
  }
  MATS.longeron.c = m.structure ? [0.95, 0.55, 0.12] : [0.13, 0.13, 0.14];
  if (m.structure) {
    ship.build({show: p => ["longeron", "frame", "thrust_cone", "shield"].includes(p.mat) || p.id === "docking_collar", strakeSpan: 0, fluids: [], features: false, bands: false});
    document.getElementById("note").textContent = m.note; dirty = true; return;
  }
  const show = st.cut ? (p => p.mat !== "outfit" && (st.rooms || !p.mat.startsWith("room_")))
                      : (p => !(p.tags || []).includes("room") && !hideExt.has(p.mat) && !p.mat.startsWith("room_"));
  const domeOpen = (m.plume || m.hot) ? 0 : st.petals, inner = new Set(["pressure_hull", "floor", "bulkhead", "avionics"]);
  const show2 = GEO.crown && domeOpen && !st.cut ? (p => p.mat !== "outfit" && p.id !== "core_racks") : show;
  ship.build({show: show2, strakeSpan: m.strakeSpan, finSpan: m.finSpan || 0, doorsOpen: !!m.doorsOpen, shuttleLift: m.shuttleLift || 0, plume: !!m.plume,
              fluids: st.cut && st.water ? GEO.fluids_by_state.S1 : [], features: !st.cut, crown: crownOf(domeOpen), shuttersClosed: !!GEO.crown && !domeOpen, cmd: GEO.crown && domeOpen && !st.cut ? CMD : null, cmdClip: null, roomsAsFloors: !!GEO.crown && domeOpen});
  document.getElementById("note").textContent = m.note + (GEO.crown ? (domeOpen ? " Crown dome open (low speed or bow out of the dust flow)." : " Crown dome closed: gores flush with the armour.") : "") + (st.cut ? " Cutaway: the port half is removed." : "");
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
const isCmd = () => !!MODES[st.mode].cmd;
function camEye() {   // ship-z-up orbit; in the command deck the bow is up (orbit about the ship x axis)
  if (isCmd()) return [cam.tx - cam.dist * Math.sin(cam.el), cam.ty + cam.dist * Math.cos(cam.el) * Math.cos(cam.az), cam.tz + cam.dist * Math.cos(cam.el) * Math.sin(cam.az)];
  return [cam.tx + cam.dist * Math.cos(cam.el) * Math.cos(cam.az), cam.ty + cam.dist * Math.cos(cam.el) * Math.sin(cam.az), cam.tz + cam.dist * Math.sin(cam.el)];
}
const zoomLim = () => isCmd() ? [2.5, 30] : [14, 220];
function frame() {
  if (dirty && ship) {
    dirty = false;
    const m = MODES[st.mode];
    if (m.cmd && look.id !== "orbit") {
      const [eye, f0, up0] = lookBasis();
      const r0 = [f0[1] * up0[2] - f0[2] * up0[1], f0[2] * up0[0] - f0[0] * up0[2], f0[0] * up0[1] - f0[1] * up0[0]];
      const cp = Math.cos(look.pitch), d = [0, 1, 2].map(i => f0[i] * cp * Math.cos(look.yaw) + r0[i] * cp * Math.sin(look.yaw) + up0[i] * Math.sin(look.pitch));
      ship.draw({eye, target: eye.map((v, i) => v + d[i]), up: up0, fov: look.fov, near: 0.05, sun: [-0.55, 0.35, -0.76], planet: true, planetC: [-2600, 950, 700], planetR: 1000,
                 clip: null, holes: true, shadows: false, exposure: 1.15, lights: [{at: [1.2, 0.0, -0.6], c: [0.45, 0.48, 0.55]}]});
      stage.querySelectorAll(".lab").forEach(e => e.remove());
      requestAnimationFrame(frame); return;
    }
    if (m.cmd) {
      const eye = camEye();
      ship.draw({eye, target: [cam.tx, cam.ty, cam.tz], up: [-1, 0, 0], fov: 40, sun: [-0.35, 0.3, 0.88], planet: false, clip: m.hab ? HAB_CLIP : CMD_CLIP, holes: true, shadows: false, exposure: 1.0,
                 lights: m.hab ? [{at: [6.0, -1.5, 0.0], c: [1.5, 1.45, 1.4]}, {at: [9.0, -2.0, -1.0], c: [1.5, 1.45, 1.4]}, {at: [12.0, -1.5, 0.5], c: [1.2, 1.2, 1.2]}]
                               : [{at: [1.0, 1.2, 1.4], c: [1.6, 1.55, 1.45]}, {at: [1.9, 0.6, -2.0], c: [1.4, 1.35, 1.3]}]});
    } else {
    const eye = camEye();
    ship.draw({eye, target: [cam.tx, cam.ty, cam.tz], fov: 38, sun: [-0.55, 0.62, 0.55], planet: true, planetC: [900, -500, -900], planetR: 1000,
               clip: st.cut ? [0, -1, 0, 0] : null, hot: m.hot || 0, exposure: 0.88, plumeI: 0.55, holes: !!GEO.crown});
    }
    stage.querySelectorAll(".lab").forEach(e => e.remove());
    const placed = [];
    if (st.labels) for (const [t, at] of (m.hab ? HAB_LABELS : m.cmd ? CMD_LABELS.map(([t, at]) => [t === "Nose windows" && GEO.crown ? "Crown dome" : t, at]) : st.cut ? ROOM_LABELS : (GEO.crown ? [["Crown dome", [0.2, 0, 1.8]], ...LABELS] : LABELS))) {
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
function lookBasis() {   // eye, forward (toward the bow) and up (toward the head) for each station
  if (look.id === "STAND") return [[CMD.floor_x - 1.6, 0.0, 2.4], [-1, 0, 0], [0, 0, -1]];
  const c = CMD.couches.find(k => k.id === look.id);
  const h = [0, c.head[0] - c.feet[0], c.head[1] - c.feet[1]], L = Math.hypot(...h);
  return [c.eye, [-1, 0, 0], h.map(v => v / L)];
}
const inLook = () => isCmd() && look.id !== "orbit";
const pts = new Map(); let last = null;
cv.addEventListener("pointerdown", e => { cv.setPointerCapture(e.pointerId); pts.set(e.pointerId, [e.clientX, e.clientY]); last = null; });
cv.addEventListener("pointerup", e => { pts.delete(e.pointerId); last = null; });
cv.addEventListener("pointercancel", e => { pts.delete(e.pointerId); last = null; });
cv.addEventListener("pointermove", e => {
  if (!pts.has(e.pointerId)) return;
  const prev = pts.get(e.pointerId); pts.set(e.pointerId, [e.clientX, e.clientY]);
  if (inLook()) {
    if (pts.size === 1) { look.yaw -= (e.clientX - prev[0]) * 0.005; look.pitch = Math.max(-1.4, Math.min(1.4, look.pitch - (e.clientY - prev[1]) * 0.005)); dirty = true; }
    else if (pts.size === 2) { const [a, b] = [...pts.values()], d = Math.hypot(a[0] - b[0], a[1] - b[1]);
      if (last) { look.fov = Math.max(40, Math.min(115, look.fov * last.d / d)); dirty = true; } last = {d, c: [0, 0]}; }
    return;
  }
  if (pts.size === 1) {
    cam.az -= (e.clientX - prev[0]) * 0.008; cam.el = Math.max(-1.45, Math.min(1.45, cam.el + (e.clientY - prev[1]) * 0.006)); dirty = true;
  } else if (pts.size === 2) {
    const [a, b] = [...pts.values()], d = Math.hypot(a[0] - b[0], a[1] - b[1]), c = [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2];
    if (last) {
      const [z0, z1] = zoomLim(); cam.dist = Math.max(z0, Math.min(z1, cam.dist * last.d / d));
      const k = cam.dist * 0.0016;
      if (isCmd()) {   // pan in the screen plane, bow up
        const e = camEye(), f = [cam.tx - e[0], cam.ty - e[1], cam.tz - e[2]], fl = Math.hypot(...f); f.forEach((v, i) => f[i] = v / fl);
        const r = [0, f[2], -f[1]], rl = Math.hypot(...r) || 1; r.forEach((v, i) => r[i] = v / rl);
        const u = [f[1] * r[2] - f[2] * r[1], f[2] * r[0] - f[0] * r[2], f[0] * r[1] - f[1] * r[0]];
        const dx = (c[0] - last.c[0]) * k, dy = (c[1] - last.c[1]) * k;
        cam.tx += -dx * r[0] + dy * u[0]; cam.ty += -dx * r[1] + dy * u[1]; cam.tz += -dx * r[2] + dy * u[2];
      } else {
      const rx = -Math.sin(cam.az), ry = Math.cos(cam.az);
      cam.tx -= (c[0] - last.c[0]) * k * rx; cam.ty -= (c[0] - last.c[0]) * k * ry; cam.tz += (c[1] - last.c[1]) * k;
      }
      dirty = true;
    }
    last = {d, c};
  }
});
cv.addEventListener("wheel", e => { e.preventDefault(); if (inLook()) { look.fov = Math.max(40, Math.min(115, look.fov * Math.exp(e.deltaY * 0.001))); dirty = true; return; } const [z0, z1] = zoomLim(); cam.dist = Math.max(z0, Math.min(z1, cam.dist * Math.exp(e.deltaY * 0.001))); dirty = true; }, {passive: false});
document.getElementById("reset").addEventListener("click", () => { cam = isCmd() ? {...cmdHome, dist: cmdFit()} : {...home, az: st.cut ? -Math.PI / 2 - 0.35 : home.az, el: st.cut ? 0.25 : home.el}; dirty = true; });
document.querySelectorAll("[data-mode]").forEach(b => b.addEventListener("click", () => {
  const was = isCmd();
  st.mode = b.dataset.mode; document.querySelectorAll("[data-mode]").forEach(x => x.setAttribute("aria-pressed", x === b));
  if (MODES[st.mode].structure) cam = {...home, dist: home.dist * 0.6, tx: 24, el: 0.32};
  else if (isCmd() !== was || isCmd()) cam = MODES[st.mode].hab ? {...habHome, dist: Math.max(15, cmdFit() * 1.6)} : isCmd() ? {...cmdHome, dist: cmdFit()} : {...home};
  document.getElementById("lookrow").hidden = !(isCmd() && !MODES[st.mode].hab);
  document.getElementById("petrow").hidden = !GEO.crown || !!MODES[st.mode].hab || !!MODES[st.mode].structure;
  if (!isCmd() || MODES[st.mode].hab) setLook("orbit");
  st.petals = isCmd() && !MODES[st.mode].hab ? 1 : 0;   // command deck opens the dome; outside at cruise speed it is closed
  document.querySelectorAll("[data-pet]").forEach(x => x.setAttribute("aria-pressed", +x.dataset.pet === st.petals));
  document.getElementById("hint").textContent = MODES[st.mode].hab ? "Bow up · cut along the axis" : isCmd() ? "Bow up · port side cut away" : "Bow at left · slot side up";
  rebuild();
}));
document.querySelectorAll("[data-tog]").forEach(b => b.addEventListener("click", () => {
  const k = b.dataset.tog; st[k] = !st[k]; b.setAttribute("aria-pressed", st[k]);
  if (k === "cut" && st.cut) { cam.az = -Math.PI / 2 - 0.35; cam.el = 0.25; }
  rebuild();
}));
document.querySelectorAll("[data-ver]").forEach(b => b.addEventListener("click", () => {
  VER = b.dataset.ver; const v = VERS[VER];
  GEO = v.geo; CMD = v.cmd; HAB = v.hab; STATS = v.stats; GATES = v.gates; SHA = v.sha;
  document.querySelectorAll("[data-ver]").forEach(x => x.setAttribute("aria-pressed", x === b));
  if (ship) ship.geo = GEO;
  document.getElementById("petrow").hidden = !GEO.crown || !!MODES[st.mode].hab || !!MODES[st.mode].structure;
  panels(); rebuild();
}));
function setLook(id) {
  look = {id, yaw: 0, pitch: 0, fov: id === "orbit" ? 90 : (id === "STAND" ? 95 : 100)};
  document.querySelectorAll("[data-look]").forEach(x => x.setAttribute("aria-pressed", x.dataset.look === id));
  if (id !== "orbit") document.getElementById("hint").textContent = "Your eye at this station · drag to turn your head · pinch for field of view";
}
document.querySelectorAll("[data-look]").forEach(b => b.addEventListener("click", () => { setLook(b.dataset.look); rebuild(); }));
document.querySelectorAll("[data-pet]").forEach(b => b.addEventListener("click", () => {
  st.petals = +b.dataset.pet; document.querySelectorAll("[data-pet]").forEach(x => x.setAttribute("aria-pressed", x === b)); rebuild(); }));
document.getElementById("expand").addEventListener("click", e => {
  const on = stage.classList.toggle("big"); e.currentTarget.setAttribute("aria-pressed", on); e.currentTarget.textContent = on ? "Shrink" : "Expand";
  if (on) stage.scrollIntoView({block: "start", behavior: "smooth"});
});
new ResizeObserver(resize).observe(cv);
resize(); rebuild(); requestAnimationFrame(frame);
window.__viewerReady = !!ship;
</script>
"""
chips = "".join(f'<button class="chip" type="button" data-ver="{v}" aria-pressed="{str(v == NEW["ver"]).lower()}">v{v}' + (" (accepted)" if v != NEW["ver"] else " (candidate)") + "</button>" for v in VERS)
html = (html.replace("__ENGINE__", engine).replace("__VERS__", json.dumps(VERS, separators=(",", ":"))).replace("__VERCHIPS__", chips)
        .replace("__SHA__", SHA).replace("__VER__", NEW["ver"]))
out = HERE / "out/wayfarer_v05_viewer.html"
out.write_text(html)
man_p = HERE / "out/manifest.json"
man = json.loads(man_p.read_text())
man["files"] = [f for f in man["files"] if f["file"] != out.name] + [{"file": out.name, "kind": "viewer", "title": "Wayfarer v0.5 Viewer", "geometry_sha256": SHA}]
man_p.write_text(json.dumps(man, indent=1))
print(out, len(html) // 1024, "KB")
