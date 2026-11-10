# Phase 9 — Book figures

Print-ready figures for the FlyGACA Cessna 172N book, built from the same data as the simulator and
the 3D twin, in English and Arabic.

**Start with [the plan](PLAN.md)** — which kind of picture to use for which job, why the generated
aircraft has not looked right, and the order of work. [النسخة العربية](README_AR.md)

## Three samples, one per method that works today

| | |
|---|---|
| ![Airspeed indicator](out/preview/asi-markings.en.png) | **S-1 · Instrument, drawn from data.** Scale, arcs and red line are read from `08_realistic_digital_twin/data/instruments.json`. |
| ![Fuel system](out/preview/fuel-system.ar.png) | **S-2 · System schematic (Arabic edition shown).** Symbols and four line codes; capacities from the POH constants in `shared/js/sim.js`. |
| ![Flight controls](out/preview/flight-controls.en.png) | **S-3 · Illustration from the 3D twin.** Flat tones and ink outlines, not a fake photograph; labels placed by code from the model's part names. |

All three are `draft`: nobody has yet checked them against the aircraft's own POH.

## Build

```bash
npm ci                    # Playwright, once
npm run figures           # every figure, both languages -> 09_book_figures/out/
npm run figures:render    # re-render the 3D illustrations in Blender (only when the model or a camera changes)
npm test                  # includes tests/figures.test.mjs
```

| Output | Use |
|---|---|
| `out/<lang>/<id>.pdf` | Print master: exact size in millimetres, vector, fonts embedded, no caption |
| `out/<lang>/<id>.svg` | Editable vector (vector figures only; install IBM Plex Sans Arabic to edit) |
| `out/preview/<id>.<lang>.png` | Review sheet with figure number, caption and review status |

With the pinned Playwright, rebuilding an unchanged figure gives byte-identical files, so git shows only real changes.

To work on one figure, serve the repository root (`npm run serve`) and open
`/09_book_figures/figure.html?fig=fuel-system&lang=ar&preview=1`.

## Add a figure

1. Add an entry to [`figures.json`](figures.json): `id`, `number`, `kind`, `method`, bilingual `title`,
   `sources` (POH page for every fact) and `status: "draft"`.
2. Put its text in `data/<name>.json` under `strings.en` and `strings.ar` (same keys in both).
3. Write `js/figures/<name>.js` exporting `size` (`[width, height]`, one unit = 0.1 mm) and
   `draw({ svg, t, text, data, json, lang, dir })`. Read numbers from the repository's data files
   rather than typing them.
4. For a figure from the 3D twin, add `data/<name>.render.json` (camera, tinted parts, parts to label)
   and reference it as `render` in the manifest. `render_figure.py` writes the picture and the pixel
   position of every labelled part; `js/callouts.js` places the labels.
5. `npm run figures && npm test`.

## Files

```
PLAN.md                    the figure plan
figures.json               manifest: one entry per figure, with sources and review status
figure.html, js/host.js    page that draws one figure (?fig=&lang=&preview=1)
js/svg.js                  SVG helpers; text alignment that works in both writing directions
js/callouts.js             automatic label placement with leader lines
js/figures/                one module per figure
data/                      bilingual text per figure; render recipes for 3D figures
blender/render_figure.py   illustration-style render + label anchor points
renders/                   rendered illustrations and their anchor files
css/figure.css             the shared visual language (type, colours, line codes)
build.mjs                  Chromium build to PDF / SVG / PNG
vendor/fonts/              IBM Plex Sans Arabic (SIL Open Font License, see OFL.txt)
tests/figures.test.mjs     manifest, bilingual text, provenance and data-agreement checks
```

## Limits

- The samples are drafts for review, not approved training material. Use the aircraft's POH/AFM.
- 3D-derived figures inherit the model's geometry status (`estimated` except the POH dimensions).
  [PLAN.md](PLAN.md) describes how to correct it.
- Arabic terminology follows the vocabulary already used in this repository and needs a native
  instructor's review before print.
