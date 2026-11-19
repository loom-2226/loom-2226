"""Write viewer/b4s.html: a standalone three.js viewer with the five B4-S states embedded (base64 GLBs).
NON-CANON. ALL bodies. ALL sponsors. 2026-2226."""
import base64, json, os
HERE = os.path.dirname(os.path.abspath(__file__)); G = os.path.join(HERE, 'viewer', 'glb')
M = json.load(open(os.path.join(HERE, 'b4s_manifest.json')))
STATES = [('flight', 'Standard'), ('rover_std', 'Rover (std)'), ('venus', 'Venus kit'), ('glide', 'Glide'), ('landed', 'Venus landed'), ('rover_out', 'Venus rover')]
DATA = {k: base64.b64encode(open(os.path.join(G, f'b4s_{k}.glb'), 'rb').read()).decode() for k, _ in STATES}
CAP = {'flight': f"Standard (no kit): 6-seat 1-bar cabin ({M['cabin']['volume_m3']:.0f} m³) + light rover docked at the back. For Earth-type and lower pressures: Moon, Mars, Earth, Titan.",
       'rover_std': 'Standard rover out: light 1-bar cabin on the common crab-steer chassis, down the side-door ramp.',
       'venus': f"Venus kit installed: the Ti pressure capsule ({M['rover']['venus_capsule_m3']:.1f} m³, 92 bar) replaces the light rover cabin on the same chassis; kit fairing on the back deck.",
       'glide': 'Gliding: the double-fold wings swing out from the shoulders (8.3 m span).',
       'landed': 'Venus: landed on four short legs, belly 0.6 m up. Crew in the capsule, cabin vented.',
       'rover_out': 'Venus rover out: the Ti capsule on the same chassis, cooler on top, down the side-door ramp.'}
html = r'''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>Shuttle B4-S: cabin, rover, Venus kit</title>
<style>
html,body{margin:0;height:100%;background:#0d1117;color:#e6e6e6;font:13px/1.35 -apple-system,system-ui,sans-serif;overflow:hidden}
canvas{display:block;width:100%;height:100%;touch-action:none}
#hud{position:fixed;left:12px;top:calc(10px + env(safe-area-inset-top));right:12px;pointer-events:none}
#hud b{font-size:15px}.s{color:#9aa4ae;font-size:11.5px}#cap{margin-top:6px;font-size:13px;color:#dfe6ec;max-width:640px}
#bar{position:fixed;left:0;right:0;bottom:0;display:flex;gap:6px;flex-wrap:wrap;justify-content:center;padding:8px 8px calc(10px + env(safe-area-inset-bottom));background:linear-gradient(transparent,#0d1117ee)}
button{background:#1c2430;color:#e6e6e6;border:1px solid #33404f;border-radius:16px;padding:8px 12px;font:inherit}
button.on{background:#2a78d6;border-color:#2a78d6}#bX.on{background:#1baf7a;border-color:#1baf7a}
#err{position:fixed;left:0;right:0;top:45%;text-align:center;color:#9aa4ae}
</style></head><body>
<canvas id="c"></canvas>
<div id="hud"><b>Shuttle B4-S</b> <span class="s">6-seat cabin + rover; Venus kit swaps in a Ti capsule · NON-CANON lab model</span>
<div id="cap"></div><div class="s" style="margin-top:4px">Blue = cabin · white = light rover · copper = Venus Ti capsule · gold = cooler. Drag to orbit, pinch to zoom.</div></div>
<div id="bar">__BUTTONS__<button id="bX">X-ray</button></div>
<div id="err">Loading…</div>
<script type="importmap">{"imports":{"three":"https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js","three/addons/":"https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"}}</script>
<script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
const DATA = __DATA__, CAP = __CAP__;
const err = document.getElementById('err');
try {
const R = new THREE.WebGLRenderer({canvas: document.getElementById('c'), antialias: true}); R.setPixelRatio(Math.min(devicePixelRatio, 2)); R.toneMapping = THREE.ACESFilmicToneMapping;
const scene = new THREE.Scene(); scene.background = new THREE.Color(0x0d1117);
scene.environment = new THREE.PMREMGenerator(R).fromScene(new RoomEnvironment(), .04).texture;
scene.add(new THREE.HemisphereLight(0xdfe8ff, 0x2a2018, .5)); const sun = new THREE.DirectionalLight(0xffffff, 2.2); sun.position.set(-8, 12, 9); scene.add(sun);
const cam = new THREE.PerspectiveCamera(40, 1, .05, 300); const ctl = new OrbitControls(cam, R.domElement); ctl.enableDamping = true; ctl.autoRotate = true; ctl.autoRotateSpeed = .6;
ctl.addEventListener('start', () => ctl.autoRotate = false);
cam.position.set(14, 7, 13); ctl.target.set(6.4, 0, 1.2);
const ground = new THREE.Mesh(new THREE.CircleGeometry(16, 64), new THREE.MeshStandardMaterial({color: 0xb07b4f, roughness: .95}));
ground.rotation.x = -Math.PI / 2; ground.position.set(8, -1.55, -2.5); ground.visible = false; scene.add(ground);
function size(){ R.setSize(innerWidth, innerHeight, false); cam.aspect = innerWidth / innerHeight; cam.fov = innerWidth < innerHeight ? 62 : 40; cam.updateProjectionMatrix(); }
addEventListener('resize', size); size();
const SKIN = /^(hull|belly_tps|glazing|wing_|door_ramp$|kit_pod|body_flap|fin_)/;
const cache = {}; let cur = null, xray = false;
const bytes = b64 => Uint8Array.from(atob(b64), c => c.charCodeAt(0)).buffer;
function applyX(){ if (!cur) return; cur.traverse(o => { if (!o.isMesh) return; const skin = SKIN.test(o.name) || SKIN.test(o.parent && o.parent.name || '');
  o.material.transparent = xray && skin; o.material.opacity = xray && skin ? .14 : 1; o.material.depthWrite = !(xray && skin); o.material.side = THREE.DoubleSide; }); }
async function show(k){
  for (const b of document.querySelectorAll('[data-s]')) b.classList.toggle('on', b.dataset.s === k);
  document.getElementById('cap').textContent = CAP[k];
  if (!cache[k]) cache[k] = await new Promise((ok, no) => new GLTFLoader().parse(bytes(DATA[k]), '', g => ok(g.scene), no));
  if (cur) scene.remove(cur); cur = cache[k]; scene.add(cur); applyX();
  ground.visible = (k === 'landed' || k === 'rover_out' || k === 'rover_std');
  const ro = (k === 'rover_out' || k === 'rover_std'); ctl.target.set(ro ? 8.5 : 6.4, ro ? -0.6 : 0, ro ? -3.2 : 0); err.textContent = '';
}
for (const b of document.querySelectorAll('[data-s]')) b.onclick = () => show(b.dataset.s);
document.getElementById('bX').onclick = e => { xray = !xray; e.target.classList.toggle('on', xray); applyX(); };
show('venus').catch(e => err.textContent = 'Could not load: ' + e);
R.setAnimationLoop(() => { ctl.update(); R.render(scene, cam); });
} catch (e) { err.textContent = 'Viewer error: ' + e; }
</script></body></html>'''
btn = ''.join(f'<button data-s="{k}">{n}</button>' for k, n in STATES)
html = html.replace('__BUTTONS__', btn).replace('__DATA__', json.dumps(DATA)).replace('__CAP__', json.dumps(CAP))
open(os.path.join(HERE, 'viewer', 'b4s.html'), 'w').write(html); print(len(html))
