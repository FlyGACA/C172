"""A real picture of the country round Thumamah to lay under a map: the open satellite imagery of data/open/oeth_area_s2.jpg (Copernicus Sentinel-2, 10 m to the pixel,
fetched by data/open/fetch_oeth_area_open.py). Every use carries the attribution "Contains modified Copernicus Sentinel data 2026". numpy and Pillow only.

    covers(frame, canvas)                 whether the picture covers the whole map of a frame (figs/h_b2.Frame) on a canvas of (w, h) units
    ensure(name, frame, canvas, ...)      the picture resampled into that map (north up, the frame's flat projection), written to renders/<name>.png once, to lay as a sprite under it

The picture lies in the grid of UTM zone 38 N; the maps of the figures have true north up, half a degree and more away from grid north here, so every point of the map is taken through
the projection (a short series, good to a millimetre) and not by a shift. Not for navigation: a picture of the ground on a few mornings of 2026."""
import json
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OPEN = os.path.join(os.path.dirname(HERE), "data", "open")
RENDERS = os.path.join(os.path.dirname(HERE), "renders")
with open(os.path.join(OPEN, "oeth_area_s2.json"), encoding="utf-8") as _f:
    META = json.load(_f)
ATTRIBUTION = META["attribution"]
_PICTURE = None


def _picture():
    global _PICTURE
    if _PICTURE is None:
        _PICTURE = np.asarray(Image.open(os.path.join(OPEN, "oeth_area_s2.jpg")).convert("RGB"), dtype=np.float32)
    return _PICTURE


def utm38(lat, lon):
    """WGS 84 to UTM zone 38 N (EPSG:32638) for arrays of degrees: the Krueger series to n^3."""
    a, f, k0, lon0 = 6378137.0, 1 / 298.257223563, 0.9996, np.radians(45.0)
    n = f / (2 - f)
    big_a = a / (1 + n) * (1 + n * n / 4 + n ** 4 / 64)
    al = (n / 2 - 2 * n * n / 3 + 5 * n ** 3 / 16, 13 * n * n / 48 - 3 * n ** 3 / 5, 61 * n ** 3 / 240)
    phi, lam = np.radians(lat), np.radians(lon) - lon0
    e = 2 * np.sqrt(n) / (1 + n)
    t = np.sinh(np.arctanh(np.sin(phi)) - e * np.arctanh(e * np.sin(phi)))
    xi, eta = np.arctan2(t, np.cos(lam)), np.arctanh(np.sin(lam) / np.sqrt(1 + t * t))
    east = 500000 + k0 * big_a * (eta + sum(al[j] * np.cos(2 * (j + 1) * xi) * np.sinh(2 * (j + 1) * eta) for j in range(3)))
    north = k0 * big_a * (xi + sum(al[j] * np.sin(2 * (j + 1) * xi) * np.cosh(2 * (j + 1) * eta) for j in range(3)))
    return east, north


def _rows_cols(frame, canvas, px_per_unit):
    """For every pixel of the map: where it lies in the picture (row, column; fractions of a pixel, the centre of the first pixel at 0)."""
    w, h = int(round(canvas[0] * px_per_unit)), int(round(canvas[1] * px_per_unit))
    xs = (np.arange(w) + 0.5) / px_per_unit
    ys = (np.arange(h) + 0.5) / px_per_unit
    lon = (frame.lon0 + (xs - frame.ox) / frame.s / frame.k)[None, :] * np.ones((h, 1))
    lat = (frame.lat0 - (ys - frame.oy) / frame.s / 60.0)[:, None] * np.ones((1, w))
    east, north = utm38(lat, lon)
    e0, _, _, n1 = META["bounds_e_n_min_e_n_max"]
    px = META["pixel_m"]
    return (n1 - north) / px - 0.5, (east - e0) / px - 0.5


def covers(frame, canvas):
    rows, cols = _rows_cols(frame, canvas, 0.25)
    wide, high = META["size_px"]
    return bool(rows.min() >= 0 and cols.min() >= 0 and rows.max() <= high - 1 and cols.max() <= wide - 1)


def ensure(name, frame, canvas, px_per_unit=4, veil=0.14, saturation=0.9, lift=1.06):
    """The picture in the map of `frame` on a canvas of (w, h) units, a little paler (`veil` towards a pale sand), a little less coloured and a little lighter, so that
    the lines drawn over it read; where the map leaves the picture the ground is the pale sand."""
    path = os.path.join(RENDERS, name + ".png")
    if os.path.exists(path):
        return path
    pic = _picture()
    rows, cols = _rows_cols(frame, canvas, px_per_unit)
    inside = (rows >= 0) & (cols >= 0) & (rows <= pic.shape[0] - 1) & (cols <= pic.shape[1] - 1)
    r = np.clip(rows, 0, pic.shape[0] - 1.001)
    c = np.clip(cols, 0, pic.shape[1] - 1.001)
    r0, c0 = r.astype(int), c.astype(int)
    fr, fc = (r - r0)[..., None], (c - c0)[..., None]
    rgb = pic[r0, c0] * (1 - fr) * (1 - fc) + pic[r0, c0 + 1] * (1 - fr) * fc + pic[r0 + 1, c0] * fr * (1 - fc) + pic[r0 + 1, c0 + 1] * fr * fc
    grey = rgb.mean(axis=2, keepdims=True)
    rgb = (grey + (rgb - grey) * saturation) * lift
    pale = np.array([244, 235, 211], dtype=np.float32)
    rgb = rgb * (1 - veil) + pale * veil
    rgb[~inside] = pale
    os.makedirs(RENDERS, exist_ok=True)
    Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8)).save(path)
    return path
