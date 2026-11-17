# Open data behind the pictures of Thumamah and Riyadh

`../build_oeth_plan.py` builds `../oeth_plan.json`, the ground plan of Thumamah (OETH), from the Sentinel-2 files here and from the AIP values in `../saudi_airspace.json`. `../../figs/terrain_real.py` reads the elevation file for the real ground of Figures 17-1, 17-7 and 17-8. Not for navigation.

| File | What it is | Source and licence |
| --- | --- | --- |
| `oeth_s2_composite.npz`, `oeth_s2_composite.json` | Median of 14 cloud-free Sentinel-2 L2A scenes (bands B02, B03, B04, B08 at 10 m), cut to 3 km by 5.8 km round the aerodrome; the JSON lists the scenes, the bounds and the method | Copernicus Sentinel-2, from the open archive on AWS through the Earth Search STAC API. Copernicus Sentinel data are free, full and open; the attribution is **"Contains modified Copernicus Sentinel data 2026"** |
| `oeth_plan_check.png` | The outlines of `oeth_plan.json` drawn over the composite (taxiways blue, aprons orange, roofs green, the AIP runway magenta) | Contains modified Copernicus Sentinel data 2026 |
| `oeth_osm_check.json` | The OpenStreetMap ways tagged `aeroway` or `building` inside the aerodrome, **for comparison only**: none of their geometry is in the plan or in the figures | © OpenStreetMap contributors, Open Database License 1.0 |
| `fetch_oeth_open.py` | Fetches all of the above again (needs `rasterio` and network access) | this repository |
| `riyadh_terrain.npz`, `riyadh_terrain.json` | Ground elevation, 24.70 to 25.50 N and 46.20 to 47.20 E, every 2 arc-seconds (about 60 m), metres above mean sea level | NASA Shuttle Radar Topography Mission (SRTM), 1 arc-second, **public domain**, from the Terrain Tiles open dataset on AWS; credit line "Elevation: NASA SRTM" |
| `fetch_terrain_open.py` | Fetches the elevation file again (needs numpy and network access) | this repository |

To refresh: `python fetch_oeth_open.py [first date] [last date]`, then `python ../build_oeth_plan.py --check-picture` (needs numpy, pillow, scikit-image and shapely), look at `oeth_plan_check.png`, and rebuild the plates that draw the plan (18-1, 18-6, 26-1).

The elevation data agree with the AIP where the two can be compared: 1 877 ft at the Thumamah reference point (the AIP's elevation is 1 870 ft) and 1 867 and 1 854 ft at the two thresholds (1 870 and 1 868 ft). It is a radar survey flown in 2000, good to some tens of feet: it shows the shape of the country, not obstacles.
