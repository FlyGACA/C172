// SVG instrument panel. Scales/markings come from data/instruments.json (POH-referenced),
// the same file the GLB builder uses for the 3D dials.
const NS = 'http://www.w3.org/2000/svg';
const COLORS = { white: '#f2f2f2', green: '#22c55e', yellow: '#facc15', red: '#ef4444' };

export function valueToAngle(spec, v) {
  const pts = spec.map;
  if (spec.wrap) {
    const span = pts[pts.length - 1][0] - pts[0][0];
    v = pts[0][0] + ((((v - pts[0][0]) % span) + span) % span);
  }
  v = Math.min(Math.max(v, pts[0][0]), pts[pts.length - 1][0]);
  for (let i = 1; i < pts.length; i++) {
    const [v0, a0] = pts[i - 1], [v1, a1] = pts[i];
    if (v <= v1) return a0 + ((a1 - a0) * (v - v0)) / (v1 - v0);
  }
  return pts[pts.length - 1][1];
}

const el = (tag, attrs = {}, parent) => {
  const e = document.createElementNS(NS, tag);
  for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, v);
  if (parent) parent.append(e);
  return e;
};
const P = (a, r) => [r * Math.sin((a * Math.PI) / 180), -r * Math.cos((a * Math.PI) / 180)];
function arcPath(a0, a1, r) {
  const [x0, y0] = P(a0, r), [x1, y1] = P(a1, r);
  const large = Math.abs(a1 - a0) > 180 ? 1 : 0;
  return `M${x0.toFixed(2)} ${y0.toFixed(2)} A${r} ${r} 0 ${large} 1 ${x1.toFixed(2)} ${y1.toFixed(2)}`;
}

function frame(host, key, title) {
  const wrap = document.createElement('figure');
  wrap.className = 'gauge';
  wrap.dataset.key = key;
  const svg = el('svg', { viewBox: '-100 -100 200 200', role: 'img', 'aria-label': title });
  wrap.append(svg);
  const cap = document.createElement('figcaption');
  cap.innerHTML = `<span class="g-title"></span><output class="g-read"></output>`;
  cap.querySelector('.g-title').textContent = title;
  wrap.append(cap);
  host.append(wrap);
  el('circle', { r: 98, class: 'g-bezel' }, svg);
  el('circle', { r: 88, class: 'g-face' }, svg);
  return { wrap, svg, read: cap.querySelector('.g-read'), titleEl: cap.querySelector('.g-title') };
}

function needle(svg, len = 74, w = 4, cls = 'g-needle') {
  const g = el('g', { class: cls }, svg);
  el('path', { d: `M${-w / 2} 14 L${-w / 2} ${-len + 8} L0 ${-len} L${w / 2} ${-len + 8} L${w / 2} 14 Z` }, g);
  return g;
}

export function dialGauge(host, key, spec, title, fmt) {
  const f = frame(host, key, title);
  const { svg } = f;
  const bands = { outer: [74, 84], inner: [64, 72] };
  for (const arc of spec.arcs) {
    const [r0, r1] = bands[arc.band];
    el('path', { d: arcPath(valueToAngle(spec, arc.from), valueToAngle(spec, arc.to), (r0 + r1) / 2), stroke: COLORS[arc.color], 'stroke-width': r1 - r0, fill: 'none' }, svg)
      .append(Object.assign(el('title'), { textContent: arc.ref || '' }));
  }
  for (const red of spec.redlines) {
    const a = valueToAngle(spec, red.value);
    const [x0, y0] = P(a, 60), [x1, y1] = P(a, 88);
    el('line', { x1: x0, y1: y0, x2: x1, y2: y1, stroke: COLORS.red, 'stroke-width': 5 }, svg)
      .append(Object.assign(el('title'), { textContent: red.ref || '' }));
  }
  const t = spec.ticks;
  for (let v = t.minor_from; v <= spec.max + 1e-9; v += t.minor_step) {
    const major = t.major.some((m) => Math.abs(m - v) < 1e-9);
    const a = valueToAngle(spec, v);
    const [x0, y0] = P(a, major ? 70 : 78), [x1, y1] = P(a, 87);
    el('line', { x1: x0, y1: y0, x2: x1, y2: y1, class: major ? 'g-tick-major' : 'g-tick' }, svg);
  }
  for (const v of spec.labels) {
    const a = valueToAngle(spec, v);
    const [x, y] = P(a, 52);
    const txt = spec.label_text?.[String(v)] ?? String(spec.label_abs ? Math.abs(v / (spec.label_divisor || 1)) : v / (spec.label_divisor || 1));
    el('text', { x, y: y + 6, class: 'g-label' }, svg).textContent = txt;
  }
  el('text', { x: 0, y: key === 'ALT' ? -26 : 34, class: 'g-unit' }, svg).textContent = spec.unit;
  if (key === 'VSI') { el('text', { x: -24, y: -14, class: 'g-small' }, svg).textContent = 'UP'; el('text', { x: -24, y: 24, class: 'g-small' }, svg).textContent = 'DN'; }
  const n = needle(svg);
  el('circle', { r: 8, class: 'g-hub' }, svg);
  return {
    ...f,
    update(v) {
      n.setAttribute('transform', `rotate(${valueToAngle(spec, v).toFixed(2)})`);
      f.read.textContent = fmt(v);
    },
  };
}

export function altimeter(host, spec, title) {
  const f = dialGauge(host, 'ALT', spec, title, () => '');
  const n1000 = needle(f.svg, 48, 7, 'g-needle g-needle-short');
  const n10k = needle(f.svg, 84, 1.6, 'g-needle g-needle-thin');
  el('circle', { r: 8, class: 'g-hub' }, f.svg);
  el('rect', { x: 14, y: -9, width: 40, height: 16, rx: 2, class: 'g-window' }, f.svg);
  const kollsman = el('text', { x: 34, y: 3.5, class: 'g-small' }, f.svg);
  return {
    ...f,
    update(alt, setting) {
      const a100 = ((alt % 1000) + 1000) % 1000 * 0.36;
      f.svg.querySelector('.g-needle').setAttribute('transform', `rotate(${a100})`);
      n1000.setAttribute('transform', `rotate(${((alt % 10000) + 10000) % 10000 * 0.036})`);
      n10k.setAttribute('transform', `rotate(${((alt % 100000) + 100000) % 100000 * 0.0036})`);
      kollsman.textContent = setting.toFixed(2);
      f.read.textContent = `${Math.round(alt).toLocaleString('en-US')} ft`;
    },
  };
}

export function attitude(host, title) {
  const f = frame(host, 'AI', title);
  const { svg } = f;
  const clip = el('clipPath', { id: 'ai-clip' }, el('defs', {}, svg));
  el('circle', { r: 86 }, clip);
  const world = el('g', { 'clip-path': 'url(#ai-clip)' }, svg);
  const card = el('g', {}, world);
  el('rect', { x: -200, y: -400, width: 400, height: 400, class: 'ai-sky' }, card);
  el('rect', { x: -200, y: 0, width: 400, height: 400, class: 'ai-ground' }, card);
  el('line', { x1: -200, y1: 0, x2: 200, y2: 0, class: 'ai-horizon' }, card);
  for (const p of [-20, -10, 10, 20]) el('line', { x1: -14 - Math.abs(p) / 2, y1: -p * 2.4, x2: 14 + Math.abs(p) / 2, y2: -p * 2.4, class: 'ai-pitch' }, card);
  for (const a of [-60, -30, -20, -10, 0, 10, 20, 30, 60]) {
    const [x0, y0] = P(a, 76), [x1, y1] = P(a, a % 30 ? 84 : 88);
    el('line', { x1: x0, y1: y0, x2: x1, y2: y1, class: 'g-tick-major' }, svg);
  }
  const pointer = el('path', { d: 'M0 -74 L-6 -64 L6 -64 Z', class: 'ai-pointer' }, svg);
  el('path', { d: 'M-48 0 L-16 0 L-8 8 L0 0 L8 8 L16 0 L48 0', class: 'ai-plane' }, svg);
  el('circle', { r: 3, class: 'ai-dot' }, svg);
  return {
    ...f,
    update(bank, pitch) {
      card.setAttribute('transform', `rotate(${(-bank).toFixed(2)}) translate(0 ${(pitch * 2.4).toFixed(2)})`);
      pointer.setAttribute('transform', `rotate(${(-bank).toFixed(2)})`);
      f.read.textContent = `${Math.round(bank)}° / ${Math.round(pitch)}°`;
    },
  };
}

export function heading(host, title) {
  const f = frame(host, 'HI', title);
  const { svg } = f;
  const card = el('g', {}, svg);
  for (let a = 0; a < 360; a += 5) {
    const [x0, y0] = P(a, a % 10 ? 80 : 72), [x1, y1] = P(a, 87);
    el('line', { x1: x0, y1: y0, x2: x1, y2: y1, class: a % 30 ? 'g-tick' : 'g-tick-major' }, card);
  }
  const names = { 0: 'N', 90: 'E', 180: 'S', 270: 'W' };
  for (let a = 0; a < 360; a += 30) {
    const [x, y] = P(a, 58);
    el('text', { x, y: y + 6, class: names[a] ? 'g-label hi-cardinal' : 'g-label', transform: `rotate(${a} ${x} ${y})` }, card).textContent = names[a] || String(a / 10);
  }
  el('path', { d: 'M0 -88 L-5 -78 L5 -78 Z', class: 'ai-pointer' }, svg);
  el('path', { d: 'M0 -26 L0 22 M-20 -2 L20 -2 M-8 18 L8 18', class: 'hi-plane' }, svg);
  return {
    ...f,
    update(h) {
      card.setAttribute('transform', `rotate(${(-h).toFixed(2)})`);
      f.read.textContent = `${String(Math.round(h) % 360 || 360).padStart(3, '0')}°`;
    },
  };
}

export function turnCoordinator(host, title) {
  const f = frame(host, 'TC', title);
  const { svg } = f;
  for (const a of [-90, 90, -110, 110]) {
    const [x0, y0] = P(a, 70), [x1, y1] = P(a, 86);
    el('line', { x1: x0, y1: y0, x2: x1, y2: y1, class: 'g-tick-major' }, svg);
  }
  el('text', { x: -62, y: 44, class: 'g-label' }, svg).textContent = 'L';
  el('text', { x: 62, y: 44, class: 'g-label' }, svg).textContent = 'R';
  el('text', { x: 0, y: 70, class: 'g-small' }, svg).textContent = '2 MIN';
  const plane = el('g', {}, svg);
  el('path', { d: 'M-66 0 L-10 0 L-6 -8 L6 -8 L10 0 L66 0 M-20 18 L20 18 M0 0 L0 18', class: 'tc-plane' }, plane);
  el('rect', { x: -40, y: 32, width: 80, height: 14, rx: 7, class: 'tc-tube' }, svg);
  el('circle', { cx: 0, cy: 39, r: 6, class: 'tc-ball' }, svg);
  const flag = el('text', { x: 0, y: -40, class: 'tc-flag' }, svg);
  return {
    ...f,
    update(rate, off) {
      plane.setAttribute('transform', `rotate(${(rate * 20).toFixed(2)})`);
      flag.textContent = off ? 'OFF' : '';
      f.read.textContent = off ? 'OFF' : `${(rate * 3).toFixed(1)}°/s`;
    },
  };
}
