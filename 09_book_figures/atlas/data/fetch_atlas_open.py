"""Fetch an open satellite picture of each aerodrome of the atlas, and write it under open/ next to this file.

Sentinel-2 L2A (Copernicus; free, full and open, attribution "Contains modified Copernicus Sentinel data <year>"): the bands B04, B03 and B02 of cloud-free scenes from the open
archive on AWS, found through the Earth Search STAC API. For each aerodrome the window is a rectangle round the middle of its runways (the thresholds of AIP AD 2.12), 16 km by
11 km, read at 10 m to the pixel in the UTM grid of the scenes. Of the tiles that cover the whole window the one with the most cloud-free scenes is taken, and every pixel gets
the median of its latest scenes (at most five).
    -> open/<icao>_s2.jpg and open/<icao>_s2.json (bounds, grid, scenes, the stretch), in the form figs/imagery_real.py of the handbook plates reads.

Needs: numpy, pillow, rasterio (GDAL) and network access.     python fetch_atlas_open.py aerodromes.json ICAO [ICAO ...]      Not for navigation.
"""
import json
import os
import sys
import urllib.request

import numpy as np
import rasterio
from PIL import Image
from rasterio.enums import Resampling
from rasterio.warp import transform
from rasterio.windows import from_bounds

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "open")
FIRST, LAST = "2026-06-01", "2026-11-16"
PIXEL = 10
HALF_E, HALF_N = 8000, 5500                         # metres from the middle of the runways to the sides of the window
N_SCENES = 5
STRETCH = (1.0, 99.7)
UA = {"User-Agent": "handbook-figure-builder/1.0", "Content-Type": "application/json"}


def search(lon, lat):
    d = 0.09
    box = {"type": "Polygon", "coordinates": [[[lon - d, lat - d], [lon + d, lat - d], [lon + d, lat + d], [lon - d, lat + d], [lon - d, lat - d]]]}
    body = {"collections": ["sentinel-2-l2a"], "intersects": box, "datetime": f"{FIRST}T00:00:00Z/{LAST}T23:59:59Z",
            "query": {"eo:cloud_cover": {"lt": 2.0}}, "sortby": [{"field": "properties.datetime", "direction": "desc"}], "limit": 100}
    req = urllib.request.Request("https://earth-search.aws.element84.com/v1/search", data=json.dumps(body).encode(), headers=UA)
    return json.load(urllib.request.urlopen(req, timeout=120))["features"]


def tile_of(f):
    p = f["properties"]
    return f"{p['mgrs:utm_zone']}{p['mgrs:latitude_band']}{p['mgrs:grid_square']}"


def fetch(icao, lon, lat):
    feats = search(lon, lat)
    by = {}
    for f in feats:
        by.setdefault(tile_of(f), []).append(f)
    best = None
    with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR", CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif", GDAL_HTTP_MAX_RETRY="4", GDAL_HTTP_RETRY_DELAY="2", AWS_NO_SIGN_REQUEST="YES"):
        for tile, fs in sorted(by.items(), key=lambda kv: -len(kv[1])):
            scenes, used, crs, bounds = [], [], None, None
            for f in fs:
                bands = []
                for key in ("red", "green", "blue"):
                    with rasterio.open(f["assets"][key]["href"]) as ds:
                        if crs is None:
                            crs = str(ds.crs)
                            (e,), (n,) = transform("EPSG:4326", crs, [lon], [lat])
                            snap = lambda v: round(v / PIXEL) * PIXEL
                            bounds = (snap(e - HALF_E), snap(n - HALF_N), snap(e + HALF_E), snap(n + HALF_N))
                            shape = (int((bounds[3] - bounds[1]) / PIXEL), int((bounds[2] - bounds[0]) / PIXEL))
                        assert str(ds.crs) == crs
                        bands.append(ds.read(1, window=from_bounds(*bounds, transform=ds.transform), out_shape=shape, resampling=Resampling.average, boundless=True, fill_value=0))
                a = np.stack(bands).astype(np.float32)
                if (a.min(axis=0) > 0).mean() < 0.999:      # the pass does not cover the whole window
                    continue
                scenes.append(a)
                used.append({"tile": tile, "id": f["id"], "datetime": f["properties"]["datetime"]})
                if len(scenes) == N_SCENES:
                    break
            if scenes and (best is None or len(scenes) > len(best[0])):
                best = (scenes, used, crs, bounds, e, n)
            if best and len(best[0]) == N_SCENES:
                break
    assert best, f"{icao}: no cloud-free scene covers the window"
    scenes, used, crs, bounds, e, n = best
    comp = np.median(np.stack(scenes), axis=0)
    lo, hi = (float(v) for v in np.percentile(comp, STRETCH))
    rgb = np.clip((comp - lo) / (hi - lo) * 255.0, 0, 255).astype(np.uint8).transpose(1, 2, 0)
    os.makedirs(OUT, exist_ok=True)
    name = icao.lower() + "_s2"
    Image.fromarray(rgb).save(os.path.join(OUT, name + ".jpg"), quality=86, subsampling=0, optimize=True)
    meta = {"source": f"Copernicus Sentinel-2 L2A, tile {used[0]['tile']}, bands B04 B03 B02 at 10 m; open archive on AWS (sentinel-cogs), found through Earth Search",
            "attribution": f"Contains modified Copernicus Sentinel data {FIRST[:4]}", "licence": "Copernicus Sentinel data: free, full and open access (Regulation (EU) No 1159/2013)",
            "method": "for every pixel the median of the scenes listed; one linear stretch for the three bands together",
            "crs": crs, "bounds_e_n_min_e_n_max": list(bounds), "pixel_m": PIXEL, "size_px": [rgb.shape[1], rgb.shape[0]], "centre_lon_lat": [lon, lat], "centre_e_n": [round(e, 1), round(n, 1)],
            "stretch_reflectance_dn": [round(lo, 1), round(hi, 1)], "scenes": used}
    with open(os.path.join(OUT, name + ".json"), "w") as f:
        json.dump(meta, f, indent=1)
        f.write("\n")
    print(icao, rgb.shape, len(used), "scenes", used[0]["tile"], crs, flush=True)


def main():
    airports = {a["icao"]: a for a in json.load(open(sys.argv[1], encoding="utf-8"))["airports"]}
    for icao in sys.argv[2:]:
        if os.path.exists(os.path.join(OUT, icao.lower() + "_s2.json")):
            continue
        th = [r["threshold"] for r in airports[icao]["runways"] if r.get("threshold")]
        lon, lat = sum(t["lon"] for t in th) / len(th), sum(t["lat"] for t in th) / len(th)
        try:
            fetch(icao, lon, lat)
        except Exception as ex:                       # one aerodrome must not stop the others
            print(icao, "FAILED", repr(ex)[:300], flush=True)


if __name__ == "__main__":
    main()
