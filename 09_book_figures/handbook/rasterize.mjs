// Flatten the plates' SVGs with Chromium, to a lossless picture that book_plates.py encodes once as the book's JPEG.
//   node 09_book_figures/handbook/rasterize.mjs [id ...]       cache/flat-src/<id>.svg -> cache/flat/<id>.png (data-px-per-unit px to a unit)
import { readFile, readdir, writeFile, mkdir } from 'node:fs/promises';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';

const pw = await import(process.env.PLAYWRIGHT_MODULE || 'playwright');
const { chromium } = pw.default ?? pw;
const HERE = fileURLToPath(new URL('./', import.meta.url));
const SRC = join(HERE, 'cache', 'flat-src');
const wanted = process.argv.slice(2);
const files = (await readdir(SRC)).filter((f) => f.endsWith('.svg') && (!wanted.length || wanted.includes(f.slice(0, -4))));
const FLAT = join(HERE, 'cache', 'flat');
await mkdir(FLAT, { recursive: true });
const browser = await chromium.launch();
for (const file of files) {
  const svg = await readFile(join(SRC, file), 'utf8');
  const [, w, h] = /viewBox="0 0 (\d+) (\d+)"/.exec(svg);
  const scale = +(/data-px-per-unit="([\d.]+)"/.exec(svg)?.[1] ?? 3);
  const page = await browser.newPage({ viewport: { width: +w, height: +h }, deviceScaleFactor: scale });
  await page.setContent(`<!doctype html><body style="margin:0;background:#fff">${svg.replace(/^<\?xml[^>]*>\s*/, '')}</body>`);
  await page.waitForFunction(() => [...document.images].every((i) => i.complete), null, { timeout: 30000 }).catch(() => {});
  await page.waitForTimeout(150);
  const shot = await page.screenshot({ type: 'png', clip: { x: 0, y: 0, width: +w, height: +h } });
  await writeFile(join(FLAT, file.replace(/\.svg$/, '.png')), shot);
  await page.close();
  console.log('flattened', file);
}
await browser.close();
