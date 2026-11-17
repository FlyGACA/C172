"""Fetch an open picture of the coast round Red Sea International (OERS) for the map of its control zone (figs/f_17_02_class_by_the_clock.py), and write it next to this file.

Sentinel-2 L2A (Copernicus; free, full and open, attribution "Contains modified Copernicus Sentinel data <year>"): the bands B02, B03 and B04 of cloud-free scenes from the open
archive on AWS (found through the Earth Search STAC API). The control zone lies across two tiles of the same grid (37RBJ to the west, 37RCJ to the east; UTM zone 37 N), and
a pass of a satellite covers a tile wholly or only along one edge, so the scenes are not treated tile by tile: each scene is scaled to the brightness of the others over the
ground they share (the widest scene first), and every pixel gets the median of the scenes that have it. The window is a square of 52 km round the aerodrome reference point, read
at 20 m to the pixel (the 10 m bands, averaged by the reader).
    -> oers_area_s2.jpg (8 bit, north up in the grid of EPSG:32637, 20 m to the pixel) and oers_area_s2.json (bounds, scenes, the stretch).

figs/imagery_real.py lays it under a map. Needs: numpy, pillow, rasterio (GDAL) and network access.
    python fetch_oers_area_open.py [first date] [last date]      Not for navigation.
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
FIRST, LAST = sys.argv[1:3] if len(sys.argv) >= 3 else ("2026-08-01", "2026-11-16")
ARP = (25.6283333, 37.0888889)                      # AIP AD 2.2
TILES = ("37RBJ", "37RCJ")                          # west, east
N_SCENES = 6                                        # the latest cloud-free scenes of each tile
PIXEL = 20
HALF = 26000                                        # metres from the reference point to each side of the window
STRETCH = (1.0, 99.7)                               # the percentiles of all three bands together that become black and white
UA = {"User-Agent": "handbook-figure-builder/1.0", "Content-Type": "application/json"}


def search(tile, bounds_lonlat):
    """Cloud-free scenes of one tile that have data over the whole part of the window the tile covers (a pass can cut a tile along its edge)."""
    west, south, east, north = bounds_lonlat
    box = {"type": "Polygon", "coordinates": [[[west, south], [east, south], [east, north], [west, north], [west, south]]]}
    body = {"collections": ["sentinel-2-l2a"], "intersects": box, "datetime": f"{FIRST}T00:00:00Z/{LAST}T23:59:59Z",
            "query": {"eo:cloud_cover": {"lt": 1.0}}, "sortby": [{"field": "properties.datetime", "direction": "desc"}], "limit": 100}
    req = urllib.request.Request("https://earth-search.aws.element84.com/v1/search", data=json.dumps(body).encode(), headers=UA)
    feats = json.load(urllib.request.urlopen(req, timeout=120))["features"]
    return [f for f in feats if f"_{tile}_" in f["id"]]


def read(feature, bounds, shape):
    """The three bands of a scene over the window (zeros where the scene has no data)."""
    bands = []
    for key in ("red", "green", "blue"):
        with rasterio.open(feature["assets"][key]["href"]) as ds:
            assert str(ds.crs).endswith("32637"), ds.crs
            win = from_bounds(*bounds, transform=ds.transform)
            bands.append(ds.read(1, window=win, out_shape=shape, resampling=Resampling.average, boundless=True, fill_value=0))
    return np.stack(bands).astype(np.float32)


def main():
    (e,), (n,) = transform("EPSG:4326", "EPSG:32637", [ARP[1]], [ARP[0]])
    snap = lambda v: round(v / PIXEL) * PIXEL
    bounds = (snap(e - HALF), snap(n - HALF), snap(e + HALF), snap(n + HALF))
    shape = (int((bounds[3] - bounds[1]) / PIXEL), int((bounds[2] - bounds[0]) / PIXEL))
    lon, lat = transform("EPSG:32637", "EPSG:4326", [bounds[0], bounds[2], bounds[0], bounds[2]], [bounds[1], bounds[1], bounds[3], bounds[3]])
    box = (min(lon), min(lat), max(lon), max(lat))
    scenes, used = [], []
    with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR", CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif", GDAL_HTTP_MAX_RETRY="4", GDAL_HTTP_RETRY_DELAY="2", AWS_NO_SIGN_REQUEST="YES"):
        for tile in TILES:
            for f in search(tile, box)[:N_SCENES]:
                a = read(f, bounds, shape)
                has = a.min(axis=0) > 0
                a[:, ~has] = np.nan
                scenes.append(a)
                used.append({"tile": tile, "id": f["id"], "datetime": f["properties"]["datetime"], "share_of_window": round(float(has.mean()), 3)})
                print(f["id"], f"{has.mean():.0%} of the window", flush=True)
    # every scene is brought to the brightness of what is already there, over the ground the two share, the widest scene first
    order = sorted(range(len(scenes)), key=lambda i: -used[i]["share_of_window"])
    done = [scenes[order[0]]]
    for i in order[1:]:
        base = np.nanmedian(np.stack(done), axis=0)
        shared = np.isfinite(base[0]) & np.isfinite(scenes[i][0])
        assert shared.sum() > 10000, "a scene shares no ground with the others"
        k = np.array([np.median(base[b][shared]) / np.median(scenes[i][b][shared]) for b in range(3)])
        done.append(scenes[i] * k[:, None, None])
    stack = np.stack(done)
    count = np.isfinite(stack[:, 0]).sum(axis=0)
    assert count.min() >= 1, "part of the window has no scene"
    comp = np.nanmedian(stack, axis=0)
    print("scenes over a pixel: least", int(count.min()), "most", int(count.max()))
    lo, hi = (float(v) for v in np.percentile(comp, STRETCH))
    rgb = np.clip((comp - lo) / (hi - lo) * 255.0, 0, 255).astype(np.uint8).transpose(1, 2, 0)
    Image.fromarray(rgb).save(os.path.join(HERE, "oers_area_s2.jpg"), quality=88, subsampling=0, optimize=True)
    meta = {"source": "Copernicus Sentinel-2 L2A, tiles 37RBJ and 37RCJ, bands B04 B03 B02 read at 20 m; open archive on AWS (sentinel-cogs), found through Earth Search",
            "attribution": f"Contains modified Copernicus Sentinel data {FIRST[:4]}", "licence": "Copernicus Sentinel data: free, full and open access (Regulation (EU) No 1159/2013)",
            "method": "each scene scaled to the brightness of the others over the ground they share (the widest scene first), then for every pixel the median of the scenes that have it; one linear stretch for the three bands, JPEG quality 88",
            "crs": "EPSG:32637", "bounds_e_n_min_e_n_max": list(bounds), "pixel_m": PIXEL, "size_px": [rgb.shape[1], rgb.shape[0]], "arp_e_n": [round(e, 1), round(n, 1)],
            "scenes_over_a_pixel": [int(count.min()), int(count.max())], "stretch_reflectance_dn": [round(lo, 1), round(hi, 1)], "scenes": used}
    with open(os.path.join(HERE, "oers_area_s2.json"), "w") as f:
        json.dump(meta, f, indent=1)
        f.write("\n")
    print("picture", rgb.shape, "from", len(used), "scenes")


if __name__ == "__main__":
    main()
