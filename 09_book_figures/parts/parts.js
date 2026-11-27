// The parts catalogue: the list, the search and the three views of a part (on its own, in the
// aircraft, in 3D). Everything shown is read from parts.json, which build.py writes. A part and its view have
// an address of their own, and so has the list (a search, a system, a source): link.js reads and writes them, and the
// page keeps the address up to date as the reader moves.
import { SOURCES, buildLink, indexParts, linkPairs, listPairs, parseLink, parseList } from './link.js';
import { ORDER, SOURCE_NAMES, systemName } from './names.js';
import { haystack, matches, words } from './search.js';
import { CONTROLS, MOVING, pose, rest } from './motions.js';
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
  $('d-3d').hidden = !is3d; $('around').hidden = $('bfit').hidden = $('moves3d').hidden = !is3d;
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
    for (const k of ['part', 'view', 'scope', 'q', 'system', 'source']) url.searchParams.delete(k);
    for (const [k, v] of [...listPairs(filters()), ...(now ? linkPairs(now) : [])]) url.searchParams.set(k, v);
    history.replaceState(null, '', url.pathname + url.search + url.hash);
  } catch { /* an address that cannot be changed, such as a file opened from disk, is left as it is */ }
}
$('dlg').addEventListener('close', sync);
$('blink').onclick = async () => {
  const now = open_(); if (!now) return;
  const link = buildLink(here(), now);
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
    T = { THREE, GLTFLoader, scene, camera, controls, faint, marked, draw, roots: new Map(), ray: new THREE.Raycaster() };
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
      shifted.set(grab.piece, (shifted.get(grab.piece) || new THREE.Vector3()).add(at.clone().sub(grab.last))); grab.last.copy(at);
      paint(); $('bback').hidden = false;
    });
    const drop = () => { if (grab) { grab = null; controls.enabled = true; } };
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
      if (u.hinge_axis) return { id, kind: 'hinge', at, axis: AXES[u.hinge_axis].clone().applyQuaternion(q), sign: u.hinge_sign || 1 };
      if (u.spin_axis) return { id, kind: 'spin', at, axis: AXES[u.spin_axis].clone().applyQuaternion(q), sign: u.spin_sign || 1 };
      return { id, kind: 'move', parent };
    };
    const joints = new Map(); gltf.scene.traverse((o) => { if (o.userData.id && MOVING.has(o.userData.id)) joints.set(o, joint(o)); });
    for (const m of meshes) { m.userData.joints = []; for (let a = m; a; a = a.parent) if (joints.has(a)) m.userData.joints.push(joints.get(a)); }
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
  const s = box.getBoundingSphere(new THREE.Sphere()), R = Math.max(s.radius, 1e-4), d = (R / Math.sin(THREE.MathUtils.degToRad(12))) * (all && scope === 'aircraft' ? 0.6 : 1.08), az = THREE.MathUtils.degToRad(35), el = THREE.MathUtils.degToRad(22);
  controls.target.copy(s.center); camera.position.set(s.center.x + d * Math.cos(el) * Math.sin(az), s.center.y + d * Math.sin(el), s.center.z + d * Math.cos(el) * Math.cos(az));
  camera.near = all ? 0.02 : Math.max(R / 200, 1e-4); camera.far = d + R * 400 + 50; camera.updateProjectionMatrix();
  controls.minDistance = all ? 0.05 : R * 0.3; controls.maxDistance = d * 30 + 20; controls.update(); T.draw();
}
/** Moves a mesh as the controls say, about each hinge or axis it hangs from, the nearest first. */
let current = pose(ctl);
function place(m) {
  const { THREE } = T, q = new THREE.Quaternion(), v = new THREE.Vector3();
  for (const j of m.userData.joints) {
    if (j.kind === 'move') { const d = current.move.get(j.id); if (d) m.position.add(v.set(...d).applyQuaternion(j.parent)); continue; }
    const amount = j.kind === 'hinge' ? (current.hinge.get(j.id) ?? 0) * Math.PI / 180 : (current.spin.get(j.id) ?? 0);
    if (!amount) continue;
    q.setFromAxisAngle(j.axis, amount * j.sign);
    m.position.sub(j.at).applyQuaternion(q).add(j.at); m.quaternion.premultiply(q);
  }
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
    const by = shifted.get(m.userData.piece); if (by) m.position.add(by);
    m.visible = scope === 'aircraft' ? around : chosen || around;
    m.material = chosen ? (solid && !quiet ? T.marked : m.userData.material) : solid ? m.userData.material : T.faint;
    m.renderOrder = chosen || solid ? 0 : 1;
  }
  T.draw();
}
function choose() {
  const p = shown[cur], want = new Set([p.id, ...p.more.map((m) => m[0])]); let any = false;
  for (const [, m] of meshes()) { m.userData.chosen = want.has(m.userData.part); any ||= m.userData.chosen; }
  return any;
}
const HINT = ['Drag to turn · scroll or pinch to zoom · right-drag or two fingers to move', 'اسحب للتدوير · مرّر أو قرّب بإصبعين للتكبير · اسحب بالزر الأيمن أو بإصبعين للتحريك'];
const DRAG = ['Drag a part to move it · drag empty space to turn the view', 'اسحب قطعة لتحريكها · اسحب في الفراغ لتدوير العرض'];
const HINT_ALL = ['Click a part to choose it · drag to turn · scroll or pinch to zoom · right-drag or two fingers to move', 'انقر على قطعة لاختيارها · اسحب للتدوير · مرّر أو قرّب بإصبعين للتكبير · اسحب بالزر الأيمن أو بإصبعين للتحريك'];
async function show3d(keep) {
  const mine = ++turn, p = shown[cur], whole = scope === 'aircraft';
  $('dlg').classList.toggle('is-wide', whole); $('bsolid').hidden = $('pull').hidden = scope === 'part'; $('hide').hidden = !whole;
  message('Loading the 3D model…', 'جارٍ تحميل النموذج ثلاثي الأبعاد…');
  try {
    await setup(); await model(p.s); if (mine !== turn) return;
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
$('bsolid').onclick = () => { solid = !solid; $('bsolid').setAttribute('aria-pressed', String(solid)); if (T) paint(); };
$('bfit').onclick = () => { if (T) fit(scope === 'aircraft' || (scope === 'system' && pull > 0)); };
$('spread').oninput = () => { pull = $('spread').value / 100; if (T) paint(); };
// Moving it like the real aircraft: one slider for each control, which moves every part that control moves in the aircraft.
for (const c of CONTROLS) {
  const row = el('label', 'parts-slide'), input = el('input'), name = el('span', 'parts-slide-name'), shown = el('output');
  input.type = 'range'; input.min = c.min; input.max = c.max; input.step = c.step; input.value = 0; name.append(both(c.en, c.ar));
  if (c.note) { row.title = c.note.en + ' · ' + c.note.ar; }
  input.oninput = () => { ctl[c.key] = Number(input.value); shown.textContent = c.max > 1 ? input.value : Number(input.value).toFixed(2); current = pose(ctl); if (T) paint(); };
  shown.textContent = c.max > 1 ? '0' : '0.00'; input.dataset.key = c.key; row.append(name, input, shown); $('slides').append(row);
}
const anything = () => CONTROLS.some((c) => ctl[c.key]) || shifted.size > 0;
const tidy = () => { $('bback').hidden = !anything(); };
$('slides').addEventListener('input', tidy);
$('bctl').onclick = () => { const open = $('slides').hidden; $('slides').hidden = !open; $('bctl').setAttribute('aria-pressed', String(open)); $('dlg').classList.toggle('has-slides', open); };
$('bmove').onclick = () => { moving = !moving; $('bmove').setAttribute('aria-pressed', String(moving)); $('bdeep').hidden = !moving; message(...(moving ? DRAG : scope === 'aircraft' ? HINT_ALL : HINT)); };
$('bdeep').onclick = () => { deep = !deep; $('bdeep').setAttribute('aria-pressed', String(deep)); };
$('bback').onclick = () => {
  for (const c of CONTROLS) ctl[c.key] = 0; shifted.clear(); current = pose(ctl);
  $('slides').querySelectorAll('input').forEach((i) => { i.value = 0; i.dispatchEvent(new Event('input')); });
  $('bback').hidden = true; if (T) paint();
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
