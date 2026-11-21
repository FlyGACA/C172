// FlyGACA C172N training handbook: builds 11_training_handbook/index.html, one page in Arabic and English, from
// content.mjs and the twin's records of the Pilot's Operating Handbook.
//
//   node 11_training_handbook/build.mjs           write index.html
//   node 11_training_handbook/build.mjs --check   fail when index.html is stale
//   node 11_training_handbook/build.mjs --pdf     also print out/flygaca-c172n-training-handbook-{en,ar}.pdf (Playwright)
import { readFileSync, writeFileSync, mkdirSync, mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { spawnSync } from 'node:child_process';
import * as C from './content.mjs';

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = join(HERE, '..');
const OUT_HTML = join(HERE, 'index.html');
const read = (rel) => readFileSync(join(ROOT, rel), 'utf8');

// ------------------------------------------------------------------ the records

export async function loadData() {
  const poh = JSON.parse(read('08_realistic_digital_twin/data/poh_references.json'));
  const y79 = JSON.parse(read('04b_poh_reference/poh_1979_reference_data.json'));
  const inst = JSON.parse(read('08_realistic_digital_twin/data/instruments.json'));
  const tablesText = read('shared/js/poh_tables.js');
  const tables = await import(pathToFileURL(join(ROOT, 'shared/js/poh_tables.js')).href);
  return {
    poh, y79, inst, tables, tablesText,
    pohByKey: Object.fromEntries(poh.values.map((v) => [v.key, v])),
    y79ByKey: Object.fromEntries(y79.values.map((v) => [v.key, v])),
  };
}

/** The JSDoc comment written above an export in poh_tables.js: it states the table's conditions. */
function tableComment(data, name) {
  const at = data.tablesText.indexOf(`export const ${name} `);
  if (at < 0) return '';
  const before = data.tablesText.slice(0, at);
  const start = before.lastIndexOf('/**');
  return start >= 0 && !before.slice(start).includes('export ') ? before.slice(start) : '';
}

function resolve(data, ref) {
  const [kind, key] = ref.split(':');
  if (ref === 'src') {
    const s = data.poh.source;
    return { raw: `${s.title} ${s.edition}`, pages: [] };
  }
  if (kind === 'poh') {
    const v = data.pohByKey[key];
    if (!v) throw new Error(`unknown record ${ref}`);
    return { raw: String(v.value), pages: [v.page] };
  }
  if (kind === 'y79') {
    const v = data.y79ByKey[key];
    if (!v) throw new Error(`unknown record ${ref}`);
    const page = (v.source_page.match(/(?:p\.|Figure [\d-]+, p\.)\s*([\d-]+)/) || [])[1] || v.source_page;
    return { raw: `${v.value} ${v.source_page}`, pages: [page] };
  }
  if (kind === 'tab') {
    const t = data.tables[key];
    if (!t) throw new Error(`unknown table ${ref}`);
    return { raw: `${JSON.stringify(t)} ${tableComment(data, key)}`, pages: [t.ref.replace(/^p\./, '')] };
  }
  if (kind === 'inst') {
    const i = data.inst.instruments[key];
    if (!i) throw new Error(`unknown instrument ${ref}`);
    const marks = [...(i.arcs || []), ...(i.redlines || [])];
    const pages = [...new Set(marks.flatMap((m) => [...(m.ref || '').matchAll(/p\.(\d+-\d+(?: Fig \d+-\d+)?)/g)].map((x) => x[1])))];
    return { raw: JSON.stringify(i), pages };
  }
  throw new Error(`unknown reference ${ref}`);
}

/** The text a block's numbers must be found in: every record it names. */
export function sourceText(data, refs) {
  return refs.map((r) => resolve(data, r).raw).join(' ');
}

function pagesOf(data, refs) {
  return [...new Set(refs.flatMap((r) => resolve(data, r).pages))];
}

// ------------------------------------------------------------------ HTML helpers

const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

// Latin words, codes and numbers inside Arabic sit in a left-to-right isolate. The spaces and sentence punctuation at
// the run's edges stay outside it, so they print on the right side of the run.
const EDGES = /^([\s.,;:!?،؛]*)(.*?)([\s.,;:!?،؛]*)$/s;
function arabic(text) {
  return String(text).split(/([؀-ۿ،؛]+)/).map((part) => {
    if (!/[A-Za-z0-9]/.test(part)) return esc(part);
    let [, lead, core, trail] = part.match(EDGES);
    while (core) {
      if (core[0] === ')' || (core[0] === '(' && (core.match(/\(/g) || []).length > (core.match(/\)/g) || []).length)) { lead += core[0]; core = core.slice(1); }
      else if (core.endsWith('(') || (core.endsWith(')') && (core.match(/\)/g) || []).length > (core.match(/\(/g) || []).length)) { trail = core.slice(-1) + trail; core = core.slice(0, -1); }
      else break;
      const [, l2, c2, t2] = core.match(EDGES);
      lead += l2; core = c2; trail = t2 + trail;
    }
    return core ? `${esc(lead)}<bdi dir="ltr">${esc(core)}</bdi>${esc(trail)}` : esc(part);
  }).join('');
}

const both = (l) => `<span class="ufuq-en">${esc(l.en)}</span><span class="ufuq-ar" lang="ar">${arabic(l.ar)}</span>`;
const cites = (data, refs) => pagesOf(data, refs).map((p) => ` <span class="ufuq-cite hb-page" dir="ltr" title="Pilot's Operating Handbook page">POH ${esc(p)}</span>`).join('');
// Numbers, ranges and units in tables are left-to-right isolates, so an Arabic row reads 41–85 and −20 °C, not 85–41.
const ltr = (v) => (String(v).trim() ? `<bdi dir="ltr">${esc(String(v).trim())}</bdi>` : '');
const cell = (v) => (v === null || v === undefined ? '—' : ltr(v));

function headRow(cols) {
  return `<thead><tr>${cols.map((c) => `<th scope="col">${typeof c === 'string' ? ltr(c) : both(c)}</th>`).join('')}</tr></thead>`;
}

// ------------------------------------------------------------------ tables drawn from the records

function tableHtml(data, name, caption) {
  const T = C.TABLE_TEXT;
  const tab = data.tables;
  let head, rows, refs;
  if (name === 'asi') {
    const i = data.inst.instruments.ASI;
    refs = ['inst:ASI'];
    head = [T.colour, T.range, T.meaning];
    rows = i.arcs.map((a) => [T[a.color], `${a.from}–${a.to} KIAS`, T[`${a.color}Meaning`]])
      .concat(i.redlines.map((r) => [T.red, `${r.value} KIAS`, T.redMeaning]));
  } else if (name === 'engine') {
    const I = data.inst.instruments;
    refs = ['inst:TACH', 'inst:OIL_P', 'inst:OIL_T', 'inst:SUCTION', 'poh:tach.green'];
    head = [T.instrument, T.green, T.red];
    const tachGreen = I.TACH.arcs[0];
    rows = [
      [T.tach, { en: `${tachGreen.from}–${tachGreen.to} RPM ${T.tachAlt.en}`, ar: `${tachGreen.from}–${tachGreen.to} RPM ${T.tachAlt.ar}` }, `${I.TACH.redlines[0].value} RPM`],
      [T.oilP, `${I.OIL_P.arcs[0].from}–${I.OIL_P.arcs[0].to} psi`, { en: I.OIL_P.redlines.map((r, k) => `${k ? T.max.en : T.min.en} ${r.value} psi`).join('; '), ar: I.OIL_P.redlines.map((r, k) => `${k ? T.max.ar : T.min.ar} ${r.value} psi`).join('؛ ') }],
      [T.oilT, `${I.OIL_T.arcs[0].from}–${I.OIL_T.arcs[0].to} °F`, `${I.OIL_T.redlines[0].value} °F`],
      [T.suction, `${I.SUCTION.arcs[0].from}–${I.SUCTION.arcs[0].to} inHg`, null],
    ];
  } else if (name === 'speeds') {
    const s = tab.SPEEDS;
    refs = ['tab:SPEEDS'];
    head = [T.speed, T.kias];
    const at = (l, extra) => ({ en: `${l.en}, ${extra.en}`, ar: `${l.ar}، ${extra.ar}` });
    rows = [
      [T.normalClimbOut, `${s.normalClimbOut[0]}–${s.normalClimbOut[1]}`],
      [at(T.bestRate, T.atSea), s.bestRate[0]], [at(T.bestRate, T.at10k), s.bestRate[10000]],
      [at(T.bestAngle, T.atSea), s.bestAngle[0]], [at(T.bestAngle, T.at10k), s.bestAngle[10000]],
      [T.shortField50, s.shortFieldAt50Ft],
      [T.approachUp, `${s.approachFlapsUp[0]}–${s.approachFlapsUp[1]}`], [T.approach40, `${s.approachFlaps40[0]}–${s.approachFlaps40[1]}`],
      [T.shortFieldApproach, s.shortFieldApproach],
      [T.balked, s.balkedLanding.kias],
      [T.crosswind, `${s.maxDemonstratedCrosswindKt} kt`],
    ];
  } else if (name === 'stall') {
    const s = tab.STALL_KCAS;
    refs = ['tab:STALL_KCAS'];
    head = [T.cg, T.flaps, ...s.bankDeg.map((b) => ({ en: `${T.bank.en} ${b}°`, ar: `${T.bank.ar} ${b}°` }))];
    rows = [];
    for (const side of ['aft', 'fwd']) {
      for (const [flap, speeds] of Object.entries(s[side])) rows.push([T[side], `${flap}°`, ...speeds]);
    }
  } else if (name === 'takeoff') {
    refs = ['tab:TAKEOFF'];
    head = [T.elevation, T.temp, T.weight, T.roll, T.over50, T.liftOff, T.at50];
    rows = tab.TAKEOFF.rows;
  } else if (name === 'climb') {
    refs = ['tab:CLIMB_STANDARD'];
    head = [T.altitude, T.climbKias, T.fpm];
    rows = tab.CLIMB_STANDARD.rows;
  } else if (name === 'climbTemp') {
    const c = tab.CLIMB_TEMPERATURE;
    refs = ['tab:CLIMB_TEMPERATURE'];
    head = [T.altitude, T.climbKias, ...c.tempC.map((t) => `${t} °C`)];
    rows = Object.entries(c.rows).map(([alt, r]) => [alt, ...r]);
  } else if (name === 'cruise') {
    refs = ['tab:CRUISE'];
    head = [T.altitude, T.rpm, T.bhp, T.ktas];
    rows = Object.entries(tab.CRUISE.rows).flatMap(([alt, rs]) => rs.map((r, k) => [k ? '' : alt, ...r]));
  } else if (name === 'landing') {
    refs = ['tab:LANDING'];
    head = [T.elevation, T.temp, T.landRoll, T.landOver50];
    rows = tab.LANDING.rows;
  } else {
    throw new Error(`unknown table ${name}`);
  }
  const body = rows.map((r) => `<tr>${r.map((c) => `<td>${c && typeof c === 'object' ? both(c) : cell(c)}</td>`).join('')}</tr>`).join('');
  return `<figure class="hb-table"><figcaption>${both(caption)}${cites(data, refs)}</figcaption>`
    + `<div class="hb-scroll"><table class="ufuq-table">${headRow(head)}<tbody>${body}</tbody></table></div></figure>`;
}

// ------------------------------------------------------------------ figures from Phase 9

const FIGURES = {
  'aircraft-exterior': { en: '../09_book_figures/renders/aircraft-exterior.png', ar: '../09_book_figures/renders/aircraft-exterior.png', w: 2400, h: 1080 },
  'flight-controls': { en: '../09_book_figures/renders/flight-controls.png', ar: '../09_book_figures/renders/flight-controls.png', w: 1800, h: 1395 },
  'asi-markings': { en: '../09_book_figures/out/en/asi-markings.svg', ar: '../09_book_figures/out/ar/asi-markings.svg', w: 1600, h: 930 },
  'fuel-system': { en: '../09_book_figures/out/en/fuel-system.svg', ar: '../09_book_figures/out/ar/fuel-system.svg', w: 1600, h: 930 },
};

function figureHtml(id, caption) {
  const f = FIGURES[id];
  if (!f) throw new Error(`unknown figure ${id}`);
  const img = (lang) => `<img class="ufuq-${lang}"${lang === 'ar' ? ' lang="ar"' : ''} src="${f[lang]}" alt="" width="${f.w}" height="${f.h}" loading="lazy">`;
  const imgs = f.en === f.ar ? `<img src="${f.en}" alt="" width="${f.w}" height="${f.h}" loading="lazy">` : img('en') + img('ar');
  return `<figure class="hb-figure"><div class="hb-figure__art">${imgs}</div><figcaption>${both(caption)}</figcaption></figure>`;
}

// ------------------------------------------------------------------ blocks and page

function blockHtml(data, b) {
  if (b.type === 'p') return `<p>${both(b)}${cites(data, b.refs)}</p>`;
  if (b.type === 'note') {
    return `<div class="ufuq-callout ufuq-callout--${b.kind === 'warning' ? 'warning' : 'tip'}"><p>${both(b)}${cites(data, b.refs)}</p></div>`;
  }
  if (b.type === 'facts') {
    const rows = b.rows.map((r) => `<tr><th scope="row">${both(r.label)}</th><td>${both(r)}${cites(data, r.refs)}</td></tr>`).join('');
    return `<div class="hb-scroll"><table class="ufuq-table hb-facts"><tbody>${rows}</tbody></table></div>`;
  }
  if (b.type === 'steps') {
    const items = b.items.map((i) => `<li>${both(i)}</li>`).join('');
    const after = b.after ? `<p class="hb-after">${both(b.after)}</p>` : '';
    return `<section class="hb-steps"><h3>${both(b.title)}${cites(data, b.refs)}</h3><ol>${items}</ol>${after}</section>`;
  }
  if (b.type === 'list') {
    return `<ul class="hb-list">${b.items.map((i) => `<li>${both(i)}</li>`).join('')}</ul><p class="hb-list-cite">${cites(data, b.refs).trim()}</p>`;
  }
  if (b.type === 'table') return tableHtml(data, b.name, b.caption);
  if (b.type === 'figure') return figureHtml(b.id, b.caption);
  throw new Error(`unknown block type ${b.type}`);
}

export async function render(data) {
  data = data || await loadData();
  const toc = C.SECTIONS.map((s, k) => `<li><a href="#${s.id}"><span class="hb-num">${k + 1}</span> ${both(s.title)}</a></li>`).join('');
  const sections = C.SECTIONS.map((s, k) => `<section class="hb-section" id="${s.id}" aria-labelledby="${s.id}-h">`
    + `<h2 id="${s.id}-h"><span class="hb-num">${k + 1}</span> ${both(s.title)}</h2>${s.blocks.map((b) => blockHtml(data, b)).join('\n')}</section>`).join('\n');
  const notice = `<div class="ufuq-callout ufuq-callout--warning hb-notice" role="note"><p class="hb-notice__title">${both(C.NOTICE.title)}</p>`
    + C.NOTICE.en.map((en, k) => `<p>${both({ en, ar: C.NOTICE.ar[k] })}</p>`).join('') + '</div>';
  const sources = `<section class="hb-section" id="sources" aria-labelledby="sources-h"><h2 id="sources-h">${both(C.SOURCES.title)}</h2><p>${both(C.SOURCES)}</p></section>`;
  return `<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${esc(C.TITLE.en)} · ${esc(C.TITLE.ar)} — Fly GACA</title>
<meta name="description" content="${esc(C.SUBTITLE.ar)}. ${esc(C.SUBTITLE.en)}.">
<meta name="generator" content="11_training_handbook/build.mjs; edit content.mjs or the records, not this page">
<link rel="icon" href="../site/ufuq/c172-mark.svg">
<link rel="stylesheet" href="../site/ufuq/ufuq.css">
<link rel="stylesheet" href="../site/ufuq/ufuq.components.css">
<link rel="stylesheet" href="handbook.css">
<script src="../site/ufuq/ufuq.shell.js"></script>
</head>
<body class="hb">
<header class="ufuq-shell">
  <a class="ufuq-shell__brand" href="../"><img class="on-night" src="../site/ufuq/c172-mark.svg" alt="" width="32" height="32"><img class="on-day" src="../site/ufuq/c172-mark-ink.svg" alt="" width="32" height="32"><span class="ufuq-en">C172 Twin</span><span class="ufuq-ar" lang="ar">توأم سيسنا 172</span></a>
  <nav class="ufuq-shell__nav" aria-label="الصفحات" data-label-en="Pages" data-label-ar="الصفحات">
    <a href="../"><span class="ufuq-en">Home</span><span class="ufuq-ar" lang="ar">الرئيسية</span></a>
    <a href="../08_realistic_digital_twin/index.html"><span class="ufuq-en">The aircraft</span><span class="ufuq-ar" lang="ar">الطائرة</span></a>
    <a href="../08_realistic_digital_twin/docs/gallery.html"><span class="ufuq-en">Gallery</span><span class="ufuq-ar" lang="ar">المعرض</span></a>
    <a href="./" aria-current="page"><span class="ufuq-en">Handbook</span><span class="ufuq-ar" lang="ar">الدليل</span></a>
  </nav>
  <div class="ufuq-shell__tools">
    <button type="button" class="ufuq-shell__tool" data-shell-theme><span class="ufuq-en">Day / Night</span><span class="ufuq-ar" lang="ar">نهاري / ليلي</span></button>
    <button type="button" class="ufuq-shell__tool" data-shell-lang><span class="ufuq-en" lang="ar">العربية</span><span class="ufuq-ar" lang="en">English</span></button>
  </div>
</header>
<main class="ufuq-container hb-main">
<header class="hb-head">
  <p class="ufuq-eyebrow"><span class="ufuq-en">Fly GACA · Cessna 172N, 1979</span><span class="ufuq-ar" lang="ar">فلاي قاكا · سيسنا 172N، موديل 1979</span></p>
  <h1>${both(C.TITLE)}</h1>
  <p class="hb-lead">${both(C.SUBTITLE)}</p>
</header>
${notice}
<nav class="hb-toc" aria-label="المحتويات" data-label-en="Contents" data-label-ar="المحتويات"><ol>${toc}<li><a href="#sources">${both(C.SOURCES.title)}</a></li></ol></nav>
${sections}
${sources}
</main>
<footer class="ufuq-shell-foot">
  <a class="ufuq-shell-foot__family" href="https://flygaca.com/"><img src="../site/ufuq/flygaca-mark.png" alt="" width="48" height="48"><span class="ufuq-en">Part of Fly GACA</span><span class="ufuq-ar" lang="ar">جزء من فلاي قاكا</span></a>
  <p>${both(C.MAKER_NOTICE)}</p>
  <p lang="en" dir="ltr">${esc(C.BRAND_NOTICE.en)}</p>
  <p lang="ar" dir="rtl">${esc(C.BRAND_NOTICE.ar)}</p>
</footer>
</body>
</html>
`;
}

async function printPdfs() {
  const mod = await import(process.env.PLAYWRIGHT_MODULE || 'playwright');
  const pw = mod.chromium ? mod : mod.default;  // a CommonJS path given in PLAYWRIGHT_MODULE arrives as `default`
  // The two SVG figures are <img>s: an image cannot load the page's @font-face, so its text uses whatever font the system
  // has under the name "IBM Plex Sans Arabic" and otherwise falls back to a system CFF font that Chromium embeds as Type 3.
  // Make the vendored files visible to fontconfig for this one browser (Linux; harmless elsewhere).
  const fontDir = join(ROOT, '09_book_figures', 'vendor', 'fonts');
  const conf = join(mkdtempSync(join(tmpdir(), 'c172-fonts-')), 'fonts.conf');
  writeFileSync(conf, `<?xml version="1.0"?><fontconfig><include ignore_missing="yes">/etc/fonts/fonts.conf</include><dir>${fontDir}</dir></fontconfig>`);
  const browser = await pw.chromium.launch({ env: { ...process.env, FONTCONFIG_FILE: conf } });
  mkdirSync(join(HERE, 'out'), { recursive: true });
  try {
    for (const lang of ['en', 'ar']) {
      const page = await browser.newPage();
      await page.goto(`${pathToFileURL(OUT_HTML).href}?lang=${lang}&theme=day`, { waitUntil: 'load' });
      // The figures load lazily on screen; for print every one must be loaded, the hidden language's included.
      // The print stylesheet names the vendored fonts; load them under print media, before the PDF is made.
      await page.emulateMedia({ media: 'print' });
      await page.evaluate(() => document.fonts.ready);
      await page.evaluate(() => Promise.all([...document.images].map((i) => { i.loading = 'eager'; return i.decode().catch(() => null); })));
      const label = lang === 'ar' ? 'مرجع دراسي، ليس دليل تشغيل الطيار · لا تطِر به' : 'Study reference, not a POH · never fly from it';
      await page.pdf({
        path: join(HERE, 'out', `flygaca-c172n-training-handbook-${lang}.pdf`), format: 'A4', printBackground: true,
        margin: { top: '16mm', bottom: '18mm', left: '15mm', right: '15mm' }, displayHeaderFooter: true, outline: true, tagged: true,
        headerTemplate: '<span></span>',
        footerTemplate: `<div style="font:8px \'IBM Plex Sans Arabic\',sans-serif;width:100%;padding:0 15mm;display:flex;justify-content:space-between;color:#555"><span>FlyGACA · ${label}</span><span class="pageNumber"></span></div>`,
      });
      await page.close();
    }
  } finally {
    await browser.close();
  }
  // Chromium leaves U+0000 in the PDF's text map for the font's alternate glyphs; give them their characters (needs python3, pypdf, fontTools).
  const fix = spawnSync('python3', ['-I', join(HERE, 'fix_tounicode.py'), ...['en', 'ar'].map((l) => join(HERE, 'out', `flygaca-c172n-training-handbook-${l}.pdf`))], { stdio: 'inherit' });
  if (fix.status !== 0) throw new Error('fix_tounicode.py failed: the PDFs still carry NUL characters');
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const html = await render();
  if (process.argv.includes('--check')) {
    let current = '';
    try { current = readFileSync(OUT_HTML, 'utf8'); } catch { /* missing */ }
    if (current !== html) {
      console.error('11_training_handbook/index.html is stale: run node 11_training_handbook/build.mjs');
      process.exit(1);
    }
    console.log('training handbook: ok');
  } else {
    writeFileSync(OUT_HTML, html);
    console.log('wrote 11_training_handbook/index.html');
    if (process.argv.includes('--pdf')) {
      await printPdfs();
      console.log('wrote 11_training_handbook/out/flygaca-c172n-training-handbook-{en,ar}.pdf');
    }
  }
}
