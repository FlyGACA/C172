// "Save for offline use": the page asks for the models, the picture sheets and the code it has loaded to be kept, so that
// the catalogue opens without a connection. sw.js answers from the copy; this file makes it. Nothing is saved unless the
// reader asks, and the copy can be removed again. The picture of every part at full size (about 320 MB) is not included.
export const CACHE = 'c172-parts-v1';
const KEY = 'c172-parts-offline';

export const supported = () => typeof navigator !== 'undefined' && 'serviceWorker' in navigator && typeof caches !== 'undefined';

/** The files that make up an offline copy, apart from the code the page has loaded: each system's model and every picture sheet. */
export function packList(D) {
  const systems = [...new Set(D.parts.map((p) => p.s))].sort();
  return [...systems.map((s) => `m/${s}.glb`), ...D.thumb.files.map((f) => f.f), ...D.large.files.map((f) => f.f), ...D.place.files.map((f) => f.f), 'parts.json'];
}

const remembered = () => { try { return JSON.parse(localStorage.getItem(KEY)); } catch { return null; } };
const remember = (v) => { try { if (v) localStorage.setItem(KEY, JSON.stringify(v)); else localStorage.removeItem(KEY); } catch { /* storage may be blocked */ } };

/** Whether a copy has been saved, and how much of it. */
export async function status() {
  if (!supported() || !(await caches.has(CACHE))) return { saved: false };
  return { saved: true, ...remembered() };
}

/**
 * Saves the copy. `onProgress(done, total)` is called as files arrive; `signal` stops it. Returns what was saved, and the files that
 * could not be (the rest still work offline).
 */
export async function save(D, onProgress = () => {}, signal) {
  // The code the page loads when the 3D view opens is part of the copy, so open it once if it has not been.
  await Promise.all([import('three'), import('three/addons/loaders/GLTFLoader.js'), import('three/addons/controls/OrbitControls.js'), import('three/addons/environments/RoomEnvironment.js')]).catch(() => {});
  const here = location.href.split(/[?#]/)[0], base = new URL('.', location.href).href;
  const seen = performance.getEntriesByType('resource').map((e) => e.name).filter((u) => u.startsWith(location.origin) && !u.includes('/cdn-cgi/'));
  const urls = [...new Set([here, base, ...seen.map((u) => u.split('#')[0]), ...packList(D).map((f) => new URL(f, base).href)])];
  const cache = await caches.open(CACHE), failed = []; let done = 0, bytes = 0, next = 0;
  const worker = async () => {
    while (next < urls.length && !signal?.aborted) {
      const url = urls[next++];
      try { const response = await fetch(url, { headers: { 'x-parts-refresh': '1' } }); if (!response.ok) throw new Error(String(response.status)); bytes += Number(response.headers.get('content-length')) || 0; await cache.put(url, response); }
      catch { failed.push(url); }
      onProgress(++done, urls.length);
    }
  };
  await Promise.all([worker(), worker(), worker(), worker()]);
  if (signal?.aborted) { await caches.delete(CACHE); remember(null); return { saved: false, aborted: true, failed }; }
  remember({ at: Date.now(), files: urls.length - failed.length, bytes });
  return { saved: true, files: urls.length - failed.length, bytes, failed };
}

/** Removes the copy. */
export async function remove() { remember(null); return supported() ? caches.delete(CACHE) : false; }
