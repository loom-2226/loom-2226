/* Whole Catalog authority-to-pixel reconciliation on the historical Pixel viewport. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const { chromium } = require('playwright');

const baseUrl = process.env.SOLAR_INSPECTOR_URL || 'http://127.0.0.1:8765';
const evidencePath = process.env.SOLAR_Q8_EVIDENCE || '/tmp/solar-inspector-q8-evidence.json';

(async () => {
  const browser = await chromium.launch({ headless: true,
    args: ['--no-sandbox', '--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const page = await browser.newPage({ viewport: { width: 412, height: 915 }, deviceScaleFactor: 3,
    isMobile: true, hasTouch: true });
  page.setDefaultTimeout(900000);
  const errors = [], failedResponses = [], requests = [];
  page.on('pageerror', error => errors.push(error.message));
  page.on('crash', () => errors.push('page crashed'));
  page.on('request', request => {
    if (request.url().includes('/api/trajectory?') && request.url().includes('view=auto')) {
      const query = new URL(request.url()).searchParams;
      requests.push({ body: query.get('body'), start: query.get('start'), center: query.get('center') });
    }
  });
  page.on('response', response => {
    if (response.url().includes('/api/trajectory?') && response.url().includes('view=auto') && !response.ok())
      failedResponses.push(`${response.status()} ${response.url()}`);
  });
  try {
    await page.goto(baseUrl + '/');
    await page.waitForFunction(() => window.__solarInspectorReconcile?.()?.complete);
    await page.click('#mobileControls');
    await page.fill('#epoch', '2026-07-03T12:34:56Z');
    await page.click('#load');
    await page.waitForFunction(() => {
      const report = window.__solarInspectorReconcile?.();
      return report?.complete && report.objects.length === 110 && report.epochEt > 836000000;
    });
    await page.selectOption('#scope','all');
    await page.waitForFunction(() => {
      const report = window.__solarInspectorReconcile?.();
      return report?.complete && report.paths.length === 98 &&
        report.paths.every(path => path.requestState === 'READY' || path.requestState === 'FAILED') &&
        report.paths.every(path => !path.lodEligible || path.requestState === 'FAILED' ||
          path.submittedSegments === path.drawableSegments);
    });
    await page.click('#mobileControls');
    await page.click('#sceneSystem');
    const before = await page.evaluate(() => window.__solarInspectorReconcile(true));
    await page.screenshot({ path: '/tmp/solar-inspector-q8-pixel-before-fit.png' });
    await page.click('#mobileControls');
    await page.click('#fit');
    await page.click('#mobileControls');
    const after = await page.evaluate(() => window.__solarInspectorReconcile(true));
    await page.screenshot({ path: '/tmp/solar-inspector-q8-pixel-after-fit.png' });
    const epochRequests = requests.filter(request => request.start === String(after.epochEt) && request.center === 'SUN');
    assert.equal(before.viewport.width, 412);
    assert.equal(before.viewport.height, 915);
    assert.equal(before.objects.length, 110);
    assert.equal(before.paths.length, 98);
    assert.equal(after.paths.length, 98);
    assert.equal(new Set(epochRequests.map(request => request.body)).size, 98,
      'each Whole Catalog candidate must issue one governed automatic request');
    assert.deepEqual(before.paths.map(path => path.body_id).sort(), epochRequests.map(request => request.body).sort());
    for (const report of [before, after]) {
      assert.equal(report.complete, true);
      assert(report.objects.every(row => row.visualState && (row.relative || row.reason)));
      assert(report.objects.filter(row => row.sceneEligible).every(row => row.markerSubmitted));
      assert(report.paths.every(path => path.requestState === 'READY' && path.drawableSegments > 0));
      assert(report.paths.every(path => path.lodEligible ?
        path.submittedSegments === path.drawableSegments : path.submittedSegments === 0));
      assert(report.paths.every(path => path.visualState && path.materialVisible));
      assert(report.paths.filter(path => path.projectedSegments).every(path =>
        path.isolatedPixelContribution > 0 && path.screenBoundsPx),
      'every projected governed path must rasterize when isolated');
      assert(report.objects.filter(row => row.markerLodVisible && row.markerInClip).every(row =>
        row.isolatedPixelContribution > 0),
      'every projected marker must rasterize when isolated');
      assert(report.paths.filter(path => path.horizonStatus === 'MAX_HORIZON_TRUNCATED')
        .every(path => path.visualState !== 'REQUEST_FAILED'));
    }
    assert(before.objects.some(row => row.sceneEligible && row.markerLodVisible && !row.markerInClip),
      'overview must reproduce clipped outer objects');
    assert(after.objects.filter(row => row.sceneEligible).every(row => row.markerInClip),
      'Fit Scene must frame every eligible governed position at Pixel width');
    assert.equal(after.objects.filter(row => row.visualState === 'AUTHORITY_UNRESOLVED').length, 2);
    assert.equal(after.paths.filter(path => path.horizonStatus === 'MAX_HORIZON_TRUNCATED').length, 15);
    const noHorizontalOverflow = await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth);
    assert.equal(noHorizontalOverflow, true);
    fs.writeFileSync(evidencePath, JSON.stringify({ before, after, browser: {
      automaticRequests: requests, wholeCatalogRequests: epochRequests, failedResponses, errors,
      noHorizontalOverflow
    } }, null, 2) + '\n');
    const summarize = report => ({ camera: report.camera, objects: {
      total: report.objects.length, resolved: report.objects.filter(row => row.resolution === 'RESOLVED').length,
      eligible: report.objects.filter(row => row.sceneEligible).length,
      lodVisible: report.objects.filter(row => row.markerLodVisible).length,
      inClip: report.objects.filter(row => row.markerLodVisible && row.markerInClip).length
    }, paths: { total: report.paths.length,
      ready: report.paths.filter(path => path.requestState === 'READY').length,
      failed: report.paths.filter(path => path.requestState === 'FAILED').map(path => path.body_id),
      noGeometry: report.paths.filter(path => !path.drawableSegments).map(path => path.body_id),
      submitted: report.paths.filter(path => path.submittedSegments).length,
      inClip: report.paths.filter(path => path.projectedSegments).length,
      pixels: report.paths.filter(path => path.pixelContribution > 0).length,
      truncated: report.paths.filter(path => path.horizonStatus === 'MAX_HORIZON_TRUNCATED').map(path => path.body_id) } });
    console.log(JSON.stringify({ before: summarize(before), after: summarize(after),
      errors, failedResponses, requestCount: requests.length, evidencePath }, null, 2));
    assert.deepEqual(errors, []);
    assert.deepEqual(failedResponses, []);
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
