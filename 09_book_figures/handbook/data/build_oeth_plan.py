"""Build data/oeth_plan.json, the ground plan of Thumamah (OETH) that Figure 18-1 and the other Thumamah pictures draw from.

Source: the saudi-airspace repository (scene/oeth): the runway, the stopways and the thresholds are the AIP's (AD 2.12, AMDT 11/26); the pavements (apron, links, turn loops), the buildings, the road and
the berm were traced by that project from satellite imagery (Esri World Imagery, capture 2024-12-21, stated accuracy 5 m, edges +/-10 m), and the parked aeroplanes are the ones its scene places.
This file holds the outlines (facts about the ground) only; no image pixels are copied. Coordinates are metres in the runway frame: s from the threshold of runway 17 towards the threshold of
runway 35 (southwards), t to the west of the centreline.   python3 build_oeth_plan.py [/path/to/saudi-airspace]    Not for navigation.
"""
import importlib.util
import json
import math
import os
import sys

SRC = sys.argv[1] if len(sys.argv) > 1 else "/workspace/saudi-airspace"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "oeth_plan.json")
sys.path.insert(0, os.path.join(SRC, "scripts"))
spec = importlib.util.spec_from_file_location("oeth_site", os.path.join(SRC, "scene/oeth/blender/oeth/site.py"))
S = importlib.util.module_from_spec(spec)
sys.modules["oeth_site"] = S
spec.loader.exec_module(S)


def inside(pt, poly):
    x, y = pt
    c = False
    for i in range(len(poly)):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % len(poly)]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            c = not c
    return c


def r1(v):
    return round(v, 1)


rf_ring = lambda pts: [[r1(t), r1(s)] for t, s in (S.to_rf(x, y) for x, y in pts)]
pav = S.pavements()
isl = [(n, [S.to_rf(x, y) for x, y in p]) for n, _, p in S.islands()]
pavements = []
for name, kind, status, poly in pav:
    ring = [S.to_rf(x, y) for x, y in poly]
    holes = [[[r1(t), r1(s)] for t, s in ip] for n, ip in isl if inside((sum(q[0] for q in ip) / len(ip), sum(q[1] for q in ip) / len(ip)), ring)]
    pavements.append({"name": name, "surface": kind, "status": status, "ring": [[r1(t), r1(s)] for t, s in ring], "holes": holes})
buildings = []
for f in S.footprints():
    L, W, rot = f["length"], f["width"], f["rot"]
    n = (-math.sin(rot), math.cos(rot))
    e = (math.cos(rot), math.sin(rot))
    cx, cy = f["x"], f["y"]
    corners = [(cx + a * (L / 2) * n[0] + b * (W / 2) * e[0], cy + a * (L / 2) * n[1] + b * (W / 2) * e[1]) for a, b in ((1, 1), (1, -1), (-1, -1), (-1, 1))]
    buildings.append({"id": f["id"], "roof": f["roof"], "height_m_estimated": f["height"], "ring": rf_ring(corners)})
lines = {fid: [[r1(t), r1(s)] for t, s in (S.to_rf(x, y) for x, y in S.feature_line_xy(fid))] for fid in ("EAST_BERM", "ACCESS_ROAD")}
north = [S.to_rf(0, 1)[0] - S.to_rf(0, 0)[0], S.to_rf(0, 1)[1] - S.to_rf(0, 0)[1]]
parked = [[265, 330, 1], [265, 350, 1], [265, 370, 1], [265, 390, 1], [265, 410, 1], [205, 1478, 1], [190, 1612, 2], [180, 1640, 1], [205, 1652, 2], [250, 1268, 1]]
out = {
    "provenance": {"runway": "AIP AD 2.12 (AMDT 11/26): 4000 x 50 m, true bearing 171/351; stopways 300 m (north of THR 17) and 60 m (south of THR 35)",
                   "traced": "pavements, buildings, road and berm: traced by the saudi-airspace project from satellite imagery (Esri World Imagery, 2024-12-21), edges +/-10 m; outlines only",
                   "parked": "positions of the parked aeroplanes in the project's scene (t, s, heading 1 = nose north, 2 = nose south)",
                   "frame": "metres in the runway frame: s from THR 17 towards THR 35 (south), t to the west of the centreline"},
    "runway": {"length_m": 4000, "width_m": 50, "true_deg_17": 171.0, "stopway_north_m": 300, "stopway_south_m": 60, "north_in_ts_per_m": [round(north[0], 4), round(north[1], 4)]},
    "pavements": pavements, "buildings": buildings, "lines": lines, "parked_aeroplanes": parked,
}
json.dump(out, open(OUT, "w"), separators=(",", ":"))
print("wrote", OUT, os.path.getsize(OUT), "bytes;", len(pavements), "pavements,", len(buildings), "buildings; north in (t, s):", out["runway"]["north_in_ts_per_m"])
