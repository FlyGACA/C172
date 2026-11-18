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


# What the book takes from the saudi-airspace scene: the AIP's runway and obstacles, the ICAO markings, the SRTM terrain and the PAPI placed from
# the AIP (statuses of its scene_index.json). Its pavements, buildings and compounds are traced from Esri World Imagery, whose licence the
# book's open ground plan avoids, so they are left out and the plan of data/oeth_plan.json (open Sentinel-2 imagery) is built instead.
KEEP_SOURCES = ["aip", "icao_standard", "srtm", "estimated"]


def open_plan():
    """The ground plan of figs/h_b4.py (data/oeth_plan.json, rings as [t, s]) in the scene frame: pavements, sand islands, roofs and the road."""
    def ring(r):
        return [[round(c, 2) for c in xy(s, t)] for t, s in r]
    return {
        "pavements": [{"name": p["name"], "zone": p["zone"], "ring": ring(p["ring"]), "holes": [ring(h) for h in p["holes"]]} for p in B.PLAN["pavements"]],
        "islands": [{"ring": ring(r)} for r in B.PLAN["islands"]],
        "buildings": [{"name": b["id"], "ring": ring(b["ring"]), "height": b["height_m_estimated"]} for b in B.PLAN["buildings"]],
        "roads": [{"points": ring(pts), "width": 9.0} for pts in B.PLAN["lines"].values()],
    }


def nearest_d(c, s, t):
    """The distance along circuit c of its point nearest to (s, t) of the runway frame."""
    best, d = (1e18, 0.0), 0.0
    while d < c.length:
        (cs, ct), _ = c.at(d)
        e = (cs - s) ** 2 + (ct - t) ** 2
        if e < best[0]:
            best = (e, d)
        d += 5.0
    return best[1]


def circuit_recipe(rid, camera, size=(2400, 1220), scale=30.0, D=1000.0, R=300.0, join_leave=True, extra_anchors=None, extra_paths=None):
    """The left-hand circuit of runway 35 in the scene. extra_anchors: {name: (s, t) | (s, t, "ground")}: points of the runway frame, at the circuit's height
    there (on the ground with "ground"); extra_paths: more tubes (a wind arrow, say), in the scene frame."""
    c = B.circuit35(D=D, R=R)
    h, _ = circuit_heights(c)
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
        "n0": [0.0, 0.0, 0.0], "n1": [0.0, 800.0, 0.0],     # the aerodrome reference point and a point 800 m north of it: north in the picture
    }
    for k, v in (extra_anchors or {}).items():
        anchors[k] = a3(v[0], v[1], z=0.0) if len(v) > 2 and v[2] == "ground" else a3(v[0], v[1], d=nearest_d(c, v[0], v[1]))
    paths = [{"points": pts, "colour": "#1D4ED8", "radius": 15.0, "arrows": 1100.0, "arrow_size": 85.0}]
    if join_leave:
        paths += [{"points": [[*j0, top + 6.0], [*j1, top + 6.0]], "colour": "#15803D", "radius": 13.0, "arrows": 1500.0, "arrow_size": 75.0},
                  {"points": [[*straight[0], 0.36 * top], [*straight[1], 0.66 * top]], "colour": "#C2410C", "radius": 12.0, "arrows": 1500.0, "arrow_size": 70.0},
                  {"points": [[*turn45[0], 0.36 * top], [*turn45[1], 0.42 * top], [*turn45[2], 0.66 * top]], "colour": "#C2410C", "radius": 12.0, "arrows": 1400.0, "arrow_size": 70.0}]
    paths += list(extra_paths or [])
    return {
        "id": rid, "camera": camera, "size": list(size), "samples": 96, "sun": {"elevation": 42, "azimuth": 120, "energy": 3.2}, "exposure": -0.3, "look": "AgX - High Contrast",
        "keep_sources": KEEP_SOURCES, "plan": open_plan(),
        "aircraft": aircraft,
        "paths": paths,
        "anchors": anchors,
    }


def runway_point(s, t=0.0):
    """A point s metres from the threshold of 17 along the runway (no h_b4 scaling), t to the west."""
    return (T17[0] + s * V[0] + t * WEST[0], T17[1] + s * V[1] + t * WEST[1])


def circuit_26_02():
    """Figure 26-2: the same circuit and view as 18-7 without the join and the ways of leaving; the points of its tags and callouts, and the wind from
    the north as two pale arrows blowing south high over the far side of the circuit."""
    S_LINEUP, S_ROTATE, S_AIM = 3975.0, 3275.0, 3694.6
    D = B.DOWNWIND
    pts = {"lineup": (S_LINEUP, 0.0, "ground"), "rotate": (S_ROTATE, 0.0, "ground"), "aim": (S_AIM, 0.0, "ground"), "climb": (-500.0, 0.0), "cross": (-1000.0, 360.0),
           "down": (900.0, D), "abeam": (B.S_S, D), "base": (B.S_S + D + B.CORNER, 330.0), "final": (4850.0, 0.0)}
    z = z_ft(2900.0) + 450.0                             # the wind: two pale arrows 450 m above the circuit, west of it, pointing true south
    wind = []
    for k, (s0, t0) in enumerate(((700.0, 1500.0), (1700.0, 1800.0))):
        x, y = runway_point(s0, t0)
        wind.append({"points": [[x, y + 700.0, z + 250.0 * k], [x, y - 700.0, z + 250.0 * k]], "colour": "#7FA3D6", "radius": 22.0, "end_arrow": True, "arrow_size": 120.0})
        pts[f"wind{k}"] = None
        anchors_wind = (x, y + 700.0, z + 250.0 * k)
    pts.pop("wind0"); pts.pop("wind1")
    pts_xyz = {"wind": list(anchors_wind)}
    r = circuit_recipe("oeth-26-02-circuit", {"at": [4700.0, -2300.0, 3300.0], "look": [-560.0, -480.0, 60.0], "lens": 30}, join_leave=False, extra_anchors=pts, extra_paths=wind)
    r["anchors"].update(pts_xyz)
    return r


def _air_data():
    with open(os.path.join(HERE, "data", "saudi_airspace.json"), encoding="utf-8") as f:
        return json.load(f)


NM = 1852.0


def airspace_17_01(k=5.0):
    """Figure 17-1, the 3D view: the blocks of airspace between Thumamah and Riyadh from data/saudi_airspace.json (AIP AMDT 11/26), seen from the
    west-south-west so that north is on the left, as in the section below it. Heights (of the ground too) are drawn k times their scale. The Thumamah
    ATZ (Class G, SFC to 3 000 ft), the Riyadh CTR (Class D, SFC to 4 500 ft), the final director area for 15L (Class C, 700 ft above the ground to
    11 000 ft, excluding the CTR) and the floor of the Riyadh East TMA part 1 (Class C from 700 ft above the ground, excluding the CTR and the ATZ);
    the runways of King Khaled; a VFR aeroplane under the floor of the terminal area; the line of the section, dashed on the ground. The ground itself is
    left flat at the aerodrome's elevation (no SRTM tile: the ground here is nearly flat, and the tile's edge would show); only the airspace and the
    aeroplane's height are exaggerated."""
    d = _air_data()
    A = d["areas"]

    def ring(lonlat):
        return [[round(c, 1) for c in local(lat, lon)] for lon, lat in lonlat]

    def z(ft):                                           # feet AMSL -> scene height, exaggerated
        return round((ft - FIELD_FT) * FT * k, 1)
    agl700 = {"agl": round(700.0 * FT * k, 1)}
    vols = [
        {"name": "ATZ", "ring": ring(A["oeth_atz_ring"]), "floor": -30.0, "ceiling": z(3000.0), "colour": "#16A34A", "alpha": 0.42, "edge": 80.0},
        {"name": "CTR", "ring": ring(A["oerk_ctr_ring"]), "floor": -30.0, "ceiling": z(4500.0), "colour": "#2563EB", "alpha": 0.32, "edge": 80.0},
        {"name": "FDA", "ring": ring(A["riyadh_final_director_east_15l"]["ring"]), "floor": agl700, "ceiling": z(11000.0), "colour": "#0EA5E9", "alpha": 0.10, "edge": 55.0, "corner_edges": True,
         "subtract": ["CTR"]},
        {"name": "TMA", "ring": ring(A["riyadh_east_tma_part1"]["ring"]), "floor": agl700, "ceiling": z(2570.0 + 700.0), "colour": "#6366F1", "alpha": 0.07, "edge": 45.0, "no_floor_edge": True,
         "subtract": ["ATZ", "CTR"]},
    ]
    # the runways of King Khaled (AD 2 OERK 2.12): from each threshold along its true bearing
    pav = []
    seen = set()
    for rw in d["oerk"]["runways"]:
        th = rw["threshold"]
        x0, y0 = local(th["lat"], th["lon"])
        key = (round(x0, -2), round(y0, -2))
        a = math.radians(rw["true_deg"])
        ux, uy = math.sin(a), math.cos(a)
        L, w = rw["length_m"], rw["width_m"] / 2.0
        if any(abs(x0 + ux * L - sx) < 300 and abs(y0 + uy * L - sy) < 300 for sx, sy in seen):
            continue                                     # the reciprocal of a runway already drawn
        seen.add(key)
        nx, ny = -uy * w, ux * w
        pav.append({"name": "OERK " + rw["id"], "zone": "runway", "holes": [],
                    "ring": [[x0 + nx, y0 + ny], [x0 + ux * L + nx, y0 + uy * L + ny], [x0 + ux * L - nx, y0 + uy * L - ny], [x0 - nx, y0 - ny]]})
    plan = open_plan()
    plan["pavements"] = plan["pavements"] + pav
    oerk = local(d["oerk"]["arp"]["lat"], d["oerk"]["arp"]["lon"])
    brg = math.radians(166.0)                            # the line of the section (data: oeth_to_oerk), from 9 NM before Thumamah to 27 NM beyond it
    on_line = lambda nm: (math.sin(brg) * nm * NM, math.cos(brg) * nm * NM)
    line = [[*on_line(nm), 0.0] for nm in [x * 0.5 for x in range(-18, 55)]]
    acx, acy = on_line(-6.6)
    ac_z = round(400.0 * FT * k + 10.0 * k, 1)
    fda = ring(A["riyadh_final_director_east_15l"]["ring"])[:-1]
    fx, fy = sum(p[0] for p in fda) / 4.0, sum(p[1] for p in fda) / 4.0
    atz_w = (-5.0 * NM * math.cos(math.radians(20)), -5.0 * NM * math.sin(math.radians(20)))
    anchors = {
        "atz": [*atz_w, z(2500.0)], "ctr": [oerk[0] - 10.0 * NM * 0.94, oerk[1] - 10.0 * NM * 0.34, z(3600.0)], "fda": [fx, fy, z(11000.0)],
        "tma": [-11.0 * NM, -3.0 * NM, z(2570.0 + 700.0)], "g": [-8.0 * NM, -9.0 * NM, 60.0 * k], "ac": [acx, acy, ac_z], "oeth": [0.0, 0.0, 0.0],
        "oerk": [oerk[0], oerk[1], 0.0], "line_n": [*on_line(-9.0), 0.0], "line_s": [*on_line(27.0), 0.0],
        "n0": [0.0, 0.0, 0.0], "n1": [0.0, 4000.0, 0.0],
    }
    return {
        "id": "oeth-17-01-airspace", "camera": {"at": [-80000.0, -46000.0, 40000.0], "look": [2500.0, -13000.0, 2500.0], "lens": 35}, "size": [2400, 1150], "samples": 96,
        "sun": {"elevation": 48, "azimuth": 150, "energy": 3.0}, "exposure": -0.2, "look": "AgX - Medium High Contrast",
        "keep_sources": [x for x in KEEP_SOURCES if x != "srtm"], "far_ground_z": 0.0, "far_ground_size": 3000000, "clip_end": 2000000, "plan": plan, "volumes": vols,
        "aircraft": [{"at": [round(acx, 1), round(acy, 1), ac_z], "heading": 166.0, "scale": 260.0}],
        "paths": [{"points": line, "colour": "#FFFFFF", "radius": 70.0, "dash": [900.0, 600.0], "drape": 40.0}],
        "anchors": anchors,
    }


RECIPES = {
    "oeth-17-01-airspace": airspace_17_01,
    "oeth-26-02-circuit": circuit_26_02,
    "oeth-18-07-circuit": lambda: circuit_recipe("oeth-18-07-circuit", {"at": [4700.0, -2300.0, 3300.0], "look": [-560.0, -480.0, 60.0], "lens": 30}),
}


if __name__ == "__main__":
    name = sys.argv[1]
    os.makedirs(os.path.join(HERE, "cache", "oeth3d"), exist_ok=True)
    out = os.path.join(HERE, "cache", "oeth3d", name + ".json")
    with open(out, "w") as f:
        json.dump(RECIPES[name](), f)
    print(out)
