# Book figures — the plan

Written 2026-11-10 against this repository at Phase 8. Four sample figures made the way this plan
recommends are in [`out/preview/`](out/preview/); how they are built is in [`README.md`](README.md).

**Update, same day.** The first three-quarter illustration drawn from the model showed the problem
described below too plainly: it did not look like a Cessna 172. The shape of the model has since
been corrected against photographs of the type and the illustration renderer rewritten; sample
[S-4](out/preview/aircraft-exterior.en.png) is the result. The sections below say what was wrong,
what was done, and what still depends on photographs and measurements of your own aircraft.

## The recommendation

Stop trying to make one generated 3D aircraft look like a photograph. Use three kinds of picture,
each for the job it does best, all in one visual style:

1. **Photographs of the real aircraft** wherever the reader has to *recognise* something on the ramp
   or in the cockpit.
2. **Vector diagrams built from this repository's data** wherever the reader has to *understand* how
   something works, or read an instrument.
3. **The 3D twin drawn as technical illustration** — flat tones, ink outlines, the subject tinted and
   labelled — for the views no camera can take: cutaways, exploded views, systems seen through the skin.

The twin keeps its place, but as an illustration engine. It does not have to pass for a photograph;
it has to be *recognisably a 172*, which is a much smaller problem (see "Source 3").

## Why the generated Cessna did not look right

It was a shape problem, not a rendering problem.

- The model builder was given four real dimensions: span, length, height and propeller diameter
  (POH Figure 1-1). Every other number — fuselage sections, fin, cowl, windows, fairings — had the
  status `estimated` in [`units.py`](../08_realistic_digital_twin/blender/c172/units.py) and was typed
  by hand into tables such as `FUS_TABLE` and `COWL_TABLE`.
- Each phase improved the technique: primitives, then a kinematic model, then Blender surfaces with
  textures and sky lighting. None added shape information. Better rendering of an estimated shape
  gives a sharper picture of a generic high-wing aircraft, and pilots know this outline by heart.
- A photoreal look is the least forgiving target there is. Every missing rivet line, reflection or
  placard reads as "fake".

What a pilot noticed first, and what was done about it:

| In the first model | On the aircraft | Now |
|---|---|---|
| Stood far too high: 17.6 in under the propeller, belly 31 in above the ground | 11¾ in propeller clearance, belly about 17 in up | Corrected (published clearance; photo-profile) |
| Rudder trailing edge vertical, fin upright with a kinked fillet | 45° swept fin on a long, low dorsal fin; raked rudder | Corrected (photo-profile) |
| Tail 29 in too far aft | — | Corrected (photo-profile) |
| Side windows 22 in tall, flat windshield between thick pillars, small rear window in the roof | 13 in windows, a windshield that wraps round to thin door posts, a rear window over the whole back of the cabin | Corrected (photo-profile, ramp photograph) |
| Wheel fairings large half-discs | Slim teardrops (and many trainers fly without them) | Corrected (ramp photograph) |
| Short nose, rectangular light off centre | Longer cowl; one round landing light and the carburettor air inlet on the centreline of the nose cap | Corrected (photo-profile, ramp photograph, POH 7-27) |

How the outline was measured, the readings, and how far they can be trusted are in
[`docs/05_shape_reference.md`](../08_realistic_digital_twin/docs/05_shape_reference.md). In short:
one photograph of a Cessna 172 taken almost exactly side-on, scaled by the POH length, gives the
side elevation; the model's silhouette now overlaps it by 0.90 (0.78 before). Widths and details
come from two more photographs and are less certain. The status of the shape stays `estimated`:
it follows *a* 172, not yet *your* 172.

Two things also made the published pictures look worse than the model was. Both are fixed:

- **The engine cowl was missing from the first picture people see.** The gallery command hid the
  upper cowl for every view, and the image at the top of the root README showed the engine blocks
  exposed. Only the engine views leave the cowl off now.
- **A white aircraft stood on a white floor.** The apron material was not saved with the scene, so
  the renders had no ground to give contrast. It is now.

## The principle: realism for recognition, clarity for understanding

A figure has a job. If the job is "know it when you see it", the best picture is the real thing.
If the job is "understand how it works", detail gets in the way.

- Richard Mayer's multimedia-learning research gives three rules that apply directly: leave out
  material that is not needed (coherence), mark what matters (signalling), and put the words next to
  the thing they describe (spatial contiguity). *Multimedia Learning*, Cambridge University Press.
- Francis Dwyer's experiments compared line drawings, shaded drawings and photographs of the same
  subject. More realism did not reliably give more learning; it helped mainly when the test was to
  recognise the real object. A 2021 review in *Educational Psychology Review* reaches the same
  conclusion (doi:10.1007/s10648-021-09638-1).
- The handbooks pilots already trust work this way. The POH explains every system with a line
  schematic. The FAA handbooks pair photographs (what it looks like) with drawings (how it works).

## The right picture for each job

| The reader has to… | Typical figures | Best source | Why |
|---|---|---|---|
| Recognise it on the aircraft | Walk-around items, drains, pitot tube, static port, oil door, cockpit layout, controls | Photograph, labelled | Only a photograph is fully real, and it is *your* aircraft |
| Name the parts | Exterior, landing gear, control surfaces, panel | Photograph, or 3D illustration with labels | One clean angle, no background clutter |
| Find what is hidden | Tanks and fuel lines, battery, vacuum pump, pitot and static lines | 3D illustration, skin ghosted | Cannot be photographed |
| Understand how it works | Fuel, electrical, ignition, induction, oil, vacuum, pitot-static, brakes | Vector schematic | Symbols and flow beat detail |
| Read the instrument | Airspeed arcs, tachometer arcs, altimeter, engine gauges | Vector, drawn from `instruments.json` | Exact markings, any needle position |
| See inside | Four-stroke cycle, valve train, carburettor | 3D cutaway paired with a schematic | The twin's kinematics are already correct |
| Follow a procedure | Starting, run-up, emergencies | Panel photograph with a numbered flow | Order matters, not detail |
| Fly it | Forces, stalls, traffic pattern, crosswind | Vector diagram with a simple aircraft symbol | Standard textbook practice |
| Use the numbers | Performance, weight and balance | Vector chart from POH data | It is data |

## Source 1 — photographs

One well-prepared day with the aircraft gives the book all of its realism.

- **Light.** Open shade, overcast, or the first hour after sunrise. Midday sun burns out white paint.
  A polarising filter removes glare from windows and instrument glass.
- **Consistency.** One lens and one height for each series, a tripod in the cockpit, a clean aircraft,
  nothing on the apron behind it. Shoot more than you need.
- **Exterior.** Each walk-around station in order, then the details a student is asked to check: fuel
  caps and sump drains, strainer drain, pitot tube, stall-warning opening, static port, oil filler
  door and dipstick, air inlets, propeller and spinner, nose strut, tyres and brakes, hinges, trim tab,
  tie-downs, baggage door.
- **Cockpit.** The whole panel square-on (for a labelled figure), then each group: flight instruments,
  engine gauges, switches and breakers, engine controls, fuel selector, flap lever, trim wheel,
  ignition switch, parking brake, alternate static valve.
- **Permission.** Get the operator's and the airport's agreement before shooting airside, and written
  consent from anyone who appears.
- **On the same day, shoot the reference set for the 3D twin** (see Source 3). It costs an extra hour.

Labels are added by the same build that makes the other figures, so photographs match the diagrams.

## Source 2 — vector diagrams from data

This is where the repository is already strong, and where most of the book's figures can come from.

- `data/instruments.json` holds every dial scale and limit with its POH page; `shared/js/sim.js` holds
  the POH constants; `data/poh_references.json` and `data/parts_catalog.json` hold the cited facts and
  the bilingual names. A figure drawn from these cannot disagree with the simulator.
- Vector art is sharp at any print size, small in the repository, and is built in English and Arabic
  from the same source.
- Samples: [S-1 airspeed indicator](out/preview/asi-markings.en.png),
  [S-2 fuel system](out/preview/fuel-system.en.png).

Next in line, in order of value: tachometer, altimeter and engine-gauge figures (the data exists);
then the electrical, ignition, induction and carburettor-ice, oil, vacuum, pitot-static and brake
schematics; then weight-and-balance and performance charts.

## Source 3 — the 3D twin as an illustration engine

**What it is for.** Views a camera cannot take, and any view that has to be repeated exactly: systems
ghosted inside the airframe, cutaways, exploded assemblies, the engine's moving parts, the same
aircraft from a fixed angle with different parts highlighted.

**How it is drawn.** Soft neutral tones, ink outlines, colour only on the subject, labels placed by
code from the model's own part names. Samples: [S-3 flight controls](out/preview/flight-controls.en.png)
(plan view) and [S-4 major components](out/preview/aircraft-exterior.en.png) (three-quarter view).

The outlines are not traced and not left to a stroke renderer. For every pixel the renderer knows
exactly which part is there, how far away it is and which way the surface faces; a heavy line is
drawn round the aircraft, a medium line wherever two parts meet, and a fine line at folds. The same
model therefore always gives the same clean drawing, at any angle, with any parts tinted.

**What it rests on.** Line art puts the outline in front of the reader, so it is only as good as
the shape of the model. That shape now follows photographs of the type (see above). Three steps
turn "a 172" into "your 172", and none of them needs the builder to change:

1. *Capture reference from the real aircraft.* A side, front, rear and (from a ladder, mezzanine or
   drone) top photograph, each taken from as far away as possible with the longest lens available, the
   aircraft level, a tape or scale bar in the frame. A phone LiDAR or photogrammetry scan is a useful
   extra. Glossy white paint and glass scan badly, so treat a scan as a shape reference accurate to a
   few centimetres, not as a finished model.
2. *Check the model against it.* The overlay method of `docs/05_shape_reference.md` works with any
   square-on photograph. Widths, the cowl and the nose cap are the parts most likely to move, because
   they changed between model years and are the least well covered by the photographs used so far.
3. *Record it.* Enter the measurements through the existing workflow
   ([`docs/04_aircraft_measurements.md`](../08_realistic_digital_twin/docs/04_aircraft_measurements.md))
   so the affected parts move from `estimated` to `measured`.

Every 3D figure then improves by re-running the build; no label is placed again by hand.

**Faster alternatives, if time matters more than ownership.** License a professionally made C172 model
for book renders, or commission a 3D artist to model over your photographs. Check that a licence
covers print and e-book publication. Most marketplaces forbid passing the model file on, so a bought
model could not replace the open one in the web viewer.

## One visual language

- One typeface for both scripts (IBM Plex Sans Arabic). Labels 8.5 pt, notes 6.8 pt, nothing under 6 pt.
- Colour has fixed meanings. Blue is fuel. Green, yellow and red mean normal, caution and limit, as on
  the instruments, and are used for nothing else. Everything that is not the subject stays neutral.
- The aircraft is never mirrored for the Arabic edition. Text and tables change direction; left stays left.
- Words that are on the aircraft — placards, dial legends, switch names — stay in English as placarded.
  The explanation is translated.
- Labels sit next to the part with a leader line. Use a numbered key only when a figure has too many
  parts for that.
- 3D figures are never dressed up as photographs. Photographs are never retouched to change what the
  aircraft looks like.
- Units as in the POH (KIAS, US gallons, pounds, °F).

## How a figure is made and checked

1. It gets an entry in [`figures.json`](figures.json): what kind it is, how it is made, where each fact
   comes from (POH page), and its status.
2. `npm run figures` builds it in both languages: a PDF print master, an editable SVG, and a review
   sheet with the caption and status.
3. `npm test` checks that every string exists in both languages, that every cited POH key exists, and
   that figure values agree with the instrument data and the simulation constants.
4. It stays `draft` until an instructor has checked it against the aircraft's own POH and an Arabic
   reader has checked the Arabic. Then `reviewed`, then `approved` for print.

For print, keep the sources in RGB and convert to CMYK at the end with the printer's colour profile,
then proof one sheet before the run.

## Beyond the printed page

The same sources serve every reader, not only the print run.

- **Print, e-book and web from one build.** The PDF is the print master; the SVG and PNG go to the
  e-book and to FlyGACA.com unchanged.
- **Link the page to the interactive twin.** A short link or QR code beside a figure can open the
  viewer on the matching view, so a student reads the schematic and then operates the system. The
  viewer accepts only `?q=` and `?lang=` today; it needs deep links for mode, part and scenario first.
- **Colour is never the only code.** Line types differ in shape as well as colour and every arc is
  named in text, so the figures still work in black and white and for colour-blind readers.
- **Every figure carries its title as alternative text** for screen readers in the web and e-book editions.

## Order of work

1. Fix the book's figure list (the starter list below) and its format: trim size, colour, one language
   per edition or both on the page.
2. Photograph day, including the reference set for the twin.
3. Instrument figures and system schematics. These need nothing from the 3D model and are most of the
   figures.
4. Check the twin's shape against the photographs of your own aircraft (it now follows the type);
   then the ghosted, cutaway and further perspective figures.
5. Review rounds, then a print proof.

Steps 2 and 3 can start now and do not wait for each other.

## What to stop doing

- Chasing a photoreal look from the generated model.
- Using AI image generators for technical figures. They do not know this aircraft: they invent
  instrument faces, panel lines and strut geometry, cannot keep the aircraft the same from one figure
  to the next, and nothing in the result can be traced to the POH.
- Publishing renders of a white aircraft on a white floor, or with the cowl off unless the figure is
  about the engine.

## Decisions that are yours

1. Which aircraft is the book's reference, and can it be photographed? The measurement file names a
   profile `HZ-C172`, with serial number and installed equipment still unverified.
2. The book's format (trim size, colour, print and e-book, language layout).
3. For the twin: check it against your own reference photographs (recommended), license a model, or
   commission one.
4. Who reviews: an instructor for content, and a reader for the Arabic terminology.

## Starter figure list

Adapt it to the book's chapters. P = photograph, V = vector from data, S = vector schematic,
3D = illustration from the twin.

| Chapter | Figure | Source |
|---|---|---|
| The aircraft | Three-view with principal dimensions | V (POH numbers) + 3D outline |
| | Major components — **sample S-4** | 3D |
| | Exterior and its parts, as on the ramp | P |
| | Doors, windows, baggage door | P |
| Flight controls | Control surfaces — **sample S-3** | 3D |
| | Control wheel, pedals, trim wheel, flap lever | P |
| | Flap positions | V |
| Instrument panel | Whole panel, labelled | P |
| | Airspeed indicator markings — **sample S-1** | V |
| | Altimeter, vertical speed, attitude, heading, turn coordinator | V |
| | Tachometer and engine gauges | V |
| Powerplant | Engine with the cowl off, labelled | P |
| | Four-stroke cycle and valve train | 3D cutaway + S |
| | Ignition: dual magneto and plug map | S |
| | Induction, carburettor and carburettor ice | S |
| | Oil system | S |
| | Propeller | P + V |
| Fuel | Fuel system — **sample S-2** | S |
| | Where the tanks, lines, selector and strainer are | 3D ghosted |
| | Caps, drains, selector placard | P |
| Electrical | Electrical system and bus | S |
| | Ammeter and low-voltage light indications | V |
| Pitot-static and vacuum | Pitot-static system and alternate static source | S |
| | Vacuum system and its instruments | S |
| | Blocked pitot or static port: what the instruments show | V |
| Landing gear | Nose gear, main gear, brakes | P |
| | Brake system | S |
| Pre-flight | Walk-around route | V (plan view) |
| | One photograph per station | P |
| Limitations and performance | Speed ranges on the airspeed indicator | V |
| | Weight-and-balance envelope and loading stations | V |
| Procedures | Start, run-up and emergency flows on the panel | P with numbered flow |
