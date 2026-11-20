// The C172N training handbook: its page is current, and every number it prints comes from the records it cites.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, existsSync } from 'node:fs';
import { dirname, join, normalize } from 'node:path';
import { fileURLToPath } from 'node:url';
import * as C from '../content.mjs';
import { loadData, render, sourceText } from '../build.mjs';

const HERE = join(dirname(fileURLToPath(import.meta.url)), '..');
const ROOT = join(HERE, '..');
const data = await loadData();
const html = await render(data);

// Numbers as written: thousands separators dropped, fractions and ranges split into their numbers.
const numbers = (text) => (String(text).replace(/(\d)[,   ](?=\d{3}\b)/g, '$1').match(/\d+(?:\.\d+)?/g) || []);

function assertNumbersFrom(texts, refs, where) {
  const source = new Set(numbers(sourceText(data, refs)));
  for (const text of texts) {
    for (const n of numbers(text)) assert.ok(source.has(n), `${where}: ${n} is not in ${refs.join(', ') || 'any cited record'} ("${text}")`);
  }
}

test('index.html is current', () => {
  assert.equal(readFileSync(join(HERE, 'index.html'), 'utf8'), html, 'run node 11_training_handbook/build.mjs');
});

test('every number in the text comes from a record the block cites', () => {
  for (const section of C.SECTIONS) {
    for (const [k, b] of section.blocks.entries()) {
      const where = `${section.id} block ${k + 1}`;
      if (b.type === 'p' || b.type === 'note') assertNumbersFrom([b.en, b.ar], b.refs, where);
      if (b.type === 'facts') for (const r of b.rows) assertNumbersFrom([r.en, r.ar, r.label.en, r.label.ar], r.refs, `${where} ${r.label.en}`);
      if (b.type === 'steps') {
        const texts = [b.title.en, b.title.ar, ...b.items.flatMap((i) => [i.en, i.ar]), ...(b.after ? [b.after.en, b.after.ar] : [])];
        assertNumbersFrom(texts, b.refs, `${where} ${b.title.en}`);
      }
      if (b.type === 'list') assertNumbersFrom(b.items.flatMap((i) => [i.en, i.ar]), b.refs, where);
      if (b.type === 'figure') assertNumbersFrom([b.caption.en, b.caption.ar], [], where);
    }
    assertNumbersFrom([section.title.en, section.title.ar], [], section.id);
  }
  // The sources paragraph names files (08_…, 04b_…), so only its edition is checked.
  const sources = [C.SOURCES.en, C.SOURCES.ar].map((t) => t.replace(/\S*\/\S*/g, ''));
  assertNumbersFrom([C.TITLE.en, C.TITLE.ar, C.SUBTITLE.en, C.SUBTITLE.ar, ...C.NOTICE.en, ...C.NOTICE.ar, ...sources], ['src', 'y79:weight.max_takeoff_lb'], 'front matter');
});

test('table captions and headings carry only numbers from the tables they head', () => {
  const allTables = ['tab:STALL_KCAS', 'tab:CLIMB_STANDARD', 'tab:CLIMB_TEMPERATURE', 'tab:CRUISE', 'tab:TAKEOFF', 'tab:LANDING', 'tab:SPEEDS', 'tab:GLIDE', 'inst:ASI', 'inst:TACH', 'inst:OIL_P', 'inst:OIL_T', 'inst:SUCTION', 'poh:tach.green'];
  const captions = C.SECTIONS.flatMap((s) => s.blocks.filter((b) => b.type === 'table').flatMap((b) => [b.caption.en, b.caption.ar]));
  const headings = Object.values(C.TABLE_TEXT).flatMap((l) => [l.en, l.ar]);
  assertNumbersFrom([...captions, ...headings], allTables, 'tables');
});

test('every record cited exists and has a POH page', () => {
  const refs = C.SECTIONS.flatMap((s) => s.blocks.flatMap((b) => [...(b.refs || []), ...(b.rows || []).flatMap((r) => r.refs)]));
  assert.ok(refs.length > 40);
  for (const ref of new Set(refs)) {
    if (ref === 'src') continue;
    assert.doesNotThrow(() => sourceText(data, [ref]), ref);
  }
  assert.doesNotMatch(html, /POH undefined|POH <\/span>/);
});

test('both languages are written, with the same steps', () => {
  for (const section of C.SECTIONS) {
    for (const b of section.blocks) {
      for (const l of [b, b.caption, b.title, b.after, ...(b.rows || []), ...(b.items || []), ...(b.rows || []).map((r) => r.label)].filter((x) => x && 'en' in x)) {
        assert.ok(l.en.trim() && l.ar.trim(), `${section.id}: an empty language in "${l.en}"`);
        if (l.ar !== l.en) assert.match(l.ar, /[؀-ۿ]/, `${section.id}: the Arabic of "${l.en}" has no Arabic`);
        assert.doesNotMatch(l.ar, /[٠-٩]/, 'Arabic-Indic digits: the books use Western digits');
      }
    }
  }
  assert.equal(C.NOTICE.en.length, C.NOTICE.ar.length);
});

test('the page says what it is not, and carries the approved notice word for word', () => {
  const home = readFileSync(join(ROOT, 'index.html'), 'utf8');
  for (const line of [C.BRAND_NOTICE.en, C.BRAND_NOTICE.ar]) {
    assert.ok(home.includes(line), 'the notice is the one the home page prints');
    assert.ok(html.includes(line));
  }
  assert.match(html, /This is not a Pilot&#39;s Operating Handbook|This is not a Pilot's Operating Handbook/);
  assert.match(html, /Never fly from it/);
  assert.match(html, /لا تطِر به أبدًا/);
  assert.match(html, /not affiliated with Cessna or Textron Aviation/);
});

test('Latin runs in the Arabic keep their edge spaces outside the isolate', () => {
  assert.doesNotMatch(html, /<bdi dir="ltr">\s|\s<\/bdi>/);
});

test('everything the page loads or links to exists in the repository', () => {
  const refs = [...html.matchAll(/\b(?:href|src)="([^"#]+)"/g)].map((m) => m[1]).filter((r) => !/^https?:/.test(r));
  assert.ok(refs.length > 5);
  for (const ref of refs) {
    const path = normalize(join(HERE, ref.split('?')[0]));
    assert.ok(existsSync(path.endsWith('/') || ref === '../' || ref === './' ? join(path, 'index.html') : path), ref);
  }
});
