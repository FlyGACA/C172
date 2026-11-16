// Browser smoke test for the Phase 7 viewer (real Chromium + WebGL via SwiftShader).
// Usage: npm run test:e2e   (E2E_SHOTS=dir to keep screenshots; PLAYWRIGHT_MODULE to use a preinstalled Playwright)
import http from 'node:http';
import { readFile, mkdir } from 'node:fs/promises';
import { extname, join, normalize } from 'node:path';
import { fileURLToPath } from 'node:url';
import assert from 'node:assert/strict';

const { chromium } = await import(process.env.PLAYWRIGHT_MODULE || 'playwright');
const ROOT = fileURLToPath(new URL('../../', import.meta.url));
const SHOTS = process.env.E2E_SHOTS;
const MIME = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.mjs': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.glb': 'model/gltf-binary', '.png': 'image/png', '.jpeg': 'image/jpeg' };

const server = http.createServer(async (req, res) => {
  const path = normalize(decodeURIComponent(new URL(req.url, 'http://x').pathname)).replace(/^([/\\])+/, '');
  if (path.includes('..')) { res.writeHead(400).end(); return; }
  try {
    const body = await readFile(join(ROOT, path));
    res.writeHead(200, { 'content-type': MIME[extname(path)] || 'application/octet-stream' }).end(body);
  } catch { res.writeHead(404).end('not found'); }
});
await new Promise((r) => server.listen(0, '127.0.0.1', r));
const base = `http://127.0.0.1:${server.address().port}/07_kinematic_twin/index.html`;

const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
const results = [];
async function check(name, fn) {
  try { await fn(); results.push(['ok', name]); console.log(`ok - ${name}`); }
  catch (e) { results.push(['FAIL', name]); console.log(`not ok - ${name}\n  ${e.message}`); }
}
async function shot(page, name, opts = {}) {
  if (!SHOTS) return;
  await mkdir(SHOTS, { recursive: true });
  await page.screenshot({ path: join(SHOTS, `${name}.png`), ...opts });
}

try {
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
  const errors = [];
  page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()); });
  page.on('pageerror', (e) => errors.push(e.message));
  await page.goto(`${base}?test=1&lang=en`);
  await page.waitForFunction(() => window.__twin?.ready, null, { timeout: 60000 });

  await check('model loads with all system groups and part nodes', async () => {
    const info = await page.evaluate(() => {
      const t = window.__twin;
      const groups = [...t.nodes.values()].filter((n) => n.userData?.kind === 'group').map((n) => n.name).sort();
      return { groups, n: t.nodes.size, hasPistons: [1, 2, 3, 4].every((c) => t.nodes.has(`ENGINE__piston_${c}`)) };
    });
    assert.deepEqual(info.groups, ['AIRFRAME', 'ELECTRICAL', 'ENGINE', 'FUEL', 'IGNITION', 'INDUCTION', 'OIL', 'PANEL', 'PITOT_STATIC', 'VACUUM']);
    assert.ok(info.n > 250, `nodes ${info.n}`);
    assert.ok(info.hasPistons);
  });

  await check('engine starts from the cockpit controls (POH 4-7 flow)', async () => {
    await page.click('#masterBat');
    await page.click('#masterAlt');
    for (let i = 0; i < 3; i++) await page.click('#primer');
    await page.$eval('#throttle', (el) => { el.value = '6'; el.dispatchEvent(new Event('input')); });
    const start = page.locator('#startBtn');
    await start.hover();
    await page.mouse.down();
    await page.waitForFunction(() => window.__twin.sim.engine.running, null, { timeout: 15000 });
    await page.mouse.up();
    await page.waitForTimeout(500);
    const s = await page.evaluate(() => ({ ign: window.__twin.sim.controls.ignition, running: window.__twin.sim.engine.running }));
    assert.equal(s.ign, 'BOTH', 'START springs back to BOTH');
    assert.equal(s.running, true);
  });

  await check('pistons follow the slider-crank motion between BDC and TDC', async () => {
    await page.click('#views button[data-view="engine"]');
    const xs = [];
    for (let i = 0; i < 12; i++) { xs.push(await page.evaluate(() => window.__twin.pistonX(1))); await page.waitForTimeout(120); }
    const mags = xs.map(Math.abs);
    assert.ok(Math.max(...mags) - Math.min(...mags) > 0.02, `piston 1 travel ${Math.max(...mags) - Math.min(...mags)}`);
    assert.ok(Math.min(...mags) >= 0.162 - 0.0492 - 1e-3 && Math.max(...mags) <= 0.162 + 0.0492 + 1e-3);
    assert.ok(xs.every((x) => x < 0), 'cylinder 1 is on the right bank (-X)');
    await page.waitForTimeout(900);
    await shot(page, 'engine_running');
  });

  await check('exploded view moves parts away from their assembled position', async () => {
    const before = await page.evaluate(() => window.__twin.partPos('IGNITION__dual_magneto'));
    await page.$eval('#explode', (el) => { el.value = '100'; el.dispatchEvent(new Event('input')); });
    // Software-rendered CI frames can exceed a fixed sleep; wait for the move itself.
    await page.waitForFunction((b) => {
      const p = window.__twin.partPos('IGNITION__dual_magneto');
      return Math.hypot(p[0] - b[0], p[1] - b[1], p[2] - b[2]) > 0.1;
    }, before, { timeout: 5000 });
    const after = await page.evaluate(() => window.__twin.partPos('IGNITION__dual_magneto'));
    assert.ok(Math.hypot(after[0] - before[0], after[1] - before[1], after[2] - before[2]) > 0.1);
    await shot(page, 'engine_exploded');
    await page.$eval('#explode', (el) => { el.value = '0'; el.dispatchEvent(new Event('input')); });
  });

  await check('clicking a part shows its POH-referenced description', async () => {
    await page.evaluate(() => window.__twin.selectPart('IGNITION__dual_magneto'));
    const txt = await page.textContent('#partInfo');
    assert.match(txt, /Dual magneto/);
    assert.match(txt, /POH 7-18/);
  });

  await check('instrument panel reflects the running engine', async () => {
    await page.$eval('#throttle', (el) => { el.value = '50'; el.dispatchEvent(new Event('input')); });
    await page.waitForTimeout(2500);
    const read = await page.textContent('.gauge[data-key="TACH"] .g-read');
    assert.ok(Number(read) > 1200, `tach ${read}`);
    await page.click('#views button[data-view="panel"]');
    await page.waitForTimeout(1200);
    await shot(page, 'panel_view');
  });

  await check('guided scenario renders steps and debrief flow', async () => {
    await page.selectOption('#scenarioSel', 'runup');
    await page.click('#scenarioStart');
    await page.waitForSelector('.steps li');
    const n = await page.locator('.steps li').count();
    assert.equal(n, 11);
    await shot(page, 'scenario_runup', { fullPage: true });
  });

  await check('Arabic is the default language and right-to-left', async () => {
    await page.click('#lang');
    const dir = await page.evaluate(() => document.documentElement.dir);
    assert.equal(dir, 'rtl');
    assert.match(await page.textContent('h1'), /سيسنا/);
    await shot(page, 'arabic_full', { fullPage: true });
  });

  await check('no console errors', async () => { assert.deepEqual(errors, []); });

  const mobile = await browser.newPage({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 1 });
  await mobile.goto(`${base}?test=1`);
  await mobile.waitForFunction(() => window.__twin?.ready, null, { timeout: 60000 });
  await check('phone width has no horizontal scroll', async () => {
    const { sw, cw } = await mobile.evaluate(() => ({ sw: document.documentElement.scrollWidth, cw: document.documentElement.clientWidth }));
    assert.ok(sw <= cw, `scrollWidth ${sw} > ${cw}`);
    await shot(mobile, 'mobile', { fullPage: false });
  });
} finally {
  await browser.close();
  server.close();
}

const failed = results.filter((r) => r[0] === 'FAIL').length;
console.log(`# ${results.length - failed} passed, ${failed} failed`);
process.exit(failed ? 1 : 0);
