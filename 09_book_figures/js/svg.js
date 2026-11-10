// Small SVG helpers shared by every figure module. No dependencies; runs in the figure host page.
//
// Coordinates: one user unit is 0.1 mm on paper (a 160 mm wide figure has a viewBox 1600 units wide),
// so stroke widths and type sizes can be read straight off as print dimensions.

export const NS = 'http://www.w3.org/2000/svg';

const f = (n) => Number(n.toFixed(2));

export function el(tag, attrs = {}, parent) {
  const node = document.createElementNS(NS, tag);
  for (const [key, value] of Object.entries(attrs)) {
    if (value !== undefined && value !== null) node.setAttribute(key, value);
  }
  if (parent) parent.append(node);
  return node;
}

/** Angles follow data/instruments.json: degrees clockwise from 12 o'clock. */
export function polar(cx, cy, r, deg) {
  const a = (deg * Math.PI) / 180;
  return [cx + r * Math.sin(a), cy - r * Math.cos(a)];
}

export function arcPath(cx, cy, r, a0, a1) {
  const [x0, y0] = polar(cx, cy, r, a0);
  const [x1, y1] = polar(cx, cy, r, a1);
  const large = Math.abs(a1 - a0) > 180 ? 1 : 0;
  const sweep = a1 > a0 ? 1 : 0;
  return `M${f(x0)} ${f(y0)} A${f(r)} ${f(r)} 0 ${large} ${sweep} ${f(x1)} ${f(y1)}`;
}

/** A polyline with rounded corners: how pipe and cable runs are drawn. */
export function roundedPath(points, radius = 18) {
  if (points.length < 2) return '';
  let d = `M${f(points[0][0])} ${f(points[0][1])}`;
  for (let i = 1; i < points.length - 1; i++) {
    const [px, py] = points[i - 1];
    const [cx, cy] = points[i];
    const [nx, ny] = points[i + 1];
    const inLen = Math.hypot(cx - px, cy - py);
    const outLen = Math.hypot(nx - cx, ny - cy);
    const r = Math.min(radius, inLen / 2, outLen / 2);
    const ax = cx + ((px - cx) / inLen) * r;
    const ay = cy + ((py - cy) / inLen) * r;
    const bx = cx + ((nx - cx) / outLen) * r;
    const by = cy + ((ny - cy) / outLen) * r;
    d += ` L${f(ax)} ${f(ay)} Q${f(cx)} ${f(cy)} ${f(bx)} ${f(by)}`;
  }
  const last = points[points.length - 1];
  return `${d} L${f(last[0])} ${f(last[1])}`;
}

/**
 * Text factory bound to the figure language.
 *
 * `align` is the VISUAL alignment ('left' | 'center' | 'right'). SVG's text-anchor is relative to the
 * writing direction, so it is translated here; figure code never has to think about RTL.
 * `content` may contain "\n" for explicit line breaks. Returns the <text> element.
 */
export function textFactory(dir) {
  return function text(parent, x, y, content, opts = {}) {
    // Arabic needs more leading than Latin: its descenders and marks would touch the next line.
    const { align = 'left', cls = 'label', size, lineHeight = dir === 'rtl' ? 1.42 : 1.22, valign = 'baseline', fill, weight, rotate } = opts;
    const anchor = align === 'center' ? 'middle' : (align === 'left') === (dir === 'ltr') ? 'start' : 'end';
    const node = el('text', { class: cls, 'text-anchor': anchor, direction: dir, fill, 'font-weight': weight }, parent);
    if (size) node.setAttribute('font-size', size);
    const lines = String(content).split('\n');
    const fontSize = size || parseFloat(getComputedStyle(node).fontSize) || 30;
    const step = fontSize * lineHeight;
    let y0 = y;
    if (valign === 'middle') y0 = y - ((lines.length - 1) * step) / 2 + fontSize * 0.35;
    if (valign === 'top') y0 = y + fontSize * 0.8;
    lines.forEach((line, index) => {
      const span = el('tspan', { x: f(x), y: f(y0 + index * step) }, node);
      // "V_{NE}" sets NE as a subscript, the way V-speeds are printed in handbooks.
      const drop = fontSize * 0.2;
      line.split(/(_\{[^}]*\})/).forEach((piece, at, pieces) => {
        if (!piece) return;
        const sub = /^_\{(.*)\}$/.exec(piece);
        if (sub) el('tspan', { dy: f(drop), 'font-size': f(fontSize * 0.72) }, span).textContent = sub[1];
        else if (at > 0 && /^_\{/.test(pieces[at - 1])) el('tspan', { dy: f(-drop) }, span).textContent = piece;
        else span.append(piece);
      });
    });
    if (rotate) node.setAttribute('transform', `rotate(${rotate} ${f(x)} ${f(y)})`);
    return node;
  };
}

/**
 * Break `content` into lines no wider than `maxWidth` figure units, measured in the real font of
 * class `cls`. Returns the text with "\n" between lines, ready for the text factory.
 */
export function wrapLines(parent, content, maxWidth, { cls = 'label', dir = 'ltr' } = {}) {
  const probe = el('text', { class: cls, direction: dir, visibility: 'hidden' }, parent);
  const lines = [];
  for (const paragraph of String(content).split('\n')) {
    let line = '';
    for (const word of paragraph.split(/\s+/).filter(Boolean)) {
      const candidate = line ? `${line} ${word}` : word;
      probe.textContent = candidate;
      if (line && probe.getComputedTextLength() > maxWidth) { lines.push(line); line = word; } else line = candidate;
    }
    lines.push(line);
  }
  probe.remove();
  return lines.join('\n');
}

/** Arrowhead centred on (x, y) pointing along `deg` (0 = up, 90 = right, 180 = down). */
export function arrowHead(parent, x, y, deg, size = 16, cls = 'arrow') {
  const d = `M0 ${-size * 0.9} L${size * 0.62} ${size * 0.5} L${-size * 0.62} ${size * 0.5} Z`;
  return el('path', { d, class: cls, transform: `translate(${f(x)} ${f(y)}) rotate(${deg})` }, parent);
}
