#!/usr/bin/env node
// Home page data: site/home-data.js, everything the root index.html shows that
// is a fact about the project. Nothing is typed into the page.
//   - the part count, from 08_realistic_digital_twin/docs/06_parts_index.md
//   - the flight lessons, from shared/js/lessons.js
//   - the phases and their dates, from RELEASES.md
// `--check` writes nothing and exits 1 if site/home-data.js is out of date.
import { existsSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

export const ROOT = dirname(dirname(fileURLToPath(import.meta.url)));
const DST = 'site/home-data.js';
const HEAD = '// Built by scripts/build_site.mjs from RELEASES.md, shared/js/lessons.js and the Phase 8 parts index. Do not edit by hand.\nwindow.HOME=';

// Where each phase opens. Phases with no page of their own link to their folder's README.
const PAGES = {
  '01': '01_initial/README.md',
  '02': '02_classic_analog_v2/FlyGACA_Interactive_Viewer.html',
  '02b': '02b_refined_airframe/FlyGACA_Interactive_Viewer.html',
  '03': '03_education/FlyGACA_Instrument_Training_Lab.html',
  '04': '04_digital_twin/FlyGACA_C172N_Learning_Lab.html',
  '04b': '04b_poh_reference/FlyGACA_C172N_Learning_Lab.html',
  '05': '05_systems_lab/FlyGACA_Systems_Lab.html',
  '06': '06_interactive_twin/FlyGACA_C172N_Phase6_Viewer.html',
  '07': '07_kinematic_twin/index.html',
  '08': '08_realistic_digital_twin/index.html',
  '09': '09_book_figures/atlas/README.md',
};

/** The phases as RELEASES.md lists them: `07 — Kinematic twin (2026-11-06):`. */
export function phases(releases) {
  return [...releases.matchAll(/^(\d\d[a-z]?) — (.+)$/gm)].map(([, id, rest]) => {
    const dated = rest.match(/^(.*?) \((\d{4}-\d{2}-\d{2})\):?$/);
    const title = (dated ? dated[1] : rest).replace(/[.:]$/, '');
    return { id, title, date: dated ? dated[2] : null, page: PAGES[id] && existsSync(join(ROOT, PAGES[id])) ? PAGES[id] : null };
  });
}

/** `**1198 parts.**` in the generated parts index. */
export function partCount(index) {
  const m = index.match(/\*\*(\d+) parts\.\*\*/);
  return m ? Number(m[1]) : null;
}

export async function build() {
  const { LESSONS } = await import(pathToFileURL(join(ROOT, 'shared/js/lessons.js')).href);
  const home = {
    parts: partCount(readFileSync(join(ROOT, '08_realistic_digital_twin/docs/06_parts_index.md'), 'utf8')),
    parts_from: '08_realistic_digital_twin/docs/06_parts_index.md',
    lessons: LESSONS.map((l) => ({ id: l.id, en: l.title.en.replace(/^Flight lesson: /, ''), ar: l.title.ar.replace(/^درس طيران: /, ''), poh: l.poh })),
    phases: phases(readFileSync(join(ROOT, 'RELEASES.md'), 'utf8')),
  };
  return `${HEAD}${JSON.stringify(home)};\n`;
}

if (process.argv[1] && fileURLToPath(import.meta.url) === process.argv[1]) {
  const text = await build();
  if (process.argv.includes('--check')) {
    const current = existsSync(join(ROOT, DST)) ? readFileSync(join(ROOT, DST), 'utf8') : '';
    if (current !== text) {
      console.error(`${DST} is out of date: run \`npm run build:site\``);
      process.exit(1);
    }
    console.log(`${DST} is current`);
  } else {
    writeFileSync(join(ROOT, DST), text);
    console.log(`wrote ${DST}`);
  }
}
