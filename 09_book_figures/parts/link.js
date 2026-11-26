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

/** The link to a part, on top of `base` (a URL without its query or fragment). Defaults are left out. */
export function buildLink(base, { part, view = 'alone', scope = 'part' }) {
  const q = new URLSearchParams({ part });
  if (view !== 'alone') q.set('view', view);
  if (view === '3d' && scope !== 'part') q.set('scope', scope);
  return `${base}?${q}`;
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
