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

  await check('flight mode: the flight model flies the aircraft and moves the surfaces and the instruments', async () => {
    const pf = await browser.newPage({ viewport: { width: 1440, height: 900 } });
    const { errors: errs } = await open(pf, 'lang=en&q=low');
    await pf.click('#modes button[data-mode=flight]');
    await pf.waitForFunction(() => window.__twin.flight.active, null, { timeout: 30000 });
    // software GL draws a few frames a second, so the test advances the flight itself
    const fly = (seconds, set = {}) => pf.evaluate(([seconds, set]) => {
      const t = window.__twin, f = t.flight;
      if (set.throttle != null) t.sim.controls.throttle = set.throttle;
      if (set.parking != null) f.parking = set.parking;
      if (set.flaps != null) f.setFlaps(set.flaps);
      f.stick.dragging = set.wheel != null; if (set.wheel != null) { f.stick.x = set.wheel[0]; f.stick.y = set.wheel[1]; }
      for (let i = 0; i < seconds * 60; i++) f.step(1 / 60);
      f.place(); t.rig.update(0.016, 0.05);
      const o = f.deck.flight.out, r = t.rig, moved = (n) => { const p = r.part(n); return p ? p.quaternion.angleTo(r.base.get(p).q) : -1; };
      return { kias: o.kias, agl: o.aglFt, gs: o.groundSpeedKt, hdg: o.headingDeg, bank: o.bankDeg, flap: o.flapDeg, wheels: o.wheels, rpm: t.sim.ind.rpm, ias: t.sim.ind.ias, alt: t.sim.ind.alt, stall: t.sim.ind.stallWarning,
        pivot: f.pivot.position.toArray(), elevator: moved('EMPENNAGE.elevator'), flapPart: moved('WING_L.flap'), asi: moved('PANEL.ASI.needle_ASI'), crashed: f.crashed, hudStall: document.getElementById('fhud').classList.contains('stall') };
    }, [seconds, set]);
    const start = await pf.evaluate(() => { const t = window.__twin; return { hud: !document.getElementById('fhud').hidden, pad: !document.getElementById('fpad').hidden, parent: t.viewer.model.parent.name, dynamic: !!t.sim.flight.dynamic, running: t.sim.engine.running, far: t.viewer.camera.far }; });
    assert.deepEqual(start, { hud: true, pad: true, parent: '_aircraftPivot', dynamic: true, running: true, far: 45000 });
    const roll = await fly(18, { throttle: 1, parking: false });
    assert.ok(roll.gs > 45 && roll.wheels === 3, `after 18 s at full throttle: ${roll.gs.toFixed(0)} kt on ${roll.wheels} wheels`);
    assert.ok(roll.rpm > 2280 && roll.rpm < 2420, `tachometer ${roll.rpm.toFixed(0)}`);
    assert.ok(Math.abs(((roll.hdg + 180) % 360) - 180) < 6, `it runs straight: heading ${roll.hdg.toFixed(1)}`);
    assert.ok(roll.asi > 0.3, 'the airspeed needle of the 3D panel has moved');
    await fly(3, { wheel: [0, 0.25] });
    const air = await fly(8, { wheel: [0, 0.06] });
    assert.ok(air.agl > 30 && air.wheels === 0 && !air.crashed, `airborne at ${air.agl.toFixed(0)} ft`);
    assert.ok(air.pivot[1] > 9 && air.pivot[2] > 300, `the model is where the flight is: ${air.pivot.map((v) => v.toFixed(0))}`);
    assert.ok(air.elevator > 0.01, 'the elevator of the model follows the wheel');
    assert.ok(Math.abs(air.ias - air.kias) < 3 && air.alt > 30, `instruments: ${air.ias.toFixed(0)} KIAS, ${air.alt.toFixed(0)} ft`);
    await shot(pf, 'p8_flight_climb');
    // cruise: the flaps travel at the speed of their motor, and the model's flaps with them
    await pf.evaluate(() => window.__twin.beginFlight('cruise'));
    const flap = await fly(5, { flaps: 20, wheel: [0, -0.05] });
    assert.ok(Math.abs(flap.flap - 20) < 0.5 && flap.flapPart > 0.3, `flaps ${flap.flap.toFixed(1)}`);
    // throttle closed and the wheel coming back: the stall warning
    let warned = false;
    await fly(1, { throttle: 0, flaps: 0 });
    for (let i = 0; i < 30 && !warned; i++) { const s = await fly(1.5, { wheel: [0, Math.min(0.6, 0.05 + i * 0.03)] }); warned = s.stall && s.hudStall; }
    assert.ok(warned, 'the stall warning shows');
    // the pilot's eye
    await pf.evaluate(() => { const f = window.__twin.flight; window.__twin.beginFlight('approach'); f.setCamera('cockpit', true); f.place(); });
    const eye = await pf.evaluate(() => { const t = window.__twin, f = t.flight; return { d: t.viewer.camera.position.distanceTo(f.pivot.position), manual: !!t.viewer.manualCamera, fov: t.viewer.camera.fov }; });
    assert.ok(eye.d < 1.2 && eye.manual && eye.fov > 60, JSON.stringify(eye));
    await settle(pf, 1500); await shot(pf, 'p8_flight_cockpit');
    // every number of the model, with its source
    await pf.click('#flCoef');
    const table = await pf.evaluate(() => ({ rows: document.querySelectorAll('#coefTable tbody tr').length, kinds: [...new Set([...document.querySelectorAll('#coefTable .badge')].map((b) => b.className.replace('badge ', '')))].sort() }));
    assert.ok(table.rows > 70, `rows ${table.rows}`); assert.deepEqual(table.kinds, ['derived', 'estimated', 'poh']);
    await pf.click('#coefClose');
    await pf.click('#lang'); await pf.click('#flCoef');
    assert.match(await pf.$eval('#coefTable tbody tr td:nth-child(4)', (el) => el.textContent), /[\u0600-\u06FF]{4}/);
    await pf.click('#coefClose'); await pf.click('#lang');
    // a flight lesson from the scenario list, flown by its demonstration pilot: the steps latch, the record is shown
    await pf.evaluate(() => { document.getElementById('scenarioBox').open = true; });
    await pf.selectOption('#scenarioSel', 'go_around');
    const began = await pf.evaluate(() => { const t = window.__twin, o = t.flight.deck.flight.out; return { lesson: !!t.scenario.lesson, flap: o.flapDeg, agl: o.aglFt, heat: t.sim.controls.carbHeat, demoButton: !!document.getElementById('lessonDemo') }; });
    assert.ok(began.lesson && began.demoButton && began.flap === 40 && began.agl > 100 && began.heat === 1, JSON.stringify(began));
    await pf.click('#lessonDemo');
    const goAround = await pf.evaluate(() => { const t = window.__twin; t.advance(40); return { done: (t.ctx.done || []).filter(Boolean).length, steps: t.scenario.steps.length, flap: t.flight.deck.flight.flapDeg, agl: t.flight.deck.flight.out.aglFt,
      throttle: Number(document.getElementById('throttle').value), report: document.querySelectorAll('#scenarioBody ul li').length, completed: /lesson|Scenario complete/i.test(document.getElementById('scenarioBody').textContent) }; });
    assert.equal(goAround.done, goAround.steps, JSON.stringify(goAround));
    assert.ok(goAround.flap === 0 && goAround.agl > 300 && goAround.report === 3 && goAround.completed, JSON.stringify(goAround));
    // the engine failure of the fault panel ends the pull, from a lesson or by hand
    await pf.selectOption('#scenarioSel', 'engine_failure_after_takeoff');
    await pf.click('#lessonDemo');
    const failure = await pf.evaluate(() => { const t = window.__twin; t.advance(60); const o = t.flight.deck.flight.out; return { done: (t.ctx.done || []).filter(Boolean).length, steps: t.scenario.steps.length, fault: t.sim.faults.engineFailure, lamp: document.getElementById('f_engine').classList.contains('on'),
      running: t.sim.engine.running, onGround: o.onGround, crashed: t.flight.crashed, master: t.sim.controls.masterBat, selector: t.sim.controls.fuelSelector }; });
    assert.deepEqual(failure, { done: failure.steps, steps: failure.steps, fault: true, lamp: true, running: false, onGround: true, crashed: null, master: false, selector: 'OFF' });
    await shot(pf, 'p8_flight_lesson');
    await pf.selectOption('#scenarioSel', '');
    // leaving the mode puts the aircraft back on the apron
    await pf.click('#modes button[data-mode=exterior]');
    const end = await pf.evaluate(() => { const t = window.__twin; return { active: t.flight.active, parent: t.viewer.model.parent.type, pos: t.viewer.model.position.toArray(), dynamic: !!t.sim.flight.dynamic, far: t.viewer.camera.far, manual: !!t.viewer.manualCamera, hud: document.getElementById('fhud').hidden, fov: t.viewer.camera.fov }; });
    assert.deepEqual(end, { active: false, parent: 'Scene', pos: [0, 0, 0], dynamic: false, far: 300, manual: false, hud: true, fov: 42 });
    assert.deepEqual(errs, []);
    await pf.close();
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
