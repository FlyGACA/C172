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

**Status:** Phases 01–06 are stored exactly as delivered (verify with `npm run verify:checksums`). No flight-certified or maintenance-grade simulation is claimed.
