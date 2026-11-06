# Phase 7 — Kinematic twin & POH-referenced systems simulation

**Open:** from the repository root run `python3 -m http.server 8000`, then visit
<http://localhost:8000/07_kinematic_twin/>. Everything (three.js included) is in this
folder, so it works offline. Arabic is the default language; the button in the top
corner switches to English.

[النسخة العربية](README_AR.md)

## What is new

| Area | Phase 6 | Phase 7 |
|---|---|---|
| 3D model | 224 parts baked in world space (no pivots) | 254 meshes / 281 nodes, every part on its own pivot, PBR materials, colour-coded plumbing |
| Engine motion | pistons bobbed on a sine wave | crankshaft, rods, pistons and valves driven by crank angle (slider-crank), firing order 1-3-2-4, camshaft at half speed, plugs flash when they fire |
| Cylinder numbering | 1 and 2 on the same side | Lycoming convention: odd on the right bank, even on the left, No. 1 right-front |
| Ignition | two separate magnetos | one dual magneto with the POH plug map (p.7-19) |
| Airframe | separate approximate GLB (missing from the package) | 1:1 envelope from POH Fig 1-1 in the same file, systems placed where Section 7 says they are |
| Simulation | throttle → RPM line, frozen-needle faults | documented systems model (`js/sim.js`), see below |
| Lessons | 5 two-option questions | 10 guided POH checklists with live step checking, debriefs and review questions |
| Instruments | text read-outs | 14-gauge SVG panel + working 3D needles, markings from POH Fig 2-2 / 2-3 |
| Testing | none ("not tested in a browser") | 41 unit/scenario tests, Playwright browser test, CI |

## Using it

- **Cockpit controls** (left): split master BAT/ALT, avionics, ignition OFF-R-L-BOTH and a
  spring-loaded START (hold), throttle, mixture, carb heat, primer, fuel selector,
  alternate static, pitot heat, lights, Kollsman setting.
- **Flight state**: the instructor sets airspeed, altitude, bank and pitch. This is a
  *systems* trainer, not a flight model.
- **Faults**: pitot (inlet / inlet + drain), static port, alternator (failed /
  over-voltage), vacuum pump, carburetor-icing conditions, each magneto (weak, dead,
  ungrounded P-lead), tank quantities.
- **3D toolbar**: view presets, X-ray engine, labels, airframe, isolate a system,
  explode, displayed motion speed (the real 2400 RPM is shown slowed down), and a
  hand-turn slider for walking through the four-stroke cycle with the engine stopped.
- Click any part for a bilingual description and its documentation status
  (POH page / engine type data / illustrative).

## Scenarios

| Scenario | POH | What the student does |
|---|---|---|
| Engine start (cold) | 4-7, 4-11 | full start checklist incl. priming; over-priming floods |
| Run-up & magneto check | 4-7, 4-13 | 1700 RPM, R/L drops evaluated against 125 / 50 RPM |
| Run-up: diagnose the ignition | 3-16, 4-13 | hidden weak magneto, decide airworthiness |
| Cruise leaning | 4-16 | lean until RPM peaks, then until it drops 25–50 RPM |
| Carburetor icing | 3-16 | recognise RPM loss, full throttle + full heat |
| Static source blockage | 3-8, 5-9 | frozen altimeter / VSI, alternate static, calibration table |
| Iced pitot tube | 7-31 | ASI decays, pitot heat |
| Low-voltage light | 3-9, 7-26 | ACU over-voltage trip, master recycle, load shedding |
| Vacuum failure | 7-34 | suction low, partial panel with the turn coordinator |
| Engine failure (fuel) | 3-4 | empty tank, 65 KIAS, POH restart checklist |

## How the simulation is built (`js/sim.js`)

Every number that comes from the handbook is in the `POH` object and in
[`data/poh_references.json`](data/poh_references.json) with its page. Tests assert
the model reproduces them:

- full-throttle static RPM 2280–2400 (p.2-5); full carb heat at full throttle costs
  100–225 RPM (p.7-19); healthy magneto drops pass ≤125 / ≤50 RPM (p.4-7);
  suction 4.5–5.4 inHg at run-up (p.2-6); RPM peaks while leaning at altitude (p.4-16);
  ALT off with load lights LOW VOLTAGE (p.7-26/27); 1.5 gal unusable per tank (p.2-6);
  alternate-static ASI equals the Fig 5-1 table (p.5-9).
- Pitot-static uses the ISA atmosphere and the compressible impact-pressure equation,
  so blocked-line behaviour emerges from the physics: inlet blocked with drain open →
  ASI to zero; inlet and drain blocked → ASI climbs with altitude; static blocked →
  altimeter frozen, VSI zero, ASI under-reads in a climb.

Everything else (prop absorption curve, alternator output vs RPM, battery capacity,
gyro spin times, oil temperature, valve timing, rod length) is **illustrative** and
labelled as such in the code.

## Files

```
index.html, css/, js/          viewer (ES modules, no build step)
js/sim.js                      systems simulation (DOM-free)
js/kinematics.js               engine kinematics (shared with tests)
js/scenarios.js                guided POH scenarios
data/instruments.json          dial scales/markings used by both the GLB builder and the SVG panel
data/parts_catalog.json        bilingual part descriptions
data/poh_references.json       page-referenced handbook values
data/model_index.json          generated by the builder (part counts, cylinder layout, plug map)
build/                         build_phase7_model.py (+ geometry.py, glb_writer.py), verify_model.py
C172N_Phase7_Kinematic_Twin.glb
vendor/three/                  three.js r160 (MIT) — pinned, served locally
tests/                         node:test unit tests and the Playwright browser test
```

Rebuild the model with `npm run build:model` (Python 3 + numpy). Open the GLB in
Blender (File → Import → glTF 2.0): each part is a named object with its pivot at a
sensible origin, and glTF `extras` (Blender custom properties) carry the system group,
cylinder number and POH reference.

## Limits

Geometry is schematic and not taken from Cessna/Lycoming drawings or an IPC.
The simulation is a teaching model, not certified and not calibrated against an
aircraft. Installed equipment differs by serial number and modification. Always use
the aircraft-specific POH/AFM and your instructor.

## Next steps

1. Panel layout and equipment from the FlyGACA aircraft's own equipment list.
2. IPC-based remodelling of engine accessories and firewall installations.
3. Flight-dynamics layer (glide, climb performance from POH Section 5).
4. Instructor/student progress tracking and integration on FlyGACA.com.
