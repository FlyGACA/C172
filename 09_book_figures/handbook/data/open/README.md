# Open data behind the ground plan of Thumamah (OETH)

`../build_oeth_plan.py` builds `../oeth_plan.json` from the files here and from the AIP values in `../saudi_airspace.json`. Not for navigation.

| File | What it is | Source and licence |
| --- | --- | --- |
| `oeth_s2_composite.npz`, `oeth_s2_composite.json` | Median of 14 cloud-free Sentinel-2 L2A scenes (bands B02, B03, B04, B08 at 10 m), cut to 3 km by 5.8 km round the aerodrome; the JSON lists the scenes, the bounds and the method | Copernicus Sentinel-2, from the open archive on AWS through the Earth Search STAC API. Copernicus Sentinel data are free, full and open; the attribution is **"Contains modified Copernicus Sentinel data 2026"** |
| `oeth_plan_check.png` | The outlines of `oeth_plan.json` drawn over the composite (taxiways blue, aprons orange, roofs green, the AIP runway magenta) | Contains modified Copernicus Sentinel data 2026 |
| `oeth_osm_check.json` | The OpenStreetMap ways tagged `aeroway` or `building` inside the aerodrome, **for comparison only**: none of their geometry is in the plan or in the figures | © OpenStreetMap contributors, Open Database License 1.0 |
| `fetch_oeth_open.py` | Fetches all of the above again (needs `rasterio` and network access) | this repository |

To refresh: `python fetch_oeth_open.py [first date] [last date]`, then `python ../build_oeth_plan.py --check-picture` (needs numpy, pillow, scikit-image and shapely), look at `oeth_plan_check.png`, and rebuild the plates that draw the plan (18-1, 18-6, 26-1).
