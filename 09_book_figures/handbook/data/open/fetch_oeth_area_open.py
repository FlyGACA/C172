"""Fetch an open picture of the country round Thumamah (OETH) for the map of its local procedures (figs/f_18_08_local_procedures.py), and write it next to this file.

Sentinel-2 L2A (Copernicus; free, full and open, attribution "Contains modified Copernicus Sentinel data <year>"): the 10 m bands B02, B03 and B04 of three cloud-free
scenes of tile 38RPN from the open archive on AWS (found through the Earth Search STAC API), cut to a window that reaches 6.8 km west of the aerodrome reference
point, 19 km east, 7.4 km south and 10.3 km north (where the tile ends), each scene scaled to the common brightness, their median taken, and the result written as an
ordinary colour picture: one linear stretch for the three bands together, so the colours stay the ground's own.
    -> oeth_area_s2.jpg (8 bit, north up in the grid of EPSG:32638, 10 m to the pixel) and oeth_area_s2.json (bounds, scenes, the stretch).

figs/imagery_real.py lays it under a map. Needs: numpy, pillow, rasterio (GDAL) and network access.
    python fetch_oeth_area_open.py [first date] [last date]      Not for navigation.
"""
import json
import os
import sys
import urllib.request

import numpy as np
import rasterio
from PIL import Image
from rasterio.warp import transform
from rasterio.windows import from_bounds

HERE = os.path.dirname(os.path.abspath(__file__))
FIRST, LAST = sys.argv[1:3] if len(sys.argv) >= 3 else ("2026-06-25", "2026-11-16")
ARP = (25.2141667, 46.6408333)                      # AIP AD 2.2
N_SCENES = 3
PIXEL = 10
WEST, EAST, SOUTH, NORTH = 6800, 19000, 7400, 10300       # metres from the reference point (the tile ends 10.34 km north of it)
STRETCH = (1.0, 99.6)                               # the percentiles of all three bands together that become black and white
UA = {"User-Agent": "handbook-figure-builder/1.0", "Content-Type": "application/json"}


def search():
    body = {"collections": ["sentinel-2-l2a"], "intersects": {"type": "Point", "coordinates": [ARP[1], ARP[0]]}, "datetime": f"{FIRST}T00:00:00Z/{LAST}T23:59:59Z",
            "query": {"eo:cloud_cover": {"lt": 0.02}}, "sortby": [{"field": "properties.datetime", "direction": "desc"}], "limit": 60}
    req = urllib.request.Request("https://earth-search.aws.element84.com/v1/search", data=json.dumps(body).encode(), headers=UA)
    feats = json.load(urllib.request.urlopen(req, timeout=120))["features"]
    return [f for f in feats if f["properties"].get("s2:nodata_pixel_percentage", 0) == 0 and "_38RPN_" in f["id"]][:N_SCENES]


def composite(feats):
    (e,), (n,) = transform("EPSG:4326", "EPSG:32638", [ARP[1]], [ARP[0]])
    snap = lambda v: round(v / PIXEL) * PIXEL
    bounds = (snap(e - WEST), snap(n - SOUTH), snap(e + EAST), snap(n + NORTH))
    stack, used = [], []
    with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR", CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif", GDAL_HTTP_MAX_RETRY="4", GDAL_HTTP_RETRY_DELAY="2", AWS_NO_SIGN_REQUEST="YES"):
        for f in feats:
            bands = []
            for key in ("red", "green", "blue"):
                with rasterio.open(f["assets"][key]["href"]) as ds:
                    assert str(ds.crs).endswith("32638"), ds.crs
                    assert bounds[3] <= ds.bounds.top and bounds[2] <= ds.bounds.right and bounds[0] >= ds.bounds.left and bounds[1] >= ds.bounds.bottom, (bounds, ds.bounds)
                    bands.append(ds.read(1, window=from_bounds(*bounds, transform=ds.transform)))
            stack.append(np.stack(bands).astype(np.float32))
            used.append({"id": f["id"], "datetime": f["properties"]["datetime"]})
            print(f["id"], stack[-1].shape, flush=True)
    stack = np.stack(stack)
    ref = np.median(stack, axis=(0, 2, 3), keepdims=True)
    comp = np.median(stack * (ref / np.median(stack, axis=(2, 3), keepdims=True)), axis=0)
    lo, hi = (float(v) for v in np.percentile(comp, STRETCH))
    rgb = np.clip((comp - lo) / (hi - lo) * 255.0, 0, 255).astype(np.uint8).transpose(1, 2, 0)
    Image.fromarray(rgb).save(os.path.join(HERE, "oeth_area_s2.jpg"), quality=90, subsampling=0, optimize=True)
    meta = {"source": "Copernicus Sentinel-2 L2A, tile 38RPN, 10 m bands B04 B03 B02; open archive on AWS (sentinel-cogs), found through Earth Search",
            "attribution": f"Contains modified Copernicus Sentinel data {FIRST[:4]}", "licence": "Copernicus Sentinel data: free, full and open access (Regulation (EU) No 1159/2013)",
            "method": "per-scene scaling to the common median, the median over the scenes, one linear stretch for the three bands, JPEG quality 90",
            "crs": "EPSG:32638", "bounds_e_n_min_e_n_max": bounds, "pixel_m": PIXEL, "size_px": [rgb.shape[1], rgb.shape[0]], "arp_e_n": [round(e, 1), round(n, 1)],
            "stretch_reflectance_dn": [round(lo, 1), round(hi, 1)], "scenes": used}
    json.dump(meta, open(os.path.join(HERE, "oeth_area_s2.json"), "w"), indent=1)
    print("picture", rgb.shape, "from", len(used), "scenes")


if __name__ == "__main__":
    composite(search())
