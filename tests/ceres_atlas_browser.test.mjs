/** Optional real-browser acceptance. Missing tooling is SKIP, never PASS. */
import {test, before, after} from 'node:test';
import assert from 'node:assert/strict';
import {spawn, spawnSync} from 'node:child_process';
import {once} from 'node:events';
import {fileURLToPath} from 'node:url';
import {mkdtempSync, rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';

let chromium, browser, server, baseURL, mediaFixtureDirectory;
let gap = 'Playwright is not installed; real-browser verification unavailable.';
try {
  ({chromium} = await import('playwright'));
} catch (error) {
  if (error.code !== 'ERR_MODULE_NOT_FOUND') throw error;
}

before(async () => {
  if (!chromium) return;
  try {
    browser = await chromium.launch({headless: true});
  } catch (error) {
    if (!/Executable doesn't exist|not supported|missing dependencies/i.test(error.message)) throw error;
    gap = `Chromium unavailable: ${error.message.split('\n')[0]}`;
    return;
  }
  const cwd = fileURLToPath(new URL('../', import.meta.url));
  const python = process.env.PYTHON || 'python';
  mediaFixtureDirectory = mkdtempSync(join(tmpdir(), 'ceres-atlas-media-'));
  const mediaDB = join(mediaFixtureDirectory, 'media.sqlite3');
  const fixture = spawnSync(python, ['-B', 'tests/create_ceres_media_fixture.py', mediaDB], {cwd, encoding: 'utf8'});
  assert.equal(fixture.status, 0, fixture.stderr || 'MEDIA fixture creation failed');
  server = spawn(python, ['-B', 'tools/serve_ceres_atlas.py', '--port', '0', '--media-db', mediaDB], {
    cwd, stdio: ['ignore', 'pipe', 'pipe'],
  });
  baseURL = await new Promise((resolve, reject) => {
    let output = '';
    const timer = setTimeout(() => reject(new Error('Atlas launcher timed out')), 10000);
    server.once('error', error => { clearTimeout(timer); reject(error); });
    server.once('exit', code => { clearTimeout(timer); reject(new Error(`Atlas exited early: ${code}`)); });
    server.stdout.on('data', chunk => {
      output += chunk;
      const match = output.match(/http:\/\/127\.0\.0\.1:\d+\//);
      if (match) { clearTimeout(timer); resolve(match[0]); }
    });
  });
});

after(async () => {
  await browser?.close();
  if (server && server.exitCode === null) {
    const stopped = once(server, 'exit');
    server.kill('SIGTERM');
    await stopped;
  }
  if (mediaFixtureDirectory) rmSync(mediaFixtureDirectory, {recursive: true, force: true});
});

async function open(t, options = {}, hash = '', beforeNavigation = null) {
  if (!browser) { t.skip(gap); return null; }
  const context = await browser.newContext({viewport: {width: 393, height: 851}, ...options});
  t.after(() => context.close());
  const errors = [], external = [];
  await context.route('**/*', route => {
    if (!route.request().url().startsWith(baseURL)) {
      external.push(route.request().url()); return route.abort();
    }
    return route.continue();
  });
  const page = await context.newPage();
  page.on('pageerror', error => errors.push(error.message));
  t.after(() => {
    assert.deepEqual(errors, [], 'no browser script exceptions');
    assert.deepEqual(external, [], 'all application requests stay on loopback');
  });
  // Register failure fixtures before navigation: list thumbnails can otherwise
  // load the identical URL before a detail-only interception is installed.
  if (beforeNavigation) await beforeNavigation(page);
  await page.goto(baseURL + hash);
  await page.locator(hash.includes('collection=1') ? '#list-view' : '#detail-view').waitFor({state: 'visible'});
  return page;
}

test('body topology opens all five dossiers and multi-hop history preserves context', async t => {
  const page = await open(t, {viewport: {width: 1280, height: 900}});
  if (!page) return;
  assert.equal(await page.locator('#detail-title').textContent(), 'Ceres');
  assert.equal(await page.locator('.headline-kpi').count(), 6);
  assert.equal(await page.locator('.headline-kpi', {hasText: 'Biological residents'}).locator('strong').textContent(), '7.729M');
  assert.equal(await page.locator('.headline-kpi', {hasText: 'Annual value added'}).locator('strong').textContent(), '5.508T');
  await page.waitForFunction(() => document.querySelector('.hero-ceres img')?.naturalWidth === 1024);
  const hero = page.locator('.hero-ceres img');
  assert.equal(await hero.getAttribute('src'), 'assets/ceres-world-hero.png');
  assert.equal(await hero.evaluate(image => image.currentSrc), baseURL + 'assets/ceres-world-hero.png');
  assert.ok(await hero.isVisible());
  assert.ok(await page.locator('.hero-ceres .image-fallback').isHidden());
  assert.equal(await page.locator('.topology-node').count(), 5);
  for (let i = 1; i <= 5; i++) {
    const id = `CER-P0${i}`;
    await page.locator(`#topology-${id}`).click();
    assert.ok((await page.locator('#detail-view .eyebrow').textContent()).includes(id));
    if (id === 'CER-P01') assert.equal(await page.locator('.metric', {hasText: 'Resident population'}).locator('strong').textContent(), '24,914');
    await page.waitForFunction(() => document.querySelector('#detail-view .detail-media img')?.naturalWidth > 0);
    assert.ok((await page.locator('#detail-view .detail-media img').getAttribute('src')).includes(id));
    await page.goBack();
    await page.waitForFunction(() => document.querySelector('#detail-title')?.textContent === 'Ceres');
  }

  await page.getByRole('button', {name: 'Institutions'}).click();
  await page.locator('#topology-CER-P01').click();
  assert.equal(await page.locator('#detail-title').textContent(), 'Occator Industrial Lift & Surface Port');
  const institution = page.locator('.analysis .metric button.entity-link', {hasText: 'Ceres Commonwealth'}).first();
  assert.equal(await institution.evaluate(node => node.tagName), 'BUTTON');
  assert.equal(await institution.getAttribute('aria-label'), 'Open institution dossier: Ceres Commonwealth');
  const target = await institution.boundingBox();
  assert.ok(target.height >= 48, 'institution control has an accessible touch target');
  await institution.click();
  assert.equal(await page.locator('#detail-title').textContent(), 'Ceres Commonwealth');
  await page.getByRole('button', {name: 'Ceres Belt Exchange'}).click();
  assert.equal(await page.locator('#detail-title').textContent(), 'Ceres Belt Exchange');
  await page.goBack();
  assert.equal(await page.locator('#detail-title').textContent(), 'Ceres Commonwealth');
  await page.goBack();
  assert.equal(await page.locator('#detail-title').textContent(), 'Occator Industrial Lift & Surface Port');
  await page.goBack();
  assert.equal(await page.locator('#detail-title').textContent(), 'Ceres');
  assert.equal(await page.locator('.domain-nav button.selected').textContent(), 'Institutions');
});

test('filters, return scroll/focus, refresh and browser Back/Forward preserve state', async t => {
  const page = await open(t, {}, '#collection=1');
  if (!page) return;
  await page.locator('#search').fill('ceres');
  await page.locator('#type-filter').selectOption('ORBITAL_SHIPYARD');
  assert.equal(await page.locator('.facility-card').count(), 1);
  await page.locator('#open-CER-P04').click();
  await page.reload();
  await page.locator('#detail-title').waitFor({state: 'visible'});
  await page.locator('#back-to-list').click();
  await page.locator('#list-view').waitFor({state: 'visible'});
  assert.equal(await page.locator('#search').inputValue(), 'ceres');
  assert.equal(await page.locator('#type-filter').inputValue(), 'ORBITAL_SHIPYARD');
  await page.goForward();
  await page.locator('#detail-view').waitFor({state: 'visible'});
  await page.goBack();
  await page.locator('#list-view').waitFor({state: 'visible'});
  await page.locator('#clear-filters').click();
  await page.locator('#open-CER-P05').scrollIntoViewIfNeeded();
  const scroll = await page.evaluate(() => window.scrollY);
  assert.ok(scroll > 0);
  await page.locator('#open-CER-P05').click();
  await page.locator('#back-to-list').click();
  await page.waitForFunction(() => document.activeElement.id === 'open-CER-P05');
  assert.ok(Math.abs(await page.evaluate(() => window.scrollY) - scroll) < 3);
});

test('keyboard: Tab, Enter, Space and Escape support the same interaction', async t => {
  const page = await open(t, {}, '#collection=1');
  if (!page) return;
  await page.locator('#clear-filters').focus();
  await page.keyboard.press('Tab');
  assert.equal(await page.evaluate(() => document.activeElement.id), 'open-CER-P01');
  await page.keyboard.press('Enter');
  await page.waitForFunction(() => document.activeElement.id === 'detail-title');
  await page.keyboard.press('Escape');
  await page.waitForFunction(() => document.activeElement.id === 'open-CER-P01');
  await page.keyboard.press('Space');
  await page.locator('#detail-view').waitFor({state: 'visible'});
  await page.locator('#back-to-list').focus();
  await page.keyboard.press('Enter');
  await page.waitForFunction(() => document.activeElement.id === 'open-CER-P01');
});

test('touch and 320px/Pixel portrait/landscape layouts have no horizontal overflow', async t => {
  const page = await open(t, {hasTouch: true, isMobile: true}, '#collection=1');
  if (!page) return;
  for (const viewport of [{width: 320, height: 640}, {width: 393, height: 851}, {width: 851, height: 393}]) {
    await page.setViewportSize(viewport);
    assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth));
    const box = await page.locator('#clear-filters').boundingBox();
    assert.ok(box.height >= 48);
    await page.locator('#open-CER-P01').tap();
    await page.locator('#detail-view').waitFor({state: 'visible'});
    await page.locator('summary').tap();
    assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth));
    await page.locator('#back-to-list').tap();
    await page.locator('#list-view').waitFor({state: 'visible'});
  }
});

test('unknown deep link returns safely; empty search can be cleared', async t => {
  const page = await open(t, {}, '#q=ceres&facility=CER-P99');
  if (!page) return;
  assert.equal(await page.locator('#detail-title').textContent(), 'Facility not found');
  await page.locator('#back-to-list').click();
  assert.equal(await page.locator('#detail-title').textContent(), 'Ceres');
  await page.getByRole('button', {name: 'Browse facility collection'}).click();
  await page.locator('#list-view').waitFor({state: 'visible'});
  assert.equal(await page.locator('#search').inputValue(), 'ceres');
  await page.locator('#search').fill('no facility matches this');
  await page.locator('#empty').waitFor({state: 'visible'});
  await page.locator('#clear-filters').click();
  assert.equal(await page.locator('.facility-card').count(), 5);
});

test('missing image retains identity and supports retry without navigation loss', async t => {
  const page = await open(t, {}, '#collection=1', async page => {
    await page.route('**/images/CER-P01*', route => route.fulfill({status: 404, body: ''}));
  });
  if (!page) return;
  await page.locator('#open-CER-P01').click();
  await page.locator('#detail-view .image-fallback').waitFor({state: 'visible'});
  assert.equal(await page.locator('#detail-title').textContent(), 'Occator Industrial Lift & Surface Port');
  await page.unroute('**/images/CER-P01*');
  await page.getByRole('button', {name: 'Retry facility image'}).click();
  await page.waitForFunction(() => document.querySelector('#detail-view img')?.naturalWidth > 0);
  await page.locator('#back-to-list').click();
  await page.locator('#list-view').waitFor({state: 'visible'});
});

test('manifest failure has a usable retry and never renders unapproved records', async t => {
  const page = await open(t, {}, '#collection=1');
  if (!page) return;
  await page.route('**/manifest.json', route => route.fulfill({status: 503, body: ''}));
  await page.reload();
  await page.locator('#load-error').waitFor({state: 'visible'});
  assert.equal(await page.locator('.facility-card:visible').count(), 0);
  await page.unroute('**/manifest.json');
  await page.locator('#retry-load').click();
  await page.locator('#list-view').waitFor({state: 'visible'});
  assert.equal(await page.locator('.facility-card').count(), 5);
});
