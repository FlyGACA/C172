# Phase 8 — Validation report

Date: 2026-11-06; sections 1–4 updated 2026-11-10 after the outline of the airframe was corrected
(see [05_shape_reference.md](05_shape_reference.md)). Environment: Linux x64 container, 4 CPU, no
GPU (Blender Cycles on CPU; browser tests on Chromium with SwiftShader software WebGL). Real-GPU
numbers must be measured on target devices.

## 1. Build and model

| Level | Objects | Triangles | GLB size | Build time | Subdivision | Textures |
|---|---|---|---|---|---|---|
| high | 337 | 355 948 | 4.6 MB | 26–28 s | 2 | 2048 px |
| medium | 337 | 186 566 | 3.3 MB | 12–13 s | 1 | 1024 px |
| low | 337 | 93 589 | 2.1 MB | 13–14 s (incl. decimation) | 1 + decimate 0.5 | 512 px |

All three are far inside the budgets set in `02_modeling_architecture.md` (25 / 12 / 5 MB,
600 k / 250 k / 100 k triangles). Editable source `models/C172N_realistic.blend`: 1.1 MB
(compressed, modifiers live, cutters in a hidden collection, textures relative).

`scripts/validate_glb.py` — all levels **OK**: glTF 2.0 binary, Draco required, every primitive has
NORMAL + TEXCOORD_0 and a PBR material (39 materials, 23 images), every mesh node carries
`system`, `label_en`, `label_ar`, `status ∈ {measured, poh, type_data, estimated}` extras.

Determinism: two consecutive builds produced identical object lists, triangle counts and file
sizes (`scripts/compare_builds.py`), which is what the CI `blender-rebuild` job checks.

Spatial regression: `blender/validate_geometry.py` measures the built scene and rejects

- non-finite or newly degenerate mesh data (existing generator debt is capped at 56 degenerate
  faces per crankcase half, so it cannot silently increase) and aircraft-envelope violations;
- a built dimension that differs from the published one: wing span, length, wheel base, track,
  propeller ground clearance, tail span, tyres on the ground (table in section 2);
- a strut, fairing, gear leg, step, fin, stabiliser or cowl half that neither intersects its
  neighbour nor comes within 2–3 cm of it (14 attachments), and downward wing-root-fairing normals;
- any of the 255 parts of the engine, panel and cabin that reaches more than 3 mm outside the skin,
  tested against the section tables the skin is lofted from.

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
| Wing span over the tips (lights excluded) | 35 ft 10 in = 10.922 m | 10.922 m | 2 cm |
| Length, spinner tip to rudder | 26 ft 11 in = 8.204 m (POH Fig 1-1) | 8.203 m | 3 cm |
| Wheel base | 65 in = 1.651 m | 1.651 m | 1 cm |
| Gear track | 8 ft 3½ in = 2.527 m | 2.527 m | 1 cm |
| Propeller ground clearance | 11¾ in = 0.298 m | 0.298 m | 1.5 cm |
| Span of the horizontal tail | 11 ft 4 in = 3.454 m | 3.454 m | 2 cm |
| Propeller diameter | 75 in = 1.905 m (POH 1-3) | 1.905 m | unit test |
| Wing area | 174 ft² (type data) | 174.5 ft² from the planform | unit test (±4 ft²) |

Height: the POH gives 8 ft 9½ in as the maximum, with the nose gear depressed. At rest the top of
the beacon is 96.5 in (2.45 m) above the ground in the reference photograph, and that is what the
model reproduces.

One inconsistency in the repository's own data is left for the POH check: `units.py` carries the
span as 35 ft 10 in "Fig 1-1", while `data/poh_references.json` records "span 36 ft" from the same
figure. The model measures 10.92 m over the wing tips and 11.00 m (36 ft 1 in) over the navigation
lights, so the two figures may simply be the span without and with the tip lights.

Outline: the side elevation follows a photograph of a Cessna 172 taken almost exactly side-on and
scaled by the POH length. The model's silhouette, rendered from the direction of the photograph,
overlaps it by 0.90 (0.78 for the first Phase 8 model); the remaining difference is the wings and
wheels of an aircraft in flight. Method, readings and limits are in
[05_shape_reference.md](05_shape_reference.md). Cross-sections, the nose cap and the wheel fairings
come from two further photographs read by eye. The geometry status therefore remains
**estimated**: it follows the type, not a survey of the FlyGACA aircraft.

## 3. Automated tests

| Suite | Result |
|---|---|
| `tests/test_profiles.py` (airfoil, superellipse, resampling, shape-preserving interpolation, units, stance) | 13 / 13 pass |
| `tests/kinematics.test.mjs` (GLB ↔ kinematics ↔ POH plug map ↔ labels) | 8 / 8 pass |
| `tests/sim.test.mjs`, `tests/scenarios.test.mjs` (Phase 7 behaviour, re-run on the Phase 8 copies) | 35 / 35 pass |
| Phase 7 suites (`07_kinematic_twin/tests`) | unchanged, 41 / 41 pass |
| `scripts/validate_glb.py` | 3 / 3 levels OK |
| `blender/validate_geometry.py` | 11 critical objects, 14 attachments, 6 published dimensions, 255 interior parts inside the skin, fairing normals OK |
| `scripts/compare_renders.py` | 3 canonical render views within perceptual thresholds |

## 4. Browser test (`tests/e2e.mjs`, Playwright Chromium + SwiftShader)

Final run: **10 / 10 checks passed** (`?test=1` disables the GTAO pass; everything else as shipped).

| Check | Result |
|---|---|
| high level loads: 10 system groups, 337 parts, no console errors | ok |
| doors open, flaps 30°, aileron input moves the surfaces | ok |
| part selection shows bilingual info and the status badge (propeller → POH) | ok |
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
| high | 4.6 s | 690 | 621 576 |
| medium | 1.8 s | 687 | 342 028 |
| low | 1.7 s | 681 | 171 468 |

Draw calls are dominated by part count (331 selectable objects); the next optimisation step would
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
