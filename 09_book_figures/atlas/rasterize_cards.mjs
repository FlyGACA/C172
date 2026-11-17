// Flatten the cards of the atlas with Chromium:  node rasterize_cards.mjs [icao ...]     cache/<icao>.svg -> out/card-<icao>.jpg (3 px to a unit)
import { readFile, readdir, writeFile, mkdir } from 'node:fs/promises';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';

const pw = await import(process.env.PLAYWRIGHT_MODULE || 'playwright');
const { chromium } = pw.default ?? pw;
const HERE = fileURLToPath(new URL('./', import.meta.url));
const wanted = process.argv.slice(2).map((s) => s.toLowerCase());
const files = (await readdir(join(HERE, 'cache'))).filter((f) => f.endsWith('.svg') && (!wanted.length || wanted.includes(f.slice(0, -4))));
await mkdir(join(HERE, 'out'), { recursive: true });
const browser = await chromium.launch();
for (const file of files) {
  const svg = await readFile(join(HERE, 'cache', file), 'utf8');
  const [, w, h] = /viewBox="0 0 ([0-9.]+) ([0-9.]+)"/.exec(svg);
  const page = await browser.newPage({ viewport: { width: +w, height: +h }, deviceScaleFactor: 3 });
  await page.setContent(`<!doctype html><body style="margin:0;background:#fff">${svg}</body>`);
  await page.waitForFunction(() => [...document.images].every((i) => i.complete), null, { timeout: 30000 }).catch(() => {});
  await page.waitForTimeout(150);
  const shot = await page.screenshot({ type: 'jpeg', quality: 90, clip: { x: 0, y: 0, width: +w, height: +h } });
  await writeFile(join(HERE, 'out', 'card-' + file.replace(/\.svg$/, '.jpg')), shot);
  await page.close();
  console.log('flattened', file);
}
await browser.close();
