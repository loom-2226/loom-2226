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
  const errors = [], external = [], snapshots = [];
  page.on('pageerror', e => errors.push(e.message));
  page.on('request', r => { if (!r.url().startsWith('http://127.0.0.1:8765/')) external.push(r.url()); });
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
    await page.setViewportSize({ width: 390, height: 844 });
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true);
    console.log(JSON.stringify({ result: 'PASS', exactStateSnapshots: snapshots.length, pageErrors: errors, externalRequests: external,
      exercised: ['2026/2226/2250', 'arbitrary UTC', 'Earth/Moon', 'Jupiter', 'Pluto', 'Ida/Dactyl', 'physical/schematic immutability', 'rotate/pan/zoom', 'canvas and catalog selection', 'step/play/pause', 'New Horizons seam', 'open interstellar path', '390px layout'] }, null, 2));
  } finally { await browser.close(); }
})().catch(e => { console.error(e); process.exit(1); });
