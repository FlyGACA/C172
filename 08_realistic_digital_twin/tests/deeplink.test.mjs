import test from 'node:test';
import assert from 'node:assert/strict';
import { parseLink } from '../js/deeplink.js';
import { SCENARIOS } from '../js/scenarios.js';
import { LESSONS } from '../js/lessons.js';

const parse = (query) => parseLink(new URLSearchParams(query), { scenarios: [...SCENARIOS, ...LESSONS] });

test('absent deep-link parameters leave the default view alone', () => {
  assert.deepEqual(parse('q=low&lang=en'), { mode: null, part: null, scenario: null, lesson: false, rejected: [] });
});

for (const mode of ['exterior', 'cockpit', 'engine', 'systems', 'flight']) {
  test(`accepts the ${mode} mode`, () => {
    const link = parse(`mode=${mode}`);
    assert.equal(link.mode, mode);
    assert.deepEqual(link.rejected, []);
  });
}

for (const s of [...SCENARIOS, ...LESSONS]) {
  test(`accepts the registered scenario or lesson ${s.id}`, () => {
    const link = parse(`scenario=${s.id}`);
    assert.equal(link.scenario, s.id);
    assert.equal(link.lesson, !!s.lesson);
    assert.deepEqual(link.rejected, []);
  });
}

test('accepts a combined view and decodes a dotted part name', () => {
  const link = parse('mode=engine&part=POWERPLANT%2Epropeller&scenario=runup');
  assert.deepEqual(link, { mode: 'engine', part: 'POWERPLANT.propeller', scenario: 'runup', lesson: false, rejected: [] });
  assert.equal(parse('part=PANEL.ASI.needle_ASI').part, 'PANEL.ASI.needle_ASI');
});

for (const [key, values] of Object.entries({
  mode: ['', 'Engine', 'constructor', '__proto__', 'unknown'],
  part: ['', '../ENGINE', '<script>', 'ENGINE', 'ENGINE..piston', 'ENGINE.piston\n', `ENGINE.${'a'.repeat(121)}`],
  scenario: ['', 'RUNUP', 'constructor', '__proto__', 'unknown'],
})) {
  for (const value of values) {
    test(`rejects ${key}=${JSON.stringify(value)} without throwing`, () => {
      const link = parse(new URLSearchParams({ [key]: value }).toString());
      assert.equal(link[key], null);
      assert.equal(link.rejected.length, 1);
      assert.equal(link.rejected[0].key, key);
      assert.ok(link.rejected[0].value.length <= 80);
    });
  }
  test(`rejects repeated ${key} rather than choosing one`, () => {
    const link = parse(`${key}=engine&${key}=cockpit`);
    assert.equal(link[key], null);
    assert.equal(link.rejected.length, 1);
    assert.equal(link.rejected[0].key, key);
  });
}

test('one invalid value does not discard the other valid parameters', () => {
  const link = parse('mode=unknown&scenario=runup&part=POWERPLANT.propeller');
  assert.equal(link.mode, null);
  assert.equal(link.scenario, 'runup');
  assert.equal(link.part, 'POWERPLANT.propeller');
  assert.deepEqual(link.rejected.map((r) => r.key), ['mode']);
});

test('a lesson keeps its flight state when a non-flight mode is requested', () => {
  const link = parse('mode=cockpit&scenario=go_around');
  assert.equal(link.scenario, 'go_around');
  assert.equal(link.mode, null);
  assert.deepEqual(link.rejected.map((r) => r.key), ['mode']);
  assert.equal(parse('mode=flight&scenario=go_around').mode, 'flight');
});

test('a ground scenario is not overwritten by a flight-mode start', () => {
  const link = parse('mode=flight&scenario=runup');
  assert.equal(link.scenario, 'runup');
  assert.equal(link.mode, null);
  assert.deepEqual(link.rejected.map((r) => r.key), ['mode']);
});
