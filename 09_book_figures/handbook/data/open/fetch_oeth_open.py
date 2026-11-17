"""Fetch the open data that data/build_oeth_plan.py draws the ground plan of Thumamah (OETH) from, and write it next to this file.

1. Sentinel-2 L2A (Copernicus; free, full and open, attribution "Contains modified Copernicus Sentinel data <year>"): the 10 m bands B02, B03, B04
   and B08 of cloud-free scenes of tile 38RPN from the open archive on AWS (found through the Earth Search STAC API), cut to a window round the
   aerodrome, each scene scaled to the common brightness, and their median taken (parked aeroplanes and shadows drop out).
   -> oeth_s2_composite.npz (uint16, north up, EPSG:32638) and oeth_s2_composite.json (bounds, scenes).
2. OpenStreetMap (ODbL 1.0, (c) OpenStreetMap contributors): the ways tagged aeroway or building inside the aerodrome, kept only to compare
   with: none of their geometry goes into the plan.  -> oeth_osm_check.json

Needs: numpy, pillow, rasterio (GDAL) and network access.   python fetch_oeth_open.py [first date] [last date]    Not for navigation.
"""
import json
import os
import sys
import urllib.request
import xml.etree.ElementTree as ET

import numpy as np
import rasterio
from rasterio.warp import transform
from rasterio.windows import from_bounds

HERE = os.path.dirname(os.path.abspath(__file__))
FIRST, LAST = (sys.argv[1:3] + ["2026-06-25", "2026-11-16"])[:2] if len(sys.argv) >= 3 else ("2026-06-25", "2026-11-16")
ARP = (25.2141667, 46.6408333)                      # AIP AD 2.2
N_SCENES = 14
UA = {"User-Agent": "handbook-figure-builder/1.0", "Content-Type": "application/json"}


def search():
    body = {"collections": ["sentinel-2-l2a"], "intersects": {"type": "Point", "coordinates": [ARP[1], ARP[0]]}, "datetime": f"{FIRST}T00:00:00Z/{LAST}T23:59:59Z",
            "query": {"eo:cloud_cover": {"lt": 0.02}}, "sortby": [{"field": "properties.datetime", "direction": "desc"}], "limit": 60}
    req = urllib.request.Request("https://earth-search.aws.element84.com/v1/search", data=json.dumps(body).encode(), headers=UA)
    feats = json.load(urllib.request.urlopen(req, timeout=120))["features"]
    return [f for f in feats if f["properties"].get("s2:nodata_pixel_percentage", 0) == 0][:N_SCENES]


def composite(feats):
    (e,), (n,) = transform("EPSG:4326", "EPSG:32638", [ARP[1] - 0.0008], [ARP[0] - 0.0017])
    bounds = (round((e - 1500) / 10) * 10, round((n - 2900) / 10) * 10, round((e + 1500) / 10) * 10, round((n + 2900) / 10) * 10)
    stack, used = [], []
    with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR", CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif", GDAL_HTTP_MAX_RETRY="4", GDAL_HTTP_RETRY_DELAY="2", AWS_NO_SIGN_REQUEST="YES"):
        for f in feats:
            bands = []
            for key in ("blue", "green", "red", "nir"):
                with rasterio.open(f["assets"][key]["href"]) as ds:
                    assert str(ds.crs).endswith("32638"), ds.crs
                    bands.append(ds.read(1, window=from_bounds(*bounds, transform=ds.transform)))
            stack.append(np.stack(bands).astype(np.float32))
            used.append({"id": f["id"], "datetime": f["properties"]["datetime"]})
            print(f["id"], stack[-1].shape, flush=True)
    stack = np.stack(stack)
    ref = np.median(stack, axis=(0, 2, 3), keepdims=True)
    comp = np.median(stack * (ref / np.median(stack, axis=(2, 3), keepdims=True)), axis=0)
    comp = np.clip(np.rint(comp), 0, 65535).astype(np.uint16)
    np.savez_compressed(os.path.join(HERE, "oeth_s2_composite.npz"), B02=comp[0], B03=comp[1], B04=comp[2], B08=comp[3])
    meta = {"source": "Copernicus Sentinel-2 L2A, tile 38RPN, 10 m bands B02 B03 B04 B08; open archive on AWS (sentinel-cogs), found through Earth Search",
            "attribution": f"Contains modified Copernicus Sentinel data {FIRST[:4]}", "licence": "Copernicus Sentinel data: free, full and open access (Regulation (EU) No 1159/2013)",
            "method": "per-scene scaling to the common median, then the median over the scenes", "crs": "EPSG:32638", "bounds_e_n_min_e_n_max": bounds, "pixel_m": 10,
            "scenes": used}
    json.dump(meta, open(os.path.join(HERE, "oeth_s2_composite.json"), "w"), indent=1)

    print("composite", comp.shape, "from", len(used), "scenes")


def osm_check():
    url = "https://api.openstreetmap.org/api/0.6/map?bbox=46.600,25.170,46.680,25.260"
    root = ET.fromstring(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120).read())
    nodes = {n.get("id"): (float(n.get("lat")), float(n.get("lon"))) for n in root.iter("node")}
    ways = []
    for w in root.iter("way"):
        tags = {t.get("k"): t.get("v") for t in w.findall("tag")}
        if "aeroway" not in tags and "building" not in tags:
            continue
        pts = [nodes[nd.get("ref")] for nd in w.findall("nd") if nd.get("ref") in nodes]
        if not any(25.19 < la < 25.24 and 46.63 < lo < 46.65 for la, lo in pts):
            continue
        ways.append({"way": int(w.get("id")), "version": int(w.get("version")), "timestamp": w.get("timestamp"),
                     "tags": {k: v for k, v in tags.items() if k in ("aeroway", "building", "ref", "icao", "surface")}, "lat_lon": [[round(la, 7), round(lo, 7)] for la, lo in pts]})
    out = {"source": "OpenStreetMap, API 0.6 map call", "attribution": "(c) OpenStreetMap contributors", "licence": "Open Database License (ODbL) 1.0, https://opendatacommons.org/licenses/odbl/1-0/",
           "use": "comparison only: no geometry of this file is in oeth_plan.json or in the figures", "ways": ways}
    json.dump(out, open(os.path.join(HERE, "oeth_osm_check.json"), "w"), indent=1)
    print("OpenStreetMap:", len(ways), "ways")


if __name__ == "__main__":
    composite(search())
    osm_check()
