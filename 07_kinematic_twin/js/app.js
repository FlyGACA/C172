// FlyGACA C172N Digital Twin — Phase 7 viewer.
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { CSS2DRenderer, CSS2DObject } from 'three/addons/renderers/CSS2DRenderer.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { createState, step, annunciations, POH } from './sim.js';
import * as K from './kinematics.js';
import { SCENARIOS, evaluateSteps } from './scenarios.js';
import { STRINGS } from './i18n.js';
import { dialGauge, altimeter, attitude, heading, turnCoordinator, valueToAngle } from './gauges.js';

const $ = (id) => document.getElementById(id);
const store = {
  get(k) { try { return localStorage.getItem(k); } catch { return null; } },
  set(k, v) { try { localStorage.setItem(k, v); } catch { /* private mode */ } },
};
const qs = new URLSearchParams(location.search);
let lang = qs.get('lang') || store.get('c172.lang') || 'ar';
if (!STRINGS[lang]) lang = 'ar';
const T = () => STRINGS[lang];
const tx = (o) => (o ? o[lang] ?? o.en : '');

const [INSTR, CATALOG] = await Promise.all([
  fetch('data/instruments.json').then((r) => r.json()).then((j) => j.instruments),
  fetch('data/parts_catalog.json').then((r) => r.json()).then((j) => j.entries.map((e) => ({ ...e, re: new RegExp(e.match) }))),
]);

// ===================================================================== simulation state
let sim = createState();
let scenario = null;
let ctx = {};
let paused = false;
let timeScale = 1;
let animSpeed = 0.025;
let theta = 0; // displayed crank angle, radians

// ===================================================================== three.js scene
const viewport = $('viewport');
const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, preserveDrawingBuffer: qs.has('test') });
renderer.setClearColor(0x000000, 0);
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
viewport.prepend(renderer.domElement);
const labelRenderer = new CSS2DRenderer();
labelRenderer.domElement.style.cssText = 'position:absolute;inset:0;pointer-events:none;z-index:2';
viewport.append(labelRenderer.domElement);

const scene = new THREE.Scene();
const pmrem = new THREE.PMREMGenerator(renderer);
scene.environment = pmrem.fromScene(new RoomEnvironment(renderer), 0.04).texture;
scene.add(new THREE.HemisphereLight(0xdfeeff, 0x223344, 0.8));
const sun = new THREE.DirectionalLight(0xffffff, 1.6);
sun.position.set(4, 8, 6);
scene.add(sun);
const camera = new THREE.PerspectiveCamera(40, 1, 0.01, 200);
camera.position.set(9, 5, 9);
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.target.set(0, 1.3, -1.5);

function resize() {
  const w = viewport.clientWidth, h = viewport.clientHeight;
  renderer.setSize(w, h, false);
  labelRenderer.setSize(w, h);
  camera.aspect = w / Math.max(1, h);
  camera.updateProjectionMatrix();
}
new ResizeObserver(resize).observe(viewport);
resize();

// model bookkeeping
const nodes = new Map();        // name -> Object3D
const groups = new Map();       // group name -> group node
const parts = [];               // direct children of group nodes
const base = new Map();         // part -> base position
const explodeDir = new Map();   // part -> offset vector at explode = 1
const plugs = [];
const xrayMats = new Set();
const labels = [];
let model = null;

function partOf(obj) {
  let o = obj;
  while (o && o.parent && o.parent.userData?.kind !== 'group') o = o.parent;
  return o && o.parent ? o : null;
}

new GLTFLoader().load('C172N_Phase7_Kinematic_Twin.glb', (gltf) => {
  model = gltf.scene;
  scene.add(model);
  model.traverse((o) => {
    if (o.name) nodes.set(o.name, o);
    if (o.userData?.kind === 'group') groups.set(o.userData.group, o);
  });
  model.updateMatrixWorld(true);
  for (const g of groups.values()) {
    const gbox = new THREE.Box3().setFromObject(g);
    const gc = gbox.getCenter(new THREE.Vector3());
    const radius = gbox.getSize(new THREE.Vector3()).length() / 2;
    for (const p of g.children) {
      parts.push(p);
      base.set(p, p.position.clone());
      const c = new THREE.Box3().setFromObject(p).getCenter(new THREE.Vector3());
      const d = c.sub(gc);
      if (d.lengthSq() < 1e-6) d.set(0, 1, 0);
      explodeDir.set(p, d.normalize().multiplyScalar(Math.max(0.25, radius * 0.45)));
    }
  }
  model.traverse((o) => {
    if (!o.isMesh) return;
    if (partOf(o)?.userData?.xray) xrayMats.add(o.material);
    if (o.userData?.anim === 'spark') {
      o.material = o.material.clone();
      plugs.push({ mesh: o, cyl: o.userData.cyl, mag: o.userData.magneto });
    }
    if (o.name === 'PANEL__LOW_VOLTAGE_light') o.material = o.material.clone();
  });
  buildLabels();
  setLabelsVisible(labelsWanted);
  buildIsolate();
  applyXray(true);
  setView('aircraft', true);
  const st = $('viewstatus');
  st.dataset.i18n = 'ready';
  st.textContent = T().ready;
  setTimeout(() => (st.hidden = true), 3500);
  window.__twin.ready = true;
}, undefined, (err) => {
  console.error(err);
  $('viewstatus').dataset.i18n = 'loadFail';
  $('viewstatus').textContent = T().loadFail;
});

function applyXray(on) {
  for (const m of xrayMats) {
    m.transparent = on;
    m.opacity = on ? 0.22 : 1;
    m.depthWrite = !on;
    m.needsUpdate = true;
  }
}

const LABELS = [
  ['ENGINE__cylinder_1_rocker_cover', 'cyl', 1], ['ENGINE__cylinder_2_rocker_cover', 'cyl', 2],
  ['ENGINE__cylinder_3_rocker_cover', 'cyl', 3], ['ENGINE__cylinder_4_rocker_cover', 'cyl', 4],
  ['IGNITION__dual_magneto'], ['ELECTRICAL__battery'], ['ENGINE__alternator'], ['ENGINE__starter'],
  ['INDUCTION__carburetor'], ['VACUUM__engine_driven_pump'], ['OIL__oil_cooler'], ['FUEL__selector_valve_body'],
  ['FUEL__fuel_strainer'], ['FUEL__tank_L'], ['FUEL__tank_R'], ['PITOT_STATIC__pitot_tube'], ['PITOT_STATIC__static_port'],
  ['ELECTRICAL__alternator_control_unit'], ['OIL__sump'],
];
const LABEL_TEXT = {
  PITOT_STATIC__static_port: { en: 'Static port', ar: 'منفذ الضغط الساكن' },
  PITOT_STATIC__pitot_tube: { en: 'Pitot tube', ar: 'أنبوب البيتو' },
  FUEL__tank_L: { en: 'Left tank', ar: 'الخزان الأيسر' },
  FUEL__tank_R: { en: 'Right tank', ar: 'الخزان الأيمن' },
  FUEL__selector_valve_body: { en: 'Fuel selector', ar: 'صمام اختيار الوقود' },
};
function catalogFor(name) {
  for (const e of CATALOG) {
    const m = name.match(e.re);
    if (m) {
      const fill = (s) => s.replace(/\{(\d)\}/g, (_, i) => m[Number(i)] ?? '');
      return { e, title: fill(tx({ en: e.en.t, ar: e.ar.t })), desc: fill(tx({ en: e.en.d, ar: e.ar.d })) };
    }
  }
  return null;
}
function buildLabels() {
  for (const [name, kind, n] of LABELS) {
    const obj = nodes.get(name);
    if (!obj) continue;
    const div = document.createElement('div');
    div.className = 'label3d' + (kind === 'cyl' ? ' cyl' : '');
    const lbl = new CSS2DObject(div);
    obj.add(lbl);
    labels.push({ lbl, div, name, kind, n });
  }
  refreshLabels();
}
function refreshLabels() {
  for (const L of labels) {
    if (L.kind === 'cyl') {
      const side = K.CYLINDERS[L.n].side < 0 ? T().bankR : T().bankL;
      L.div.textContent = `${T().cyl} ${L.n} · ${side}`;
    } else L.div.textContent = tx(LABEL_TEXT[L.name]) || catalogFor(L.name)?.title || L.name;
  }
}
function setLabelsVisible(on) {
  labelsWanted = on;
  $('labels').setAttribute('aria-pressed', String(on));
  for (const L of labels) L.lbl.visible = on && !labelsSuppressed;
}

function buildIsolate() {
  const sel = $('isolate');
  for (const g of groups.keys()) {
    const o = document.createElement('option');
    o.value = g;
    o.dataset.group = g;
    o.textContent = T().groups[g] || g;
    sel.append(o);
  }
}
function applyVisibility() {
  const iso = $('isolate').value;
  const showAirframe = $('airframe').getAttribute('aria-pressed') === 'true';
  for (const [g, node] of groups) {
    node.visible = iso ? g === iso : g !== 'AIRFRAME' || showAirframe;
  }
  for (const L of labels) {
    const g = L.name.split('__')[0];
    L.div.style.display = !iso || iso === g ? '' : 'none';
  }
}

// camera presets
let camAnim = null;
const VIEWS = {
  aircraft: () => ({ pos: [7.5, 4.2, 8.5], tgt: [0, 1.4, -1.0] }),
  engine: () => ({ pos: [1.45, 1.85, 2.35], tgt: [0, 1.12, 1.40] }),
  panel: () => ({ pos: [0.30, 1.29, 0.22], tgt: [0.30, 1.29, 0.8] }),
  fuel: () => ({ pos: [3.4, 4.1, 3.6], tgt: [0, 1.5, 0.5] }),
  electrical: () => ({ pos: [1.6, 1.9, 2.2], tgt: [0.1, 1.15, 1.05] }),
  pitot: () => ({ pos: [3.4, 2.6, 3.2], tgt: [1.0, 1.5, 0.6] }),
};
const FOCUS_VIEW = { ENGINE: 'engine', IGNITION: 'engine', INDUCTION: 'engine', FUEL: 'fuel', ELECTRICAL: 'electrical', PITOT_STATIC: 'pitot', VACUUM: 'electrical', PANEL: 'panel' };
const AIRFRAME_VIEWS = new Set(['aircraft', 'fuel', 'pitot']);
let labelsWanted = matchMedia('(min-width: 761px)').matches;
let labelsSuppressed = false;
function setView(name, instant = false) {
  const v = VIEWS[name]();
  $('airframe').setAttribute('aria-pressed', String(AIRFRAME_VIEWS.has(name)));
  labelsSuppressed = name === 'panel';
  setLabelsVisible(labelsWanted);
  applyVisibility();
  const to = { pos: new THREE.Vector3(...v.pos), tgt: new THREE.Vector3(...v.tgt) };
  if (instant) { camera.position.copy(to.pos); controls.target.copy(to.tgt); controls.update(); return; }
  camAnim = { t: 0, from: { pos: camera.position.clone(), tgt: controls.target.clone() }, to };
  for (const b of $('views').querySelectorAll('button')) b.classList.toggle('on', b.dataset.view === name);
}

// picking
let selected = null;
const savedMats = new Map();
function highlight(part, on) {
  part.traverse((o) => {
    if (!o.isMesh) return;
    if (on) {
      savedMats.set(o, o.material);
      const m = o.material.clone();
      m.emissive = new THREE.Color(0x3aa0ff);
      m.emissiveIntensity = 0.55;
      o.material = m;
    } else if (savedMats.has(o)) {
      o.material = savedMats.get(o);
      savedMats.delete(o);
    }
  });
}
const ray = new THREE.Raycaster();
let downXY = null;
renderer.domElement.addEventListener('pointerdown', (e) => { downXY = [e.clientX, e.clientY]; });
renderer.domElement.addEventListener('pointerup', (e) => {
  if (!downXY || Math.hypot(e.clientX - downXY[0], e.clientY - downXY[1]) > 5 || !model) return;
  const r = renderer.domElement.getBoundingClientRect();
  ray.setFromCamera(new THREE.Vector2(((e.clientX - r.left) / r.width) * 2 - 1, -((e.clientY - r.top) / r.height) * 2 + 1), camera);
  const visibleMeshes = [];
  model.traverseVisible((o) => { if (o.isMesh) visibleMeshes.push(o); });
  const hits = ray.intersectObjects(visibleMeshes, false);
  const hit = hits.find((h) => !(h.object.material.transparent && h.object.material.opacity < 0.25)) || hits[0];
  selectPart(hit ? partOf(hit.object) : null);
});
function selectPart(p) {
  if (selected) highlight(selected, false);
  selected = p;
  if (p) highlight(p, true);
  renderPartInfo();
}
function renderPartInfo() {
  const box = $('partInfo');
  if (!selected) { box.className = 'muted'; box.textContent = T().clickPart; return; }
  const info = catalogFor(selected.name);
  box.className = '';
  box.replaceChildren();
  const h = document.createElement('h3');
  h.style.margin = '0 0 6px';
  h.textContent = info?.title || selected.name;
  const badge = document.createElement('span');
  const status = info?.e.status || 'illustrative';
  badge.className = 'badge ' + status;
  badge.textContent = { poh: T().st_poh, type_data: T().st_type, illustrative: T().st_ill }[status];
  const p = document.createElement('p');
  p.textContent = info?.desc || '';
  const meta = document.createElement('p');
  meta.className = 'tiny mono';
  meta.textContent = `${selected.name}${info?.e.ref ? ' · ' + info.e.ref : ''}`;
  box.append(h, badge, p, meta);
}

// ===================================================================== gauges
const G = {};
function buildGauges() {
  const host = $('gauges');
  host.replaceChildren();
  const L = (k) => tx(INSTR[k]?.label) || k;
  const r0 = (v) => Math.round(v);
  G.ASI = dialGauge(host, 'ASI', INSTR.ASI, L('ASI'), (v) => `${r0(v)} kt`);
  G.AI = attitude(host, lang === 'ar' ? 'مؤشر الوضعية' : 'Attitude');
  G.ALT = altimeter(host, INSTR.ALT, L('ALT'));
  G.TC = turnCoordinator(host, lang === 'ar' ? 'منسق الانعطاف' : 'Turn coordinator');
  G.HI = heading(host, lang === 'ar' ? 'مؤشر الاتجاه' : 'Heading');
  G.VSI = dialGauge(host, 'VSI', INSTR.VSI, L('VSI'), (v) => `${Math.round(v / 10) * 10} fpm`);
  G.TACH = dialGauge(host, 'TACH', INSTR.TACH, L('TACH'), (v) => `${Math.round(v / 10) * 10}`);
  G.SUCTION = dialGauge(host, 'SUCTION', INSTR.SUCTION, L('SUCTION'), (v) => `${v.toFixed(1)}`);
  G.AMMETER = dialGauge(host, 'AMMETER', INSTR.AMMETER, L('AMMETER'), (v) => `${v >= 0 ? '+' : ''}${v.toFixed(0)} A`);
  G.OIL_P = dialGauge(host, 'OIL_P', INSTR.OIL_P, L('OIL_P'), (v) => `${r0(v)} psi`);
  G.OIL_T = dialGauge(host, 'OIL_T', INSTR.OIL_T, L('OIL_T'), (v) => `${r0(v)} °F`);
  G.FUEL_L = dialGauge(host, 'FUEL_L', INSTR.FUEL_L, L('FUEL_L'), (v) => `${v.toFixed(1)} gal`);
  G.FUEL_R = dialGauge(host, 'FUEL_R', INSTR.FUEL_R, L('FUEL_R'), (v) => `${v.toFixed(1)} gal`);
}

function updateGauges() {
  const i = sim.ind;
  G.ASI.update(i.ias);
  G.AI.update(i.aiBank, i.aiPitch);
  G.ALT.update(i.alt, sim.controls.altimeterSetting);
  G.TC.update(i.tc, i.tcFlag);
  G.HI.update(i.hi);
  G.VSI.update(i.vsi);
  G.TACH.update(i.rpm);
  G.SUCTION.update(i.suction);
  G.AMMETER.update(i.ammeter);
  G.OIL_P.update(i.oilP);
  G.OIL_T.update(i.oilT);
  G.FUEL_L.update(i.fuelL);
  G.FUEL_R.update(i.fuelR);
  $('lvLamp').classList.toggle('on', !!i.lowVoltage);
}

// ===================================================================== 3D animation from sim state
const D2R = Math.PI / 180;
const tmp = new THREE.Vector3();
function explodeAmount() { return Number($('explode').value) / 100; }
function placePart(p, x, y, z) {
  const ex = explodeAmount();
  const d = explodeDir.get(p);
  p.position.set(x + (d ? d.x * ex : 0), y + (d ? d.y * ex : 0), z + (d ? d.z * ex : 0));
}
function setNeedle(name, angleDeg) { const n = nodes.get(name); if (n) n.rotation.z = angleDeg * D2R; }

function update3D() {
  if (!model) return;
  const ex = explodeAmount();
  for (const p of parts) {
    const b = base.get(p), d = explodeDir.get(p);
    p.position.set(b.x + d.x * ex, b.y + d.y * ex, b.z + d.z * ex);
  }
  const deg = theta / D2R;
  const crank = nodes.get('ENGINE__crankshaft');
  if (crank) { const b = base.get(crank); placePart(crank, b.x, b.y, b.z); crank.rotation.z = theta; }
  const prop = nodes.get('ENGINE__propeller');
  if (prop) { const b = base.get(prop); placePart(prop, b.x, b.y, b.z); prop.rotation.z = theta; }
  const cam = nodes.get('ENGINE__camshaft');
  if (cam) { const b = base.get(cam); placePart(cam, b.x, b.y, b.z); cam.rotation.z = -theta / 2; }
  for (const c of [1, 2, 3, 4]) {
    const side = K.CYLINDERS[c].side;
    const pis = nodes.get(`ENGINE__piston_${c}`);
    if (pis) placePart(pis, ...K.pistonPosition(theta, c));
    const rod = nodes.get(`ENGINE__connecting_rod_${c}`);
    if (rod) { placePart(rod, ...K.pinPosition(theta, c)); rod.rotation.z = K.rodAngle(theta, c); }
    for (const kind of ['intake', 'exhaust']) {
      const v = nodes.get(`ENGINE__${kind}_valve_${c}`);
      if (!v) continue;
      const b = base.get(v);
      placePart(v, b.x - side * K.valveLift(deg, c, kind) * K.VALVE_LIFT, b.y, b.z);
    }
  }
  const e = sim.engine;
  const firingNow = e.running || e.cranking;
  for (const p of plugs) {
    const on = firingNow && e.magsFiring.includes(p.mag) && K.sparkActive(deg, p.cyl) && (e.running || e.cranking);
    p.mesh.material.emissive.setRGB(on ? 1 : 0, on ? 0.75 : 0, on ? 0.2 : 0);
    p.mesh.material.emissiveIntensity = on ? 3 : 0;
  }
  // panel needles (same scale data as the 2D gauges)
  const i = sim.ind;
  for (const k of ['ASI', 'VSI', 'TACH', 'SUCTION', 'AMMETER', 'OIL_P', 'OIL_T', 'FUEL_L', 'FUEL_R']) {
    const v = { ASI: i.ias, VSI: i.vsi, TACH: i.rpm, SUCTION: i.suction, AMMETER: i.ammeter, OIL_P: i.oilP, OIL_T: i.oilT, FUEL_L: i.fuelL, FUEL_R: i.fuelR }[k];
    setNeedle(`PANEL__${k}__needle`, valueToAngle(INSTR[k], v));
  }
  setNeedle('PANEL__ALT__needle_100ft', (((i.alt % 1000) + 1000) % 1000) * 0.36);
  setNeedle('PANEL__ALT__needle_1000ft', (((i.alt % 10000) + 10000) % 10000) * 0.036);
  const hor = nodes.get('PANEL__AI__horizon');
  if (hor) { hor.rotation.z = -i.aiBank * D2R; hor.position.y = -Math.max(-10, Math.min(10, i.aiPitch)) * 0.0012; }
  setNeedle('PANEL__HI__card', -i.hi);
  setNeedle('PANEL__TC__airplane', i.tc * 20);
  const c = sim.controls;
  setNeedle('PANEL__ignition_switch_key', { OFF: -60, R: -30, L: 0, BOTH: 30, START: 60 }[c.ignition]);
  const knob = (name, out) => { const n = nodes.get(name); if (n) n.position.z -= out; }; // pulled toward the pilot (-Z)
  knob('PANEL__throttle_knob', (1 - c.throttle) * 0.06);
  knob('PANEL__mixture_knob', (1 - c.mixture) * 0.06);
  knob('PANEL__carb_heat_knob', c.carbHeat * 0.05);
  knob('PANEL__alternate_static_knob', c.altStatic ? 0.035 : 0);
  const rock = (name, on) => { const n = nodes.get(name); if (n) n.rotation.x = on ? -0.35 : 0.35; };
  rock('PANEL__master_BAT', c.masterBat); rock('PANEL__master_ALT', c.masterAlt); rock('PANEL__avionics_power_switch', c.avionics);
  const sel = nodes.get('FUEL__selector_handle');
  if (sel) sel.rotation.y = { BOTH: 0, LEFT: Math.PI / 2, RIGHT: -Math.PI / 2, OFF: Math.PI }[c.fuelSelector];
  for (const [side, q] of [['L', sim.fuel.left], ['R', sim.fuel.right]]) {
    const lv = nodes.get(`FUEL__fuel_level_${side}`);
    if (lv) lv.scale.y = Math.max(0.01, q / POH.fuelPerTankTotal);
  }
  const lamp = nodes.get('PANEL__LOW_VOLTAGE_light');
  if (lamp?.material) { lamp.material.emissive.setRGB(i.lowVoltage ? 1 : 0, 0, 0); lamp.material.emissiveIntensity = i.lowVoltage ? 2.5 : 0; }
}

// ===================================================================== status / cycle table
function renderStatus() {
  const e = sim.engine, el = sim.elec, t = T();
  const state = e.running ? t.running : e.cranking ? t.cranking : t.stopped;
  const cells = [
    [t.engine, state], [t.rpm, Math.round(e.rpm)], [t.fuelFlow, `${e.fuelFlowGph.toFixed(1)} ${t.gph}`],
    [t.bus, `${el.busVolts.toFixed(1)} V`], [t.battery, `${Math.round(el.soc * 100)}%`],
    [t.magsFiring, e.magsFiring.join(' + ') || t.none], [t.iceLevel, `${Math.round(e.ice * 100)}%`],
  ];
  const box = $('status');
  if (box.children.length !== cells.length) box.replaceChildren(...cells.map(() => { const d = document.createElement('div'); d.innerHTML = '<small></small><b></b>'; return d; }));
  cells.forEach(([k, v], idx) => { box.children[idx].firstChild.textContent = k; box.children[idx].lastChild.textContent = v; });
  const ann = annunciations(sim);
  const ab = $('annunciators');
  const html = ann.map((a) => t.ann[a] || a);
  if (ab.dataset.v !== html.join('|')) {
    ab.dataset.v = html.join('|');
    ab.replaceChildren(...html.map((s) => Object.assign(document.createElement('span'), { textContent: s })));
  }
  const ev = sim.events.slice(-3).map((x) => `${t.ev[x.type] || x.type}`).join(' · ');
  if ($('events').textContent !== ev) $('events').textContent = ev;

  const deg = ((theta / D2R) % 720 + 720) % 720;
  const rows = [1, 3, 2, 4].map((c) => {
    const st = K.strokeOf(deg, c);
    const spark = (e.running || e.cranking) && K.sparkActive(deg, c);
    return `<tr><td>${t.cyl} ${c}</td><td>${K.CYLINDERS[c].side < 0 ? t.bankR : t.bankL}</td><td class="st-${st}">${t.strokes[st]}</td><td class="spark">${spark ? '⚡ ' + t.fires : ''}</td></tr>`;
  }).join('');
  $('cycle').innerHTML = `<tbody>${rows}</tbody>`;
  $('crankOut').textContent = `${Math.round(deg)}°`;
}

// ===================================================================== controls wiring
const C = () => sim.controls;
function bindToggle(id, get, set) {
  const b = $(id);
  b.addEventListener('click', () => { set(!get()); syncUI(); });
}
bindToggle('masterBat', () => C().masterBat, (v) => (C().masterBat = v));
bindToggle('masterAlt', () => C().masterAlt, (v) => (C().masterAlt = v));
bindToggle('avionics', () => C().avionics, (v) => (C().avionics = v));
for (const k of ['altStatic', 'pitotHeat', 'beacon', 'navLights', 'landingLight']) bindToggle(k, () => C()[k], (v) => (C()[k] = v));
function bindSeg(id, key) {
  $(id).addEventListener('click', (e) => { const v = e.target.closest('button')?.dataset.v; if (v) { C()[key] = v; syncUI(); } });
}
bindSeg('ignition', 'ignition');
bindSeg('fuelSelector', 'fuelSelector');
const startBtn = $('startBtn');
const startOn = (e) => { e.preventDefault(); C().ignition = 'START'; startBtn.classList.add('active'); syncUI(); };
const startOff = () => { if (C().ignition === 'START') { C().ignition = 'BOTH'; startBtn.classList.remove('active'); syncUI(); } };
startBtn.addEventListener('pointerdown', startOn);
for (const ev of ['pointerup', 'pointerleave', 'pointercancel', 'blur']) startBtn.addEventListener(ev, startOff);
startBtn.addEventListener('keydown', (e) => { if (e.key === ' ' || e.key === 'Enter') startOn(e); });
startBtn.addEventListener('keyup', startOff);
$('primer').addEventListener('click', () => { C().primeStrokes += 1; ctx.primes = (ctx.primes || 0) + 1; syncUI(); });
for (const k of ['throttle', 'mixture', 'carbHeat']) $(k).addEventListener('input', () => { C()[k] = Number($(k).value) / 100; syncUI(); });
$('kollsman').addEventListener('input', () => { C().altimeterSetting = Number($('kollsman').value) / 100; syncUI(); });
$('onGround').addEventListener('change', () => { sim.flight.onGround = $('onGround').checked; syncUI(); });
for (const [id, key] of [['iasTarget', 'iasTarget'], ['altTarget', 'altTarget'], ['bank', 'bank'], ['pitch', 'pitch']]) {
  $(id).addEventListener('input', () => { sim.flight[key] = Number($(id).value); syncUI(); });
}
$('timeScale').addEventListener('change', () => (timeScale = Number($('timeScale').value)));
$('pause').addEventListener('click', () => { paused = !paused; $('pause').dataset.i18n = paused ? 'resume' : 'pause'; $('pause').textContent = T()[paused ? 'resume' : 'pause']; });
$('reset').addEventListener('click', () => { scenario = null; ctx = {}; sim = createState(); $('scenarioSel').value = ''; renderScenario(); syncUI(); });
$('f_pitot').addEventListener('change', () => (sim.faults.pitot = $('f_pitot').value));
$('f_static').addEventListener('change', () => (sim.faults.staticBlocked = $('f_static').checked));
$('f_alt').addEventListener('change', () => (sim.faults.alternator = $('f_alt').value));
$('f_vac').addEventListener('change', () => (sim.faults.vacuum = $('f_vac').checked));
$('f_ice').addEventListener('change', () => (sim.faults.carbIce = $('f_ice').checked));
$('f_magL').addEventListener('change', () => (sim.faults.magneto.L = $('f_magL').value));
$('f_magR').addEventListener('change', () => (sim.faults.magneto.R = $('f_magR').value));
$('f_fuelL').addEventListener('input', () => { sim.fuel.left = Number($('f_fuelL').value) / 10; syncUI(); });
$('f_fuelR').addEventListener('input', () => { sim.fuel.right = Number($('f_fuelR').value) / 10; syncUI(); });

$('views').addEventListener('click', (e) => { const v = e.target.closest('button')?.dataset.view; if (v) setView(v); });
$('xray').addEventListener('click', () => { const on = $('xray').getAttribute('aria-pressed') !== 'true'; $('xray').setAttribute('aria-pressed', on); applyXray(on); });
$('labels').addEventListener('click', () => setLabelsVisible(!labelsWanted));
$('airframe').addEventListener('click', () => { const on = $('airframe').getAttribute('aria-pressed') !== 'true'; $('airframe').setAttribute('aria-pressed', on); applyVisibility(); });
$('isolate').addEventListener('change', applyVisibility);
$('animSpeed').addEventListener('change', () => (animSpeed = Number($('animSpeed').value)));
$('crank').addEventListener('input', () => { if (sim.engine.rpm < 1) theta = Number($('crank').value) * D2R; });

function syncUI() {
  const c = C(), f = sim.flight, t = T();
  for (const k of ['masterBat', 'masterAlt', 'avionics', 'altStatic', 'pitotHeat', 'beacon', 'navLights', 'landingLight']) $(k).setAttribute('aria-pressed', String(!!c[k]));
  $('avionics').textContent = c.avionics ? 'ON' : 'OFF';
  for (const b of $('ignition').querySelectorAll('button')) b.setAttribute('aria-checked', String(b.dataset.v === c.ignition));
  for (const b of $('fuelSelector').querySelectorAll('button')) b.setAttribute('aria-checked', String(b.dataset.v === c.fuelSelector));
  for (const k of ['throttle', 'mixture', 'carbHeat']) { $(k).value = Math.round(c[k] * 100); $(k + 'Out').textContent = `${Math.round(c[k] * 100)}%`; }
  $('mixtureOut').textContent = c.mixture >= 0.97 ? 'RICH' : c.mixture < 0.08 ? 'IDLE CUT-OFF' : `${Math.round(c.mixture * 100)}%`;
  $('primeCount').textContent = ctx.primes || 0;
  $('kollsman').value = Math.round(c.altimeterSetting * 100);
  $('kollsmanOut').textContent = `${c.altimeterSetting.toFixed(2)} inHg`;
  $('onGround').checked = f.onGround;
  $('iasTarget').value = f.iasTarget; $('iasOut').textContent = `${f.iasTarget} kt`;
  $('altTarget').value = f.altTarget; $('altOut').textContent = `${f.altTarget} ft`;
  $('bank').value = f.bank; $('bankOut').textContent = `${Math.round(f.bank)}°`;
  $('pitch').value = f.pitch; $('pitchOut').textContent = `${Math.round(f.pitch)}°`;
  const fl = sim.faults;
  $('f_pitot').value = fl.pitot; $('f_static').checked = fl.staticBlocked; $('f_alt').value = fl.alternator;
  $('f_vac').checked = fl.vacuum; $('f_ice').checked = fl.carbIce; $('f_magL').value = fl.magneto.L; $('f_magR').value = fl.magneto.R;
  $('f_fuelL').value = Math.round(sim.fuel.left * 10); $('fuelLOut').textContent = `${sim.fuel.left.toFixed(1)} ${t.gal}`;
  $('f_fuelR').value = Math.round(sim.fuel.right * 10); $('fuelROut').textContent = `${sim.fuel.right.toFixed(1)} ${t.gal}`;
  $('crank').disabled = sim.engine.rpm >= 1;
}

// ===================================================================== scenarios
function buildScenarioSelect() {
  const sel = $('scenarioSel');
  const cur = sel.value;
  sel.replaceChildren();
  const free = document.createElement('option');
  free.value = '';
  free.textContent = T().freePlay;
  sel.append(free);
  for (const s of SCENARIOS) {
    const o = document.createElement('option');
    o.value = s.id;
    o.textContent = `${tx(s.title)} · ${s.poh}`;
    sel.append(o);
  }
  sel.value = cur;
}
function startScenario(id) {
  scenario = SCENARIOS.find((s) => s.id === id) || null;
  ctx = { done: [] };
  sim = createState(scenario ? structuredClone(scenario.setup) : {});
  theta = 0;
  if (scenario) {
    $('isolate').value = '';
    applyVisibility();
    setView(FOCUS_VIEW[scenario.focus] || 'aircraft');
  }
  renderScenario();
  syncUI();
}
let lastStepIdx = -1;
function renderScenario() {
  const body = $('scenarioBody');
  const t = T();
  body.replaceChildren();
  if (!scenario) { lastStepIdx = -1; return; }
  const brief = document.createElement('div');
  brief.className = 'brief';
  brief.innerHTML = `<b>${t.briefing}</b> · <span class="mono">${scenario.poh}</span><br>`;
  brief.append(tx(scenario.brief));
  const ol = document.createElement('ol');
  ol.className = 'steps';
  ol.setAttribute('aria-live', 'polite');
  const cur = evaluateSteps(scenario, sim, ctx);
  lastStepIdx = cur;
  scenario.steps.forEach((st, i) => {
    const li = document.createElement('li');
    li.textContent = tx(st);
    if (ctx.done[i]) li.className = 'done';
    else if (i === cur) {
      li.className = 'cur';
      if (st.ack) {
        const b = document.createElement('button');
        b.className = 'btn'; b.type = 'button'; b.textContent = t.ack;
        b.onclick = () => { ctx.done[i] = true; renderScenario(); };
        li.append(b);
      }
      if (st.choice) {
        const wrap = document.createElement('div');
        wrap.className = 'choices';
        st.options.forEach((o, k) => {
          const b = document.createElement('button');
          b.className = 'btn'; b.type = 'button'; b.textContent = tx(o);
          b.onclick = () => { if (k === st.answer) { ctx.done[i] = true; renderScenario(); } else { b.disabled = true; b.textContent += ' ✗'; } };
          wrap.append(b);
        });
        li.append(wrap);
      }
    }
    ol.append(li);
  });
  body.append(brief, ol);
  if (ctx.mag) {
    const m = ctx.mag;
    const box = document.createElement('div');
    box.className = 'magres';
    box.innerHTML = `<b>${t.magResult}</b><br>${t.dropR}: ${Math.round(m.dropR)} · ${t.dropL}: ${Math.round(m.dropL)} · ${t.diff}: ${Math.round(m.diff)}<br><span class="${m.pass ? 'good' : 'badtxt'}">${m.pass ? t.pass : t.fail}</span> <span class="tiny">(≤${POH.magDropMax} / ≤${POH.magDiffMax} RPM, POH 4-7)</span>`;
    body.append(box);
  }
  if (cur >= scenario.steps.length) {
    const d = document.createElement('div');
    d.className = 'debrief';
    d.innerHTML = `<b>✓ ${t.completed} — ${t.debrief}</b><br>`;
    d.append(tx(scenario.debrief));
    body.append(d);
    if (scenario.quiz) {
      const q = document.createElement('div');
      q.className = 'brief';
      q.innerHTML = `<b>${t.quiz}</b> <span class="tiny mono">${scenario.quiz.ref || ''}</span><br>`;
      q.append(tx(scenario.quiz.q));
      const wrap = document.createElement('div');
      wrap.className = 'choices';
      const fb = document.createElement('p');
      fb.setAttribute('aria-live', 'polite');
      scenario.quiz.options.forEach((o, k) => {
        const b = document.createElement('button');
        b.className = 'btn'; b.type = 'button'; b.textContent = tx(o);
        b.onclick = () => { fb.textContent = k === scenario.quiz.answer ? t.correct : t.wrong; fb.className = k === scenario.quiz.answer ? 'good' : 'badtxt'; };
        wrap.append(b);
      });
      q.append(wrap, fb);
      body.append(q);
    }
  }
}
$('scenarioStart').addEventListener('click', () => startScenario($('scenarioSel').value));

// ===================================================================== language
function applyLang() {
  const t = T();
  document.documentElement.lang = t.lang;
  document.documentElement.dir = t.dir;
  $('lang').textContent = t.other;
  for (const n of document.querySelectorAll('[data-i18n]')) { const v = t[n.dataset.i18n]; if (typeof v === 'string') n.textContent = v; }
  for (const o of $('isolate').querySelectorAll('option[data-group]')) o.textContent = t.groups[o.dataset.group];
  $('legend').innerHTML = `<b>${t.legend}:</b>` + [['--fuel', t.lg_fuel], ['--oil', t.lg_oil], ['--elec', t.lg_elec], ['--vac', t.lg_vac], ['--pitot', t.lg_pitot], ['--static', t.lg_static], ['--ign', t.lg_ign]]
    .map(([c, n]) => `<span><i style="background:var(${c})"></i>${n}</span>`).join('');
  buildScenarioSelect();
  buildGauges();
  updateGauges();
  renderScenario();
  renderPartInfo();
  refreshLabels();
  syncUI();
}
$('lang').addEventListener('click', () => { lang = lang === 'ar' ? 'en' : 'ar'; store.set('c172.lang', lang); applyLang(); });

// ===================================================================== main loop
const clock = new THREE.Clock();
let uiTimer = 0;
function frame() {
  requestAnimationFrame(frame);
  const dt = Math.min(clock.getDelta(), 0.1);
  if (!paused) {
    const sdt = dt * timeScale;
    step(sim, sdt);
    if (scenario) {
      scenario.tick?.(sim, ctx, sdt);
      const idx = evaluateSteps(scenario, sim, ctx);
      if (idx !== lastStepIdx || (ctx.mag && !document.querySelector('.magres'))) renderScenario();
    }
    if (sim.engine.rpm >= 1) {
      theta += (sim.engine.rpm / 60) * 2 * Math.PI * animSpeed * dt;
      theta %= 4 * Math.PI;
      $('crank').value = Math.round(((theta / D2R) % 720 + 720) % 720);
    }
  }
  if (camAnim) {
    camAnim.t = Math.min(1, camAnim.t + dt / 0.8);
    const k = 1 - Math.pow(1 - camAnim.t, 3);
    camera.position.lerpVectors(camAnim.from.pos, camAnim.to.pos, k);
    controls.target.lerpVectors(camAnim.from.tgt, camAnim.to.tgt, k);
    if (camAnim.t >= 1) camAnim = null;
  }
  update3D();
  uiTimer += dt;
  if (uiTimer > 1 / 30) {
    uiTimer = 0;
    updateGauges();
    renderStatus();
    if (!document.activeElement || !document.activeElement.matches('input[type=range]')) syncUI();
  }
  controls.update();
  renderer.render(scene, camera);
  labelRenderer.render(scene, camera);
}

// test / automation hook (used by the Playwright smoke test)
window.__twin = {
  ready: false,
  get sim() { return sim; },
  get ctx() { return ctx; },
  get theta() { return theta; },
  nodes, startScenario, setView, selectPart: (name) => selectPart(nodes.get(name) || null),
  pistonX: (c) => nodes.get(`ENGINE__piston_${c}`)?.position.x,
  partPos: (name) => nodes.get(name)?.position.toArray(),
};

applyLang();
setLabelsVisible(labelsWanted);
applyVisibility();
frame();
