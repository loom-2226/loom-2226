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
  // Display policy only. Distances are scene units (AU in PHYSICAL mode).
  // The resolver and the catalog remain independent of these camera bands.
  function displayLod(distance, mode) {
    const schematic = mode === 'SCHEMATIC';
    return distance > (schematic ? 8 : 3) ? 1 : distance > (schematic ? 3 : .4) ? 3 : 4;
  }
  function labelRank(row, selectedId, localFamily, barycentersEnabled = false) {
    if (row.body_id === selectedId) return 0;
    if (row.body_class === 'BARYCENTER' && barycentersEnabled) return 1;
    if (row.body_id === 'SUN' || row.body_class === 'PLANET') return 1;
    if (row.body_class === 'NATURAL_SATELLITE') return localFamily.has(row.body_id) ? 2 : 4;
    if (row.body_class === 'SPACECRAFT' || row.body_class === 'DWARF_PLANET') return 3;
    return 4;
  }
  function showMinorPath(row, selectedId, centerId, distance, mode) {
    if (row.body_id === selectedId || row.body_class === 'PLANET') return true;
    if (row.body_class === 'NATURAL_SATELLITE' && centerId !== 'SUN') return true;
    return displayLod(distance, mode) === 4;
  }
  const api = { transform, AU_KM, displayLod, labelRank, showMinorPath };
  if (typeof module !== 'undefined') module.exports = api;
  else root.SolarPresentation = api;
})(globalThis);
