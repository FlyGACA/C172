// Links to one part of the catalogue: ?part=ENGINE.piston_1&view=3d&scope=system
//   part   a part's name in the model, SYSTEM.part, the same names the Phase 8 viewer's own ?part= link uses
//   view   alone | place | 3d              (default alone)
//   scope  part | system | aircraft        (3D only; default part)
// Every value is checked before it is used. One that fails is left out, named in `rejected`, and the rest of the
// link still applies; a bad link never stops the catalogue from opening. No DOM here, so it can be tested alone.

export const VIEWS = ['alone', 'place', '3d'];
export const SCOPES = ['part', 'system', 'aircraft'];
/** A part's name in the model; the same pattern as 08_realistic_digital_twin/js/deeplink.js. */
export const PART_NAME = /^[A-Z][A-Z0-9_]*(\.[A-Za-z0-9_]+)+$/;
const MAX_PART = 120;
const SHOWN = 80; // how much of a rejected value is repeated back

/**
 * @param {URLSearchParams} params
 * @param {(id: string) => boolean} has  whether the catalogue has a part with this name
 * @returns {{ part: string|null, view: string, scope: string, rejected: { key: string, value: string, reason: string }[] }}
 */
export function parseLink(params, has) {
  const link = { part: null, view: 'alone', scope: 'part', rejected: [] };
  const reject = (key, value, reason) => link.rejected.push({ key, value: String(value).slice(0, SHOWN), reason });
  const one = (key) => {
    const all = params.getAll(key);
    if (all.length === 0) return null;
    if (all.length > 1) { reject(key, all.join(','), 'given more than once'); return null; }
    return all[0];
  };
  const part = one('part'), view = one('view'), scope = one('scope');
  if (part !== null) {
    if (part.length > MAX_PART || !PART_NAME.test(part)) reject('part', part, 'not a part name');
    else if (!has(part)) reject('part', part, 'no such part in the catalogue');
    else link.part = part;
  }
  if (link.part === null) {
    if (view !== null) reject('view', view, 'a view needs a part');
    if (scope !== null) reject('scope', scope, 'a scope needs a part');
    return link;
  }
  if (view !== null) { if (VIEWS.includes(view)) link.view = view; else reject('view', view, 'no such view'); }
  if (scope !== null) {
    if (!SCOPES.includes(scope)) reject('scope', scope, 'no such scope');
    else if (link.view !== '3d') reject('scope', scope, 'a scope applies to the 3D view only');
    else link.scope = scope;
  }
  return link;
}

/** The query values of a link to a part, in order. Defaults are left out. */
export function linkPairs({ part, view = 'alone', scope = 'part' }) {
  const pairs = [['part', part]];
  if (view !== 'alone') pairs.push(['view', view]);
  if (view === '3d' && scope !== 'part') pairs.push(['scope', scope]);
  return pairs;
}

/** The link to a part, on top of `base` (a URL without its query or fragment); `extra` adds more query pairs, such as a pose. */
export function buildLink(base, state, extra = []) {
  return `${base}?${new URLSearchParams([...linkPairs(state), ...extra])}`;
}

export const SOURCES = ['poh', 'type_data', 'estimated'];
export const MAX_QUERY = 80;
const SYSTEM_NAME = /^[A-Z][A-Z0-9_]*$/;

/**
 * The list's own state in the address: ?q=piston&system=ENGINE&source=poh, checked like a link to a part.
 * @param {URLSearchParams} params
 * @param {string[]} systems  the systems the catalogue has
 * @returns {{ q: string, system: string, source: string, rejected: { key: string, value: string, reason: string }[] }}
 */
export function parseList(params, systems) {
  const list = { q: '', system: '', source: '', rejected: [] };
  const reject = (key, value, reason) => list.rejected.push({ key, value: String(value).slice(0, SHOWN), reason });
  const one = (key) => {
    const all = params.getAll(key);
    if (all.length === 0) return null;
    if (all.length > 1) { reject(key, all.join(','), 'given more than once'); return null; }
    return all[0];
  };
  const q = one('q'), system = one('system'), source = one('source');
  if (q !== null) { if (q.length > MAX_QUERY) reject('q', q, `longer than ${MAX_QUERY} characters`); else list.q = q.trim(); }
  if (system !== null) { if (SYSTEM_NAME.test(system) && systems.includes(system)) list.system = system; else reject('system', system, 'no such system'); }
  if (source !== null) { if (SOURCES.includes(source)) list.source = source; else reject('source', source, 'no such source'); }
  return list;
}

/** The query values of the list's state, in order. What is empty is left out. */
export function listPairs({ q = '', system = '', source = '' }) {
  const pairs = [];
  if (q.trim()) pairs.push(['q', q.trim().slice(0, MAX_QUERY)]);
  if (system) pairs.push(['system', system]);
  if (source) pairs.push(['source', source]);
  return pairs;
}

/**
 * Every name a link can carry, to the catalogue entry that shows it. A part has an entry of its own; one drawn with
 * another part also resolves to that other entry, but never in place of its own.
 * @param {{ id: string, more: string[][] }[]} parts
 * @returns {Map<string, object>}
 */
export function indexParts(parts) {
  const index = new Map();
  for (const p of parts) for (const m of p.more) index.set(m[0], p);
  for (const p of parts) index.set(p.id, p);
  return index;
}

// A pose: how the controls are set and which parts have been dragged, so a posed aircraft can be shared.
//   pose   key:value pairs for the controls that are off their resting value, e.g. pose=flaps:30,doorL:1,crank:90
//   moved  parts dragged by the reader, id:x:y:z in metres, e.g. moved=ENGINE.piston_1:0.01:0:-0.02
// Same rules as the rest of the link: each entry is checked, one that fails is named in `rejected` and left out.
export const MAX_SHIFTS = 24;
const MAX_POSE = 1200;
const MAX_SHIFT_M = 20;
const decimals = (step) => (String(step).split('.')[1] || '').length;

/**
 * @param {URLSearchParams} params
 * @param {{ key: string, min: number, max: number, step: number, toggle?: boolean, group: string }[]} controls
 * @param {(id: string) => boolean} hasPart  whether the catalogue has a part with this name
 * @returns {{ values: Record<string, number>, shifts: { piece: string, x: number, y: number, z: number }[], rejected: { key: string, value: string, reason: string }[] }}
 */
export function parsePose(params, controls, hasPart) {
  const out = { values: {}, shifts: [], rejected: [] };
  const reject = (key, value, reason) => out.rejected.push({ key, value: String(value).slice(0, SHOWN), reason });
  const one = (key) => {
    const all = params.getAll(key);
    if (all.length === 0) return null;
    if (all.length > 1) { reject(key, all.join(','), 'given more than once'); return null; }
    if (all[0].length > MAX_POSE) { reject(key, all[0], `longer than ${MAX_POSE} characters`); return null; }
    return all[0];
  };
  const by = new Map(controls.map((c) => [c.key, c]));
  const pose = one('pose'), moved = one('moved');
  for (const item of pose ? pose.split(',') : []) {
    const [key, text, ...rest] = item.split(':'), c = by.get(key), v = Number(text);
    if (!c) { reject('pose', item, 'no such control'); continue; }
    if (rest.length || text === undefined || text === '' || !Number.isFinite(v)) { reject('pose', item, 'not a number'); continue; }
    if (key in out.values) { reject('pose', item, 'given more than once'); continue; }
    if (v < c.min || v > c.max) { reject('pose', item, `outside ${c.min} to ${c.max}`); continue; }
    if (c.toggle && v !== 1 && v !== -1) { reject('pose', item, 'a switch is 1 (up) or -1 (down)'); continue; }
    const k = 10 ** decimals(c.step);
    out.values[key] = Math.round(v * k) / k;
  }
  const seen = new Set();
  for (const item of moved ? moved.split(',') : []) {
    const [piece, ...xyz] = item.split(':'), n = xyz.map(Number);
    if (out.shifts.length >= MAX_SHIFTS) { reject('moved', item, `more than ${MAX_SHIFTS} parts`); break; }
    if (!PART_NAME.test(piece) || piece.length > MAX_PART || !hasPart(piece)) { reject('moved', item, 'no such part'); continue; }
    if (xyz.length !== 3 || n.some((x) => !Number.isFinite(x) || Math.abs(x) > MAX_SHIFT_M)) { reject('moved', item, `three distances of at most ${MAX_SHIFT_M} metres`); continue; }
    if (seen.has(piece)) { reject('moved', item, 'given more than once'); continue; }
    seen.add(piece); out.shifts.push({ piece, x: n[0], y: n[1], z: n[2] });
  }
  return out;
}

/**
 * The query values of a pose, in the order of the controls. A control at its resting value is left out, and so is every
 * instrument until one has been set (`values.inst`). A shift smaller than a millimetre in every direction is left out.
 */
export function posePairs(values, controls, shifts = []) {
  const parts = [];
  for (const c of controls) {
    if (c.group === 'instruments' && !values.inst) continue;
    const v = values[c.key], home = c.home ?? 0;
    // with the instruments on, one is always written so that they stay on even if every reading is back at its resting value
    if (v === undefined || (v === home && !(values.inst && c.key === 'asi'))) continue;
    const k = 10 ** decimals(c.step); parts.push(`${c.key}:${Math.round(v * k) / k}`);
  }
  const moved = shifts.filter((s) => Math.max(Math.abs(s.x), Math.abs(s.y), Math.abs(s.z)) >= 0.0005).slice(0, MAX_SHIFTS)
    .map((s) => `${s.piece}:${[s.x, s.y, s.z].map((x) => Math.round(x * 1000) / 1000).join(':')}`);
  const pairs = [];
  if (parts.length) pairs.push(['pose', parts.join(',')]);
  if (moved.length) pairs.push(['moved', moved.join(',')]);
  return pairs;
}
