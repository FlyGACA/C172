// Browser test for the Phase 8 viewer (real Chromium + WebGL via SwiftShader).
// Usage: npm run test:e2e:p8   (E2E_SHOTS=dir keeps screenshots; PLAYWRIGHT_MODULE for a preinstalled Playwright)
import http from 'node:http';
import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { extname, join, normalize } from 'node:path';
import { fileURLToPath } from 'node:url';
import assert from 'node:assert/strict';

const pw = await import(process.env.PLAYWRIGHT_MODULE || 'playwright');
const { chromium, devices } = pw.default ?? pw;
const ROOT = fileURLToPath(new URL('../../', import.meta.url));
const SHOTS = process.env.E2E_SHOTS;
const MIME = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.mjs': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.glb': 'model/gltf-binary', '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.hdr': 'application/octet-stream', '.wasm': 'application/wasm' };

const server = http.createServer(async (req, res) => {
  const path = normalize(decodeURIComponent(new URL(req.url, 'http://x').pathname)).replace(/^([/\\])+/, '');
  if (path.includes('..')) { res.writeHead(400).end(); return; }
  try { const body = await readFile(join(ROOT, path)); res.writeHead(200, { 'content-type': MIME[extname(path)] || 'application/octet-stream' }).end(body); }
  catch { res.writeHead(404).end('not found'); }
});
await new Promise((r) => server.listen(0, '127.0.0.1', r));
const base = `http://127.0.0.1:${server.address().port}/08_realistic_digital_twin/index.html`;
const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const results = [];
const perf = {};
async function check(name, fn) {
  try { await fn(); results.push(['ok', name]); console.log(`ok - ${name}`); }
  catch (e) { results.push(['FAIL', name]); console.log(`not ok - ${name}\n  ${e.stack || e.message}`); }
}
async function shot(page, name) { if (!SHOTS) return; await mkdir(SHOTS, { recursive: true }); await page.screenshot({ path: join(SHOTS, `${name}.png`), timeout: 180000, animations: 'disabled' }); }
const settle = (page, ms = 1200) => page.waitForTimeout(ms);

async function open(page, query) {
  const errors = [];
  page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()); });
  page.on('pageerror', (e) => errors.push(e.message));
  const t0 = Date.now();
  await page.goto(`${base}?test=1&${query}`);
  await page.waitForFunction(() => window.__twin?.ready, null, { timeout: 180000 });
  return { errors, loadMs: Date.now() - t0 };
}

try {
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  const { errors, loadMs } = await open(page, 'lang=en&q=high');
  perf.high_load_ms = loadMs;
  await settle(page, 2500);

  await check('high LOD loads with every system group and no console errors', async () => {
    const info = await page.evaluate(() => { const r = window.__twin.rig; return { groups: [...r.groups.keys()].sort(), parts: r.parts.size, stats: window.__twin.stats() }; });
    assert.deepEqual(errors, [], 'console errors');
    assert.deepEqual(info.groups, ['AIRFRAME', 'EMPENNAGE', 'ENGINE', 'GEAR', 'INTERIOR', 'PANEL', 'POWERPLANT', 'SYSTEMS', 'WING_L', 'WING_R']);
    assert.ok(info.parts > 300, `parts ${info.parts}`);
    assert.ok(info.stats.triangles > 100000, `triangles ${info.stats.triangles}`);
    perf.high = info.stats;
    assert.deepEqual(errors, []);
  });
  await shot(page, 'p8_exterior');

  await check('exterior: doors open, flaps 40, control surfaces follow the inputs', async () => {
    await page.click('#doors');
    await page.click('#flapsel button[data-v="40"]');
    await page.$eval('#aileron', (el) => { el.value = '1'; el.dispatchEvent(new Event('input')); });
    await settle(page, 800);
    const q = await page.evaluate(() => {
      const r = window.__twin.rig; const d = r.part('AIRFRAME.door_L'); const f = r.part('WING_L.flap'); const a = r.part('WING_L.aileron');
      return { door: d.quaternion.toArray(), flap: f.quaternion.toArray(), ail: a.quaternion.toArray(), base: r.base.get(d).q.toArray() };
    });
    assert.ok(q.door.some((v, i) => Math.abs(v - q.base[i]) > 0.05), 'door rotated');
    assert.notDeepEqual(q.flap.map((v) => v.toFixed(3)), [0, 0, 0, 1].map((v) => v.toFixed(3)));
    await shot(page, 'p8_doors_flaps');
    await page.click('#doors'); await page.$eval('#aileron', (el) => { el.value = '0'; el.dispatchEvent(new Event('input')); }); await page.click('#flapsel button[data-v="0"]');
  });

  await check('parts tree lists the systems; isolating one draws only its parts', async () => {
    const r = await page.evaluate(() => {
      const t = window.__twin; const all = [...t.rig.parts.values()];
      t.rig.isolate('FUEL');
      const drawn = all.filter((o) => t.rig.drawn(o));
      const out = { drawn: drawn.length, systems: [...new Set(drawn.map((o) => o.userData.system))], rows: document.querySelectorAll('#tree > li').length, parts: all.length };
      t.rig.isolate(null);
      out.after = all.filter((o) => t.rig.drawn(o)).length;
      return out;
    });
    assert.deepEqual(r.systems, ['FUEL']);
    assert.ok(r.drawn > 20, `fuel parts drawn ${r.drawn}`);
    assert.ok(r.rows >= 18, `tree rows ${r.rows}`);
    assert.equal(r.after, r.parts);
  });

  await check('part selection shows bilingual info with a documentation status', async () => {
    await page.evaluate(() => window.__twin.select(window.__twin.rig.part('POWERPLANT.propeller')));
    const html = await page.$eval('#info', (el) => el.innerHTML);
    assert.match(html, /McCauley/); assert.match(html, /badge poh/);
    await page.evaluate(() => window.__twin.select(null));
  });

  await check('confidence overlay colours parts by provenance and restores materials', async () => {
    const before = await page.evaluate(() => window.__twin.rig.part('AIRFRAME.fuselage').material.color.getHex());
    await page.click('#confidence');
    const during = await page.evaluate(() => window.__twin.rig.part('AIRFRAME.fuselage').material.color.getHex());
    assert.notEqual(during, before);
    await page.click('#confidence');
    const after = await page.evaluate(() => window.__twin.rig.part('AIRFRAME.fuselage').material.color.getHex());
    assert.equal(after, before);
  });

  await check('explode animation moves parts away from their system centres', async () => {
    await page.click('#playExplode');
    await page.waitForFunction(() => !window.__twin.exploding, null, { timeout: 120000 });
    const d = await page.evaluate(() => { const r = window.__twin.rig; const w = r.part('WING_L.wing'); const b = r.base.get(w).p; return { dist: w.position.distanceTo(b), f: Number(document.getElementById('explode').value) }; });
    assert.ok(d.f > 0.8 && d.dist > 0.4, JSON.stringify(d));
    await shot(page, 'p8_exploded');
    await page.$eval('#explode', (el) => { el.value = '0'; el.dispatchEvent(new Event('input')); });
    await settle(page, 500);
  });

  await check('engine mode removes the cowl; start from the controls turns the crank and pistons (1-3-2-4)', async () => {
    await page.evaluate(() => window.__twin.setMode('engine', true));
    await settle(page, 1200);
    await shot(page, 'p8_engine');
    await page.click('#bat'); await page.click('#alt');
    for (let i = 0; i < 3; i++) await page.click('#prime');
    await page.$eval('#throttle', (el) => { el.value = '0.08'; el.dispatchEvent(new Event('input')); });
    await page.click('#ign button[data-v="BOTH"]');
    await page.evaluate(() => { const s = window.__twin.sim; s.controls.ignition = 'START'; });
    await page.waitForFunction(() => window.__twin.sim.engine.running, null, { timeout: 20000 });
    await page.evaluate(() => { window.__twin.sim.controls.ignition = 'BOTH'; });
    await page.waitForFunction(() => window.__twin.sim.engine.rpm > 500, null, { timeout: 60000 });
    const e = await page.evaluate(() => { const r = window.__twin.rig; const p1 = r.part('ENGINE.piston_1'), p2 = r.part('ENGINE.piston_2'); return { rpm: window.__twin.sim.engine.rpm, x1: p1.position.x, x2: p2.position.x, cowl: r.part('POWERPLANT.cowl_upper').visible, theta: r.state.theta }; });
    assert.ok(e.rpm > 500, `rpm ${e.rpm}`); assert.ok(e.theta > 0); assert.ok(e.x1 < 0 && e.x2 > 0, 'piston 1 right bank, 2 left bank'); assert.equal(e.cowl, false);
    await page.click('#xray'); await settle(page, 600); await shot(page, 'p8_engine_xray'); await page.click('#xray');
  });

  await check('cockpit mode: camera at the pilot eye, needles follow the simulation', async () => {
    await page.evaluate(() => window.__twin.setMode('cockpit', true));
    await settle(page, 1500);
    const n = await page.evaluate(() => { const r = window.__twin.rig; const t = r.part('PANEL.TACH.needle_TACH'); const cam = window.__twin.viewer.camera.position; return { q: t.quaternion.toArray(), base: r.base.get(t).q.toArray(), cam: [cam.x, cam.y, cam.z], rpm: window.__twin.sim.ind.rpm }; });
    assert.ok(n.q.some((v, i) => Math.abs(v - n.base[i]) > 0.02), 'tach needle rotated');
    assert.ok(n.cam[1] > 1.3 && n.cam[1] < 1.7, `camera y ${n.cam[1]}`);   // pilot eye: just below the top of the side window
    await shot(page, 'p8_cockpit');
  });

  await check('run-up scenario starts and evaluates steps live', async () => {
    await page.evaluate(() => window.__twin.startScenario('runup'));
    await settle(page, 500);
    await page.click('#fuelsel button[data-v="BOTH"]');
    await page.waitForFunction(() => (window.__twin.ctx.done || []).filter(Boolean).length >= 2, null, { timeout: 60000 });
    await page.evaluate(() => window.__twin.startScenario(''));
    await page.close();   // stop this page's render loop before the next pages load (software GL shares the CPU)
  });

  await check('Arabic RTL default', async () => {
    const p2 = await browser.newPage({ viewport: { width: 1440, height: 900 } });
    await p2.goto(`${base}?test=1&q=low`);
    await p2.waitForFunction(() => window.__twin?.ready, null, { timeout: 120000 });
    const dir = await p2.$eval('html', (el) => el.dir);
    assert.equal(dir, 'rtl');
    assert.match(await p2.$eval('#modes', (el) => el.textContent), /الخارج/);
    await settle(p2, 800); await shot(p2, 'p8_arabic');
    await p2.close();
  });

  await check('phone-width low LOD loads and stays console-clean', async () => {
    const ctxm = await browser.newContext({ ...devices['Pixel 5'] });
    const pm = await ctxm.newPage();
    const { errors: errs, loadMs: ms } = await open(pm, 'lang=en');
    perf.low_load_ms = ms;
    await settle(pm, 2000);
    const s = await pm.evaluate(() => ({ q: document.getElementById('quality').value, stats: window.__twin.stats(), scrollW: document.documentElement.scrollWidth, w: innerWidth }));
    perf.low = s.stats;
    assert.equal(s.q, 'low'); assert.ok(s.scrollW <= s.w + 1, 'no horizontal overflow');
    assert.deepEqual(errs, []);
    await shot(pm, 'p8_phone');
    await ctxm.close();
  });

  await check('medium LOD loads', async () => {
    const p3 = await browser.newPage({ viewport: { width: 1200, height: 800 } });
    const { errors: errs, loadMs: ms } = await open(p3, 'lang=en&q=medium');
    perf.medium_load_ms = ms; await settle(p3, 1500);
    perf.medium = await p3.evaluate(() => window.__twin.stats());
    assert.deepEqual(errs, []);
    await p3.close();
  });
} finally {
  await browser.close(); server.close();
}
if (SHOTS) await writeFile(join(SHOTS, 'perf.json'), JSON.stringify(perf, null, 1));
console.log(JSON.stringify(perf));
const failed = results.filter((r) => r[0] === 'FAIL').length;
console.log(`\n${results.length - failed}/${results.length} checks passed`);
process.exit(failed ? 1 : 0);
