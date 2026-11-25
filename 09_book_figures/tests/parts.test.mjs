// Checks on the parts catalogue (09_book_figures/parts/): what the page reads is complete, comes from the
// model's own records and is all in the repository. No browser needed: `npm test`.
import test from 'node:test';
import assert from 'node:assert/strict';
import { existsSync, readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';

const HERE = new URL('../parts/', import.meta.url);
const path = (relative) => fileURLToPath(new URL(relative, HERE));
const text = (relative) => readFileSync(path(relative), 'utf8');
const data = JSON.parse(text('parts.json'));
const page = text('index.html');
const records = JSON.parse(text('../../08_realistic_digital_twin/models/parts_all.json')).parts.filter((p) => !p.group);
const ARABIC = /[؀-ۿ]/;

/** The names of the nodes in a binary glTF file. */
function nodeNames(file) {
  const bytes = readFileSync(file);
  assert.equal(bytes.toString('latin1', 0, 4), 'glTF', `${file} is not a binary glTF file`);
  return JSON.parse(bytes.toString('utf8', 20, 20 + bytes.readUInt32LE(12))).nodes.map((n) => n.name);
}

test('every part of the model is in the catalogue once, under the names the model gives it', () => {
  const drawn = data.parts.flatMap((p) => [p.id, ...p.more.map((m) => m[0])]);
  assert.equal(new Set(data.parts.map((p) => p.id)).size, data.parts.length, 'a part is listed twice');
  assert.deepEqual([...new Set(drawn)].sort(), records.map((p) => p.id).sort());
  const byId = new Map(records.map((p) => [p.id, p]));
  for (const p of data.parts) {
    const r = byId.get(p.id);
    assert.equal(p.s, r.system, p.id);
    assert.ok(p.en && ARABIC.test(p.ar), `${p.id} needs a name in both languages`);
    assert.ok(['poh', 'type_data', 'estimated'].includes(p.st), `${p.id} has no source status`);
  }
});

test('every picture sheet and model file the page asks for is in the repository', () => {
  for (const sheet of [data.thumb, data.large, data.place]) {
    assert.equal(sheet.files.length, Math.ceil(data.parts.length / sheet.per));
    for (const file of sheet.files) assert.ok(existsSync(path(file.f)), `${file.f} is missing`);
  }
  for (const p of data.parts) for (const kind of ['alone', 'place']) assert.ok(existsSync(path(`full/${kind}/${p.k}.png`)), `full/${kind}/${p.k}.png is missing`);
  for (const system of new Set(data.parts.map((p) => p.s))) {
    const names = new Set(nodeNames(path(`m/${system}.glb`)));
    for (const p of data.parts) if (p.s === system) assert.ok(names.has(p.id), `${p.id} is not in m/${system}.glb`);
  }
});

test('the page loads nothing from outside the repository, and everything it loads exists', () => {
  const refs = [...page.matchAll(/\b(?:href|src)="([^"#]+)"/g)].map((m) => m[1]);
  const map = JSON.parse(page.match(/<script type="importmap">([\s\S]*?)<\/script>/)[1]).imports;
  for (const ref of [...refs.filter((r) => !/^https:\/\/([a-z]+\.)?flygaca\.com\//.test(r)), map.three, `${map['three/addons/']}loaders/GLTFLoader.js`, `${map['three/addons/']}controls/OrbitControls.js`, `${map['three/addons/']}environments/RoomEnvironment.js`]) {
    assert.doesNotMatch(ref, /^(https?:)?\/\//, `${ref} is loaded from outside`);
    assert.ok(existsSync(path(ref.split('?')[0])), `${ref} does not exist`);
  }
  assert.doesNotMatch(text('parts.js'), /https?:\/\//);
});

test('the page carries the notice in both languages and says what the model is not', () => {
  assert.ok(page.includes('Not affiliated with GACA'));
  assert.ok(page.includes('غير تابعة'));
  assert.match(page, /no certified fidelity/);
  assert.match(page, /not a parts manual and not for maintenance/);
  assert.doesNotMatch(page + text('parts.js'), /\b1,?198\b/, 'the part count is read from parts.json, not typed into the page');
});

test('the page offers the whole aircraft in 3D, with every control named in both languages', () => {
  for (const id of ['explore', 'around', 'bsolid', 'bfit', 'hide', 'pull', 'spread']) assert.match(page, new RegExp(`id="${id}"`), `#${id} is missing`);
  assert.deepEqual([...page.matchAll(/data-scope="([a-z]+)"/g)].map((m) => m[1]), ['part', 'system', 'aircraft']);
  for (const [, inner] of page.matchAll(/<button[^>]*>([\s\S]*?)<\/button>/g)) assert.ok(inner.includes('ufuq-en') && inner.includes('ufuq-ar'), `a button is in one language only: ${inner.slice(0, 60)}`);
});

test('the stylesheet takes its colours from the Ufuq tokens', () => {
  const css = text('parts.css').replace(/\/\*[\s\S]*?\*\//g, '');
  assert.doesNotMatch(css, /#[0-9a-f]{3,8}\b|\brgba?\(|\bhsla?\(/i, 'a literal colour');
  assert.doesNotMatch(css, /\b(margin|padding|border)-(left|right)\b|\btext-align:\s*(left|right)\b|!important/, 'a physical property or !important');
});
