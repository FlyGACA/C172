# C172 study visuals

Deterministic, POH-cited SVG figures for the FlyGACA Individuals funnel. The pack ships one free
sample visual and three premium visuals, in English and Arabic editions.

**Training and reference only. Not for flight, navigation or maintenance.** Every figure is drawn
for study; none of it replaces the aircraft's POH.

> Fly GACA is an independent educational platform, not affiliated with, endorsed by, or operated by
> GACA or the Government of Saudi Arabia. GACA (gaca.gov.sa) is always the authoritative source.
>
> فلاي قاكا منظومة تعليمية مستقلة، غير تابعة لهيئة الطيران المدني (GACA) وغير مرتبطة بها ولا معتمدة منها.
> هيئة الطيران المدني هي المصدر الرسمي.

## Visuals

| File | Tier | Title | POH pages |
| --- | --- | --- | --- |
| `v-speeds` | free | V-speeds and airspeed colour arcs | p.2-4 Fig 2-1; p.2-5 Fig 2-2 |
| `fuel-capacity` | premium | Fuel capacity, standard and long-range tanks | p.1-4; p.2-6 Fig 2-3 |
| `alternate-static` | premium | Airspeed correction with the alternate static source | p.5-9 Fig 5-1 sheet 2 |
| `engine-propeller` | premium | Engine, propeller and operating limits | p.1-3; p.2-5; p.2-6 Fig 2-3 |

Each figure exists as `out/en/<id>.svg` and `out/ar/<id>.svg`. Manifest metadata (tier, titles,
sources, bilingual strings) is in [`manifest.json`](manifest.json); per-figure data and strings are
in [`visuals/`](visuals).

## Where the numbers come from

- `shared/js/sim.js` — the repository's POH constants: V-speeds, airspeed arcs, tank capacities and
  `ALT_STATIC_TABLE` (POH p.5-9 Fig 5-1 sheet 2). The builder reads this file at build time.
- `08_realistic_digital_twin/data/poh_references.json` — the cited POH table (59 values, each with a
  page). Every source and fact in this pack points at a key in that file.
- `08_realistic_digital_twin/data/instruments.json` — the airspeed indicator arcs; the test compares
  them with the figure data and with `sim.js`.

No value is typed into this pack from memory. Derived quantities are labelled as derived: per-tank
usable fuel is the published usable total divided by two, and the alternate-static line between
published points is a straight-line interpolation for study only.

Nothing here is airspace or navigation data, so no AIP or GACAR citation is claimed; the source for
every figure is the Cessna 172N POH.

## Build

```sh
python3 content/study-visuals/build.py            # writes content/study-visuals/out/
python3 content/study-visuals/build.py --out DIR  # writes somewhere else
```

The builder uses only the Python standard library and is byte-for-byte deterministic: no clocks, no
randomness, stable file order. `out/` is committed so the funnel can serve the files directly.

## Tests

`tests/test_study_visuals.py` (run by `python -m unittest discover -s tests` in CI) checks that:

- every figure cites a POH page and every cited key exists in `poh_references.json` on that page;
- every fact string appears in the cited POH value;
- arcs, V-speeds, tank figures and the alternate-static table agree with `sim.js`, and the airspeed
  arcs also agree with `instruments.json`;
- English and Arabic string sets have identical keys, and every SVG carries the non-affiliation
  statement in both languages plus the "training and reference only" line;
- a rebuild into a temporary directory equals the committed `out/` byte for byte.

## Languages and right-to-left layout

The Arabic edition is a real layout, not mirrored markup: panels, cards and line starts swap sides,
anchors are chosen from the writing direction, and numeric runs such as `41–85` or `85 / 110` are
wrapped in left-to-right isolates (U+2066 ... U+2069), the same technique as
`09_book_figures/js/figures/aircraft_exterior.js`. Arabic wording in this pack is draft copy flagged
for native review; it must not be treated as reviewed regulatory prose.

## Status

`draft`. Figures are not linked from a published page yet; the funnel work that consumes them is
still behind its own flags.
