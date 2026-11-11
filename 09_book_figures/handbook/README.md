# Handbook plates

Pictures from the 3D twin, in the format the handbook (the book repository, `handbook/ppl/figures/`) takes for its
artwork, so that a figure of the book that looks poor can be replaced without touching the book's text: the caption, the
numbered list under the figure and the callout numbers stay as they are.

The book's rules for artwork, which these follow:

- The two editions (English, Arabic) share **one file** for each figure, so the artwork carries **no words**: parts are
  marked with **numbered callouts**, and each edition explains the numbers in a numbered list under the figure.
- A figure keeps its callout numbers, so the list under it and the text that refers to "callout 6" stay as they are.
- The book's build takes two kinds of file (its `docs/handbook.md`, Figures): an SVG of at most 40 KB with no picture in it
  (`fig-NN-NN-name.svg`), and a JPEG colour plate of at most 800 KB, 3,200 px a side, 8-bit RGB, with no metadata
  (`plate-NN-NN-name.jpg`). A render cannot be the first, so a render becomes a plate and keeps its caption's number: Figure 5-1 is
  `plate-05-01-four-forces.jpg`. A drawing (the airfoil) stays an SVG. `book_rules.py` repeats the book's checks.

## What is here

| Plate | Book file | Made from | Callouts |
|---|---|---|---|
| `fig-05-01-four-forces` | `plate-05-01-four-forces.jpg`: Figure 5-1, the four forces in straight-and-level flight | the model, level flight, side view, with the forces drawn over it | 1 lift · 2 weight · 3 thrust · 4 drag · 5 centre of gravity · 6 tail-down force |
| `fig-05-02-airfoil-angle-of-attack` | `fig-05-02-airfoil-angle-of-attack.svg`: Figure 5-2, airfoil terms, relative wind and angle of attack | a drawing of the NACA 2412 section the model's wing is built from | 1 leading edge · 2 trailing edge · 3 chord line, extended ahead · 4 mean camber line · 5 relative wind · 6 angle of attack α · 7 flight path · 8 lift · 9 drag |
| `fig-10-01-instrument-panel` | `plate-10-01-instrument-panel.jpg`: Figure 10-1, the six flight instruments in straight and level cruise | the model's panel, square on: 105 kt, level, 3,500 ft, no turn, heading 120°, no climb | 1 airspeed · 2 attitude · 3 altimeter · 4 turn coordinator · 5 heading · 6 vertical speed · 7 the basic T |
| `fig-10-03-airspeed-indicator-markings` | `plate-10-03-airspeed-indicator-markings.jpg`: Figure 10-3, colour markings on an airspeed indicator | the model's airspeed indicator, square on, no needle | 1 white arc · 2 green arc · 3 yellow arc · 4 red line · 5 VS0 · 6 VS1 · 7 VFE · 8 VNO |
| `plate-07-01-airframe` | `plate-07-01-airframe.jpg`: Colour plate 7-1, the five major components | the model from the front left and above: wings blue, tail group green, powerplant orange, landing gear gold, the fuselage in its own paint | 1 wing · 2 fuselage · 3 powerplant · 4 landing gear · 5 empennage |
| `plate-07-02-control-surfaces` | `plate-07-02-control-surfaces.jpg`: Colour plate 7-2, movable control surfaces | the model from behind, to the right and above: aileron, elevator and rudder painted amber, flap blue | 1 aileron · 2 flap · 3 elevator · 4 rudder |

(The legends are what the English edition says today. Where a legend and a plate disagree the plate is wrong: the numbers are
checked against `legend` in `plates.json` by `tests/test_plates.py`.)

Outputs, in `out/`:

- `book/<book file>`: **what goes into the book's `handbook/ppl/figures/`**, checked against the book's rules (`book_plates.py`). The
  JPEGs are the picture and the callouts flattened and encoded once (the sharpest that fits 780 KB); the SVG is the airfoil.
- `<id>.svg`: the same figure as a master, with the render embedded as a JPEG, the callouts as vector and the digits as outlines (no
  font is needed), 640 units wide like the book's other figures. The book does not take it (an SVG with a picture in it breaks its rules);
  it is there for whoever wants the callouts as vector.

## The rest of the book's figures

The first six plates are in `plates.json`. The others are one Python module each in `figs/` (`f_NN_NN_name.py`, a function `plate()` that
returns a plate in the same form; `plates_spec.py` joins them), written in three ways:

- **Composite plates** (`"layers"`): several renders, each in a box of the canvas, with vector overlays over them. The instrument figures
  (28-4 to 28-7, 6-3) lay out renders of single instruments of the model (`figs/kit.py` `dial_layer`: bezel, dial and pointers with the readings
  of the situation, a soft shadow, anchors on the rim for the callouts); 22-6 has a night view from above with the three sectors of light drawn
  under the aeroplane (`"ground"`) and four night views of the aeroplane from the front left, front right, head on and from behind.
- **Renders with a drawing over them** (`"render"` and `"overlays"`): 7-1 (the three axes), 25-4 (the walk-around route). Overlays are numbered
  callouts (also sitting on a route, `"on"`), arrows (also an out-and-back `"pair"`), paths and arcs projected from 3D, text, pictograms, sectors of
  light, glowing dots, free markup and pictures of the aeroplane (`"sprite"`); see `build_plates.py` `overlays()`.
- **An old figure with the model's aeroplane in it** (`"reskin"`, `reskin.py`): the diagram of the figure the book had (its SVG kept in `old/`)
  with its flat aeroplane symbols replaced by pictures of the model, in the same place, heading and size, tinted where the symbol was coloured, in the
  book's fonts. Fifty-seven figures are made this way. A symbol the patterns of `reskin.py` do not know is named in the figure's module: `"drop"` takes a
  stretch of the old drawing out and puts the new things there (so that the z-order stays: a sprite can lie over a flight path and under a callout, and
  `"before"` draws something under it), `"remove"`, `"replace"`, `"sprites"` and `"markup"` do the rest; `figs/kit.py` `side_plane()` stands the model on the
  wheels of an old silhouette (its translate, rotate and scale), and `dial_sprite()` makes one instrument of the model a picture to set into an old figure
  (31-4). Where the old drawing is a diagram of something the model does not have (a low-wing aeroplane, an airliner), or of an idea rather than of the
  aeroplane (the vestibular illusions), the drawing stays.

The pictures of the aeroplane are `figs/sprites.py`: from above, from the side (both sides), from ahead, from behind, from above by moonlight and in a
developed spin, rendered once on a transparent background, and the four instruments of Figure 31-4 (`npm run plates:render` makes them with the rest).

`to_book.py <book checkout>` puts the finished plates of `out/book/` into the book's `handbook/ppl/figures/`, points both editions' chapters at
them and removes the figures they replace; then the book's own `build_handbook.py --swap` and `build_review_packet.py`. The raw renders
(`renders/`) and the web SVGs (`out/<id>.svg`) of these plates are **not kept in git** (they are large): `npm run plates:render` makes them
again, and `build_plates.py` skips a plate whose render is missing (a re-skinned plate waits only for the pictures of the aeroplane it lays on its drawing,
and the message names the ones missing; a plate named on the command line is built or fails).

## What changed against the figures it replaces

The old figures were drawn by hand as flat vectors: a toy aeroplane in 5-1, a lens-shaped section with no camber in 5-2, a
generic dial in 10-3. These come from the digital twin of the aircraft, so they are the aircraft (paint, windows, struts, the
spinner and propeller, the gauges with their real scales and arcs) and they change when the twin changes. Two facts they put
right on the way: the airspeed indicator's white arc, which the dial drawing had wiped out wherever the green arc overlapped it
(`blender/c172/dials.py`), and the turn coordinator's ball, which sat on a tube drawn the wrong way up.

**The airspeed indicator carries the book's numbers, not the model's.** The book's example aeroplane (its `docs/handbook.md`: chapters
11 to 13 and Part 7 build on it) has `VS0` 45, `VS1` 52, `VFE` 90, `VNO` 125 and `VNE` 160 kt, which Figure 10-3 gives. The model's
indicator has the Cessna 172N's (white arc 41 to 85, green 47 to 128, yellow 128 to 160). The plates draw the book's: `plates.json`
`"dials"` lays them over `data/instruments.json` for the plates only, and `fine_textures.py` draws the finer dial atlas with them. The model
and the viewer keep the 172N's.

## Build

```bash
npm run plates:fine       # the dials at 1024 px a cell (the model carries 512), once        -> handbook/cache/ (not kept)
npm run plates:render     # the renders in Blender, 5 to 25 minutes each                      -> handbook/renders/<id>.png
npm run plates:build      # compose (build_plates.py), flatten (rasterize.mjs), encode (book_plates.py) -> handbook/out/, handbook/out/book/
npm run test:plates:py    # the book's rules for artwork, on plates.json, on out/ and on out/book/
```

`plates:render` takes `--plate <id>` and `--quick` (half size, few samples, for choosing a camera) after `--`. To change a
callout, edit the plate in `plates.json` and run `plates:build`: no new render. To change a view, edit its `render` recipe
(documented at the top of `blender/render_plate.py`: cameras, parts shown or hidden, instrument readings, parts painted one colour,
callout points that the camera really sees) and render that plate again. The airfoil is a drawing, not a render (`vector_plates.py`).
A plate can also take a picture made elsewhere (`"source"` in `plates.json`, for example the ink pictures of `../README.md`).

`make_glyphs.py` (needs fontTools) wrote `glyphs.json`, the outlines of the digits and of α in Inter Bold; it does not have to be run again.

## What these are not

- Not a record of an aircraft: no registration, no operator's marks other than the model's own wordmark, and the panel is the
  model's estimate of the handbook's figure of it (`../../08_realistic_digital_twin/docs/12_cockpit.md`).
- Not reviewed against the book's own sources. The numbers they show (airspeeds, heading, altitude) are the figure's legend's.
- The dials carry the instruments' own English legends (AIRSPEED, KNOTS, ...), as the real instruments do. The book's artwork carries no
  words so that both editions share a file; a picture of an instrument is the one place a word is part of the thing. Whether to keep them
  is for the book's editorial review (its docs say that raster lettering needs one).
