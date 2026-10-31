// loomgl.js -- ALL bodies. ALL sponsors. 2026-2226.
// NON-GOVERNING SANDBOX. A small self-contained WebGL2 renderer for Wayfarer v0.5.
// Builds meshes from the part shapes in wayfarer_v05_geometry.json (the same
// shapes certify.py checks), so every image is generated from the hashed
// geometry. No external libraries.
// Ship coordinates: x bow->aft, y starboard, z toward the shuttle slot.
// World (GL) coordinates: X = x - xc, Y = z, Z = -y.

export const MATS = {
  hull_armor:   {c: [0.60, 0.60, 0.585], m: 0.05, r: 0.72, seam: 1, holes: 1},
  hull_skin:    {c: [0.66, 0.665, 0.65], m: 0.08, r: 0.62, seam: 1},
  door:         {c: [0.50, 0.51, 0.53], m: 0.15, r: 0.55, seam: 1},
  pressure_hull:{c: [0.82, 0.82, 0.80], m: 0.0, r: 0.6, holes: 1},
  bulkhead:     {c: [0.55, 0.55, 0.56], m: 0.2, r: 0.6},
  floor:        {c: [0.42, 0.43, 0.45], m: 0.2, r: 0.7},
  core:         {c: [0.45, 0.46, 0.48], m: 0.3, r: 0.5},
  avionics:     {c: [0.16, 0.20, 0.24], m: 0.4, r: 0.4},
  outfit:       {c: [0.42, 0.43, 0.45], m: 0.1, r: 0.8},
  radiator:     {c: [0.05, 0.05, 0.055], m: 0.35, r: 0.35, kind: 2},
  hotfin:       {c: [0.08, 0.072, 0.065], m: 0.55, r: 0.38, kind: 4},
  manifold:     {c: [0.33, 0.34, 0.36], m: 0.65, r: 0.38},
  shield:       {c: [0.22, 0.22, 0.24], m: 0.7, r: 0.4},
  reactor:      {c: [0.40, 0.41, 0.43], m: 0.85, r: 0.28},
  nozzle:       {c: [0.93, 0.62, 0.36], m: 1.0, r: 0.22, kind: 3},
  rcs:          {c: [0.28, 0.28, 0.30], m: 0.6, r: 0.4},
  collar:       {c: [0.78, 0.78, 0.76], m: 0.4, r: 0.35},
  shuttle:      {c: [0.86, 0.86, 0.84], m: 0.05, r: 0.5, kind: 1},
  tank_shell:   {c: [0.88, 0.88, 0.86], m: 0.0, r: 0.55},
  longeron:     {c: [0.13, 0.13, 0.14], m: 0.3, r: 0.4},
  frame:        {c: [0.30, 0.30, 0.32], m: 0.5, r: 0.45},
  bay:          {c: [0.48, 0.48, 0.49], m: 0.4, r: 0.5},
  thrust_cone:  {c: [0.28, 0.28, 0.30], m: 0.6, r: 0.4},
  plant:        {c: [0.34, 0.32, 0.56], m: 0.6, r: 0.3},
  equipment:    {c: [0.44, 0.44, 0.41], m: 0.2, r: 0.6},
  tunnel:       {c: [0.74, 0.74, 0.71], m: 0.2, r: 0.5},
  drone:        {c: [0.86, 0.44, 0.10], m: 0.1, r: 0.5},
  water:        {c: [0.10, 0.34, 0.72], m: 0.0, r: 0.15},
  cargo:        {c: [0.55, 0.45, 0.30], m: 0.0, r: 0.8},
  room_command: {c: [0.20, 0.62, 0.60], m: 0, r: 0.8},
  room_galley:  {c: [0.86, 0.62, 0.24], m: 0, r: 0.8},
  room_wardroom:{c: [0.90, 0.50, 0.28], m: 0, r: 0.8},
  room_observation:{c: [0.45, 0.70, 0.90], m: 0, r: 0.8},
  room_exercise:{c: [0.45, 0.72, 0.36], m: 0, r: 0.8},
  room_hygiene: {c: [0.62, 0.80, 0.88], m: 0, r: 0.8},
  room_cabin:   {c: [0.42, 0.55, 0.85], m: 0, r: 0.8},
  room_cabin_guest:{c: [0.62, 0.50, 0.82], m: 0, r: 0.8},
  room_shelter: {c: [0.28, 0.34, 0.50], m: 0, r: 0.8},
  room_medical: {c: [0.88, 0.40, 0.45], m: 0, r: 0.8},
  room_eclss:   {c: [0.45, 0.58, 0.48], m: 0, r: 0.8},
  room_airlock: {c: [0.92, 0.80, 0.25], m: 0, r: 0.8},
  room_suits:   {c: [0.92, 0.66, 0.30], m: 0, r: 0.8},
  room_workshop:{c: [0.60, 0.48, 0.36], m: 0, r: 0.8},
  room_custody: {c: [0.62, 0.20, 0.22], m: 0, r: 0.8},
  room_stores:  {c: [0.78, 0.72, 0.58], m: 0, r: 0.8},
  room_vestibule:{c: [0.72, 0.74, 0.76], m: 0, r: 0.8},
  plume:        {c: [0.75, 0.62, 1.0], m: 0, r: 1, kind: 9},
  window:       {c: [0.02, 0.03, 0.045], m: 0.9, r: 0.05, em: [0.035, 0.03, 0.022]},
  aoi:          {c: [0.08, 0.24, 0.29], m: 0.1, r: 0.11, em: [0.012, 0.028, 0.035]},
  hatch:        {c: [0.72, 0.72, 0.70], m: 0.3, r: 0.4},
  // L1 command scene (render-only items placed from render/out/l1_scene.json, the scene the ray tests score)
  couch:        {c: [0.20, 0.24, 0.29], m: 0.15, r: 0.55},
  crew:         {c: [0.86, 0.42, 0.12], m: 0.0, r: 0.75},
  helmet:       {c: [0.90, 0.90, 0.88], m: 0.1, r: 0.35},
  screen:       {c: [0.025, 0.035, 0.05], m: 0.3, r: 0.2, em: [0.012, 0.075, 0.11]},
  rail:         {c: [0.62, 0.63, 0.65], m: 0.7, r: 0.35},
  well:         {c: [0.03, 0.035, 0.04], m: 0.0, r: 0.9},
  frame:        {c: [0.30, 0.31, 0.33], m: 0.6, r: 0.4, nosec: 1},
  mattress:     {c: [0.55, 0.62, 0.72], m: 0.0, r: 0.85},
  litter:       {c: [0.95, 0.72, 0.15], m: 0.0, r: 0.6},
  shutter:      {c: [0.62, 0.62, 0.60], m: 0.1, r: 0.65, seam: 1},
  brow:         {c: [0.64, 0.64, 0.625], m: 0.08, r: 0.55},
  tambour:      {c: [0.58, 0.59, 0.60], m: 0.15, r: 0.5, kind: 5},
  camera:       {c: [0.08, 0.08, 0.09], m: 0.6, r: 0.3},
  hold_door:    {c: [0.46, 0.47, 0.49], m: 0.3, r: 0.5},
  engine_bell:  {c: [0.10, 0.10, 0.11], m: 0.8, r: 0.3},
  // rev 7 external equipment and metric node faces (drawn from the geometry's parts and features)
  sensor:       {c: [0.06, 0.07, 0.08], m: 0.5, r: 0.25},
  antenna:      {c: [0.34, 0.35, 0.37], m: 0.3, r: 0.55},
  port:         {c: [0.40, 0.41, 0.43], m: 0.7, r: 0.35},
  dock:         {c: [0.30, 0.31, 0.33], m: 0.6, r: 0.4},
  rail_ext:     {c: [0.70, 0.62, 0.20], m: 0.3, r: 0.45},
  node_face:    {c: [0.035, 0.04, 0.05], m: 0.25, r: 0.15, kind: 6},
};
// rev 7 skin (kT 2026-10-26): which materials take the Strata / tunable-flank finish (1 = full detail, 2 = colour only)
export const SKINMAT = {hull_armor: 1, hull_skin: 1, door: 1, shutter: 1, brow: 2, tambour: 2};
for (const [k, v] of Object.entries(MATS)) v.sec = k.startsWith("room_") ? 0.95 : (k === "water" ? 0.9 : 0.55);

// ------------------------------------------------------------ mesh builder
class MB {
  constructor(xc) { this.p = []; this.n = []; this.i = []; this.xc = xc; }
  w(x, y, z) { return [x - this.xc, z, -y]; }
  wn(nx, ny, nz) { return [nx, nz, -ny]; }
  v(s, n) { const k = this.p.length / 3; const a = this.w(...s), b = this.wn(...n); this.p.push(...a); this.n.push(...b); return k; }
  tri(a, b, c, ref) {   // ref: reference normal in ship coords, used to fix winding
    const P = this.p, A = [P[a*3], P[a*3+1], P[a*3+2]], B = [P[b*3], P[b*3+1], P[b*3+2]], C = [P[c*3], P[c*3+1], P[c*3+2]];
    const u = [B[0]-A[0], B[1]-A[1], B[2]-A[2]], v = [C[0]-A[0], C[1]-A[1], C[2]-A[2]];
    const cr = [u[1]*v[2]-u[2]*v[1], u[2]*v[0]-u[0]*v[2], u[0]*v[1]-u[1]*v[0]];
    const R = this.wn(...ref);
    if (cr[0]*R[0] + cr[1]*R[1] + cr[2]*R[2] < 0) this.i.push(a, c, b); else this.i.push(a, b, c);
  }
  quad(s0, s1, s2, s3, n) { const a = this.v(s0, n), b = this.v(s1, n), c = this.v(s2, n), d = this.v(s3, n); this.tri(a, b, c, n); this.tri(a, c, d, n); }
  // strip of smooth quads: rows A[k], B[k] with normals NA[k], NB[k]; ref(k) gives the outward direction
  strip(A, B, NA, NB, ref) {
    const ia = A.map((s, k) => this.v(s, NA[k])), ib = B.map((s, k) => this.v(s, NB[k]));
    for (let k = 0; k < A.length - 1; k++) { const r = ref(k); this.tri(ia[k], ib[k], ib[k+1], r); this.tri(ia[k], ib[k+1], ia[k+1], r); }
  }
}

const D2R = Math.PI / 180;
const cyl = (x, r, t) => [x, r * Math.cos(t), r * Math.sin(t)];

function meshSector(mb, s, ox = 0, oy = 0) {
  const span = Math.min(s.a1 - s.a0, 360), full = span >= 359.999;
  const n = Math.max(6, Math.ceil(span / 3));
  const th = [...Array(n + 1)].map((_, k) => (s.a0 + span * k / n) * D2R);
  const P = (x, r, t) => { const q = cyl(x, r, t); return [q[0], q[1] + oy, q[2] + ox]; };
  const rad = t => [0, Math.cos(t), Math.sin(t)];
  mb.strip(th.map(t => P(s.x0, s.r1, t)), th.map(t => P(s.x1, s.r1, t)), th.map(rad), th.map(rad), k => rad(th[k]));
  if (s.r0 > 1e-6) { const ir = t => rad(t).map(v => -v);
    mb.strip(th.map(t => P(s.x0, s.r0, t)), th.map(t => P(s.x1, s.r0, t)), th.map(ir), th.map(ir), k => ir(th[k])); }
  for (const [x, nx] of [[s.x0, -1], [s.x1, 1]]) {
    const nn = th.map(() => [nx, 0, 0]);
    mb.strip(th.map(t => P(x, s.r0, t)), th.map(t => P(x, s.r1, t)), nn, nn, () => [nx, 0, 0]);
  }
  if (!full) for (const [t, sg] of [[th[0], -1], [th[n], 1]]) {
    const tn = [0, -Math.sin(t) * sg, Math.cos(t) * sg];
    mb.quad(P(s.x0, s.r0, t), P(s.x1, s.r0, t), P(s.x1, s.r1, t), P(s.x0, s.r1, t), tn);
  }
}

function meshCSlot(mb, s, x0o) {
  const x0 = x0o ?? s.x0, x1 = s.x1, r0 = s.r0, r1 = s.r1, hw = s.hw;
  const ao = Math.acos(Math.min(1, hw / r1)) / D2R, ai = Math.acos(Math.min(1, hw / r0)) / D2R;
  let o0 = 180 - ao, o1 = 360 + ao, i0 = 180 - ai, i1 = 360 + ai;
  if (s.side === 1) { o0 = 270; i0 = 270; }
  if (s.side === -1) { o1 = 270; i1 = 270; }
  const N = Math.max(24, Math.round((o1 - o0) * 1.5));
  const T = [...Array(N + 1)].map((_, k) => k / N);
  const ro = t => {
    const th = t * D2R; let r = r1;
    if (s.gw) for (const a of s.grooves) { const d = th - a * D2R; if (Math.cos(d) > 0 && Math.abs(r1 * Math.sin(d)) < s.gw / 2) r = r1 - s.gd; }
    return r;
  };
  const tho = T.map(t => o0 + (o1 - o0) * t), thi = T.map(t => i0 + (i1 - i0) * t);
  const rad = d => [0, Math.cos(d * D2R), Math.sin(d * D2R)];
  const nrad = d => rad(d).map(v => -v);
  const O = (x, k) => cyl(x, ro(tho[k]), tho[k] * D2R), In = (x, k) => cyl(x, r0, thi[k] * D2R);
  mb.strip(T.map((_, k) => O(x0, k)), T.map((_, k) => O(x1, k)), tho.map(rad), tho.map(rad), k => rad(tho[k]));
  mb.strip(T.map((_, k) => In(x0, k)), T.map((_, k) => In(x1, k)), thi.map(nrad), thi.map(nrad), k => nrad(thi[k]));
  for (const [x, nx] of [[x0, -1], [x1, 1]]) { const nn = T.map(() => [nx, 0, 0]);
    mb.strip(T.map((_, k) => In(x, k)), T.map((_, k) => O(x, k)), nn, nn, () => [nx, 0, 0]); }
  for (const [k, sg] of [[0, 1], [N, -1]]) {
    const a = In(x0, k), b = O(x0, k), c = O(x1, k), d = In(x1, k);
    const e = [0, b[1] - a[1], b[2] - a[2]]; // along wall in yz
    const nrm = [0, -e[2] * sg, e[1] * sg]; const L = Math.hypot(nrm[1], nrm[2]) || 1;
    mb.quad(a, b, c, d, [0, nrm[1] / L, nrm[2] / L]);
  }
}

function lathe(mb, prof, nth = 64, ox = 0, oy = 0) {  // prof: [[x, r, nx, nr], ...] around the ship x axis
  const th = [...Array(nth + 1)].map((_, k) => k / nth * 2 * Math.PI);
  for (let j = 0; j < prof.length - 1; j++) {
    const [xa, ra, nxa, nra] = prof[j], [xb, rb, nxb, nrb] = prof[j + 1];
    const A = th.map(t => { const q = cyl(xa, ra, t); return [q[0], q[1] + oy, q[2] + ox]; });
    const B = th.map(t => { const q = cyl(xb, rb, t); return [q[0], q[1] + oy, q[2] + ox]; });
    const NA = th.map(t => [nxa, nra * Math.cos(t), nra * Math.sin(t)]), NB = th.map(t => [nxb, nrb * Math.cos(t), nrb * Math.sin(t)]);
    mb.strip(A, B, NA, NB, k => [(nxa + nxb) / 2, (nra + nrb) / 2 * Math.cos(th[k]), (nra + nrb) / 2 * Math.sin(th[k])]);
  }
}

function ellProfile(xa, xb, xc, R, inward = false, M = 24, xs = null) {
  const h = xb - xa, out = [];
  const u0 = xs === null ? 1 : Math.max(0, Math.min(1, (xb - xs) / h));
  if (xs !== null) { const r0 = R * Math.sqrt(Math.max(0, 1 - u0 * u0)); out.push([xs, 0, -1, 0]); out.push([xs, r0, -1, 0]); }
  for (let i = 0; i <= M; i++) {
    const u = u0 * (1 - i / M), x = xb - u * h, r = R * Math.sqrt(Math.max(0, 1 - u * u));
    let nx = -(u) / h, nr = (r / R) / R; const L = Math.hypot(nx, nr) || 1; nx /= L; nr /= L;
    if (i === 0 && xs === null) { nx = -1; nr = 0; }
    out.push(inward ? [x, r, -nx, -nr] : [x, r, nx, nr]);
  }
  out.push(inward ? [xc, R, 0, -1] : [xc, R, 0, 1]);
  out[out.length - 2] = inward ? [xb, R, 0, -1] : [xb, R, 0, 1];
  return out;
}

function latheArc(mb, prof, a0, a1) {  // lathe over the arc a0..a1 degrees
  const n = Math.max(4, Math.ceil((a1 - a0) / 3));
  const th = [...Array(n + 1)].map((_, k) => (a0 + (a1 - a0) * k / n) * D2R);
  for (let j = 0; j < prof.length - 1; j++) {
    const [xa, ra, nxa, nra] = prof[j], [xb, rb, nxb, nrb] = prof[j + 1];
    mb.strip(th.map(t => cyl(xa, ra, t)), th.map(t => cyl(xb, rb, t)), th.map(t => [nxa, nra * Math.cos(t), nra * Math.sin(t)]),
             th.map(t => [nxb, nrb * Math.cos(t), nrb * Math.sin(t)]), k => [(nxa + nxb) / 2, (nra + nrb) / 2 * Math.cos(th[k]), (nra + nrb) / 2 * Math.sin(th[k])]);
  }
}

function meshDomeSolid(mb, s) {
  // solid ellipsoidal cap (plus cylinder to xc), optionally only r >= rin, truncated at xc < xb, with angular gaps [centre, half-width]
  const h = s.xb - s.xa, R = s.R, rin = s.rin || 0, xe = s.xc;
  const x0 = rin > 0 ? s.xb - h * Math.sqrt(Math.max(0, 1 - (rin / R) ** 2)) : s.xa;
  const u0 = (s.xb - x0) / h, u1 = Math.max(0, (s.xb - Math.min(xe, s.xb)) / h), M = 28;
  const outer = [];
  for (let i = 0; i <= M; i++) {
    const u = u0 + (u1 - u0) * i / M, x = s.xb - u * h, r = R * Math.sqrt(Math.max(0, 1 - u * u));
    let nx = -u / h, nr = r / (R * R); const L = Math.hypot(nx, nr) || 1;
    outer.push([x, r, nx / L, nr / L]);
  }
  if (xe > s.xb) { outer.push([s.xb, R, 0, 1]); outer.push([xe, R, 0, 1]); }
  const rEnd = outer[outer.length - 1][1];
  const gaps = (s.gaps || []).map(([c, w]) => [c - w, c + w]).sort((a, b) => a[0] - b[0]);
  const arcs = [];
  if (!gaps.length) arcs.push([0, 360]);
  else for (let k = 0; k < gaps.length; k++) { const a0 = gaps[k][1], a1 = k + 1 < gaps.length ? gaps[k + 1][0] : gaps[0][0] + 360; if (a1 > a0) arcs.push([a0, a1]); }
  for (const [a0, a1] of arcs) {
    latheArc(mb, outer, a0, a1);
    if (rin > 0) latheArc(mb, [[x0, rin, 0, -1], [xe, rin, 0, -1]], a0, a1);
    latheArc(mb, [[xe, rin, 1, 0], [xe, rEnd, 1, 0]], a0, a1);
    if (gaps.length) for (const [a, sg] of [[a0, -1], [a1, 1]]) {
      const t = a * D2R, n = [0, -Math.sin(t) * sg, Math.cos(t) * sg];
      mb.strip(outer.map(q => cyl(q[0], rin, t)), outer.map(q => cyl(q[0], q[1], t)), outer.map(() => n), outer.map(() => n), () => n);
    }
  }
}

function meshDome(mb, s) {
  if ((s.rin || 0) > 0 || (s.gaps && s.gaps.length) || (s.t <= 0 && s.xc < s.xb)) return meshDomeSolid(mb, s);
  lathe(mb, ellProfile(s.xa, s.xb, s.xc, s.R, false, 24, s.xs !== undefined ? s.xs + 0.015 : null));   // tiny gap: avoids z-fighting with the part ahead
  if (s.t > 0) {
    lathe(mb, ellProfile(s.xa + s.t, s.xb, s.xc, s.R - s.t, true));
    lathe(mb, [[s.xc, s.R - s.t, 1, 0], [s.xc, s.R, 1, 0]]);
  } else lathe(mb, [[s.xc, 0, 1, 0], [s.xc, s.R, 1, 0]]);
}

function meshFrustum(mb, s, ox = 0, oy = 0) {
  const L = s.x1 - s.x0, dr = s.r1 - s.r0, k = Math.hypot(L, dr), nx = -dr / k, nr = L / k;
  lathe(mb, [[s.x0, s.r0, nx, nr], [s.x1, s.r1, nx, nr]], 64, ox, oy);
  if (s.t > 0) {
    lathe(mb, [[s.x0, s.r0 - s.t, -nx, -nr], [s.x1, s.r1 - s.t, -nx, -nr]], 64, ox, oy);
    lathe(mb, [[s.x0, s.r0 - s.t, -1, 0], [s.x0, s.r0, -1, 0]], 64, ox, oy);
    lathe(mb, [[s.x1, s.r1 - s.t, 1, 0], [s.x1, s.r1, 1, 0]], 64, ox, oy);
  } else {
    lathe(mb, [[s.x0, 0, -1, 0], [s.x0, s.r0, -1, 0]], 64, ox, oy);
    lathe(mb, [[s.x1, 0, 1, 0], [s.x1, s.r1, 1, 0]], 64, ox, oy);
  }
}

function meshTube(mb, s, n = 24) {
  const p0 = s.p0, p1 = s.p1, d = p1.map((v, i) => v - p0[i]), L = Math.hypot(...d), u = d.map(v => v / L);
  let a = Math.abs(u[0]) < 0.9 ? [1, 0, 0] : [0, 1, 0];
  const v = [u[1]*a[2]-u[2]*a[1], u[2]*a[0]-u[0]*a[2], u[0]*a[1]-u[1]*a[0]], lv = Math.hypot(...v); for (let i = 0; i < 3; i++) v[i] /= lv;
  const w = [u[1]*v[2]-u[2]*v[1], u[2]*v[0]-u[0]*v[2], u[0]*v[1]-u[1]*v[0]];
  const th = [...Array(n + 1)].map((_, k) => k / n * 2 * Math.PI);
  const ring = (p, t) => [0, 1, 2].map(i => p[i] + s.r * (Math.cos(t) * v[i] + Math.sin(t) * w[i]));
  const nr = t => [0, 1, 2].map(i => Math.cos(t) * v[i] + Math.sin(t) * w[i]);
  mb.strip(th.map(t => ring(p0, t)), th.map(t => ring(p1, t)), th.map(nr), th.map(nr), k => nr(th[k]));
  for (const [p, sg] of [[p0, -1], [p1, 1]]) {
    const c = mb.v(p, u.map(x => x * sg)); const ids = th.map(t => mb.v(ring(p, t), u.map(x => x * sg)));
    for (let k = 0; k < n; k++) mb.tri(c, ids[k], ids[k + 1], u.map(x => x * sg));
  }
}

function meshBox(mb, b) {
  const [x0, x1, y0, y1, z0, z1] = b;
  mb.quad([x0,y0,z0],[x0,y1,z0],[x0,y1,z1],[x0,y0,z1],[-1,0,0]); mb.quad([x1,y0,z0],[x1,y1,z0],[x1,y1,z1],[x1,y0,z1],[1,0,0]);
  mb.quad([x0,y0,z0],[x1,y0,z0],[x1,y0,z1],[x0,y0,z1],[0,-1,0]); mb.quad([x0,y1,z0],[x1,y1,z0],[x1,y1,z1],[x0,y1,z1],[0,1,0]);
  mb.quad([x0,y0,z0],[x1,y0,z0],[x1,y1,z0],[x0,y1,z0],[0,0,-1]); mb.quad([x0,y0,z1],[x1,y0,z1],[x1,y1,z1],[x0,y1,z1],[0,0,1]);
}

function meshPanel(mb, s, span, tilt = 0) {
  // flat plate along x at azimuth a from radius r0 outward by span, thickness t (tangential); optional accordion zig-zag
  const c = Math.cos(s.a * D2R), sn = Math.sin(s.a * D2R);
  const P = (x, along, across) => [x, along * c - across * sn, along * sn + across * c];
  const t = s.t / 2, a0 = s.r0, a1 = s.r0 + span;
  const N = [0, -sn, c], A = [0, c, sn];
  if (tilt > 0 && span > 0.5) {   // accordion pleats: alternating facets
    const np = Math.max(1, Math.round(span / 2));
    for (let k = 0; k < np; k++) {
      const ra = a0 + span * k / np, rb = a0 + span * (k + 1) / np, off = (k % 2 ? 1 : -1) * tilt;
      const na = [0, -sn * Math.cos(off) + c * Math.sin(off), c * Math.cos(off) + sn * Math.sin(off)];
      mb.quad(P(s.x0, ra, -t), P(s.x1, ra, -t), P(s.x1, rb, t), P(s.x0, rb, t), na);
      mb.quad(P(s.x0, ra, -t), P(s.x1, ra, -t), P(s.x1, rb, t), P(s.x0, rb, t), na.map(v => -v));
    }
    return;
  }
  mb.quad(P(s.x0, a0, t), P(s.x1, a0, t), P(s.x1, a1, t), P(s.x0, a1, t), N);
  mb.quad(P(s.x0, a0, -t), P(s.x1, a0, -t), P(s.x1, a1, -t), P(s.x0, a1, -t), N.map(v => -v));
  mb.quad(P(s.x0, a1, -t), P(s.x1, a1, -t), P(s.x1, a1, t), P(s.x0, a1, t), A);
  mb.quad(P(s.x0, a0, -t), P(s.x1, a0, -t), P(s.x1, a0, t), P(s.x0, a0, t), A.map(v => -v));
  mb.quad(P(s.x0, a0, -t), P(s.x0, a1, -t), P(s.x0, a1, t), P(s.x0, a0, t), [-1, 0, 0]);
  mb.quad(P(s.x1, a0, -t), P(s.x1, a1, -t), P(s.x1, a1, t), P(s.x1, a0, t), [1, 0, 0]);
}

function meshOBox(mb, c, A, h) {   // oriented box: centre c, unit axes A[0..2], half sizes h[0..2] (ship coords)
  const P = (a, b, d) => [0, 1, 2].map(i => c[i] + a * h[0] * A[0][i] + b * h[1] * A[1][i] + d * h[2] * A[2][i]);
  for (let k = 0; k < 3; k++) for (const sg of [-1, 1]) {
    const k1 = (k + 1) % 3, k2 = (k + 2) % 3, q = [];
    for (const [p1, p2] of [[-1, -1], [1, -1], [1, 1], [-1, 1]]) { const w = [0, 0, 0]; w[k] = sg; w[k1] = p1; w[k2] = p2; q.push(P(...w)); }
    mb.quad(q[0], q[1], q[2], q[3], A[k].map(v => v * sg));
  }
}

function meshSphere(mb, c, r, n = 14) {
  const prof = [];
  for (let i = 0; i <= n; i++) { const a = Math.PI * i / n; prof.push([c[0] - r * Math.cos(a), r * Math.sin(a), -Math.cos(a), Math.sin(a)]); }
  lathe(mb, prof, 2 * n, c[2], c[1]);
}

function meshBore(mb, p, nn, r, b, n = 40) {
  // window opening seen from inside: pane frame at the pressure hull, opening splayed outward through the armour
  // b: {wall_m, armour_m, splay_deg}; a is distance along the outward normal from the outer surface point p
  const u = nn, a0 = Math.abs(u[0]) < 0.9 ? [1, 0, 0] : [0, 1, 0];
  const v = [u[1]*a0[2]-u[2]*a0[1], u[2]*a0[0]-u[0]*a0[2], u[0]*a0[1]-u[1]*a0[0]], lv = Math.hypot(...v); for (let i = 0; i < 3; i++) v[i] /= lv;
  const w = [u[1]*v[2]-u[2]*v[1], u[2]*v[0]-u[0]*v[2], u[0]*v[1]-u[1]*v[0]];
  const th = [...Array(n + 1)].map((_, k) => k / n * 2 * Math.PI), t = Math.tan(b.splay_deg * D2R);
  const rd = q => [0, 1, 2].map(i => Math.cos(q) * v[i] + Math.sin(q) * w[i]);
  const at = (a, rr, q) => p.map((x, i) => x + a * u[i] + rr * rd(q)[i]);
  const prof = [[-b.wall_m, r], [-b.armour_m, r], [0.006, r + (b.armour_m + 0.006) * t]];
  for (let j = 0; j < prof.length - 1; j++) {
    const [aa, ra] = prof[j], [ab, rb] = prof[j + 1], f = (rb - ra) / (ab - aa), L = Math.hypot(1, f);
    const nr = q => rd(q).map((x, i) => (-x + f * u[i]) / L);
    mb.strip(th.map(q => at(aa, ra, q)), th.map(q => at(ab, rb, q)), th.map(nr), th.map(nr), k => nr(th[k]));
  }
  const ro = prof[2][1], up = u, dn = u.map(x => -x);
  mb.strip(th.map(q => at(0.006, ro, q)), th.map(q => at(0.006, ro + 0.05, q)), th.map(() => up), th.map(() => up), () => up);   // outer rim
  mb.strip(th.map(q => at(-b.wall_m - 0.004, r - 0.035, q)), th.map(q => at(-b.wall_m - 0.004, r + 0.01, q)), th.map(() => dn), th.map(() => dn), () => dn);   // pane frame, cabin side
}

function meshRing(mb, p0, p1, ri, ro, n = 32) {   // hollow tube (window frame): axis p0->p1, inner and outer radius
  const d = p1.map((v, i) => v - p0[i]), L = Math.hypot(...d), u = d.map(v => v / L);
  const a = Math.abs(u[0]) < 0.9 ? [1, 0, 0] : [0, 1, 0];
  const v = [u[1]*a[2]-u[2]*a[1], u[2]*a[0]-u[0]*a[2], u[0]*a[1]-u[1]*a[0]], lv = Math.hypot(...v); for (let i = 0; i < 3; i++) v[i] /= lv;
  const w = [u[1]*v[2]-u[2]*v[1], u[2]*v[0]-u[0]*v[2], u[0]*v[1]-u[1]*v[0]];
  const th = [...Array(n + 1)].map((_, k) => k / n * 2 * Math.PI);
  const rd = t => [0, 1, 2].map(i => Math.cos(t) * v[i] + Math.sin(t) * w[i]);
  const at = (p, r, t) => p.map((x, i) => x + r * rd(t)[i]);
  mb.strip(th.map(t => at(p0, ro, t)), th.map(t => at(p1, ro, t)), th.map(rd), th.map(rd), k => rd(th[k]));
  const ir = t => rd(t).map(x => -x);
  mb.strip(th.map(t => at(p0, ri, t)), th.map(t => at(p1, ri, t)), th.map(ir), th.map(ir), k => ir(th[k]));
  for (const [p, sg] of [[p0, -1], [p1, 1]]) { const nn = u.map(x => x * sg);
    mb.strip(th.map(t => at(p, ri, t)), th.map(t => at(p, ro, t)), th.map(() => nn), th.map(() => nn), () => nn); }
}

// CONCEPT (non-governing): crown dome, Osteon/Strata version. A Builder-grammar frame: 8 graded roots spring
// from a brow ring and fork once into 16 blades that land on a slim ring round a 2.3 m central pane. Blades are
// flat and set edge-on to the pilots. Strata tambour gores close the dome on meridian tracks and retract into
// the brow ring, so nothing sits outside the glass when it is open.
export function crownMeshes(cw, xc) {
  const G = {}, mb = m => (G[m] ||= new MB(xc));
  // kT I4 Option B: 37 OUTER nonpressure panes, ONE seamless pressure dome.
  // Rev7's 16 armour-equivalent Strata gores still close over both skins.
  if (cw.outerPaneRings && cw.innerR) {
    const bounds=cw.outerPaneRings, outer=bounds[bounds.length-1], inner=cw.innerR;
    const X=r=>2.35-2.15*Math.sqrt(Math.max(0,1-(r/4.3)**2));
    const PP=(r,a,offset=0)=>[X(r)-offset,r*Math.cos(a),r*Math.sin(a)];
    const NN=(r,a)=>{const u=Math.sqrt(Math.max(.0001,1-(r/4.3)**2));
       const v=2.15*r/(4.3*4.3*u),q=Math.hypot(1,v);
       return [-1/q,v*Math.cos(a)/q,v*Math.sin(a)/q];};
    const innerProfile=[];
    for(let j=0;j<=84;j++){const r=inner*j/84;const nn=NN(r,0);innerProfile.push([X(r),r,nn[0],nn[1]]);}
    lathe(mb("window"),innerProfile,96);
    if (cw.aoi) {
      // AOI is a filled NON-PRESSURE interlayer with an independent backup
      // ceramic dome offset 0.12 m forward. Renderer surfaces do not imply
      // proven fragment shock absorption or pressure-seal function.
      const backup=innerProfile.map(row=>[row[0]-.12,row[1],row[2],row[3]]);
      const gel=innerProfile.map(row=>[row[0]-.06,row[1],row[2],row[3]]);
      lathe(mb("window"),backup,96);
      lathe(mb("aoi"),gel,96);
    }
    // 1 centre pane and 12 trapezoids in each of three concentric bands.
    const B=mb("window"), seam=mb("frame");
    for(let ring=0;ring<4;ring++){
      const r0=bounds[ring],r1=bounds[ring+1],count=ring===0?1:12;
      for(let i=0;i<count;i++){
        const a0=2*Math.PI*i/count, a1=2*Math.PI*(i+1)/count,nn=8,steps=6;
        for(let j=0;j<steps;j++){
          const u=r0+(r1-r0)*j/steps,v=r0+(r1-r0)*(j+1)/steps;
          const aa=[...Array(nn+1)].map((_,k)=>a0+(a1-a0)*k/nn);
          B.strip(aa.map(a=>PP(u,a,.05)),aa.map(a=>PP(v,a,.05)),aa.map(a=>NN(u,a)),aa.map(a=>NN(v,a)),k=>NN((u+v)/2,aa[k]));
        }
        if(ring) meshTube(seam,{p0:PP(r0,a0,.047),p1:PP(r1,a0,.047),r:.015},8);
      }
      if(ring){
        const n=96;
        for(let j=0;j<n;j++){const a0=2*Math.PI*j/n,a1=2*Math.PI*(j+1)/n;
          meshTube(seam,{p0:PP(r0,a0,.045),p1:PP(r0,a1,.045),r:.013},5);}
      }
    }
    // Existing 16 Strata gore operating rule, with protective closed mantle.
    const brow=[];
    for(let j=0;j<=24;j++){const r=outer-.10+j*.35/24,n=NN(r,0);brow.push([X(r)-.03,r,n[0],n[1]]);}
    lathe(mb("brow"),brow,96);
    if((cw.open??1)<.5){
      const cap=[];for(let j=0;j<=60;j++){const r=outer*j/60,n=NN(r,0);cap.push([X(r)-.085,r,n[0],n[1]]);}
      lathe(mb("tambour"),cap,96);
      for(let i=0;i<16;i++){
        const a=2*Math.PI*i/16;
        meshTube(mb("frame"),{p0:PP(.02,a,.09),p1:PP(outer,a,.09),r:.024},10);
      }
    }
    return G;
  }
  const R = cw.r, c0 = cw.center || 1.15, rf = cw.fork || 2.0, N = cw.mer || 8;
  const xm = r => 2.35 - 2.25 * Math.sqrt(Math.max(0, 1 - (r / 4.4) ** 2));      // mid-wall surface
  const xo = r => 2.35 - 2.35 * Math.sqrt(Math.max(0, 1 - (r / 4.5) ** 2));      // armour outer surface
  const P = (r, a, x = xm) => [x(r), r * Math.cos(a), r * Math.sin(a)];
  const nrm = (r, a) => { const u = Math.sqrt(Math.max(1e-6, 1 - (r / 4.4) ** 2)); const nx = -1, nr = r / (4.4 * 4.4) * 2.25 / u, L = Math.hypot(nx, nr); return [nx / L, nr / L * Math.cos(a), nr / L * Math.sin(a)]; };
  const cross = (a, b) => [a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]];
  const unit = v => { const L = Math.hypot(...v) || 1; return v.map(x => x / L); };
  // a flat blade swept along a surface path: thickness w (sideways, tapered) and depth d (along the surface normal)
  function blade(path, w0, w1, d, m) {
    const n = path.length, rows = [];
    for (let i = 0; i < n; i++) {
      const [r, a] = path[i], c = P(r, a), nn = nrm(r, a);
      const nb = path[Math.min(i + 1, n - 1)], pb = path[Math.max(i - 1, 0)];
      const t = unit(P(nb[0], nb[1]).map((v, k) => v - P(pb[0], pb[1])[k])), sd = unit(cross(nn, t));
      const w = (w0 + (w1 - w0) * i / (n - 1)) / 2;
      rows.push({c, nn, sd, w});
    }
    const corner = (q, sw, dn) => q.c.map((v, k) => v + q.sd[k] * q.w * sw + q.nn[k] * d * dn);
    for (const [s1, d1, s2, d2, nf] of [[1, -0.5, 1, 0.5, q => q.sd], [-1, -0.5, -1, 0.5, q => q.sd.map(v => -v)],
                                         [-1, -0.5, 1, -0.5, q => q.nn.map(v => -v)], [-1, 0.5, 1, 0.5, q => q.nn]])
      mb(m).strip(rows.map(q => corner(q, s1, d1)), rows.map(q => corner(q, s2, d2)), rows.map(nf), rows.map(nf), k => nf(rows[k]));
  }
  const seg = (r0, a0, r1, a1, k = 24) => [...Array(k + 1)].map((_, i) => { const t = i / k, e = t * t * (3 - 2 * t); return [r0 + (r1 - r0) * t, a0 + (a1 - a0) * e]; });
  const half = Math.PI / N / 2;
  for (let j = 0; j < N; j++) {
    const a = 2 * Math.PI * j / N;
    blade(seg(R, a, rf, a, 12), 0.075, 0.05, 0.16, "frame");                     // root, thick at the brow ring
    for (const sg of [-1, 1]) blade(seg(rf, a, c0, a + sg * half), 0.05, 0.03, 0.12, "frame");   // forks, thinning inward
  }
  { const ring = [...Array(97)].map((_, i) => [c0, 2 * Math.PI * i / 96]); blade(ring, 0.04, 0.04, 0.10, "frame"); }
  // brow ring: a smooth raised band round the rim that holds the frame roots and the retracted tambour gores
  const prof = [];
  for (let i = 0; i <= 24; i++) {
    const r = R - 0.1 + 1.0 * i / 24, bump = 0.22 * Math.sin(Math.PI * i / 24) ** 0.7;
    const x0 = xo(r), u = Math.sqrt(Math.max(1e-6, 1 - (r / 4.5) ** 2)), nx = -1, nr = r / (4.5 * 4.5) * 2.35 / u, L = Math.hypot(nx, nr);
    prof.push([x0 + nx / L * bump, r + nr / L * bump, nx / L, nr / L]);
  }
  lathe(mb("brow"), prof, 96);
  // closed: strata tambour gores sit flush in the armour opening
  if ((cw.open ?? 1) < 0.5) {
    const cap = [];
    for (let i = 0; i <= 30; i++) { const r = (R + 0.05) * i / 30, u = Math.sqrt(Math.max(1e-6, 1 - (r / 4.5) ** 2)), nx = -1, nr = r / (4.5 * 4.5) * 2.35 / u, L = Math.hypot(nx, nr);
      cap.push([xo(r) - 0.005, r, nx / L, nr / L]); }
    lathe(mb("tambour"), cap, 96);
  }
  return G;
}

// a person lying on their back: T(s along the body from the head, l sideways, t up from the support surface)
function crewFigure(mb, T, axes) {
  meshSphere(mb("helmet"), T(0.15, 0, 0.13), 0.13);
  for (const sg of [-1, 1]) {
    meshTube(mb("crew"), {p0: T(0.30, sg * 0.08, 0.11), p1: T(0.95, sg * 0.08, 0.11), r: 0.11}, 16);       // torso
    meshSphere(mb("crew"), T(0.31, sg * 0.10, 0.11), 0.10, 10);                                            // shoulders
    meshTube(mb("crew"), {p0: T(0.92, sg * 0.10, 0.08), p1: T(1.84, sg * 0.10, 0.08), r: 0.075}, 14);      // legs
    meshTube(mb("crew"), {p0: T(0.34, sg * 0.25, 0.08), p1: T(0.98, sg * 0.25, 0.08), r: 0.05}, 12);       // arms
    meshOBox(mb("couch"), T(1.89, sg * 0.10, 0.12), axes, [0.05, 0.055, 0.11]);                             // boots
  }
}

// habitat crew systems: berths (with sleepers), cabin doors, ladder shafts, medical doors, a litter (render/out/hab_scene.json)
export function habitatMeshes(sc, opt = {}) {
  const G = {}, mb = m => (G[m] ||= new MB(opt.xc));
  const clip = opt.clip, gone = p => clip && clip[0] * p[0] + clip[1] * p[1] + clip[2] * p[2] + clip[3] > 0;
  const up = [-1, 0, 0];
  for (const b of sc.bunks) {
    const t = b.angle_deg * D2R, u = [0, Math.cos(t), Math.sin(t)], v = [0, -Math.sin(t), Math.cos(t)];
    const [r0, r1] = b.radial_m, W = b.width_m, L = r1 - r0;
    const P = (s, l, h) => [b.pan_x - h, (r1 - s) * u[1] + l * v[1], (r1 - s) * u[2] + l * v[2]];   // head at the outer wall
    if (gone(P(L / 2, 0, 0))) continue;
    const box = (m, s0, s1, l0, l1, h0, h1) => meshOBox(mb(m), P((s0 + s1) / 2, (l0 + l1) / 2, (h0 + h1) / 2), [u, v, up], [(s1 - s0) / 2, (l1 - l0) / 2, (h1 - h0) / 2]);
    box("couch", 0, L, -W / 2, W / 2, -0.06, 0);                  // pan
    box("mattress", 0.02, L - 0.02, -W / 2 + 0.03, W / 2 - 0.03, 0, 0.07);
    for (const sg of [-1, 1]) box("couch", 0.3, 1.2, sg * (W / 2 - 0.03) - 0.02, sg * (W / 2 - 0.03) + 0.02, 0.07, 0.15);   // restraint rails
    if (b.tier === 2) for (const s0 of [0.03, L - 0.03]) for (const sg of [-1, 1])
      meshTube(mb("rail"), {p0: P(s0, sg * (W / 2 - 0.03), -0.06), p1: P(s0, sg * (W / 2 - 0.03), -0.06 - (sc.tier_h || 1.08) + 0.06), r: 0.02}, 8);
    crewFigure(mb, (s, l, h) => P(s + 0.05, l, h + 0.07), [u, v, up]);
  }
  for (const d of sc.doors) {
    const t = d.center_deg * D2R, n = [0, Math.cos(t), Math.sin(t)], tg = [0, -Math.sin(t), Math.cos(t)];
    const c = [d.floor_x - d.height_m / 2, (d.at_r_m - 0.05) * n[1], (d.at_r_m - 0.05) * n[2]];
    if (gone(c)) continue;
    meshOBox(mb("door"), c, [[1, 0, 0], tg, n], [d.height_m / 2, d.width_m / 2, 0.02]);
  }
  const m = sc.medical, half = m.width_m / 2 / m.at_r_m;
  for (const sg of [-1, 1]) {      // bi-parting doors, slid open beside the opening
    const t = m.center_deg * D2R + sg * (half + 0.6 / m.at_r_m / 1.0), n = [0, Math.cos(t), Math.sin(t)], tg = [0, -Math.sin(t), Math.cos(t)];
    const c = [(m.x_m[0] + m.x_m[1]) / 2 + 0.1, (m.at_r_m - 0.06) * n[1], (m.at_r_m - 0.06) * n[2]];
    if (!gone(c)) meshOBox(mb("door"), c, [[1, 0, 0], tg, n], [1.05, 0.6, 0.02]);
  }
  for (const l of sc.ladderways) {                 // rails and rungs on the inboard face of each shaft, every deck L1-L4
    const t = l.theta_deg * D2R, n = [0, Math.cos(t), Math.sin(t)], tg = [0, -Math.sin(t), Math.cos(t)];
    const ri = l.r_m - l.size_m / 2 + 0.06;
    for (const d of sc.decks.slice(0, -1)) {
      const xa = d.x_m[1] - 1.0, xb = d.x_m[1] + sc.floor_t_m + 2.3;
      if (gone([(xa + xb) / 2, ri * n[1], ri * n[2]])) continue;
      for (const sg of [-1, 1]) {
        const q = [0, ri * n[1] + sg * 0.22 * tg[1], ri * n[2] + sg * 0.22 * tg[2]];
        meshTube(mb("rail"), {p0: [xa, q[1], q[2]], p1: [Math.min(xb, d.x_m[1] + sc.floor_t_m + 2.29), q[1], q[2]], r: 0.018}, 8);
      }
      for (let x = d.x_m[1] + 0.15; x < d.x_m[1] + sc.floor_t_m + 2.3; x += 0.3)
        meshTube(mb("rail"), {p0: [x, ri * n[1] - 0.22 * tg[1], ri * n[2] - 0.22 * tg[2]], p1: [x, ri * n[1] + 0.22 * tg[1], ri * n[2] + 0.22 * tg[2]], r: 0.014}, 6);
    }
  }
  if (opt.litter && sc.litter) {
    const L = sc.litter, t = L.pose.theta_deg * D2R, u = [0, Math.cos(t), Math.sin(t)], v = [0, -Math.sin(t), Math.cos(t)];
    const rc = (L.pose.r_m[0] + L.pose.r_m[1]) / 2, c = [L.pose.x, rc * u[1], rc * u[2]];
    meshOBox(mb("litter"), c, [u, v, up], [L.length_m / 2, L.width_m / 2, 0.05]);
    const fl = sc.decks.find(d => d.x_m[0] < L.pose.x && L.pose.x < d.x_m[1]);
    if (fl) meshOBox(mb("couch"), [(L.pose.x + 0.05 + fl.x_m[1]) / 2, c[1], c[2]], [[1, 0, 0], u, v], [(fl.x_m[1] - L.pose.x - 0.05) / 2, L.length_m / 2 - 0.3, 0.2]);   // treatment couch
  }
  return G;
}

// L1 command scene: couches, crew, displays, ladders, from render/out/l1_scene.json (ship coords)
export function commandMeshes(sc, opt = {}) {
  const G = {}, mb = m => (G[m] ||= new MB(opt.xc));
  const hide = opt.hide || new Set(), hideCrew = opt.hideCrew || new Set(), clip = opt.clip;
  const gone = p => clip && clip[0] * p[0] + clip[1] * p[1] + clip[2] * p[2] + clip[3] > 0;
  const nrm = v => { const L = Math.hypot(...v); return v.map(x => x / L); };
  const cross = (a, b) => [a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]];
  const domeX = r => sc.dome.xb - (sc.dome.xb - sc.dome.xa) * Math.sqrt(Math.max(0, 1 - (r / sc.dome.R) ** 2));
  const hidden = new Set();
  for (const c of sc.couches) {
    const [hy, hz] = c.head, [fy, fz] = c.feet, L = c.L, u = nrm([0, fy - hy, fz - hz]), v = [0, -u[2], u[1]], up = [-1, 0, 0];
    const mid = [c.base_x, (hy + fy) / 2, (hz + fz) / 2];
    if (hide.has(c.id) || gone(mid)) { hidden.add(c.id); continue; }
    const back = sc.couch.back_above_base_m, W = sc.couch.width_m;
    const P = (s, l, t) => [c.base_x - t, hy + s * u[1] + l * v[1], hz + s * u[2] + l * v[2]];
    const box = (m, s0, s1, l0, l1, t0, t1) => meshOBox(mb(m), P((s0 + s1) / 2, (l0 + l1) / 2, (t0 + t1) / 2), [u, v, up], [(s1 - s0) / 2, (l1 - l0) / 2, (t1 - t0) / 2]);
    box("couch", 0.25, L - 0.25, -0.2, 0.2, 0, back - 0.1);                 // pedestal
    box("couch", 0, L, -W / 2, W / 2, back - 0.1, back);                     // pan
    for (const sg of [-1, 1]) {
      box("couch", 0.35, 1.15, sg * (W / 2 - 0.05) - 0.025, sg * (W / 2 - 0.05) + 0.025, back, back + 0.08);   // side bolsters
      box("couch", 0.02, 0.30, sg * 0.165 - 0.025, sg * 0.165 + 0.025, back, back + 0.12);                    // head wings
    }
    box("couch", L - 0.07, L, -0.22, 0.22, back, back + 0.2);               // foot plate
    if (hideCrew.has(c.id)) continue;
    crewFigure(mb, (s, l, t) => P(s, l, back + t), [u, v, up]);
  }
  for (const d of sc.displays) {
    if (hidden.has(d.for)) continue;
    const c = d.box.map(([a, b]) => (a + b) / 2), cc = sc.couches.find(k => k.id === d.for);
    const n = nrm(cc.eye.map((e, i) => e - c[i]));
    const [hy, hz] = cc.head, [fy, fz] = cc.feet, u = nrm([0, fy - hy, fz - hz]), lat = [0, -u[2], u[1]];
    const dl = lat[0] * n[0] + lat[1] * n[1] + lat[2] * n[2];
    const hor = nrm(lat.map((x, i) => x - dl * n[i])), ver = cross(n, hor);
    const pilot = d.for === "PILOT" || d.for === "NAV";
    meshOBox(mb("screen"), c, [hor, ver, n], [pilot ? 0.225 : 0.2, pilot ? 0.14 : 0.13, 0.015]);
    meshOBox(mb("couch"), c.map((x, i) => x - n[i] * 0.03), [hor, ver, n], [pilot ? 0.24 : 0.215, pilot ? 0.155 : 0.145, 0.015]);
    // mounts (indicative): pilots' displays hang from the dome just above them; support displays sit on an arm from the couch
    const b = c.map((x, i) => x - n[i] * 0.045);
    if (pilot && opt.crown) {   // crown concept: the dome is glass, so the pilot displays sit on arms from the flight deck's head end
      const ar = [cc.base_x, b[1], cc.head[1] + 0.12]; meshTube(mb("rail"), {p0: b, p1: [cc.base_x - 0.05, b[1], b[2]], r: 0.022}, 10);
    } else if (pilot) { const top = domeX(Math.hypot(b[1], b[2])); if (b[0] - top > 0.02) meshTube(mb("rail"), {p0: b, p1: [top, b[1], b[2]], r: 0.022}, 10); }
    else meshTube(mb("rail"), {p0: b, p1: [cc.base_x - sc.couch.back_above_base_m, b[1], b[2]], r: 0.022}, 10);
  }
  for (const it of sc.carryover || []) {
    const mt=it.id.startsWith("lights")?"screen":it.kind==="tube"||it.kind==="arc"?"rail":"equipment";
    if(it.kind==="box"){
      const c=it.xyz,[sx,sy,sz]=it.size;
      meshBox(mb(mt),[c[0]-sx/2,c[0]+sx/2,c[1]-sy/2,c[1]+sy/2,c[2]-sz/2,c[2]+sz/2]);
    }else if(it.kind==="tube"){
      meshTube(mb(mt),{p0:it.a,p1:it.b,r:it.radius_m},8);
    }else if(it.kind==="arc"){
      const [a0,a1]=it.angles_rad;
      for(let j=0;j<18;j++){const a=a0+(a1-a0)*j/18,b=a0+(a1-a0)*(j+1)/18;
        meshTube(mb("rail"),{p0:[it.x_m,it.radius_m*Math.cos(a),it.radius_m*Math.sin(a)],
             p1:[it.x_m,it.radius_m*Math.cos(b),it.radius_m*Math.sin(b)],r:it.tube_radius_m},6);}
    }
  }
  for (const l of sc.ladders) {
    const ctr = [sc.floor_x, l.y, l.z];
    if (gone(ctr)) continue;
    const s = l.size / 2, th = Math.atan2(l.z, l.y), rad = [0, Math.cos(th), Math.sin(th)], tan = [0, -Math.sin(th), Math.cos(th)];
    meshOBox(mb("well"), [sc.floor_x - 0.004, l.y, l.z], [[1, 0, 0], rad, tan], [0.004, s, s]);
    for (const sg of [-1, 1]) {
      const b = [sc.floor_x, l.y + rad[1] * (s - 0.05) + tan[1] * sg * (s - 0.08), l.z + rad[2] * (s - 0.05) + tan[2] * sg * (s - 0.08)];
      meshTube(mb("rail"), {p0: b, p1: [sc.floor_x - 1.05, b[1], b[2]], r: 0.022}, 10);
    }
    const t0 = [sc.floor_x - 1.05, l.y + rad[1] * (s - 0.05), l.z + rad[2] * (s - 0.05)];
    meshTube(mb("rail"), {p0: t0.map((x, i) => x - tan[i] * (s - 0.08)), p1: t0.map((x, i) => x + tan[i] * (s - 0.08)), r: 0.022}, 10);
  }
  const fl = sc.flight_deck_ladder;
  if (fl && !gone([(fl.x[0] + fl.x[1]) / 2, 0, fl.z])) {
    const top = opt.crown ? fl.x[0] - 0.6 : domeX(Math.hypot(fl.y[1], fl.z)) + 0.08;   // crown concept: handholds stop 0.6 m above the deck
    for (const y of fl.y) meshTube(mb("rail"), {p0: [fl.x[1], y, fl.z], p1: [top, y, fl.z], r: 0.022}, 10);
    for (let x = fl.x[1] - 0.3; x > fl.x[0] + 0.05; x -= 0.3) meshTube(mb("rail"), {p0: [x, fl.y[0], fl.z], p1: [x, fl.y[1], fl.z], r: 0.016}, 8);
  }
  return G;
}

function meshShuttle(mb, s, lift = 0) {
  const x0 = s.p0[0], L = s.p1[0] - s.p0[0], R = s.r;
  const pts = [[0, 0.0], [0.15, 0.32], [0.6, 0.62], [3.0, 1.25], [6.2, R], [L - 1.2, R], [L - 0.2, R * 0.86], [L, R * 0.78]];
  const prof = [];
  for (let i = 0; i < pts.length; i++) {
    const [a, r] = pts[i], [b, rb] = pts[Math.min(i + 1, pts.length - 1)], [pa, pr] = pts[Math.max(i - 1, 0)];
    const dx = (b - pa) || 1, dr = rb - pr, k = Math.hypot(dx, dr);
    prof.push([x0 + a, r, i === 0 ? -1 : -dr / k, i === 0 ? 0 : dx / k]);
  }
  const before = mb.p.length / 3;
  lathe(mb, prof, 48);
  lathe(mb, [[x0 + L, 0, 1, 0], [x0 + L, R * 0.78, 1, 0]], 48);
  if (lift) for (let k = before; k < mb.p.length / 3; k++) mb.p[k * 3 + 1] += lift;
}

function meshPlume(mb, x0, R0, len, ox, oy) {
  const prof = [];
  for (let i = 0; i <= 20; i++) { const t = i / 20, r = R0 * (0.75 + 1.9 * Math.sqrt(t)); prof.push([x0 + len * t, r, 0, 1]); }
  lathe(mb, prof, 48, ox, oy);
}

export function shapeMesh(mb, p, opt = {}) {
  let s = p.shape, ox = 0, oy = 0;
  if (s.offset_yz) { oy = s.offset_yz[0]; ox = s.offset_yz[1]; }
  const before = mb.p.length / 3;
  if (p.id === "shuttle" && s.k === "tube") { meshShuttle(mb, s, opt.shuttleLift || 0); return; }
  if (p.tags && p.tags.includes("strake")) {
    const span = opt.strakeSpan ?? 0;
    if (span > 0.01) meshPanel(mb, {x0: s.x0, x1: s.x1, a: s.a, r0: s.r0 + s.span, t: 0.06}, span, 0.12);
    meshPanel(mb, s, s.span);      // stowed stack / root block
    return;
  }
  if (p.tags && p.tags.includes("fin")) {      // hot fins: folded stack, or unfolded to finSpan in torch burns
    const span = opt.finSpan ?? 0;
    if (span > 0.01) meshPanel(mb, {x0: s.x0, x1: s.x1, a: s.a, r0: s.r0, t: 0.06}, span, 0.10);
    else meshPanel(mb, s, s.span);
    return;
  }
  if (p.tags && p.tags.includes("door") && opt.doorsOpen) {
    const sg = p.id.includes("starboard") ? 1 : -1, y = sg * 2.45, z0 = Math.sqrt(4.5 * 4.5 - 2.4 * 2.4);
    meshBox(mb, [s.x0, s.x1, Math.min(y, y + sg * 0.1), Math.max(y, y + sg * 0.1), z0, z0 + 2.5]);
    return;
  }
  const x0 = s.settled_fraction !== undefined ? s.x1 - s.settled_fraction * (s.x1 - s.x0) : undefined;
  switch (s.k) {
    case "sector": meshSector(mb, x0 !== undefined ? {...s, x0} : s, ox, oy); break;
    case "cslot": meshCSlot(mb, s, x0); break;
    case "domecyl": meshDome(mb, s); break;
    case "frustum": meshFrustum(mb, s, ox, oy); break;
    case "tube": meshTube(mb, s); break;
    case "box": meshBox(mb, [s.x0, s.x1, s.y0, s.y1, s.z0, s.z1]); break;
    case "panel": meshPanel(mb, s, s.span); break;
  }
  if ((ox || oy) && (s.k === "box")) for (let k = before; k < mb.p.length / 3; k++) { mb.p[k*3+1] += ox; mb.p[k*3+2] -= oy; }
}

// ------------------------------------------------------------ GL
const VS = `#version 300 es
in vec3 aP; in vec3 aN;
uniform mat4 uVP; uniform mat4 uL; uniform float uXc;
out vec3 vW; out vec3 vN; out vec4 vS; out vec3 vShip;
void main(){ vW=aP; vN=aN; vS=uL*vec4(aP,1.0); vShip=vec3(aP.x+uXc,-aP.z,aP.y); gl_Position=uVP*vec4(aP,1.0); }`;

const FS = `#version 300 es
precision highp float;
in vec3 vW; in vec3 vN; in vec4 vS; in vec3 vShip;
uniform vec3 uC; uniform float uM; uniform float uR; uniform float uSeam; uniform int uKind; uniform vec3 uEm;
uniform vec3 uSun; uniform vec3 uSunC; uniform vec3 uEye; uniform sampler2D uSh; uniform float uShOn;
uniform vec4 uClip; uniform float uClipOn; uniform float uExp; uniform float uAlpha; uniform float uHot;
uniform vec3 uPlanetDir; uniform float uShZ; uniform float uLen; uniform float uSec; uniform vec3 uRim; uniform vec3 uRimC;
uniform float uCrown; uniform float uNoSec; uniform float uHoleOn; uniform vec4 uWinP[40]; uniform vec3 uWinN[40]; uniform int uNWin; uniform vec4 uBand[6]; uniform int uNBand; uniform float uArm; uniform float uSplay;
uniform vec3 uPLP[3]; uniform vec3 uPLC[3]; uniform int uNPL;
uniform float uSkin; uniform float uSkinMat; uniform float uCold;
out vec4 o;
float hsh(vec2 p){ return fract(sin(dot(p,vec2(12.9898,78.233)))*43758.5453); }
float sh(vec3 n){
  if(uShOn<0.5) return 1.0;
  vec3 p=vS.xyz/vS.w*0.5+0.5; if(p.x<0.0||p.x>1.0||p.y<0.0||p.y>1.0) return 1.0;
  float b=0.0018+0.004*(1.0-max(dot(n,uSun),0.0)); float s=0.0; vec2 t=1.0/vec2(textureSize(uSh,0));
  for(int i=-2;i<=2;i++) for(int j=-2;j<=2;j++){ s+= (p.z-b> texture(uSh,p.xy+vec2(i,j)*t).r)?0.0:1.0; }
  return s/25.0;
}
vec3 aces(vec3 x){ return clamp((x*(2.51*x+0.03))/(x*(2.43*x+0.59)+0.14),0.0,1.0); }
vec3 env(vec3 r){ float pl=max(dot(r,uPlanetDir),0.0); return vec3(0.010,0.014,0.025)+vec3(0.05,0.11,0.22)*pow(pl,6.0)+vec3(0.015)*max(r.y,0.0); }
void main(){
  if(uClipOn>0.5 && dot(vec4(vW,1.0),uClip)>0.0) discard;
  if(uHoleOn>0.5 && uCrown>0.0 && vShip.x<1.4 && length(vShip.yz)<uCrown) discard;
  if(uHoleOn>0.5){ for(int i=0;i<40;i++){ if(i>=uNWin) break; vec3 d=vW-uWinP[i].xyz; float a=dot(d,uWinN[i]);
    if(a>-0.6 && a<0.2 && length(d-a*uWinN[i])<uWinP[i].w+clamp(a+uArm,0.0,uArm)*uSplay) discard; }
    float ang=degrees(atan(vShip.z,vShip.y)); if(ang<0.0) ang+=360.0; float rr=length(vShip.yz);
    for(int i=0;i<6;i++){ if(i>=uNBand) break; vec4 b=uBand[i]; if(rr>4.0 && vShip.x>b.x && vShip.x<b.y && ang>b.z && ang<b.w) discard; } }
  vec3 base=uC; float R=uR; float M=uM;
  if(!gl_FrontFacing){ if(uClipOn>0.5 && uNoSec<0.5){ o=vec4(pow(aces(base*uSec*uExp),vec3(1.0/2.2)),1.0); return; } discard; }
  vec3 n=normalize(vN); vec3 v=normalize(uEye-vW); vec3 l=uSun;
  bool skin = uSkin>0.5 && uSkinMat>0.5;
  if(skin){   // rev 7: bare Strata bow (placeholder look), tunable flanks: normal (light, high IR emissivity) or cold running (low-e, metallic: a proposed optical property)
    float x=vShip.x; float rr=max(length(vShip.yz),0.3); float thr=atan(vShip.z,vShip.y); float deg=degrees(thr); if(deg<0.0) deg+=360.0; float s=thr*rr;
    vec3 Ta=vec3(1.0,0.0,0.0); vec3 Tc=cross(Ta,n); Tc = length(Tc)>1e-3 ? normalize(Tc) : vec3(0.0,1.0,0.0);
    float pd=22.5; float dd=deg-11.25; vec2 cell=vec2(floor(x/2.0),floor(dd/pd)); float h1=hsh(cell), h2=hsh(cell+3.3);
    bool bow = x<2.6;
    float fwd=max(-n.x,0.0); float wear=clamp(pow(fwd,1.3)*0.9+0.4*exp(-x/2.0),0.0,1.0);
    if(bow){ base=vec3(0.105,0.098,0.092)*(0.92+0.12*h1); M=0.35; R=0.6;
      float grain=0.5+0.5*sin(s*90.0+sin(x*7.0)*1.5); base*=0.93+0.10*grain*(1.0-smoothstep(0.004,0.02,fwidth(s)));
      base=mix(base,vec3(0.16,0.15,0.14),wear*0.3); R=mix(R,0.85,wear); }
    else if(uCold<0.5){ base=vec3(0.76,0.765,0.75)*(0.95+0.08*h1); M=0.0; R=0.55+0.12*h2; }
    else { base=vec3(0.80,0.81,0.83)*(0.95+0.07*h1); M=1.0; R=0.22+0.08*h2; }
    if(uSkinMat<1.5){
      float sa=(fract(x/2.0+0.5)-0.5)*2.0; float pc=pd/57.2958*rr; float sc=(fract((dd/57.2958*rr)/pc+0.5)-0.5)*pc;
      float wa=0.008+fwidth(x)*1.2, wc=0.008+fwidth(s)*1.2;
      float ga=(1.0-smoothstep(0.0,wa,abs(sa)))*min(1.0,0.008/wa), gc=(1.0-smoothstep(0.0,wc,abs(sc)))*min(1.0,0.008/wc);
      if(bow){ ga=0.0; gc*=0.5; }
      n=normalize(n-Ta*sign(sa)*ga*0.6-Tc*sign(sc)*gc*0.6);
      base=mix(base,base*0.55,max(ga,gc)*0.85);
    }
  }
  if(uKind==9){ float f=pow(1.0-abs(dot(n,v)),1.5); float t=clamp((vShip.x-uLen)/70.0,0.0,1.0);
    o=vec4(uC*(1.0-t)*(0.6+1.6*(1.0-f)), (1.0-t)*(1.0-f)*uAlpha); return; }
  if(uSeam>0.5 && !skin){ float th=atan(vShip.z,vShip.y)*57.2958; float sx=abs(fract(vShip.x/2.0+0.5)-0.5)*2.0; float st=abs(fract(th/15.0+0.5)-0.5)*15.0*0.0785*4.5;
    float sm=smoothstep(0.0,0.035,abs(fract(vShip.x/2.0)-0.5)*2.0*1.0); float line=min(smoothstep(0.0,0.012,abs(fract(vShip.x/2.0)-0.0)),1.0);
    float a=1.0-0.18*(1.0-smoothstep(0.0,0.02,abs(fract(vShip.x/2.0+0.5)-0.5)))-0.14*(1.0-smoothstep(0.0,0.025,abs(fract(th/15.0+0.5)-0.5)*0.262*4.5));
    float tile=0.94+0.06*fract(sin(dot(floor(vec2(vShip.x/2.0,th/15.0)),vec2(12.9898,78.233)))*43758.5453); base*=a*tile; }
  if(uKind==1){ if(vShip.z< uShZ-0.55) base=vec3(0.07,0.07,0.075); }
  if(uKind==3){ float ring=step(0.5,fract(vShip.x/0.7)); base*=0.75+0.25*ring; }
  if(uKind==5){ float rr=length(vShip.yz); float an=atan(vShip.z,vShip.y)*57.2958;
    float slat=smoothstep(0.0,0.012,abs(fract(rr/0.16)-0.5)*0.16); float gore=smoothstep(0.0,0.02,abs(fract(an/22.5+0.5)-0.5)*22.5*0.0175*max(rr,0.3));
    base*=(0.80+0.20*slat)*(0.55+0.45*gore); }
  vec3 h=normalize(l+v); float nl=max(dot(n,l),0.0), nv=max(dot(n,v),1e-3), nh=max(dot(n,h),0.0), vh=max(dot(v,h),0.0);
  float a2=pow(max(R,0.05),4.0); float d=nh*nh*(a2-1.0)+1.0; float D=a2/(3.14159*d*d);
  float k=pow(R+1.0,2.0)/8.0; float G=(nl/(nl*(1.0-k)+k))*(nv/(nv*(1.0-k)+k));
  vec3 F0=mix(vec3(0.04),base,M); vec3 F=F0+(1.0-F0)*pow(1.0-vh,5.0);
  vec3 spec=D*G*F/(4.0*nl*nv+1e-3); vec3 kd=(1.0-F)*(1.0-M);
  float s=sh(n);
  vec3 col=(kd*base/3.14159+spec)*uSunC*nl*s;
  vec3 hr=normalize(uRim+v); float nlr=max(dot(n,uRim),0.0); float nhr=max(dot(n,hr),0.0); float dr=nhr*nhr*(a2-1.0)+1.0;
  col+=(kd*base/3.14159+F*(a2/(3.14159*dr*dr))*0.25)*uRimC*nlr;
  vec3 hemi=mix(vec3(0.020,0.022,0.030),vec3(0.040,0.050,0.070),n.y*0.5+0.5)+vec3(0.05,0.10,0.20)*0.35*max(dot(n,uPlanetDir),0.0);
  col+=kd*base*hemi*1.6;
  for(int i=0;i<3;i++){ if(i>=uNPL) break; vec3 lv=uPLP[i]-vW; float d2=dot(lv,lv); lv=normalize(lv); vec3 hh=normalize(lv+v);
    float q=max(dot(n,lv),0.0); float dd=pow(max(dot(n,hh),0.0),24.0)*(1.0-R)*0.6;
    col+=(kd*base/3.14159+F0*dd)*uPLC[i]*q/(1.0+0.35*d2); }
  vec3 r=reflect(-v,n); col+=env(r)*mix(F0,vec3(1.0),pow(1.0-nv,5.0))*(1.0-R*0.7)*2.0;
  if(uKind==6){ col*=0.85; }
  if(uKind==2){ col+=uHot*vec3(1.0,0.32,0.07)*(0.55+0.45*fract(sin(floor(vShip.x*0.5)*7.13)*91.7)); }
  if(uKind==4){ col+=uHot*vec3(1.0,0.44,0.12)*0.62*(0.70+0.30*fract(sin(floor(vShip.x*0.5)*5.31)*71.3)); }
  col+=uEm;
  o=vec4(pow(aces(col*uExp),vec3(1.0/2.2)),1.0);
}`;

const SVS = `#version 300 es
in vec3 aP; uniform mat4 uL; out vec3 vW; void main(){ vW=aP; gl_Position=uL*vec4(aP,1.0); }`;
const SFS = `#version 300 es
precision highp float; in vec3 vW; uniform vec4 uClip; uniform float uClipOn; out vec4 o;
void main(){ if(uClipOn>0.5 && dot(vec4(vW,1.0),uClip)>0.0) discard; o=vec4(1.0); }`;

const BVS = `#version 300 es
in vec2 aQ; out vec2 vQ; void main(){ vQ=aQ; gl_Position=vec4(aQ,0.9999,1.0); }`;
const BFS = `#version 300 es
precision highp float; in vec2 vQ; uniform mat4 uIVP; uniform vec3 uEye; uniform vec3 uSun; uniform vec3 uPlanetC; uniform float uPlanetR; uniform float uStars; uniform float uPlanetOn;
out vec4 o;
float h3(vec3 p){ p=fract(p*0.3183099+0.1); p*=17.0; return fract(p.x*p.y*p.z*(p.x+p.y+p.z)); }
vec3 aces(vec3 x){ return clamp((x*(2.51*x+0.03))/(x*(2.43*x+0.59)+0.14),0.0,1.0); }
void main(){
  vec4 a=uIVP*vec4(vQ,1.0,1.0); vec3 d=normalize(a.xyz/a.w-uEye);
  vec3 col=vec3(0.0035,0.004,0.007);
  vec3 g=d*300.0; vec3 c=floor(g); float s=h3(c); vec3 f=fract(g)-0.5;
  if(s>0.985){ float b=pow((s-0.985)/0.015,3.0); float dd=length(f); col+=vec3(0.8,0.85,1.0)*b*smoothstep(0.32,0.0,dd)*uStars; }
  vec3 g2=d*90.0; vec3 c2=floor(g2); float s2=h3(c2+7.0); if(s2>0.996){ float dd=length(fract(g2)-0.5); col+=vec3(1.0,0.95,0.85)*smoothstep(0.25,0.0,dd)*1.4*uStars; }
  if(uPlanetOn>0.5){
    vec3 oc=uEye-uPlanetC; float b=dot(oc,d); float cc=dot(oc,oc)-uPlanetR*uPlanetR; float disc=b*b-cc;
    float dist=length(cross(d,uPlanetC-uEye));
    if(disc>0.0 && -b-sqrt(disc)>0.0){ vec3 p=uEye+d*(-b-sqrt(disc)); vec3 n=normalize(p-uPlanetC);
      float lat=dot(n,normalize(vec3(0.15,1.0,0.1))); float band=0.5+0.5*sin(lat*38.0+sin(lat*9.0)*1.7);
      vec3 alb=mix(vec3(0.10,0.21,0.42),vec3(0.15,0.30,0.55),band*0.6); float nl=max(dot(n,uSun),0.0);
      float rim=pow(1.0-max(dot(n,-d),0.0),3.0);
      col=alb*(nl*1.25+0.015)+vec3(0.35,0.6,1.0)*rim*nl*0.8; }
    else { float glow=smoothstep(uPlanetR*1.06,uPlanetR,dist); col+=vec3(0.2,0.42,0.9)*glow*glow*0.35*max(dot(normalize(uPlanetC-uEye),uSun)*-0.5+0.6,0.2); }
  }
  o=vec4(pow(aces(col*1.6),vec3(1.0/2.2)),1.0);
}`;

function compile(gl, vs, fs) {
  const p = gl.createProgram();
  for (const [t, src] of [[gl.VERTEX_SHADER, vs], [gl.FRAGMENT_SHADER, fs]]) {
    const s = gl.createShader(t); gl.shaderSource(s, src); gl.compileShader(s);
    if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(s));
    gl.attachShader(p, s);
  }
  gl.bindAttribLocation(p, 0, "aP"); gl.bindAttribLocation(p, 1, "aN"); gl.bindAttribLocation(p, 0, "aQ");
  gl.linkProgram(p);
  if (!gl.getProgramParameter(p, gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(p));
  const U = {}; const n = gl.getProgramParameter(p, gl.ACTIVE_UNIFORMS);
  for (let i = 0; i < n; i++) { const u = gl.getActiveUniform(p, i); U[u.name] = gl.getUniformLocation(p, u.name); }
  return {p, U};
}

// ------------------------------------------------------------ math
export const M4 = {
  mul(a, b) { const o = new Float32Array(16); for (let i = 0; i < 4; i++) for (let j = 0; j < 4; j++) { let s = 0; for (let k = 0; k < 4; k++) s += a[k * 4 + j] * b[i * 4 + k]; o[i * 4 + j] = s; } return o; },
  persp(fov, asp, n, f) { const t = 1 / Math.tan(fov / 2), o = new Float32Array(16); o[0] = t / asp; o[5] = t; o[10] = (f + n) / (n - f); o[11] = -1; o[14] = 2 * f * n / (n - f); return o; },
  ortho(l, r, b, t, n, f) { const o = new Float32Array(16); o[0] = 2 / (r - l); o[5] = 2 / (t - b); o[10] = -2 / (f - n); o[12] = -(r + l) / (r - l); o[13] = -(t + b) / (t - b); o[14] = -(f + n) / (f - n); o[15] = 1; return o; },
  look(e, c, u) {
    const z = norm(sub(e, c)), x = norm(crs(u, z)), y = crs(z, x), o = new Float32Array(16);
    o[0] = x[0]; o[4] = x[1]; o[8] = x[2]; o[1] = y[0]; o[5] = y[1]; o[9] = y[2]; o[2] = z[0]; o[6] = z[1]; o[10] = z[2];
    o[12] = -dot(x, e); o[13] = -dot(y, e); o[14] = -dot(z, e); o[15] = 1; return o;
  },
  inv(m) {
    const a = m, o = new Float32Array(16);
    const b00 = a[0]*a[5]-a[1]*a[4], b01 = a[0]*a[6]-a[2]*a[4], b02 = a[0]*a[7]-a[3]*a[4], b03 = a[1]*a[6]-a[2]*a[5], b04 = a[1]*a[7]-a[3]*a[5], b05 = a[2]*a[7]-a[3]*a[6];
    const b06 = a[8]*a[13]-a[9]*a[12], b07 = a[8]*a[14]-a[10]*a[12], b08 = a[8]*a[15]-a[11]*a[12], b09 = a[9]*a[14]-a[10]*a[13], b10 = a[9]*a[15]-a[11]*a[13], b11 = a[10]*a[15]-a[11]*a[14];
    let d = b00*b11-b01*b10+b02*b09+b03*b08-b04*b07+b05*b06; d = 1 / d;
    o[0]=(a[5]*b11-a[6]*b10+a[7]*b09)*d; o[1]=(a[2]*b10-a[1]*b11-a[3]*b09)*d; o[2]=(a[13]*b05-a[14]*b04+a[15]*b03)*d; o[3]=(a[10]*b04-a[9]*b05-a[11]*b03)*d;
    o[4]=(a[6]*b08-a[4]*b11-a[7]*b07)*d; o[5]=(a[0]*b11-a[2]*b08+a[3]*b07)*d; o[6]=(a[14]*b02-a[12]*b05-a[15]*b01)*d; o[7]=(a[8]*b05-a[10]*b02+a[11]*b01)*d;
    o[8]=(a[4]*b10-a[5]*b08+a[7]*b06)*d; o[9]=(a[1]*b08-a[0]*b10-a[3]*b06)*d; o[10]=(a[12]*b04-a[13]*b02+a[15]*b00)*d; o[11]=(a[9]*b02-a[8]*b04-a[11]*b00)*d;
    o[12]=(a[5]*b07-a[4]*b09-a[6]*b06)*d; o[13]=(a[0]*b09-a[1]*b07+a[2]*b06)*d; o[14]=(a[13]*b01-a[12]*b03-a[14]*b00)*d; o[15]=(a[8]*b03-a[9]*b01+a[10]*b00)*d;
    return o;
  },
};
const sub = (a, b) => a.map((v, i) => v - b[i]), dot = (a, b) => a[0]*b[0]+a[1]*b[1]+a[2]*b[2];
const crs = (a, b) => [a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]];
const norm = a => { const l = Math.hypot(...a) || 1; return a.map(v => v / l); };
export const V3 = {sub, dot, crs, norm};

// ------------------------------------------------------------ scene
export class Ship {
  constructor(canvas, geo, opts = {}) {
    this.cv = canvas; this.geo = geo; this.xc = geo.length_m / 2;
    const gl = canvas.getContext("webgl2", {antialias: true, preserveDrawingBuffer: true});
    if (!gl) throw new Error("WebGL2 not available");
    this.gl = gl;
    this.main = compile(gl, VS, FS); this.shp = compile(gl, SVS, SFS); this.bg = compile(gl, BVS, BFS);
    this.quad = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, this.quad); gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);
    this.shSize = opts.shadowSize || 2048;
    this.shTex = gl.createTexture(); gl.bindTexture(gl.TEXTURE_2D, this.shTex);
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.DEPTH_COMPONENT32F, this.shSize, this.shSize, 0, gl.DEPTH_COMPONENT, gl.FLOAT, null);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.NEAREST); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.NEAREST);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
    this.fb = gl.createFramebuffer(); gl.bindFramebuffer(gl.FRAMEBUFFER, this.fb);
    gl.framebufferTexture2D(gl.FRAMEBUFFER, gl.DEPTH_ATTACHMENT, gl.TEXTURE_2D, this.shTex, 0); gl.bindFramebuffer(gl.FRAMEBUFFER, null);
    this.meshes = [];
  }

  // config: {show(part)->bool, strakeSpan, finSpan, doorsOpen, shuttleLift, fluids:[parts], plume, guestCabins:Set}
  build(cfg) {
    const gl = this.gl;
    for (const m of this.meshes) { gl.deleteBuffer(m.pb); gl.deleteBuffer(m.nb); gl.deleteBuffer(m.ib); }
    this.meshes = [];
    const groups = {};
    const parts = [...this.geo.parts, ...(cfg.fluids || [])];
    for (const p of parts) {
      if (cfg.show && !cfg.show(p)) continue;
      if ((p.tags || []).includes("no_render")) continue;
      if (cfg.roomsAsFloors && (p.tags || []).includes("room") && p.shape.k === "sector") {
        const s = p.shape, key = (p.mat === "room_cabin" && p.id.includes("-G") ? "room_cabin_guest" : p.mat) + "|floor";
        (groups[key] ||= {mat: key.split("|")[0], system: "floorplan", mb: new MB(this.xc), ids: []});
        meshSector(groups[key].mb, {...s, x0: s.x1 - 0.03, x1: s.x1 - 0.005});
        continue;
      }
      let mat = p.mat;
      if (mat === "room_cabin" && p.id.includes("-G")) mat = "room_cabin_guest";
      const key = mat + "|" + p.system;
      (groups[key] ||= {mat, system: p.system, mb: new MB(this.xc), ids: []});
      shapeMesh(groups[key].mb, p, cfg); groups[key].ids.push(p.id);
    }
    const tw = (p) => this.toWorld(...p), twn = n => [n[0], n[2], -n[1]];
    const crown = cfg.crown || null;
    this.crownR = crown ? crown.r : 0;
    const wins = (this.geo.features || []).filter(f => f.kind === "window" && !(crown && f.forward));
    this.win = wins.slice(0, 40).map(f => ({p: tw(f.pos), n: twn(f.normal), r: f.d_m / 2}));
    if (crown) {
      const G = crownMeshes(crown, this.xc);
      for (const [mat, mb] of Object.entries(G)) groups[mat + "|crown"] = {mat, system: "crown", mb, ids: ["crown_concept"]};
    }
    this.bore = cfg.bore || this.geo.window_bore || {wall_m: 0.23, armour_m: 0.2, splay_deg: 0};
    if (cfg.windowFrames) {
      const mb = new MB(this.xc), pane = new MB(this.xc);
      for (const f of wins) {
        const n = f.normal, p = f.pos, r = f.d_m / 2;
        meshBore(mb, p, n, r, this.bore);
        if (cfg.windowPanes) meshTube(pane, {p0: p.map((v, i) => v - n[i] * (this.bore.armour_m + 0.01)), p1: p.map((v, i) => v - n[i] * this.bore.armour_m), r: r + 0.01}, 40);
      }
      groups["frame|feature"] = {mat: "frame", system: "feature", mb, ids: ["window_frames"]};
      if (cfg.windowPanes) groups["window|feature"] = {mat: "window", system: "feature", mb: pane, ids: ["window_panes"]};
    }
    // v0.5.7 rev 3: viewport band (open: panes, Osteon mullions, sill and head; closed: tambour shutter flush with the armour)
    this.bandHoles = [];
    const bands = (cfg.bands === false) ? [] : (this.geo.bands || []);
    if (bands.length) {
      const pane = new MB(this.xc), fr = new MB(this.xc), lip = new MB(this.xc), sh = new MB(this.xc);
      for (const b of bands) {
        const [x0, x1] = b.x, [a0, a1] = b.a;
        if (cfg.shuttersClosed) { latheArc(sh, [[x0 - 0.03, 4.505, 0, 1], [x1 + 0.03, 4.505, 0, 1]], a0, a1); continue; }
        this.bandHoles.push([x0, x1, a0, a1]);
        latheArc(pane, [[x0, 4.30, 0, 1], [x1, 4.30, 0, 1]], a0, a1);
        for (const xe of [x0, x1]) latheArc(lip, [[xe - 0.05, 4.27, 0, 1], [xe - 0.05, 4.53, -1, 0], [xe + 0.05, 4.53, 1, 0], [xe + 0.05, 4.27, 0, 1]], a0, a1);
        if (x1 - x0 > 1.0) { const xm = (x0 + x1) / 2; latheArc(fr, [[xm - 0.04, 4.28, 0, 1], [xm - 0.04, 4.46, -1, 0], [xm + 0.04, 4.46, 1, 0], [xm + 0.04, 4.28, 0, 1]], a0, a1); }   // rev 4: lounge transom
        for (let a = a0; a <= a1 + 1e-6; a += b.mullion_deg) {
          const t = a * D2R, c = Math.cos(t), s_ = Math.sin(t), R = [0, c, s_], Tn = [0, -s_, c];
          const end = a === a0 || a1 - a < 1e-6;
          meshOBox(fr, [(x0 + x1) / 2, 4.39 * c, 4.39 * s_], [[1, 0, 0], R, Tn], [(x1 - x0) / 2, 0.12, end ? 0.06 : 0.025]);
          for (const xe of [x0, x1]) meshOBox(fr, [xe, 4.39 * c, 4.39 * s_], [[1, 0, 0], R, Tn], [0.09, 0.12, 0.07]);   // forked root where the mullion meets the sill
        }
      }
      for (const [g, mat] of [[pane, "window"], [fr, "frame"], [lip, "brow"], [sh, "shutter"]]) if (g.p.length) groups[mat + "|band"] = {mat, system: "band", mb: g, ids: ["viewport_band"]};
    }
    if (cfg.cmd) {
      const sc = {...cfg.cmd}, ring = this.geo.parts.find(p => p.id === "bow_sensors");
      if (ring) { sc.ring_rin = ring.shape.rin; sc.ring_x = ring.shape.xc; sc.ring_gaps = ring.shape.gaps; }
      const G = commandMeshes(sc, {xc: this.xc, hide: new Set(cfg.cmdHide || []), hideCrew: new Set(cfg.cmdHideCrew || []), clip: cfg.cmdClip, crown: !!cfg.crown});
      for (const [mat, mb] of Object.entries(G)) groups[mat + "|cmd"] = {mat, system: "cmd", mb, ids: ["l1_scene"], noclip: true};
    }
    if (cfg.hab) {
      const G = habitatMeshes({...cfg.hab, tier_h: cfg.hab.tier_h}, {xc: this.xc, clip: cfg.cmdClip, litter: cfg.litter});
      for (const [mat, mb] of Object.entries(G)) groups[mat + "|hab"] = {mat, system: "hab", mb, ids: ["hab_scene"], noclip: true};
    }
    if (cfg.features) for (const f of this.geo.features || []) {
      if (f.kind === "window" && cfg.windowFrames) continue;   // drawn as openings with panes instead
      if (f.kind === "node_face") {   // rev 7: visible flush face (materials, cover and seal OPEN)
        (groups["node_face|feature"] ||= {mat: "node_face", system: "feature", mb: new MB(this.xc), ids: []});
        const n = f.normal, p = f.pos, r = f.d_m / 2;
        meshTube(groups["node_face|feature"].mb, {p0: p.map((v, i) => v - n[i] * 0.02), p1: p.map((v, i) => v + n[i] * 0.012), r}, 28);
        (groups["port|nodering"] ||= {mat: "port", system: "feature", mb: new MB(this.xc), ids: []});
        meshTube(groups["port|nodering"].mb, {p0: p.map((v, i) => v - n[i] * 0.02), p1: p.map((v, i) => v + n[i] * 0.008), r: r + 0.035}, 28);
        continue;
      }
      const mat = f.kind === "hold_door" ? "hold_door" : f.kind;
      const key = mat + "|feature";
      (groups[key] ||= {mat, system: "feature", mb: new MB(this.xc), ids: []});
      const mb = groups[key].mb, n = f.normal, p = f.pos;
      if (f.kind === "hold_door") {
        const [w, h] = f.size_m, th = Math.atan2(p[2], p[1]), tn = [0, -Math.sin(th), Math.cos(th)];
        const c = (a, b, o) => [p[0] + a, p[1] + n[1] * o + tn[1] * b, p[2] + n[2] * o + tn[2] * b];
        mb.quad(c(-w / 2, -h / 2, 0.035), c(w / 2, -h / 2, 0.035), c(w / 2, h / 2, 0.035), c(-w / 2, h / 2, 0.035), n);
      } else {
        const r = f.d_m / 2, dz = f.kind === "hatch" ? 0.07 : 0.06;
        if (f.kind === "window" && cfg.shuttersClosed) {   // Strata dust shutter closed over the viewport
          (groups["shutter|feature"] ||= {mat: "shutter", system: "feature", mb: new MB(this.xc), ids: []});
          meshTube(groups["shutter|feature"].mb, {p0: p.map((v, i) => v - n[i] * 0.05), p1: p.map((v, i) => v + n[i] * dz), r: r + 0.02});
          continue;
        }
        meshTube(mb, {p0: p.map((v, i) => v - n[i] * 0.05), p1: p.map((v, i) => v + n[i] * dz), r});
        if (f.kind === "window") {
          (groups["hatch|feature"] ||= {mat: "hatch", system: "feature", mb: new MB(this.xc), ids: []});
          meshTube(groups["hatch|feature"].mb, {p0: p.map((v, i) => v - n[i] * 0.05), p1: p.map((v, i) => v + n[i] * 0.035), r: r + 0.09});
        }
      }
    }
    if (cfg.shuttleDetail !== false && parts.some(p => p.id === "shuttle" && (!cfg.show || cfg.show(p)))) {
      const s = this.geo.parts.find(p => p.id === "shuttle").shape, lift = cfg.shuttleLift || 0;
      const mb = new MB(this.xc); const L = s.p1[0] - s.p0[0];
      meshFrustum(mb, {x0: s.p1[0] - 0.05, x1: s.p1[0] + 0.9, r0: 0.75, r1: 1.15, t: 0.05}, lift, 0);
      for (const a of [62, 82, 98, 118]) { const th = a * D2R, x = s.p0[0] + 2.2, r = 1.08;
        meshTube(mb, {p0: [x, (r - 0.04) * Math.cos(th), (r - 0.04) * Math.sin(th) + lift], p1: [x + 0.02, (r + 0.06) * Math.cos(th), (r + 0.06) * Math.sin(th) + lift], r: 0.17}); }
      groups["engine_bell|shuttle"] = {mat: "engine_bell", system: "shuttle", mb, ids: ["shuttle_detail"]};
    }
    if (cfg.plume) {
      const off = this.geo.thrust_line_offset_m;
      const mb = new MB(this.xc); meshPlume(mb, this.geo.length_m, 3.0, 70, off.z, off.y);
      groups["plume"] = {mat: "plume", system: "plume", mb, ids: ["plume"]};
    }
    for (const g of Object.values(groups)) {
      const m = {mat: g.mat, system: g.system, n: g.mb.i.length, ids: g.ids, noclip: !!g.noclip};
      m.pb = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, m.pb); gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(g.mb.p), gl.STATIC_DRAW);
      m.nb = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, m.nb); gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(g.mb.n), gl.STATIC_DRAW);
      m.ib = gl.createBuffer(); gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, m.ib); gl.bufferData(gl.ELEMENT_ARRAY_BUFFER, new Uint32Array(g.mb.i), gl.STATIC_DRAW);
      this.meshes.push(m);
    }
    this.cfg = cfg;
    return this.meshes.reduce((s, m) => s + m.n / 3, 0);
  }

  toWorld(x, y, z) { return [x - this.xc, z, -y]; }

  // view: {eye:[ship xyz], target:[ship xyz], fov, sun:[world dir], clip:[a,b,c,d] in ship coords (keep where a x + b y + c z + d <= 0), exposure, planet, hot, stars}
  draw(view) {
    const gl = this.gl, W = this.cv.width, H = this.cv.height;
    const eye = this.toWorld(...view.eye), tgt = this.toWorld(...view.target);
    const up = view.up ? this.toWorld(...view.up).map((v, i) => v - this.toWorld(0, 0, 0)[i]) : [0, 1, 0];
    const P = view.ortho ? M4.ortho(-view.ortho * W / H, view.ortho * W / H, -view.ortho, view.ortho, 0.1, 2000) : M4.persp((view.fov || 35) * D2R, W / H, view.near || 0.5, 3000);
    const Vm = M4.look(eye, tgt, up), VP = M4.mul(P, Vm);
    const sun = norm(view.sun || [-0.55, 0.62, 0.55]);
    const lc = [0, 0, 0], le = lc.map((v, i) => v + sun[i] * 120);
    const LV = M4.look(le, lc, Math.abs(sun[1]) > 0.95 ? [1, 0, 0] : [0, 1, 0]), LP = M4.ortho(-40, 40, -40, 40, 1, 260), L = M4.mul(LP, LV);
    // shadow pass
    gl.bindFramebuffer(gl.FRAMEBUFFER, this.fb); gl.viewport(0, 0, this.shSize, this.shSize);
    gl.clear(gl.DEPTH_BUFFER_BIT); gl.enable(gl.DEPTH_TEST); gl.disable(gl.CULL_FACE);
    let clip = [0, 0, 0, 0], clipOn = 0;
    if (view.clip) { const [a, b, c, d] = view.clip; clip = [a, c, -b, d + a * this.xc]; clipOn = 1; }
    gl.useProgram(this.shp.p); gl.uniformMatrix4fv(this.shp.U.uL, false, L); gl.uniform4fv(this.shp.U.uClip, clip);
    for (const m of this.meshes) { if (m.mat === "plume") continue; gl.uniform1f(this.shp.U.uClipOn, m.noclip ? 0 : clipOn);
      this.bind(m, false); gl.drawElements(gl.TRIANGLES, m.n, gl.UNSIGNED_INT, 0); }
    gl.bindFramebuffer(gl.FRAMEBUFFER, null); gl.viewport(0, 0, W, H);
    gl.clearColor(0, 0, 0, 1); gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);
    // background
    const planetC = view.planetC ? this.toWorld(...view.planetC) : [-900, -600, -1400];
    gl.disable(gl.DEPTH_TEST); gl.useProgram(this.bg.p);
    gl.uniformMatrix4fv(this.bg.U.uIVP, false, M4.inv(VP)); gl.uniform3fv(this.bg.U.uEye, eye); gl.uniform3fv(this.bg.U.uSun, sun);
    gl.uniform3fv(this.bg.U.uPlanetC, planetC); gl.uniform1f(this.bg.U.uPlanetR, view.planetR || 700); gl.uniform1f(this.bg.U.uStars, view.stars ?? 1);
    gl.uniform1f(this.bg.U.uPlanetOn, view.planet ? 1 : 0);
    gl.bindBuffer(gl.ARRAY_BUFFER, this.quad); gl.enableVertexAttribArray(0); gl.vertexAttribPointer(0, 2, gl.FLOAT, false, 0, 0); gl.disableVertexAttribArray(1);
    gl.drawArrays(gl.TRIANGLES, 0, 3);
    // main
    gl.enable(gl.DEPTH_TEST); gl.useProgram(this.main.p); const U = this.main.U;
    gl.uniformMatrix4fv(U.uVP, false, VP); gl.uniformMatrix4fv(U.uL, false, L); gl.uniform1f(U.uXc, this.xc);
    gl.uniform3fv(U.uSun, sun); gl.uniform3fv(U.uSunC, view.sunC || [3.4, 3.25, 3.05]); gl.uniform3fv(U.uEye, eye);
    gl.uniform3fv(U.uPlanetDir, norm(planetC.map((v, i) => v - eye[i])));
    gl.uniform3fv(U.uRim, norm(view.rim || [0.6, -0.15, -0.8])); gl.uniform3fv(U.uRimC, view.rimC || [0.22, 0.30, 0.45]);
    gl.activeTexture(gl.TEXTURE0); gl.bindTexture(gl.TEXTURE_2D, this.shTex); gl.uniform1i(U.uSh, 0); gl.uniform1f(U.uShOn, view.shadows === false ? 0 : 1);
    gl.uniform4fv(U.uClip, clip);
    const W16 = new Float32Array(160), N16 = new Float32Array(120), win = this.win || [];
    win.forEach((w, i) => { W16.set([...w.p, w.r], i * 4); N16.set(w.n, i * 3); });
    gl.uniform4fv(U["uWinP[0]"], W16); gl.uniform3fv(U["uWinN[0]"], N16); gl.uniform1i(U.uNWin, win.length);
    const BH = new Float32Array(24); (this.bandHoles || []).slice(0, 6).forEach((b, i) => BH.set(b, i * 4));
    if (U["uBand[0]"]) { gl.uniform4fv(U["uBand[0]"], BH); gl.uniform1i(U.uNBand, Math.min(6, (this.bandHoles || []).length)); }
    const bo = this.bore || {armour_m: 0.2, splay_deg: 0}; gl.uniform1f(U.uCrown, this.crownR || 0); gl.uniform1f(U.uArm, bo.armour_m); gl.uniform1f(U.uSplay, Math.tan(bo.splay_deg * D2R));
    const lights = (view.lights || []).slice(0, 3), PLP = new Float32Array(9), PLC = new Float32Array(9);
    lights.forEach((l, i) => { PLP.set(this.toWorld(...l.at), i * 3); PLC.set(l.c, i * 3); });
    gl.uniform3fv(U["uPLP[0]"], PLP); gl.uniform3fv(U["uPLC[0]"], PLC); gl.uniform1i(U.uNPL, lights.length); gl.uniform1f(U.uClipOn, clipOn); gl.uniform1f(U.uExp, view.exposure || 1.0); gl.uniform1f(U.uHot, view.hot || 0);
    gl.uniform1f(U.uShZ, (this.cfg && this.cfg.shuttleLift) || 0); gl.uniform1f(U.uLen, this.geo.length_m);
    for (const m of this.meshes) {
      if (m.mat === "plume") continue;
      const mt = MATS[m.mat] || MATS.equipment;
      gl.uniform1f(U.uSkin, view.finish || 0); gl.uniform1f(U.uSkinMat, SKINMAT[m.mat] || 0); gl.uniform1f(U.uCold, view.cold || 0);
      gl.uniform3fv(U.uC, mt.c); gl.uniform1f(U.uM, mt.m); gl.uniform1f(U.uR, mt.r); gl.uniform1f(U.uSeam, mt.seam || 0); gl.uniform1i(U.uKind, mt.kind || 0);
      gl.uniform3fv(U.uEm, (view.emissive && view.emissive[m.mat]) || mt.em || [0, 0, 0]); gl.uniform1f(U.uAlpha, 1); gl.uniform1f(U.uSec, mt.sec ?? 0.55);
      gl.uniform1f(U.uClipOn, m.noclip ? 0 : clipOn); gl.uniform1f(U.uHoleOn, view.holes && mt.holes ? 1 : 0); gl.uniform1f(U.uNoSec, mt.nosec ? 1 : 0);
      this.bind(m, true); gl.drawElements(gl.TRIANGLES, m.n, gl.UNSIGNED_INT, 0);
    }
    const pl = this.meshes.find(m => m.mat === "plume");
    if (pl) {
      gl.enable(gl.BLEND); gl.blendFunc(gl.SRC_ALPHA, gl.ONE); gl.depthMask(false); gl.uniform1f(U.uClipOn, 0);
      const mt = MATS.plume; gl.uniform3fv(U.uC, mt.c.map(v => v * (view.plumeI || 1.0))); gl.uniform1i(U.uKind, 9); gl.uniform1f(U.uAlpha, 0.9);
      this.bind(pl, true); gl.drawElements(gl.TRIANGLES, pl.n, gl.UNSIGNED_INT, 0);
      gl.depthMask(true); gl.disable(gl.BLEND);
    }
    this.VP = VP;
  }

  bind(m, normals) {
    const gl = this.gl;
    gl.bindBuffer(gl.ARRAY_BUFFER, m.pb); gl.enableVertexAttribArray(0); gl.vertexAttribPointer(0, 3, gl.FLOAT, false, 0, 0);
    if (normals) { gl.bindBuffer(gl.ARRAY_BUFFER, m.nb); gl.enableVertexAttribArray(1); gl.vertexAttribPointer(1, 3, gl.FLOAT, false, 0, 0); }
    else gl.disableVertexAttribArray(1);
    gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, m.ib);
  }

  project(x, y, z) {   // ship coords -> CSS pixel position on the canvas
    const w = this.toWorld(x, y, z), m = this.VP;
    const cx = m[0]*w[0]+m[4]*w[1]+m[8]*w[2]+m[12], cy = m[1]*w[0]+m[5]*w[1]+m[9]*w[2]+m[13], cw = m[3]*w[0]+m[7]*w[1]+m[11]*w[2]+m[15];
    const r = this.cv.getBoundingClientRect();
    return [(cx / cw * 0.5 + 0.5) * r.width, (1 - (cy / cw * 0.5 + 0.5)) * r.height, cw > 0];
  }
}

export {MB};
