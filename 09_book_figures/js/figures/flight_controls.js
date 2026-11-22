// Flight control surfaces, plan view.
// Method: illustration rendered from the 3D model (blender/render_figure.py) with labels placed by
// code. The picture is never photoreal: flat tones, ink outlines, the subject tinted. Label positions
// come from the model, so a new camera angle or corrected geometry needs no manual re-annotation.

import { el } from '../svg.js';
import { placeCallouts } from '../callouts.js';

export const size = [1600, 1196];

export async function draw({ svg, t, text, data, json, lang, dir }) {
  const render = await json(data.render);
  const IMG = { x: 290, y: 24, w: 1020 };
  IMG.h = (IMG.w * render.height) / render.width;
  const scale = IMG.w / render.width;
  const href = `renders/${render.image}`;
  await new Promise((resolve, reject) => { const probe = new Image(); probe.onload = resolve; probe.onerror = () => reject(new Error(`cannot load ${href}`)); probe.src = href; });
  el('image', { href, x: IMG.x, y: IMG.y, width: IMG.w, height: IMG.h, preserveAspectRatio: 'xMidYMid meet' }, svg);

  // ---- labels on the artwork
  const items = data.callouts.map(({ anchor, side }) => {
    const point = render.anchors[anchor];
    if (!point?.visible) throw new Error(`flight-controls: "${anchor}" is not visible in ${render.image}; re-run the render`);
    const override = data.strings[lang][`name_${anchor}`];
    return { key: anchor, side, x: IMG.x + point.x * scale, y: IMG.y + point.y * scale, title: override || point[`label_${lang}`] };
  });
  placeCallouts(el('g', {}, svg), text, items, { left: 278, right: 1322, top: 60, bottom: IMG.y + IMG.h - 10, gap: 30 });

  // ---- side view of the tail: from above the rudder is edge-on, so the plan view cannot show it green
  const tail = await json(data.inset.render);
  const BOX = { x: 28, y: IMG.y, w: 250 };
  BOX.h = (BOX.w * tail.height) / tail.width;
  el('image', { href: `renders/${tail.image}`, x: BOX.x, y: BOX.y, width: BOX.w, height: BOX.h, preserveAspectRatio: 'xMidYMid meet' }, svg);
  el('rect', { x: BOX.x, y: BOX.y, width: BOX.w, height: BOX.h, class: 'outline-thin', fill: 'none' }, svg);
  text(svg, BOX.x, BOX.y + BOX.h + 24, t('inset_title'), { align: 'left', cls: 'label' });
  const dot = tail.anchors[data.inset.anchor];
  const label = data.strings[lang][`name_${data.inset.anchor}`] || dot[`label_${lang}`];
  const dx = BOX.x + dot.x * (BOX.w / tail.width);
  const dy = BOX.y + dot.y * (BOX.h / tail.height);
  el('line', { x1: BOX.x + 40, y1: BOX.y + 42, x2: dx, y2: dy, class: 'outline-thin' }, svg);
  text(svg, BOX.x + 10, BOX.y + 34, label, { align: 'left', cls: 'label label-strong' });

  // ---- what each surface does (mirrored for right-to-left reading; the aircraft never is)
  const TOP = IMG.y + IMG.h + 58;
  const ROW = 50;
  const X = { a: 60, name: 112, effect: 470, control: 1010, b: 1540 };
  const at = (x) => (dir === 'rtl' ? size[0] - x : x);
  const align = dir === 'rtl' ? 'right' : 'left';
  for (const [key, x] of [['head_surface', X.name], ['head_effect', X.effect], ['head_control', X.control]]) text(svg, at(x), TOP, t(key), { align, cls: 'heading' });
  el('line', { x1: X.a, y1: TOP + 20, x2: X.b, y2: TOP + 20, class: 'outline-thin' }, svg);
  data.table.forEach((row, index) => {
    const y = TOP + 20 + (index + 1) * ROW;
    const sx = dir === 'rtl' ? at(X.a) - 32 : X.a;
    el('rect', { x: sx, y: y - 39, width: 32, height: 26, rx: 5, class: 'swatch', fill: row.color }, svg);
    text(svg, at(X.name), y - 16, t(row.key), { align, cls: 'label label-strong' });
    text(svg, at(X.effect), y - 16, t(`${row.key}_effect`), { align });
    text(svg, at(X.control), y - 16, t(`${row.key}_control`), { align });
    if (index < data.table.length - 1) el('line', { x1: X.a, y1: y, x2: X.b, y2: y, class: 'hairline' }, svg);
  });
}
