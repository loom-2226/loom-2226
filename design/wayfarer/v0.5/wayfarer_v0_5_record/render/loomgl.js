// loomgl.js -- ALL bodies. ALL sponsors. 2026-2226.
// NON-GOVERNING SANDBOX. A small self-contained WebGL2 renderer for Wayfarer v0.5.
// Builds meshes from the part shapes in wayfarer_v05_geometry.json (the same
// shapes certify.py checks), so every image is generated from the hashed
// geometry. No external libraries.
// Ship coordinates: x bow->aft, y starboard, z toward the shuttle slot.
// World (GL) coordinates: X = x - xc, Y = z, Z = -y.

export const MATS = {
  hull_armor:   {c: [0.60, 0.60, 0.585], m: 0.05, r: 0.72, seam: 1},
  hull_skin:    {c: [0.66, 0.665, 0.65], m: 0.08, r: 0.62, seam: 1},
  door:         {c: [0.50, 0.51, 0.53], m: 0.15, r: 0.55, seam: 1},
  pressure_hull:{c: [0.82, 0.82, 0.80], m: 0.0, r: 0.6},
  bulkhead:     {c: [0.55, 0.55, 0.56], m: 0.2, r: 0.6},
  floor:        {c: [0.42, 0.43, 0.45], m: 0.2, r: 0.7},
  core:         {c: [0.45, 0.46, 0.48], m: 0.3, r: 0.5},
  avionics:     {c: [0.16, 0.20, 0.24], m: 0.4, r: 0.4},
  outfit:       {c: [0.42, 0.43, 0.45], m: 0.1, r: 0.8},
  radiator:     {c: [0.05, 0.05, 0.055], m: 0.35, r: 0.35, kind: 2},
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
  hatch:        {c: [0.72, 0.72, 0.70], m: 0.3, r: 0.4},
  hold_door:    {c: [0.46, 0.47, 0.49], m: 0.3, r: 0.5},
  engine_bell:  {c: [0.10, 0.10, 0.11], m: 0.8, r: 0.3},
};
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

function meshDome(mb, s) {
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
out vec4 o;
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
  vec3 base=uC;
  if(!gl_FrontFacing){ if(uClipOn>0.5){ o=vec4(pow(aces(base*uSec*uExp),vec3(1.0/2.2)),1.0); return; } discard; }
  vec3 n=normalize(vN); vec3 v=normalize(uEye-vW); vec3 l=uSun;
  if(uKind==9){ float f=pow(1.0-abs(dot(n,v)),1.5); float t=clamp((vShip.x-uLen)/70.0,0.0,1.0);
    o=vec4(uC*(1.0-t)*(0.6+1.6*(1.0-f)), (1.0-t)*(1.0-f)*uAlpha); return; }
  if(uSeam>0.5){ float th=atan(vShip.z,vShip.y)*57.2958; float sx=abs(fract(vShip.x/2.0+0.5)-0.5)*2.0; float st=abs(fract(th/15.0+0.5)-0.5)*15.0*0.0785*4.5;
    float sm=smoothstep(0.0,0.035,abs(fract(vShip.x/2.0)-0.5)*2.0*1.0); float line=min(smoothstep(0.0,0.012,abs(fract(vShip.x/2.0)-0.0)),1.0);
    float a=1.0-0.18*(1.0-smoothstep(0.0,0.02,abs(fract(vShip.x/2.0+0.5)-0.5)))-0.14*(1.0-smoothstep(0.0,0.025,abs(fract(th/15.0+0.5)-0.5)*0.262*4.5));
    float tile=0.94+0.06*fract(sin(dot(floor(vec2(vShip.x/2.0,th/15.0)),vec2(12.9898,78.233)))*43758.5453); base*=a*tile; }
  if(uKind==1){ if(vShip.z< uShZ-0.55) base=vec3(0.07,0.07,0.075); }
  if(uKind==3){ float ring=step(0.5,fract(vShip.x/0.7)); base*=0.75+0.25*ring; }
  vec3 h=normalize(l+v); float nl=max(dot(n,l),0.0), nv=max(dot(n,v),1e-3), nh=max(dot(n,h),0.0), vh=max(dot(v,h),0.0);
  float a2=pow(max(uR,0.05),4.0); float d=nh*nh*(a2-1.0)+1.0; float D=a2/(3.14159*d*d);
  float k=pow(uR+1.0,2.0)/8.0; float G=(nl/(nl*(1.0-k)+k))*(nv/(nv*(1.0-k)+k));
  vec3 F0=mix(vec3(0.04),base,uM); vec3 F=F0+(1.0-F0)*pow(1.0-vh,5.0);
  vec3 spec=D*G*F/(4.0*nl*nv+1e-3); vec3 kd=(1.0-F)*(1.0-uM);
  float s=sh(n);
  vec3 col=(kd*base/3.14159+spec)*uSunC*nl*s;
  vec3 hr=normalize(uRim+v); float nlr=max(dot(n,uRim),0.0); float nhr=max(dot(n,hr),0.0); float dr=nhr*nhr*(a2-1.0)+1.0;
  col+=(kd*base/3.14159+F*(a2/(3.14159*dr*dr))*0.25)*uRimC*nlr;
  vec3 hemi=mix(vec3(0.020,0.022,0.030),vec3(0.040,0.050,0.070),n.y*0.5+0.5)+vec3(0.05,0.10,0.20)*0.35*max(dot(n,uPlanetDir),0.0);
  col+=kd*base*hemi*1.6; vec3 r=reflect(-v,n); col+=env(r)*mix(F0,vec3(1.0),pow(1.0-nv,5.0))*(1.0-uR*0.7)*2.0;
  if(uKind==2){ col+=uHot*vec3(1.0,0.32,0.07)*(0.55+0.45*fract(sin(floor(vShip.x*0.5)*7.13)*91.7)); }
  col+=uEm;
  o=vec4(pow(aces(col*uExp),vec3(1.0/2.2)),1.0);
}`;

const SVS = `#version 300 es
in vec3 aP; uniform mat4 uL; void main(){ gl_Position=uL*vec4(aP,1.0); }`;
const SFS = `#version 300 es
precision highp float; out vec4 o; void main(){ o=vec4(1.0); }`;

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

  // config: {show(part)->bool, strakeSpan, doorsOpen, shuttleLift, fluids:[parts], plume, guestCabins:Set}
  build(cfg) {
    const gl = this.gl;
    for (const m of this.meshes) { gl.deleteBuffer(m.pb); gl.deleteBuffer(m.nb); gl.deleteBuffer(m.ib); }
    this.meshes = [];
    const groups = {};
    const parts = [...this.geo.parts, ...(cfg.fluids || [])];
    for (const p of parts) {
      if (cfg.show && !cfg.show(p)) continue;
      let mat = p.mat;
      if (mat === "room_cabin" && p.id.includes("-G")) mat = "room_cabin_guest";
      const key = mat + "|" + p.system;
      (groups[key] ||= {mat, system: p.system, mb: new MB(this.xc), ids: []});
      shapeMesh(groups[key].mb, p, cfg); groups[key].ids.push(p.id);
    }
    if (cfg.features) for (const f of this.geo.features || []) {
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
      const m = {mat: g.mat, system: g.system, n: g.mb.i.length, ids: g.ids};
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
    const P = view.ortho ? M4.ortho(-view.ortho * W / H, view.ortho * W / H, -view.ortho, view.ortho, 0.1, 2000) : M4.persp((view.fov || 35) * D2R, W / H, 0.5, 3000);
    const Vm = M4.look(eye, tgt, up), VP = M4.mul(P, Vm);
    const sun = norm(view.sun || [-0.55, 0.62, 0.55]);
    const lc = [0, 0, 0], le = lc.map((v, i) => v + sun[i] * 120);
    const LV = M4.look(le, lc, Math.abs(sun[1]) > 0.95 ? [1, 0, 0] : [0, 1, 0]), LP = M4.ortho(-40, 40, -40, 40, 1, 260), L = M4.mul(LP, LV);
    // shadow pass
    gl.bindFramebuffer(gl.FRAMEBUFFER, this.fb); gl.viewport(0, 0, this.shSize, this.shSize);
    gl.clear(gl.DEPTH_BUFFER_BIT); gl.enable(gl.DEPTH_TEST); gl.disable(gl.CULL_FACE);
    gl.useProgram(this.shp.p); gl.uniformMatrix4fv(this.shp.U.uL, false, L);
    for (const m of this.meshes) { if (m.mat === "plume") continue; this.bind(m, false); gl.drawElements(gl.TRIANGLES, m.n, gl.UNSIGNED_INT, 0); }
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
    let clip = [0, 0, 0, 0], clipOn = 0;
    if (view.clip) { const [a, b, c, d] = view.clip; clip = [a, c, -b, d + a * this.xc]; clipOn = 1; }
    gl.uniform4fv(U.uClip, clip); gl.uniform1f(U.uClipOn, clipOn); gl.uniform1f(U.uExp, view.exposure || 1.0); gl.uniform1f(U.uHot, view.hot || 0);
    gl.uniform1f(U.uShZ, (this.cfg && this.cfg.shuttleLift) || 0); gl.uniform1f(U.uLen, this.geo.length_m);
    for (const m of this.meshes) {
      if (m.mat === "plume") continue;
      const mt = MATS[m.mat] || MATS.equipment;
      gl.uniform3fv(U.uC, mt.c); gl.uniform1f(U.uM, mt.m); gl.uniform1f(U.uR, mt.r); gl.uniform1f(U.uSeam, mt.seam || 0); gl.uniform1i(U.uKind, mt.kind || 0);
      gl.uniform3fv(U.uEm, (view.emissive && view.emissive[m.mat]) || mt.em || [0, 0, 0]); gl.uniform1f(U.uAlpha, 1); gl.uniform1f(U.uSec, mt.sec ?? 0.55);
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
