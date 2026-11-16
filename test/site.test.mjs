// The site's front door: the root index.html and what it loads.
import test from 'node:test';
import assert from 'node:assert/strict';
import { existsSync, readFileSync } from 'node:fs';
import { join } from 'node:path';
import { ROOT, build, partCount, phases } from '../scripts/build_site.mjs';

const read = (rel) => readFileSync(join(ROOT, rel), 'utf8');
const home = read('index.html');
const data = JSON.parse(read('site/home-data.js').replace(/^[\s\S]*?window\.HOME=/, '').replace(/;\s*$/, ''));

test('site/home-data.js is current', async () => {
  assert.equal(read('site/home-data.js'), await build(), 'run `npm run build:site`');
});

test('the home page opens the Phase 8 aircraft, not an archived phase', () => {
  assert.doesNotMatch(home, /http-equiv="refresh"/i, 'the front door must not redirect');
  assert.match(home, /href="08_realistic_digital_twin\/index\.html"/);
  for (const [, href] of home.matchAll(/class="ufuq-btn ufuq-btn--primary" href="([^"]+)"/g)) assert.ok(href.startsWith('08_realistic_digital_twin/'), `${href} is a primary action that leaves Phase 8`);
});

test('everything the home page loads or links to exists in the repository', () => {
  const refs = [...home.matchAll(/\b(?:href|src)="([^"#]+)"/g)].map((m) => m[1]).filter((r) => !/^https?:/.test(r));
  assert.ok(refs.length > 10);
  for (const ref of refs) {
    assert.ok(!ref.startsWith('..') && !ref.startsWith('/'), `${ref} points outside the site`);
    assert.ok(existsSync(join(ROOT, ref.split('?')[0])), `${ref} does not exist`);
  }
  for (const p of data.phases) if (p.page) assert.ok(existsSync(join(ROOT, p.page)), `${p.page} does not exist`);
});

test('the page carries the notice in both languages and says what the model is not', () => {
  assert.ok(home.includes('Not affiliated with GACA'));
  assert.ok(home.includes('غير تابعة'));
  assert.match(home, /no certified fidelity/);
  assert.match(home, /not a flight training device/);
});

test('facts on the page come from their sources', () => {
  assert.equal(data.parts, partCount(read('08_realistic_digital_twin/docs/06_parts_index.md')));
  assert.ok(data.parts > 0);
  assert.doesNotMatch(home, /\b1,?198\b/, 'the part count is read from the parts index, not typed into the page');
  assert.deepEqual(data.lessons.map((l) => l.id), ['stall_recovery', 'go_around', 'engine_failure_after_takeoff']);
  assert.deepEqual(phases('07 — Kinematic twin (2026-11-06):\n- x\n\n01 — First.\n').map((p) => [p.id, p.title, p.date]), [['07', 'Kinematic twin', '2026-11-06'], ['01', 'First', null]]);
});
