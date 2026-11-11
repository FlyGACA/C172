// Airspeed indicator colour markings.
// Method: vector, drawn from data. The scale, arcs and red line come from the same instruments.json
// that drives the simulator gauges and the 3D dial, so a corrected value corrects every figure.

import { el, polar, arcPath } from '../svg.js';
import { placeCallouts } from '../callouts.js';
import { valueToAngle } from '../../../shared/js/gauges.js';

export const size = [1600, 930];

const C = [800, 442];          // dial centre
const R = { bezel: 322, face: 294, tickOuter: 288, tickMinor: 268, tickMajor: 254, outer: 236, inner: 207, numbers: 157 };
const BAND = { outer: R.outer, inner: R.inner };
const BAND_WIDTH = 24;

export async function draw({ svg, t, data, json, text, dir }) {
  const spec = (await json('../08_realistic_digital_twin/data/instruments.json')).instruments[data.instrument];
  const angle = (v) => valueToAngle(spec, v);
  const ltr = (s) => (dir === 'rtl' ? `⁦${s}⁩` : s);       // keep "41–85 KIAS" in reading order inside Arabic text
  const arc = (color) => spec.arcs.find((a) => a.color === color);
  const range = (a) => ltr(`${a.from}–${a.to} ${spec.unit}`);
  const red = spec.redlines[0].value;
  const fill = (s) => s
    .replace('{white}', range(arc('white'))).replace('{green}', range(arc('green'))).replace('{yellow}', range(arc('yellow')))
    .replace('{red}', ltr(`${red} ${spec.unit}`)).replace('{va}', ltr(`${data.va.kias} ${spec.unit}`)).replace('{weight}', ltr(`${data.va.weight_lb} lb`));

  // ---- instrument
  const dial = el('g', { class: 'dial' }, svg);
  el('circle', { cx: C[0], cy: C[1], r: R.bezel, class: 'dial-bezel' }, dial);
  el('circle', { cx: C[0], cy: C[1], r: R.face, class: 'dial-face' }, dial);
  for (const a of spec.arcs) {
    el('path', { d: arcPath(C[0], C[1], BAND[a.band], angle(a.from), angle(a.to)), class: `arc-${a.color}`, fill: 'none', 'stroke-width': BAND_WIDTH }, dial);
  }
  for (let v = spec.ticks.minor_from; v <= spec.max + 1e-9; v += spec.ticks.minor_step) {
    const major = spec.ticks.major.includes(v);
    const [x0, y0] = polar(C[0], C[1], major ? R.tickMajor : R.tickMinor, angle(v));
    const [x1, y1] = polar(C[0], C[1], R.tickOuter, angle(v));
    el('line', { x1: x0, y1: y0, x2: x1, y2: y1, class: major ? 'dial-tick-major' : 'dial-tick' }, dial);
  }
  {
    const [x0, y0] = polar(C[0], C[1], R.inner - BAND_WIDTH / 2, angle(red));
    const [x1, y1] = polar(C[0], C[1], R.tickOuter, angle(red));
    el('line', { x1: x0, y1: y0, x2: x1, y2: y1, class: 'arc-red', 'stroke-width': 11 }, dial);
  }
  for (const v of spec.labels) {
    const [x, y] = polar(C[0], C[1], R.numbers, angle(v));
    el('text', { x, y: y + 13, class: 'dial-number', 'text-anchor': 'middle', direction: 'ltr' }, dial).textContent = String(v);
  }
  // legends printed on the real instrument stay in English in every edition
  el('text', { x: C[0], y: C[1] + 62, class: 'dial-caption', 'text-anchor': 'middle', direction: 'ltr' }, dial).textContent = 'AIRSPEED';
  el('text', { x: C[0], y: C[1] + 88, class: 'dial-caption', 'text-anchor': 'middle', direction: 'ltr' }, dial).textContent = 'KNOTS';
  el('path', { d: 'M-7 34 L-7 -196 L0 -226 L7 -196 L7 34 Z', class: 'dial-needle', transform: `translate(${C[0]} ${C[1]}) rotate(${angle(0)})` }, dial);
  el('circle', { cx: C[0], cy: C[1], r: 22, class: 'dial-hub' }, dial);

  // ---- V-speed tags on the rim, one per arc end
  const tags = [
    ['V_{S0}', arc('white').from], ['V_{S1}', arc('green').from], ['V_{FE}', arc('white').to],
    ['V_{NO}', arc('green').to], ['V_{NE}', red],
  ];
  for (const [name, value] of tags) {
    const a = angle(value);
    const [x0, y0] = polar(C[0], C[1], R.bezel + 2, a);
    const [x1, y1] = polar(C[0], C[1], R.bezel + 26, a);
    el('line', { x1: x0, y1: y0, x2: x1, y2: y1, class: 'outline-thin' }, svg);
    const [cx, cy] = polar(C[0], C[1], R.bezel + 70, a);
    const tag = el('g', { class: 'speed-tag' }, svg);
    const box = el('rect', { rx: 18, height: 38 }, tag);
    const label = text(tag, cx, cy + 8, `${name} ${value}`, { align: 'center' });
    label.setAttribute('direction', 'ltr');
    const w = label.getBBox().width + 30;
    box.setAttribute('x', cx - w / 2); box.setAttribute('y', cy - 19); box.setAttribute('width', w);
  }

  // ---- callouts: where each leader touches the dial
  const at = (band, value) => { const [x, y] = polar(C[0], C[1], band, angle(value)); return { x, y }; };
  const mid = (a, f = 0.5) => a.from + (a.to - a.from) * f;
  const items = [
    { key: 'white', side: 'right', ...at(R.inner, mid(arc('white'), 0.62)), title: fill(t('white_title')), lines: fill(t('white_lines')).split('\n') },
    { key: 'green', side: 'right', ...at(R.outer, mid(arc('green'), 0.66)), title: fill(t('green_title')), lines: fill(t('green_lines')).split('\n') },
    { key: 'red', side: 'left', ...at(R.tickOuter - 14, red), title: fill(t('red_title')), lines: fill(t('red_lines')).split('\n') },
    { key: 'yellow', side: 'left', ...at(R.outer, mid(arc('yellow'), 0.45)), title: fill(t('yellow_title')), lines: fill(t('yellow_lines')).split('\n') },
  ];
  placeCallouts(el('g', {}, svg), text, items, { left: 400, right: 1200, top: 90, bottom: 830, gap: 54 });

  text(svg, C[0], 892, fill(t('note')), { align: 'center', cls: 'label-small' });
}
