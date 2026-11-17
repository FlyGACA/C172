"""Real ground for the pictures of the country round Thumamah and Riyadh: the open elevation data of data/open/riyadh_terrain.npz (NASA SRTM, public domain, thinned to
2 arc-seconds; fetched by data/open/fetch_terrain_open.py). numpy and Pillow only.

    elevation_m(lat, lon)                 the ground there, metres above mean sea level (bilinear)
    profile(points, step_nm)              the ground under a route: [(distance along it in NM, elevation in ft), ...] for [(lat, lon), ...]
    corridor_max_ft(points, half_nm)      the highest ground within `half_nm` of the route, in ft, with where it is
    ensure(name, frame, canvas, ...)      a shaded relief of the country a map frame (figs/h_b2.Frame) shows, written to renders/<name>.png once, to lay as a sprite under the map

Not for navigation: 60 m samples of a radar survey flown in 2000; it shows the shape of the country, not obstacles."""
import json
import math
import os

import numpy as np
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
OPEN = os.path.join(os.path.dirname(HERE), "data", "open")
RENDERS = os.path.join(os.path.dirname(HERE), "renders")
FT = 0.3048
with open(os.path.join(OPEN, "riyadh_terrain.json"), encoding="utf-8") as _f:
    META = json.load(_f)
_Z = None


def _z():
    global _Z
    if _Z is None:
        _Z = np.load(os.path.join(OPEN, "riyadh_terrain.npz"))["elevation_m"].astype(np.float32)
    return _Z


def _rc(lat, lon):
    k = 3600.0 / META["step_arcsec"]
    return (META["north"] - lat) * k, (lon - META["west"]) * k


def elevation_m(lat, lon):
    z = _z()
    r, c = _rc(lat, lon)
    r = min(max(r, 0.0), z.shape[0] - 1.001)
    c = min(max(c, 0.0), z.shape[1] - 1.001)
    r0, c0 = int(r), int(c)
    fr, fc = r - r0, c - c0
    return float(z[r0, c0] * (1 - fr) * (1 - fc) + z[r0, c0 + 1] * (1 - fr) * fc + z[r0 + 1, c0] * fr * (1 - fc) + z[r0 + 1, c0 + 1] * fr * fc)


def _nm(a, b):
    """Distance in NM and the unit vector (east, north) from a to b, both (lat, lon), on the flat map of the figures."""
    k = 60.0 * math.cos(math.radians((a[0] + b[0]) / 2))
    e, n = (b[1] - a[1]) * k, (b[0] - a[0]) * 60.0
    d = math.hypot(e, n)
    return d, ((e / d, n / d) if d else (0.0, 0.0))


def profile(points, step_nm=0.05):
    out, along = [], 0.0
    for a, b in zip(points, points[1:]):
        d, _ = _nm(a, b)
        n = max(1, int(round(d / step_nm)))
        for i in range(n + (1 if b is points[-1] else 0)):
            f = i / n
            out.append((along + d * f, elevation_m(a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f) / FT))
        along += d
    return out


def corridor_max_ft(points, half_nm=0.5, step_nm=0.05):
    best = (-1.0, 0.0, None)
    along = 0.0
    for a, b in zip(points, points[1:]):
        d, (ue, un) = _nm(a, b)
        k = 60.0 * math.cos(math.radians((a[0] + b[0]) / 2))
        n = max(1, int(round(d / step_nm)))
        for i in range(n + 1):
            f = i / n
            la, lo = a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f
            for off in np.arange(-half_nm, half_nm + 1e-9, step_nm):
                # the point `off` NM to the right of the track: right of (ue, un) is (un, -ue)
                pla, plo = la + off * (-ue) / 60.0, lo + off * un / k
                h = elevation_m(pla, plo) / FT
                if h > best[0]:
                    best = (h, along + d * f, (pla, plo))
        along += d
    return best


def ensure(name, frame, canvas, px_per_unit=4, veil=0.34, soft=1.2, exaggeration=7.0):
    """Shaded relief for the map of `frame` (figs/h_b2.Frame) on a canvas of (w, h) units: sand-coloured by height, lit from the north-west, washed towards pale by `veil`."""
    path = os.path.join(RENDERS, name + ".png")
    if os.path.exists(path):
        return path
    w, h = int(canvas[0] * px_per_unit), int(canvas[1] * px_per_unit)
    xs = (np.arange(w) + 0.5) / px_per_unit
    ys = (np.arange(h) + 0.5) / px_per_unit
    lon = frame.lon0 + (xs - frame.ox) / frame.s / frame.k
    lat = frame.lat0 - (ys - frame.oy) / frame.s / 60.0
    z = _z()
    k = 3600.0 / META["step_arcsec"]
    r = np.clip((META["north"] - lat) * k, 0, z.shape[0] - 1.001)[:, None] * np.ones((1, w))
    c = np.clip((lon - META["west"]) * k, 0, z.shape[1] - 1.001)[None, :] * np.ones((h, 1))
    r0, c0 = r.astype(int), c.astype(int)
    fr, fc = r - r0, c - c0
    g = z[r0, c0] * (1 - fr) * (1 - fc) + z[r0, c0 + 1] * (1 - fr) * fc + z[r0 + 1, c0] * fr * (1 - fc) + z[r0 + 1, c0 + 1] * fr * fc
    metres_per_px = 1852.0 / (frame.s * px_per_unit)
    gy, gx = np.gradient(g, metres_per_px)
    gx, gy = gx * exaggeration, gy * exaggeration
    lx, ly, lz = -0.6, -0.6, 0.53                                    # the light: from the upper left (north-west), about 32 degrees up
    shade = (-gx * lx - gy * ly + lz) / np.sqrt(gx * gx + gy * gy + 1.0) / math.sqrt(lx * lx + ly * ly + lz * lz)
    shade = np.clip(shade, 0.0, 1.0)
    t = np.clip((g - np.percentile(g, 2)) / max(np.percentile(g, 98) - np.percentile(g, 2), 1.0), 0, 1)
    ramp = [(0.0, (203, 178, 134)), (0.35, (218, 196, 152)), (0.7, (229, 211, 170)), (1.0, (239, 226, 192))]          # low ground a little darker and redder, high ground paler
    rgb = np.zeros((h, w, 3), dtype=np.float32)
    for (t0, c0_), (t1, c1_) in zip(ramp, ramp[1:]):
        m = (t >= t0) & (t <= t1)
        f = ((t - t0) / (t1 - t0))[m]
        for i in range(3):
            rgb[..., i][m] = c0_[i] + (c1_[i] - c0_[i]) * f
    light = 0.62 + 0.55 * shade                                       # 0.62 in full shadow to 1.17 facing the light
    rgb = np.clip(rgb * light[..., None], 0, 255)
    pale = np.array([244, 235, 211], dtype=np.float32)
    rgb = rgb * (1 - veil) + pale * veil
    im = Image.fromarray(rgb.astype(np.uint8))
    if soft:
        im = im.filter(ImageFilter.GaussianBlur(soft))
    os.makedirs(RENDERS, exist_ok=True)
    im.save(path)
    return path
