# Phase 8 — Repository audit, reference assessment and asset-gap report

Date: 2026-11-06. Scope: everything in `iflygaca/C172` at commit `9de688c` (Phases 01–07).

## 1. What exists and what can be reused

| Phase | Asset | Geometry quality | Verdict for Phase 8 |
|---|---|---|---|
| 01 | `Cessna172_Editable` (trimesh script + GLB) | primitives only | historical; not reused |
| 02 / 02b | `Cessna_172_Classic_Analog_V2.glb`, `FlyGACA_C172_Classic_Analog_Phase2.glb` (487 objects, 31 784 tris), Blender enhance script | box/cylinder primitives, no UVs, flat colours | historical; the Blender script was never run (its README says so) and only adds studio lights, not geometry |
| 03 | exploded engine GLB, instrument lab HTML | primitives | curriculum JSON (`curriculum_ar_en.json`) is reusable as lesson text |
| 04 / 04b | systems GLB, approximate airframe GLB, `poh_1979_reference_data.json` | primitives | **POH reference values reused** (page-referenced) |
| 05 | systems lab, `lessons.json`, `system_manifest.json` | primitives | lesson structure reusable |
| 06 | 224-part animated GLB | primitives baked in world space (no pivots) | not reused |
| 07 | deterministic numpy GLB (254 meshes), `js/sim.js`, `js/kinematics.js`, `js/scenarios.js`, `js/gauges.js`, `data/instruments.json`, `data/poh_references.json`, `data/parts_catalog.json`, tests, CI | schematic but correctly organised (pivots, Lycoming numbering, plug map) | **simulation, kinematics, scenarios, gauge data, instrument scales, POH references and the test approach are reused**; geometry is replaced |

Conclusion: the *logic* layer of the project (systems simulation, POH page references, scenario engine, bilingual strings) is mature enough to keep. The *visual* layer in every phase is primitive-based with flat colours, no UVs, no textures, no smooth surfaces, no window openings, no interior — a functional prototype, exactly as the master prompt describes it.

## 2. Reference material in the repository

Nine photographs are stored in `02_classic_analog_v2/reference_photos/` (duplicated in `02b`). Their provenance is **not recorded** in the repository (file names such as `AD3750_Original.jpeg` and `2023-07-19(…)_Original.jpeg` suggest they were collected from an image service rather than photographed by FlyGACA). They are used here **only as visual proportion references**; nothing is traced or reprojected from them, and they are not copied into Phase 8.

| File | Subject | Period-correct for a 1979 172N? | Useful for |
|---|---|---|---|
| `2023-07-19(1)` | 172 from below in flight | yes (airframe) | planform, strut and gear geometry, underside panel lines |
| `2023-07-19(23)` | **Cessna 140/170 tail-dragger (CF-YRT)** | **no** — different type | nothing |
| `2023-07-19(2502)` | **Cessna 210 Centurion** | **no** — different type | nothing |
| `2023-07-19(2505)` | 172SP (N3537B) in flight | airframe yes; cowl/spinner details are post-1996 | side proportions |
| `AD2722` | 172 (C-GBPT) in flight | yes | side/tail proportions |
| `AD3256`, `AD3286` | **1970s 172 panel (C-FZKL)** | **yes** — classic six-pack, ARC radio stack, wood-grain lower panel, red mixture knob, floor fuel selector | cockpit layout, control positions, placards |
| `AD3750` | 172 (OO-NZA) from below | yes | planform, tail planform |
| `AD4495` | **172SP panel (N243SP)** | **no** — 1990s panel with modern avionics | instrument face layouts only |

## 3. Dimensional reference status

Values used by the Phase 8 builder (`blender/c172/units.py`) carry one of three statuses:

- `poh` — taken from the 1979 Cessna 172N POH (page cited): span, length, height, prop diameter, fuel capacities, engine model, static RPM, instrument markings.
- `type_data` — widely published type data not in the POH (wing area 174 ft², NACA 2412/0012 airfoils, main gear track, tyre sizes, O-320 bore/stroke). To be confirmed against TCDS 3A12 / E-274 before any claim of accuracy.
- `estimated` — derived from photographs and general-arrangement proportions (fuselage cross-sections, window outlines, cowl inlet shape, panel dimensions). **Not manufacturer data.**

No Cessna drawings, Illustrated Parts Catalog, or Lycoming engineering drawings are available in this repository or this environment. Everything built from `estimated` values is therefore an educational representation, as the master prompt requires.

## 4. Asset gaps (what had to be created in Phase 8)

| Gap | Resolution in Phase 8 |
|---|---|
| No editable source model (.blend) in any phase | Blender 4.5 LTS scripted build; `.blend` saved by the build |
| No smooth surfaces / no subdivision topology | subdivision-surface cage meshes for fuselage, cowl, fairings; lofted airfoil wings |
| No window or door openings | exact boolean cut-outs; glass is the intersection of the shell with the same cutters so it follows the fuselage curvature |
| No UVs, no textures | deterministic UV projection + generated texture atlases (albedo, roughness/metal/AO, normal) |
| No rivets, seams, placards | rivet rows and panel seams painted into normal maps in UV space from parametric line lists |
| No interior | cabin liner, panel, instruments, controls, seats, belts, carpet |
| Flat-shaded engine | finned cylinders, crankcase, accessories, hoses, baffles, tubular mount |
| No LODs, no compression | high / medium / low GLBs with Draco, texture sizes per LOD |
| No environment lighting / shadows | procedural sky HDR (generated, original), PMREM environment, shadow-mapped sun, GTAO |
| Viewer never performance-tested | Playwright measurement of load time, draw calls, triangle count per LOD |

## 5. Intellectual-property position

- All geometry is generated by code in this repository; nothing is downloaded from, traced from, or derived from commercial model libraries.
- All textures are generated procedurally by `blender/c172/textures.py`; no third-party images are embedded.
- The livery is an original FlyGACA-style scheme, not a reproduction of a Cessna factory paint scheme.
- The reference photographs remain in the historical phases and are not redistributed in Phase 8.
- three.js is MIT-licensed and vendored with its licence file.
