// Links to one part of the catalogue: what they accept, what they refuse, and that every part can be linked to.
// No browser needed: `npm test`.
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { PART_NAME, SCOPES, VIEWS, buildLink, indexParts, parseLink } from '../parts/link.js';
import { PART_NAME as VIEWER_PART_NAME } from '../../08_realistic_digital_twin/js/deeplink.js';

const path = (relative) => fileURLToPath(new URL(relative, import.meta.url));
const data = JSON.parse(readFileSync(path('../parts/parts.json'), 'utf8'));
const names = new Set(data.parts.flatMap((p) => [p.id, ...p.more.map((m) => m[0])]));
const parse = (query) => parseLink(new URLSearchParams(query), (id) => names.has(id));

test('a part, a view and a scope are read together', () => {
  assert.deepEqual(parse('part=ENGINE.piston_1'), { part: 'ENGINE.piston_1', view: 'alone', scope: 'part', rejected: [] });
  assert.deepEqual(parse('part=ENGINE.piston_1&view=place'), { part: 'ENGINE.piston_1', view: 'place', scope: 'part', rejected: [] });
  assert.deepEqual(parse('part=ENGINE.piston_1&view=3d&scope=aircraft'), { part: 'ENGINE.piston_1', view: '3d', scope: 'aircraft', rejected: [] });
  assert.deepEqual(parse(''), { part: null, view: 'alone', scope: 'part', rejected: [] });
});

test('a part drawn together with another opens that entry', () => {
  const secondary = data.parts.find((p) => p.more.length).more[0][0];
  assert.equal(parse(`part=${secondary}`).part, secondary);
});

test('a part always opens its own entry, and one drawn with another opens that other entry', () => {
  const index = indexParts(data.parts);
  for (const p of data.parts) assert.equal(index.get(p.id), p, `${p.id} does not open its own entry`);
  const nobody = new Set(data.parts.map((p) => p.id));
  for (const p of data.parts) for (const [id] of p.more) if (!nobody.has(id)) assert.equal(index.get(id), p, `${id} does not open ${p.id}`);
  assert.deepEqual([...index.keys()].sort(), [...names].sort());
});

test('a value that fails is named and left out, and the rest still applies', () => {
  const bad = (query, key, reason) => { const l = parse(query); assert.ok(l.rejected.some((r) => r.key === key && r.reason.includes(reason)), `${query}: ${JSON.stringify(l.rejected)}`); return l; };
  assert.equal(bad('part=nope', 'part', 'not a part name').part, null);
  assert.equal(bad('part=ENGINE.no_such_part', 'part', 'no such part').part, null);
  assert.equal(bad(`part=${'A.'.repeat(100)}b`, 'part', 'not a part name').part, null);
  assert.equal(bad('part=<script>alert(1)</script>', 'part', 'not a part name').part, null);
  assert.equal(bad('part=ENGINE.piston_1&view=sideways', 'view', 'no such view').view, 'alone');
  assert.equal(bad('part=ENGINE.piston_1&view=place&scope=aircraft', 'scope', '3D view only').scope, 'part');
  assert.equal(bad('part=ENGINE.piston_1&view=3d&scope=everything', 'scope', 'no such scope').scope, 'part');
  assert.equal(bad('part=ENGINE.piston_1&part=ENGINE.piston_2', 'part', 'more than once').part, null);
  bad('view=3d', 'view', 'needs a part');
  bad('scope=aircraft', 'scope', 'needs a part');
  assert.equal(parse('part=ENGINE.piston_1&view=3d&scope=nope').view, '3d', 'the view still applies when the scope is refused');
});

test('a rejected value is repeated back in part only', () => {
  const l = parse(`part=${'X'.repeat(500)}`);
  assert.ok(l.rejected[0].value.length <= 80);
});

test('a link built is a link read, for every view and scope', () => {
  const base = 'https://example.test/09_book_figures/parts/index.html';
  for (const view of VIEWS) for (const scope of SCOPES) {
    const url = new URL(buildLink(base, { part: 'ENGINE.piston_1', view, scope }));
    assert.equal(url.origin + url.pathname, base);
    const l = parseLink(url.searchParams, (id) => names.has(id));
    assert.deepEqual([l.part, l.view, l.scope, l.rejected.length], ['ENGINE.piston_1', view, view === '3d' ? scope : 'part', 0]);
  }
  assert.equal(buildLink(base, { part: 'ENGINE.piston_1' }), `${base}?part=ENGINE.piston_1`, 'defaults are left out');
});

test('every part in the catalogue can be linked to, and the name check is the viewer\'s', () => {
  assert.equal(PART_NAME.source, VIEWER_PART_NAME.source, 'the catalogue and the Phase 8 viewer check part names the same way');
  for (const id of names) assert.match(id, PART_NAME, `${id} cannot be linked to`);
  assert.ok(names.size >= data.parts.length);
});

test('the Phase 8 viewer links a selected part to the catalogue, in both languages, to a page that exists and parts that exist', () => {
  const app = readFileSync(path('../../08_realistic_digital_twin/js/app.js'), 'utf8');
  const link = app.match(/<a id="inCatalogue" href="([^"]+)"/);
  assert.ok(link, 'showInfo has no link to the catalogue');
  assert.match(link[1], /^\.\.\/09_book_figures\/parts\/index\.html\?part=\$\{encodeURIComponent\(o\.name\)\}$/);
  assert.ok(readFileSync(path('../parts/index.html'), 'utf8').length > 0);
  const strings = readFileSync(path('../../08_realistic_digital_twin/js/i18n.js'), 'utf8');
  assert.equal([...strings.matchAll(/inCatalogue: '([^']+)'/g)].length, 2, 'one string for each language');
  assert.match(strings, /inCatalogue: '[؀-ۿ]/, 'the Arabic string is in Arabic');
  // Every part the viewer can show opens a part of the catalogue.
  const model = JSON.parse(readFileSync(path('../../08_realistic_digital_twin/models/model_index_high.json'), 'utf8'));
  for (const part of model.parts) {
    const l = parse(`part=${encodeURIComponent(part.id)}`);
    assert.equal(l.part, part.id, `${part.id}: ${JSON.stringify(l.rejected)}`);
  }
});
