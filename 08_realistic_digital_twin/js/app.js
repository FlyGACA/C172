// FlyGACA C172N — Phase 8 realistic digital twin viewer (glue: UI, simulation, rig, scenarios).
import * as THREE from 'three';
import { Viewer, pickQuality, QUALITY } from './viewer.js';
import { Rig } from './rig.js';
import { createState, step, annunciations } from './sim.js';
import { SCENARIOS, evaluateSteps } from './scenarios.js';
import { STRINGS } from './i18n.js';
import { dialGauge, altimeter, attitude, heading, turnCoordinator } from './gauges.js';

const $ = (id) => document.getElementById(id);
const qs = new URLSearchParams(location.search);
const store = { get: (k) => { try { return localStorage.getItem(k); } catch { return null; } }, set: (k, v) => { try { localStorage.setItem(k, v); } catch { /* private */ } } };
let lang = qs.get('lang') || store.get('c172.lang') || 'ar';
if (!STRINGS[lang]) lang = 'ar';
const T = () => STRINGS[lang];
const tx = (o) => (o ? o[lang] ?? o.en : '');

const [INSTR, CATALOG] = await Promise.all([
  fetch('data/instruments.json').then((r) => r.json()).then((j) => j.instruments),
  fetch('data/parts_catalog.json').then((r) => r.json()).then((j) => j.entries.map((e) => ({ ...e, re: new RegExp(e.match) }))).catch(() => []),
]);

// ------------------------------------------------------------------ state
let sim = createState();
let scenario = null, ctx = {};
let paused = false, timeScale = 1, animSpeed = 0.05;
let quality = pickQuality(qs);
let mode = 'exterior';
const ui = { strobe: false };

// ------------------------------------------------------------------ viewer
const viewer = new Viewer($('viewport'), quality, { test: qs.has('test') });
const rigReady = (async () => {
  await viewer.loadEnvironment('assets/hdri/sky.hdr');
  viewer.addGround('assets/textures');
  const root = await viewer.loadModel(QUALITY[quality].file, (f) => { $('loading').querySelector('i').style.width = `${Math.round(f * 100)}%`; });
  const rig = new Rig(root, INSTR, lang);
  rig.buildLabels(lang);
  viewer.setAO(!qs.has('test'));   // software GL in CI cannot afford the AO pass
  if (qs.has('test')) $('ao').classList.remove('on');
  $('loading').classList.add('hide');
  return rig;
})();
let rig = null;
rigReady.then((r) => { rig = r; buildTree(); setMode('exterior', true); window.__twin.ready = true; }).catch((e) => { console.error(e); $('loading').querySelector('span').textContent = T().loadFail; });

// ------------------------------------------------------------------ language
function applyLang() {
  document.documentElement.lang = lang; document.documentElement.dir = T().dir;
  document.querySelectorAll('[data-i18n]').forEach((el) => { const k = el.dataset.i18n; if (T()[k]) el.textContent = T()[k]; });
  $('lang').textContent = T().other; $('title').textContent = T().title8;
  document.title = T().title8;
  $('quality').innerHTML = ['high', 'medium', 'low'].map((q) => `<option value="${q}" ${q === quality ? 'selected' : ''}>${T()['q_' + q]}</option>`).join('');
  $('sources').textContent = T().srcText;
  fillScenarios();
  if (rig) { rig.lang = lang; rig.buildLabels(lang); buildTree(); showInfo(selected); }
}
$('lang').onclick = () => { lang = lang === 'ar' ? 'en' : 'ar'; store.set('c172.lang', lang); applyLang(); };
$('quality').onchange = (e) => { const u = new URL(location.href); u.searchParams.set('q', e.target.value); location.href = u; };
$('btnControls').onclick = () => { $('left').classList.toggle('open'); $('right').classList.remove('open'); };
$('btnParts').onclick = () => { $('right').classList.toggle('open'); $('left').classList.remove('open'); };

// ------------------------------------------------------------------ modes & cameras
const CAMS = {
  exterior: { pos: [-8.5, 2.9, 8.5], tgt: [0, 1.0, 0.2] },
  front: { pos: [0, 1.7, 13], tgt: [0, 1.0, 0] },
  top: { pos: [0.5, 16, 1.2], tgt: [0, 0.8, 1.0] },
  nose: { pos: [-3.0, 1.81, 4.55], tgt: [0.0, 1.15, 0.87] },
  tail: { pos: [3.5, 2.06, -7.56], tgt: [0.0, 1.35, -4.54] },
  gear: { pos: [-3.2, 0.82, 1.48], tgt: [-0.8, 0.41, -0.41] },
  pilot: { pos: [0.28, 1.54, -0.34], tgt: [0.1, 1.23, 0.56] },
  panel: { pos: [0.0, 1.4, -0.59], tgt: [0.0, 1.29, 0.51] },
  engine: { pos: [-2.4, 1.99, 3.74], tgt: [0.0, 1.2, 0.67] },
};
function setMode(m, instant = false) {
  mode = m;
  document.querySelectorAll('#modes button').forEach((b) => b.classList.toggle('on', b.dataset.mode === m));
  if (!rig) return;
  const st = rig.state;
  viewer.camera.near = (m === 'cockpit') ? 0.03 : 0.25; viewer.camera.updateProjectionMatrix();
  if (m === 'exterior') { st.cowlOff = 0; $('cowl').classList.remove('on'); viewer.flyTo(CAMS.exterior.pos, CAMS.exterior.tgt, instant); viewer.controls.minDistance = 1.5; rig.showAll(); rig.isolate(null); }
  if (m === 'cockpit') { viewer.flyTo(CAMS.pilot.pos, CAMS.pilot.tgt, instant); viewer.controls.minDistance = 0.05; rig.isolate(null); rig.showAll(); $('left').classList.add('open'); }
  if (m === 'engine') { st.cowlOff = 1; $('cowl').classList.add('on'); viewer.flyTo(CAMS.engine.pos, CAMS.engine.tgt, instant); viewer.controls.minDistance = 0.3; rig.isolate(null); }
  if (m === 'systems') { viewer.flyTo(CAMS.exterior.pos, CAMS.exterior.tgt, instant); viewer.controls.minDistance = 0.5; rig.setXray(true); $('xray').classList.add('on'); $('scenarioBox').open = true; $('left').classList.add('open'); }
  else { rig.setXray($('xray').classList.contains('on') && m === 'engine'); if (m !== 'engine') $('xray').classList.remove('on'); }
}
document.querySelectorAll('#modes button').forEach((b) => (b.onclick = () => setMode(b.dataset.mode)));
document.querySelectorAll('#cams button').forEach((b) => (b.onclick = () => { const c = CAMS[b.dataset.cam]; if (c) { viewer.flyTo(c.pos, c.tgt); viewer.controls.minDistance = b.dataset.cam === 'pilot' || b.dataset.cam === 'panel' ? 0.05 : 0.5; } }));

// ------------------------------------------------------------------ selection
const ray = new THREE.Raycaster();
let selected = null;
let downAt = null;
viewer.renderer.domElement.addEventListener('pointerdown', (e) => { downAt = [e.clientX, e.clientY]; });
viewer.renderer.domElement.addEventListener('pointerup', (e) => {
  if (!rig || !downAt || Math.hypot(e.clientX - downAt[0], e.clientY - downAt[1]) > 6) return;
  const r = viewer.renderer.domElement.getBoundingClientRect();
  ray.setFromCamera(new THREE.Vector2(((e.clientX - r.left) / r.width) * 2 - 1, -((e.clientY - r.top) / r.height) * 2 + 1), viewer.camera);
  const hits = ray.intersectObject(rig.root, true).filter((h) => h.object.visible && h.object.userData.kind !== 'glass' || h.object.parent?.userData.kind !== 'glass');
  let hit = null;
  for (const h of hits) { let o = h.object; while (o && !o.userData.system) o = o.parent; if (o && o.visible && !o.userData.group) { hit = o; break; } }
  select(hit);
});
function select(o) {
  selected = o; rig.highlight(o); showInfo(o);
  if (o && innerWidth <= 1000) $('right').classList.add('open');
}
function catalogText(name) {
  const e = CATALOG.find((c) => c.re.test(name));
  return e ? (e[lang] || e.en).d : '';
}
function showInfo(o) {
  const box = $('info');
  if (!o) { box.innerHTML = `<p>${T().clickPart}</p>`; return; }
  const u = o.userData;
  const st = u.status || 'estimated';
  const sysName = (T().groups8 || {})[u.system] || u.system;
  const extra = [];
  if (u.ref) extra.push(`<div><b>${T().ref}:</b> ${u.ref}</div>`);
  if (u.note) extra.push(`<div><b>${T().note}:</b> ${u.note}</div>`);
  if (u.cyl) extra.push(`<div><b>${T().cyl}:</b> ${u.cyl}${u.magneto ? ` · ${T().f_mag} ${u.magneto}` : ''}</div>`);
  if (u.range_deg) extra.push(`<div>${u.range_deg[0]}° … ${u.range_deg[1]}°</div>`);
  const desc = catalogText(o.name);
  box.innerHTML = `<h3>${rig.label(o)}</h3><div><span class="badge ${st}">${T()['st_' + st]}</span><span class="badge" style="background:var(--line)">${sysName}</span></div>
    ${desc ? `<p>${desc}</p>` : ''}${extra.join('')}<div class="pair" style="margin-top:8px"><button id="hidePart">${T().hidePart}</button><button id="isoPart">${T().isolatePart}</button><code style="color:var(--mute);font-size:.75rem">${o.name}</code></div>`;
  $('hidePart').onclick = () => { rig.hide(o); select(null); };
  $('isoPart').onclick = () => { rig.isolate(u.system); };
}

// ------------------------------------------------------------------ parts tree
function buildTree() {
  const ul = $('tree'); ul.innerHTML = '';
  const by = rig.partsBySystem();
  for (const [sys, g] of rig.groups) {
    if (!(by[sys] || []).length) continue;
    const li = document.createElement('li');
    const name = (T().groups8 || {})[sys] || sys;
    li.innerHTML = `<input type="checkbox" ${g.visible ? 'checked' : ''}><span class="nm">${name} <small style="color:var(--mute)">(${(by[sys] || []).length})</small></span><button data-iso>${T().isolateSys}</button>`;
    li.querySelector('input').onchange = (e) => rig.setGroupVisible(sys, e.target.checked);
    li.querySelector('[data-iso]').onclick = () => { rig.isolate(sys); buildTree(); };
    li.querySelector('.nm').onclick = () => { li.nextElementSibling?.classList.contains('subs') ? li.nextElementSibling.remove() : expand(li, sys); };
    ul.append(li);
  }
  function expand(li, sys) {
    const holder = document.createElement('li'); holder.className = 'subs'; holder.style.cssText = 'display:block;padding:0;border:0';
    const inner = document.createElement('ul'); inner.style.cssText = 'list-style:none;padding:0;margin:0';
    const seen = new Set();
    for (const o of by[sys] || []) {
      if (o.parent && o.parent.userData.system && !o.parent.userData.group) continue; // sub-parts follow parents
      const lab = rig.label(o); if (seen.has(lab)) continue; seen.add(lab);
      const s = document.createElement('li'); s.className = 'sub';
      s.innerHTML = `<span class="nm">${lab}</span><button>👁</button>`;
      s.querySelector('.nm').onclick = () => select(o);
      s.querySelector('button').onclick = () => { o.visible = !o.visible; };
      inner.append(s);
    }
    holder.append(inner); li.after(holder);
  }
}
$('showAll').onclick = () => { rig.showAll(); rig.isolate(null); buildTree(); };
$('isolateNone').onclick = () => { rig.isolate(null); rig.showAll(); buildTree(); };

// ------------------------------------------------------------------ view tools
$('explode').oninput = (e) => rig && rig.setExplode(Number(e.target.value));
let explodeAnim = null;
$('playExplode').onclick = () => { explodeAnim = { t: 0, from: Number($('explode').value), to: Number($('explode').value) > 0.5 ? 0 : 1 }; };
const tog = (id, fn) => { $(id).onclick = () => { $(id).classList.toggle('on'); fn($(id).classList.contains('on')); }; };
tog('xray', (on) => rig && rig.setXray(on));
tog('labels', (on) => rig && rig.setLabels(on));
tog('confidence', (on) => { if (rig) { select(null); rig.setConfidence(on); } });
tog('cowl', (on) => { if (rig) rig.state.cowlOff = on ? 1 : 0; });
tog('doors', (on) => { if (rig) { rig.state.doorL = on ? 1 : 0; rig.state.doorR = on ? 1 : 0; } });
tog('fairings', (on) => rig && rig.setFairings(on));
tog('ao', (on) => viewer.setAO(on));
$('animSpeed').oninput = (e) => { animSpeed = Number(e.target.value); };
$('crank').oninput = (e) => { if (rig && sim.engine.rpm < 1) rig.state.theta = Number(e.target.value) * Math.PI / 180; };

// ------------------------------------------------------------------ cockpit controls → sim
const c = () => sim.controls;
const bindTog = (id, key) => { $(id).onclick = () => { c()[key] = !c()[key]; $(id).classList.toggle('on', c()[key]); }; };
bindTog('bat', 'masterBat'); bindTog('alt', 'masterAlt'); bindTog('avionics', 'avionics');
bindTog('beacon', 'beacon'); bindTog('navLights', 'navLights'); bindTog('landingLight', 'landingLight'); bindTog('pitotHeat', 'pitotHeat'); bindTog('altStatic', 'altStatic');
$('strobe').onclick = () => { c().strobe = !c().strobe; $('strobe').classList.toggle('on', c().strobe); };
let ignBefore = 'OFF';
document.querySelectorAll('#ign button[data-v]').forEach((b) => (b.onclick = () => { c().ignition = b.dataset.v; ignBefore = b.dataset.v; syncIgn(); }));
const startDown = () => { ignBefore = c().ignition === 'START' ? ignBefore : c().ignition; c().ignition = 'START'; $('start').classList.add('on'); };
const startUp = () => { if (c().ignition === 'START') c().ignition = ignBefore === 'OFF' ? 'BOTH' : ignBefore; $('start').classList.remove('on'); syncIgn(); };
$('start').addEventListener('pointerdown', startDown); $('start').addEventListener('pointerup', startUp); $('start').addEventListener('pointerleave', startUp);
function syncIgn() { document.querySelectorAll('#ign button[data-v]').forEach((b) => b.classList.toggle('on', b.dataset.v === c().ignition)); }
$('throttle').oninput = (e) => { c().throttle = Number(e.target.value); };
$('mixture').oninput = (e) => { c().mixture = Number(e.target.value); };
$('carbHeat').oninput = (e) => { c().carbHeat = Number(e.target.value); };
$('prime').onclick = () => { c().primeStrokes = (c().primeStrokes || 0) + 1; ctx.primes = (ctx.primes || 0) + 1; $('primes').value = ctx.primes; };
document.querySelectorAll('#fuelsel button').forEach((b) => (b.onclick = () => { c().fuelSelector = b.dataset.v; document.querySelectorAll('#fuelsel button').forEach((x) => x.classList.toggle('on', x === b)); }));
document.querySelectorAll('#flapsel button').forEach((b) => (b.onclick = () => { if (rig) rig.state.flaps = Number(b.dataset.v); document.querySelectorAll('#flapsel button').forEach((x) => x.classList.toggle('on', x === b)); }));
$('kollsman').onchange = (e) => { c().altimeterSetting = Number(e.target.value); };
for (const k of ['aileron', 'elevator', 'rudder', 'trim']) $(k).oninput = (e) => { if (rig) rig.state[k] = Number(e.target.value); };
$('centerCtl').onclick = () => { for (const k of ['aileron', 'elevator', 'rudder', 'trim']) { $(k).value = 0; if (rig) rig.state[k] = 0; } };
// flight state
$('onGround').onclick = () => { sim.flight.onGround = !sim.flight.onGround; $('onGround').classList.toggle('on', sim.flight.onGround); };
for (const [id, key, out] of [['iasTarget', 'iasTarget', 'iasOut'], ['altTarget', 'altTarget', 'altOut'], ['bank', 'bank', 'bankOut'], ['pitch', 'pitch', 'pitchOut']]) {
  $(id).oninput = (e) => { sim.flight[key] = Number(e.target.value); $(out).value = e.target.value; };
}
$('timeScale').oninput = (e) => { timeScale = Number(e.target.value); };
$('pause').onclick = () => { paused = !paused; $('pause').textContent = paused ? T().resume : T().pause; };
$('resetSim').onclick = () => { sim = createState(); scenario = null; ctx = {}; syncUI(); };
// faults
$('f_pitot').onchange = (e) => { sim.faults.pitot = e.target.value; };
$('f_static').onclick = () => { sim.faults.staticBlocked = !sim.faults.staticBlocked; $('f_static').classList.toggle('on', sim.faults.staticBlocked); };
$('f_alt').onchange = (e) => { sim.faults.alternator = e.target.value; };
$('f_vac').onclick = () => { sim.faults.vacuum = !sim.faults.vacuum; $('f_vac').classList.toggle('on', sim.faults.vacuum); };
$('f_ice').onclick = () => { sim.faults.carbIce = !sim.faults.carbIce; $('f_ice').classList.toggle('on', sim.faults.carbIce); };
$('f_magR').onchange = (e) => { sim.faults.magneto.R = e.target.value; };
$('f_magL').onchange = (e) => { sim.faults.magneto.L = e.target.value; };
$('fuelL').onchange = (e) => { sim.fuel.left = Number(e.target.value); };
$('fuelR').onchange = (e) => { sim.fuel.right = Number(e.target.value); };

function syncUI() {
  const k = c();
  for (const [id, key] of [['bat', 'masterBat'], ['alt', 'masterAlt'], ['avionics', 'avionics'], ['beacon', 'beacon'], ['navLights', 'navLights'], ['landingLight', 'landingLight'], ['pitotHeat', 'pitotHeat'], ['altStatic', 'altStatic'], ['strobe', 'strobe']]) $(id).classList.toggle('on', !!k[key]);
  syncIgn(); $('throttle').value = k.throttle; $('mixture').value = k.mixture; $('carbHeat').value = k.carbHeat;
  document.querySelectorAll('#fuelsel button').forEach((x) => x.classList.toggle('on', x.dataset.v === k.fuelSelector));
  $('onGround').classList.toggle('on', sim.flight.onGround);
  $('iasTarget').value = sim.flight.iasTarget; $('iasOut').value = sim.flight.iasTarget; $('altTarget').value = sim.flight.altTarget; $('altOut').value = sim.flight.altTarget;
  $('f_pitot').value = sim.faults.pitot; $('f_alt').value = sim.faults.alternator; $('f_magR').value = sim.faults.magneto.R; $('f_magL').value = sim.faults.magneto.L;
  $('f_static').classList.toggle('on', sim.faults.staticBlocked); $('f_vac').classList.toggle('on', sim.faults.vacuum); $('f_ice').classList.toggle('on', sim.faults.carbIce);
  $('fuelL').value = sim.fuel.left; $('fuelR').value = sim.fuel.right; $('primes').value = ctx.primes || 0;
}

// ------------------------------------------------------------------ scenarios
function fillScenarios() {
  const sel = $('scenarioSel');
  sel.innerHTML = `<option value="">${T().freePlay}</option>` + SCENARIOS.map((s) => `<option value="${s.id}">${tx(s.title)} — ${s.poh}</option>`).join('');
  sel.value = scenario ? scenario.id : '';
  renderScenario();
}
$('scenarioSel').onchange = (e) => startScenario(e.target.value);
function startScenario(id) {
  scenario = SCENARIOS.find((s) => s.id === id) || null; ctx = {};
  sim = createState(scenario ? JSON.parse(JSON.stringify(scenario.setup || {})) : {});
  if (scenario && scenario.setup) sim = createState(scenario.setup);
  syncUI(); renderScenario();
  if (scenario && scenario.focus === 'ENGINE' && mode !== 'engine') setMode('engine');
}
function renderScenario() {
  const body = $('scenarioBody');
  if (!scenario) { body.innerHTML = ''; return; }
  const cur = evaluateSteps(scenario, sim, ctx);
  let html = `<p><b>${T().briefing}:</b> ${tx(scenario.brief)}</p><ol class="steps">`;
  scenario.steps.forEach((st, i) => {
    const cls = ctx.done[i] ? 'done' : i === cur ? 'cur' : '';
    html += `<li class="${cls}">${i + 1}. ${tx(st)}${i === cur && st.ack ? ` <button data-ack="${i}">${T().ack}</button>` : ''}${i === cur && st.choice ? st.choice.options.map((o, j) => ` <button data-choice="${i}" data-j="${j}">${tx(o)}</button>`).join('') : ''}</li>`;
  });
  html += '</ol>';
  if (ctx.magResult) html += `<p><b>${T().magResult}:</b> ${T().dropR} ${Math.round(ctx.magResult.dropR)} · ${T().dropL} ${Math.round(ctx.magResult.dropL)} · ${T().diff} ${Math.round(ctx.magResult.diff)} → ${ctx.magResult.pass ? T().pass : T().fail}</p>`;
  if (cur >= scenario.steps.length) {
    html += `<p style="color:var(--green)"><b>${T().completed}</b></p><p><b>${T().debrief}:</b> ${tx(scenario.debrief)}</p>`;
    if (scenario.quiz) {
      html += `<p><b>${T().quiz}:</b> ${tx(scenario.quiz.q)}</p>` + scenario.quiz.options.map((o, j) => `<button data-quiz="${j}">${tx(o)}</button> `).join('');
      if (ctx.quiz !== undefined) html += `<p>${ctx.quiz === scenario.quiz.answer ? T().correct : T().wrong} (${scenario.quiz.ref})</p>`;
    }
  }
  html += `<p><button id="restartSc">${T().restart}</button></p>`;
  body.innerHTML = html;
  body.querySelectorAll('[data-ack]').forEach((b) => (b.onclick = () => { ctx.done[Number(b.dataset.ack)] = true; renderScenario(); }));
  body.querySelectorAll('[data-choice]').forEach((b) => (b.onclick = () => { const st = scenario.steps[Number(b.dataset.choice)]; if (Number(b.dataset.j) === st.choice.answer) { ctx.done[Number(b.dataset.choice)] = true; } else { ctx.wrong = (ctx.wrong || 0) + 1; } renderScenario(); }));
  body.querySelectorAll('[data-quiz]').forEach((b) => (b.onclick = () => { ctx.quiz = Number(b.dataset.quiz); renderScenario(); }));
  const rs = $('restartSc'); if (rs) rs.onclick = () => startScenario(scenario.id);
}
let lastStepState = '';

// ------------------------------------------------------------------ 2D gauges
const G = {};
{
  const host = $('gauges');
  G.ASI = dialGauge(host, 'ASI', INSTR.ASI, 'ASI', (v) => `${Math.round(v)} kt`);
  G.AI = attitude(host, 'AI'); G.ALT = altimeter(host, INSTR.ALT, 'ALT');
  G.TC = turnCoordinator(host, 'TC'); G.HI = heading(host, 'HI'); G.VSI = dialGauge(host, 'VSI', INSTR.VSI, 'VSI', (v) => `${Math.round(v)} fpm`);
  G.TACH = dialGauge(host, 'TACH', INSTR.TACH, 'RPM', (v) => `${Math.round(v)}`);
  G.SUCTION = dialGauge(host, 'SUCTION', INSTR.SUCTION, 'SUCT', (v) => v.toFixed(1)); G.AMMETER = dialGauge(host, 'AMMETER', INSTR.AMMETER, 'AMP', (v) => `${Math.round(v)}`);
  G.OIL_P = dialGauge(host, 'OIL_P', INSTR.OIL_P, 'OIL P', (v) => `${Math.round(v)}`); G.OIL_T = dialGauge(host, 'OIL_T', INSTR.OIL_T, 'OIL T', (v) => `${Math.round(v)}`);
  G.FUEL_L = dialGauge(host, 'FUEL_L', INSTR.FUEL_L, 'FUEL L', (v) => v.toFixed(1)); G.FUEL_R = dialGauge(host, 'FUEL_R', INSTR.FUEL_R, 'FUEL R', (v) => v.toFixed(1));
}
function updateGauges() {
  const i = sim.ind;
  G.ASI.update(i.ias); G.AI.update(i.aiBank, i.aiPitch); G.ALT.update(i.alt, sim.controls.altimeterSetting); G.TC.update(i.tc, i.tcFlag); G.HI.update(i.hi); G.VSI.update(i.vsi);
  G.TACH.update(i.rpm); G.SUCTION.update(i.suction); G.AMMETER.update(i.ammeter); G.OIL_P.update(i.oilP); G.OIL_T.update(i.oilT); G.FUEL_L.update(i.fuelL); G.FUEL_R.update(i.fuelR);
}

// ------------------------------------------------------------------ main loop
let gaugeTimer = 0, statTimer = 0;
viewer.onFrame.push((dt) => {
  if (!paused) {
    step(sim, dt * timeScale);
    if (scenario) {
      if (scenario.tick) scenario.tick(sim, ctx, dt * timeScale);
      const key = JSON.stringify(ctx.done || []) + (ctx.magResult ? 'm' : '');
      if (key !== lastStepState) { lastStepState = key; renderScenario(); } else evaluateSteps(scenario, sim, ctx);
    }
  }
  viewer.tickCamera(dt);
  if (explodeAnim) { explodeAnim.t = Math.min(1, explodeAnim.t + dt / 1.6); const k = 1 - Math.pow(1 - explodeAnim.t, 3); const v = explodeAnim.from + (explodeAnim.to - explodeAnim.from) * k; $('explode').value = v; rig && rig.setExplode(v); if (explodeAnim.t >= 1) explodeAnim = null; }
  if (rig) {
    const st = rig.state;
    st.ind = sim.ind; st.controls = sim.controls; st.truth = sim.truth;
    st.running = sim.engine.running; st.cranking = sim.engine.cranking; st.magsFiring = sim.engine.magsFiring || [];
    rig.update(dt, animSpeed);
    if (sim.engine.rpm >= 1) { $('crank').value = Math.round(((st.theta * 180 / Math.PI) % 720 + 720) % 720); }
    $('crankOut').textContent = `${$('crank').value}°`;
  }
  gaugeTimer += dt;
  if (gaugeTimer > 0.1) { gaugeTimer = 0; updateGauges(); const a = annunciations(sim); $('annun').innerHTML = a.map((k) => `<span class="${k === 'low_voltage' || k === 'oil_pressure_low' ? '' : 'warn'}">${(T().annun || {})[k] || k}</span>`).join(''); }
  statTimer += dt;
  if (statTimer > 2 && rig) { statTimer = 0; const s = viewer.stats(); $('hint').textContent = `${T().hint} · ${s.triangles.toLocaleString()} ${T().stats} · ${s.calls} ${T().calls} · ${T()['q_' + quality]}`; }
});
viewer.start();
applyLang(); syncUI();

// test hook
window.__twin = { ready: false, get exploding() { return !!explodeAnim; }, get rig() { return rig; }, get sim() { return sim; }, viewer, setMode, select, startScenario, stats: () => viewer.stats(), get scenario() { return scenario; }, get ctx() { return ctx; } };
