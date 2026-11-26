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

/** The link to a part, on top of `base` (a URL without its query or fragment). */
export function buildLink(base, state) {
  return `${base}?${new URLSearchParams(linkPairs(state))}`;
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
