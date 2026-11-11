# Phase 8 — Modelling architecture and milestones

## Toolchain

```
blender/build.py  ──(bpy, headless Blender 4.5 LTS)──►  models/C172N_realistic.blend
       │                                                 models/C172N_realistic_{high,medium,low}.glb
       │  c172/units.py      reference dimensions with status (measured / poh / type_data / estimated)
       │  c172/shapes.py     airfoils, cross-sections, lofts, bmesh helpers, UV projection
       │  posmaps.py         where each texel of the painted skins lies (run first: the paint is laid from it)
       │  c172/textures.py   numpy/PIL texture generation (paint scheme, atlases, normal maps, dials, sky HDR)
       │  c172/decals.py     markings laid on the skin as separate pieces; c172/ao.py shade baked into the GLB
       │  c172/materials.py  Principled BSDF materials wired to the generated textures
       │  c172/airframe.py   fuselage, windows, doors, wings, control surfaces, tail, fairings
       │  c172/gear.py       main gear, nose gear, wheels, fairings, brakes
       │  c172/powerplant.py cowling, spinner, propeller, exhaust, engine assembly
       │  c172/cockpit.py    panel, instruments, radio stack, controls, seats, interior
       │  c172/export.py     LOD derivation, Draco glTF export, model_index.json
       ▼
index.html + js/  ──(three.js r160, vendored, no build step)──►  interactive viewer
```

`scripts/get_blender.sh` downloads the exact Blender build used (4.5.15 LTS) so the model
can be rebuilt identically on a developer machine or in CI.

## Conventions

- Units: metres. The build works in Blender's frame (Z up, −Y forward = nose, +X = right
  wing); the glTF exporter converts to glTF axes (+Y up, +Z forward, +X = left wing), the
  same frame Phase 7 uses, so the Phase 7 simulation/animation code carries over.
- Datum: fuselage station 0 is the firewall (POH weight-and-balance datum).
- Every selectable part is its own object with a meaningful pivot (hinge line for control
  surfaces and doors, crank axis for the propeller, knob axis for controls).
- Object names: `SYSTEM.part_name` (`AIRFRAME.door_L`, `ENGINE.cylinder_1`, …).
  glTF `extras` carry `system`, `label_en`, `label_ar`, `status` (poh / type_data /
  estimated) and animation hints (`hinge_axis`, `range_deg`).
- Materials: Principled BSDF only (glTF-compatible), textures from `assets/textures/`.

## Quality levels

| Level | Subsurf | Textures | Target | Budget |
|---|---|---|---|---|
| high | 2 | 2048 px | desktop | ≤ 600 k triangles, ≤ 25 MB |
| medium | 1 | 1024 px | laptop / tablet | ≤ 250 k triangles, ≤ 12 MB |
| low | 1 + decimate (painted skins and propeller left whole) | 1024 px | telephone | ≤ 150 k triangles, ≤ 6 MB |

The paint of the fuselage is twice the size given (4096 px / 2048 px). `scripts/quality_gate.py` holds the
download sizes closer than this table: 9.6 / 5.9 / 5.4 MB.

Draco compression on all three; the viewer picks a level from device memory/GPU and the
user can override it.

## Milestones

1. **M1 — Exterior airframe**: fuselage with windows and doors, wings with flaps and
   ailerons, tail with elevator, rudder and trim tab, gear with fairings, cowling, spinner
   and propeller, exterior details, PBR materials with rivet/seam normal maps, livery,
   glass; viewer with HDR environment, shadows, LOD switching, orbit/touch.
2. **M2 — Cockpit**: panel, instruments with animated needles driven by the Phase 7
   simulation, radio stack, yokes, pedals, controls, seats, belts, interior trim.
3. **M3 — Engine compartment**: O-320-H2AD assembly with removable cowl, finned cylinders,
   accessories, internals animated by crank angle, exploded assembly animation.
4. **M4 — Lessons and faults**: Phase 7 scenarios wired to the new model; electrical, fuel,
   pitot-static and vacuum system highlights.
5. **M5 — Validation and performance**: render comparisons, proportion checks, console-clean
   load, desktop and mobile measurements, documented limitations.

`03_validation_report.md` records what each delivery actually achieved.
