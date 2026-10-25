/* Pixel-sized governed satellite-path reference and renderer regression. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const { chromium } = require('playwright');
const { transform } = require('../web/solar-inspector/presentation.js');

const baseUrl = process.env.SOLAR_INSPECTOR_URL || 'http://127.0.0.1:8765';
const evidencePath = process.env.SOLAR_LOCAL_PATH_BROWSER_EVIDENCE || '/tmp/solar-local-path-browser.json';
const epoch = '2026-07-03T12:34:56Z';
const distance = (a,b) => Math.hypot(...a.map((value,i) => value-b[i]));
async function get(route, query) {
  const response = await fetch(baseUrl + route + '?' + new URLSearchParams(query));
  if (response.status !== 200) assert.fail(`HTTP ${response.status}: ${await response.text()}`);
  return response.json();
}

function assertSubmittedGeometry(actual, source) {
  assert.equal(actual.path.reference_center, source.reference_center);
  assert.equal(actual.path.reference_frame, source.reference_frame);
  assert.equal(actual.path.closed_by_renderer, false);
  assert.equal(actual.path.horizon.orbital_reference_center, 'MARS_SYSTEM_BARYCENTER');
  assert.equal(actual.path.segments.length, source.segments.length);
  for (const [i, segment] of actual.path.segments.entries()) {
    const expected = source.segments[i];
    assert.equal(segment.submitted, true, `segment ${i} must enter the Three.js scene`);
    assert.equal(segment.material_visible, true);
    assert.deepEqual(segment.source_indices, expected.indices);
    assert.deepEqual(segment.sources, expected.sources);
    assert.equal(segment.scene_vertices.length, expected.indices.length);
    for (const [j, index] of expected.indices.entries()) {
      assert.equal(actual.path.points[index].epoch_et, source.points[index].epoch_et);
      assert.deepEqual(actual.path.points[index].relative, source.points[index].relative);
      assert.deepEqual(segment.scene_vertices[j],
        transform(source.points[index].relative.position_km, 'PHYSICAL').map(Math.fround),
        `vertex ${j} must be the governed ${source.reference_center}-relative sample in AU/Y-up`);
    }
  }
  assert.deepEqual(actual.marker.source_position_km, source.points[0].relative.position_km);
  assert.deepEqual(actual.marker.scene_position, transform(actual.marker.source_position_km,'PHYSICAL'));
}

(async () => {
  const sunPath = await get('/api/trajectory', {body:'PHOBOS',start:epoch,center:'SUN',view:'auto'});
  const marsPath = await get('/api/trajectory', {body:'PHOBOS',start:epoch,center:'MARS',view:'auto'});
  assert.equal(sunPath.start_et, marsPath.start_et);
  assert.equal(sunPath.end_et, marsPath.end_et);
  assert.equal(sunPath.horizon.status, 'REVOLUTION_COMPLETE');
  assert.equal(marsPath.horizon.status, 'REVOLUTION_COMPLETE');
  const sunDisplacement = distance(sunPath.points[0].relative.position_km,
    sunPath.points.at(-1).relative.position_km);
  const marsDisplacement = distance(marsPath.points[0].relative.position_km,
    marsPath.points.at(-1).relative.position_km);
  const marsRadius = Math.hypot(...marsPath.points[0].relative.position_km);
  assert(sunDisplacement > marsRadius * 50, 'Sun-centered worldline must carry the moving Mars system');
  assert(marsDisplacement < marsRadius * .01, 'Mars-centered governed samples should return near T0 after one revolution');
  const browser = await chromium.launch({headless:true,
    args:['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
  const page = await browser.newPage({viewport:{width:412,height:915},deviceScaleFactor:3,
    isMobile:true,hasTouch:true});
  page.setDefaultTimeout(180000);
  const errors = [], failedResponses = [];
  page.on('pageerror', error => errors.push(error.message));
  page.on('response', response => {
    if (response.url().includes('/api/trajectory?') && !response.ok())
      failedResponses.push(`${response.status()} ${response.url()}`);
  });
  try {
    await page.goto(baseUrl + '/');
    await page.waitForFunction(() => window.__solarInspectorReconcile?.()?.complete);
    await page.click('#mobileControls');
    await page.fill('#epoch',epoch);
    await page.click('#load');
    await page.waitForFunction(et => {
      const report = window.__solarInspectorReconcile?.();
      return report?.complete && report.epochEt === et;
    },sunPath.start_et);
    await page.selectOption('#catalog','PHOBOS');
    await page.waitForFunction(() => window.__solarInspectorReconcile?.()?.paths.some(path =>
      path.body_id === 'PHOBOS' && path.requestState === 'READY'));
    await page.selectOption('#scope','all');
    await page.selectOption('#catalog','MARS');
    await page.click('#mobileControls');
    await page.click('#sceneFocus');
    for (let i = 0; i < 3; i++) await page.click('#zoomOut');
    await page.waitForFunction(() => window.__solarInspectorReconcile?.()?.paths.some(path =>
      path.body_id === 'PHOBOS' && path.submittedSegments === path.drawableSegments && path.submittedSegments > 0));
    const sunGeometry = await page.evaluate(() => window.__solarInspectorPathGeometry('PHOBOS'));
    const sunScene = await page.evaluate(() => window.__solarInspectorReconcile(true));
    await page.screenshot({path:'/tmp/solar-local-phobos-sun-centered.png'});
    assert.equal(sunScene.center,'SUN'); assert.equal(sunScene.scope,'all'); assert.equal(sunScene.mode,'PHYSICAL');
    assert.match(await page.locator('#horizons').textContent(),
      /Phobos: .*orbital reference MARS_SYSTEM_BARYCENTER · scene reference SUN/);
    assertSubmittedGeometry(sunGeometry,sunPath);
    const sunVisual = sunScene.paths.find(path => path.body_id === 'PHOBOS');
    assert.equal(sunVisual.lodEligible,true);
    assert.equal(sunVisual.submittedSegments,1);
    assert.equal(sunScene.objects.find(row => row.body_id === 'PHOBOS').markerInClip,true);
    assert(sunVisual.pixelContribution > 0, 'Sun-centered inertial worldline should be visible after framing Phobos');

    await page.click('#sceneSystem');
    await page.waitForFunction(et => {
      const report = window.__solarInspectorReconcile?.();
      return report?.complete && report.epochEt === et && report.center === 'MARS' &&
        document.querySelector('#stage').dataset.systemFit === 'complete' &&
        report.paths.some(path => path.body_id === 'PHOBOS' && path.requestState === 'READY' && path.submittedSegments > 0);
    },sunPath.start_et);
    const marsGeometry = await page.evaluate(() => window.__solarInspectorPathGeometry('PHOBOS'));
    const marsScene = await page.evaluate(() => window.__solarInspectorReconcile(true));
    await page.screenshot({path:'/tmp/solar-local-phobos-mars-centered.png'});
    assert.equal(marsScene.center,'MARS'); assert.equal(marsScene.scope,'local'); assert.equal(marsScene.mode,'PHYSICAL');
    assert.match(await page.locator('#horizons').textContent(),
      /Phobos: .*orbital reference MARS_SYSTEM_BARYCENTER · scene reference MARS/);
    assertSubmittedGeometry(marsGeometry,marsPath);
    const marsVisual = marsScene.paths.find(path => path.body_id === 'PHOBOS');
    assert.notEqual(marsVisual.requestKey,sunVisual.requestKey,
      'cache identity must include the selected scene center');
    assert.equal(marsVisual.submittedSegments,1);
    assert(marsVisual.pixelContribution > 0, 'governed Phobos path must contribute Mars-centered pixels');
    assert(marsVisual.screenBoundsPx.maxX - marsVisual.screenBoundsPx.minX > 10);
    assert(marsVisual.screenBoundsPx.maxY - marsVisual.screenBoundsPx.minY > 10);
    const marsMarker = marsScene.objects.find(row => row.body_id === 'MARS').markerScreenPx;
    assert(marsMarker[0] > marsVisual.screenBoundsPx.minX && marsMarker[0] < marsVisual.screenBoundsPx.maxX);
    assert(marsMarker[1] > marsVisual.screenBoundsPx.minY && marsMarker[1] < marsVisual.screenBoundsPx.maxY);
    assert.deepEqual(errors,[]); assert.deepEqual(failedResponses,[]);
    fs.writeFileSync(evidencePath,JSON.stringify({sunPath,marsPath,sunGeometry,marsGeometry,
      sunScene:{viewport:sunScene.viewport,camera:sunScene.camera,phobos:sunVisual,
        marsMarker:sunScene.objects.find(row => row.body_id === 'MARS'),
        phobosMarker:sunScene.objects.find(row => row.body_id === 'PHOBOS')},
      marsScene:{viewport:marsScene.viewport,camera:marsScene.camera,phobos:marsVisual,
        marsMarker:marsScene.objects.find(row => row.body_id === 'MARS'),
        phobosMarker:marsScene.objects.find(row => row.body_id === 'PHOBOS')},
      errors,failedResponses},null,2)+'\n');
    console.log(JSON.stringify({result:'PASS',sunCenter:sunVisual.visualState,
      sunDisplacementKm:sunDisplacement,marsDisplacementKm:marsDisplacement,
      sunCameraDistance:sunScene.camera.distance,marsCenter:marsVisual.visualState,
      marsCameraDistance:marsScene.camera.distance,marsPathBoundsPx:marsVisual.screenBoundsPx,
      marsPathPixels:marsVisual.pixelContribution,evidencePath},null,2));
  } finally { await browser.close(); }
})().catch(error => {console.error(error);process.exitCode=1;});
