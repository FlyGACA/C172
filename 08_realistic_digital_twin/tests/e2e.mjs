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
const ONLY = process.env.E2E_ONLY;      // run only the checks whose name contains this: for work on one check, never in CI
async function check(name, fn) {
  if (ONLY && !name.includes(ONLY)) { console.log(`skipped - ${name}`); return; }
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

  await check("the pilot's seat: the head turns within its limits, the hand works the controls it can reach", async () => {
    await page.evaluate(() => { window.__twin.setMode('cockpit', true); window.__twin.seat.lookAt('ahead', true); window.__twin.seat.place(); });
    // the camera is the pilot's eye; the orbit of the other modes is off
    const eye = await page.evaluate(async () => {
      const S = await import('./js/seat.js'); const t = window.__twin, c = t.viewer.camera, want = S.eyePosition(S.REST);
      return { enabled: t.seat.enabled, off: Math.hypot(c.position.x - want[0], c.position.y - want[1], c.position.z - want[2]), manual: !!t.viewer.manualCamera, orbit: t.viewer.controls.enabled, fov: c.fov, near: c.near, box: document.getElementById('seatBox').hidden, head: S.HEAD };
    });
    assert.ok(eye.enabled && eye.manual && !eye.orbit && !eye.box, JSON.stringify(eye));
    assert.ok(eye.off < 1e-6 && eye.fov === 68 && eye.near === 0.03, `eye ${eye.off}, fov ${eye.fov}, near ${eye.near}`);
    // the head: no farther than its limits, by the pointer or by a lean
    const lim = await page.evaluate(() => {
      const s = window.__twin.seat, run = () => { for (let i = 0; i < 80; i++) s.tick(0.05); return { ...s.head }; };
      s.look(999, 999); const most = { ...s.head }; s.look(-9999, -9999); const least = { ...s.head };
      s.lean(9, 9); const leantOut = run(); s.lean(-99, -99); const leantBack = run();
      s.lookAt('ahead', true); s.place();
      return { most, least, leantOut, leantBack };
    });
    const H = eye.head;
    assert.deepEqual([lim.most.yaw, lim.most.pitch, lim.least.yaw, lim.least.pitch], [H.yaw[1], H.pitch[1], H.yaw[0], H.pitch[0]]);
    assert.ok(Math.abs(lim.leantOut.forward - H.leanForward[1]) < 1e-3 && Math.abs(lim.leantOut.side - H.leanSide[1]) < 1e-3, JSON.stringify(lim.leantOut));
    assert.ok(Math.abs(lim.leantBack.forward - H.leanForward[0]) < 1e-3 && Math.abs(lim.leantBack.side - H.leanSide[0]) < 1e-3, JSON.stringify(lim.leantBack));
    // wherever the limits let the eye go, the cabin stays clear of it: nothing nearer than 6 cm, twice the near plane of the camera
    const clear = await page.evaluate(async () => {
      const THREE = await import('three'), S = await import('./js/seat.js');
      const root = window.__twin.rig.root, L = S.HEAD, datum = new THREE.Vector3(...L.eye), near = [], sphere = new THREE.Sphere();
      root.traverse((m) => { if (!m.isMesh || m.userData.fpShell) return; if (!m.geometry.boundingSphere) m.geometry.computeBoundingSphere(); sphere.copy(m.geometry.boundingSphere).applyMatrix4(m.matrixWorld); if (sphere.center.distanceTo(datum) - sphere.radius < 0.9) near.push(m); });
      const dirs = [], N = 60; for (let i = 0; i < N; i++) { const y = 1 - (2 * (i + 0.5)) / N, rad = Math.sqrt(1 - y * y), th = i * Math.PI * (3 - Math.sqrt(5)); dirs.push(new THREE.Vector3(Math.cos(th) * rad, y, Math.sin(th) * rad)); }
      const ray = new THREE.Raycaster(); ray.far = 0.3;
      let min = { d: 9 };
      for (const yaw of [L.yaw[0], -90, 0, 90, L.yaw[1]]) for (const pitch of [L.pitch[0], -35, L.pitch[1]]) for (const forward of L.leanForward) for (const side of L.leanSide) {
        const e = new THREE.Vector3(...S.eyePosition({ yaw, pitch, forward, side }));
        for (const dir of dirs) { ray.set(e, dir); const h = ray.intersectObjects(near, false).find((i) => i.object.visible); if (h && h.distance < min.d) { let o = h.object; while (o && !o.userData.system) o = o.parent; min = { d: h.distance, part: o ? o.name : '?', yaw, pitch, forward, side }; } }
      }
      return min;
    });
    assert.ok(clear.d >= 0.06, `the eye comes within ${(clear.d * 100).toFixed(1)} cm of ${clear.part}: ${JSON.stringify(clear)}`);
    // what the hand reaches from the seat
    const reach = await page.evaluate(() => { const s = window.__twin.seat; return Object.fromEntries(Object.keys(s.controls).map((n) => [n, s.reach(n)])); });
    assert.ok(Object.keys(reach).length >= 22, `${Object.keys(reach).length} controls`);
    for (const n of ['PANEL.throttle', 'PANEL.mixture', 'PANEL.carb_heat', 'PANEL.ignition_switch', 'PANEL.master_bat', 'PANEL.master_alt', 'PANEL.switch_beacon', 'PANEL.primer', 'PANEL.flap_switch', 'INTERIOR.trim_wheel', 'INTERIOR.yoke_L', 'INTERIOR.parking_brake', 'FUEL.selector_handle', 'INTERIOR.door_inner_handle_L']) assert.equal(reach[n], 'near', n);
    assert.equal(reach['PANEL.cabin_air'], 'lean', 'the cabin air control, on the far side of the panel, takes a lean');
    assert.ok(!Object.values(reach).includes('far'), `one pilot flies it: no control is out of reach of the left seat: ${JSON.stringify(reach)}`);
    // the hand, with the pointer of the browser
    const look = (view) => page.evaluate((v) => { const s = window.__twin.seat; s.lookAt(v, true); s.place(); }, view);
    const locate = async (name, half = null) => { const p = await page.evaluate(([n, h]) => window.__twin.seat.locate(n, h), [name, half]); assert.ok(p, `${name} can be seen and pointed at`); return p; };
    const tip = () => page.evaluate(() => { const t = document.getElementById('fptip'); return t.hidden ? '' : `${t.className}: ${t.textContent}`; });
    const controls = () => page.evaluate(() => { const t = window.__twin, c = t.sim.controls, st = t.rig.state; return { beacon: !!c.beacon, ignition: c.ignition, throttle: c.throttle, flaps: st.flaps, trim: st.trim, aileron: st.aileron, elevator: st.elevator, cabinAir: st.cabinAir, head: { ...t.seat.head } }; });
    await look('panel');
    let p = await locate('PANEL.switch_beacon');
    const before = await controls();
    await page.mouse.move(p.x, p.y);
    assert.match(await tip(), /^near: Beacon.* · (ON|OFF)$/);
    await page.mouse.click(p.x, p.y);
    assert.equal((await controls()).beacon, !before.beacon, 'a click flips the beacon switch');
    assert.match(await tip(), before.beacon ? /OFF$/ : /ON$/);
    // the key: the left half turns it back one position, the right half forward; held on the right at BOTH it is the starter
    await page.evaluate(() => { window.__twin.sim.controls.ignition = 'BOTH'; });
    p = await locate('PANEL.ignition_switch', 'left'); await page.mouse.click(p.x, p.y);
    assert.equal((await controls()).ignition, 'L');
    p = await locate('PANEL.ignition_switch', 'right'); await page.mouse.click(p.x, p.y);
    assert.equal((await controls()).ignition, 'BOTH');
    p = await locate('PANEL.ignition_switch', 'right'); await page.mouse.move(p.x, p.y); await page.mouse.down();
    assert.equal((await controls()).ignition, 'START');
    await page.mouse.up();
    assert.equal((await controls()).ignition, 'BOTH');
    // push-pull, lever and wheels
    await look('pedestal');
    const t0 = (await controls()).throttle;
    p = await locate('PANEL.throttle');
    await page.mouse.move(p.x, p.y); await page.mouse.down(); await page.mouse.move(p.x, p.y - 51, { steps: 5 }); await page.mouse.up();
    const t1 = (await controls()).throttle;
    assert.ok(Math.abs(t1 - Math.min(1, t0 + 0.3)) < 0.02, `throttle pushed in: ${t0.toFixed(2)} to ${t1.toFixed(2)}`);
    p = await locate('PANEL.flap_switch'); await page.mouse.move(p.x, p.y); await page.mouse.wheel(0, 100);
    assert.equal((await controls()).flaps, 10, 'the flap lever, one position down');
    assert.match(await tip(), /10°$/);
    await page.mouse.wheel(0, -100);
    assert.equal((await controls()).flaps, 0);
    p = await locate('INTERIOR.trim_wheel'); await page.mouse.move(p.x, p.y); await page.mouse.down(); await page.mouse.move(p.x, p.y + 60, { steps: 5 }); await page.mouse.up();
    assert.ok(Math.abs((await controls()).trim - 0.1) < 0.01, 'the trim wheel rolled down: nose up');
    p = await locate('INTERIOR.yoke_L'); await page.mouse.move(p.x, p.y); await page.mouse.down(); await page.mouse.move(p.x + 75, p.y + 45, { steps: 5 });
    const held = await controls();
    await page.mouse.up();
    assert.ok(Math.abs(held.aileron - 0.5) < 0.02 && Math.abs(held.elevator - 0.3) < 0.02, `the control wheel in the hand: ${held.aileron}, ${held.elevator}`);
    await shot(page, 'p8_seat_hand');
    await page.evaluate(() => { const st = window.__twin.rig.state; st.aileron = st.elevator = st.trim = 0; });
    // out of reach until the body leans toward it
    p = await locate('PANEL.cabin_air');
    assert.equal(p.reach, 'lean');
    await page.mouse.move(p.x, p.y);
    assert.match(await tip(), /^lean: Cabin air.*out of reach/);
    await page.mouse.click(p.x, p.y);
    assert.equal((await controls()).cabinAir, 0, 'a control out of reach does not move');
    await page.evaluate(() => { const s = window.__twin.seat; s.lean(0.08, -0.08); for (let i = 0; i < 60; i++) s.tick(0.05); s.place(); });
    p = await locate('PANEL.cabin_air');
    assert.equal(p.reach, 'near');
    await page.mouse.click(p.x, p.y);
    assert.equal((await controls()).cabinAir, 1, 'with a lean the hand reaches it');
    await page.evaluate(() => { window.__twin.rig.state.cabinAir = 0; window.__twin.seat.setShowReach(true); });
    await look('pedestal'); await settle(page, 600); await shot(page, 'p8_seat_reach');
    const tinted = await page.evaluate(() => { const s = window.__twin.seat; const n = [...s.shells.values()].filter(Boolean).length; s.setShowReach(false); return n; });
    assert.ok(tinted >= 22, `${tinted} controls tinted by reach`);
    // the head: a drag on the picture turns it the way the pointer goes; a key leans; the orbit camera stays out of it
    await look('ahead');
    const box = await page.evaluate(() => { const r = window.__twin.viewer.renderer.domElement.getBoundingClientRect(); return { x: r.left + r.width / 2, y: r.top + r.height * 0.22 }; });
    await page.mouse.move(box.x, box.y); await page.mouse.down(); await page.mouse.move(box.x - 150, box.y + 50, { steps: 6 }); await page.mouse.up();
    const turned = (await controls()).head;
    assert.ok(Math.abs(turned.yaw - 30) < 1.5 && Math.abs(turned.pitch - (-11 - 8.5)) < 1.5, `head ${turned.yaw.toFixed(1)}, ${turned.pitch.toFixed(1)}`);
    await page.keyboard.down('KeyW');
    await page.waitForFunction(() => window.__twin.seat.head.forward > 0.03, null, { timeout: 30000 });
    await page.keyboard.up('KeyW'); await page.keyboard.press('KeyR');
    await page.waitForFunction(() => { const s = window.__twin.seat; return s.settled && s.head.forward < 0.005 && Math.abs(s.head.yaw) < 0.5; }, null, { timeout: 30000 });
    // a click on anything that is not a control shows what it is; the eye looks through the glass of an instrument
    p = await page.evaluate(async () => { const THREE = await import('three'); const t = window.__twin; t.seat.place(); const c = new THREE.Box3().setFromObject(t.rig.part('PANEL.ALT.glass')).getCenter(new THREE.Vector3()).project(t.viewer.camera), r = t.viewer.renderer.domElement.getBoundingClientRect(); return { x: r.left + ((c.x + 1) / 2) * r.width, y: r.top + ((1 - c.y) / 2) * r.height }; });
    await page.mouse.click(p.x, p.y);
    const named = await page.$eval('#info h3', (el) => el.textContent);
    assert.ok(/ALT/.test(named) && !/glass/i.test(named), `clicked the altimeter: "${named}"`);
    await shot(page, 'p8_seat');
    // leaving the seat gives the viewer its camera back
    await page.click('#modes button[data-mode=exterior]');
    const left = await page.evaluate(() => { const t = window.__twin; return { enabled: t.seat.enabled, manual: !!t.viewer.manualCamera, orbit: t.viewer.controls.enabled, fov: t.viewer.camera.fov, near: t.viewer.camera.near, box: document.getElementById('seatBox').hidden, tinted: [...t.seat.shells.values()].filter(Boolean).length, tip: document.getElementById('fptip').hidden }; });
    assert.deepEqual(left, { enabled: false, manual: false, orbit: true, fov: 42, near: 0.25, box: true, tinted: 0, tip: true });
    assert.deepEqual(errors, []);
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
console.log(`\n${results.length - failed}/${results.length} checks passed${ONLY ? ` (only those named "${ONLY}")` : ''}`);
process.exit(failed ? 1 : 0);
