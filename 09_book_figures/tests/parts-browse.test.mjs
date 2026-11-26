// Browsing the catalogue: search folding, names for every system and source, the list's link state, the page's controls.
// No browser needed: `npm test`.
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { fold, words, haystack, matches } from '../parts/search.js';
import { ORDER, SOURCE_NAMES, systemName } from '../parts/names.js';
import { SOURCES, MAX_QUERY, parseList, listPairs } from '../parts/link.js';

const path = (relative) => fileURLToPath(new URL(relative, import.meta.url));
const data = JSON.parse(readFileSync(path('../parts/parts.json'), 'utf8'));
const page = readFileSync(path('../parts/index.html'), 'utf8');
const systems = [...new Set(data.parts.map((p) => p.s))];

test('Arabic spellings that differ only in hamza, ya, ta marbuta or digits find each other', () => {
  assert.equal(fold('الجناح الأيسر'), fold('الجناح الايسر'));
  assert.equal(fold('مقصورة'), fold('مقصوره'));
  assert.equal(fold('٦٠ أمبير'), '60 امبير');
  assert.equal(fold('ENGINE.piston_1'), 'engine piston 1');
});

test('every word of a search must match, in any order, in English, Arabic or the id', () => {
  const part = data.parts.find((p) => p.id === 'AIRFRAME.baggage_door');
  const hay = haystack(part);
  assert.ok(matches(hay, words('door baggage')));
  assert.ok(matches(hay, words('باب الامتعة')));
  assert.ok(matches(hay, words('airframe.baggage')));
  assert.ok(!matches(hay, words('baggage propeller')));
  assert.ok(matches(hay, words('')));
});

test('every system in the catalogue has an English and an Arabic name and a place in the order', () => {
  for (const s of systems) {
    const n = systemName(s);
    assert.ok(n.en && n.en !== s && n.ar && n.ar !== s, `${s} has no real name: ${JSON.stringify(n)}`);
    assert.ok(ORDER.includes(s), `${s} is not in ORDER`);
  }
  assert.equal(new Set(ORDER).size, ORDER.length);
});

test('every source has names in both languages and a note', () => {
  for (const s of SOURCES) { const n = SOURCE_NAMES[s]; assert.ok(n && n.en && n.ar && n.note && n.note.en && n.note.ar, s); }
  assert.ok([...new Set(data.parts.map((p) => p.st))].every((s) => SOURCES.includes(s)));
});

test('the list state is read, refused and written back', () => {
  const list = (q) => parseList(new URLSearchParams(q), systems);
  assert.deepEqual(list('q=door&system=AIRFRAME&source=poh'), { q: 'door', system: 'AIRFRAME', source: 'poh', rejected: [] });
  assert.equal(list('system=NOPE').system, '');
  assert.equal(list('system=NOPE').rejected[0].key, 'system');
  assert.equal(list('source=guess').rejected[0].key, 'source');
  assert.equal(list(`q=${'a'.repeat(MAX_QUERY + 1)}`).q, '');
  assert.equal(list('q=a&q=b').rejected[0].reason, 'given more than once');
  assert.deepEqual(listPairs({ q: ' door ', system: '', source: 'poh' }), [['q', 'door'], ['source', 'poh']]);
  assert.deepEqual(listPairs({}), []);
});

test('the page has its search, filters, count, key and back-to-top, and every button is bilingual', () => {
  for (const id of ['q', 'fsys', 'fsrc', 'fclear', 'count', 'key-list', 'totop', 'blink', 'd-full', 'prev', 'next', 'close']) assert.match(page, new RegExp(`id="${id}"`), `#${id} is missing`);
  for (const b of page.match(/<button[\s\S]*?<\/button>/g)) assert.ok(b.includes('ufuq-en') && b.includes('ufuq-ar'), `button not bilingual: ${b.slice(0, 80)}`);
});
