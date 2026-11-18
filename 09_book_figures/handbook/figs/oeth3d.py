"""3D views of Thumamah (OETH) for the handbook: the frame of the saudi-airspace scene (x east, y north, z up in metres, origin at the AIP aerodrome
reference point, z = 0 at 570 m AMSL, the field elevation), the runway frame of figs/h_b4.py mapped into it, and recipes for blender/render_oeth.py.

Not a figure itself. `python3 -m figs.oeth3d <name>` writes cache/oeth3d/<name>.json; render it with
    blender -b --factory-startup --python ../blender/render_oeth.py -- --recipe cache/oeth3d/<name>.json"""
import json
import math
import os
import sys

from figs import h_b4 as B

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARP = (25.2141667, 46.6408333)                          # AD 2 OETH 2.2


def local(lat, lon):
    return ((lon - ARP[1]) * 111320.0 * math.cos(math.radians(ARP[0])), (lat - ARP[0]) * 110574.0)


T17 = local(25.2310528, 46.6376833)                     # AD 2 OETH 2.12 (saudi-airspace data/structured/oeth.json)
T35 = local(25.1953639, 46.6440139)
_L = math.hypot(T35[0] - T17[0], T35[1] - T17[1])
V = ((T35[0] - T17[0]) / _L, (T35[1] - T17[1]) / _L)   # along the runway, north to south: s of the h_b4 frame
WEST = (V[1], -V[0])                                    # across, to the west of the runway: t of the h_b4 frame
FT = 0.3048
FIELD_FT = 1870.0


def xy(s, t):
    """A point of the h_b4 runway frame (s from the threshold of 17 toward 35, t to the west), in the scene."""
    s = s * _L / B.S_S
    return (T17[0] + s * V[0] + t * WEST[0], T17[1] + s * V[1] + t * WEST[1])


def z_ft(alt_ft):
    return (alt_ft - FIELD_FT) * FT


def heading(p, q):
    return math.degrees(math.atan2(q[0] - p[0], q[1] - p[1])) % 360.0


def circuit_heights(path):
    """Height above the field along the left-hand circuit of 35: climbing to 1 030 ft above it (2 900 ft AMSL) by the start of the downwind leg,
    level until abeam the threshold, then descending on the base leg and final."""
    m = path.marks
    ab = m["downwind"] + (B.S_S - (-700.0))
    top = z_ft(2900.0)
    knots = [(0.0, 0.0), (m["up_end"], 0.42 * top), (m["downwind"], top), (ab, top), (m["base_start"], 0.70 * top), (m["final"], 0.27 * top), (m["end"], 0.0)]

    def h(d):
        for (d0, z0), (d1, z1) in zip(knots, knots[1:]):
            if d <= d1:
                return z0 + (z1 - z0) * (d - d0) / max(d1 - d0, 1e-6)
        return knots[-1][1]
    return h, ab


def circuit_recipe(rid, camera, size=(2400, 1220), scale=30.0, D=1000.0, R=300.0):
    c = B.circuit35(D=D, R=R)
    h, ab = circuit_heights(c)
    pts = []
    d = 0.0
    while d < c.length:
        (s, t), _ = c.at(d)
        x, y = xy(s, t)
        pts.append([round(x, 1), round(y, 1), round(h(d) + 6.0, 1)])
        d += 40.0
    top = z_ft(2900.0)
    sm = 2000.0                                          # the middle of the downwind leg, where the 45 degree join meets it
    j0, j1 = xy(sm - 1500.0, D + 1500.0), xy(sm, D)
    l0 = xy(-700.0, 0.0)
    straight = [xy(-700.0, 0.0), xy(-2600.0, 0.0)]
    turn45 = [xy(-700.0, 0.0), xy(-1050.0, 120.0), xy(-2100.0, 1170.0)]
    m = c.marks

    def plane(dd, pitch=0.0, bank=0.0):
        (s, t), _ = c.at(dd)
        (s2, t2), _ = c.at(dd + 30.0)
        p, q = xy(s, t), xy(s2, t2)
        return {"at": [round(p[0], 1), round(p[1], 1), round(h(dd) + 6.0, 1)], "heading": round(heading(p, q), 1), "pitch": pitch, "bank": bank, "scale": scale}

    aircraft = [plane(m["up_end"] * 0.55, pitch=7.0), plane((m["cross_start"] + m["cross_end"]) / 2), plane(m["downwind"] + 1300.0),
                plane((m["base_start"] + m["base_end"]) / 2, pitch=-2.0), plane((m["final"] + m["end"]) / 2, pitch=-3.0)]

    def a3(s, t, d=None, z=None):
        x, y = xy(s, t)
        return [round(x, 1), round(y, 1), round(z if z is not None else (h(d) if d is not None else top), 1)]
    anchors = {
        "1": a3(-560.0, 0.0, z=0.36 * top), "2": a3(-1000.0, 520.0, z=0.62 * top), "3": a3(800.0, D), "4": a3(B.S_S + D + R, 330.0, z=0.55 * top),
        "5": a3(4500.0, 0.0, z=0.12 * top), "6": a3(sm - 900.0, D + 900.0), "7": a3(3300.0, D), "8": a3(B.S_S, D),
        "9": a3(B.S_S + D, D - R * 0.3, d=m["downwind_end"] + 120.0), "10": a3(-2100.0, 0.0, z=0.55 * top),
        "t35": a3(B.S_S, 0.0, z=0.0), "t17": a3(0.0, 0.0, z=0.0),
    }
    return {
        "id": rid, "camera": camera, "size": list(size), "samples": 96, "sun": {"elevation": 42, "azimuth": 120, "energy": 3.2}, "exposure": -0.3, "look": "AgX - High Contrast",
        "aircraft": aircraft,
        "paths": [{"points": pts, "colour": "#1D4ED8", "radius": 15.0, "arrows": 1100.0, "arrow_size": 85.0},
                  {"points": [[*j0, top + 6.0], [*j1, top + 6.0]], "colour": "#15803D", "radius": 13.0, "arrows": 1500.0, "arrow_size": 75.0},
                  {"points": [[*straight[0], 0.36 * top], [*straight[1], 0.66 * top]], "colour": "#C2410C", "radius": 12.0, "arrows": 1500.0, "arrow_size": 70.0},
                  {"points": [[*turn45[0], 0.36 * top], [*turn45[1], 0.42 * top], [*turn45[2], 0.66 * top]], "colour": "#C2410C", "radius": 12.0, "arrows": 1400.0, "arrow_size": 70.0}],
        "anchors": anchors,
    }


def runway_point(s, t=0.0):
    """A point s metres from the threshold of 17 along the runway (no h_b4 scaling), t to the west."""
    return (T17[0] + s * V[0] + t * WEST[0], T17[1] + s * V[1] + t * WEST[1])


RECIPES = {
    "oeth-18-07-circuit": lambda: circuit_recipe("oeth-18-07-circuit", {"at": [4700.0, -2300.0, 3300.0], "look": [-560.0, -480.0, 60.0], "lens": 30}),
}


if __name__ == "__main__":
    name = sys.argv[1]
    os.makedirs(os.path.join(HERE, "cache", "oeth3d"), exist_ok=True)
    out = os.path.join(HERE, "cache", "oeth3d", name + ".json")
    with open(out, "w") as f:
        json.dump(RECIPES[name](), f)
    print(out)
