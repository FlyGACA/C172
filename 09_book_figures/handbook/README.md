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
  book's fonts. A hundred and one figures are made this way (seventy of them draw a new picture on the old canvas, `"blank": True`). A symbol the patterns of `reskin.py` do not know is named in the figure's module: `"drop"` takes a
  stretch of the old drawing out and puts the new things there (so that the z-order stays: a sprite can lie over a flight path and under a callout, and
  `"before"` draws something under it), `"remove"`, `"replace"`, `"sprites"` and `"markup"` do the rest; `figs/kit.py` `side_plane()` stands the model on the
  wheels of an old silhouette (its translate, rotate and scale), and `dial_sprite()` makes one instrument of the model a picture to set into an old figure
  (31-4). Where the old drawing is a diagram of something the model does not have (a low-wing aeroplane, an airliner), or of an idea rather than of the
  aeroplane (the vestibular illusions), the drawing stays.

The pictures of the aeroplane are `figs/sprites.py`: from above, from the side (both sides), from ahead, from behind, from above by moonlight and in a
developed spin, rendered once on a transparent background, and the four instruments of Figure 31-4 (`npm run plates:render` makes them with the rest).

The clouds of the weather figures are `figs/clouds.py` (recipes) and `blender/render_clouds.py` (the renderer; the model is not needed). A cloud is a few volumes of a
scattering medium lit by a physical sky and a white sun from the upper left: the heaps (cumulus, towering cumulus, the tower and the anvil of a cumulonimbus, a roll, the
fields of cloudlets of altocumulus and stratocumulus) are metaballs made into a closed mesh and then, by geometry nodes, into a grid whose density rises gently from the surface,
times a noise pattern that eats it into billows and wisps and is cut flat at the foot where the recipe says so; the layers (stratus, nimbostratus, a veil, cirrus) are a box whose
shader carries the whole pattern (a thickness that tapers and follows a slow noise, a foot ragged by noise, fibres of stretched ridged noise). Each is rendered on a transparent
background as a sprite (`renders/cloud-<kind>.png`: cumulus, towering cumulus, cumulonimbus, a dying anvil, stratus, a veil, nimbostratus, stratocumulus, altocumulus, a stack of
lenses, a roll, cirrus in two patterns, a thick altostratus, a wide cumulus, and the three decks of cirrocumulus, altocumulus and stratocumulus seen from the ground). `npm run plates:render:clouds` makes them (`--cloud <id>`, `--quick`, `--pixels`, `--samples`, `--set '{...}'` and `--suffix` after `--`; a minute or two for
the layers, ten to twenty for the towers, about two hours in all on four cores). A weather figure keeps its old diagram (the arrows, the rain, the
numbered callouts), takes the outlined clouds out with `"remove"`, puts a sky behind it with `"replace"` and lays the clouds in with a `"drop"` of the kind that
only inserts (the same text twice): a sprite overlay names the cloud, gives its place and `"width"`, and `"height"` where the figure wants it taller or thinner than
the cloud is; `"tint"` paints a cloud the colour of dust; `"haze"` fades a far cloud into the colour of the sky, `"feather"` softens its edge, `"flip"` turns it over.

The weather figures that show a place (14-3, 14-6, 14-7, 14-8, 14-9, 15-1, 15-4, 15-6) are drawn again as **illustrated scenes** on the old figure's canvas: a plate whose
`"reskin"` has `"blank": True` and `"layers"` starts from nothing and lays strings of SVG and cloud sprites in order, back to front. `figs/scene.py` is the kit: skies and the sun
and moon, the country of the Peninsula (hills, dunes, a sandy plain with scrub, date palms, acacias, flat-roofed houses, a sea with a dhow, a mountain of rock with strata, gullies
and a lit and a shaded face, a V valley with a lake of fog), ribbon arrows that curve and carry a shadow, rain, lightning, hail, banks of fog and dust, glass blocks for the fronts,
rounded cards for the figures that show several places, and the numbered callouts in the book's style. 15-2 keeps its diagram and gets the dark base of a storm and billows of dust.
The systems figures (8-1 the four strokes, 8-2 the carburettor, 9-1 the fuel system, 9-2 the electrical system, 9-3 the vacuum system, 10-2 the pitot-static system) are drawn again the same
way as illustrated cutaways and schematics: `figs/parts.py` has their gradients, lit pipes with flow arrows and a few fittings, each figure's module draws its own components (the cast body
and the float of the carburettor, the battery, the master switch and the alternator, the tanks and the strainer, the pump), and the instruments are the twin's own pictures (the dial
sprites of `figs/sprites.py`, with a heading indicator `dial-09-03-dg` added; `npm run plates:render` makes them). The figures that are charts of numbers (14-1, 14-5, 15-3, 15-7, 16-4) stay drawings. The captions, the numbered lists and the callouts are the old figures', in both editions;
the artwork has no words, only digits, symbols and METAR codes.

The figures that show a manoeuvre, a pattern or a piece of country from above (18-7, 25-6, 25-7, 26-4, 26-5, 27-2, 27-5, 27-7, 27-8, 28-8, 30-2, 30-3, 30-4) keep their diagrams and lie
on an **aerial view of the country**. `figs/terrain.py` makes it (numpy and Pillow, a few seconds a picture, the same picture for the same seed; it is written to
`renders/terrain-*.png`, which are not kept in git, so a plate's module asks for it as it is imported): gravel and sand shaded as a height field, dry beds, bushes, tracks, circles of
irrigated crop (one of them may lie fallow), villages, a concrete apron in slabs, a salt flat cracked into plates, soft sand, gravel strewn with stones, a wall of billowing dust, and
`piece()` cuts any of these to a shape: a framed tile of a figure, a hill given a dome so that the light finds slopes on it, a dry river bed between its banks. `figs/h_plan.py` is what such
a figure takes from the kit: `layer()` puts the terrain under the old drawing and gives its flat grey, pale and tinted rectangles a surface (asphalt with a shoulder and edge lines, a
tarred road, a taxiway, a slab of concrete, a crop, a ploughed plot, gravel, a flat roof), `panel()` makes a card with a sky for the side view that shares the canvas, and `path_points()`
samples a curve of the old drawing to cut a picture to it; `reskin.py`'s `"halo"` puts a white casing under every line and word of the old drawing so that it can be read on the picture.
The ground is soft on purpose: the book takes a JPEG of 800 kB at most, and fine grain costs most.

The helper modules `figs/h_a1.py` to `h_a4.py` hold what four parallel passes over the remaining figures needed and shared with nobody: scene cards with a runway edge-on, windsocks, masts, hangars, a tower, a heavy aeroplane and glass blocks (`h_a1`); aerodrome pictures, worn runway paint, taxiway signs, lamps and PAPI beams, the marshaller (`h_a2`); night terrain cards, glass canals, windscreen views (`h_a3`); globes, instrument cards, ribbons and rulers for the chart-work and navigation figures (`h_a4`). They are plain Python, not plate modules, and the terrain pictures they ask for are made when a module is imported (they are not kept in git).

`to_book.py <book checkout>` puts the finished plates of `out/book/` into the book's `handbook/ppl/figures/`, points both editions' chapters at
them and removes the figures they replace; then the book's own `build_handbook.py --swap` and `build_review_packet.py`. The raw renders
(`renders/`) and the web SVGs (`out/<id>.svg`) of these plates are **not kept in git** (they are large): `npm run plates:render` makes them
again, and `build_plates.py` skips a plate whose render is missing (a re-skinned plate waits only for the pictures of the aeroplane it lays on its drawing,
and the message names the ones missing; a plate named on the command line is built or fails).

## Real Saudi data (chapters 17, 18, 20 and 26)

Nine of the book's figures show real places and real airspace instead of invented ones: 17-1 (the airspace blocks between Thumamah and Riyadh in a vertical section), 17-7 (the air traffic services along a flight from Riyadh to Thumamah), 17-8 and 17-9 (the worked example, a local flight from Thumamah, in plan and in profile), 18-1 (the plan of Thumamah), 18-3 (naming a runway: Thumamah, and the three parallel runways of Jeddah), 18-7 and 26-1 (the circuit of Thumamah) and 18-9 (relabelled: runway 35 at Thumamah). Two more are new to the book, which had no such figures: 18-8, the AIP's local procedures at Thumamah on a satellite picture (below), and 18-2, the declared distances of Thumamah's runway (the AIP's AD 2.13: `TORA`, `TODA`, `ASDA` and `LDA` as bars to scale over the plan; a plate with no old drawing has a re-skin without an `svg`, and its `replaces` only keeps the rule that it starts with the id). When a figure is added in the middle of a chapter the later ones are renumbered in both repositories: module names, ids, `replaces`, the old drawings in `old/` and the book files all follow the book's current numbers. They draw from two data files that scripts in `data/` build:

- `data/saudi_airspace.json` (`build_saudi_facts.py`, from a checkout of the `saudi-airspace` repository, default `/workspace/saudi-airspace`): the AIP's values (AIRAC AIP AMDT 11/26, effective 2026-10-29) for Thumamah, Riyadh, Jeddah and Red Sea, the polygons of the airspace blocks and of the special use areas, and the numbers derived from them, marked `_derived` (distances, bearings, magnetic directions, the legs of the worked example). Before it was used, every value of AD 2 OETH was compared with the official page (54 values, all found verbatim) and the runway thresholds of Jeddah and Red Sea with theirs.
- `data/oeth_plan.json` (`build_oeth_plan.py`): the outlines of Thumamah in the runway frame, **from open data only**. The runway, its stopways and its thresholds are the AIP's. The pavements, the sand islands, the roofs and the road are derived from open satellite imagery: the median of 14 cloud-free Copernicus Sentinel-2 L2A scenes (10 m pixels, tile 38RPN, 30 June to 15 November 2026), which `data/open/fetch_oeth_open.py` fetches from the open archive and keeps as `data/open/oeth_s2_composite.npz`. A cell is pavement where its colour is neutral and the desert is red; the outline is vectorised, simplified and squared to the runway's axes. The imagery sits on the AIP's runway to within about a metre across it (`provenance.check` in the file), and the outlines are good to about 10 m, one pixel. `data/open/oeth_plan_check.png` shows them over the composite. **Every use carries the attribution "Contains modified Copernicus Sentinel data 2026".** OpenStreetMap (ODbL) was fetched too (`data/open/oeth_osm_check.json`) and is only compared with: it agrees on the main apron, the main hangar and the links it has, but dates from 2011 and lacks the south apron, so none of its geometry is in the plan or in the pictures. Until November 2026 the outlines were traced from Esri World Imagery; the owner asked for open sources, and nothing of that tracing remains.

- `data/open/riyadh_terrain.npz` (`data/open/fetch_terrain_open.py`) and `figs/terrain_real.py`: the real ground. Open elevation data (NASA SRTM, public domain, thinned to about 60 m) gives the ground line of the two sections (17-1 along the line from Thumamah to Riyadh, 17-9 under the three legs of the worked example, level at the aerodrome elevation along the runways) and the shaded relief under the map of 17-8. The floors that the AIP gives as 700 ft above the ground follow that ground. In 17-9 two small figures give the highest ground under the route (about 2 630 ft on the way out, 2 520 ft on the way back). The survey agrees with the AIP's elevations at Thumamah to within about 15 ft.

- `data/open/oeth_area_s2.jpg` (`data/open/fetch_oeth_area_open.py`), `figs/imagery_real.py` and `data/oeth_area.json` (`data/build_oeth_area.py`): a real picture of the country. Figure 18-8 lays the departures, the arrivals and the two circuits of AD 2.22 over an open satellite picture, the median of three Sentinel-2 scenes at 10 m (25.8 km by 17.7 km), taken point by point into the map's own flat projection with true north up. The highway west of the aerodrome is traced on the same picture as its darkest line, so that the figure can draw it as a road. The heights and the names are the AIP's; the tracks are a reading of its words (where the turns are made, a downwind leg 1 NM from the runway and so west of the fenced ground that the picture shows where AD 2.21 puts the wildlife reserve, the highway along the dunes as the "Thumamah highway"): the figure's note says so, and the book's open item OI-032 asks someone who flies there to check it. **Every use carries the attribution "Contains modified Copernicus Sentinel data 2026".**

- `data/open/oers_area_s2.jpg` (`data/open/fetch_oers_area_open.py`) and the `oers` part of `data/saudi_airspace.json`: one airspace at two times of day. Figure 17-2 (new: the book said it in words only) draws the control zone of Red Sea International twice on an open satellite picture of the coast: in the hours of its tower (07:00 to 15:00, Class D, Red Sea Tower on 118.200 MHz) and for the rest of the day (the same outline as an ATZ of Class G, with the TIBA broadcasts on 122.8 MHz inside it as well as outside), with the seven reporting points of AD 2.22.12 and the runway, all at the AIP's printed positions. The picture is the median of twelve cloud-free Sentinel-2 scenes from two tiles of one grid (52 km square, 20 m to the pixel); `figs/imagery_real.py` now serves more than one picture and UTM zone. Chapter 17's later figures move up by one (17-3 to 17-9).
- `data/open/arabia_relief.jpg`, `globe_relief.jpg` and their land masks (`data/open/fetch_arabia_open.py`), `figs/arabia_real.py`, and the `charts` part of `data/saudi_airspace.json`: the projection of the AIP's own charts. Figure 20-2 (new: the book's section on chart projections had no figure) draws the cone of the Lambert conformal conic twice, to scale: as glass on a globe, with the two standard parallels where glass and globe meet, and laid flat as a chart of the peninsula with the 45 sheets of the AIP's 1:500 000 series, the sheet of Riyadh and Thumamah (2546-C) and a straight line from Jeddah to Riyadh whose direction is read at three meridians. The standard parallels are the ones printed in the margin of every sheet, 25°20' and 30°40' (AIP GEN 3.2.4.2 says they are "indicated on chart"); `data/check_chart_cone.py` measured the convergence of the meridians on six sheets and found the constant of that cone (0.464 to 0.473 against 0.4696; `data/chart_cone_check.json`). The same check shows that the six sheets differ in scale by up to 0.8 % in a way the cone alone does not explain, so neither the figure nor the book says how the scale of the printed sheets varies. The relief and the land are Natural Earth's (public domain); **no boundary between countries is drawn**, only coasts and the outline of the AIP's sheets. The numbers in the figure (063°, 065°, 067°) are worked out by the module from the cone and asserted against the legend. Chapter 20's later figures move up by one (20-3 to 20-9).

The legends of these figures are the ones in the book's chapters (not the old figures' lists), and the pictures say "not for navigation". The book's `docs/saudi-examples.md` records the sources, what was compared and the open items.

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
npm run plates:render:clouds   # the clouds in Blender (no model), about two hours in all      -> handbook/renders/cloud-<kind>.png
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
