// Automatic callouts (boundary labelling).
//
// Labels sit in a column to the left and a column to the right of the artwork and are joined to the
// part they name by a leader line. Within a column the labels keep the vertical order of the points
// they refer to, so leaders do not cross, and labels are pushed apart until none overlap. Nothing is
// placed by hand: change the camera or the model, re-run the build, and the labels follow.

import { el } from './svg.js';

/**
 * @param parent  SVG group to draw into
 * @param text    text factory from svg.js (already bound to the language direction)
 * @param items   [{ key, x, y, side?, title, lines?, color? }]  x,y = anchor in figure units
 * @param opts    { left, right, top, bottom, gap, stub }  left/right = x of each label column's inner edge
 * @returns       placed items with the final label position
 */
export function placeCallouts(parent, text, items, opts) {
  const { left, right, top, bottom, gap = 26, stub = 34, centre = (left + right) / 2 } = opts;
  const placed = [];
  for (const side of ['left', 'right']) {
    const column = items
      .filter((item) => (item.side || (item.x < centre ? 'left' : 'right')) === side)
      .sort((a, b) => a.y - b.y);
    if (!column.length) continue;
    const edge = side === 'left' ? left : right;
    const align = side === 'left' ? 'right' : 'left';
    // 1. draw every label at the origin to measure it
    const blocks = column.map((item) => {
      const group = el('g', { class: 'callout' }, parent);
      const title = text(group, 0, 0, item.title, { align, cls: 'label label-strong' });
      let height = title.getBBox().height;
      if (item.lines?.length) {
        const sub = text(group, 0, height * 0.42, item.lines.join('\n'), { align, cls: 'label-small', valign: 'top' });
        height = height * 0.42 + sub.getBBox().height + 12;
      }
      return { item, group, height, firstLine: title.getBBox().height };
    });
    // 2. start each label level with its anchor, then resolve overlaps downwards and upwards
    const ys = blocks.map((b) => b.item.y - b.firstLine / 2);
    for (let i = 1; i < blocks.length; i++) ys[i] = Math.max(ys[i], ys[i - 1] + blocks[i - 1].height + gap);
    const overflow = ys[blocks.length - 1] + blocks[blocks.length - 1].height - bottom;
    if (overflow > 0) {
      ys[blocks.length - 1] -= overflow;
      for (let i = blocks.length - 2; i >= 0; i--) ys[i] = Math.min(ys[i], ys[i + 1] - blocks[i].height - gap);
    }
    if (ys[0] < top) {
      ys[0] = top;
      for (let i = 1; i < blocks.length; i++) ys[i] = Math.max(ys[i], ys[i - 1] + blocks[i - 1].height + gap);
    }
    // 3. position the labels and draw the leaders
    blocks.forEach((block, index) => {
      const y = ys[index];
      const baseline = y + block.firstLine * 0.78;
      block.group.setAttribute('transform', `translate(${edge.toFixed(1)} ${baseline.toFixed(1)})`);
      const startX = side === 'left' ? edge + 14 : edge - 14;
      const elbowX = side === 'left' ? startX + stub : startX - stub;
      const midY = y + block.firstLine / 2;
      const { x, y: ay } = block.item;
      const d = `M${startX.toFixed(1)} ${midY.toFixed(1)} L${elbowX.toFixed(1)} ${midY.toFixed(1)} L${x.toFixed(1)} ${ay.toFixed(1)}`;
      el('path', { class: 'leader-halo', d }, parent);       // keeps the leader readable over dark artwork
      el('path', { class: 'leader', d }, parent);
      el('circle', { class: 'leader-dot', cx: x.toFixed(1), cy: ay.toFixed(1), r: 6.5, fill: block.item.color || undefined }, parent);
      placed.push({ ...block.item, side, labelY: y, labelHeight: block.height });
    });
  }
  return placed;
}
