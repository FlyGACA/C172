// Who may open the twin. No dependency and no Node API: Web Crypto only, so the same code runs
// in the Cloudflare Worker and in the tests.
//
// The FlightBag shop (FlyGACA/FlightBag, lib/twin.js) takes the payment and signs a five-minute
// pass with a secret the two share (TWIN_ACCESS_SECRET):
//     v1.<pass expiry>.<access expiry>.<subject>.<hex HMAC-SHA256 of "c172-twin-pass:" + the rest>
// Times are seconds since the epoch; the subject is a hash, not an email. This Worker turns a
// valid pass into its own session cookie, which lasts until the access ends or for 30 days,
// whichever comes first. Keep the pass format in step with the shop's.

export const COOKIE = 'c172_s';
export const SESSION_DAYS = 30;
const MIN_SECRET = 32;
const enc = new TextEncoder();

export const secretIsUsable = (secret) => typeof secret === 'string' && secret.length >= MIN_SECRET;

async function hmacHex(secret, text) {
  const k = await crypto.subtle.importKey('raw', enc.encode(secret), { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']);
  const sig = new Uint8Array(await crypto.subtle.sign('HMAC', k, enc.encode(text)));
  return [...sig].map((b) => b.toString(16).padStart(2, '0')).join('');
}

/** Compare two strings in time that depends on their length only. */
function sameText(a, b) {
  if (typeof a !== 'string' || typeof b !== 'string' || a.length !== b.length) return false;
  let diff = 0;
  for (let i = 0; i < a.length; i++) diff |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return diff === 0;
}

const INT = /^[1-9]\d{9,10}$/;
const SUBJECT = /^[0-9a-f]{16}$/;
const SIG = /^[0-9a-f]{64}$/;

/** `{ subject, accessEnds }` (seconds) for a pass that is genuine and still valid, else null. */
export async function readPass(pass, secret, nowMs = Date.now()) {
  if (!secretIsUsable(secret) || typeof pass !== 'string' || pass.length > 200) return null;
  const parts = pass.split('.');
  if (parts.length !== 5) return null;
  const [version, passExp, accessExp, subject, sig] = parts;
  if (version !== 'v1' || !INT.test(passExp) || !INT.test(accessExp) || !SUBJECT.test(subject) || !SIG.test(sig)) return null;
  if (!sameText(await hmacHex(secret, `c172-twin-pass:${version}.${passExp}.${accessExp}.${subject}`), sig)) return null;
  const now = Math.floor(nowMs / 1000);
  if (Number(passExp) < now || Number(accessExp) <= now) return null;
  return { subject, accessEnds: Number(accessExp) };
}

/** The Set-Cookie value for a session that ends with the access, or after SESSION_DAYS. */
export async function sessionCookie(subject, accessEnds, secret, nowMs = Date.now()) {
  const now = Math.floor(nowMs / 1000);
  const exp = Math.min(accessEnds, now + SESSION_DAYS * 86400);
  const body = `v1.${exp}.${subject}`;
  const value = `${body}.${await hmacHex(secret, `c172-twin-session:${body}`)}`;
  return `${COOKIE}=${value}; Path=/; Max-Age=${Math.max(0, exp - now)}; HttpOnly; Secure; SameSite=Lax`;
}

export const clearCookie = () => `${COOKIE}=; Path=/; Max-Age=0; HttpOnly; Secure; SameSite=Lax`;

/** `{ subject, exp }` from a Cookie header when the session is genuine and not over, else null. */
export async function readSession(cookieHeader, secret, nowMs = Date.now()) {
  if (!secretIsUsable(secret) || typeof cookieHeader !== 'string') return null;
  const raw = cookieHeader.split(';').map((c) => c.trim()).find((c) => c.startsWith(`${COOKIE}=`));
  if (!raw) return null;
  const parts = raw.slice(COOKIE.length + 1).split('.');
  if (parts.length !== 4) return null;
  const [version, exp, subject, sig] = parts;
  if (version !== 'v1' || !INT.test(exp) || !SUBJECT.test(subject) || !SIG.test(sig)) return null;
  if (!sameText(await hmacHex(secret, `c172-twin-session:${version}.${exp}.${subject}`), sig)) return null;
  if (Number(exp) <= Math.floor(nowMs / 1000)) return null;
  return { subject, exp: Number(exp) };
}

/** What anyone may open: the home page and the few files it and the locked page need. */
export function isPublicPath(pathname) {
  let p;
  try { p = decodeURIComponent(pathname); } catch { return false; }
  if (p.includes('..') || p.includes('\\') || p.includes('//')) return false;
  return p === '/' || p === '/index.html' || p === '/robots.txt' || p.startsWith('/site/');
}
