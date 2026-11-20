# Phase 11 — C172N training handbook

FlyGACA's own handbook for the Cessna 172N of the twin, in English and Arabic: [the page](index.html), and A4 PDFs in
[`out/`](out/). [النسخة العربية](README_AR.md)

It follows the order a pilot knows from the Pilot's Operating Handbook (general, limitations, emergency procedures,
normal procedures, performance, weight and balance, systems), but the text is FlyGACA's and it is **not** a Pilot's
Operating Handbook or an Airplane Flight Manual. No authority and no manufacturer has approved it, and it must never be
used to fly. Every page says so in both languages, with the notice the home page carries.

## Where the values come from

Nothing is typed into the text without its source. The values are the twin's records of the Cessna Model 172N Pilot's
Operating Handbook (1979 model, issued 1 July 1978), each with its page:

| Record | Used for |
|---|---|
| [`08_realistic_digital_twin/data/poh_references.json`](../08_realistic_digital_twin/data/poh_references.json) | Engine, propeller, fuel, oil, limits, checklists, systems, loading stations, dimensions |
| [`04b_poh_reference/poh_1979_reference_data.json`](../04b_poh_reference/poh_1979_reference_data.json) | Maximum takeoff weight |
| [`08_realistic_digital_twin/data/instruments.json`](../08_realistic_digital_twin/data/instruments.json) | Instrument arcs and red lines |
| [`shared/js/poh_tables.js`](../shared/js/poh_tables.js) | Speeds, stall speeds, takeoff, climb, cruise, landing and glide tables |

The four figures are Phase 9's ([`09_book_figures/`](../09_book_figures/README.md)), used as they are.

In [`content.mjs`](content.mjs) each block of text names the records it rests on, and the page prints their POH pages
beside it. The tests fail when a number in a block is not in one of those records, when a record has no page, when a
language is missing, or when `index.html` is stale.

## Build

```bash
node 11_training_handbook/build.mjs          # write index.html
node 11_training_handbook/build.mjs --pdf    # also print out/flygaca-c172n-training-handbook-{en,ar}.pdf (Playwright)
node 11_training_handbook/build.mjs --check  # fail when index.html is stale
node --test 11_training_handbook/tests/handbook.test.mjs
```

The npm scripts are `handbook`, `handbook:pdf` and `handbook:check`, and `npm test` runs the tests. Change a value in its
record, never in the page; change the wording in `content.mjs`, then rebuild.

## Not yet done

- No pilot or instructor has reviewed the text, and the Arabic has not had a native aviation reader.
- The twin records only some of the handbook's emergency procedures and some rows of its performance figures; the page
  says so where it applies.
