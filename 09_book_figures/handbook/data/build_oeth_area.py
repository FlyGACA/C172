"""Build data/oeth_area.json: the line of the highway west of Thumamah (OETH), read off the open satellite picture data/open/oeth_area_s2.jpg (Copernicus Sentinel-2, 10 m;
"Contains modified Copernicus Sentinel data 2026"). figs/f_18_08_local_procedures.py draws it as a road, so that it can be seen at the size of a page.

The AIP's arrival from the west (AD 2.22) keeps "west of Thumamah highway" until the 45 degree entry. The picture shows one highway west of the aerodrome, along the edge of the
dunes, 4 to 5 km from the runway; that it is the one the AIP means is this project's reading (the book says so). The road is asphalt on pale sand, so it is the darkest line of
the picture: the path of least brightness between two points on it (two places named below, each moved to the darkest pixel within 250 m) follows it. No other source is used.

Needs numpy, pillow and scikit-image.   python build_oeth_area.py [--check-picture]      Not for navigation.
"""
import json
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw
from skimage.graph import route_through_array

HERE = os.path.dirname(os.path.abspath(__file__))
OPEN = os.path.join(HERE, "open")
with open(os.path.join(OPEN, "oeth_area_s2.json"), encoding="utf-8") as _f:
    META = json.load(_f)
E0, N0, E1, N1 = META["bounds_e_n_min_e_n_max"]
PX = META["pixel_m"]
ENDS = ((25.2379, 46.5769), (25.1514, 46.6491))        # two places on the highway (lat, lon), read off the picture: north-west of the aerodrome, and south of it
SNAP_M = 250.0
TOLERANCE_M = 12.0                                    # the line is thinned to points no further than this from the traced path

A, FLAT, K0, LON0 = 6378137.0, 1 / 298.257223563, 0.9996, math.radians(45.0)
_N = FLAT / (2 - FLAT)
_BIG = A / (1 + _N) * (1 + _N * _N / 4 + _N ** 4 / 64)


def utm38(lat, lon):
    """WGS 84 to UTM zone 38 N (EPSG:32638), the Krueger series to n^3."""
    al = (_N / 2 - 2 * _N * _N / 3 + 5 * _N ** 3 / 16, 13 * _N * _N / 48 - 3 * _N ** 3 / 5, 61 * _N ** 3 / 240)
    phi, lam = math.radians(lat), math.radians(lon) - LON0
    e = 2 * math.sqrt(_N) / (1 + _N)
    t = math.sinh(math.atanh(math.sin(phi)) - e * math.atanh(e * math.sin(phi)))
    xi, eta = math.atan2(t, math.cos(lam)), math.atanh(math.sin(lam) / math.sqrt(1 + t * t))
    east = 500000 + K0 * _BIG * (eta + sum(al[j] * math.cos(2 * (j + 1) * xi) * math.sinh(2 * (j + 1) * eta) for j in range(3)))
    north = K0 * _BIG * (xi + sum(al[j] * math.sin(2 * (j + 1) * xi) * math.cosh(2 * (j + 1) * eta) for j in range(3)))
    return east, north


def lat_lon(east, north):
    """UTM zone 38 N to WGS 84: the same series turned round."""
    be = (_N / 2 - 2 * _N * _N / 3 + 37 * _N ** 3 / 96, _N * _N / 48 + _N ** 3 / 15, 17 * _N ** 3 / 480)
    de = (2 * _N - 2 * _N * _N / 3 - 2 * _N ** 3, 7 * _N * _N / 3 - 8 * _N ** 3 / 5, 56 * _N ** 3 / 15)
    xi, eta = north / (K0 * _BIG), (east - 500000) / (K0 * _BIG)
    xi1 = xi - sum(be[j] * math.sin(2 * (j + 1) * xi) * math.cosh(2 * (j + 1) * eta) for j in range(3))
    eta1 = eta - sum(be[j] * math.cos(2 * (j + 1) * xi) * math.sinh(2 * (j + 1) * eta) for j in range(3))
    chi = math.asin(math.sin(xi1) / math.cosh(eta1))
    phi = chi + sum(de[j] * math.sin(2 * (j + 1) * chi) for j in range(3))
    return math.degrees(phi), math.degrees(LON0 + math.atan2(math.sinh(eta1), math.cos(xi1)))


def pixel(lat, lon):
    east, north = utm38(lat, lon)
    return int(round((N1 - north) / PX - 0.5)), int(round((east - E0) / PX - 0.5))


def darkest(lum, rc):
    half = int(SNAP_M / PX)
    r, c = rc
    r0, c0 = max(0, r - half), max(0, c - half)
    win = lum[r0:r + half + 1, c0:c + half + 1]
    i = np.unravel_index(np.argmin(win), win.shape)
    return int(r0 + i[0]), int(c0 + i[1])


def thin(points, tolerance):
    """Douglas and Peucker: the fewest of the points that keep the line within `tolerance`."""
    if len(points) < 3:
        return list(points)
    (x0, y0), (x1, y1) = points[0], points[-1]
    length = math.hypot(x1 - x0, y1 - y0) or 1.0
    far, where = 0.0, 0
    for i in range(1, len(points) - 1):
        d = abs((x1 - x0) * (y0 - points[i][1]) - (x0 - points[i][0]) * (y1 - y0)) / length
        if d > far:
            far, where = d, i
    if far <= tolerance:
        return [points[0], points[-1]]
    return thin(points[:where + 1], tolerance)[:-1] + thin(points[where:], tolerance)


def main():
    pic = np.asarray(Image.open(os.path.join(OPEN, "oeth_area_s2.jpg")).convert("RGB"), dtype=np.float32)
    lum = pic.mean(axis=2)
    a, b = (darkest(lum, pixel(*p)) for p in ENDS)
    cost = (lum / np.median(lum)) ** 6 + 0.002           # dark is cheap, steeply: the path stays on the asphalt
    path, _ = route_through_array(cost, a, b, fully_connected=True, geometric=True)
    path = np.array(path)
    grid = [(E0 + (c + 0.5) * PX, N1 - (r + 0.5) * PX) for r, c in path]          # the centres of the pixels, in the grid
    line = thin(grid, TOLERANCE_M)
    on_road = float(lum[path[:, 0], path[:, 1]].mean())
    length_km = float(np.hypot(np.diff(path[:, 0]), np.diff(path[:, 1])).sum()) * PX / 1000
    out = {"provenance": {"source": META["source"], "attribution": META["attribution"], "licence": META["licence"], "scenes": [s["id"] for s in META["scenes"]],
                          "method": "the path of least brightness on the picture between two places on the highway, thinned to %g m" % TOLERANCE_M,
                          "accuracy_m": "about 10 (one pixel)",
                          "check": {"mean_brightness_on_the_line": round(on_road, 1), "median_brightness_of_the_picture": round(float(np.median(lum)), 1), "length_km": round(length_km, 2)},
                          "reading": "that this road is the 'Thumamah highway' of AIP AD 2.22 is this project's reading: it is the only highway west of the aerodrome"},
           "highway_west_lat_lon": [[round(v, 6) for v in lat_lon(e, n)] for e, n in line]}
    assert on_road < 0.45 * float(np.median(lum)), "the traced line is not dark enough to be the road"
    with open(os.path.join(HERE, "oeth_area.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
    print("highway:", len(path), "pixels,", len(line), "points,", round(length_km, 2), "km; brightness on it", round(on_road, 1), "of", round(float(np.median(lum)), 1))
    if "--check-picture" in sys.argv:
        im = Image.fromarray(pic.astype(np.uint8))
        ImageDraw.Draw(im).line([((e - E0) / PX - 0.5, (N1 - n) / PX - 0.5) for e, n in line], fill=(0, 255, 255), width=2)
        im.crop((0, 400, 1500, 1770)).resize((1000, 913), Image.LANCZOS).save(os.path.join(OPEN, "oeth_area_check.jpg"), quality=80)


if __name__ == "__main__":
    main()
