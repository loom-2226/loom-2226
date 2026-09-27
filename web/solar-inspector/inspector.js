/* Thin presentation client. No ephemeris, source selection, or orbital model. */
(() => {
  'use strict';
  const $ = id => document.getElementById(id);
  const style = getComputedStyle(document.documentElement);
  const color = key => style.getPropertyValue('--loom-' + key).trim();
  const palette = { direct: color('domain-certainty-verified-color'), propagated: color('domain-certainty-provisional-color'),
    selected: color('domain-selection-highlight'), node: color('domain-nav-node-color'),
    sun: color('brand-color-secondary-sand'), background: color('interface-surface-canvas') };
  const stage = $('stage');
  let renderer;
  try { renderer = new THREE.WebGLRenderer({ antialias: true }); }
  catch (e) { $('message').textContent = 'WebGL unavailable: ' + e.message; return; }
  renderer.setPixelRatio(Math.min(devicePixelRatio || 1, 2));
  stage.prepend(renderer.domElement);
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(palette.background);
  const camera = new THREE.PerspectiveCamera(45, 1, 1e-9, 1e8);
  const objects = new THREE.Group(), paths = new THREE.Group();
  scene.add(objects, paths);
  let catalog = null, snapshot = null, trajectory = null, selected = null, busy = false, playing = false;
  let playGeneration = 0, loadGeneration = 0, selectionGeneration = 0, trajectoryVersion = 0, detailKey = '', pendingDetailKey = '';
  const orbitPaths = new Map();
  const orbitPathRequests = new Map();
  const orbitVisuals = new Map();
  const maxOrbitPaths = 256;
  let orbitLoading = false, orbitRefreshRequested = false;
  let initialSystemFit = null;
  let renderedLod = null;
  let distance = 80, theta = .55, phi = .65, target = new THREE.Vector3();
  let markers = [], labels = [], drag = null, moved = false;
  const pointers = new Map(); let pinch = null;
  const vector = p => new THREE.Vector3(...SolarPresentation.transform(p, $('mode').value));
  const disc = document.createElement('canvas'); disc.width = disc.height = 32;
  const ink = disc.getContext('2d'); ink.fillStyle = color('brand-color-neutral-white');
  ink.beginPath(); ink.arc(16, 16, 14, 0, Math.PI * 2); ink.fill();
  const markerTexture = new THREE.CanvasTexture(disc);
  const byId = id => catalog?.objects.find(row => row.body_id === id);
  const barycenters = () => catalog?.objects.filter(row => row.body_class === 'BARYCENTER') || [];
  function membersOf(root) {
    if (root === 'SUN') return ['SUN'];
    if (root === 'OTHER') return catalog.objects.filter(row => row.body_id !== 'SUN' &&
      !barycenters().some(group => membersOf(group.body_id).includes(row.body_id))).map(row => row.body_id);
    const members = new Set([root]);
    const prefix = root === 'EARTH_MOON_BARYCENTER' ? null : root.replace('_SYSTEM_BARYCENTER','');
    if (root === 'EARTH_MOON_BARYCENTER') { members.add('EARTH'); members.add('MOON'); }
    if (prefix && byId(prefix)) members.add(prefix);
    let changed = true;
    while (changed) {
      changed = false;
      for (const row of catalog.objects) if (row.parent_body_id && members.has(row.parent_body_id) && !members.has(row.body_id)) {
        members.add(row.body_id); changed = true;
      }
    }
    return [...members];
  }
  function systemFor(id) {
    if (id === 'SUN') return 'SUN';
    return barycenters().find(row => membersOf(row.body_id).includes(id))?.body_id || 'OTHER';
  }
  function localFamily(centerId) {
    const system = systemFor(centerId);
    return new Set(system === 'OTHER'
      ? [centerId,...catalog.objects.filter(row => row.parent_body_id === centerId).map(row => row.body_id)]
      : membersOf(system));
  }
  function enterScope(scope) {
    $('scope').value = scope;
    const enabled = scope === 'all' ? ['layerSun','layerPlanets','layerMoons','layerMinor','layerSpacecraft']
      : scope === 'local' ? ['layerPlanets','layerMoons','layerMinor','layerSpacecraft']
      : ['layerSun','layerPlanets'];
    for (const id of ['layerSun','layerPlanets','layerMoons','layerMinor','layerSpacecraft','layerBarycenters'])
      $(id).checked = enabled.includes(id);
  }
  function populateCenters(centerId = 'SUN') {
    const system = systemFor(centerId);
    $('system').value = system;
    const members = membersOf(system).map(byId).filter(Boolean);
    if (system === 'OTHER') {
      const groups = new Map();
      for (const row of members) {
        if (!groups.has(row.body_class)) groups.set(row.body_class,document.createElement('optgroup'));
        groups.get(row.body_class).label = row.body_class.replaceAll('_',' ').toLowerCase();
        groups.get(row.body_class).append(new Option(`${row.canonical_name} [${row.body_id}]`,row.body_id));
      }
      $('center').replaceChildren(...[...groups.values()]);
    } else $('center').replaceChildren(...members.map(row => new Option(`${row.canonical_name} [${row.body_id}]`,row.body_id)));
    $('center').value = centerId;
  }
  function populateSystems() {
    const options = [new Option('Solar','SUN'), ...barycenters().map(row => new Option(row.canonical_name,row.body_id)),
      new Option('Other catalog centers','OTHER')];
    $('system').replaceChildren(...options);
    populateCenters('SUN');
  }

  function clear(group) {
    for (const item of [...group.children]) {
      group.remove(item);
      if (!item.userData.cachedPathVisual) { item.geometry?.dispose(); item.material?.dispose(); }
    }
  }
  function disposeVisual(item) { item.geometry?.dispose(); item.material?.dispose(); }
  function clearTrajectoryVisuals() {
    for (const [key, visual] of orbitVisuals) if (key.startsWith('trajectory|') || key.startsWith('seam|')) {
      paths.remove(visual); disposeVisual(visual); orbitVisuals.delete(key);
    }
  }
  function rememberOrbitPath(key, path) {
    orbitPaths.set(key,path);
    while (orbitPaths.size > maxOrbitPaths) {
      const oldest = orbitPaths.keys().next().value;
      orbitPaths.delete(oldest);
      for (const [visualKey, visual] of orbitVisuals) if (visualKey.startsWith(oldest + '|')) {
        paths.remove(visual); disposeVisual(visual); orbitVisuals.delete(visualKey);
      }
    }
  }
  function updateCamera() {
    camera.near = Math.max(distance * 1e-6, 1e-12);
    camera.far = Math.max(distance * 10000, 1e7);
    camera.position.set(target.x + distance * Math.cos(phi) * Math.cos(theta),
      target.y + distance * Math.sin(phi), target.z + distance * Math.cos(phi) * Math.sin(theta));
    stage.dataset.cameraDistance = String(distance);
    stage.dataset.cameraTarget = [target.x,target.y,target.z].join(',');
    camera.lookAt(target); camera.updateProjectionMatrix();
    const lod = SolarPresentation.displayLod(distance, $('mode').value);
    if (snapshot && lod !== renderedLod) rebuild(false); else draw();
  }
  function draw() {
    for (const item of paths.children) if (item.isMesh) item.quaternion.copy(camera.quaternion);
    const lod = SolarPresentation.displayLod(distance, $('mode').value);
    let visibleMarkers = 0;
    for (const marker of markers) {
      marker.mesh.visible = marker.priority <= lod || marker.row.body_id === selected;
      if (marker.mesh.visible) visibleMarkers++;
    }
    stage.dataset.visibleMarkers = String(visibleMarkers);
    renderer.render(scene, camera);
    let shown = 0; const occupied = [];
    const budget = Math.max(8, Math.min(30, Math.floor(stage.clientWidth * stage.clientHeight / 25000)));
    for (const { element, position, id, priority } of labels) {
      const p = position.clone().project(camera);
      const visible = p.z >= -1 && p.z <= 1 && Math.abs(p.x) < 1 && Math.abs(p.y) < 1 &&
        (priority <= lod || id === selected) && (shown < budget || id === selected);
      element.hidden = !visible;
      if (visible) {
        const x = (p.x + 1) / 2 * stage.clientWidth + 8, y = (1 - p.y) / 2 * stage.clientHeight;
        const rect = { x, y, w: element.offsetWidth, h: element.offsetHeight };
        if (occupied.some(r => x < r.x+r.w && x+rect.w > r.x && y < r.y+r.h && y+rect.h > r.y)) {
          element.hidden = true; continue;
        }
        occupied.push(rect); shown++;
        element.style.left = x + 'px'; element.style.top = y + 'px';
      }
    }
  }
  function resize() {
    renderer.setSize(stage.clientWidth, stage.clientHeight, false);
    camera.aspect = stage.clientWidth / stage.clientHeight; updateCamera();
  }
  function visibleRows() {
    if (!snapshot) return [];
    const family = localFamily(snapshot.reference_center);
    return snapshot.objects.filter(r => {
      if (!r.relative) return false;
      if ($('scope').value === 'local' && !family.has(r.body_id) && r.body_id !== selected) return false;
      if (r.body_class === 'BARYCENTER') return $('layerBarycenters').checked;
      if (r.body_id === selected) return true;
      if (r.body_id === 'SUN') return $('layerSun').checked;
      if (r.body_class === 'PLANET') return $('layerPlanets').checked;
      if (r.body_class === 'NATURAL_SATELLITE') return $('layerMoons').checked;
      if (r.body_class === 'SPACECRAFT' || r.body_class === 'INTERSTELLAR_OBJECT') return $('layerSpacecraft').checked;
      return $('layerMinor').checked;
    });
  }
  function point(position, tint, size, group = objects) {
    const geometry = new THREE.BufferGeometry().setFromPoints([position]);
    const mesh = new THREE.Points(geometry, new THREE.PointsMaterial({ color: tint, size, sizeAttenuation: false,
      map: markerTexture, transparent: true, alphaTest: .1 }));
    group.add(mesh); return mesh;
  }
  function ring(position, radius, group = objects) {
    const mesh = new THREE.Mesh(new THREE.RingGeometry(radius, radius * 1.15, 32),
      new THREE.MeshBasicMaterial({ color: palette.selected, side: THREE.DoubleSide }));
    mesh.position.copy(position); mesh.quaternion.copy(camera.quaternion); group.add(mesh);
  }
  const solarPathClasses = new Set(['PLANET','NATURAL_SATELLITE','ASTEROID','NEAR_EARTH_ASTEROID','TROJAN_ASTEROID','BINARY_ASTEROID_PRIMARY','DWARF_PLANET','CENTAUR','TRANS_NEPTUNIAN_OBJECT','COMET','INTERSTELLAR_OBJECT','SPACECRAFT']);
  function pathLayer(row) {
    if (row.body_class === 'PLANET') return 'layerPlanets';
    if (row.body_class === 'NATURAL_SATELLITE') return 'layerMoons';
    if (row.body_class === 'SPACECRAFT' || row.body_class === 'INTERSTELLAR_OBJECT') return 'layerSpacecraft';
    return 'layerMinor';
  }
  function pathCandidates() {
    if (!snapshot) return [];
    return visibleRows().filter(r => r.body_id !== snapshot.reference_center && solarPathClasses.has(r.body_class) &&
      ($(pathLayer(r)).checked || (r.body_id === selected && $('layerSelected').checked)))
      .sort((a,b) => (b.body_id === selected ? 1 : 0) - (a.body_id === selected ? 1 : 0) ||
        (a.body_class === 'PLANET' ? -1 : b.body_class === 'PLANET' ? 1 : 0));
  }
  function pathKey(row) { return [row.body_id,snapshot.epoch_utc,snapshot.reference_center,'auto'].join('|'); }
  function loadPlanetOrbits() {
    orbitRefreshRequested = true;
    if (orbitLoading || playing) return;
    orbitLoading = true;
    (async () => {
      while (!playing) {
        orbitRefreshRequested = false;
        const candidates = pathCandidates();
        const next = candidates.find(row => !orbitPaths.has(pathKey(row)));
        if (!next) {
          if (orbitRefreshRequested) continue;
          break;
        }
        const key = pathKey(next), center = snapshot.reference_center;
        if (!orbitPathRequests.has(key)) {
          const request = get('/api/trajectory', { body: next.body_id, start: snapshot.epoch_utc, center, view: 'auto' })
            .catch(() => null).then(path => { rememberOrbitPath(key, path); orbitPathRequests.delete(key); return path; });
          orbitPathRequests.set(key, request);
        }
        await orbitPathRequests.get(key);
        if (!playing && pathCandidates().some(row => row.body_id === next.body_id && pathKey(row) === key)) {
          rebuild(false); advanceInitialSystemFit();
        }
        await new Promise(resolve => setTimeout(resolve, 0));
      }
    })().finally(() => {
      orbitLoading = false;
      if (orbitRefreshRequested && !playing) loadPlanetOrbits();
    });
  }
  function renderPlanetOrbits() {
    if (!snapshot) return;
    for (const row of pathCandidates()) {
      if (!SolarPresentation.showMinorPath(row, selected, snapshot.reference_center, distance, $('mode').value)) continue;
      const key=pathKey(row), path=orbitPaths.get(key); if (!path) continue;
      for (let i=0;i<path.segments.length;i++) {
        const segment=path.segments[i];
        if (segment.indices.length < 2) continue;
        const visualKey=[key,$('mode').value,i].join('|');
        let line=orbitVisuals.get(visualKey);
        if (!line) {
          const pts=segment.indices.map(j => path.points[j].relative && vector(path.points[j].relative.position_km)).filter(Boolean);
          if (pts.length < 2) continue;
          const options = { color: row.body_id === selected ? palette.selected : segment.authority_class === 'PROPAGATED' ? palette.propagated : palette.node,
            transparent: true, opacity: row.body_id === selected ? .85 : row.body_class === 'PLANET' ? .62 : .45,
            depthTest: false };
          const material = segment.authority_class === 'PROPAGATED'
            ? new THREE.LineDashedMaterial({ ...options, dashSize: Math.max(distance / 150, 1e-10), gapSize: Math.max(distance / 250, 1e-10) })
            : new THREE.LineBasicMaterial(options);
          line=new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts),material);
          if (segment.authority_class === 'PROPAGATED') line.computeLineDistances();
          line.userData.cachedPathVisual=true;
          orbitVisuals.set(visualKey,line);
        }
        line.material.color.set(row.body_id === selected ? palette.selected : segment.authority_class === 'PROPAGATED' ? palette.propagated : palette.node);
        line.material.opacity = row.body_id === selected ? .85 : row.body_class === 'PLANET' ? .62 : .45;
        paths.add(line);
      }
    }
  }
  function updateOrbitStatus() {
    const candidates = pathCandidates();
    if (!candidates.length) { $('orbitStatus').textContent = ''; $('horizons').replaceChildren(); return; }
    const ready = candidates.filter(row => orbitPaths.get(pathKey(row))).length;
    const failed = candidates.filter(row => orbitPaths.has(pathKey(row)) && !orbitPaths.get(pathKey(row))).length;
    const capped = candidates.filter(row => orbitPaths.get(pathKey(row))?.horizon.status === 'MAX_HORIZON_TRUNCATED').length;
    const gaps = candidates.filter(row => orbitPaths.get(pathKey(row))?.gap_indices.length).length;
    $('orbitStatus').textContent = `Resolver paths ${ready}/${candidates.length}` +
      (failed ? ` · ${failed} unavailable` : '') + (capped ? ` · ${capped} max-horizon truncated` : '') +
      (gaps ? ` · ${gaps} with gaps` : '');
    $('horizons').replaceChildren(...candidates.map(row => {
      const item = document.createElement('p'), path = orbitPaths.get(pathKey(row));
      const gaps = path?.gap_indices.map(index => path.points[index].epoch_utc) || [];
      const seams = path?.seams?.map(seam => seam.time_bracket_utc.join(' → ')) || [];
      item.textContent = `${row.canonical_name}: ${path ? `${path.horizon.start} → ${path.horizon.end} · ${path.horizon.status} · orbital reference ${path.horizon.orbital_reference_center} · ${gaps.length} gaps${gaps.length ? ` (${gaps.slice(0,3).join(', ')}${gaps.length > 3 ? ', …' : ''})` : ''} · ${seams.length} source seams${seams.length ? ` (${seams.join(', ')})` : ''}` : orbitPaths.has(pathKey(row)) ? 'unavailable' : 'loading'}`;
      return item;
    }));
  }
  function rebuild(fit = false) {
    if (!snapshot) return;
    renderedLod = SolarPresentation.displayLod(distance, $('mode').value);
    clear(objects); clear(paths); markers = []; labels = []; $('labels').replaceChildren();
    const rows = visibleRows();
    const center = snapshot.reference_center;
    const localMembers = center === 'SUN' ? new Set() : localFamily(center);
    for (const row of rows) {
      const position = vector(row.relative.position_km);
      const priority = SolarPresentation.labelRank(row, selected, localMembers, $('layerBarycenters').checked);
      const mesh = point(position, row.body_id === selected ? palette.selected : row.body_id === 'SUN' ? palette.sun : palette.node,
        row.body_id === 'SUN' ? 12 : row.body_id === selected ? 9 : 5);
      markers.push({ row, position, mesh, priority });
      const element = document.createElement('div');
      element.className = 'object-label' + (row.body_id === selected ? ' selected' : '');
      element.textContent = row.canonical_name;
      $('labels').append(element); labels.push({ element, position, id: row.body_id, priority });
    }
    labels.sort((a, b) => a.priority-b.priority || a.id.localeCompare(b.id));
    renderPlanetOrbits();
    updateOrbitStatus();
    if (trajectory && $('layerSelected').checked) {
      for (let i=0;i<trajectory.segments.length;i++) {
        const segment=trajectory.segments[i], propagated=segment.authority_class === 'PROPAGATED';
        const visualKey=['trajectory',trajectoryVersion,$('mode').value,i].join('|');
        let line=orbitVisuals.get(visualKey);
        if (!line) {
          const points=segment.indices.map(j => vector(trajectory.points[j].relative.position_km));
          if (points.length === 1) {
            line=point(points[0],propagated ? palette.propagated : palette.direct,4,paths);
            line.userData.cachedPathVisual=true; orbitVisuals.set(visualKey,line); continue;
          }
          if (points.length < 2) continue;
          const geometry=new THREE.BufferGeometry().setFromPoints(points);
          const material=propagated ? new THREE.LineDashedMaterial({ color: palette.propagated,
            dashSize: Math.max(distance / 150, 1e-10), gapSize: Math.max(distance / 250, 1e-10) }) :
            new THREE.LineBasicMaterial({ color: palette.direct });
          line=new THREE.Line(geometry,material); line.computeLineDistances(); line.userData.cachedPathVisual=true;
          orbitVisuals.set(visualKey,line);
        }
        paths.add(line);
      }
      for (let i=0;i<trajectory.seams.length;i++) {
        const seam=trajectory.seams[i];
        for (const [side,index] of [['before',seam.before_index],['after',seam.after_index]]) {
          const visualKey=['seam',trajectoryVersion,$('mode').value,i,side].join('|');
          let marker=orbitVisuals.get(visualKey);
          if (!marker) {
            marker=new THREE.Mesh(new THREE.RingGeometry(distance / 200, distance / 200 * 1.15, 32),
              new THREE.MeshBasicMaterial({ color: palette.selected, side: THREE.DoubleSide }));
            marker.position.copy(vector(trajectory.points[index].relative.position_km));
            marker.userData.cachedPathVisual=true; orbitVisuals.set(visualKey,marker);
          }
          marker.quaternion.copy(camera.quaternion); paths.add(marker);
        }
      }
    }
    const c = snapshot.counts;
    $('counts').textContent = `${snapshot.complete ? 'Catalog' : 'Preview'} ${c.catalog}/${snapshot.catalog_total} · Resolved ${c.resolved} = Direct ${c.direct} + Propagated ${c.propagated}\nUnresolved ${c.unresolved} · Catalog-only ${c.catalog_only} · Partial catalog ${c.partial_catalog}\nRenderable ${c.renderable} · Scene eligible ${rows.length} · Scope/layer-hidden ${c.renderable - rows.length}`;
    $('sceneStatus').textContent = `${snapshot.epoch_utc} | Center: ${snapshot.reference_center} | ${snapshot.reference_frame} | ` +
      ($('mode').value === 'SCHEMATIC' ? 'SCHEMATIC · NOT TO SCALE · VISUAL COMPRESSION' : 'PHYSICAL · positions to scale (1 scene unit = 1 AU)');
    if (fit) fitScene(); else draw();
  }
  function fitScene() {
    const points = markers.map(m => m.position);
    if (trajectory) for (const p of trajectory.points) if (p.relative) points.push(vector(p.relative.position_km));
    target.set(0, 0, 0);
    distance = Math.max(1e-8, ...points.map(p => p.length())) * 2.8;
    updateCamera();
  }
  function cancelInitialSystemFit() {
    if (initialSystemFit) { initialSystemFit = null; stage.dataset.systemFit = 'manual'; }
  }
  function frameLocalSystem() {
    const points = markers.map(marker => marker.position);
    for (const row of pathCandidates()) {
      const path = orbitPaths.get(pathKey(row));
      if (!path) continue;
      for (const point of path.points) if (point.relative) points.push(vector(point.relative.position_km));
    }
    const radius = Math.max(1e-8, ...points.map(point => point.length()));
    const halfVertical = THREE.MathUtils.degToRad(camera.fov / 2);
    const halfHorizontal = Math.atan(Math.tan(halfVertical) * camera.aspect);
    target.set(0,0,0);
    distance = radius / Math.sin(Math.min(halfVertical, halfHorizontal)) * 1.2;
    updateCamera();
  }
  function advanceInitialSystemFit() {
    if (!initialSystemFit || !snapshot || snapshot.reference_center !== initialSystemFit.center ||
        snapshot.epoch_utc !== initialSystemFit.epoch) return;
    frameLocalSystem();
    const present = new Set(snapshot.objects.map(row => row.body_id));
    const expected = [...localFamily(initialSystemFit.center)].filter(id => byId(id)?.body_class !== 'BARYCENTER');
    const ready = expected.every(id => present.has(id)) && pathCandidates().every(row => orbitPaths.has(pathKey(row)));
    if (ready) { initialSystemFit = null; stage.dataset.systemFit = 'complete'; }
  }
  function focusOverview() {
    const planets = markers.filter(marker => marker.row.body_class === 'PLANET')
      .sort((a,b) => a.position.length()-b.position.length());
    if (!planets.length) { fitScene(); return; }
    target.set(0,0,0);
    distance = Math.max(1e-8, planets[Math.min(4,planets.length-1)].position.length() * 3.2);
    updateCamera();
  }
  function focusSelected() {
    const marker = markers.find(item => item.row.body_id === selected);
    if (!marker) return;
    target.copy(marker.position);
    if (selected === snapshot.reference_center || selected === 'SUN') { focusSystem(); return; }
    const separations = markers.filter(item => item !== marker).map(item => item.position.distanceTo(marker.position)).filter(v => v > 0);
    const nearest = separations.length ? Math.min(...separations) : Infinity;
    distance = Math.max(1e-8, Math.min(nearest * 3, Math.max(.0001, marker.position.length() * .03)));
    updateCamera();
  }
  function frameSystem() {
    if (snapshot.reference_center === 'SUN') focusOverview();
    else frameLocalSystem();
  }
  function focusSystem() {
    if (!snapshot || !selected) { if (snapshot) frameSystem(); return; }
    if (busy) return;
    if (selected === snapshot.reference_center) {
      initialSystemFit = {center:selected,epoch:snapshot.epoch_utc};
      stage.dataset.systemFit = 'pending'; advanceInitialSystemFit(); return;
    }
    populateCenters(selected);
    enterScope(selected === 'SUN' ? 'planetary' : 'local');
    initialSystemFit = selected === 'SUN' ? null : {center:selected,epoch:$('epoch').value};
    stage.dataset.systemFit = initialSystemFit ? 'pending' : 'none';
    load(false,true);
  }
  function populateCatalog() {
    const term = $('search').value.toLowerCase(); $('catalog').replaceChildren();
    for (const row of catalog.objects) {
      if (!(row.body_id + row.canonical_name).toLowerCase().includes(term)) continue;
      const state = snapshot?.objects.find(item => item.body_id === row.body_id);
      const option = new Option(`${row.canonical_name} · ${state ? state.resolution === 'RESOLVED' ? state.authority_class : 'UNRESOLVED' : 'CATALOG'}`, row.body_id);
      $('catalog').add(option);
    }
    $('catalog').value = selected || '';
  }
  function clearSelection() {
    selectionGeneration++;
    detailKey = ''; pendingDetailKey = '';
    selected = null; trajectory = null; clearTrajectoryVisuals(); clear(paths);
    $('catalog').selectedIndex = -1; $('selection').textContent = 'No object selected.';
    $('detail').textContent = ''; $('pathStatus').textContent = ''; $('seams').replaceChildren(); $('sampleList').replaceChildren();
    rebuild(false);
  }
  async function select(id) {
    selected = id;
    const row = snapshot?.objects.find(r => r.body_id === id) || byId(id);
    if (!row) { clearSelection(); return; }
    $('catalog').value = id;
    const key = `${id}|${snapshot?.epoch_utc}|${snapshot?.reference_center}`;
    const hasDetail = detailKey === key, pendingDetail = pendingDetailKey === key;
    const generation = pendingDetail ? selectionGeneration : ++selectionGeneration;
    if (!hasDetail) {
      $('selection').textContent = `${row.canonical_name} · ${row.body_id} · ${row.body_class} · Parent ${row.parent_body_id ?? 'NULL'} · ${row.resolution || 'evaluating'}`;
      $('detail').textContent = 'Loading exact state and provenance…';
    }
    if (trajectory && trajectory.body_id !== id) clearPath();
    rebuild(false);
    if (!playing) loadPlanetOrbits();
    if (playing || !snapshot || hasDetail || pendingDetail) return;
    pendingDetailKey = key;
    const epoch = snapshot.epoch_utc, center = snapshot.reference_center;
    try {
      const detail = await get('/api/object', { body:id, epoch, center });
      if (generation !== selectionGeneration || selected !== id || snapshot.epoch_utc !== epoch || snapshot.reference_center !== center) {
        if (pendingDetailKey === key) pendingDetailKey = '';
        return;
      }
      $('selection').textContent = `${detail.canonical_name} · ${detail.body_id} · ${detail.body_class} · Parent ${detail.parent_body_id ?? 'NULL'} · ${detail.resolution}` +
        (detail.state ? ` · ${detail.authority_class} · Navigation-grade: ${detail.state.navigation_grade} · Uncertainty km: ${detail.state.provenance.uncertainty_km ?? 'NULL (not supplied)'}` : ` · ${detail.reason}`);
      $('detail').textContent = JSON.stringify(detail, null, 2);
      detailKey = key; pendingDetailKey = '';
      if (!snapshot.objects.some(item => item.body_id === id)) {
        const keys = ['body_id','canonical_name','body_class','parent_body_id','resolution','authority_class','relative','reason','presentation_reason'];
        const item = Object.fromEntries(keys.filter(field => field in detail).map(field => [field,detail[field]]));
        item.catalog_only = detail.catalog_only;
        item.partial_catalog = detail.partial_catalog;
        applySnapshot({...snapshot,objects:[...snapshot.objects,item]});
      }
    } catch (error) {
      if (pendingDetailKey === key) pendingDetailKey = '';
      if (generation === selectionGeneration) $('detail').textContent = 'Exact detail failed: ' + error.message;
    }
  }
  function setBusy(value) {
    busy = value;
    document.querySelectorAll('.toolbar input,.toolbar select,.toolbar button,#trace').forEach(el => { el.disabled = value; });
    $('play').disabled = false;
  }
  async function get(path, query) {
    const response = await fetch(path + '?' + new URLSearchParams(query));
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || response.statusText);
    return data;
  }
  let catalogPromise = null;
  async function ensureCatalog() {
    if (!catalogPromise) catalogPromise = get('/api/catalog', {epoch:$('epoch').value}).then(data => {
      catalog = data; populateSystems(); populateCatalog(); return data;
    }).catch(error => { catalogPromise = null; throw error; });
    return catalogPromise;
  }
  function sceneCounts(rows) {
    const resolved = rows.filter(row => row.resolution === 'RESOLVED').length;
    const direct = rows.filter(row => row.authority_class === 'DIRECT').length;
    return {catalog:rows.length,resolved,direct,propagated:resolved-direct,unresolved:rows.length-resolved,
      catalog_only:rows.filter(row => row.catalog_only).length,
      partial_catalog:rows.filter(row => row.partial_catalog).length,
      renderable:rows.filter(row => row.relative).length};
  }
  function applySnapshot(data, fit = false) {
    if (snapshot && snapshot.reference_center !== data.reference_center) clearPath();
    if (!data.complete && snapshot?.epoch_utc === data.epoch_utc && snapshot.reference_center === data.reference_center) {
      const byBody = new Map([...snapshot.objects,...data.objects].map(row => [row.body_id,row]));
      data = {...data,objects:catalog.objects.map(row => byBody.get(row.body_id)).filter(Boolean)};
      data.complete = data.objects.length === catalog.objects.length;
      data.counts = sceneCounts(data.objects);
    }
    snapshot = data;
    populateCenters(data.reference_center); populateCatalog(); $('failures').replaceChildren();
    for (const row of data.objects.filter(row => row.resolution === 'UNRESOLVED')) {
      const button = document.createElement('button'); button.textContent = row.canonical_name + ' [' + row.body_id + ']';
      button.onclick = () => select(row.body_id);
      const reason = document.createElement('p'); reason.textContent = row.reason;
      $('failures').append(button, reason);
    }
    if (!$('failures').children.length) $('failures').textContent = data.complete ? 'No unresolved objects at this epoch.' : 'Full catalog evaluation in progress.';
    rebuild(fit);
    advanceInitialSystemFit();
    if (selected) {
      const key = `${selected}|${data.epoch_utc}|${data.reference_center}`;
      if (detailKey !== key && pendingDetailKey !== key && !playing) select(selected);
    } else { $('catalog').selectedIndex = -1; $('selection').textContent = 'No object selected.'; }
    $('message').textContent = `${data.complete ? 'Exact resolver states evaluated' : 'Preview from exact resolver states'} at ${data.epoch_utc}. ` +
      `${data.complete ? 'Full catalog' : 'Full catalog loading'} · read-only ledger ${data.authority.ledger_sha256.slice(0,12)}.`;
    if (!playing) loadPlanetOrbits();
  }
  async function loadFull(generation, center, epoch) {
    try {
      const remaining = catalog.objects.filter(row => !snapshot.objects.some(item => item.body_id === row.body_id))
        .sort((a,b) => (a.source_asset_bytes ?? Infinity) - (b.source_asset_bytes ?? Infinity));
      for (let i=0;i<remaining.length;i+=12) {
        if (generation !== loadGeneration) return;
        const ids = remaining.slice(i,i+12).map(row => row.body_id);
        const data = await get('/api/state', { epoch, center, view:'scene', bodies:ids.join(',') });
        if (generation !== loadGeneration) return;
        applySnapshot(data);
        await new Promise(resolve => setTimeout(resolve,0));
      }
    } catch (error) {
      if (generation === loadGeneration) $('message').textContent = 'Full catalog failed; preview retained: ' + error.message;
    }
  }
  async function load(fit = false, preview = false) {
    if (busy) return;
    const generation = ++loadGeneration;
    setBusy(true); $('message').textContent = 'Evaluating governed states…';
    try {
      await ensureCatalog();
      const center = $('center').value;
      const epoch = $('epoch').value;
      const data = await get('/api/state', { epoch, center, view:'scene', ...(preview ? { preview:'1' } : {}) });
      if (generation !== loadGeneration) return;
      $('epoch').value = data.epoch_utc;
      applySnapshot(data,fit);
      if (preview && fit && center === 'SUN') focusOverview();
      if (preview) setTimeout(() => loadFull(generation,center,data.epoch_utc),150);
    } catch (e) { cancelInitialSystemFit(); stopPlay(); $('message').textContent = 'Evaluation failed; previous scene retained: ' + e.message; }
    finally { setBusy(false); }
  }
  function clearPath() {
    trajectory = null; clearTrajectoryVisuals(); clear(paths); $('seams').replaceChildren(); $('sampleList').replaceChildren();
    $('sampleDetail').textContent = ''; $('pathStatus').textContent = ''; rebuild(false);
  }
  async function trace() {
    if (busy || !snapshot || !selected) { $('pathStatus').textContent = 'Select an object first.'; return; }
    setBusy(true); $('pathStatus').textContent = 'Sampling governed resolver…';
    try {
      const result = await get('/api/trajectory', { body: selected, start: $('start').value, end: $('end').value,
        center: snapshot.reference_center, samples: $('samples').value });
      clearTrajectoryVisuals(); trajectory = result; trajectoryVersion++;
      $('pathStatus').textContent = `${trajectory.body_id} · ${trajectory.start} → ${trajectory.end} · ${trajectory.points.length} samples · ${trajectory.segments.length} segments · ${trajectory.seams.length} seams · ${trajectory.gap_indices.length} unavailable samples`;
      $('seams').replaceChildren();
      for (const seam of trajectory.seams) {
        const details = document.createElement('details'), summary = document.createElement('summary'), pre = document.createElement('pre');
        summary.textContent = 'SOURCE SEAM ' + seam.time_bracket_utc.join(' → ');
        pre.textContent = JSON.stringify({ ...seam, before: trajectory.points[seam.before_index], after: trajectory.points[seam.after_index] }, null, 2);
        details.append(summary, pre); $('seams').append(details);
      }
      $('sampleList').replaceChildren(...trajectory.points.map((p, i) => new Option(`${p.epoch_utc} · ${p.authority_class || p.resolution}`, i)));
      $('sampleList').onchange = () => { $('sampleDetail').textContent = JSON.stringify(trajectory.points[$('sampleList').value], null, 2); };
      $('sampleList').onchange(); rebuild(true);
    } catch (e) { $('pathStatus').textContent = 'Trajectory failed: ' + e.message; }
    finally { setBusy(false); }
  }
  function stopPlay() { playing = false; playGeneration++; $('play').textContent = 'Play'; $('play').setAttribute('aria-pressed', 'false'); loadPlanetOrbits(); if (selected) select(selected); }
  async function step(direction) {
    if (busy) return;
    const delta = Number($('step').value) * 86400000 * direction;
    const date = new Date(Date.parse($('epoch').value) + delta);
    if (!Number.isFinite(date.getTime()) || !Number.isFinite(delta) || !delta) { $('message').textContent = 'Enter a valid epoch and nonzero step.'; stopPlay(); return; }
    $('epoch').value = date.toISOString(); await load();
  }
  $('play').onclick = async () => {
    if (playing) { stopPlay(); return; }
    playing = true; $('play').textContent = 'Pause'; $('play').setAttribute('aria-pressed', 'true');
    const generation = ++playGeneration;
    const tick = async () => { if (!playing || generation !== playGeneration) return; await step(1); if (playing && generation === playGeneration) setTimeout(tick, 700); };
    tick();
  };
  $('load').onclick = () => load(false,true); $('back').onclick = () => step(-1); $('forward').onclick = () => step(1);
  document.querySelectorAll('[data-year]').forEach(b => { b.onclick = () => { $('epoch').value = b.dataset.year + '-01-01T00:00:00Z'; load(false,true); }; });
  $('system').onchange = () => {
    const system = $('system').value;
    const center = system === 'OTHER' ? membersOf('OTHER')[0] : system;
    cancelInitialSystemFit(); populateCenters(center); selected = center;
    enterScope(center === 'SUN' ? 'planetary' : 'local'); load(true,true);
  };
  $('center').onchange = () => { cancelInitialSystemFit(); selected = $('center').value;
    enterScope(selected === 'SUN' ? 'planetary' : 'local'); load(true,true); };
  $('mode').onchange = () => { rebuild(true); advanceInitialSystemFit(); };
  $('scope').onchange = () => { cancelInitialSystemFit(); enterScope($('scope').value); rebuild(true); loadPlanetOrbits(); };
  $('fit').onclick = () => { cancelInitialSystemFit(); fitScene(); };
  for (const id of ['layerSun','layerPlanets','layerMoons','layerMinor','layerSpacecraft','layerBarycenters','layerSelected']) $(id).onchange = () => { rebuild(false); loadPlanetOrbits(); advanceInitialSystemFit(); };
  $('focusSelected').onclick = $('sceneFocus').onclick = $('catalogFocus').onclick = () => { cancelInitialSystemFit(); focusSelected(); };
  $('focusSystem').onclick = $('sceneSystem').onclick = focusSystem;
  $('zoomIn').onclick = () => { cancelInitialSystemFit(); distance = Math.max(1e-10,distance*.6); updateCamera(); };
  $('zoomOut').onclick = () => { cancelInitialSystemFit(); distance = Math.min(1e8,distance/ .6); updateCamera(); };
  $('catalog').onchange = () => select($('catalog').value); $('search').oninput = populateCatalog;
  $('clearSelection').onclick = clearSelection;
  $('mobileControls').onclick = () => {
    const open = $('controls').classList.toggle('mobile-open');
    $('mobileControls').textContent = open ? 'Close' : 'Controls';
    $('mobileControls').setAttribute('aria-expanded', String(open));
  };
  $('toggleControls').onclick = () => {
    const collapsed = $('controls').classList.toggle('collapsed');
    $('toggleControls').textContent = collapsed ? 'Show' : 'Hide';
    $('toggleControls').setAttribute('aria-expanded', String(!collapsed));
    setTimeout(resize, 0);
  };
  $('trace').onclick = trace; $('clearPath').onclick = clearPath;
  const canvas = renderer.domElement;
  canvas.oncontextmenu = e => e.preventDefault();
  function pointerPair() {
    const values = [...pointers.values()];
    if (values.length < 2) return null;
    const [a, b] = values;
    return { distance: Math.hypot(a.x-b.x, a.y-b.y), x: (a.x+b.x)/2, y: (a.y+b.y)/2 };
  }
  canvas.onpointerdown = e => {
    cancelInitialSystemFit();
    pointers.set(e.pointerId, { x: e.clientX, y: e.clientY });
    canvas.setPointerCapture(e.pointerId); moved = false;
    if (pointers.size === 1) drag = { x: e.clientX, y: e.clientY, pan: e.shiftKey || e.button === 2 };
    else { drag = null; pinch = pointerPair(); }
  };
  canvas.onpointermove = e => {
    if (!pointers.has(e.pointerId)) return;
    const previous = pointers.get(e.pointerId);
    pointers.set(e.pointerId, { x: e.clientX, y: e.clientY });
    if (pointers.size >= 2) {
      const next = pointerPair();
      if (pinch && next && pinch.distance > 0 && next.distance > 0) {
        moved = true;
        distance = Math.max(1e-10, Math.min(1e8, distance * Math.pow(pinch.distance / next.distance,.45)));
        const dx = next.x - pinch.x, dy = next.y - pinch.y;
        const right = new THREE.Vector3().setFromMatrixColumn(camera.matrix, 0);
        const up = new THREE.Vector3().setFromMatrixColumn(camera.matrix, 1);
        target.addScaledVector(right, -dx * distance / stage.clientHeight * .2).addScaledVector(up, dy * distance / stage.clientHeight * .2);
        pinch = next; updateCamera();
      }
      return;
    }
    if (!drag) drag = { x: previous.x, y: previous.y, pan: e.shiftKey || e.button === 2 };
    const dx = e.clientX - drag.x, dy = e.clientY - drag.y;
    if (Math.abs(dx) + Math.abs(dy) > 2) moved = true;
    if (drag.pan) {
      const right = new THREE.Vector3().setFromMatrixColumn(camera.matrix, 0);
      const up = new THREE.Vector3().setFromMatrixColumn(camera.matrix, 1);
      target.addScaledVector(right, -dx * distance / stage.clientHeight * .2).addScaledVector(up, dy * distance / stage.clientHeight * .2);
    } else { theta -= dx * .003; phi = Math.max(-1.5, Math.min(1.5, phi + dy * .003)); }
    drag.x = e.clientX; drag.y = e.clientY; updateCamera();
  };
  function releasePointer(e) {
    pointers.delete(e.pointerId); pinch = pointerPair(); drag = null;
    if (pointers.size === 1) {
      const only = [...pointers.values()][0];
      drag = { x: only.x, y: only.y, pan: false };
    }
  }
  canvas.onpointerup = releasePointer; canvas.onpointercancel = releasePointer;
  canvas.addEventListener('wheel', e => { e.preventDefault(); cancelInitialSystemFit(); distance = Math.max(1e-10, Math.min(1e8, distance * Math.exp(e.deltaY * .0004))); updateCamera(); }, { passive: false });
  canvas.onclick = e => {
    if (moved) return;
    const bounds = canvas.getBoundingClientRect(); let best = null, nearest = 14;
    for (const marker of markers) {
      if (!marker.mesh.visible) continue;
      const p = marker.position.clone().project(camera);
      if (Math.abs(p.z) > 1) continue;
      const d = Math.hypot((p.x + 1) / 2 * bounds.width - (e.clientX - bounds.left), (1 - p.y) / 2 * bounds.height - (e.clientY - bounds.top));
      if (d < nearest) { nearest = d; best = marker.row.body_id; }
    }
    if (best) select(best);
  };
  new ResizeObserver(resize).observe(stage);
  resize(); load(true,true);
})();
