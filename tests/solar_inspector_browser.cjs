/* Run against the loopback inspector with an installed Playwright + Chromium. */
const assert = require('node:assert/strict');
const { chromium } = require('playwright');
const { transform } = require('../web/solar-inspector/presentation.js');

(async () => {
  const p = Object.freeze([149597870.7, 2, 3]);
  const physical = transform(p, 'PHYSICAL'), schematic = transform(p, 'SCHEMATIC');
  assert.deepEqual(p, [149597870.7, 2, 3]); assert.notDeepEqual(physical, schematic);
  assert.equal(physical[0], 1); assert.deepEqual(transform([0, 0, 0], 'SCHEMATIC'), [0, 0, -0]);
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox', '--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const page = await browser.newPage({ viewport: { width: 1500, height: 1000 } });
  page.setDefaultTimeout(180000);
  const errors = [], external = [], snapshots = [], trajectoryRequests = [];
  let pathRequestsDuringPlay = null;
  page.on('pageerror', e => errors.push(e.message));
  page.on('request', r => { if (!r.url().startsWith('http://127.0.0.1:8765/')) external.push(r.url()); });
  page.on('request', r => { if (r.url().includes('/api/trajectory?')) trajectoryRequests.push(new URL(r.url()).searchParams); });
  page.on('response', async r => { if (r.url().includes('/api/state?') && r.ok()) snapshots.push(await r.json()); });
  async function settled() { await page.waitForFunction(() => document.querySelector('#message').textContent.startsWith('Exact resolver'), { timeout: 180000 }); await page.waitForFunction(() => !document.querySelector('#load').disabled); }
  async function year(y) { await page.click(`[data-year="${y}"]`); await settled(); assert.match(await page.locator('#sceneStatus').innerText(), new RegExp(y)); }
  async function center(id) { await page.selectOption('#center', id); await settled(); assert.match(await page.locator('#sceneStatus').innerText(), new RegExp('Center: ' + id)); }
  try {
    await page.goto('http://127.0.0.1:8765/'); await settled();
    await page.selectOption('#catalog', 'EARTH');
    const exact = await page.locator('#detail').textContent();
    assert.equal(JSON.parse(exact).state.provenance.units, 'km,km/s');
    await page.selectOption('#mode', 'SCHEMATIC');
    assert.match(await page.locator('#sceneStatus').innerText(), /SCHEMATIC · NOT TO SCALE · VISUAL COMPRESSION/);
    assert.equal(await page.locator('#detail').textContent(), exact);
    await page.screenshot({ path: '/tmp/solar-inspector-schematic.png' });
    await page.selectOption('#mode', 'PHYSICAL');
    await center('EARTH'); await page.selectOption('#catalog', 'MOON');
    await page.screenshot({ path: '/tmp/solar-inspector-earth-moon.png' });
    const box = await page.locator('canvas').boundingBox();
    await page.mouse.click(box.x + box.width / 2, box.y + box.height / 2);
    assert.match(await page.locator('#selection').innerText(), /EARTH/);
    await page.selectOption('#catalog', 'MOON');
    let before = await page.locator('canvas').screenshot();
    await page.mouse.move(box.x + 200, box.y + 200); await page.mouse.down(); await page.mouse.move(box.x + 300, box.y + 260, { steps: 8 }); await page.mouse.up();
    assert.notDeepEqual(await page.locator('canvas').screenshot(), before);
    before = await page.locator('canvas').screenshot();
    await page.keyboard.down('Shift'); await page.mouse.down(); await page.mouse.move(box.x + 390, box.y + 240, { steps: 8 }); await page.mouse.up(); await page.keyboard.up('Shift');
    assert.notDeepEqual(await page.locator('canvas').screenshot(), before);
    before = await page.locator('canvas').screenshot(); await page.mouse.wheel(0, -400); await page.waitForTimeout(100);
    assert.notDeepEqual(await page.locator('canvas').screenshot(), before);
    await center('JUPITER'); await center('PLUTO'); await center('IDA');
    await page.selectOption('#catalog', 'DACTYL'); assert.match(await page.locator('#detail').textContent(), /UNRESOLVED/);
    await center('SUN'); await year('2226'); await year('2250');
    assert.match(await page.locator('#failures').innerText(), /Proteus/);
    await year('2026');
    await page.fill('#epoch', '2026-07-03T12:34:56Z'); await page.click('#load'); await settled();
    assert.match(await page.locator('#sceneStatus').innerText(), /2026-07-03T12:34:56Z/);
    await page.click('#forward'); await settled(); assert.match(await page.locator('#epoch').inputValue(), /2026-07-04/);
    await page.click('#back'); await settled(); assert.match(await page.locator('#epoch').inputValue(), /2026-07-03/);
    await page.click('#play'); await page.waitForFunction(() => document.querySelector('#epoch').value.startsWith('2026-07-04')); await page.click('#play'); await settled();
    async function traceBody(body, centerId, start, end) {
      if ((await page.locator('#center').inputValue()) !== centerId) await center(centerId);
      await page.selectOption('#catalog', body);
      await page.fill('#start', start); await page.fill('#end', end); await page.fill('#samples', '24');
      const beforePath = await page.locator('canvas').screenshot();
      await page.click('#trace');
      await page.waitForFunction(() => /[1-9]\d* segments/.test(document.querySelector('#pathStatus').textContent), { timeout: 120000 });
      assert.match(await page.locator('#pathStatus').innerText(), new RegExp('^' + body + ' ·'));
      assert(trajectoryRequests.some(q => q.get('body') === body && q.get('center') === centerId), `${body} resolver path request missing`);
      assert.notDeepEqual(await page.locator('canvas').screenshot(), beforePath, `${body} path must change the rendered canvas`);
    }
    await traceBody('EARTH', 'SUN', '2026-01-01T00:00:00Z', '2027-01-01T00:00:00Z');
    await traceBody('MOON', 'EARTH', '2026-01-01T00:00:00Z', '2026-02-01T00:00:00Z');
    await traceBody('CERES', 'SUN', '2026-01-01T00:00:00Z', '2027-01-01T00:00:00Z');
    await traceBody('COMET_67P', 'SUN', '2026-01-01T00:00:00Z', '2027-01-01T00:00:00Z');
    const wholeCatalog = snapshots.at(-1).objects.filter(r => r.relative &&
      !['STAR','BARYCENTER','SPACECRAFT'].includes(r.body_class)).map(r => r.body_id);
    await page.selectOption('#scope', 'all');
    await page.waitForFunction(() => {
      const match = document.querySelector('#orbitStatus').textContent.match(/Resolver paths (\d+)\/(\d+)/);
      return match && match[1] === match[2];
    }, null, { timeout: 600000 });
    assert.match(await page.locator('#orbitStatus').innerText(), new RegExp(`^Resolver paths ${wholeCatalog.length}/${wholeCatalog.length}$`));
    for (const body of wholeCatalog) {
      assert(trajectoryRequests.some(q => q.get('body') === body && q.get('center') === 'SUN'),
        `Whole Catalog must request ${body} through the governed resolver`);
    }
    await center('SUN');
    await page.selectOption('#catalog', 'COMET_67P');
    await page.waitForTimeout(250);
    const pathsBeforePlay = trajectoryRequests.length;
    const playStarted = Date.now();
    await page.click('#play');
    await page.waitForFunction(() => Date.parse(document.querySelector('#epoch').value) >= Date.parse('2026-07-05T00:00:00Z'));
    const playAdvanceMs = Date.now() - playStarted;
    await page.click('#play'); await settled();
    assert.equal(trajectoryRequests.length, pathsBeforePlay, 'Play must reuse cached paths and never resample them');
    pathRequestsDuringPlay = trajectoryRequests.length - pathsBeforePlay;
    await page.selectOption('#catalog', 'NEWHORIZONS');
    await page.fill('#start', '2026-01-01T00:00:00Z'); await page.fill('#end', '2250-01-01T00:00:00Z'); await page.fill('#samples', '32');
    await page.click('#trace'); await page.waitForFunction(() => document.querySelector('#pathStatus').textContent.includes('segments'), { timeout: 120000 });
    assert.match(await page.locator('#seams').innerText(), /SOURCE SEAM/);
    await page.screenshot({ path: '/tmp/solar-inspector-new-horizons.png' });
    await page.selectOption('#catalog', 'OUMUAMUA'); await page.click('#trace');
    await page.waitForFunction(() => document.querySelector('#pathStatus').textContent.includes('OUMUAMUA') && document.querySelector('#pathStatus').textContent.includes('segments'), { timeout: 120000 });
    for (const s of snapshots) {
      assert.equal(s.counts.catalog, s.objects.length);
      assert.equal(s.counts.catalog, s.counts.resolved + s.counts.unresolved);
      assert.equal(s.counts.resolved, s.counts.direct + s.counts.propagated);
      assert.equal(s.counts.renderable, s.objects.filter(r => r.relative).length);
    }
    assert.deepEqual(errors, []); assert.deepEqual(external, []);
    const mobile = await browser.newPage({ viewport: { width: 412, height: 915 }, deviceScaleFactor: 3, isMobile: true, hasTouch: true });
    const mobileErrors = [];
    mobile.on('pageerror', e => mobileErrors.push(e.message));
    const initialStart = Date.now();
    await mobile.goto('http://127.0.0.1:8765/');
    await mobile.waitForFunction(() => document.querySelector('#message').textContent.startsWith('Exact resolver'), { timeout: 180000 });
    const initialLoadMs = Date.now() - initialStart;
    assert.equal(await mobile.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true);
    await mobile.click('#mobileControls');
    assert.equal(await mobile.locator('#controls').evaluate(el => getComputedStyle(el).display), 'block');
    assert.equal(await mobile.locator('canvas').evaluate(el => el.width > 0 && el.height > 0), true);
    assert.deepEqual(mobileErrors, []);
    await mobile.close();
    assert.deepEqual(errors, []); assert.deepEqual(external, []);
    console.log(JSON.stringify({ result: 'PASS', exactStateSnapshots: snapshots.length, pageErrors: errors, externalRequests: external,
      performance: { pixelInitialLoadMs: initialLoadMs, playAdvanceMs },
      verifiedResolverPaths: ['EARTH@SUN', 'MOON@EARTH', 'CERES@SUN', 'COMET_67P@SUN'], wholeCatalogPaths: wholeCatalog.length,
      pathRequestsDuringPlay,
      exercised: ['2026/2226/2250', 'arbitrary UTC', 'Earth/Moon', 'Jupiter', 'Pluto', 'Ida/Dactyl', 'physical/schematic immutability', 'rotate/pan/zoom', 'canvas and catalog selection', 'step/play/pause', 'New Horizons seam', 'open interstellar path', '412px mobile layout'] }, null, 2));
  } finally { await browser.close(); }
})().catch(e => { console.error(e); process.exit(1); });
