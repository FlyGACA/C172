// The gate in front of the twin when it is rented out (worker/). The pass below was made by the
// shop's own code (FlyGACA/FlightBag lib/twin.js) with the same secret and clock; the same
// string is pinned in that repository's tests, so the two cannot drift apart unnoticed.
import test from 'node:test';
import assert from 'node:assert/strict';
import { existsSync, readFileSync } from 'node:fs';
import { COOKIE, isPublicPath, readPass, readSession, sessionCookie } from '../worker/access.js';
import worker from '../worker/index.js';

const SECRET = 't'.repeat(40);
const NOW = Date.UTC(2026, 10, 24, 12, 0, 0);
const PASS = 'v1.1795521900.1798113600.ae3872e434470f2b.d2567d4384c642b1c206803379be236a7602f2b9997ea0c5ca4737157dff2a21';
const ACCESS_ENDS = 1798113600;

test('the shop\'s pass is accepted while it is fresh, and only with the shared secret', async () => {
  assert.deepEqual(await readPass(PASS, SECRET, NOW), { subject: 'ae3872e434470f2b', accessEnds: ACCESS_ENDS });
  assert.equal(await readPass(PASS, 'x'.repeat(40), NOW), null, 'another secret');
  assert.equal(await readPass(PASS, SECRET, NOW + 6 * 60 * 1000), null, 'a pass lives five minutes');
  assert.equal(await readPass(PASS, 'short', NOW), null, 'a weak secret opens nothing');
  assert.equal(await readPass(PASS, undefined, NOW), null, 'no secret opens nothing');
});

test('a changed pass is refused', async () => {
  const later = PASS.replace('1798113600', '1898113600'); // someone giving themselves more time
  assert.equal(await readPass(later, SECRET, NOW), null);
  for (const bad of [null, '', 'v1', PASS + '0', PASS.replace('v1', 'v2'), PASS.slice(0, -1) + 'g', 'a.b.c.d.e', 'x'.repeat(500)]) {
    assert.equal(await readPass(bad, SECRET, NOW), null, String(bad).slice(0, 20));
  }
});

test('a session ends with the access or after 30 days, whichever is first, and cannot be forged', async () => {
  const cookie = await sessionCookie('ae3872e434470f2b', ACCESS_ENDS, SECRET, NOW);
  assert.match(cookie, /; HttpOnly; Secure; SameSite=Lax$/);
  const value = cookie.split(';')[0];
  const session = await readSession(`other=1; ${value}`, SECRET, NOW);
  assert.equal(session.exp, ACCESS_ENDS, '30 days of access: the session ends with it');
  assert.equal(await readSession(value, SECRET, ACCESS_ENDS * 1000 + 1000), null, 'over when the access is over');
  const long = await sessionCookie('ae3872e434470f2b', ACCESS_ENDS + 400 * 86400, SECRET, NOW);
  assert.equal((await readSession(long.split(';')[0], SECRET, NOW)).exp, Math.floor(NOW / 1000) + 30 * 86400, 'a year of access: the session is 30 days');
  assert.equal(await readSession(value.replace(String(ACCESS_ENDS), String(ACCESS_ENDS + 86400)), SECRET, NOW), null, 'a stretched session');
  assert.equal(await readSession(value, 'x'.repeat(40), NOW), null);
  assert.equal(await readSession(`${COOKIE}=`, SECRET, NOW), null);
  assert.equal(await readSession(undefined, SECRET, NOW), null);
});

test('only the home page and /site/ are open to all', () => {
  for (const p of ['/', '/index.html', '/site/site.css', '/site/ufuq/ufuq.css', '/site/locked.html', '/site/hero.webp']) assert.equal(isPublicPath(p), true, p);
  for (const p of ['/08_realistic_digital_twin/index.html', '/08_realistic_digital_twin/models/C172N_realistic_high.glb', '/11_training_handbook/out/flygaca-c172n-training-handbook-en.pdf',
    '/shared/js/sim.js', '/site/../08_realistic_digital_twin/index.html', '/site/%2e%2e/LICENSE', '/site//x', '/README.md', '/%zz']) assert.equal(isPublicPath(p), false, p);
});

function env(secret = SECRET) { // pass null for a Worker with no secret set
  const served = [];
  return { served, TWIN_ACCESS_SECRET: secret, ASSETS: { fetch: async (req) => { served.push(new URL(req.url).pathname); return new Response(`file ${new URL(req.url).pathname}`, { headers: { 'Content-Type': 'text/html' } }); } } };
}
const get = (path, headers = {}) => new Request(`https://twin.example${path}`, { headers });
const MODEL = '/08_realistic_digital_twin/models/C172N_realistic_high.glb';

test('signed out: the home page answers, a page gets the locked page, a file gets nothing', async () => {
  const e = env();
  assert.equal((await worker.fetch(get('/'), e)).status, 200);
  const page = await worker.fetch(get('/08_realistic_digital_twin/index.html', { accept: 'text/html,*/*' }), e);
  assert.equal(page.status, 402);
  assert.equal(await page.text(), 'file /site/locked.html');
  assert.match(page.headers.get('cache-control'), /no-store/);
  const file = await worker.fetch(get(MODEL), e);
  assert.equal(file.status, 401);
  assert.ok(!e.served.includes(MODEL), 'the model was never read');
  assert.equal((await worker.fetch(new Request('https://twin.example' + MODEL, { method: 'POST' }), e)).status, 405);
});

test('a pass becomes a session that opens the files, and signing out ends it', async (t) => {
  t.mock.timers.enable({ apis: ['Date'], now: NOW });
  const e = env();
  const signin = await worker.fetch(get(`/api/session?p=${PASS}&lang=en`), e);
  assert.equal(signin.status, 302);
  assert.equal(signin.headers.get('location'), '/');
  const cookie = signin.headers.get('set-cookie').split(';')[0];
  const file = await worker.fetch(get(MODEL, { cookie }), e);
  assert.equal(file.status, 200);
  assert.equal(file.headers.get('cache-control'), 'private, max-age=3600');
  assert.deepEqual(await (await worker.fetch(get('/api/me', { cookie }), e)).json(), { signedIn: true, until: new Date(ACCESS_ENDS * 1000).toISOString() });
  assert.match((await worker.fetch(get('/api/signout', { cookie }), e)).headers.get('set-cookie'), /Max-Age=0/);
});

test('a bad pass goes back to the shop\'s sign-in page, and no secret means nobody gets in', async (t) => {
  t.mock.timers.enable({ apis: ['Date'], now: NOW });
  const bad = await worker.fetch(get('/api/session?p=nonsense&lang=en'), env());
  assert.equal(bad.headers.get('location'), 'https://flightbag.flygaca.com/twin-signin?status=expired&lang=en');
  assert.equal(bad.headers.get('set-cookie'), null);
  const open = env(null);
  assert.equal((await worker.fetch(get(`/api/session?p=${PASS}`), open)).headers.get('set-cookie'), null);
  const cookie = (await sessionCookie('ae3872e434470f2b', ACCESS_ENDS, SECRET, NOW)).split(';')[0];
  assert.equal((await worker.fetch(get(MODEL, { cookie }), open)).status, 401, 'a session signed with a secret the Worker does not hold');
  assert.equal((await worker.fetch(get('/'), open)).status, 200, 'the home page still answers');
});

test('the locked page exists, is in both languages, and loads only what is open to all', () => {
  const html = readFileSync(new URL('../site/locked.html', import.meta.url), 'utf8');
  assert.match(html, /for renters/);
  assert.match(html, /للمستأجرين/);
  assert.match(html, /not a Pilot's Operating Handbook/);
  assert.match(html, /Not affiliated with GACA/);
  assert.match(html, /غير تابعة لـ GACA/);
  for (const [, ref] of html.matchAll(/(?:href|src)="(\/[^"#?]*)"/g)) {
    if (ref === '/' || ref.startsWith('/08_') || ref.startsWith('/11_')) continue; // links into the twin itself
    assert.ok(isPublicPath(ref), `${ref} is not open to all`);
    assert.ok(existsSync(new URL('..' + ref, import.meta.url)), `${ref} does not exist`);
  }
  assert.doesNotMatch(html, /\d+\s*(SAR|ريال)/, 'no price on the page');
});

test('the deploy config is parked outside the root and sends every request through the Worker', () => {
  assert.equal(existsSync(new URL('../wrangler.jsonc', import.meta.url)) || existsSync(new URL('../wrangler.toml', import.meta.url)), false, 'nothing at the root for a deploy to pick up');
  const cfg = readFileSync(new URL('../deploy/twin/wrangler.jsonc', import.meta.url), 'utf8');
  assert.match(cfg, /"run_worker_first": true/);
  assert.doesNotMatch(cfg, /SECRET"\s*:/, 'no secret in the config');
});
