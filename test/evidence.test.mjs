// R02 acceptance tests — the evidence record and the value gate.
// Run: node --test test/evidence.test.mjs
//
// Six behaviours: missing source, missing page, missing edition, another model, unmet or overlapping
// conditions, and the positive control that a complete record returns its value with its citation.
import test from 'node:test';
import assert from 'node:assert/strict';
import { EVIDENCE, POH_SOURCE, checkEvidence, gateRecord, useValue } from '../shared/js/evidence.js';
import { POH } from '../shared/js/sim.js';
import * as TABLES from '../shared/js/poh_tables.js';

const record = () => ({
  id: 'test.value',
  value: 123,
  unit: 'KIAS',
  page: '2-4 Fig 2-1',
  conditions: {},
  source: { ...POH_SOURCE },
  status: 'verified',
});

test('acceptance 1: a missing source withholds the value', () => {
  const r = record();
  r.source.document = '';
  const g = gateRecord(r);
  assert.equal(g.ok, false);
  assert.ok(g.reasons.includes('missing_source'), g.reasons.join(', '));

  const pending = record();
  pending.status = 'needs-source';
  assert.equal(gateRecord(pending).ok, false);
  assert.ok(gateRecord(pending).reasons.includes('needs-source'));
});

test('acceptance 2: another model prevents reliance', () => {
  const r = record();
  r.source.aircraft = 'Cessna 172P';
  const g = gateRecord(r);
  assert.equal(g.ok, false);
  assert.ok(g.reasons.includes('model_mismatch'), g.reasons.join(', '));

  const wrong = useValue('c172n.vne', { model: 'Cessna 172P' });
  assert.equal(wrong.value, null);
  assert.ok(wrong.reasons.includes('model_mismatch'));
});

test('acceptance 3: a missing page withholds the value', () => {
  const r = record();
  r.page = '';
  const g = gateRecord(r);
  assert.equal(g.ok, false);
  assert.ok(g.reasons.includes('missing_page'));
});

test('acceptance 4: a missing edition withholds the value', () => {
  const r = record();
  r.source.edition = '';
  const g = gateRecord(r);
  assert.equal(g.ok, false);
  assert.ok(g.reasons.includes('missing_edition'));
});

test('acceptance 5: conditions must be supplied and must not overlap', () => {
  assert.equal(useValue('c172n.vfe', { flapsDeg: 20 }).value, 85);

  const atTen = useValue('c172n.vfe', { flapsDeg: 10 });
  assert.equal(atTen.value, null);
  assert.ok(atTen.reasons.includes('ambiguous_conditions'), atTen.reasons.join(', '));

  const clean = useValue('c172n.vfe', { flapsDeg: 0 });
  assert.equal(clean.value, null);
  assert.ok(clean.reasons.includes('missing_conditions'));

  assert.equal(useValue('c172n.va', {}).value, null);
  assert.equal(useValue('c172n.va', { weightLb: 2300 }).value, 97);
  assert.equal(useValue('c172n.va', { weightLb: 2000 }).value, null);
});

test('acceptance 6: a complete record passes and returns its citation', () => {
  const vne = useValue('c172n.vne');
  assert.equal(vne.value, 160);
  assert.match(vne.citation, /Pilot's Operating Handbook/);
  assert.match(vne.citation, /1 July 1978/);
  assert.match(vne.citation, /p\.2-4 Fig 2-1/);

  assert.equal(POH.vne, 160);
  assert.equal(POH.vno, 128);
  assert.equal(POH.vfe, 85);
  assert.equal(POH.va2300, 97);
  assert.deepEqual(POH.staticRpm, [2280, 2400]);
  assert.deepEqual(POH.asiGreen, [47, 128]);

  assert.equal(TABLES.GLIDE.kias, 65);
  assert.deepEqual(TABLES.GLIDE.conditions, ['flaps up', 'propeller windmilling']);

  for (const r of EVIDENCE) {
    if (r.status !== 'verified') continue;
    const g = checkEvidence(r);
    assert.ok(g.ok, `${r.id}: ${g.reasons.join(', ')}`);
  }
});
