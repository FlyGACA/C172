// Figure host: loads one figure module and draws it into an SVG sized in millimetres.
// Query: ?fig=<id>&lang=en|ar  (&preview=1 adds the caption strip used on review sheets)

import { el, textFactory } from './svg.js';

const params = new URLSearchParams(location.search);
const lang = params.get('lang') === 'ar' ? 'ar' : 'en';
const dir = lang === 'ar' ? 'rtl' : 'ltr';
const preview = params.has('preview');
const sheet = document.getElementById('sheet');
const state = (window.__figure = { ready: false, error: null });

async function json(path) {
  const response = await fetch(path);
  if (!response.ok) throw new Error(`${path}: HTTP ${response.status}`);
  return response.json();
}

try {
  const manifest = await json('figures.json');
  const entry = manifest.figures.find((figure) => figure.id === params.get('fig')) || manifest.figures[0];
  document.documentElement.lang = lang;
  document.documentElement.dir = dir;
  document.title = `${entry.number} ${entry.title[lang]}`;

  // Type is measured during layout, so the fonts must be in before any figure code runs.
  await Promise.all(['400', '600'].map((weight) => document.fonts.load(`${weight} 30px "IBM Plex Sans Arabic"`, 'Aa0 ءي')));

  const module = await import(`./figures/${entry.module}`);
  const data = entry.data ? await json(entry.data) : {};
  const strings = data.strings?.[lang] || {};
  const t = (key) => {
    if (!(key in strings)) throw new Error(`${entry.id}: missing ${lang} string "${key}"`);
    return strings[key];
  };

  const [width, height] = module.size;
  sheet.style.width = `${entry.width_mm}mm`;
  const svg = el('svg', { id: 'art', viewBox: `0 0 ${width} ${height}`, role: 'img', 'aria-label': entry.title[lang] }, sheet);
  el('title', {}, svg).textContent = entry.title[lang];
  await module.draw({ svg, lang, dir, t, data, entry, json, text: textFactory(dir), width, height });

  if (preview) {
    const caption = document.createElement('div');
    caption.id = 'caption';
    const label = document.createElement('span');
    const number = document.createElement('b');
    number.textContent = lang === 'ar' ? `الشكل ${entry.number}` : `Figure ${entry.number}`;
    label.append(number, ` — ${entry.title[lang]}`);
    const status = document.createElement('span');
    status.className = `status ${entry.status}`;
    status.textContent = manifest.status_labels[entry.status][lang];
    caption.append(label, status);
    sheet.append(caption);
  }

  await document.fonts.ready;
  const box = sheet.getBoundingClientRect();
  Object.assign(state, {
    ready: true, id: entry.id, lang, vector: entry.method !== 'render-3d',
    width_mm: entry.width_mm, height_mm: (entry.width_mm * box.height) / box.width,
  });
} catch (error) {
  state.error = error.stack || String(error);
  sheet.textContent = state.error;
  console.error(error);
}
