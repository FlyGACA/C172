// Build every figure in figures.json, in every language, with real Chromium (so Arabic is shaped and
// laid out by the same engine that readers' browsers use, and the PDF is true vector).
//
//   node 09_book_figures/build.mjs                 all figures -> 09_book_figures/out/
//   node 09_book_figures/build.mjs --fig asi-markings --lang ar
//   node 09_book_figures/build.mjs --out /tmp/figs --check     build elsewhere, fail on any problem
//
// Per figure and language:
//   out/<lang>/<id>.pdf        print master: exact size in mm, vector, fonts embedded, no caption
//   out/<lang>/<id>.svg        editable vector (vector figures only)
//   out/preview/<id>.<lang>.png   review sheet with number, caption and review status

import http from 'node:http';
import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { extname, join, normalize } from 'node:path';
import { fileURLToPath } from 'node:url';

const pw = await import(process.env.PLAYWRIGHT_MODULE || 'playwright');
const { chromium } = pw.default ?? pw;
const ROOT = fileURLToPath(new URL('../', import.meta.url));
const HERE = fileURLToPath(new URL('./', import.meta.url));
const args = process.argv.slice(2);
const option = (name) => (args.includes(name) ? args[args.indexOf(name) + 1] : undefined);
const OUT = option('--out') || join(HERE, 'out');
const only = option('--fig');
const onlyLang = option('--lang');
const MIME = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.mjs': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.png': 'image/png', '.ttf': 'font/ttf', '.svg': 'image/svg+xml' };

const server = http.createServer(async (req, res) => {
  const path = normalize(decodeURIComponent(new URL(req.url, 'http://x').pathname)).replace(/^([/\\])+/, '');
  if (path.includes('..')) { res.writeHead(400).end(); return; }
  try { const body = await readFile(join(ROOT, path)); res.writeHead(200, { 'content-type': MIME[extname(path)] || 'application/octet-stream' }).end(body); }
  catch { res.writeHead(404).end('not found'); }
});
await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
const base = `http://127.0.0.1:${server.address().port}/09_book_figures/figure.html`;

const manifest = JSON.parse(await readFile(join(HERE, 'figures.json'), 'utf8'));
const css = await readFile(join(HERE, 'css/figure.css'), 'utf8');
const artCss = css.slice(css.indexOf('/* ---------- inside the artwork')).replace(/^/, `:root{${/:root\s*{([^}]*)}/.exec(css)[1]}}\n`);
// Chromium stamps the build time into each PDF. Pin it (same length, so offsets stay valid) so that
// rebuilding an unchanged figure gives an identical file and git only shows real changes.
function stableDates(buffer) {
  const text = buffer.toString('latin1').replace(/\/(CreationDate|ModDate) \(D:\d{14}/g, '/$1 (D:20000101000000');
  return Buffer.from(text, 'latin1');
}

const browser = await chromium.launch();
const problems = [];
let built = 0;

for (const figure of manifest.figures) {
  if (only && figure.id !== only) continue;
  for (const lang of manifest.languages) {
    if (onlyLang && lang !== onlyLang) continue;
    for (const preview of [false, true]) {
      const page = await browser.newPage({ viewport: { width: 1000, height: 800 }, deviceScaleFactor: 2 });
      const errors = [];
      page.on('console', (message) => { if (message.type() === 'error') errors.push(message.text()); });
      page.on('pageerror', (error) => errors.push(error.message));
      page.on('requestfailed', (request) => errors.push(`request failed: ${request.url()}`));
      await page.goto(`${base}?fig=${figure.id}&lang=${lang}${preview ? '&preview=1' : ''}`);
      await page.waitForFunction(() => window.__figure?.ready || window.__figure?.error, null, { timeout: 60000 });
      const state = await page.evaluate(() => window.__figure);
      if (state.error) errors.push(state.error);
      if (!state.error) {
        if (preview) {
          await mkdir(join(OUT, 'preview'), { recursive: true });
          await (await page.$('#sheet')).screenshot({ path: join(OUT, 'preview', `${figure.id}.${lang}.png`) });
        } else {
          await mkdir(join(OUT, lang), { recursive: true });
          const pdf = await page.pdf({ width: `${state.width_mm}mm`, height: `${(state.height_mm + 0.05).toFixed(2)}mm`, printBackground: true, pageRanges: '1' });
          await writeFile(join(OUT, lang, `${figure.id}.pdf`), stableDates(pdf));
          if (state.vector) {
            const svg = await page.evaluate((style) => {
              const node = document.getElementById('art').cloneNode(true);
              node.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
              const tag = document.createElementNS('http://www.w3.org/2000/svg', 'style');
              tag.textContent = style;
              node.insertBefore(tag, node.firstChild);
              return new XMLSerializer().serializeToString(node);
            }, artCss);
            await writeFile(join(OUT, lang, `${figure.id}.svg`), `<?xml version="1.0" encoding="UTF-8"?>\n${svg}\n`);
          }
          built += 1;
        }
      }
      for (const error of errors) problems.push(`${figure.id} [${lang}]: ${error}`);
      await page.close();
    }
    console.log(`${problems.length ? '!!' : 'ok'} ${figure.number.padEnd(5)} ${figure.id} [${lang}]`);
  }
}
await browser.close();
server.close();
console.log(`${built} figure file set(s) written to ${OUT}`);
if (problems.length) {
  console.error(`\n${problems.length} problem(s):\n  ${problems.join('\n  ')}`);
  process.exit(1);
}
