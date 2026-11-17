"""Fetch the ground under a route from open elevation data and write what the figures draw: the ground under the line and the highest ground within a few nautical miles of it.

Source: NASA Shuttle Radar Topography Mission (SRTM), 1 arc-second, public domain, as the HGT tiles of the "Terrain Tiles" open dataset on AWS (s3://elevation-tiles-prod/skadi/).
Only the tiles the corridor touches are read, and only the numbers below are kept (the tiles themselves are not): for every `STEP_NM` along the great circle, the elevation on the line
and the highest elevation within `HALF_NM` of it, to the nearest foot.   -> oerk_oejn_profile.json     Needs numpy and network access.
    python fetch_route_terrain.py           Not for navigation: a radar survey of 2000, 30 m samples; it shows the shape of the ground, not obstacles.
"""
import gzip
import json
import math
import os
import urllib.request

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
FROM = ("OERK", 24.9627778, 46.7080556)           # the reference points of AD 2 OERK and OEJN (data/saudi_airspace.json)
TO = ("OEJN", 21.6811111, 39.1561111)
STEP_NM, HALF_NM = 1.0, 10.0
FT = 3.280839895
R_NM = 3440.065


def gc(p, q, f):
    la1, lo1, la2, lo2 = map(math.radians, (p[0], p[1], q[0], q[1]))
    d = 2 * math.asin(math.sqrt(math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2))
    a, b = math.sin((1 - f) * d) / math.sin(d), math.sin(f * d) / math.sin(d)
    x = a * math.cos(la1) * math.cos(lo1) + b * math.cos(la2) * math.cos(lo2)
    y = a * math.cos(la1) * math.sin(lo1) + b * math.cos(la2) * math.sin(lo2)
    z = a * math.sin(la1) + b * math.sin(la2)
    return math.degrees(math.atan2(z, math.hypot(x, y))), math.degrees(math.atan2(y, x)), d * R_NM


def bearing(p, q):
    la1, lo1, la2, lo2 = map(math.radians, (p[0], p[1], q[0], q[1]))
    return math.degrees(math.atan2(math.sin(lo2 - lo1) * math.cos(la2), math.cos(la1) * math.sin(la2) - math.sin(la1) * math.cos(la2) * math.cos(lo2 - lo1))) % 360


TILES = {}


def tile(lat, lon):
    key = (lat, lon)
    if key not in TILES:
        name = f"{'N' if lat >= 0 else 'S'}{abs(lat):02d}{'E' if lon >= 0 else 'W'}{abs(lon):03d}"
        url = f"https://s3.amazonaws.com/elevation-tiles-prod/skadi/{name[:3]}/{name}.hgt.gz"
        raw = gzip.decompress(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "handbook-figure-builder/1.0"}), timeout=240).read())
        TILES[key] = np.frombuffer(raw, dtype=">i2").reshape(3601, 3601)
        print("tile", name, flush=True)
    return TILES[key]


def elev_m(lat, lon):
    la, lo = math.floor(lat), math.floor(lon)
    a = tile(la, lo)
    r, c = (la + 1 - lat) * 3600.0, (lon - lo) * 3600.0
    r0, c0 = min(int(r), 3599), min(int(c), 3599)
    fr, fc = r - r0, c - c0
    v = a[r0:r0 + 2, c0:c0 + 2].astype(np.float64)
    v[v < -1000] = 0.0                                    # voids
    return float(v[0, 0] * (1 - fr) * (1 - fc) + v[0, 1] * (1 - fr) * fc + v[1, 0] * fr * (1 - fc) + v[1, 1] * fr * fc)


def main():
    p, q = FROM[1:], TO[1:]
    _, _, total = gc(p, q, 1.0 - 1e-12)
    n = int(total // STEP_NM) + 1
    rows = []
    for i in range(n + 1):
        d = min(i * STEP_NM, total)
        lat, lon, _ = gc(p, q, d / total)
        la2, lo2, _ = gc(p, q, min(d + 0.05, total) / total)
        brg = bearing((lat, lon), (la2, lo2)) if d < total else bearing(p, q)
        centre = elev_m(lat, lon) * FT
        high = centre
        for off in np.arange(-HALF_NM, HALF_NM + 0.01, 1.0):             # across the line, every nautical mile
            for al in np.arange(-0.5, 0.51, 0.25):                       # and a little along it, so the 1 NM steps leave no gap
                ang = math.radians(brg + 90.0)
                dlat = (off * math.cos(ang) + al * math.cos(math.radians(brg))) / 60.0
                dlon = (off * math.sin(ang) + al * math.sin(math.radians(brg))) / 60.0 / math.cos(math.radians(lat))
                high = max(high, elev_m(lat + dlat, lon + dlon) * FT)
        rows.append([round(d, 2), round(centre), round(high)])
    out = {"source": "NASA Shuttle Radar Topography Mission (SRTM), 1 arc-second, from the Terrain Tiles open dataset on AWS (skadi HGT tiles)", "licence": "SRTM data are in the public domain",
           "attribution": "Elevation: NASA SRTM", "from": {"icao": FROM[0], "lat": FROM[1], "lon": FROM[2]}, "to": {"icao": TO[0], "lat": TO[1], "lon": TO[2]},
           "great_circle_nm": round(total, 1), "true_course_start": round(bearing(p, q), 1), "true_course_end": round((bearing(q, p) + 180) % 360, 1),
           "step_nm": STEP_NM, "half_width_nm": HALF_NM, "units": "feet above mean sea level (EGM96)", "columns": ["nm from the start", "ground on the line", "highest ground within half_width_nm"],
           "profile": rows}
    with open(os.path.join(HERE, "oerk_oejn_profile.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
        f.write("\n")
    print(out["great_circle_nm"], "NM", out["true_course_start"], out["true_course_end"], "max", max(r[2] for r in rows))


if __name__ == "__main__":
    main()
