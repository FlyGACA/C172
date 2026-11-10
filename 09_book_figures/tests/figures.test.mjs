// Checks on the book-figure manifest, text and provenance. No browser needed: `npm test`.
// (Layout problems are caught by `npm run figures:check`, which builds every figure in Chromium.)
import test from 'node:test';
import assert from 'node:assert/strict';
import { existsSync, readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';

const HERE = new URL('../', import.meta.url);
const path = (relative) => fileURLToPath(new URL(relative, HERE));
const read = (relative) => JSON.parse(readFileSync(path(relative), 'utf8'));

const manifest = read('figures.json');
const poh = read('../08_realistic_digital_twin/data/poh_references.json');
const catalog = read('../08_realistic_digital_twin/data/parts_catalog.json');
const instruments = read('../08_realistic_digital_twin/data/instruments.json').instruments;
const modelIndex = read('../08_realistic_digital_twin/models/model_index_high.json');
const { POH } = await import('../../shared/js/sim.js');

const KINDS = new Set(['instrument', 'schematic', 'illustration', 'photo', 'chart', 'diagram']);
const METHODS = new Set(['vector-data', 'vector-authored', 'render-3d', 'photo']);
const ARABIC = /[؀-ۿ]/;
const placeholders = (s) => (s.match(/\{[a-z_]+\}/g) || []).sort().join(' ');

test('manifest entries are complete, bilingual and uniquely numbered', () => {
  assert.deepEqual(manifest.languages, ['en', 'ar']);
  const ids = manifest.figures.map((f) => f.id);
  const numbers = manifest.figures.map((f) => f.number);
  assert.equal(new Set(ids).size, ids.length, 'duplicate figure id');
  assert.equal(new Set(numbers).size, numbers.length, 'duplicate figure number');
  for (const figure of manifest.figures) {
    assert.match(figure.id, /^[a-z0-9]+(-[a-z0-9]+)*$/, `${figure.id}: id must be kebab-case`);
    assert.ok(KINDS.has(figure.kind), `${figure.id}: unknown kind ${figure.kind}`);
    assert.ok(METHODS.has(figure.method), `${figure.id}: unknown method ${figure.method}`);
    assert.ok(figure.status in manifest.status_labels, `${figure.id}: unknown status ${figure.status}`);
    assert.ok(figure.width_mm >= 60 && figure.width_mm <= 210, `${figure.id}: width_mm out of range`);
    assert.ok(figure.title.en.trim() && ARABIC.test(figure.title.ar), `${figure.id}: title must be bilingual`);
    assert.ok(existsSync(path(`js/figures/${figure.module}`)), `${figure.id}: module missing`);
    assert.ok(figure.sources?.length, `${figure.id}: a figure must say where its facts come from`);
    for (const source of figure.sources) assert.ok(source.what?.trim() && (source.poh || source.model), `${figure.id}: incomplete source`);
  }
});

test('every string exists in both languages with the same placeholders', () => {
  for (const figure of manifest.figures) {
    const { strings } = read(figure.data);
    assert.deepEqual(Object.keys(strings.ar).sort(), Object.keys(strings.en).sort(), `${figure.id}: en/ar keys differ`);
    for (const [key, en] of Object.entries(strings.en)) {
      const ar = strings.ar[key];
      assert.ok(en.trim() && ar.trim(), `${figure.id}: empty string ${key}`);
      assert.ok(ARABIC.test(ar), `${figure.id}: ${key} has no Arabic text`);
      assert.equal(placeholders(ar), placeholders(en), `${figure.id}: ${key} placeholders differ`);
    }
  }
});

test('facts are traceable to the POH reference table and the parts catalogue', () => {
  const keys = new Set(poh.values.map((value) => value.key));
  const patterns = new Set(catalog.entries.map((entry) => entry.match));
  for (const figure of manifest.figures) {
    const data = read(figure.data);
    for (const key of data.poh_keys || []) assert.ok(keys.has(key), `${figure.id}: POH key ${key} not in poh_references.json`);
    for (const ref of data.catalog_refs || []) assert.ok(patterns.has(ref), `${figure.id}: catalogue entry ${ref} not found`);
  }
});

test('airspeed figure: instrument data, simulation constants and POH table agree', () => {
  const data = read('data/asi_markings.json');
  const asi = instruments[data.instrument];
  const arc = (color) => { const a = asi.arcs.find((entry) => entry.color === color); return [a.from, a.to]; };
  assert.deepEqual(arc('white'), POH.asiWhite);
  assert.deepEqual(arc('green'), POH.asiGreen);
  assert.deepEqual(arc('yellow'), POH.asiYellow);
  assert.equal(asi.redlines[0].value, POH.vne);
  assert.equal(data.va.kias, POH.va2300);
  const limits = poh.values.find((value) => value.key === data.va.poh_key).value;
  assert.ok(limits.includes(`VA ${data.va.kias} at ${data.va.weight_lb} lb`), 'manoeuvring speed differs from the POH table');
  const markings = poh.values.find((value) => value.key === 'airspeed.markings_KIAS').value;
  for (const [name, color] of [['white', 'white'], ['green', 'green'], ['yellow', 'yellow']]) {
    assert.ok(markings.includes(`${name} ${arc(color).join('-')}`), `${name} arc differs from the POH table`);
  }
});

test('fuel figure: capacities come from the simulation constants that cite the POH', () => {
  const standard = poh.values.find((value) => value.key === 'fuel.standard_tanks').value;
  assert.ok(standard.includes(`${POH.fuelPerTankTotal} gal each`));
  assert.ok(standard.includes(`${POH.fuelPerTankTotal * 2} total`));
  assert.ok(standard.includes(`${POH.fuelPerTankUsable * 2} usable`));
});

test('3D-rendered figures: recipe, picture and label anchors are consistent with the model', () => {
  const parts = new Set(modelIndex.parts.map((part) => part.name));
  for (const figure of manifest.figures.filter((f) => f.method === 'render-3d')) {
    const recipe = read(figure.render);
    const data = read(figure.data);
    const render = read(data.render);
    assert.equal(recipe.id, figure.id);
    for (const group of [...recipe.highlights, ...recipe.anchors]) {
      for (const id of group.ids) assert.ok(parts.has(id), `${figure.id}: ${id} is not a part of the model`);
    }
    const png = readFileSync(path(`renders/${render.image}`));
    assert.equal(png.subarray(1, 4).toString(), 'PNG');
    assert.deepEqual([png.readUInt32BE(16), png.readUInt32BE(20)], [render.width, render.height], `${figure.id}: anchors were not exported from this image`);
    assert.deepEqual([render.width, render.height], recipe.resolution, `${figure.id}: committed render is not full resolution`);
    for (const { anchor } of data.callouts) {
      const point = render.anchors[anchor];
      assert.ok(point?.visible, `${figure.id}: label anchor ${anchor} is missing or hidden`);
      assert.ok(point.x >= 0 && point.x <= render.width && point.y >= 0 && point.y <= render.height);
      assert.ok(point.label_en && ARABIC.test(point.label_ar), `${figure.id}: ${anchor} has no bilingual model label`);
    }
  }
});

test('built files are present for every figure and language', () => {
  for (const figure of manifest.figures) {
    for (const lang of manifest.languages) {
      const pdf = path(`out/${lang}/${figure.id}.pdf`);
      assert.ok(existsSync(pdf), `${figure.id} [${lang}]: run "npm run figures"`);
      assert.equal(readFileSync(pdf).subarray(0, 5).toString(), '%PDF-');
      assert.ok(existsSync(path(`out/preview/${figure.id}.${lang}.png`)), `${figure.id} [${lang}]: preview missing`);
      if (figure.method !== 'render-3d') {
        const svg = readFileSync(path(`out/${lang}/${figure.id}.svg`), 'utf8');
        assert.ok(svg.includes('<svg') && svg.includes(lang === 'ar' ? 'direction="rtl"' : 'direction="ltr"'));
      }
    }
  }
});
