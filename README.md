# FlyGACA — Cessna 172N Digital Twin

Canonical repository for the FlyGACA Cessna 172N educational 3D project (replaces `n172`).
Reference aircraft: **Cessna 172N, 1979 model**, factory-standard educational baseline;
the configuration of a specific serial number is not verified.

**Latest: [Phase 7 — kinematic twin & POH-referenced systems simulation](07_kinematic_twin/)**

```bash
python3 -m http.server 8000
# then open http://localhost:8000/07_kinematic_twin/
```

## Phases

| # | Folder | Contents |
|---|---|---|
| 01 | [`01_initial/`](01_initial/) | First editable airframe GLB and its Python/trimesh generator |
| 02 | [`02_classic_analog_v2/`](02_classic_analog_v2/) | Classic analog model, browser viewer, reference photos |
| 02b | [`02b_refined_airframe/`](02b_refined_airframe/) | Refined Phase 2 GLB, Blender enhancement script, viewer, photos |
| 03 | [`03_education/`](03_education/) | Exploded engine, instrument training lab, curriculum |
| 04 | [`04_digital_twin/`](04_digital_twin/) | C172N systems GLB, approximate airframe, learning lab |
| 04b | [`04b_poh_reference/`](04b_poh_reference/) | 1979 POH reference data and revised lab |
| 05 | [`05_systems_lab/`](05_systems_lab/) | Interactive systems lab, lessons, build script |
| 06 | [`06_interactive_twin/`](06_interactive_twin/) | 224-part GLB, Three.js viewer, manifest |
| **07** | [**`07_kinematic_twin/`**](07_kinematic_twin/) | Rebuilt model with pivots and Lycoming-correct engine, crank-driven animation, documented systems simulation, 10 guided POH scenarios, offline viewer, tests |

Folders 01–06 are the original release packages, imported unchanged; see
[RELEASES.md](RELEASES.md). Their integrity is checked against
[`SHA256SUMS.txt`](SHA256SUMS.txt) (the upload package's own README is kept at
[`docs/archive/UPLOAD_PACKAGE_README.md`](docs/archive/UPLOAD_PACKAGE_README.md)).

## Development

| Command | What it does |
|---|---|
| `npm run build:model` | Rebuild the Phase 7 GLB (Python 3 + numpy) |
| `npm run verify:model` | Rebuild in a temp dir and compare with the committed GLB |
| `npm run verify:checksums` | Verify the archived phase packages |
| `npm test` | Unit tests: kinematics, POH-referenced simulation behaviour, scenarios |
| `npm run test:e2e` | Browser test with Playwright (`npm ci && npx playwright install chromium` first) |

GitHub Actions runs all of the above on every pull request and push to `main`.

## Safety

All geometry, instruments, engine behaviour and fault scenarios are educational
approximations. They are not validated against a specific aircraft serial number
and are not approved for flight, maintenance or training credit. Refer to the
aircraft-specific POH/AFM and Cessna/Lycoming manuals.
