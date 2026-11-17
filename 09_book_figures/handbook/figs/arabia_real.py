"""The Arabian peninsula and the globe from open data, and the cone of the AIP's charts: the parts of figs/f_20_02_chart_projection.py that are geometry and ground.

    Cone(lat1, lat2, lon0, lat0)   a Lambert conformal conic on the WGS 84 ellipsoid (Snyder, Map Projections: A Working Manual, USGS Professional Paper 1395, 1987, equations 15-1 to 15-11)
    CONE                            the cone of the AIP's visual charts of the Kingdom: the standard parallels printed on every sheet, 25°20' and 30°40' N (data/saudi_airspace.json, "charts")
        .n                          its constant: the meridians of the chart close by n degrees for each degree of longitude
        .xy(lat, lon)               metres on the chart: x to the right and y up from the point where the central meridian crosses the parallel of origin
        .lat_lon(x, y)              back again
        .scale(lat)                 the scale along a parallel against the stated scale (1 on the two standard parallels)
        .slant(lat)                 how far the parallel lies from the apex along the cone, in earth radii (the cone as a solid in space: half-angle asin(n))
    great_circle(p, q, k)           k + 1 points of the shortest line between two places, on the sphere
    Ortho(lat, lon, r, cx, cy)      the globe seen from far away, the place (lat, lon) in the middle of the disc: .xy(lat, lon) -> (x, y, facing), .space(X, Y, Z) for a point given in earth radii
    ensure_chart(name, ...)         the land (its relief) and the sea in the chart, written to renders/<name>.png once (a sprite to lay under the drawing)
    ensure_globe(name, ...)         the globe, lit, written to renders/<name>.png once
    sprite_box(name)                where such a picture lies on its canvas: the sprite entry of a re-skin

The ground is Natural Earth's shaded relief and land (public domain; data/open/fetch_arabia_open.py): coasts, and no boundaries between countries. numpy and Pillow only. Not for navigation."""
import json
import math
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OPEN = os.path.join(os.path.dirname(HERE), "data", "open")
RENDERS = os.path.join(os.path.dirname(HERE), "renders")
with open(os.path.join(OPEN, "arabia_open.json"), encoding="utf-8") as _f:
    META = json.load(_f)
ATTRIBUTION = META["attribution"]
A_WGS, F_WGS = 6378137.0, 1 / 298.257223563
E_WGS = math.sqrt(F_WGS * (2 - F_WGS))
R_SPHERE = 6371008.8
NM = 1852.0


def _m(phi):
    return np.cos(phi) / np.sqrt(1 - (E_WGS * np.sin(phi)) ** 2)


def _t(phi):
    s = E_WGS * np.sin(phi)
    return np.tan(np.pi / 4 - phi / 2) / ((1 - s) / (1 + s)) ** (E_WGS / 2)


class Cone:
    def __init__(self, lat1, lat2, lon0, lat0):
        p1, p2 = math.radians(lat1), math.radians(lat2)
        self.lat1, self.lat2, self.lon0, self.lat0 = lat1, lat2, lon0, lat0
        self.n = float((math.log(_m(p1)) - math.log(_m(p2))) / (math.log(_t(p1)) - math.log(_t(p2))))
        self.F = float(_m(p1) / (self.n * _t(p1) ** self.n))
        self.rho0 = float(self.rho(lat0))

    def rho(self, lat):
        """The radius of a parallel on the chart, metres (its distance from the apex of the cone)."""
        return A_WGS * self.F * _t(np.radians(lat)) ** self.n

    def xy(self, lat, lon):
        rho, theta = self.rho(lat), self.n * np.radians(np.asarray(lon, dtype=float) - self.lon0)
        return rho * np.sin(theta), self.rho0 - rho * np.cos(theta)

    def lat_lon(self, x, y):
        x, y = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
        rho = np.hypot(x, self.rho0 - y)
        t = (rho / (A_WGS * self.F)) ** (1 / self.n)
        phi = np.pi / 2 - 2 * np.arctan(t)
        for _ in range(6):
            s = E_WGS * np.sin(phi)
            phi = np.pi / 2 - 2 * np.arctan(t * ((1 - s) / (1 + s)) ** (E_WGS / 2))
        return np.degrees(phi), self.lon0 + np.degrees(np.arctan2(x, self.rho0 - y)) / self.n

    def scale(self, lat):
        return self.rho(lat) * self.n / (A_WGS * _m(np.radians(lat)))

    def slant(self, lat):
        return self.rho(lat) / A_WGS

    def bearing(self, p, q, lon):
        """The angle, clockwise from the meridian of `lon`, of the straight chart line from p to q (each (lat, lon)): its true direction where it crosses that meridian."""
        (x0, y0), (x1, y1) = self.xy(*p), self.xy(*q)
        grid = math.degrees(math.atan2(x1 - x0, y1 - y0))
        return (grid + self.n * (lon - self.lon0)) % 360.0


with open(os.path.join(os.path.dirname(HERE), "data", "saudi_airspace.json"), encoding="utf-8") as _f:
    FACTS = json.load(_f)
CHARTS = FACTS["charts"]
CONE = Cone(CHARTS["projection"]["standard_parallels_deg"][0], CHARTS["projection"]["standard_parallels_deg"][1], 45.0, 24.0)


def _unit(lat, lon):
    la, lo = math.radians(lat), math.radians(lon)
    return np.array([math.cos(la) * math.cos(lo), math.cos(la) * math.sin(lo), math.sin(la)])


def great_circle(p, q, k=64):
    """k + 1 places (lat, lon) along the shortest line from p to q on the sphere, and its length in NM."""
    a, b = _unit(*p), _unit(*q)
    w = math.acos(float(np.clip(a @ b, -1, 1)))
    out = []
    for i in range(k + 1):
        f = i / k
        v = (math.sin((1 - f) * w) * a + math.sin(f * w) * b) / math.sin(w)
        out.append((math.degrees(math.asin(v[2])), math.degrees(math.atan2(v[1], v[0]))))
    return out, w * R_SPHERE / NM


def initial_course(p, q):
    """The true direction in which the great circle from p leaves towards q, degrees."""
    la1, la2, dl = math.radians(p[0]), math.radians(q[0]), math.radians(q[1] - p[1])
    return math.degrees(math.atan2(math.sin(dl) * math.cos(la2), math.cos(la1) * math.sin(la2) - math.sin(la1) * math.cos(la2) * math.cos(dl))) % 360.0


class Ortho:
    """The globe from far away. Space: earth radii, Z to the north pole, X to (0 N, the middle meridian + 90), seen so that the place (lat, lon) is in the middle of the disc."""

    def __init__(self, lat, lon, r, cx, cy):
        self.lat, self.lon, self.r, self.cx, self.cy = lat, lon, r, cx, cy
        self.sb, self.cb = math.sin(math.radians(lat)), math.cos(math.radians(lat))

    def space(self, X, Y, Z):
        """Canvas x, y and the depth towards the eye of a point in space (X to the right of the middle meridian's plane, Y away from the eye along the equator plane, Z north)."""
        return self.cx + self.r * X, self.cy - self.r * (Z * self.cb + Y * self.sb), -Y * self.cb + Z * self.sb

    def xy(self, lat, lon, radius=1.0):
        la, dl = math.radians(lat), math.radians(lon - self.lon)
        return self.space(radius * math.cos(la) * math.sin(dl), -radius * math.cos(la) * math.cos(dl), radius * math.sin(la))


def sprite_box(name, px_per_unit=4):
    """Where a picture made here lies on its canvas, as the re-skin wants a sprite: {"name", "at", "width"}. build_plates.py crops every sprite to what is not clear in it
    and puts the middle of that on "at", "width" canvas units wide, so the middle and the width of the same crop are given here."""
    alpha = Image.open(os.path.join(RENDERS, name + ".png")).getchannel("A").point(lambda v: 255 if v > 8 else 0)
    x0, y0, x1, y1 = alpha.getbbox()
    return {"name": name, "at": [(x0 + x1) / 2 / px_per_unit, (y0 + y1) / 2 / px_per_unit], "width": (x1 - x0) / px_per_unit}


def _sample(img, rows, cols):
    """Bilinear samples of a grey picture at fractional rows and columns (clamped)."""
    r = np.clip(rows, 0, img.shape[0] - 1.001)
    c = np.clip(cols, 0, img.shape[1] - 1.001)
    r0, c0 = r.astype(int), c.astype(int)
    fr, fc = r - r0, c - c0
    return img[r0, c0] * (1 - fr) * (1 - fc) + img[r0, c0 + 1] * (1 - fr) * fc + img[r0 + 1, c0] * fr * (1 - fc) + img[r0 + 1, c0 + 1] * fr * fc


_PICTURES = {}


def _grid(name):
    if name not in _PICTURES:
        relief = np.asarray(Image.open(os.path.join(OPEN, f"{name}_relief.jpg")).convert("L"), dtype=np.float32)
        land = np.asarray(Image.open(os.path.join(OPEN, f"{name}_land.png")).convert("L"), dtype=np.float32) / 255.0
        _PICTURES[name] = (relief, land, META["grids"][name])
    return _PICTURES[name]


def _ground(name, lat, lon):
    """The relief (0 to 255) and the share of land (0 to 1) at arrays of places, and whether the grid covers them."""
    relief, land, g = _grid(name)
    per = g["pixels_per_degree"]
    rows, cols = (g["north"] - lat) * per - 0.5, (lon - g["west"]) * per - 0.5
    inside = (lat <= g["north"]) & (lat >= g["south"]) & (lon >= g["west"]) & (lon <= g["east"])
    return _sample(relief, rows, cols), _sample(land, rows, cols), inside


LAND = np.array([238, 224, 190], dtype=np.float32)          # the paper of a chart: pale sand
SEA = np.array([176, 208, 233], dtype=np.float32)
COAST = np.array([74, 112, 150], dtype=np.float32)


def _paint(shade, land, strength=1.0):
    """Land and sea in the colours of a printed chart: the relief darkens and lightens the land, the coast is a thin darker line."""
    s = np.clip(1.0 + (shade - 218.0) / 150.0 * strength, 0.5, 1.12)[..., None]
    rgb = LAND * s * land[..., None] + SEA * (1 - land[..., None])
    edge = np.clip(1 - np.abs(land - 0.5) * 2.4, 0, 1)[..., None] ** 2                          # strongest where the mask is half land
    return rgb * (1 - 0.55 * edge) + COAST * 0.55 * edge


def ensure_chart(name, cone, canvas, scale, origin, west, east, south, north, px_per_unit=4, strength=1.0):
    """The chart of a cone on a canvas of (w, h) units: `scale` units to the metre, the chart's origin at the canvas point `origin`; everything outside the fan
    between the meridians west and east and the parallels south and north is left clear."""
    path = os.path.join(RENDERS, name + ".png")
    if os.path.exists(path):
        return path
    w, h = int(round(canvas[0] * px_per_unit)), int(round(canvas[1] * px_per_unit))
    u = (np.arange(w) + 0.5) / px_per_unit
    v = (np.arange(h) + 0.5) / px_per_unit
    x = ((u - origin[0]) / scale)[None, :] * np.ones((h, 1))
    y = ((origin[1] - v) / scale)[:, None] * np.ones((1, w))
    lat, lon = cone.lat_lon(x, y)
    shade, land, _ = _ground("arabia", lat, lon)
    rgb = _paint(shade, land, strength)
    feather = 0.03                                                                              # degrees: the edge of the sheet, softened by a pixel or two
    alpha = np.clip((lon - west) / feather, 0, 1) * np.clip((east - lon) / feather, 0, 1) * np.clip((lat - south) / feather, 0, 1) * np.clip((north - lat) / feather, 0, 1)
    out = np.dstack([np.clip(rgb, 0, 255), alpha * 255]).astype(np.uint8)
    os.makedirs(RENDERS, exist_ok=True)
    Image.fromarray(out, "RGBA").save(path)
    return path


def ensure_globe(name, view, canvas, px_per_unit=4, light=(-0.45, 0.55, 0.70)):
    """The globe of `view` (an Ortho) on a canvas of (w, h) units, lit from the upper left, with a thin blue rim of air; clear outside the disc."""
    path = os.path.join(RENDERS, name + ".png")
    if os.path.exists(path):
        return path
    w, h = int(round(canvas[0] * px_per_unit)), int(round(canvas[1] * px_per_unit))
    u = ((np.arange(w) + 0.5) / px_per_unit - view.cx) / view.r
    v = (view.cy - (np.arange(h) + 0.5) / px_per_unit) / view.r
    sx = u[None, :] * np.ones((h, 1))
    sy = v[:, None] * np.ones((1, w))
    rr = sx * sx + sy * sy
    sz = np.sqrt(np.clip(1 - rr, 0, None))                                                      # towards the eye
    z_north = sy * view.cb + sz * view.sb                                                       # turn the picture back into the earth's own axes
    y_away = sy * view.sb - sz * view.cb
    lat = np.degrees(np.arcsin(np.clip(z_north, -1, 1)))
    lon = view.lon + np.degrees(np.arctan2(sx, -y_away))
    shade, land, inside = _ground("globe", lat, lon)
    land = np.where(inside, land, 0.0)
    rgb = _paint(np.where(inside, shade, 218.0), land, 1.25)
    sea = np.array([58, 118, 196], dtype=np.float32)                                            # the sea of a globe is deeper than the sea of a chart
    rgb = rgb * land[..., None] + sea * (1 - land[..., None])
    lx, ly, lz = (c / math.sqrt(sum(k * k for k in light)) for c in light)
    lit = np.clip(sx * lx + sy * ly + sz * lz, 0, 1)
    rgb = rgb * (0.42 + 0.72 * lit)[..., None]
    glint = np.clip(sx * lx + sy * ly + sz * lz, 0, 1) ** 26                                    # a soft highlight on the sea
    rgb = rgb + (255 - rgb) * (0.34 * glint * (1 - 0.7 * land))[..., None]
    air = np.clip((np.sqrt(rr) - 0.86) / 0.14, 0, 1) ** 2                                       # the limb: a little blue air
    rgb = rgb * (1 - 0.5 * air[..., None]) + np.array([150, 196, 255], dtype=np.float32) * 0.5 * air[..., None]
    alpha = np.clip((1 - np.sqrt(rr)) * view.r * px_per_unit + 0.5, 0, 1)
    out = np.dstack([np.clip(rgb, 0, 255), alpha * 255]).astype(np.uint8)
    os.makedirs(RENDERS, exist_ok=True)
    Image.fromarray(out, "RGBA").save(path)
    return path
