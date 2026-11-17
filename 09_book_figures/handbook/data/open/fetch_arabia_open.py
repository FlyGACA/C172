"""Fetch open relief and land data for the chart of the Arabian peninsula and the globe of figs/f_20_02_chart_projection.py, and write them next to this file.

Natural Earth (naturalearthdata.com): public domain, "no permission is needed to use Natural Earth". Two of its files:
    SR_HR.zip (1:10m raster)        the shaded relief of the land, 21 600 x 10 800 pixels, one minute of arc to the pixel, grey
    ne_50m_land (1:50m vector)      the land as polygons: the coastline, and nothing else
Written:
    arabia_relief.jpg    the relief from 28 to 64 E and from 8 to 40 N, one minute of arc to the pixel (2 160 x 1 920, 8-bit grey)
    arabia_land.png      land (white) and sea (black) on the same grid, from the polygons, the edge smoothed
    globe_relief.jpg     the relief of the side of the globe that faces Arabia, 45 W to 135 E and 70 S to 90 N, six minutes to the pixel (1 800 x 1 600)
    globe_land.png       land and sea on that grid
    arabia_open.json     the sources, the hashes of what was downloaded, the grids
No boundary between countries is fetched: the figure draws coasts, and the sheets of the AIP's chart series.

figs/arabia_real.py lays these under a map. Needs: numpy, pillow and network access.      python fetch_arabia_open.py [folder that already holds the two downloads]      Not for navigation.
"""
import hashlib
import io
import json
import os
import sys
import urllib.request
import zipfile

import numpy as np
from PIL import Image, ImageDraw

Image.MAX_IMAGE_PIXELS = None
HERE = os.path.dirname(os.path.abspath(__file__))
RELIEF_URL = "https://naciscdn.org/naturalearth/10m/raster/SR_HR.zip"
LAND_URL = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_50m_land.geojson"
ARABIA = {"west": 28.0, "east": 64.0, "south": 8.0, "north": 40.0, "pixels_per_degree": 60}
GLOBE = {"west": -45.0, "east": 135.0, "south": -70.0, "north": 90.0, "pixels_per_degree": 10}
UA = {"User-Agent": "handbook-figure-builder/1.0"}


def get(url, cache):
    name = url.rsplit("/", 1)[1]
    if cache and os.path.exists(os.path.join(cache, name)):
        with open(os.path.join(cache, name), "rb") as f:
            return f.read()
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=600).read()


def relief_window(world, box):
    """The window of the one-minute relief for a box, at the box's own pixel size (averaged down where that is coarser)."""
    per = 60                                                                 # pixels to the degree in the source: its first column begins at 180 W, its first row at 90 N
    c0, c1 = int(round((box["west"] + 180) * per)), int(round((box["east"] + 180) * per))
    r0, r1 = int(round((90 - box["north"]) * per)), int(round((90 - box["south"]) * per))
    win = world.crop((c0, r0, c1, r1))
    k = per // box["pixels_per_degree"]
    return win if k == 1 else win.resize((win.size[0] // k, win.size[1] // k), Image.BOX)


def land_mask(land, box, over=3):
    """Land white, sea black, on the grid of a box: the polygons drawn `over` times larger and averaged down, so that the coast is smooth."""
    per = box["pixels_per_degree"] * over
    w, h = int(round((box["east"] - box["west"]) * per)), int(round((box["north"] - box["south"]) * per))
    im = Image.new("L", (w, h), 0)
    draw = ImageDraw.Draw(im)
    xy = lambda ring: [((lon - box["west"]) * per, (box["north"] - lat) * per) for lon, lat in ring]
    polygons = []
    for feature in land["features"]:
        g = feature["geometry"]
        polygons += [g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"]
    inside = lambda ring: any(box["west"] - 1 <= lon <= box["east"] + 1 and box["south"] - 1 <= lat <= box["north"] + 1 for lon, lat in ring) or (
        min(p[0] for p in ring) < box["west"] and max(p[0] for p in ring) > box["east"] and min(p[1] for p in ring) < box["south"] and max(p[1] for p in ring) > box["north"])
    for rings in polygons:                                                   # the outer rings first, then the holes (the inland seas), then the islands in them, in the order of the file
        if inside(rings[0]):
            draw.polygon(xy(rings[0]), fill=255)
            for hole in rings[1:]:
                draw.polygon(xy(hole), fill=0)
    return im.resize((w // over, h // over), Image.BOX)


def main():
    cache = sys.argv[1] if len(sys.argv) > 1 else None
    relief_zip, land_bytes = get(RELIEF_URL, cache), get(LAND_URL, cache)
    with zipfile.ZipFile(io.BytesIO(relief_zip)) as z:
        version = z.read("SR_HR.VERSION.txt").decode().strip()
        world = Image.open(io.BytesIO(z.read("SR_HR.tif")))
        world.load()
    assert world.size == (21600, 10800) and world.mode == "L", (world.size, world.mode)
    land = json.loads(land_bytes)
    out = {"source": "Natural Earth (naturalearthdata.com): shaded relief SR_HR (1:10m) and land polygons ne_50m_land (1:50m)",
           "licence": "public domain (Natural Earth terms of use: no permission needed, credit appreciated)", "attribution": "Made with Natural Earth",
           "downloads": [{"url": RELIEF_URL, "sha256": hashlib.sha256(relief_zip).hexdigest(), "bytes": len(relief_zip), "version": version},
                         {"url": LAND_URL, "sha256": hashlib.sha256(land_bytes).hexdigest(), "bytes": len(land_bytes)}],
           "method": "the relief cut to each box (averaged to six minutes for the globe), JPEG quality 90; the land polygons drawn three times larger and averaged down; no boundaries between countries",
           "grids": {}}
    for name, box in (("arabia", ARABIA), ("globe", GLOBE)):
        relief = relief_window(world, box)
        mask = land_mask(land, box)
        assert relief.size == mask.size, (relief.size, mask.size)
        relief.save(os.path.join(HERE, f"{name}_relief.jpg"), quality=90)
        mask.save(os.path.join(HERE, f"{name}_land.png"), optimize=True)
        land_share = float(np.asarray(mask).mean() / 255)
        out["grids"][name] = {**box, "size_px": list(relief.size), "land_share": round(land_share, 4), "note": "the first pixel's corner is at (west, north); longitude grows to the right, latitude falls downwards"}
        print(name, relief.size, f"land {land_share:.1%}", os.path.getsize(os.path.join(HERE, f"{name}_relief.jpg")) // 1024, "kB relief,", os.path.getsize(os.path.join(HERE, f"{name}_land.png")) // 1024, "kB land")
    with open(os.path.join(HERE, "arabia_open.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
        f.write("\n")


if __name__ == "__main__":
    main()
