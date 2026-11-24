// The licence statements agree with one another: the MIT text says what it does not cover,
// LICENSING.md names the paths, those paths exist, and the README points to it.
import test from 'node:test';
import assert from 'node:assert/strict';
import { existsSync, readFileSync } from 'node:fs';

const root = new URL('../', import.meta.url);
const read = (p) => readFileSync(new URL(p, root), 'utf8');

test('the MIT text covers the software only and points to LICENSING.md', () => {
  const mit = read('LICENSE');
  assert.match(mit, /^MIT License/);
  assert.match(mit, /software in this repository only/);
  assert.match(mit, /LICENSING\.md/);
  assert.match(mit, /Permission is hereby granted, free of charge/, 'the MIT grant itself is unchanged');
});

test('LICENSING.md reserves the model, the pictures and the handbook, in both languages', () => {
  const doc = read('LICENSING.md');
  assert.match(doc, /All rights reserved/);
  assert.match(doc, /جميع حقوقها محفوظة/);
  for (const word of ['.blend', '.glb', 'Training Handbook', 'plates']) assert.ok(doc.includes(word), word);
  assert.match(doc, /That grant stands for the versions published before this change/, 'it does not claim to take back the earlier grant');
  assert.match(doc, /not affiliated with/);
  assert.match(doc, /ليس تابعًا للهيئة العامة للطيران المدني/);
});

test('every path LICENSING.md names exists', () => {
  const paths = [...read('LICENSING.md').matchAll(/`([^`*]+\/[^`*]*|[\w.-]+\.(?:mjs|py|webp|css))`/g)].map((m) => m[1]).filter((p) => !p.startsWith('.') || p === '.github/');
  assert.ok(paths.length >= 15, `only ${paths.length} paths found`);
  for (const p of paths) assert.ok(existsSync(new URL(p, root)), `${p} is named in LICENSING.md and is not in the repository`);
});

test('the README no longer offers the models under MIT', () => {
  const readme = read('README.md');
  assert.doesNotMatch(readme, /code and models are released under/);
  assert.match(readme, /\[LICENSING\.md\]\(LICENSING\.md\)/);
});
