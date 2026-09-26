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
  let snapshot = null, trajectory = null, selected = null, busy = false, playing = false, playGeneration = 0, trajectoryVersion = 0;
  const orbitPaths = new Map();
  const orbitPathRequests = new Map();
  const orbitVisuals = new Map();
  const maxOrbitPaths = 256;
  let orbitLoading = false, orbitRefreshRequested = false;
  let distance = 80, theta = .55, phi = .65, target = new THREE.Vector3();
  let markers = [], labels = [], drag = null, moved = false;
  const pointers = new Map(); let pinch = null;
  const vector = p => new THREE.Vector3(...SolarPresentation.transform(p, $('mode').value));
  const disc = document.createElement('canvas'); disc.width = disc.height = 32;
  const ink = disc.getContext('2d'); ink.fillStyle = color('brand-color-neutral-white');
  ink.beginPath(); ink.arc(16, 16, 14, 0, Math.PI * 2); ink.fill();
  const markerTexture = new THREE.CanvasTexture(disc);

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
    camera.lookAt(target); camera.updateProjectionMatrix(); draw();
  }
  function draw() {
    for (const item of paths.children) if (item.isMesh) item.quaternion.copy(camera.quaternion);
    renderer.render(scene, camera);
    let shown = 0; const occupied = [];
    for (const { element, position, id } of labels) {
      const p = position.clone().project(camera);
      const visible = p.z >= -1 && p.z <= 1 && Math.abs(p.x) < 1 && Math.abs(p.y) < 1 && (shown < 30 || id === selected);
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
    const center = snapshot.objects.find(r => r.body_id === snapshot.reference_center);
    const parent = snapshot.objects.find(r => r.body_id === center.parent_body_id);
    const system = parent?.body_class === 'BARYCENTER' ? parent.body_id : center.body_id;
    return snapshot.objects.filter(r => {
      if (!r.relative) return false;
      const scope = $('scope').value;
      if (scope === 'all') return true;
      if (scope === 'planetary') return r.body_id === 'SUN' || r.body_class === 'PLANET' ||
        r.body_class === 'NATURAL_SATELLITE' || r.body_id === selected ||
        (r.parent_body_id && snapshot.objects.some(p => p.body_id === r.parent_body_id && p.body_class === 'PLANET'));
      return [center.body_id, system, selected].includes(r.body_id) || [center.body_id, system].includes(r.parent_body_id);
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
  const orbitDays = { MERCURY: 88, VENUS: 225, EARTH: 366, MARS: 687, JUPITER: 4333, SATURN: 10759, URANUS: 30687, NEPTUNE: 60190 };
  const solarPathClasses = new Set(['PLANET','NATURAL_SATELLITE','ASTEROID','NEAR_EARTH_ASTEROID','TROJAN_ASTEROID','BINARY_ASTEROID_PRIMARY','DWARF_PLANET','CENTAUR','TRANS_NEPTUNIAN_OBJECT','COMET','INTERSTELLAR_OBJECT']);
  function pathCandidates() {
    if (!snapshot || snapshot.reference_center !== 'SUN' || !['planetary','all'].includes($('scope').value)) return [];
    const scope = $('scope').value;
    return visibleRows().filter(r => solarPathClasses.has(r.body_class) &&
      (scope === 'all' || r.body_class === 'PLANET' || r.body_class === 'NATURAL_SATELLITE' || r.body_id === selected))
      .sort((a,b) => (b.body_id === selected ? 1 : 0) - (a.body_id === selected ? 1 : 0) ||
        (orbitDays[b.body_id] ? 1 : 0) - (orbitDays[a.body_id] ? 1 : 0));
  }
  function pathWindow(row) {
    // Presentation path only: every point still comes from the governed resolver.
    // Fixed calendar windows keep Play on cached paths; no browser orbit model is involved.
    const epoch = new Date(snapshot.epoch_utc), year = epoch.getUTCFullYear();
    const satellite = row.body_class === 'NATURAL_SATELLITE';
    const anchor = satellite ? Date.UTC(year,epoch.getUTCMonth(),17) : Date.UTC(year,6,1);
    const halfDays = satellite ? 16 : orbitDays[row.body_id] ? orbitDays[row.body_id] / 2 : 365.25 * 20;
    return [new Date(anchor-halfDays*86400000).toISOString(), new Date(anchor+halfDays*86400000).toISOString()];
  }
  function loadPlanetOrbits() {
    orbitRefreshRequested = true;
    if (orbitLoading || playing) return;
    orbitLoading = true;
    (async () => {
      while (!playing) {
        orbitRefreshRequested = false;
        const candidates = pathCandidates();
        const next = candidates.find(row => {
          const [start,end] = pathWindow(row);
          const key = [row.body_id,start,end,'SUN'].join('|');
          return !orbitPaths.has(key);
        });
        if (!next) {
          if (orbitRefreshRequested) continue;
          break;
        }
        const [start,end] = pathWindow(next);
        const key = [next.body_id,start,end,'SUN'].join('|');
        if (!orbitPathRequests.has(key)) {
          const request = get('/api/trajectory', { body: next.body_id, start, end, center: 'SUN', samples: orbitDays[next.body_id] || next.body_class === 'NATURAL_SATELLITE' ? 48 : 28 })
            .catch(() => null).then(path => { rememberOrbitPath(key, path); orbitPathRequests.delete(key); return path; });
          orbitPathRequests.set(key, request);
        }
        await orbitPathRequests.get(key);
        if (!playing && pathCandidates().some(row => row.body_id === next.body_id &&
          [row.body_id,...pathWindow(row),'SUN'].join('|') === key)) rebuild(false);
        await new Promise(resolve => setTimeout(resolve, 0));
      }
    })().finally(() => {
      orbitLoading = false;
      if (orbitRefreshRequested && !playing) loadPlanetOrbits();
    });
  }
  function renderPlanetOrbits() {
    if (!snapshot || snapshot.reference_center !== 'SUN' || !['planetary','all'].includes($('scope').value)) return;
    for (const row of pathCandidates()) {
      const key=[row.body_id,...pathWindow(row),'SUN'].join('|'), path=orbitPaths.get(key); if (!path) continue;
      for (let i=0;i<path.segments.length;i++) {
        const segment=path.segments[i];
        if (segment.indices.length < 2) continue;
        const visualKey=[key,$('mode').value,i].join('|');
        let line=orbitVisuals.get(visualKey);
        if (!line) {
          const pts=segment.indices.map(j => path.points[j].relative && vector(path.points[j].relative.position_km)).filter(Boolean);
          if (pts.length < 2) continue;
          const material = new THREE.LineBasicMaterial({ color: palette.node, transparent: true,
            opacity: orbitDays[row.body_id] ? .62 : .5, depthTest: false });
          line=new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts),material);
          line.userData.cachedPathVisual=true;
          orbitVisuals.set(visualKey,line);
        }
        paths.add(line);
      }
    }
  }
  function updateOrbitStatus() {
    const candidates = pathCandidates();
    if (!candidates.length) { $('orbitStatus').textContent = ''; return; }
    const attempted = candidates.filter(row => orbitPaths.has([row.body_id,...pathWindow(row),'SUN'].join('|'))).length;
    $('orbitStatus').textContent = `Resolver paths ${attempted}/${candidates.length}`;
  }
  function rebuild(fit = false) {
    if (!snapshot) return;
    clear(objects); clear(paths); markers = []; labels = []; $('labels').replaceChildren();
    const rows = visibleRows();
    for (const row of rows) {
      const position = vector(row.relative.position_km);
      point(position, row.body_id === selected ? palette.selected : row.body_id === 'SUN' ? palette.sun : palette.node,
        row.body_id === 'SUN' ? 12 : row.body_id === selected ? 9 : 5);
      markers.push({ row, position });
      const element = document.createElement('div');
      element.className = 'object-label' + (row.body_id === selected ? ' selected' : '');
      element.textContent = row.canonical_name;
      $('labels').append(element); labels.push({ element, position, id: row.body_id,
        priority: row.body_id === selected ? 0 : row.body_id === 'SUN' ? 1 : row.body_class === 'PLANET' ? 2 : 3 });
    }
    labels.sort((a, b) => a.priority-b.priority);
    renderPlanetOrbits();
    updateOrbitStatus();
    if (trajectory) {
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
    $('counts').textContent = `Catalog ${c.catalog} · Resolved ${c.resolved} = Direct ${c.direct} + Propagated ${c.propagated}\nUnresolved ${c.unresolved} · Catalog-only ${c.catalog_only} · Partial catalog ${c.partial_catalog}\nRenderable ${c.renderable} · Rendered ${rows.length} · Scope-hidden ${c.renderable - rows.length}`;
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
  function populateCatalog() {
    const term = $('search').value.toLowerCase(); $('catalog').replaceChildren();
    for (const row of snapshot.objects) {
      if (!(row.body_id + row.canonical_name).toLowerCase().includes(term)) continue;
      const option = new Option(`${row.canonical_name} · ${row.resolution === 'RESOLVED' ? row.authority_class : 'UNRESOLVED'}`, row.body_id);
      $('catalog').add(option);
    }
    $('catalog').value = selected || '';
  }
  function clearSelection() {
    selected = null; trajectory = null; clearTrajectoryVisuals(); clear(paths);
    $('catalog').selectedIndex = -1; $('selection').textContent = 'No object selected.';
    $('detail').textContent = ''; $('pathStatus').textContent = ''; $('seams').replaceChildren(); $('sampleList').replaceChildren();
    rebuild(false);
  }
  function select(id) {
    selected = id;
    const row = snapshot.objects.find(r => r.body_id === id);
    if (!row) { clearSelection(); return; }
    $('catalog').value = id;
    $('selection').textContent = `${row.canonical_name} · ${row.body_id} · ${row.body_class} · Parent ${row.parent_body_id ?? 'NULL'} · ${row.resolution}` +
      (row.state ? ` · ${row.authority_class} · Navigation-grade: ${row.state.navigation_grade} · Uncertainty km: ${row.state.provenance.uncertainty_km ?? 'NULL (not supplied)'}` : ` · ${row.reason}`);
    $('detail').textContent = JSON.stringify(row, null, 2);
    if (trajectory && trajectory.body_id !== id) clearPath();
    rebuild($('scope').value === 'local');
    if (!playing) loadPlanetOrbits();
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
  async function load(fit = false) {
    if (busy) return;
    setBusy(true); $('message').textContent = 'Evaluating governed states…';
    try {
      const center = $('center').value;
      const data = await get('/api/state', { epoch: $('epoch').value, center });
      if (snapshot && snapshot.reference_center !== data.reference_center) clearPath();
      snapshot = data; $('epoch').value = data.epoch_utc;
      $('center').replaceChildren(...data.objects.map(r => new Option(r.canonical_name + ' [' + r.body_id + ']', r.body_id)));
      $('center').value = data.reference_center;
      populateCatalog(); $('failures').replaceChildren();
      for (const row of data.objects.filter(r => r.resolution === 'UNRESOLVED')) {
        const button = document.createElement('button'); button.textContent = row.canonical_name + ' [' + row.body_id + ']';
        button.onclick = () => select(row.body_id);
        const reason = document.createElement('p'); reason.textContent = row.reason;
        $('failures').append(button, reason);
      }
      if (!$('failures').children.length) $('failures').textContent = 'No unresolved objects at this epoch.';
      if (selected) select(selected); else { $('catalog').selectedIndex = -1; $('selection').textContent = 'No object selected.'; rebuild(fit); }
      $('message').textContent = `Exact resolver states evaluated at ${data.epoch_utc}. Read-only PostgreSQL snapshot ${data.authority.ledger_sha256.slice(0, 12)}. Restart to reload authority.`;
      if (!playing) loadPlanetOrbits();
    } catch (e) { stopPlay(); $('message').textContent = 'Evaluation failed; previous scene retained: ' + e.message; }
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
  function stopPlay() { playing = false; playGeneration++; $('play').textContent = 'Play'; $('play').setAttribute('aria-pressed', 'false'); loadPlanetOrbits(); }
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
  $('load').onclick = () => load(); $('back').onclick = () => step(-1); $('forward').onclick = () => step(1);
  document.querySelectorAll('[data-year]').forEach(b => { b.onclick = () => { $('epoch').value = b.dataset.year + '-01-01T00:00:00Z'; load(); }; });
  $('center').onchange = () => { selected = $('center').value; $('scope').value = selected === 'SUN' ? 'planetary' : 'local'; load(true); };
  $('mode').onchange = () => rebuild(true); $('scope').onchange = () => { rebuild(true); loadPlanetOrbits(); }; $('fit').onclick = fitScene;
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
        distance = Math.max(1e-10, Math.min(1e8, distance * pinch.distance / next.distance));
        const dx = next.x - pinch.x, dy = next.y - pinch.y;
        const right = new THREE.Vector3().setFromMatrixColumn(camera.matrix, 0);
        const up = new THREE.Vector3().setFromMatrixColumn(camera.matrix, 1);
        target.addScaledVector(right, -dx * distance / stage.clientHeight).addScaledVector(up, dy * distance / stage.clientHeight);
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
      target.addScaledVector(right, -dx * distance / stage.clientHeight).addScaledVector(up, dy * distance / stage.clientHeight);
    } else { theta -= dx * .006; phi = Math.max(-1.5, Math.min(1.5, phi + dy * .006)); }
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
  canvas.addEventListener('wheel', e => { e.preventDefault(); distance = Math.max(1e-10, Math.min(1e8, distance * Math.exp(e.deltaY * .001))); updateCamera(); }, { passive: false });
  canvas.onclick = e => {
    if (moved) return;
    const bounds = canvas.getBoundingClientRect(); let best = null, nearest = 14;
    for (const marker of markers) {
      const p = marker.position.clone().project(camera);
      if (Math.abs(p.z) > 1) continue;
      const d = Math.hypot((p.x + 1) / 2 * bounds.width - (e.clientX - bounds.left), (1 - p.y) / 2 * bounds.height - (e.clientY - bounds.top));
      if (d < nearest) { nearest = d; best = marker.row.body_id; }
    }
    if (best) select(best);
  };
  new ResizeObserver(resize).observe(stage);
  resize(); load(true);
})();
