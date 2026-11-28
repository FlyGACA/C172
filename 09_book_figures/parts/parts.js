// The parts catalogue: the list, the search and the three views of a part (on its own, in the
// aircraft, in 3D). Everything shown is read from parts.json, which build.py writes. A part and its view have
// an address of their own, and so has the list (a search, a system, a source): link.js reads and writes them, and the
// page keeps the address up to date as the reader moves.
import { SOURCES, buildLink, indexParts, linkPairs, listPairs, parseLink, parseList, parsePose, posePairs } from './link.js';
import { ORDER, SOURCE_NAMES, systemName } from './names.js';
import { haystack, matches, words } from './search.js';
import { CHALLENGES, effectOf, judge, nextChallenge } from './trainer.js';
import { ROUND, makeRound, summarize } from './quiz.js';
import * as offline from './offline.js';
import { ABOUT_PARENT_Z, CONTROLS, GLOWING, GROUPS, MOVING, SCENES, STROKE_NAMES, isLit, pose, rest, setScales, strokes } from './motions.js';
const $ = (id) => document.getElementById(id);
const el = (tag, cls, text) => { const e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; };
/** A phrase in both languages; the page's language switch shows one. */
const both = (en, ar) => { const f = document.createDocumentFragment(); const a = el('span', 'ufuq-ar', ar); a.lang = 'ar'; f.append(el('span', 'ufuq-en', en), a); return f; };
const say = (node, en, ar) => node.replaceChildren(both(en, ar));

let D;
try { D = await (await fetch('parts.json')).json(); } catch { say($('list').firstElementChild, 'The parts list could not be loaded. Reload the page to try again.', 'تعذّر تحميل قائمة القطع. أعد تحميل الصفحة.'); throw new Error('parts.json'); }
const P = D.parts;
P.forEach((p, i) => { p.i = i; p.h = haystack(p); });
const present = new Set(P.map((p) => p.s));
const systems = [...ORDER.filter((s) => present.has(s)), ...[...present].filter((s) => !ORDER.includes(s)).sort()];
const rank = new Map(systems.map((s, i) => [s, i]));
let shown = P, cur = 0, view = 'alone', keepCamera = false;

/** Show tile `index` of a sheet of pictures as the background of `node`. */
function tile(node, sheet, index) {
  const file = sheet.files[Math.floor(index / sheet.per)], n = index % sheet.per, c = n % sheet.cols, r = Math.floor(n / sheet.cols);
  node.style.backgroundImage = `url("${file.f}")`;
  node.style.backgroundSize = `${sheet.cols * 100}% ${file.rows * 100}%`;
  node.style.backgroundPosition = `${sheet.cols > 1 ? (c / (sheet.cols - 1)) * 100 : 0}% ${file.rows > 1 ? (r / (file.rows - 1)) * 100 : 0}%`;
}
const seen = new IntersectionObserver((entries) => entries.forEach((e) => { if (e.isIntersecting) { tile(e.target.firstChild, D.thumb, +e.target.dataset.i); seen.unobserve(e.target); } }), { rootMargin: '600px' });

/** How well a part is sourced, as a badge with its name in both languages and what it means as its tooltip. */
function status(st) {
  const n = SOURCE_NAMES[st] || { en: st, ar: st, note: { en: '', ar: '' } }, badge = el('span', `parts-st ${st}`);
  badge.append(both(n.en, n.ar)); badge.title = `${n.note.en} · ${n.note.ar}`; return badge;
}
const count = (key, value) => P.filter((p) => p[key] === value).length;
const names = (n) => `${n.en} · ${n.ar}`;
function option(select, value, text) { const o = el('option', null, text); o.value = value; select.append(o); }
option($('fsys'), '', `All systems · كل الأنظمة (${P.length})`);
for (const s of systems) option($('fsys'), s, `${names(systemName(s))} (${count('s', s)})`);
option($('fsrc'), '', `Any source · أي مصدر (${P.length})`);
for (const s of SOURCES) option($('fsrc'), s, `${names(SOURCE_NAMES[s])} (${count('st', s)})`);
for (const s of SOURCES) { const li = el('li'), n = SOURCE_NAMES[s]; li.append(status(s), ' ', both(n.note.en, n.note.ar)); $('key-list').append(li); }

const filters = () => ({ q: $('q').value, system: $('fsys').value, source: $('fsrc').value });
function setFilters({ q = '', system = '', source = '' }) { $('q').value = q; $('fsys').value = system; $('fsrc').value = source; }
function clearFilters() { setFilters({}); render(); }

function render() {
  const f = filters(), ws = words(f.q);
  shown = P.filter((p) => (!f.system || p.s === f.system) && (!f.source || p.st === f.source) && matches(p.h, ws)).sort((a, b) => rank.get(a.s) - rank.get(b.s) || a.i - b.i);
  $('fclear').hidden = !(f.q.trim() || f.system || f.source);
  say($('count'), `${shown.length} of ${P.length} parts`, `${shown.length} من ${P.length} قطعة`);
  seen.disconnect(); sync();
  if (!shown.length) {
    const none = el('div', 'parts-empty'), m = el('p'), b = el('button', 'ufuq-btn ufuq-btn--secondary');
    say(m, 'No part matches. Try fewer words, or clear the filters.', 'لا توجد قطعة مطابقة. جرّب كلمات أقل أو امسح التصفية.');
    b.type = 'button'; b.append(both('Clear filters', 'امسح التصفية')); b.onclick = clearFilters; none.append(m, b); $('list').replaceChildren(none); return;
  }
  const per = new Map(); for (const p of shown) per.set(p.s, (per.get(p.s) || 0) + 1);
  const frag = document.createDocumentFragment(); let system = null, grid = null;
  shown.forEach((p, n) => {
    if (p.s !== system) {
      system = p.s; const s = el('section'), h = el('h2'), nm = systemName(system), small = el('small');
      say(small, `${per.get(system)} parts`, `${per.get(system)} قطعة`); h.append(both(nm.en, nm.ar), small); grid = el('div', 'parts-grid'); s.append(h, grid); frag.append(s);
    }
    const b = el('button', 'parts-tile'); b.type = 'button'; b.dataset.i = p.i; b.title = `${p.en} · ${p.ar}`;
    const cap = el('div', 'parts-cap'), en = el('span', 'parts-name', p.en), ar = el('span', 'parts-name parts-ar', p.ar);
    en.lang = 'en'; en.dir = 'ltr'; ar.lang = 'ar'; ar.dir = 'rtl';
    cap.append(en, ar, status(p.st)); b.append(el('div', 'parts-pic'), cap); b.onclick = () => open(n); grid.append(b); seen.observe(b);
  });
  $('list').replaceChildren(frag);
}

function open(n) {
  cur = (n + shown.length) % shown.length; const p = shown[cur];
  $('d-en').textContent = p.en; $('d-ar').textContent = p.ar; $('d-id').textContent = p.id;
  { const badge = status(p.st); $('d-st').className = badge.className; $('d-st').title = badge.title; $('d-st').replaceChildren(...badge.childNodes); }
  const more = $('d-more'); more.hidden = !p.more.length;
  more.replaceChildren(...p.more.map((m) => { const li = el('li'); say(li, `Also drawn: ${m[1]}`, `مرسومة معها: ${m[2]}`); return li; }));
  if (!$('dlg').open) $('dlg').showModal();
  show();
}
function show() {
  const p = shown[cur], is3d = view === '3d';
  document.querySelectorAll('[data-view]').forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.view === view)));
  $('d-3d').hidden = !is3d; $('around').hidden = $('bfit').hidden = $('moves3d').hidden = $('setting').hidden = !is3d; $('setting').value = settingFor();
  if (!is3d) { $('bsolid').hidden = $('hide').hidden = $('pull').hidden = $('slides').hidden = true; $('dlg').classList.remove('is-wide'); }
  tile($('d-pic'), view === 'place' ? D.place : D.large, p.i);
  $('d-full').href = `full/${view === 'place' ? 'place' : 'alone'}/${p.k}.png`; $('d-full').hidden = is3d;
  const keep = keepCamera; keepCamera = false;
  if (is3d) show3d(keep); else { turn += 1; message(); }
  sync();
}
document.querySelectorAll('[data-view]').forEach((b) => { b.onclick = () => { view = b.dataset.view; show(); }; });
$('prev').onclick = () => open(cur - 1); $('next').onclick = () => open(cur + 1); $('close').onclick = () => $('dlg').close();
$('dlg').addEventListener('click', (e) => { if (e.target === $('dlg')) $('dlg').close(); });
const rtl = () => getComputedStyle(document.documentElement).direction === 'rtl';
$('dlg').addEventListener('keydown', (e) => {
  if (e.target.matches('input[type=range], select') || e.altKey || e.ctrlKey || e.metaKey) return;
  const next = rtl() ? 'ArrowLeft' : 'ArrowRight', back = rtl() ? 'ArrowRight' : 'ArrowLeft';
  if (e.key === next) open(cur + 1); else if (e.key === back) open(cur - 1);
});
// A swipe over the picture goes to the next or the previous part: toward the reader's past is back, as with a page.
{
  let from = null;
  $('d-pic').addEventListener('touchstart', (e) => { from = view !== '3d' && e.touches.length === 1 ? [e.touches[0].clientX, e.touches[0].clientY] : null; }, { passive: true });
  $('d-pic').addEventListener('touchend', (e) => {
    if (!from) return; const t = e.changedTouches[0], dx = t.clientX - from[0], dy = t.clientY - from[1]; from = null;
    if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy) * 1.5) open(cur + ((dx < 0) !== rtl() ? 1 : -1));
  }, { passive: true });
}
let timer; $('q').addEventListener('input', () => { clearTimeout(timer); timer = setTimeout(render, 120); });
$('fsys').addEventListener('change', render); $('fsrc').addEventListener('change', render); $('fclear').onclick = clearFilters;
addEventListener('keydown', (e) => { if (e.key === '/' && !e.ctrlKey && !e.metaKey && !e.altKey && !$('dlg').open && !e.target.matches('input, textarea, select')) { e.preventDefault(); $('q').focus(); $('q').select(); } });

// The address of what is open. It is written as the reader moves, with no step added to the browser's history, and
// taken away when the part is closed.
const here = () => location.href.split(/[?#]/)[0];
const open_ = () => ($('dlg').open && shown[cur]) ? { part: shown[cur].id, view, scope } : null;
function sync() {
  try {
    const url = new URL(location.href), now = open_();
    for (const k of ['part', 'view', 'scope', 'q', 'system', 'source', 'pose', 'moved']) url.searchParams.delete(k);
    for (const [k, v] of [...listPairs(filters()), ...(now ? [...linkPairs(now), ...posePairsNow()] : [])]) url.searchParams.set(k, v);
    history.replaceState(null, '', url.pathname + url.search + url.hash);
  } catch { /* an address that cannot be changed, such as a file opened from disk, is left as it is */ }
}
$('dlg').addEventListener('close', sync);
$('blink').onclick = async () => {
  const now = open_(); if (!now) return;
  const link = buildLink(here(), now, posePairsNow());
  try { await navigator.clipboard.writeText(link); say($('blink-msg'), 'Link copied', 'تم نسخ الرابط'); }
  catch { window.prompt('Link · الرابط', link); say($('blink-msg'), '', ''); }
  setTimeout(() => $('blink-msg').replaceChildren(), 2500);
};

// The 3D view. Three.js and one model file per system (m/<SYSTEM>.glb) are fetched the first time they are asked for.
// Round the chosen part it can draw nothing, the rest of its system, or the whole aircraft; in the whole aircraft a
// click on any part chooses it, and whole systems can be put away to see what is under them. With anything round it,
// the parts can be pulled apart: each moves straight out from the middle of what is shown, by the same proportion.
let T = null, ready = null, turn = 0, scope = 'part', solid = false, quiet = false, pull = 0, moving = false, deep = false;
const models = {}, hidden = new Set(), ctl = rest(), shifted = new Map();   // shifted: piece -> how far the reader has dragged it
const entry = indexParts(P);
function message(en, ar) { $('d-msg').hidden = !en; if (en) say($('d-msg'), en, ar); }
function setup() {
  ready ||= (async () => {
    const THREE = await import('three');
    const [{ GLTFLoader }, { OrbitControls }, { RoomEnvironment }] = await Promise.all([import('three/addons/loaders/GLTFLoader.js'), import('three/addons/controls/OrbitControls.js'), import('three/addons/environments/RoomEnvironment.js')]);
    const canvas = $('d-3d'), renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
    renderer.setPixelRatio(Math.min(devicePixelRatio || 1, 2)); renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    const scene = new THREE.Scene(); scene.environment = new THREE.PMREMGenerator(renderer).fromScene(new RoomEnvironment(), 0.04).texture;
    const camera = new THREE.PerspectiveCamera(24, 1.6, 0.01, 100), sun = new THREE.DirectionalLight(0xffffff, 1.2);
    camera.add(sun); sun.position.set(1, 2, 1); scene.add(camera);
    const controls = new OrbitControls(camera, canvas);
    const token = (name) => getComputedStyle(canvas).getPropertyValue(name).trim() || 'gray';
    const faint = new THREE.MeshBasicMaterial({ color: token('--ufuq-print-teal'), transparent: true, opacity: 0.06, depthWrite: false });
    const marked = new THREE.MeshStandardMaterial({ color: token('--ufuq-print-clay'), roughness: 0.55, metalness: 0, emissive: token('--ufuq-print-clay'), emissiveIntensity: 0.35 });
    const frame = () => {
      const w = canvas.clientWidth, h = canvas.clientHeight; if (!w || !h) return;
      const k = renderer.getPixelRatio();
      if (canvas.width !== Math.round(w * k) || canvas.height !== Math.round(h * k)) { renderer.setSize(w, h, false); camera.aspect = w / h; camera.updateProjectionMatrix(); }
      renderer.render(scene, camera);
    };
    const draw = () => requestAnimationFrame(frame);
    controls.addEventListener('change', draw); new ResizeObserver(draw).observe(canvas);
    T = { THREE, GLTFLoader, scene, camera, controls, faint, marked, draw, renderer, headlight: sun, roomEnv: scene.environment, shown: 'plain', roots: new Map(), ray: new THREE.Raycaster() };
    // A click that is not a drag chooses the part under it.
    let down = null;
    canvas.addEventListener('pointerdown', (e) => { down = [e.clientX, e.clientY]; });
    canvas.addEventListener('pointerup', (e) => { if (down && Math.hypot(e.clientX - down[0], e.clientY - down[1]) < 5) pick(e); down = null; });
    // With "Drag a part" on, a drag that starts on a part moves that part in the plane facing the reader (or, with "Drag in
    // depth", in the plane that holds the line of sight); a drag that starts on empty space still turns the view.
    let grab = null;
    canvas.addEventListener('pointerdown', (e) => {
      if (!moving) return;
      const hit = rayHit(e); if (!hit) return;
      const view = camera.getWorldDirection(new THREE.Vector3()), plane = new THREE.Plane();
      plane.setFromNormalAndCoplanarPoint(deep ? new THREE.Vector3().crossVectors(view, camera.up).normalize() : view.negate(), hit.point);
      grab = { piece: hit.object.userData.piece, plane, last: hit.point.clone() };
      controls.enabled = false; canvas.setPointerCapture(e.pointerId);
    }, true);
    canvas.addEventListener('pointermove', (e) => {
      if (!grab) return;
      aim(e); const at = T.ray.ray.intersectPlane(grab.plane, new THREE.Vector3()); if (!at) return;
      const was = shifted.get(grab.piece) || [0, 0, 0], d = at.clone().sub(grab.last); shifted.set(grab.piece, [was[0] + d.x, was[1] + d.y, was[2] + d.z]); grab.last.copy(at);
      paint(); $('bback').hidden = false;
    });
    const drop = () => { if (grab) { grab = null; controls.enabled = true; sync(); } };
    canvas.addEventListener('pointerup', drop); canvas.addEventListener('pointercancel', drop);
  })();
  return ready;
}
/** The meshes of one system, each marked with the catalogue part it belongs to, flat under one group in the scene. */
function model(system) {
  models[system] ||= new T.GLTFLoader().loadAsync(`m/${system}.glb`).then((gltf) => {
    const { THREE } = T, ids = {};
    for (const p of P) if (p.s === system) for (const id of [p.id, ...p.more.map((m) => m[0])]) ids[THREE.PropertyBinding.sanitizeNodeName(id)] = id;
    gltf.scene.updateMatrixWorld(true);
    const meshes = []; gltf.scene.traverse((o) => { if (o.isMesh) meshes.push(o); });
    // The hinge or axis of every part that moves, in the aircraft's own frame, taken before the meshes are flattened: a mesh
    // keeps the list of the moving parts it hangs from, the nearest first.
    const AXES = { x: new THREE.Vector3(1, 0, 0), y: new THREE.Vector3(0, 1, 0), z: new THREE.Vector3(0, 0, 1) }, wq = new THREE.Quaternion();
    const joint = (o) => {
      const u = o.userData, id = u.id, at = o.getWorldPosition(new THREE.Vector3()), q = o.getWorldQuaternion(new THREE.Quaternion());
      const parent = o.parent ? o.parent.getWorldQuaternion(wq).clone() : new THREE.Quaternion();
      if (ABOUT_PARENT_Z(id)) return { id, kind: 'spin', at, axis: AXES.z.clone().applyQuaternion(parent), sign: 1, parent };
      if (u.hinge_axis) return { id, kind: 'hinge', at, axis: AXES[u.hinge_axis].clone().applyQuaternion(q), sign: u.hinge_sign || 1, parent };
      if (u.spin_axis) return { id, kind: 'spin', at, axis: AXES[u.spin_axis].clone().applyQuaternion(q), sign: u.spin_sign || 1, parent };
      return { id, kind: 'move', parent };
    };
    const joints = new Map(); gltf.scene.traverse((o) => { if (o.userData.id && MOVING.has(o.userData.id)) joints.set(o, joint(o)); });
    for (const m of meshes) { m.userData.joints = []; m.userData.lamp = null; for (let a = m; a; a = a.parent) { if (joints.has(a)) m.userData.joints.push(joints.get(a)); if (!m.userData.lamp && GLOWING.has(a.userData.id)) m.userData.lamp = a.userData.id; } }
    for (const m of meshes) { m.castShadow = true; m.receiveShadow = true; }
    for (const m of meshes) { let a = m, id = null; while (a && !id) { id = ids[a.name] || null; a = a.parent; } m.userData.part = id; m.userData.material = m.material; m.visible = false; }
    const root = new THREE.Group(); for (const m of meshes) root.attach(m);
    root.updateMatrixWorld(true);
    for (const m of meshes) m.userData.homeQ = m.quaternion.clone();   // after the flattening: now a world orientation
    // Where each mesh sits, and the middle of the catalogue entry it is drawn with: what is pulled apart moves as one piece.
    const boxes = new Map();
    for (const m of meshes) { const key = entry.get(m.userData.part)?.id ?? m.uuid; if (!boxes.has(key)) boxes.set(key, new THREE.Box3()); boxes.get(key).expandByObject(m); m.userData.piece = key; m.userData.home = m.position.clone(); }
    const middles = new Map([...boxes].map(([key, box]) => [key, box.getCenter(new THREE.Vector3())]));
    for (const m of meshes) m.userData.middle = middles.get(m.userData.piece);
    T.roots.set(system, root); T.scene.add(root);
    return root;
  });
  return models[system];
}
const meshes = function* () { for (const [system, root] of T.roots) for (const m of root.children) yield [system, m]; };
function fit(all) {
  const { THREE, camera, controls } = T, box = new THREE.Box3();
  for (const [system, m] of meshes()) if (all ? m.visible && system !== 'GROUND_EQUIPMENT' : m.userData.chosen) box.expandByObject(m);
  if (box.isEmpty()) return;
  const s = box.getBoundingSphere(new THREE.Sphere()), R = Math.max(s.radius, 1e-4), d = (R / Math.sin(THREE.MathUtils.degToRad(12))) * (all && scope === 'aircraft' ? 0.6 : 1.08), az = THREE.MathUtils.degToRad(35), el = THREE.MathUtils.degToRad(T.shown === 'airfield' && scope === 'aircraft' ? 5 : 22);   // on the airfield the camera sits low enough to show the horizon and the sky
  controls.target.copy(s.center); camera.position.set(s.center.x + d * Math.cos(el) * Math.sin(az), s.center.y + d * Math.sin(el), s.center.z + d * Math.cos(el) * Math.cos(az));
  camera.near = all ? 0.02 : Math.max(R / 200, 1e-4); camera.far = d + R * 400 + 50; camera.updateProjectionMatrix();
  controls.minDistance = all ? 0.05 : R * 0.3; controls.maxDistance = d * 30 + 20; if (T.shown === 'hangar') controls.maxDistance = Math.min(controls.maxDistance, 24); controls.update(); T.draw();
}
/** Moves a mesh as the controls say, about each hinge or axis it hangs from, the nearest first. */
let current = pose(ctl);
// The instrument scales come from the same file as the Phase 8 viewer's dials; until they arrive the needles stay put.
fetch('../../08_realistic_digital_twin/data/instruments.json').then((r) => r.json()).then((j) => { setScales(j.instruments); current = pose(ctl); if (T) paint(); }).catch(() => {});
function place(m) {
  const { THREE } = T, q = new THREE.Quaternion(), v = new THREE.Vector3();
  for (const j of m.userData.joints) {
    const amount = j.kind === 'hinge' ? (current.hinge.get(j.id) ?? 0) * Math.PI / 180 : j.kind === 'spin' ? (current.spin.get(j.id) ?? 0) : 0;
    if (amount) { q.setFromAxisAngle(j.axis, amount * j.sign); m.position.sub(j.at).applyQuaternion(q).add(j.at); m.quaternion.premultiply(q); }
    const d = current.move.get(j.id);   // a turn is about the part's own origin; the shift comes after it
    if (d) m.position.add(v.set(...d).applyQuaternion(j.parent));
  }
}
/** The beacon and strobes flash while the window is open (steady if the reader prefers reduced motion). */
let flashFrame = 0;
const calm = matchMedia('(prefers-reduced-motion: reduce)');
function flash() {
  flashFrame = 0; if (!T || !$('dlg').open) return;
  const now = performance.now(); let changed = false, any = false;
  for (const [, m] of meshes()) {
    const g = m.userData.lamp && current.glow.get(m.userData.lamp);
    if (!g || !g.flash || m.material !== m.userData.lit) continue;
    any = true; const k = isLit(g.flash, now) ? g.k : 0;
    if (m.userData.lit.emissiveIntensity !== k) { m.userData.lit.emissiveIntensity = k; changed = true; }
  }
  if (changed) T.draw();
  if (any) flashFrame = requestAnimationFrame(flash);
}
function startFlash() { if (!flashFrame && !calm.matches) flashFrame = requestAnimationFrame(flash); }
/** The material of a lamp or a spark plug that is lit: its own, glowing. */
function lit(m, g) {
  const c = (m.userData.lit ||= m.userData.material.clone());
  c.emissive = new T.THREE.Color(g.color); c.emissiveIntensity = g.k; return c;
}
function paint() {
  const home = shown[cur].s, { THREE } = T, span = new THREE.Box3(), k = scope === 'part' ? 0 : pull * 1.5;
  const round = (system) => (scope === 'aircraft' ? !hidden.has(system) : scope === 'system' && system === home);
  if (k) for (const [system, m] of meshes()) if (round(system) && system !== 'GROUND_EQUIPMENT') span.expandByPoint(m.userData.middle);
  const centre = span.isEmpty() ? null : span.getCenter(new THREE.Vector3()), out = new THREE.Vector3();
  for (const [system, m] of meshes()) {
    const chosen = m.userData.chosen, around = round(system);
    m.position.copy(m.userData.home); m.quaternion.copy(m.userData.homeQ); place(m);
    if (centre && around) m.position.addScaledVector(out.subVectors(m.userData.middle, centre), k);
    const by = shifted.get(m.userData.piece); if (by) { m.position.x += by[0]; m.position.y += by[1]; m.position.z += by[2]; }
    m.visible = scope === 'aircraft' ? around : chosen || around;
    m.material = chosen ? (solid && !quiet ? T.marked : m.userData.material) : solid ? m.userData.material : T.faint;
    const g = m.userData.lamp && current.glow.get(m.userData.lamp);
    if (g && m.material !== T.faint) m.material = lit(m, g);
    m.castShadow = m.material !== T.faint;   // a part drawn as a faint ghost throws no shadow
    m.renderOrder = chosen || solid ? 0 : 1;
  }
  T.draw(); startFlash();
}
function choose() {
  const p = shown[cur], want = new Set([p.id, ...p.more.map((m) => m[0])]); let any = false;
  for (const [, m] of meshes()) { m.userData.chosen = want.has(m.userData.part); any ||= m.userData.chosen; }
  return any;
}
const HINT = ['Drag to turn · scroll or pinch to zoom · right-drag or two fingers to move', 'اسحب للتدوير · مرّر أو قرّب بإصبعين للتكبير · اسحب بالزر الأيمن أو بإصبعين للتحريك'];
const DRAG = ['Drag a part to move it · drag empty space to turn the view', 'اسحب قطعة لتحريكها · اسحب في الفراغ لتدوير العرض'];
const HINT_ALL = ['Click a part to choose it · drag to turn · scroll or pinch to zoom · right-drag or two fingers to move', 'انقر على قطعة لاختيارها · اسحب للتدوير · مرّر أو قرّب بإصبعين للتكبير · اسحب بالزر الأيمن أو بإصبعين للتحريك'];
// The setting: the aircraft, a system or a part stands on the apron of an airfield under the sky, or on the floor of a hangar; there is no
// blank background. The sky and the apron are the Phase 8 viewer's own, painted by the program (08_realistic_digital_twin/js/sky.js).
// The airfield is the default; the reader can choose the hangar.
let setting = 'airfield', chosenSetting = false, settingTurn = 0;
const settingFor = () => (chosenSetting ? setting : 'airfield');
async function backdrop() {
  const want = settingFor(); if (!T || T.shown === want) return;
  const mine = ++settingTurn, { THREE, scene, controls } = T;
  // If the sky cannot be loaded (offline without it saved), the plain white stays and nothing else is lost.
  const sky = want === 'plain' ? null : await import('../../08_realistic_digital_twin/js/sky.js').catch(() => null);
  if (mine !== settingTurn) return;
  if (want !== 'plain' && !sky) { $('setting').value = T.shown; return; }
  if (T.back) { scene.remove(T.back); T.back.traverse((o) => { o.geometry?.dispose(); }); T.back = null; }
  T.shown = want; scene.fog = null; controls.maxPolarAngle = Math.PI; T.headlight.intensity = 1.2; scene.environment = T.roomEnv;
  if (want === 'plain') { T.draw(); return; }
  const back = new THREE.Group(); back.name = '_setting';
  const nothing = () => {}; const solid = (o) => { o.raycast = nothing; o.receiveShadow = true; return o; };
  if (want === 'airfield') {
    const el = THREE.MathUtils.degToRad(42), az = THREE.MathUtils.degToRad(35), sunDir = new THREE.Vector3(Math.cos(el) * Math.sin(az), Math.sin(el), Math.cos(el) * Math.cos(az));
    const dome = sky.createSky(sunDir); back.add(dome);
    const t = sky.apronTextures(1024, 4); for (const k of ['map', 'roughnessMap', 'normalMap']) t[k].repeat.set(1200 / 20, 1200 / 20);
    const apron = solid(new THREE.Mesh(new THREE.PlaneGeometry(1200, 1200), new THREE.MeshStandardMaterial({ ...t, roughness: 1, metalness: 0 }))); apron.rotation.x = -Math.PI / 2; back.add(apron);
    back.add(sky.standMarkings());
    const sun = new THREE.DirectionalLight(0xfff0d8, 3.2); sun.position.copy(sunDir).multiplyScalar(30); sun.castShadow = true; sun.shadow.mapSize.set(2048, 2048);
    Object.assign(sun.shadow.camera, { left: -9, right: 9, top: 9, bottom: -9, near: 5, far: 80 }); sun.shadow.bias = -0.0004; sun.shadow.normalBias = 0.02; sun.shadow.radius = 2.5;
    back.add(sun, sun.target, new THREE.HemisphereLight(0xcfe2ff, 0x8c8477, 0.5));
    if (!T.skyEnv) { const pm = new THREE.PMREMGenerator(T.renderer), box = new THREE.Scene(), d = sky.createSky(sunDir); d.scale.setScalar(50); box.add(d); T.skyEnv = pm.fromScene(box, 0, 0.1, 100).texture; pm.dispose(); }
    scene.environment = T.skyEnv; scene.fog = new THREE.Fog(sky.HAZE, 150, 800); controls.maxPolarAngle = Math.PI * 0.495; T.headlight.intensity = 0.15;
  } else {
    // a hangar: concrete floor, corrugated walls and roof, rows of lights overhead
    const W = 36, L = 56, H = 11, stripes = document.createElement('canvas'); stripes.width = 256; stripes.height = 16;
    { const g = stripes.getContext('2d'); g.fillStyle = '#c9ced4'; g.fillRect(0, 0, 256, 16); for (let x = 0; x < 256; x += 16) { g.fillStyle = 'rgba(0,0,0,.14)'; g.fillRect(x + 8, 0, 8, 16); } }
    const wall = new THREE.CanvasTexture(stripes); wall.wrapS = wall.wrapT = THREE.RepeatWrapping; wall.colorSpace = THREE.SRGBColorSpace; wall.repeat.set(20, 1);
    const wallMat = new THREE.MeshStandardMaterial({ map: wall, roughness: 0.85, metalness: 0.1, side: THREE.DoubleSide });
    const floor = solid(new THREE.Mesh(new THREE.PlaneGeometry(W, L), new THREE.MeshStandardMaterial({ color: 0x6f757b, roughness: 0.5, metalness: 0 }))); floor.rotation.x = -Math.PI / 2; back.add(floor, sky.standMarkings());
    const plane = (w, h, x, y, z, rx, ry, mat) => { const m = solid(new THREE.Mesh(new THREE.PlaneGeometry(w, h), mat)); m.position.set(x, y, z); m.rotation.set(rx, ry, 0); back.add(m); return m; };
    plane(L, H, -W / 2, H / 2, 0, 0, Math.PI / 2, wallMat); plane(L, H, W / 2, H / 2, 0, 0, -Math.PI / 2, wallMat);
    plane(W, H, 0, H / 2, -L / 2, 0, 0, wallMat); plane(W, H, 0, H / 2, L / 2, 0, Math.PI, wallMat);
    plane(W, L, 0, H, 0, Math.PI / 2, 0, new THREE.MeshStandardMaterial({ color: 0x8d949c, roughness: 0.9, side: THREE.DoubleSide }));
    const lamp = new THREE.MeshBasicMaterial({ color: 0xffffff, fog: false });
    for (const x of [-9, 0, 9]) for (const z of [-16, -5, 6, 17]) plane(5, 0.5, x, H - 0.05, z, Math.PI / 2, 0, lamp);
    for (const [x, z, shadow] of [[-6, -6, true], [7, 8, false]]) { const sp = new THREE.SpotLight(0xffffff, 700, 0, 0.95, 0.6, 2); sp.position.set(x, H - 0.5, z); sp.target.position.set(0, 0, 0); sp.castShadow = shadow; sp.shadow.mapSize.set(1024, 1024); sp.shadow.bias = -0.0005; back.add(sp, sp.target); }
    back.add(new THREE.HemisphereLight(0xeef2f7, 0x5a5e62, 0.5));
    controls.maxDistance = Math.min(controls.maxDistance, 24); T.headlight.intensity = 0.3;
  }
  T.back = back; scene.add(back); T.draw();
}
async function show3d(keep) {
  const mine = ++turn, p = shown[cur], whole = scope === 'aircraft';
  $('dlg').classList.toggle('is-wide', whole); $('bsolid').hidden = $('pull').hidden = scope === 'part'; $('hide').hidden = !whole;
  message('Loading the 3D model…', 'جارٍ تحميل النموذج ثلاثي الأبعاد…');
  try {
    await setup(); await model(p.s); await backdrop(); if (mine !== turn) return;
    if (!choose()) { paint(); message('This part has no 3D model. Choose another view to see its picture.', 'لا يوجد نموذج ثلاثي الأبعاد لهذه القطعة. اختر عرضًا آخر لرؤية صورتها.'); return; }
    paint(); if (!keep) fit(false);
    if (!whole) { message(...(scope === 'system' ? HINT_ALL : HINT)); return; }
    // The rest of the aircraft arrives a system at a time and is drawn as it comes.
    const rest = systems.filter((s) => !T.roots.has(s)); let done = systems.length - rest.length;
    for (const s of rest) {
      message(`Loading the aircraft: ${done} of ${systems.length} systems…`, `جارٍ تحميل الطائرة: ${done} من ${systems.length} نظامًا…`);
      await model(s); if (mine !== turn) return; done += 1; choose(); paint();
    }
    if (!keep) fit(true);
    message(...HINT_ALL);
  } catch { if (mine === turn) message('The 3D view could not be loaded here. Choose another view to see the picture.', 'تعذّر تحميل العرض ثلاثي الأبعاد هنا. اختر عرضًا آخر لرؤية الصورة.'); }
}
/** Points the picking ray through where the pointer is on the canvas. */
function aim(event) {
  const { THREE, ray, camera } = T, box = $('d-3d').getBoundingClientRect();
  ray.setFromCamera(new THREE.Vector2(((event.clientX - box.left) / box.width) * 2 - 1, -((event.clientY - box.top) / box.height) * 2 + 1), camera);
}
/** The nearest drawn part under the pointer, if any. */
function rayHit(event) {
  aim(event);
  const seen = []; for (const [, m] of meshes()) if (m.visible && m.userData.part) seen.push(m);
  return T.ray.intersectObjects(seen, false)[0];
}
function pick(event) {
  if (scope === 'part' || !T || moving) return;
  const hit = rayHit(event), p = hit && entry.get(hit.object.userData.part);
  if (!p) return;
  quiet = false; keepCamera = true;
  if (!shown.includes(p)) { setFilters({}); render(); }
  open(shown.indexOf(p));
}
document.querySelectorAll('[data-scope]').forEach((b) => { b.onclick = () => { scope = b.dataset.scope; document.querySelectorAll('[data-scope]').forEach((x) => x.setAttribute('aria-pressed', String(x === b))); if (view === '3d') show3d(); sync(); }; });
$('setting').onchange = () => { chosenSetting = true; setting = $('setting').value; if (T) backdrop(); };
$('bsolid').onclick = () => { solid = !solid; $('bsolid').setAttribute('aria-pressed', String(solid)); if (T) paint(); };
$('bfit').onclick = () => { if (T) fit(scope === 'aircraft' || (scope === 'system' && pull > 0)); };
$('spread').oninput = () => { pull = $('spread').value / 100; if (T) paint(); };
// Moving it like the real aircraft: a tab for the scenes and one for each group of controls, a slider (or a box for a
// switch) for each control, and a play button for the engine. Each control moves every part it moves in the aircraft.
const PANELS = ['scene', ...new Set(CONTROLS.map((c) => c.group)), 'trainer'], panels = {}, rows = {};
let tab = 'flight', playing = false, lastTick = 0, playFrame = 0;
{
  const tabs = el('div', 'ufuq-tabs parts-gtabs'); tabs.setAttribute('role', 'group'); tabs.setAttribute('aria-label', 'Controls · أدوات التحكم');
  for (const g of PANELS) {
    const b = el('button', 'ufuq-tab'); b.type = 'button'; b.dataset.group = g; b.append(both(GROUPS[g].en, GROUPS[g].ar)); b.onclick = () => showTab(g); tabs.append(b);
    panels[g] = el('div', 'parts-gpanel'); panels[g].dataset.group = g;
  }
  $('slides').append(tabs, ...PANELS.map((g) => panels[g]));
}
function showTab(g) {
  tab = g; if (g === 'trainer') trainerOpen(); else trainerRelease();
  for (const b of $('slides').querySelectorAll('.parts-gtabs button')) b.setAttribute('aria-pressed', String(b.dataset.group === g));
  for (const k of PANELS) panels[k].hidden = k !== g;
}
// A scene sets the controls and instruments together to a state worth looking at.
{
  const row = el('label', 'parts-scene'), name = el('span', 'parts-slide-name'), pick = el('select', 'ufuq-input'), note = el('p', 'parts-scene-note');
  pick.id = 'scene'; name.append(both('Scene', 'المشهد')); for (const c of SCENES) pick.append(new Option(`${c.en} · ${c.ar}`, c.key));
  note.append(both('Typical settings to look at, not values from the POH. The aircraft is posed, not simulated.', 'إعدادات نموذجية للمعاينة وليست قيمًا من دليل POH. الطائرة موضوعة في وضع وليست محاكاة.'));
  pick.onchange = () => applyScene(pick.value); row.append(name, pick); panels.scene.append(row, note);
}
const strokesEl = el('p', 'parts-strokes'); strokesEl.id = 'strokes';
/** Which stroke each cylinder is on, at the crank angle the reader has set or the engine has reached. */
function updateStrokes() {
  strokesEl.replaceChildren(...strokes(ctl.crank).map(({ cyl, stroke }) => {
    const s = el('span', 'parts-stroke'), n = STROKE_NAMES[stroke]; s.dataset.stroke = stroke; s.append(`${cyl} · `, both(n.en, n.ar)); return s;
  }));
}
for (const c of CONTROLS) {
  const row = el('label', c.toggle ? 'parts-slide parts-switch' : 'parts-slide'), input = el('input'), name = el('span', 'parts-slide-name'), shown = el('output');
  name.append(both(c.en, c.ar)); if (c.note) row.title = c.note.en + ' · ' + c.note.ar;
  input.dataset.key = c.key; input.onshow = (v) => readout(v); const home = c.home ?? 0; const places = (String(c.step).split('.')[1] || '').length;
  const readout = (v) => { shown.replaceChildren(); if (c.names) shown.append(both(c.names[v - c.min].en, c.names[v - c.min].ar)); else if (!c.toggle) shown.textContent = v.toFixed(places); else shown.append(...(v ? [both(v > 0 ? 'Up' : 'Down', v > 0 ? 'للأعلى' : 'للأسفل')] : [])); };
  const changed = () => { readout(ctl[c.key]); current = pose(ctl); if (T) paint(); if (c.key === 'crank') updateStrokes(); sync(); };
  if (c.toggle) {
    // A switch rests in the middle of its throw; the box puts it up, and unticking it puts it down.
    input.type = 'checkbox'; input.oninput = () => { ctl[c.key] = input.checked ? 1 : -1; changed(); };
    input.onreset = () => { input.checked = false; ctl[c.key] = 0; readout(0); };
  } else {
    input.type = 'range'; input.min = c.min; input.max = c.max; input.step = c.step; input.value = home;
    input.oninput = () => { ctl[c.key] = Number(input.value); if (c.group === 'instruments') ctl.inst = 1; changed(); };
    input.onreset = () => { input.value = home; ctl[c.key] = home; readout(home); };
  }
  readout(home); row.append(name, input, shown); panels[c.group].append(row); rows[c.key] = row;
  if (c.key === 'crank') {
    // Run the engine: the crank turns by itself at the speed chosen, and each cylinder's stroke is named as it goes.
    const play = el('div', 'parts-play'), bp = el('button', 'ufuq-btn ufuq-btn--quiet'), rate = el('label', 'parts-slide'), rn = el('span', 'parts-slide-name'), rin = el('input'), rout = el('output');
    bp.type = 'button'; bp.id = 'bplay'; bp.setAttribute('aria-pressed', 'false'); bp.append(both('Run the engine', 'شغّل المحرك')); bp.onclick = () => setPlaying(!playing);
    rn.append(both('Speed (turns of the crank per minute)', 'السرعة (دورات عمود المرفق في الدقيقة)')); rin.type = 'range'; rin.id = 'rpm'; rin.min = 2; rin.max = 300; rin.step = 1; rin.value = 20; rout.textContent = '20';
    rin.oninput = () => { rout.textContent = rin.value; }; rate.append(rn, rin, rout); play.append(bp, rate); panels.engine.append(play, strokesEl);
  }
}
// The control-effect trainer: a challenge names an effect ("raise the nose"), the control that causes it moves into the panel,
// and the reader sets it and checks. What the reader's setting does is told whether it is right or not.
const trainer = { asked: [], now: null, tries: 0, right: 0, total: 0, held: null };
{
  const ask = el('p', 'parts-ask'), slot = el('div', 'parts-slot'), fb = el('p', 'parts-fb'), note = el('p', 'parts-note'), row = el('div', 'parts-play');
  ask.id = 't-ask'; slot.id = 't-slot'; fb.id = 't-fb'; fb.setAttribute('role', 'status'); note.id = 't-score';
  const check = el('button', 'ufuq-btn ufuq-btn--primary'), next = el('button', 'ufuq-btn ufuq-btn--quiet');
  check.type = next.type = 'button'; check.id = 't-check'; next.id = 't-next'; check.append(both('Check', 'تحقّق')); next.append(both('Next challenge', 'التحدي التالي')); next.hidden = true;
  check.onclick = trainerCheck; next.onclick = () => trainerNext();
  row.append(check, next); panels.trainer.append(ask, slot, row, fb, note);
}
function trainerHold(key) { const row = rows[key], mark = document.createComment('control'); row.replaceWith(mark); $('t-slot').append(row); trainer.held = { row, mark }; }
function trainerRelease() { if (trainer.held) { trainer.held.mark.replaceWith(trainer.held.row); trainer.held = null; } }
function trainerOpen() { if (trainer.now) { trainerHold(trainer.now.key); } else trainerNext(); }
function trainerScore() { $('t-score').replaceChildren(both(`Right first time: ${trainer.right} of ${trainer.total}`, `صحيح من أول مرة: ${trainer.right} من ${trainer.total}`)); }
function trainerNext() {
  trainerRelease();
  if (trainer.now) { const i = $('slides').querySelector(`input[data-key="${trainer.now.key}"]`); i.onreset(); current = pose(ctl); if (T) paint(); tidy(); sync(); }   // the last control goes back to centre
  const c = nextChallenge(trainer.asked); trainer.now = c; trainer.asked.push(c.id); trainer.tries = 0; trainerHold(c.key);
  $('t-ask').replaceChildren(both(`Challenge: ${c.en}`, `التحدي: ${c.ar}`)); $('t-fb').replaceChildren(); $('t-next').hidden = true; $('t-check').hidden = false; trainerScore();
}
/** The names of the parts that a control moves, from the catalogue. */
function movedNames(key, value) {
  const p = pose({ ...rest(), [key]: value }), ids = new Set();
  for (const m of [p.hinge, p.spin, p.move]) for (const [id, v] of m) if ([].concat(v).some((x) => Math.abs(x) > 1e-9)) ids.add(id);
  return [...ids].map((id) => entry.get(id)).filter(Boolean).slice(0, 6);
}
function trainerCheck() {
  const c = trainer.now, v = ctl[c.key], j = judge(c, v), fb = $('t-fb'); trainer.tries += 1;
  const line = (t) => both(t.en, t.ar);
  if (j.ok) {
    if (trainer.tries === 1) trainer.right += 1; trainer.total += 1;
    const names = movedNames(c.key, v), moved = el('span');
    names.forEach((p, i) => { if (i) moved.append(', '); moved.append(both(p.en, p.ar)); });
    fb.replaceChildren(both('Right. ', 'صحيح. '), line(j.now), document.createElement('br'), both('Moved: ', 'تحرّك: '), moved);
    $('t-next').hidden = false; $('t-check').hidden = true; $('t-next').focus(); trainerScore();
  } else {
    fb.replaceChildren(both('Not quite. ', 'ليس تمامًا. '), j.now ? both('Your setting: ', 'إعدادك: ') : both('The control is centred, so nothing moves. ', 'أداة التحكم في الوسط فلا شيء يتحرك. '), ...(j.now ? [line(j.now)] : []), both(' Try the other way.', ' جرّب الاتجاه الآخر.'));
  }
}
/** Sets the crank angle (0 to 720 degrees) as if the slider had been moved. */
function setCrank(v) {
  ctl.crank = v; const i = $('slides').querySelector('input[data-key="crank"]'); i.value = v; i.onshow(Math.round(v));
  current = pose(ctl); if (T) paint(); updateStrokes(); tidy();
}
function setPlaying(on) {
  playing = on && !!T; const bp = $('bplay');
  bp.setAttribute('aria-pressed', String(playing)); bp.replaceChildren(playing ? both('Pause', 'أوقف') : both('Run the engine', 'شغّل المحرك'));
  cancelAnimationFrame(playFrame);
  if (playing) { lastTick = performance.now(); playFrame = requestAnimationFrame(tick); } else sync();
}
function tick(now) {
  if (!playing) return;
  if (!$('dlg').open || document.hidden) { setPlaying(false); return; }
  const dt = Math.min(0.1, (now - lastTick) / 1000); lastTick = now;
  setCrank((ctl.crank + Number($('rpm').value) * 6 * dt) % 720);   // 1 turn per minute is 6 degrees a second
  playFrame = requestAnimationFrame(tick);
}
$('dlg').addEventListener('close', () => setPlaying(false));
updateStrokes(); showTab('flight');
function applyScene(key) {
  const scene = SCENES.find((c) => c.key === key);
  Object.assign(ctl, rest()); $('slides').querySelectorAll('input').forEach((i) => i.onreset?.());
  for (const [k, v] of Object.entries(scene.set)) {
    const i = $('slides').querySelector(`input[data-key="${k}"]`); ctl[k] = v;
    if (i.type === 'checkbox') i.checked = v > 0; else i.value = v;
    i.onshow(v); if (CONTROLS.find((c) => c.key === k).group === 'instruments') ctl.inst = 1;
  }
  current = pose(ctl); if (T) paint(); updateStrokes(); tidy(); sync();
}
/** Sets the controls and the dragged parts from a pose read from an address (see parsePose). */
function applyPose({ values, shifts }) {
  Object.assign(ctl, rest()); $('slides').querySelectorAll('input').forEach((i) => i.onreset?.()); shifted.clear();
  for (const [k, v] of Object.entries(values)) {
    const i = $('slides').querySelector(`input[data-key="${k}"]`); ctl[k] = v;
    if (i.type === 'checkbox') i.checked = v > 0; else i.value = v;
    i.onshow(v); if (CONTROLS.find((c) => c.key === k).group === 'instruments') ctl.inst = 1;
  }
  for (const s of shifts) shifted.set(s.piece, [s.x, s.y, s.z]);
  current = pose(ctl); updateStrokes(); tidy();
  if (Object.keys(values).length || shifts.length) {
    $('slides').hidden = false; $('bctl').setAttribute('aria-pressed', 'true'); $('dlg').classList.add('has-slides');
    showTab(CONTROLS.find((c) => c.key in values)?.group ?? tab);
  }
}
const anything = () => CONTROLS.some((c) => ctl[c.key] !== (c.home ?? 0)) || ctl.inst || shifted.size > 0;
const tidy = () => { $('bback').hidden = !anything(); };
/** The pose and the dragged parts, as query values for an address. */
const posePairsNow = () => (view === '3d' ? posePairs({ ...ctl }, CONTROLS, [...shifted].filter(([k]) => entry.has(k)).map(([piece, [x, y, z]]) => ({ piece, x, y, z }))) : []);
$('slides').addEventListener('input', tidy);
$('bctl').onclick = () => { const open = $('slides').hidden; $('slides').hidden = !open; $('bctl').setAttribute('aria-pressed', String(open)); $('dlg').classList.toggle('has-slides', open); if (open) $('slides').scrollIntoView({ block: 'nearest' }); };
$('bmove').onclick = () => { moving = !moving; $('bmove').setAttribute('aria-pressed', String(moving)); $('bdeep').hidden = !moving; message(...(moving ? DRAG : scope === 'aircraft' ? HINT_ALL : HINT)); };
$('bdeep').onclick = () => { deep = !deep; $('bdeep').setAttribute('aria-pressed', String(deep)); };
$('bback').onclick = () => {
  setPlaying(false); Object.assign(ctl, rest()); shifted.clear(); current = pose(ctl);
  $('slides').querySelectorAll('input').forEach((i) => i.onreset?.()); $('scene').value = 'cold'; updateStrokes();
  $('bback').hidden = true; if (T) paint(); sync();
};
systems.forEach((s) => {
  const b = el('button', 'ufuq-tab'), nm = systemName(s); b.append(both(nm.en, nm.ar)); b.type = 'button'; b.setAttribute('aria-pressed', 'true');
  b.onclick = () => { if (hidden.has(s)) hidden.delete(s); else hidden.add(s); b.setAttribute('aria-pressed', String(!hidden.has(s))); if (T) paint(); };
  $('hide').append(b);
});
$('explore').onclick = () => {
  view = '3d'; scope = 'aircraft'; solid = true; quiet = true; $('bsolid').setAttribute('aria-pressed', 'true');
  document.querySelectorAll('[data-scope]').forEach((x) => x.setAttribute('aria-pressed', String(x.dataset.scope === 'aircraft')));
  open(Math.max(0, shown.findIndex((p) => p.id === 'AIRFRAME.fuselage')));
};

// The naming quiz: a picture and four names, or a name and four pictures; ten questions, then the parts to look at again.
{
  const dlg = $('qdlg'); let round = [], at = 0, results = [], answered = false;
  option($('q-sys'), '', 'All systems · كل الأنظمة'); for (const sys of systems) option($('q-sys'), sys, names(systemName(sys)));
  const show = (id, on) => { $(id).hidden = !on; };
  const setup = () => { show('q-setup', true); show('q-play', false); show('q-end', false); show('q-next', false); show('q-again-btn', false); };
  function question() {
    const q = round[at]; answered = false; show('q-next', false); $('q-fb').replaceChildren();
    $('q-prog').replaceChildren(both(`Question ${at + 1} of ${round.length}`, `السؤال ${at + 1} من ${round.length}`));
    const opts = $('q-opts'); opts.replaceChildren(); opts.dataset.mode = q.mode;
    if (q.mode === 'name') { show('q-pic', true); tile($('q-pic'), D.large, q.answer.i); say($('q-ask'), 'What is this part?', 'ما هذه القطعة؟'); }
    else {
      show('q-pic', false); const a = el('span', 'parts-name', q.answer.en), r = el('span', 'parts-name parts-ar', q.answer.ar); a.lang = 'en'; a.dir = 'ltr'; r.lang = 'ar'; r.dir = 'rtl';
      $('q-ask').replaceChildren(both('Which picture shows this part?', 'أي صورة تُظهر هذه القطعة؟'), document.createElement('br'), a, document.createElement('br'), r);
    }
    q.options.forEach((o, k) => {
      const b = el('button', 'parts-opt'); b.type = 'button'; b.dataset.k = k;
      if (q.mode === 'name') { const a = el('span', 'parts-name', o.en), r = el('span', 'parts-name parts-ar', o.ar); a.lang = 'en'; a.dir = 'ltr'; r.lang = 'ar'; r.dir = 'rtl'; b.append(`${k + 1}  `, a, r); }
      else { const pic = el('div', 'parts-pic'); tile(pic, D.large, o.i); b.append(pic); b.setAttribute('aria-label', `Picture ${k + 1} · الصورة ${k + 1}`); }
      b.onclick = () => choose(k); opts.append(b);
    });
  }
  function choose(k) {
    if (answered) return; answered = true;
    const q = round[at], ok = k === q.correct, buttons = [...$('q-opts').children];
    results.push({ ok, part: q.answer }); buttons.forEach((b) => { b.disabled = true; });
    buttons[q.correct].classList.add('is-right'); if (!ok) buttons[k].classList.add('is-wrong');
    const a = el('span', 'parts-name', q.answer.en), r = el('span', 'parts-name parts-ar', q.answer.ar); a.lang = 'en'; a.dir = 'ltr'; r.lang = 'ar'; r.dir = 'rtl';
    $('q-fb').replaceChildren(ok ? both('Right! ', 'صحيح! ') : both('Not that one. It is: ', 'ليست هذه. إنها: '), a, ' · ', r, ' ', status(q.answer.st));
    const last = at === round.length - 1; $('q-next').replaceChildren(last ? both('See the result', 'اعرض النتيجة') : both('Next', 'التالي')); show('q-next', true); $('q-next').focus();
  }
  function finish() {
    const s = summarize(results); show('q-play', false); show('q-end', true); show('q-next', false); show('q-again-btn', true);
    $('q-score').replaceChildren(both(`${s.right} of ${s.total} right`, `${s.right} صحيحة من ${s.total}`));
    $('q-again').replaceChildren(...s.again.map((p) => {
      const li = el('li'), b = el('button', 'ufuq-btn ufuq-btn--quiet'); b.type = 'button'; b.append(both(`${p.en}`, `${p.ar}`));
      b.onclick = () => { dlg.close(); const q = entry.get(p.id); if (!shown.includes(q)) { setFilters({}); render(); } open(shown.indexOf(q)); }; li.append(b); return li;
    }));
    if (!s.again.length) $('q-again').replaceChildren(el('li', null, '★'));
  }
  $('q-start').onclick = () => {
    round = makeRound(P, { mode: $('q-mode').value, system: $('q-sys').value, n: ROUND }); results = []; at = 0;
    if (!round.length) { say($('q-prog'), 'This system has too few parts for a quiz.', 'عدد قطع هذا النظام قليل لاختبار.'); show('q-play', true); show('q-pic', false); $('q-opts').replaceChildren(); $('q-ask').replaceChildren(); return; }
    show('q-setup', false); show('q-play', true); question();
  };
  $('q-next').onclick = () => { at += 1; if (at < round.length) question(); else finish(); };
  $('q-again-btn').onclick = setup; $('q-close').onclick = () => dlg.close();
  dlg.addEventListener('click', (e) => { if (e.target === dlg) dlg.close(); });
  addEventListener('keydown', (e) => { if (dlg.open && /^[1-4]$/.test(e.key) && !answered && !$('q-play').hidden && !e.target.matches('select')) { $('q-opts').children[Number(e.key) - 1]?.click(); } });
  $('bquiz').onclick = () => { setup(); dlg.showModal(); };
}

// Offline use: the reader may keep a copy of the models, the picture sheets and the code, so that the catalogue opens without a
// connection (sw.js serves it). Nothing is kept unless they ask, and the copy can be removed.
if (offline.supported()) {
  navigator.serviceWorker.register('sw.js').catch(() => { /* a page opened from disk, or a browser that refuses: no offline copy */ });
  let saving = null;
  const msg = (en, ar) => say($('off-msg'), en, ar);
  const mb = (bytes) => (bytes ? ` (${Math.max(1, Math.round(bytes / 1048576))} MB)` : '');
  async function refresh() {
    const s = await offline.status(); $('off').hidden = false; $('boffx').hidden = !s.saved;
    $('boff').replaceChildren(s.saved ? both('Update the offline copy', 'حدّث النسخة المحفوظة') : both('Save for offline use', 'احفظ للاستخدام دون اتصال'));
    if (s.saved) msg(`Saved for offline use: ${s.files ?? '?'} files${mb(s.bytes)}. The pictures at full size are not included.`, `محفوظة للاستخدام دون اتصال: ${s.files ?? '?'} ملفًا${mb(s.bytes)}. الصور بالحجم الكامل غير مشمولة.`); else $('off-msg').replaceChildren();
  }
  $('boff').onclick = async () => {
    if (saving) { saving.abort(); return; }
    saving = new AbortController(); $('boff').replaceChildren(both('Stop', 'أوقف')); $('boffx').hidden = true;
    msg('Saving… keep this page open. The models and pictures are tens of megabytes: use Wi-Fi if you can.', 'جارٍ الحفظ… أبقِ الصفحة مفتوحة. النماذج والصور عشرات الميغابايت: استخدم الواي فاي إن أمكن.');
    try {
      const r = await offline.save(D, (done, total) => msg(`Saving… ${done} of ${total} files`, `جارٍ الحفظ… ${done} من ${total} ملفًا`), saving.signal);
      await refresh(); if (r.aborted) msg('Stopped. Nothing was kept.', 'تم الإيقاف. لم يُحفظ شيء.'); else if (r.failed.length) msg(`Saved, but ${r.failed.length} files could not be fetched; the rest work offline.`, `تم الحفظ، لكن تعذّر جلب ${r.failed.length} ملفًا؛ والباقي يعمل دون اتصال.`);
    } catch { await refresh(); msg('Could not save an offline copy here (the browser may have refused or be out of space).', 'تعذّر حفظ نسخة دون اتصال هنا (قد يكون المتصفح رفض أو لا توجد مساحة).'); }
    saving = null;
  };
  $('boffx').onclick = async () => { await offline.remove(); await refresh(); };
  refresh();
}

// The list and the part an address names. A part that the list leaves out clears the list.
{
  const params = new URLSearchParams(location.search);
  setFilters(parseList(params, systems));
  render();
  const link = parseLink(params, (id) => entry.has(id));
  const p = link.part && entry.get(link.part);
  if (p) {
    if (!shown.includes(p)) { setFilters({}); render(); }
    view = link.view; scope = link.scope; solid = scope === 'aircraft'; quiet = false; $('bsolid').setAttribute('aria-pressed', String(solid));
    if (view === '3d') applyPose(parsePose(params, CONTROLS, (id) => entry.has(id)));   // before the window opens, which writes the address
    document.querySelectorAll('[data-scope]').forEach((x) => x.setAttribute('aria-pressed', String(x.dataset.scope === scope)));
    open(shown.indexOf(p));
  }
}

// The search bar steps out of the way while the list is read downward and comes back on the way up; the heading of the
// system being read stays under it. A button returns to the top once the reader is far down.
{
  const bar = $('bar'), root = document.documentElement; let last = scrollY;
  const height = () => root.style.setProperty('--parts-bar-h', `${bar.classList.contains('is-away') ? 0 : bar.offsetHeight}px`);
  new ResizeObserver(height).observe(bar);
  addEventListener('scroll', () => {
    const y = scrollY, d = y - last; $('totop').hidden = y < innerHeight * 1.5;
    if (Math.abs(d) < 8) return; last = y;
    const away = d > 0 && y > 160 && !bar.contains(document.activeElement);
    if (bar.classList.contains('is-away') !== away) { bar.classList.toggle('is-away', away); height(); }
  }, { passive: true });
  $('totop').onclick = () => scrollTo({ top: 0, behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' });
}
