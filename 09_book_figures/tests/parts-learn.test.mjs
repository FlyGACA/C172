// The naming quiz and the control-effect trainer. The trainer's claims are worked out again here from the hinge axes and
// signs in the models, in the aircraft's frame (+X toward the left wing, +Y up, +Z forward), so that if a model's hinge
// is ever turned round the trainer fails instead of teaching the wrong thing. No browser needed: `npm test`.
import test from 'node:test';
import assert from 'node:assert/strict';
import { existsSync, readFileSync, readdirSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { CHALLENGES, EFFECTS, effectOf, judge, nextChallenge, seeded } from '../parts/trainer.js';
import { MODES, ROUND, makeRound, summarize } from '../parts/quiz.js';
import { CONTROLS, D2R, pose, rest } from '../parts/motions.js';
import { CACHE, packList } from '../parts/offline.js';

const path = (relative) => fileURLToPath(new URL(relative, import.meta.url));
const nodes = new Map();
for (const f of readdirSync(path('../parts/m')).filter((n) => n.endsWith('.glb'))) {
  const b = readFileSync(path(`../parts/m/${f}`)), json = JSON.parse(b.subarray(20, 20 + b.readUInt32LE(12)));
  for (const n of json.nodes) if (n.extras?.id) nodes.set(n.extras.id, n.extras);
}
const data = JSON.parse(readFileSync(path('../parts/parts.json'), 'utf8')).parts;

/** Where a point one metre aft of a hinge ends up after the control is set, in the aircraft's frame: [x, y, z]. */
function aft(id, control, value) {
  const x = nodes.get(id), deg = pose({ ...rest(), [control]: value }).hinge.get(id), t = deg * (x.hinge_sign || 1) * D2R, [px, py, pz] = [0, 0, -1];
  if (x.hinge_axis === 'x') return [px, py * Math.cos(t) - pz * Math.sin(t), py * Math.sin(t) + pz * Math.cos(t)];
  if (x.hinge_axis === 'y') return [px * Math.cos(t) + pz * Math.sin(t), py, -px * Math.sin(t) + pz * Math.cos(t)];
  throw new Error(`${id} hinges about ${x.hinge_axis}`);
}

test('the trainer’s effects are what the models do', () => {
  // elevator up (the trailing edge rises) for a positive setting: the tail is pushed down, the nose rises
  assert.ok(aft('EMPENNAGE.elevator', 'elevator', 1)[1] > 0 && aft('EMPENNAGE.elevator', 'elevator', -1)[1] < 0);
  // positive aileron: the left aileron's trailing edge up and the right one's down, which rolls the aircraft to the left
  assert.ok(aft('WING_L.aileron', 'aileron', 1)[1] > 0 && aft('WING_R.aileron', 'aileron', 1)[1] < 0, 'left up, right down');
  assert.ok(aft('WING_L.aileron', 'aileron', -1)[1] < 0 && aft('WING_R.aileron', 'aileron', -1)[1] > 0, 'right up, left down');
  // positive rudder: the trailing edge swings toward -X, the right wing: the rudder goes right
  assert.ok(aft('EMPENNAGE.rudder', 'rudder', 1)[0] < 0 && aft('EMPENNAGE.rudder', 'rudder', -1)[0] > 0);
  // flaps: both trailing edges go down
  assert.ok(aft('WING_L.flap', 'flaps', 30)[1] < 0 && aft('WING_R.flap', 'flaps', 30)[1] < 0);
});

test('every challenge has its answer on the side the effect text describes, and both languages', () => {
  assert.equal(new Set(CHALLENGES.map((c) => c.id)).size, CHALLENGES.length);
  const keys = new Set(CONTROLS.map((c) => c.key));
  for (const c of CHALLENGES) {
    assert.ok(keys.has(c.key) && c.en && c.ar, c.id);
    const control = CONTROLS.find((x) => x.key === c.key);
    const answers = [control.min, control.max, 0, (control.min + control.max) / 2].filter((v) => c.want(v));
    assert.ok(answers.length > 0 && !c.want(0), `${c.id}: the answer must be somewhere other than the resting setting`);
    const side = c.want(control.max) ? 'pos' : 'neg';
    assert.ok(EFFECTS[c.key][side].en && EFFECTS[c.key][side].ar, `${c.id} has no effect text`);
    const done = judge(c, c.want(control.max) ? control.max : control.min);
    assert.ok(done.ok && done.now, c.id);
    assert.ok(!judge(c, 0).ok && judge(c, 0).now === null, `${c.id}: centred does nothing`);
  }
  // the text matches the side: nose-up is the positive elevator, a roll to the left the positive aileron, a yaw to the right the positive rudder
  const by = (id) => CHALLENGES.find((c) => c.id === id);
  assert.ok(by('nose_up').want(1) && by('nose_down').want(-1) && by('roll_left').want(1) && by('roll_right').want(-1) && by('yaw_right').want(1) && by('yaw_left').want(-1));
  assert.match(effectOf('elevator', 1).en, /nose rises/); assert.match(effectOf('aileron', 1).en, /left/); assert.match(effectOf('rudder', 1).en, /right/);
  assert.equal(effectOf('flaps', 0), null);
});

test('the wrong way is told what it does', () => {
  const j = judge(CHALLENGES.find((c) => c.id === 'nose_up'), -0.8);
  assert.ok(!j.ok); assert.match(j.now.en, /nose drops/);
});

test('challenges come without repeating until all have been asked, and never the same twice running', () => {
  const rng = seeded(7), asked = [];
  for (let i = 0; i < CHALLENGES.length; i++) { const c = nextChallenge(asked, rng); assert.ok(!asked.includes(c.id), `${c.id} asked twice`); asked.push(c.id); }
  for (let i = 0; i < 50; i++) { const c = nextChallenge(asked, rng); assert.notEqual(c.id, asked.at(-1)); asked.push(c.id); }
});

test('a quiz round has four different answers each, one of them right, and the same seed gives the same round', () => {
  for (const mode of MODES) {
    const round = makeRound(data, { mode, rng: seeded(11) });
    assert.equal(round.length, ROUND, mode);
    for (const q of round) {
      assert.equal(q.options.length, 4); assert.equal(q.options[q.correct], q.answer);
      assert.equal(new Set(q.options.map((p) => p.en.trim().toLowerCase())).size, 4, `${q.answer.id}: two options share an English name`);
      assert.equal(new Set(q.options.map((p) => p.ar.trim())).size, 4, `${q.answer.id}: two options share an Arabic name`);
      assert.ok(q.mode === 'name' || q.mode === 'picture');
    }
    assert.equal(new Set(round.map((q) => q.answer.id)).size, round.length, 'a part asked twice');
    assert.deepEqual(round.map((q) => q.answer.id), makeRound(data, { mode, rng: seeded(11) }).map((q) => q.answer.id));
  }
  assert.ok(makeRound(data, { mode: 'mixed', rng: seeded(3), n: 40 }).some((q) => q.mode === 'name') && makeRound(data, { mode: 'mixed', rng: seeded(3), n: 40 }).some((q) => q.mode === 'picture'));
});

test('a quiz on one system asks about that system, and prefers look-alikes from it', () => {
  const round = makeRound(data, { system: 'ENGINE', rng: seeded(5), n: 8 });
  assert.ok(round.length > 0 && round.every((q) => q.answer.s === 'ENGINE'));
  const fromSame = round.flatMap((q) => q.options.filter((o) => o !== q.answer)).filter((o) => o.s === 'ENGINE').length;
  assert.ok(fromSame >= round.length * 2, 'most distractors in an engine quiz should be engine parts');
});

test('the summary counts the right answers and lists what to look at again', () => {
  const s = summarize([{ ok: true, part: 'a' }, { ok: false, part: 'b' }, { ok: false, part: 'c' }]);
  assert.deepEqual(s, { right: 1, total: 3, again: ['b', 'c'] });
});

test('the offline copy lists every model and picture sheet, each one on disk, and the worker and the page use the same cache', () => {
  const D = JSON.parse(readFileSync(path('../parts/parts.json'), 'utf8')), files = packList(D);
  const systems = new Set(D.parts.map((p) => p.s));
  assert.equal(files.filter((f) => f.startsWith('m/')).length, systems.size, 'a model for each system');
  assert.equal(files.length, systems.size + D.thumb.files.length + D.large.files.length + D.place.files.length + 1);
  for (const f of files) assert.ok(existsSync(path(`../parts/${f}`)), `${f} is listed but missing`);
  assert.equal(new Set(files).size, files.length, 'a file listed twice');
  assert.ok(!files.some((f) => f.startsWith('full/')), 'the full-size pictures are not part of the copy');
  const worker = readFileSync(path('../parts/sw.js'), 'utf8');
  assert.ok(worker.includes(`const CACHE = '${CACHE}';`), 'sw.js and offline.js name different caches');
  assert.ok(worker.includes('x-parts-refresh') && readFileSync(path('../parts/offline.js'), 'utf8').includes('x-parts-refresh'), 'an update must bypass the saved copy');
  assert.ok(/caches\.has\(CACHE\)/.test(worker), 'the worker must do nothing until a copy has been asked for');
});

test('the page has the quiz, the offline controls and the trainer, and every button is in both languages', () => {
  const page = readFileSync(path('../parts/index.html'), 'utf8');
  for (const id of ['bquiz', 'qdlg', 'q-mode', 'q-sys', 'q-start', 'q-play', 'q-pic', 'q-opts', 'q-fb', 'q-next', 'q-close', 'q-end', 'q-score', 'q-again', 'off', 'boff', 'boffx', 'off-msg']) assert.match(page, new RegExp(`id="${id}"`), `#${id} is missing`);
  for (const b of page.match(/<button[\s\S]*?<\/button>/g)) assert.ok(b.includes('ufuq-en') && b.includes('ufuq-ar'), `not bilingual: ${b.slice(0, 70)}`);
  assert.ok(readFileSync(path('../parts/parts.js'), 'utf8').includes("'trainer'"), 'the trainer tab is missing');
});
