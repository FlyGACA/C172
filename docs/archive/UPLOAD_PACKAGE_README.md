# FlyGACA C172 Digital Twin — complete project history

Canonical GitHub destination: `iflygaca/C172`.

All eight directories preserve the original release packages in chronological order, including the alternate Phase 2 revision and POH reference update. Source files, editable GLB meshes, HTML learning labs, reference images and metadata are included where they existed in the source archives.

## Folder map

| Folder | Contents |
|---|---|
| `01_initial/` | First editable airframe and generator source |
| `02_classic_analog_v2/` | Intermediate V2 analog model, viewer and reference photos |
| `02b_refined_airframe/` | Phase 2 refined GLB, viewer, Blender enhancement script, photos |
| `03_education/` | Exploded engine, instrument lab, curriculum |
| `04_digital_twin/` | C172N systems GLB, approximate airframe, learning lab |
| `04b_poh_reference/` | 1979 POH reference data and revised lab |
| `05_systems_lab/` | Interactive systems lab, lessons, build script |
| `06_interactive_twin/` | 224-part GLB, Three.js viewer, phase manifest |

## Upload to GitHub

1. Download and extract `C172_GitHub_Upload_All_Phases.zip` on a computer.
2. Open `https://github.com/iflygaca/C172`.
3. Choose **Add file → Upload files**, then drag the **contents of the extracted folder** (all phase folders and files) into the upload page. Do not upload only the ZIP if you want GitHub to show the individual source files.
4. Commit the upload to `main` or create a PR.
5. Check `06_interactive_twin/C172N_Phase6_Animated_Parts.glb` and the HTML viewer are present.

The GitHub website may limit individual upload sizes/counts; upload phase folders separately if needed. The existing root README can be replaced by this one.

## Running Phase 6

From the extracted project root: `python -m http.server 8000` then visit `http://localhost:8000/06_interactive_twin/FlyGACA_C172N_Phase6_Viewer.html`. The viewer needs internet for its Three.js CDN dependencies.

**Safety:** All geometry, flight instruments, engine behavior and fault scenarios are educational approximations. Not validated against a specific aircraft serial number and not approved for operational or maintenance use.
