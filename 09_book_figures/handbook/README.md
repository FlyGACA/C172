# Handbook plates

Pictures from the 3D twin, drawn in the format the handbook (the book repository, `handbook/ppl/figures/`) uses for its
artwork, so that a figure of the book that looks poor can be replaced by a file of the same name without touching the
book's text.

The book's rules for artwork, which these follow:

- The two editions (English, Arabic) share **one file** for each figure, so the artwork carries **no words**: parts are
  marked with **numbered callouts**, and each edition explains the numbers in a numbered list under the figure.
- A figure keeps its file name (`fig-05-01-four-forces.svg`) and its callout numbers, so the list under it, the text
  that refers to "callout 6" and the review files stay as they are.
- Rendered colour plates from the model are `plate-NN-NN-short-name.jpg`.

## What is here

| Plate | Replaces in the book | Made from | Callouts |
|---|---|---|---|
| `fig-05-01-four-forces` | Figure 5-1, the four forces in straight-and-level flight | the model, level flight, side view | 1 lift · 2 weight · 3 thrust · 4 drag · 5 centre of gravity · 6 tail-down force |
| `fig-05-02-airfoil-angle-of-attack` | Figure 5-2, airfoil terms, relative wind and angle of attack | a drawing of the NACA 2412 section the model's wing is built from | 1 leading edge · 2 trailing edge · 3 chord line, extended ahead · 4 mean camber line · 5 relative wind · 6 angle of attack α · 7 flight path · 8 lift · 9 drag |
| `fig-10-01-instrument-panel` | Figure 10-1, the six flight instruments in straight and level cruise | the model's panel, square on: 105 kt, level, 3,500 ft, no turn, heading 120°, no climb | 1 airspeed · 2 attitude · 3 altimeter · 4 turn coordinator · 5 heading · 6 vertical speed · 7 the basic T |
| `fig-10-03-airspeed-indicator-markings` | Figure 10-3, colour markings on an airspeed indicator | the model's airspeed indicator, square on, 105 kt | 1 white arc · 2 green arc · 3 yellow arc · 4 red line · 5 VS0 · 6 VS1 · 7 VFE · 8 VNO |
| `plate-07-01-airframe` | Colour plate 7-1, the five major components | the model, three-quarter view, ink and tint | 1 wing · 2 fuselage · 3 powerplant · 4 landing gear · 5 empennage |
| `plate-07-02-control-surfaces` | Colour plate 7-2, movable control surfaces | the model from above, ink and tint: ailerons, elevator and rudder in amber, flaps in blue | none: the colours explain it, as the caption does (the book's text may number it: check) |

(The legends are what the English edition says today. Where a legend and a plate disagree the plate is wrong: the numbers are
checked against `legend` in `plates.json` by `tests/test_plates.py`.)

Outputs, in `out/`:

- `<id>.svg`: the figure, under the file name of the one it replaces. The render is embedded as a JPEG, the callouts are vector, the
  digits are outlines (no font is needed). 640 units wide like the book's other figures, 3 px to the unit.
- `preview/<id>.jpg`: the same, flattened by Chromium. For the two colour plates (`plate-07-01`, `plate-07-02`) this is the file
  the book wants (`plate-NN-NN-name.jpg`); for a figure it is what to use if the book's build does not take an SVG with a
  picture in it, and what to look at to review.

## What changed against the figures it replaces

The old figures were drawn by hand as flat vectors: a toy aeroplane in 5-1, a lens-shaped section with no camber in 5-2, a
generic dial in 10-3. These come from the digital twin of the aircraft, so they are the aircraft (paint, windows, struts, the
spinner and propeller, the gauges with their real scales and arcs) and they change when the twin changes. Two facts they put
right on the way: the airspeed indicator's white arc, which the dial drawing had wiped out wherever the green arc overlapped it
(`blender/c172/dials.py`), and the turn coordinator's ball, which sat on a tube drawn the wrong way up.

The numbers on the dials are those of the Cessna 172N handbook (white arc 41 to 85 KIAS, green 47 to 128, yellow 128 to 160, red line
160). Figure 10-3's text calls them illustrative; they are a real aeroplane's.

## Build

```bash
npm run plates:fine       # the dials at 1024 px a cell (the model carries 512), once        -> handbook/cache/ (not kept)
npm run plates:render     # the renders in Blender, 5 to 25 minutes each                      -> handbook/renders/<id>.png
npm run plates:build      # compose (build_plates.py) and flatten (rasterize.mjs)             -> handbook/out/
npm run test:plates:py    # the book's rules for artwork, on plates.json and on out/
```

`plates:render` takes `--plate <id>` and `--quick` (half size, few samples, for choosing a camera) after `--`. To change a
callout, edit the plate in `plates.json` and run `plates:build`: no new render. To change a view, edit its `render` recipe
(documented at the top of `blender/render_plate.py`) and render that plate again. `plate-07-01-airframe` is the picture of
`renders/aircraft-exterior.png` (`npm run figures:render`) with callouts; the airfoil is drawn by `vector_plates.py`.

`make_glyphs.py` (needs fontTools) wrote `glyphs.json`, the outlines of the digits and of α in Inter Bold; it does not have to be run again.

## What these are not

- Not a record of an aircraft: no registration, no operator's marks other than the model's own wordmark, and the panel is the
  model's estimate of the handbook's figure of it (`../../08_realistic_digital_twin/docs/12_cockpit.md`).
- Not reviewed against the book's own sources. The numbers they show (airspeeds, heading, altitude) are the figure's legend's.
- Whether the book's build accepts an SVG that embeds a JPEG is untested: this session had no access to the book repository.
  If it does not, use `preview/<id>.jpg` as a plate.
