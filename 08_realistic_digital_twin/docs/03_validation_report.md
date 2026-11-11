# Phase 8 — Validation report

Date: 2026-11-06; sections 1–4 updated 2026-11-10 after the outline of the airframe was corrected
against the handbook drawings (see [05_shape_reference.md](05_shape_reference.md)) and the model was
taken under the skin (see [07_under_the_skin.md](07_under_the_skin.md)); section 1 updated 2026-11-11
after the paint, the markings, the cabin trim and the propeller were redone
(see [11_paint_and_look.md](11_paint_and_look.md)) and the instrument panel was laid out again after the
handbook's figure (see [12_cockpit.md](12_cockpit.md)). Environment: Linux x64 container, 4 CPU, no
GPU (Blender Cycles on CPU; browser tests on Chromium with SwiftShader software WebGL). Real-GPU
numbers must be measured on target devices.

## 1. Build and model

| Level | Objects | Triangles | GLB size | Build time | Subdivision | Textures |
|---|---|---|---|---|---|---|
| high | 951 | 558 716 | 9.1 MB | 65–80 s | 2 | 2048 px (paint of the fuselage 4096 px) |
| medium | 369 | 243 890 | 5.6 MB | 20–23 s | 1 | 1024 px (paint of the fuselage 2048 px) |
| low | 369 | 146 952 | 5.2 MB | 20–23 s (incl. decimation) | 1 + decimate 0.5, the painted skins and the propeller left whole | as medium |

The high level carries detail level 1 (structure, control runs, systems, the insides of the engine
and of the instruments, cabin air and lights, seat, door and baggage fittings, the avionics installation: 582 parts under the skin);
medium and low are the basic model of 369 parts. The editable scene also holds detail level 2
(fasteners, the hardware kit and ground equipment, 247 parts), which is in no web model: 1 198 parts in all, listed in
`models/parts_all.json` and [06_parts_index.md](06_parts_index.md).

All three are inside the budgets set in `02_modeling_architecture.md` (25 / 12 / 6 MB,
600 k / 250 k / 150 k triangles). The low level grew on 2026-11-11 (it was 2.1 MB, 97 k triangles): it now
shares the 1024 px textures of the medium level, because at 512 px the stripes and the cabin trim were a
blur on a telephone, and it keeps every face of the painted skins and of the propeller, because a stripe
wavers across faces that have been thinned out. Editable source `models/C172N_realistic.blend`: 3.6 MB
(compressed, modifiers live, cutters in a hidden collection, textures relative).

`scripts/validate_glb.py` — all levels **OK**: glTF 2.0 binary, Draco required, every primitive has
NORMAL + TEXCOORD_0 and a PBR material (51 materials in the high level, 39 images), every mesh node carries
`system`, `label_en`, `label_ar`, `status ∈ {measured, poh, type_data, estimated}` extras.

Determinism: two consecutive builds produced identical object lists, triangle counts and file
sizes (`scripts/compare_builds.py`), which is what the CI `blender-rebuild` job checks.

Spatial regression: `blender/validate_geometry.py` measures the built scene and rejects

- non-finite or newly degenerate mesh data (existing generator debt is capped at 56 degenerate
  faces per crankcase half, so it cannot silently increase) and aircraft-envelope violations;
- a built dimension that differs from the published one: wing span over the tips and over the strobe
  lights, length, wheel base, track, tail span, tyres on the ground, and the maximum height together
  with the propeller clearance, which the POH gives for the nose gear depressed (table in section 2);
- a strut, fairing, gear leg, step, fin, stabiliser, cowl half, door, baggage door or wing that
  neither intersects its neighbour nor comes within 1–3 cm of it (19 attachments);
- any of the 431 parts in the fuselage and cowl (engine, panel, cabin, structure, control runs,
  pipes, wiring) that reaches more than 3 mm outside the skin, tested against the section tables the
  skin is lofted from, and any of the 155 parts in the wings that leaves the wing section. Every
  detail level is checked, the fasteners included.

The last check exists because the first corrected build had rudder pedals, harness anchors and
engine baffles showing through the new, lower fuselage; it found all of them.

Visual regression: the rebuild job renders the front-quarter, landing-gear detail, and top views
at 800 × 450 and 16 samples, then compares luminance, RGB RMS, and edge differences against the
committed reference renders. Failure diffs are uploaded as a CI artifact.

## 2. Proportion checks

Published dimensions, measured on the built scene by `validate_geometry.py` (not read back from
the constants the model was built with):

| Quantity | Published | Built model | Tolerance |
|---|---|---|---|
| Wing span with strobe lights installed | 36 ft = 10.973 m (POH Fig 1-1, note 1) | 10.973 m | 2 cm |
| Wing span over the tips | 35 ft 10 in = 10.922 m (type data) | 10.922 m | 2 cm |
| Length, spinner tip to rudder, aircraft on its wheels | 26 ft 11 in = 8.204 m (POH Fig 1-1) | 8.202 m | 3 cm |
| Wheel base | 65 in = 1.651 m | 1.653 m | 1 cm |
| Main wheel track | 8 ft 4½ in = 2.553 m (POH Fig 1-1) | 2.553 m | 1 cm |
| Span of the horizontal tail | 11 ft 4 in = 3.454 m | 3.454 m | 2 cm |
| Maximum height, nose gear depressed until the propeller clears the ground by 11¾ in | 8 ft 9½ in = 2.680 m (POH Fig 1-1, note 2) | 2.651 m | 3 cm |
| Propeller diameter | 75 in = 1.905 m (POH 1-3) | 1.905 m | unit test |
| Wing area | 174 ft² (type data) | 174.5 ft² from the planform | unit test (±4 ft²) |

Height and propeller clearance: the POH gives both for the nose gear depressed. At rest the model's
propeller clears the ground by 16.9 in and the beacon is 93.7 in high; pushing the nose wheel 3.6 in
down, which a strut and a tyre can give, brings the clearance to the published 11¾ in and the height
to 2.651 m, 2.9 cm under the published maximum. The validator and a unit test hold the two together.

Span: the POH figure of 36 ft is the span "with strobe lights installed"; the type data's 35 ft 10 in
is the span over the wing tips. The model reproduces both.

Outline: the side, top and front views of the model, drawn to scale by `blender/threeview.py`, are
laid over the manufacturer's three-view drawing and the cabin figures of the handbook. Fuselage,
cabin openings, wing planform and tail agree within about an inch in the side and top views. Method,
readings and what remains uncertain (the nose and wheel fairings of this model year, cross-sections,
the pitch of the fuselage reference line) are in [05_shape_reference.md](05_shape_reference.md). The
geometry status remains **estimated**: it follows the type's drawings, not a survey of the FlyGACA
aircraft.

## 3. Automated tests

| Suite | Result |
|---|---|
| `tests/test_profiles.py` (airfoil, superellipse, resampling, shape-preserving interpolation, units, stance, sheet-metal geometry) | 20 / 20 pass |
| `tests/kinematics.test.mjs` (GLB ↔ kinematics ↔ POH plug map ↔ labels) | 8 / 8 pass |
| `tests/sim.test.mjs`, `tests/scenarios.test.mjs` (Phase 7 behaviour, re-run on the Phase 8 copies) | 35 / 35 pass |
| Phase 7 suites (`07_kinematic_twin/tests`) | unchanged, 41 / 41 pass |
| `scripts/validate_glb.py` | 3 / 3 levels OK |
| `blender/validate_geometry.py` | 14 critical objects, 19 attachments, 7 published dimensions, 609 parts inside the fuselage skin, 157 inside the wing skin, 75 runs (pipes, hoses, ducts, cables, wires) clear of every other part |
| `scripts/quality_gate.py` | catalogue, provenance, instruments, LOD indexes, parts list (1 198 parts, bilingual, status, POH page), parts index up to date |
| `09_book_figures/tests/test_ink.py` (ink-line rules, camera framing) | 12 / 12 pass |
| `scripts/compare_renders.py` | 3 canonical render views within perceptual thresholds |

## 4. Browser test (`tests/e2e.mjs`, Playwright Chromium + SwiftShader)

Final run: **12 / 12 checks passed** (`?test=1` disables the GTAO pass; everything else as shipped).

| Check | Result |
|---|---|
| high level loads: 10 system groups, 951 parts, no console errors | ok |
| doors open, flaps 40°, aileron input moves the surfaces | ok |
| the parts tree lists the systems; isolating one (fuel) draws only its parts, wherever they are | ok |
| part selection shows bilingual info and the status badge (propeller → POH) | ok |
| confidence overlay colours the parts by provenance and restores the materials | ok |
| exploded assembly animation displaces parts from their system centres | ok |
| engine mode removes the upper cowl; start from the cockpit controls (BAT/ALT, prime, throttle, BOTH, START) → engine runs, crank turns, piston 1 on the right bank, 2 on the left | ok |
| cockpit mode: camera at the pilot's eye, tachometer needle follows the simulation | ok |
| run-up scenario starts and evaluates steps live | ok |
| Arabic RTL default | ok |
| phone width (Pixel 5 emulation) picks the low level, no horizontal overflow, console clean | ok |
| medium level loads, console clean | ok |

Measured in the container (software WebGL, so load times and frame rates are not representative
of a real GPU; draw calls and triangles are device-independent):

| Level | Load to interactive | Draw calls | Triangles per frame (incl. shadow pass) |
|---|---|---|---|
| high | 4.9 s | 1 872 | 1 012 776 |
| medium | 1.8 s | 710 | 386 320 |
| low | 1.8 s | 705 | 192 722 |

Draw calls are dominated by part count (951 selectable objects in the high level); the next optimisation step would
be merging static exterior parts into fewer meshes for the low level while keeping the part
index for selection.

Screenshots from the run are uploaded as the `e2e-screenshots` artifact in CI
(`npm run test:e2e8` with `E2E_SHOTS=dir` locally).

## 4b. Gallery renders

`docs/gallery.html` presents seven transparent print-size views plus two exploded-assembly
views (`docs/gallery/*.png`, 1800 × 1000, Cycles 96 samples, shadow catcher, soft fill), with
live EN/AR captions. Before/after images of the same camera on the Phase 7 and Phase 8 models
are in `docs/renders/phase7_*.png` and `phase8_*.png`.

`npm run render8` and `npm run gallery8` regenerate both sets. Two faults in the earlier sets are
fixed: the upper cowl was hidden in every gallery view and in the front-quarter reference image
(only the engine views leave it off now), and the apron material was not saved with the scene, so
the aircraft stood on a blank white floor.

## 5. Known limitations (technical)

- **Software WebGL in CI** renders the high level at ~1 frame/s; the `?test=1` flag therefore
  disables the GTAO pass so screenshots complete. On a real GPU the high level with AO is the
  intended desktop experience; medium/low disable AO by default.
- **Glass** is alpha-blended (no refraction) for broad device support; instrument glass uses the
  same approach.
- **Rivets and seams** are normal-mapped, not modelled; close-ups beyond ~0.3 m show the texture.
- **Cockpit camera** is an orbit camera parked at the pilot's eye, not a true first-person walk.
- **Explode** moves direct children of each system group; sub-parts (needles, door windows) stay
  attached to their parent, which is the intended behaviour for an assembly animation.
- **Engine accessories** are placed from the POH system descriptions, not from the IPC; the
  O-320-H2AD-specific accessory case layout is representative.
- **No flight dynamics**: control inputs move the surfaces and yokes; the airframe does not fly.
