/* Geometry only: never mutate resolver states or infer an orbit. Also tested in Node. */
(function (root) {
  'use strict';
  const AU_KM = 149597870.7;
  function transform(positionKm, mode) {
    const p = positionKm.map(v => v / AU_KM);
    const r = Math.hypot(...p);
    const scale = mode === 'SCHEMATIC' && r ? Math.log1p(r * 100) / r : 1;
    // Rotate canonical ecliptic XYZ into the viewer's Y-up coordinates.
    return [p[0] * scale, p[2] * scale, -p[1] * scale];
  }
  const api = { transform, AU_KM };
  if (typeof module !== 'undefined') module.exports = api;
  else root.SolarPresentation = api;
})(globalThis);
