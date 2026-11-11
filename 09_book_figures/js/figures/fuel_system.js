// Fuel system schematic.
// Method: authored vector diagram. This is the kind of figure where realism would get in the way:
// the reader has to follow the flow, so the system is reduced to symbols and four line codes.
// The aircraft's left is on the left of the page in every language edition.

import { el, roundedPath, arrowHead } from '../svg.js';
import { POH } from '../../../shared/js/sim.js';

export const size = [1600, 1180];

export async function draw({ svg, t, text, dir, json }) {
  const poh = await json('../08_realistic_digital_twin/data/poh_references.json');
  const engineModel = poh.values.find((v) => v.key === 'engine.model').value;
  const ltr = (s) => (dir === 'rtl' ? `⁦${s}⁩` : s);
  const fill = (s) => s
    .replace('{total}', ltr(POH.fuelPerTankTotal)).replace('{usable}', ltr(POH.fuelPerTankUsable))
    .replace('{total_all}', ltr(POH.fuelPerTankTotal * 2)).replace('{usable_all}', ltr(POH.fuelPerTankUsable * 2));
  const back = el('g', {}, svg);        // pipes
  const parts = el('g', {}, svg);       // components
  const notes = el('g', {}, svg);       // labels
  const fuel = (points, cls = 'pipe-fuel') => el('path', { d: roundedPath(points, 26), class: cls }, back);
  const vent = (points) => {
    el('path', { d: roundedPath(points, 22), class: 'pipe-vent' }, back);
    el('path', { d: roundedPath(points, 22), class: 'pipe-vent-core' }, back);
  };
  const flow = (x, y, deg) => arrowHead(parts, x, y, deg, 17);

  // ---------------------------------------------------------------- tanks
  const TANK = { y0: 150, y1: 330, level: 208 };
  const tanks = { left: { x0: 140, x1: 600, sender: 560, riser: 490, cap: 310, drain: 215, label: 335 }, right: { x0: 1000, x1: 1460, sender: 1040, riser: 1110, cap: 1290, drain: 1385, label: 1265 } };
  for (const [side, k] of Object.entries(tanks)) {
    const w = k.x1 - k.x0;
    el('rect', { x: k.x0, y: TANK.y0, width: w, height: TANK.y1 - TANK.y0, rx: 20, class: 'outline f-paper' }, parts);
    const clip = el('clipPath', { id: `tank-${side}` }, svg);
    el('rect', { x: k.x0 + 2, y: TANK.y0 + 2, width: w - 4, height: TANK.y1 - TANK.y0 - 4, rx: 18 }, clip);
    el('rect', { x: k.x0, y: TANK.level, width: w, height: TANK.y1 - TANK.level, class: 'fuel-fill', 'clip-path': `url(#tank-${side})` }, parts);
    el('line', { x1: k.x0 + 4, y1: TANK.level, x2: k.x1 - 4, y2: TANK.level, stroke: 'var(--fuel)', 'stroke-width': 3 }, parts);
    el('rect', { x: k.x0, y: TANK.y0, width: w, height: TANK.y1 - TANK.y0, rx: 20, class: 'outline f-none' }, parts);
    // filler cap
    el('path', { d: `M${k.cap - 34} ${TANK.y0} v-12 q0 -10 10 -10 h48 q10 0 10 10 v12 z`, class: 'outline' }, parts);
    // float-type quantity transmitter
    el('rect', { x: k.sender - 16, y: TANK.y0 - 12, width: 32, height: 24, rx: 5, class: 'outline' }, parts);
    const fx = k.sender + (side === 'left' ? -58 : 58);
    el('line', { x1: k.sender, y1: TANK.y0 + 12, x2: fx, y2: TANK.level - 8, class: 'outline-thin' }, parts);
    el('ellipse', { cx: fx, cy: TANK.level - 8, rx: 17, ry: 11, class: 'outline f-paper' }, parts);
    // sump drain
    el('path', { d: `M${k.drain - 11} ${TANK.y1} v22 h22 v-22`, class: 'outline' }, parts);
    el('line', { x1: k.drain - 20, y1: TANK.y1 + 22, x2: k.drain + 20, y2: TANK.y1 + 22, class: 'outline-thin' }, parts);
    el('path', { d: `M${k.drain} ${TANK.y1 + 32} q-9 13 0 20 q9 -7 0 -20z`, fill: 'var(--fuel)' }, parts);
    text(notes, k.label, 262, t(`tank_${side}`), { align: 'center', cls: 'label label-strong' });
    text(notes, k.label, 300, fill(t('tank_capacity')), { align: 'center', cls: 'label-small' });
  }
  text(notes, tanks.left.cap, 112, t('cap'), { align: 'center' });
  text(notes, tanks.right.cap, 112, t('cap_vented'), { align: 'center' });
  // vent slots on the right-hand cap
  for (const dx of [-12, 0, 12]) el('line', { x1: tanks.right.cap + dx, y1: 134, x2: tanks.right.cap + dx, y2: 144, class: 'outline-thin' }, parts);
  text(notes, tanks.left.drain + 34, TANK.y1 + 34, t('sump_drain'), { align: 'left' });
  text(notes, tanks.left.drain + 34, TANK.y1 + 64, t('sump_drain_note'), { align: 'left', cls: 'label-small' });

  // ---------------------------------------------------------------- vents
  vent([[tanks.left.riser, TANK.y0], [tanks.left.riser, 84], [tanks.right.riser, 84], [tanks.right.riser, TANK.y0]]);
  text(notes, 800, 62, t('vent_crossover'), { align: 'center' });
  vent([[176, TANK.y0], [176, 84], [72, 84], [72, 432]]);
  el('circle', { cx: 72, cy: 268, r: 23, class: 'outline f-paper' }, parts);                  // check valve
  // the valve passes air toward the tank and stops fuel running out, so the arrow points along the line to the tank
  el('path', { d: 'M61 278 L83 278 L72 258 Z', class: 'arrow' }, parts);
  el('line', { x1: 60, y1: 255, x2: 84, y2: 255, class: 'outline-thin' }, parts);
  text(notes, 44, 478, t('vent_overboard'), { align: 'left' });
  text(notes, 44, 508, t('vent_overboard_note'), { align: 'left', cls: 'label-small' });

  // ---------------------------------------------------------------- quantity indicators
  for (const [side, cx] of [['left', 742], ['right', 858]]) {
    const k = tanks[side];
    el('path', { d: roundedPath([[k.sender, TANK.y0 - 12], [k.sender, 122], [cx, 122], [cx, 176]], 14), class: 'wire' }, back);
    el('circle', { cx, cy: 224, r: 48, class: 'dial-bezel' }, parts);
    el('circle', { cx, cy: 224, r: 40, class: 'dial-face' }, parts);
    el('path', { d: `M${cx - 26} ${224 + 10} A28 28 0 0 1 ${cx + 26} ${224 + 10}`, fill: 'none', stroke: '#f2f3f4', 'stroke-width': 3 }, parts);
    el('line', { x1: cx - 26, y1: 234, x2: cx - 31, y2: 239, stroke: 'var(--limit)', 'stroke-width': 5 }, parts);
    el('line', { x1: cx, y1: 232, x2: cx + 15, y2: 208, stroke: '#f2f3f4', 'stroke-width': 3.5, 'stroke-linecap': 'round' }, parts);
    el('text', { x: cx - 24, y: 254, class: 'dial-caption', 'text-anchor': 'middle', direction: 'ltr', 'font-size': 15 }, parts).textContent = 'E';
    el('text', { x: cx + 24, y: 254, class: 'dial-caption', 'text-anchor': 'middle', direction: 'ltr', 'font-size': 15 }, parts).textContent = 'F';
  }
  text(notes, 800, 318, t('indicators'), { align: 'center' });
  text(notes, 800, 348, t('indicators_note'), { align: 'center', cls: 'label-small' });

  // ---------------------------------------------------------------- supply to the selector valve
  const SEL = { x: 800, y: 548, w: 250, h: 188 };
  fuel([[tanks.left.x1 - 40, TANK.y1], [tanks.left.x1 - 40, SEL.y], [SEL.x - SEL.w / 2, SEL.y]]);
  fuel([[tanks.right.x0 + 40, TANK.y1], [tanks.right.x0 + 40, SEL.y], [SEL.x + SEL.w / 2, SEL.y]]);
  flow(tanks.left.x1 - 40, 440, 180);
  flow(tanks.right.x0 + 40, 440, 180);
  el('rect', { x: SEL.x - SEL.w / 2, y: SEL.y - SEL.h / 2, width: SEL.w, height: SEL.h, rx: 22, class: 'outline' }, parts);
  el('circle', { cx: SEL.x, cy: SEL.y, r: 40, class: 'outline f-paper' }, parts);
  el('path', { d: `M${SEL.x - 13} ${SEL.y + 30} L${SEL.x - 13} ${SEL.y - 34} L${SEL.x} ${SEL.y - 58} L${SEL.x + 13} ${SEL.y - 34} L${SEL.x + 13} ${SEL.y + 30} Z`, fill: 'var(--limit)', stroke: 'var(--ink)', 'stroke-width': 3, 'stroke-linejoin': 'round' }, parts);
  for (const [word, dx, dy] of [['BOTH', 0, -66], ['LEFT', -84, 8], ['RIGHT', 84, 8], ['OFF', 0, 82]]) {
    el('text', { x: SEL.x + dx, y: SEL.y + dy, class: 'label-tiny label-strong', 'text-anchor': 'middle', direction: 'ltr', fill: 'var(--ink)' }, parts).textContent = word;
  }
  text(notes, 648, 628, t('selector'), { align: 'right' });
  text(notes, 648, 658, t('selector_note'), { align: 'right', cls: 'label-small' });

  // ---------------------------------------------------------------- strainer, primer, carburetor, engine
  const STR = { x: 800, y0: 706, y1: 806, w: 118 };
  fuel([[SEL.x, SEL.y + SEL.h / 2], [SEL.x, STR.y0]]);
  flow(SEL.x, 674, 180);
  el('rect', { x: STR.x - STR.w / 2, y: STR.y0, width: STR.w, height: STR.y1 - STR.y0, rx: 16, class: 'outline f-fuel' }, parts);
  for (let i = -3; i <= 3; i++) el('line', { x1: STR.x + i * 15 - 6, y1: STR.y0 + 58, x2: STR.x + i * 15 + 6, y2: STR.y0 + 42, class: 'outline-thin' }, parts);
  el('line', { x1: STR.x - STR.w / 2 + 6, y1: STR.y0 + 50, x2: STR.x + STR.w / 2 - 6, y2: STR.y0 + 50, class: 'hairline' }, parts);
  // strainer drain
  el('path', { d: `M${STR.x - STR.w / 2} ${STR.y1 - 20} h-38 v26`, class: 'pipe-fuel-thin' }, back);
  el('line', { x1: STR.x - STR.w / 2 - 54, y1: STR.y1 + 8, x2: STR.x - STR.w / 2 - 22, y2: STR.y1 + 8, class: 'outline-thin' }, parts);
  el('path', { d: `M${STR.x - STR.w / 2 - 38} ${STR.y1 + 18} q-9 13 0 20 q9 -7 0 -20z`, fill: 'var(--fuel)' }, parts);
  text(notes, 648, 748, t('strainer'), { align: 'right' });
  text(notes, 648, 822, t('strainer_drain'), { align: 'right', cls: 'label-small' });

  const CARB = { x: 800, y0: 916, y1: 1030, w: 176 };
  const ENG = { x0: 520, x1: 1080, y0: 1030, y1: 1132 };
  fuel([[STR.x, STR.y1], [STR.x, CARB.y0]]);
  flow(STR.x, 866, 180);
  el('rect', { x: ENG.x0, y: ENG.y0, width: ENG.x1 - ENG.x0, height: ENG.y1 - ENG.y0, rx: 20, class: 'outline' }, parts);
  el('rect', { x: CARB.x - CARB.w / 2, y: CARB.y0, width: CARB.w, height: CARB.y1 - CARB.y0 + 4, rx: 16, class: 'outline f-paper' }, parts);
  el('path', { d: `M${CARB.x - 40} ${CARB.y0 + 14} q26 43 0 86 M${CARB.x + 40} ${CARB.y0 + 14} q-26 43 0 86`, class: 'outline-thin' }, parts);   // venturi
  el('line', { x1: CARB.x - 17, y1: CARB.y0 + 44, x2: CARB.x + 17, y2: CARB.y0 + 70, class: 'outline-thin', 'stroke-width': 4.5 }, parts);       // throttle plate
  text(notes, CARB.x + CARB.w / 2 + 22, CARB.y0 + 44, t('carburetor'), { align: 'left' });
  text(notes, (ENG.x0 + ENG.x1) / 2, ENG.y0 + 50, t('engine'), { align: 'center', cls: 'label label-strong' });
  el('text', { x: (ENG.x0 + ENG.x1) / 2, y: ENG.y0 + 82, class: 'label-small', 'text-anchor': 'middle', direction: 'ltr' }, notes).textContent = engineModel;

  // primer: draws from the strainer, delivers to the intake ports
  const PR = { x0: 1066, x1: 1166, y: 756 };
  fuel([[STR.x + STR.w / 2, PR.y], [PR.x0, PR.y]], 'pipe-fuel-thin');
  fuel([[PR.x0 + 30, PR.y + 22], [PR.x0 + 30, ENG.y0 + 51], [ENG.x1, ENG.y0 + 51]], 'pipe-fuel-thin');
  arrowHead(parts, PR.x0 + 30, 918, 180, 13);
  el('rect', { x: PR.x0, y: PR.y - 22, width: PR.x1 - PR.x0, height: 44, rx: 8, class: 'outline f-paper' }, parts);
  el('line', { x1: PR.x1, y1: PR.y, x2: PR.x1 + 50, y2: PR.y, class: 'outline-thin', 'stroke-width': 7 }, parts);
  el('circle', { cx: PR.x1 + 68, cy: PR.y, r: 21, class: 'outline f-ink' }, parts);
  text(notes, (PR.x0 + PR.x1) / 2 + 30, PR.y - 44, t('primer'), { align: 'center' });
  text(notes, PR.x0 + 54, 908, t('primer_line'), { align: 'left', cls: 'label-small' });

  // engine controls
  for (const [key, y, colour] of [['throttle', CARB.y0 + 34, 'f-ink'], ['mixture', CARB.y0 + 84, 'f-limit']]) {
    el('path', { d: `M388 ${y} H${CARB.x - CARB.w / 2}`, class: 'linkage' }, back);
    el('line', { x1: 318, y1: y, x2: 388, y2: y, class: 'outline-thin', 'stroke-width': 7 }, parts);
    el('circle', { cx: 300, cy: y, r: 21, class: `outline ${colour}` }, parts);
    text(notes, 262, y + 10, t(key), { align: 'right' });
  }

  // ---------------------------------------------------------------- key facts and line code
  const NOTE = { x: 1128, y: 394, w: 432 };
  const box = el('rect', { x: NOTE.x, y: NOTE.y, width: NOTE.w, rx: 14, class: 'note-box' }, notes);
  let cursor = NOTE.y + 48;
  for (const key of ['note_1', 'note_2', 'note_3']) {
    const lines = fill(t(key)).split('\n');
    const bx = dir === 'rtl' ? NOTE.x + NOTE.w - 28 : NOTE.x + 28;
    el('circle', { cx: bx, cy: cursor - 8, r: 5, fill: 'var(--ink-soft)' }, notes);
    text(notes, dir === 'rtl' ? bx - 20 : bx + 20, cursor, lines.join('\n'), { align: dir === 'rtl' ? 'right' : 'left', cls: 'label-small', fill: 'var(--ink)' });
    cursor += lines.length * 24 * (dir === 'rtl' ? 1.42 : 1.22) + 16;
  }
  box.setAttribute('height', cursor - NOTE.y - 22);

  const LEG = { x: 44, y: 1058 };
  const sample = (i) => [[LEG.x, LEG.y + i * 34], [LEG.x + 92, LEG.y + i * 34]];
  el('path', { d: roundedPath(sample(0)), class: 'pipe-fuel' }, notes);
  el('path', { d: roundedPath(sample(1)), class: 'pipe-vent' }, notes);
  el('path', { d: roundedPath(sample(1)), class: 'pipe-vent-core' }, notes);
  el('path', { d: roundedPath(sample(2)), class: 'wire' }, notes);
  el('path', { d: roundedPath(sample(3)), class: 'linkage' }, notes);
  ['legend_fuel', 'legend_vent', 'legend_wire', 'legend_link'].forEach((key, i) => {
    text(notes, LEG.x + 112, LEG.y + i * 34 + 8, t(key), { align: 'left', cls: 'label-small', fill: 'var(--ink)' });
  });
}
