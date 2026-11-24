// The Cloudflare Worker in front of the twin, for when it is rented out. Every file passes
// through here: the home page and /site/ are open to all, everything else needs a session.
// It fails closed: with no usable TWIN_ACCESS_SECRET nobody has a session, so only the home
// page answers. See docs/RENTAL.md; nothing here is live until the owner deploys it.
import { clearCookie, isPublicPath, readPass, readSession, sessionCookie } from './access.js';

const DEFAULT_SHOP = 'https://flightbag.flygaca.com';
const PRIVATE = { 'Cache-Control': 'private, no-store', 'Referrer-Policy': 'no-referrer' };

function shopOrigin(env) {
  try {
    const u = new URL(env.SHOP_ORIGIN ?? DEFAULT_SHOP);
    return u.protocol === 'https:' ? u.origin : DEFAULT_SHOP;
  } catch { return DEFAULT_SHOP; }
}

const redirect = (location, extra = {}) => new Response(null, { status: 302, headers: { Location: location, ...PRIVATE, ...extra } });
const lang = (url) => (url.searchParams.get('lang') === 'en' ? 'en' : 'ar');

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const secret = env.TWIN_ACCESS_SECRET;

    if (url.pathname === '/api/session') {
      const pass = await readPass(url.searchParams.get('p'), secret);
      if (!pass) return redirect(`${shopOrigin(env)}/twin-signin?status=expired&lang=${lang(url)}`);
      return redirect('/', { 'Set-Cookie': await sessionCookie(pass.subject, pass.accessEnds, secret) });
    }
    if (url.pathname === '/api/signout') return redirect('/', { 'Set-Cookie': clearCookie() });
    if (url.pathname === '/api/me') {
      const session = await readSession(request.headers.get('cookie'), secret);
      return new Response(JSON.stringify({ signedIn: Boolean(session), until: session ? new Date(session.exp * 1000).toISOString() : null }), {
        headers: { 'Content-Type': 'application/json; charset=utf-8', ...PRIVATE },
      });
    }
    if (url.pathname.startsWith('/api/')) return new Response('Not found', { status: 404, headers: PRIVATE });

    if (request.method !== 'GET' && request.method !== 'HEAD') return new Response('Method not allowed', { status: 405, headers: { Allow: 'GET, HEAD' } });
    if (isPublicPath(url.pathname)) return env.ASSETS.fetch(request);

    const session = await readSession(request.headers.get('cookie'), secret);
    if (session) {
      const res = await env.ASSETS.fetch(request);
      const out = new Response(res.body, res);
      out.headers.set('Cache-Control', 'private, max-age=3600'); // never in a shared cache
      out.headers.set('Vary', 'Cookie');
      return out;
    }
    // Signed out. A page gets the locked page at its own address; any other file gets a bare 401,
    // so a model or a PDF never answers to someone who only knows its address.
    const wantsPage = (request.headers.get('accept') ?? '').includes('text/html');
    if (!wantsPage) return new Response('Sign in to open the twin.', { status: 401, headers: PRIVATE });
    const locked = await env.ASSETS.fetch(new Request(new URL('/site/locked.html', url), { headers: { accept: 'text/html' } }));
    return new Response(locked.body, { status: 402, headers: { 'Content-Type': 'text/html; charset=utf-8', ...PRIVATE, 'X-Robots-Tag': 'noindex' } });
  },
};
