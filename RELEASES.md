# C172 project history

01 — Editable airframe (initial procedural 3D model).
02 — Classic analog model, browser viewer, improved procedural geometry.
02b — Refined Phase 2 airframe with Blender enhancement script.
03 — Engine exploded-view training and analog instrument lab.
04 — C172N system component geometry and Arabic educational modules.
04b — Reference metadata from a manufacturer-authored 1979 C172N handbook; no engineering validation of geometry.
05 — Educational systems lab with basic fault scenarios.
06 — 224 separate 3D parts, animated educational components and interactive viewer.
07 — Kinematic twin (2026-11-06):
- New deterministic model builder (Python + numpy): every part on its own pivot, PBR materials, colour-coded system plumbing, 1:1 airframe envelope from POH Fig 1-1.
- Lycoming cylinder numbering and firing order 1-3-2-4; crank-driven pistons, rods, valves and camshaft; one dual magneto wired to the POH plug map.
- Documented systems simulation (engine/prop, mixture, carb heat and ice, magnetos, starter/priming/flooding, fuel, 28 V electrical, vacuum, ISA pitot-static) with POH-page references.
- 10 guided POH checklist scenarios with live step checking, 14-gauge panel, bilingual Arabic/English UI, offline three.js.
- 41 unit/scenario tests, Playwright browser test, GitHub Actions CI.
- Fixes Phase 6 issues: exploded view had no effect, cylinders 1 and 2 on the same side, two separate magnetos, missing airframe GLB, viewer never browser-tested.

08 — Realistic digital twin (2026-11-06):
- Model built in Blender 4.5 LTS by a Python package (`blender/c172`): subdivision-surface fuselage with boolean window/door openings and hinged doors, NACA 2412/0012 lofted wings with flaps/ailerons, empennage with elevator/rudder/trim tab, tubular gear with fairings, cowl with inlets and landing light, spinner/propeller.
- Full cockpit: 15 instruments with faces drawn from the POH-referenced scales, radio stack, switches, push-pull controls, yokes, pedals, trim wheel, fuel selector, seats and belts.
- O-320-H2AD assembly: finned barrels and heads, accessories, exhaust/muffler, mount, baffles; crank train animated with the Phase 7 kinematics; POH plug map on the plugs.
- Generated PBR textures (livery, rivets/seams, wear, dials, placards), generated sky HDR; editable `.blend`; high/medium/low Draco GLBs with per-level textures.
- New three.js viewer: HDR environment, shadows, GTAO, modes (exterior/cockpit/engine/systems), select/isolate/hide, exploded assembly, animated controls and surfaces, 3D instruments driven by the Phase 7 simulation, 69-entry bilingual part catalogue.
- Tests: Python profile tests, node tests (GLB ↔ kinematics ↔ plug map), GLB validator, Playwright browser test, CI job that rebuilds the model in Blender and compares it.
- Every dimension carries a status (POH page / type data / estimated); geometry remains representative, not manufacturer drawings.

09 — Book figures (2026-11-10):
- Figure plan (`09_book_figures/PLAN.md`): photographs for recognition, vector diagrams for understanding, the 3D twin as a technical-illustration engine; why the generated airframe does not read as a 172 (estimated shape tables) and how to correct it from reference photographs of the real aircraft.
- Figure build: one module per figure drawn as SVG in Chromium, exported as vector PDF (exact size, fonts embedded), SVG and review PNG, in English and Arabic from the same source; reproducible output.
- Illustration renderer for the Phase 8 model (flat tones, ink outlines, tinted subject) that also exports label anchor points, and automatic callout placement.
- Three draft samples: airspeed indicator markings (from `instruments.json`), fuel system schematic, flight control surfaces. Not yet reviewed against the aircraft's POH.
- Tests: manifest, bilingual text, POH provenance keys, agreement between instrument data, simulation constants and the POH table.

**Status:** Phases 01–06 are stored exactly as delivered (verify with `npm run verify:checksums`). No flight-certified or maintenance-grade simulation is claimed.
