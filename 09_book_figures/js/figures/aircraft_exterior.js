// Major components of the aircraft, three-quarter view.
// Method: illustration rendered from the 3D model (blender/render_figure.py) with labels placed by
// code. The five components are tinted in the picture; each label's dot carries the colour of the
// component its part belongs to, and the table underneath says what each component is for.

import { el, wrapLines } from '../svg.js';
import { placeCallouts } from '../callouts.js';

export const size = [1600, 1100];

export async function draw({ svg, t, text, data, json, lang, dir }) {
  const render = await json(data.render);
  const poh = await json('../08_realistic_digital_twin/data/poh_references.json');
  const fact = (key) => poh.values.find((value) => value.key === key).value;
  // Latin facts inside Arabic text are isolated so that "160 BHP" keeps its own left-to-right order
  const latin = (value) => (dir === 'rtl' ? `\u2066${value}\u2069` : value);
  const fill = (string) => string.replace('{engine}', latin(fact('engine.model'))).replace('{rating}', latin(fact('engine.rating').replace(/ at .*/, '')));

  const IMG = { x: 272, y: 22, w: 972 };
  IMG.h = (IMG.w * render.height) / render.width;
  const scale = IMG.w / render.width;
  const href = `renders/${render.image}`;
  await new Promise((resolve, reject) => { const probe = new Image(); probe.onload = resolve; probe.onerror = () => reject(new Error(`cannot load ${href}`)); probe.src = href; });
  el('image', { href, x: IMG.x, y: IMG.y, width: IMG.w, height: IMG.h, preserveAspectRatio: 'xMidYMid meet' }, svg);

  // ---- labels on the artwork
  const components = Object.fromEntries(data.components.map((component) => [component.key, component]));
  const items = data.callouts.map(({ anchor, side, component }) => {
    const point = render.anchors[anchor];
    if (!point?.visible) throw new Error(`aircraft-exterior: "${anchor}" is not visible in ${render.image}; re-run the render`);
    if (!components[component]) throw new Error(`aircraft-exterior: "${anchor}" names an unknown component "${component}"`);
    return { key: anchor, side, x: IMG.x + point.x * scale, y: IMG.y + point.y * scale, title: t(`name_${anchor}`), color: components[component].dot };
  });
  placeCallouts(el('g', {}, svg), text, items, { left: 260, right: 1256, top: 26, bottom: IMG.y + IMG.h + 46, gap: 19 });

  // ---- the five components (mirrored for right-to-left reading; the aircraft never is)
  const TOP = IMG.y + IMG.h + 96;
  const ROW = 96;
  const X = { a: 60, name: 112, role: 440, b: 1540 };
  const at = (x) => (dir === 'rtl' ? size[0] - x : x);
  const align = dir === 'rtl' ? 'right' : 'left';
  for (const [key, x] of [['head_component', X.name], ['head_role', X.role]]) text(svg, at(x), TOP, t(key), { align, cls: 'heading' });
  el('line', { x1: X.a, y1: TOP + 20, x2: X.b, y2: TOP + 20, class: 'outline-thin' }, svg);
  data.components.forEach((row, index) => {
    const y = TOP + 20 + index * ROW;
    const sx = dir === 'rtl' ? at(X.a) - 32 : X.a;
    el('rect', { x: sx, y: y + 22, width: 32, height: 26, rx: 5, class: 'swatch', fill: row.color }, svg);
    text(svg, at(X.name), y + 45, t(row.key), { align, cls: 'label label-strong' });
    const role = wrapLines(svg, fill(t(`${row.key}_role`)), X.b - X.role, { cls: 'label', dir });
    if (role.split('\n').length > 2) throw new Error(`aircraft-exterior [${lang}]: the description of "${row.key}" needs more than two lines`);
    text(svg, at(X.role), y + 45, role, { align });
    if (index < data.components.length - 1) el('line', { x1: X.a, y1: y + ROW, x2: X.b, y2: y + ROW, class: 'hairline' }, svg);
  });
}
