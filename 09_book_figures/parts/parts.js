// The parts catalogue: the list, the search and the three views of a part (on its own, in the
// aircraft, in 3D). Everything shown is read from parts.json, which build.py writes.
const $ = (id) => document.getElementById(id);
const el = (tag, cls, text) => { const e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; };
/** A phrase in both languages; the page's language switch shows one. */
const both = (en, ar) => { const f = document.createDocumentFragment(); const a = el('span', 'ufuq-ar', ar); a.lang = 'ar'; f.append(el('span', 'ufuq-en', en), a); return f; };
const say = (node, en, ar) => node.replaceChildren(both(en, ar));

let D;
try { D = await (await fetch('parts.json')).json(); } catch { say($('list').firstElementChild, 'The parts list could not be loaded. Reload the page to try again.', 'تعذّر تحميل قائمة القطع. أعد تحميل الصفحة.'); throw new Error('parts.json'); }
const P = D.parts;
P.forEach((p, i) => { p.i = i; p.h = [p.en, p.ar, p.id, ...p.more.flatMap((m) => [m[1], m[2]])].join(' ').toLowerCase(); });
const systems = [...new Set(P.map((p) => p.s))];
let fs = '', fst = '', shown = P, cur = 0, view = 'alone';

/** Show tile `index` of a sheet of pictures as the background of `node`. */
function tile(node, sheet, index) {
  const file = sheet.files[Math.floor(index / sheet.per)], n = index % sheet.per, c = n % sheet.cols, r = Math.floor(n / sheet.cols);
  node.style.backgroundImage = `url("${file.f}")`;
  node.style.backgroundSize = `${sheet.cols * 100}% ${file.rows * 100}%`;
  node.style.backgroundPosition = `${sheet.cols > 1 ? (c / (sheet.cols - 1)) * 100 : 0}% ${file.rows > 1 ? (r / (file.rows - 1)) * 100 : 0}%`;
}
const seen = new IntersectionObserver((entries) => entries.forEach((e) => { if (e.isIntersecting) { tile(e.target.firstChild, D.thumb, +e.target.dataset.i); seen.unobserve(e.target); } }), { rootMargin: '600px' });

function chips(box, items, set) {
  items.forEach(([value, label, n], k) => {
    const b = el('button', 'ufuq-tab'); b.type = 'button'; b.setAttribute('aria-pressed', String(k === 0)); b.append(label, el('b', null, String(n)));
    b.onclick = () => { set(value); [...box.children].forEach((x) => x.setAttribute('aria-pressed', String(x === b))); render(); };
    box.append(b);
  });
}
const count = (key, value) => P.filter((p) => p[key] === value).length;
chips($('sys'), [['', both('All systems', 'كل الأنظمة'), P.length], ...systems.map((s) => [s, s, count('s', s)])], (v) => { fs = v; });
chips($('stat'), [['', both('Any source', 'أي مصدر'), P.length], ...['poh', 'type_data', 'estimated'].map((s) => [s, s, count('st', s)])], (v) => { fst = v; });

function render() {
  const words = $('q').value.trim().toLowerCase().split(/\s+/).filter(Boolean);
  shown = P.filter((p) => (!fs || p.s === fs) && (!fst || p.st === fst) && words.every((w) => p.h.includes(w)));
  say($('count'), `${shown.length} of ${P.length} parts`, `${shown.length} من ${P.length} قطعة`);
  seen.disconnect();
  if (!shown.length) { const none = el('p', 'parts-empty'); say(none, 'No part matches. Clear the search or pick another system.', 'لا توجد قطعة مطابقة. امسح البحث أو اختر نظامًا آخر.'); $('list').replaceChildren(none); return; }
  const frag = document.createDocumentFragment(); let system = null, grid = null;
  shown.forEach((p, n) => {
    if (p.s !== system) {
      system = p.s; const s = el('section'), h = el('h2', null, system), k = shown.filter((x) => x.s === system).length, small = el('small');
      say(small, `${k} parts`, `${k} قطعة`); h.dir = 'ltr'; h.append(small); grid = el('div', 'parts-grid'); s.append(h, grid); frag.append(s);
    }
    const b = el('button', 'parts-tile'); b.type = 'button'; b.dataset.i = p.i;
    const cap = el('div', 'parts-cap'), en = el('span', null, p.en), ar = el('span', 'parts-ar', p.ar);
    en.lang = 'en'; en.dir = 'ltr'; ar.lang = 'ar'; ar.dir = 'rtl';
    cap.append(en, ar, el('span', `parts-st ${p.st}`, p.st)); b.append(el('div', 'parts-pic'), cap); b.onclick = () => open(n); grid.append(b); seen.observe(b);
  });
  $('list').replaceChildren(frag);
}

function open(n) {
  cur = (n + shown.length) % shown.length; const p = shown[cur];
  $('d-en').textContent = p.en; $('d-ar').textContent = p.ar; $('d-id').textContent = p.id;
  $('d-st').className = `parts-st ${p.st}`; $('d-st').textContent = p.st;
  const more = $('d-more'); more.hidden = !p.more.length;
  more.replaceChildren(...p.more.map((m) => { const li = el('li'); say(li, `Also drawn: ${m[1]}`, `مرسومة معها: ${m[2]}`); return li; }));
  if (!$('dlg').open) $('dlg').showModal();
  show();
}
function show() {
  const p = shown[cur], is3d = view === '3d';
  document.querySelectorAll('[data-view]').forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.view === view)));
  $('d-3d').hidden = !is3d; $('bsys').hidden = $('bfit').hidden = !is3d;
  tile($('d-pic'), view === 'place' ? D.place : D.large, p.i);
  if (is3d) show3d(); else { turn += 1; message(); }
}
document.querySelectorAll('[data-view]').forEach((b) => { b.onclick = () => { view = b.dataset.view; show(); }; });
$('prev').onclick = () => open(cur - 1); $('next').onclick = () => open(cur + 1); $('close').onclick = () => $('dlg').close();
$('dlg').addEventListener('click', (e) => { if (e.target === $('dlg')) $('dlg').close(); });
$('dlg').addEventListener('keydown', (e) => { if (e.key === 'ArrowLeft') open(cur - 1); if (e.key === 'ArrowRight') open(cur + 1); });
let timer; $('q').addEventListener('input', () => { clearTimeout(timer); timer = setTimeout(render, 120); });

// The 3D view. Three.js and one model file per system (m/<SYSTEM>.glb) are fetched the first time they are asked for.
let T = null, ready = null, turn = 0, ghost = false; const models = {};
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
    const faint = new THREE.MeshBasicMaterial({ color: getComputedStyle(canvas).getPropertyValue('--ufuq-print-teal').trim() || 'gray', transparent: true, opacity: 0.07, depthWrite: false });
    const frame = () => {
      const w = canvas.clientWidth, h = canvas.clientHeight; if (!w || !h) return;
      const k = renderer.getPixelRatio();
      if (canvas.width !== Math.round(w * k) || canvas.height !== Math.round(h * k)) { renderer.setSize(w, h, false); camera.aspect = w / h; camera.updateProjectionMatrix(); }
      renderer.render(scene, camera);
    };
    const draw = () => requestAnimationFrame(frame);
    controls.addEventListener('change', draw); new ResizeObserver(draw).observe(canvas);
    T = { THREE, GLTFLoader, scene, camera, controls, faint, draw, root: null };
  })();
  return ready;
}
/** The meshes of one system, each marked with the catalogue part it belongs to, flat under one group. */
function model(system) {
  models[system] ||= new T.GLTFLoader().loadAsync(`m/${system}.glb`).then((gltf) => {
    const { THREE } = T, ids = {};
    for (const p of P) if (p.s === system) for (const id of [p.id, ...p.more.map((m) => m[0])]) ids[THREE.PropertyBinding.sanitizeNodeName(id)] = id;
    gltf.scene.updateMatrixWorld(true);
    const meshes = []; gltf.scene.traverse((o) => { if (o.isMesh) meshes.push(o); });
    for (const m of meshes) { let a = m, id = null; while (a && !id) { id = ids[a.name] || null; a = a.parent; } m.userData.part = id; m.userData.material = m.material; }
    const root = new THREE.Group(); for (const m of meshes) root.attach(m);
    return root;
  });
  return models[system];
}
function fit() {
  const { THREE, camera, controls } = T, box = new THREE.Box3();
  for (const m of T.root.children) if (m.userData.chosen) box.expandByObject(m);
  if (box.isEmpty()) return;
  const s = box.getBoundingSphere(new THREE.Sphere()), R = Math.max(s.radius, 1e-4), d = (R / Math.sin(THREE.MathUtils.degToRad(12))) * 1.08, az = THREE.MathUtils.degToRad(35), el = THREE.MathUtils.degToRad(22);
  controls.target.copy(s.center); camera.position.set(s.center.x + d * Math.cos(el) * Math.sin(az), s.center.y + d * Math.sin(el), s.center.z + d * Math.cos(el) * Math.cos(az));
  camera.near = Math.max(R / 200, 1e-4); camera.far = d + R * 400 + 50; camera.updateProjectionMatrix();
  controls.minDistance = R * 0.3; controls.maxDistance = d * 30 + 20; controls.update(); T.draw();
}
function paint() {
  for (const m of T.root.children) { m.visible = m.userData.chosen || ghost; m.material = m.userData.chosen ? m.userData.material : T.faint; m.renderOrder = m.userData.chosen ? 0 : 1; }
  T.draw();
}
async function show3d() {
  const mine = ++turn, p = shown[cur];
  message('Loading the 3D model…', 'جارٍ تحميل النموذج ثلاثي الأبعاد…');
  try {
    await setup(); const root = await model(p.s); if (mine !== turn) return;
    if (T.root !== root) { if (T.root) T.scene.remove(T.root); T.scene.add(root); T.root = root; }
    const want = new Set([p.id, ...p.more.map((m) => m[0])]); let any = false;
    for (const m of root.children) { m.userData.chosen = want.has(m.userData.part); any ||= m.userData.chosen; }
    if (!any) { for (const m of root.children) m.visible = false; T.draw(); message('This part has no 3D model. Choose another view to see its picture.', 'لا يوجد نموذج ثلاثي الأبعاد لهذه القطعة. اختر عرضًا آخر لرؤية صورتها.'); return; }
    paint(); fit(); message('Drag to turn · scroll or pinch to zoom · right-drag or two fingers to move', 'اسحب للتدوير · مرّر أو قرّب بإصبعين للتكبير · اسحب بالزر الأيمن أو بإصبعين للتحريك');
  } catch { if (mine === turn) message('The 3D view could not be loaded here. Choose another view to see the picture.', 'تعذّر تحميل العرض ثلاثي الأبعاد هنا. اختر عرضًا آخر لرؤية الصورة.'); }
}
$('bsys').onclick = () => { ghost = !ghost; $('bsys').setAttribute('aria-pressed', String(ghost)); if (T?.root) paint(); };
$('bfit').onclick = () => { if (T?.root) fit(); };

render();
