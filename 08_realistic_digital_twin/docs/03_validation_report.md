# Phase 8 — Validation report

Date: 2026-11-06. Environment: Linux x64 container, 4 CPU, no GPU (Blender Cycles on CPU; browser
tests on Chromium with SwiftShader software WebGL). Real-GPU numbers must be measured on target devices.

## 1. Build and model

| Level | Objects | Triangles | GLB size | Build time | Subdivision | Textures |
|---|---|---|---|---|---|---|
| high | 331 | 310 530 | 4.5 MB | 28–38 s | 2 | 2048 px |
| medium | 331 | 171 026 | 3.2 MB | 13–16 s | 1 | 1024 px |
| low | 331 | 85 818 | 2.0 MB | 17 s (incl. decimation) | 1 + decimate 0.5 | 512 px |

All three are far inside the budgets set in `02_modeling_architecture.md` (25 / 12 / 5 MB,
600 k / 250 k / 100 k triangles). Editable source `models/C172N_realistic.blend`: 1.1 MB
(compressed, modifiers live, cutters in a hidden collection, textures relative).

`scripts/validate_glb.py` — all levels **OK**: glTF 2.0 binary, Draco required, every primitive has
NORMAL + TEXCOORD_0 and a PBR material (37 materials, 23 images), every mesh node carries
`system`, `label_en`, `label_ar`, `status ∈ {poh, type_data, estimated}` extras.

Determinism: two consecutive builds produced identical object lists and triangle counts
(`scripts/compare_builds.py`), which is what the CI `blender-rebuild` job checks.

## 2. Proportion checks against the POH (Figure 1-1)

| Quantity | POH | Model (from `units.py`) | Check |
|---|---|---|---|
| Wingspan | 35 ft 10 in = 10.922 m | 10.922 m | unit test `test_poh_dimensions` |
| Length | 26 ft 11 in = 8.204 m | spinner tip to tail end 8.204 m | unit test |
| Height | 8 ft 9½ in = 2.680 m | fin tip 2.68 m + rudder horn 2.80 m (rudder horn is above the POH datum height; estimated) | visual |
| Propeller | 75 in = 1.905 m | 1.905 m | unit test |
| Wing area | 174 ft² (type data) | 174.5 ft² from the root/taper/tip planform | unit test `test_wing_area_from_planform` (±4 ft²) |
| Gear track | 8 ft 3½ in | 2.527 m | from `units.py` |

Visual comparison with the in-flight reference photographs (planform, strut position, tail shape,
window outlines) was done by eye on the Cycles renders in `docs/renders/`; no photogrammetric
fit was attempted — fuselage sections remain **estimated**.

## 3. Automated tests

| Suite | Result |
|---|---|
| `tests/test_profiles.py` (airfoil, superellipse, resampling, units) | 9 / 9 pass |
| `tests/kinematics.test.mjs` (GLB ↔ kinematics ↔ POH plug map ↔ labels) | 8 / 8 pass |
| `tests/sim.test.mjs`, `tests/scenarios.test.mjs` (Phase 7 behaviour, re-run on the Phase 8 copies) | 35 / 35 pass |
| Phase 7 suites (`07_kinematic_twin/tests`) | unchanged, 41 / 41 pass |
| `scripts/validate_glb.py` | 3 / 3 levels OK |

## 4. Browser test (`tests/e2e.mjs`, Playwright Chromium + SwiftShader)

Final run: **10 / 10 checks passed** (`?test=1` disables the GTAO pass; everything else as shipped).

| Check | Result |
|---|---|
| high level loads: 10 system groups, 331 parts, no console errors | ok |
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
