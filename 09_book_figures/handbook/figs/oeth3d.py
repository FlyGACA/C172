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


def _from_canvas(F):
    """A function from a canvas point of a figs/h_b2.Frame map to the scene (metres east and north of the Thumamah reference point)."""
    dx, dy = local(F.lat0, F.lon0)                       # the frame's origin in the scene (the ARP for both figures: (0, 0))
    return lambda p: (round(dx + (p[0] - F.ox) / F.s * NM, 1), round(dy - (p[1] - F.oy) / F.s * NM, 1))


def _profile(points, knots):
    """Heights along a polyline: knots are (index of a point, feet AMSL); between them the height runs linearly with the distance flown."""
    cum = [0.0]
    for a, b in zip(points, points[1:]):
        cum.append(cum[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
    kd = [(cum[i], ft) for i, ft in knots]
    out = []
    for c in cum:
        for (d0, f0), (d1, f1) in zip(kd, kd[1:]):
            if c <= d1 + 1e-6:
                out.append(f0 + (f1 - f0) * (c - d0) / max(d1 - d0, 1e-6))
                break
        else:
            out.append(kd[-1][1])
    return out


def _dense(points, step):
    """The polyline with points added so that none of its pieces is longer than step."""
    out = [points[0]]
    for a, b in zip(points, points[1:]):
        n = max(1, int(math.ceil(math.dist(a, b) / step)))
        out += [(a[0] + (b[0] - a[0]) * i / n, a[1] + (b[1] - a[1]) * i / n) for i in range(1, n + 1)]
    return out


def _nearest(points, q):
    return min(range(len(points)), key=lambda i: (points[i][0] - q[0]) ** 2 + (points[i][1] - q[1]) ** 2)


def procedures_18_08(k=4.0):
    """Figure 18-8, the 3D view: the AIP's local procedures of Thumamah (AD 2.22) over the SRTM ground of the scene, heights (the ground's too) k times
    their scale. The routes are figs/f_18_08_local_procedures.py's own, carried from its map into the scene; their heights are the AIP's: the circuits at
    2 900 ft; the departure of 35 to 2 600 ft on runway heading, then 3 000 ft to the North VRP; that of 17 to 2 300 ft, round its circuit at 2 900 ft, then
    3 000 ft; the arrival from the east at 3 500 ft from the East VRP until past the ridge, then down to 2 900 ft by mid-field; that from the west at 2 900 ft."""
    from figs import f_18_08_local_procedures as L
    to = _from_canvas(L.F)

    def z(ft):
        return round((ft - FIELD_FT) * FT * k, 1)

    def path3(points, feet):
        return [[*to(p), z(f)] for p, f in zip(points, feet)]

    def circuit3(c):
        h, _ = circuit_heights(c)
        out, d = [], 0.0
        while d < c.length:
            (s, t), _u = c.at(d)
            x, y = runway_point(s, t)
            out.append([round(x, 1), round(y, 1), round(h(d) / FT * FT * k + 4.0 * k, 1)])
            d += 40.0
        return out
    step = L.units(60.0)                                 # canvas units for 60 m: the routes are cut into pieces that short, so that a height can change anywhere along them
    DEP35, DEP17, ARR_EAST, ARR_WEST = (_dense(p, step) for p in (L.DEP35, L.DEP17, L.ARR_EAST, L.ARR_WEST))
    turn = _nearest(DEP35, L.P(L.TURN_35, 0.0))
    dep35 = path3(DEP35, _profile(DEP35, [(0, 1870.0 + 150.0), (turn, 2600.0), (len(DEP35) - 1, 3000.0)]))
    m17 = L._m17
    dw = _nearest(DEP17, L.P(*L.C17.at(m17["downwind"])[0]))
    upend = _nearest(DEP17, L.P(*L.C17.at(m17["up_end"])[0]))
    dep17 = path3(DEP17, _profile(DEP17, [(0, 1870.0), (upend, 2300.0), (dw, 2900.0), (len(DEP17) - 1, 3000.0)]))
    ridge = _nearest(ARR_EAST, L.RIDGE)
    mid = _nearest(ARR_EAST, L.MIDFIELD)
    arr_e = path3(ARR_EAST, _profile(ARR_EAST, [(0, 3500.0), (ridge, 3500.0), (mid, 2900.0), (len(ARR_EAST) - 1, 2900.0)]))
    arr_w = path3(ARR_WEST, [2900.0] * len(ARR_WEST))
    c35 = circuit3(L.C35)
    c17 = circuit3(L.C17)
    hw = [[*to(p), 0.0] for p in L.HIGHWAY]
    atz = [[round(c, 1) for c in to(L.F.xy(lon, lat))] for lon, lat in _air_data()["areas"]["oeth_atz_ring"]]
    rx, ry = to(L.RESERVE)
    rr = 400.0
    reserve = [[round(rx + rr * math.cos(i * math.pi / 18), 1), round(ry + rr * math.sin(i * math.pi / 18), 1)] for i in range(36)]

    def on(points, frac):
        cum = [0.0]
        for a, b in zip(points, points[1:]):
            cum.append(cum[-1] + math.dist(a, b))
        target = cum[-1] * frac
        i = next(j for j in range(1, len(cum)) if cum[j] >= target)
        f = (target - cum[i - 1]) / max(cum[i] - cum[i - 1], 1e-6)
        return [points[i - 1][q] + (points[i][q] - points[i - 1][q]) * f for q in range(3)], [points[i][q] - points[i - 1][q] for q in range(2)]

    def plane(points, frac, scale=80.0):
        p, (dx, dy) = on(points, frac)
        return {"at": [round(c, 1) for c in p], "heading": round(math.degrees(math.atan2(dx, dy)) % 360.0, 1), "scale": scale}
    nv, ev = to(L.NV), to(L.EV)
    anchors = {
        "rwy": [*to(L.P(3350.0, -40.0)), 0.0], "dep35": on(dep35, 0.30)[0], "dep17": on(dep17, 0.52)[0], "nv": [*nv, 0.0], "nv_top": [*nv, z(3000.0)], "ev": [*ev, 0.0],
        "ev_top": [*ev, z(3500.0)], "ridge": arr_e[ridge], "mid": arr_e[mid], "hw": [*to(L.HIGHWAY[len(L.HIGHWAY) // 2]), 0.0], "entry": on(arr_w, 0.35)[0],
        "reserve": [rx, ry, 0.0], "atz": [*to(L.F.bearing_point(L.ARP, 150.0, 5.0)), z(2400.0)], "c35": on(c35, 0.55)[0],
        "n0": [6400.0, 0.0, 0.0], "n1": [6400.0, 1500.0, 0.0],             # north at the middle of the view (in perspective it leans elsewhere)
    }
    return {
        "id": "oeth-18-08-procedures", "camera": {"at": [6300.0, -19000.0, 6400.0], "look": [6400.0, 2500.0, 700.0], "lens": 27}, "size": [2400, 1150], "samples": 96,
        "sun": {"elevation": 40, "azimuth": 135, "energy": 3.2}, "exposure": -0.3, "look": "AgX - High Contrast", "zscale": k,
        "far_ground_size": 3000000, "clip_end": 2000000,
        "keep_sources": KEEP_SOURCES, "plan": open_plan(),
        "volumes": [{"name": "ATZ", "ring": atz, "floor": -30.0, "ceiling": z(3000.0), "colour": "#16A34A", "alpha": 0.14, "edge": 40.0},
                    {"name": "reserve", "ring": reserve, "floor": -30.0, "ceiling": 60.0 * k, "colour": "#DC2626", "alpha": 0.45, "edge": 18.0}],
        "aircraft": [plane(dep35, 0.45), plane(arr_e, 0.55), plane(arr_w, 0.5)],
        "paths": [{"points": c17, "colour": "#60A5FA", "radius": 58.0, "dash": [300.0, 200.0]},
                  {"points": c35, "colour": "#1D4ED8", "radius": 80.0, "arrows": 2600.0, "arrow_size": 320.0},
                  {"points": dep35, "colour": "#A21CAF", "radius": 80.0, "arrows": 2600.0, "arrow_size": 320.0},
                  {"points": dep17, "colour": "#C026D3", "radius": 64.0, "dash": [340.0, 220.0], "end_arrow": True, "arrow_size": 300.0},
                  {"points": arr_e, "colour": "#047857", "radius": 80.0, "arrows": 3000.0, "arrow_size": 320.0},
                  {"points": arr_w, "colour": "#047857", "radius": 80.0, "arrows": 2600.0, "arrow_size": 320.0},
                  {"points": hw, "colour": "#3A3F4A", "radius": 55.0, "drape": 8.0}],
        "anchors": anchors,
    }


def route_17_09(k=5.0):
    """Figure 17-9, the 3D view: the worked example (Thumamah, North VRP, East VRP, Thumamah) among the blocks of airspace of data/saudi_airspace.json, as in
    Figure 17-1 (heights k times their scale, the ground flat): the ATZ, the final director area, the floor of the terminal area, the northern part of the Riyadh
    CTR and the three special use areas (OED25 and OED33 to 4 200 and 4 500 ft AMSL, OER212 to 500 ft above the ground); the route at the heights of
    Figure 17-10 (runway heading to 2 600 ft, 3 000 ft at the North VRP, 3 500 ft to past the ridge, then 2 900 ft)."""
    from figs import f_17_10_route_profile as R
    d = _air_data()
    A = d["areas"]

    def ring(lonlat):
        return [[round(c, 1) for c in local(lat, lon)] for lon, lat in lonlat]

    def z(ft):
        return round((ft - FIELD_FT) * FT * k, 1)
    agl = lambda ft: {"agl": round(ft * FT * k, 1)}
    red = "#DC2626"
    prd = A["prd"]
    vols = [
        {"name": "ATZ", "ring": ring(A["oeth_atz_ring"]), "floor": -30.0, "ceiling": z(3000.0), "colour": "#16A34A", "alpha": 0.40, "edge": 70.0},
        {"name": "CTR", "ring": ring(A["oerk_ctr_ring"]), "floor": -30.0, "ceiling": z(4500.0), "colour": "#2563EB", "alpha": 0.30, "edge": 70.0},
        {"name": "FDA", "ring": ring(A["riyadh_final_director_east_15l"]["ring"]), "floor": agl(700.0), "ceiling": z(11000.0), "colour": "#0EA5E9", "alpha": 0.08, "edge": 50.0,
         "corner_edges": True, "subtract": ["CTR"]},
        {"name": "TMA", "ring": ring(A["riyadh_east_tma_part1"]["ring"]), "floor": agl(700.0), "ceiling": z(2570.0 + 700.0), "colour": "#6366F1", "alpha": 0.07, "edge": 40.0,
         "no_floor_edge": True, "subtract": ["ATZ", "CTR"]},
        {"name": "OED25", "ring": ring(prd["OED25"]["ring"]), "floor": -30.0, "ceiling": z(4200.0), "colour": red, "alpha": 0.32, "edge": 55.0, "corner_edges": True},
        {"name": "OER212", "ring": ring(prd["OER212"]["ring"]), "floor": -30.0, "ceiling": round(500.0 * FT * k, 1), "colour": red, "alpha": 0.40, "edge": 55.0, "corner_edges": True},
        {"name": "OED33", "ring": ring(prd["OED33"]["ring"]), "floor": -30.0, "ceiling": z(4500.0), "colour": red, "alpha": 0.32, "edge": 55.0, "corner_edges": True},
    ]
    vr = {v["name"]: local(v["lat"], v["lon"]) for v in d["oeth"]["vrps"]}
    names = list(vr)
    nv, ev = vr[names[0]], vr[names[1]]
    legs = [(0.0, 0.0), nv, ev, (0.0, 0.0)]
    cum = [0.0]
    for a, b in zip(legs, legs[1:]):
        cum.append(cum[-1] + math.dist(a, b) / NM)
    scale_nm = R.TOTAL / cum[-1]                          # the profile's distances (great circle) against this flat frame's: within a few tenths of a per cent
    pts = []
    for i in range(3):
        n = 60
        for j in range(n):
            f = j / n
            x, y = legs[i][0] + (legs[i + 1][0] - legs[i][0]) * f, legs[i][1] + (legs[i + 1][1] - legs[i][1]) * f
            dnm = (cum[i] + (cum[i + 1] - cum[i]) * f) * scale_nm
            pts.append((x, y, dnm))
    pts.append((0.0, 0.0, R.TOTAL))

    def ft_at(dnm):
        for (d0, f0), (d1, f1) in zip(R.PATH, R.PATH[1:]):
            if dnm <= d1:
                return f0 + (f1 - f0) * (dnm - d0) / max(d1 - d0, 1e-6)
        return R.PATH[-1][1]
    route = [[round(x, 1), round(y, 1), z(ft_at(dn)) + 20.0] for x, y, dn in pts if dn <= R.PATH[-1][0]]
    oerk = local(d["oerk"]["arp"]["lat"], d["oerk"]["arp"]["lon"])
    cen = lambda r: [sum(p[0] for p in r[:-1]) / (len(r) - 1), sum(p[1] for p in r[:-1]) / (len(r) - 1)]
    o25, o212, o33 = (cen(ring(prd[n]["ring"])) for n in ("OED25", "OER212", "OED33"))
    mid = route[len(route) // 2]
    anchors = {
        "atz": [-5.0 * NM * 0.94, -5.0 * NM * 0.34, z(2600.0)], "tma": [-14.0 * NM, 6.0 * NM, agl(700.0)["agl"]], "fda": [-3.0 * NM, 10.0 * NM, z(11000.0)],
        "ctr": [oerk[0] - 7.0 * NM, oerk[1] + 7.0 * NM, z(4000.0)], "nv": [*nv, 0.0], "ev": [*ev, 0.0], "o25": [*o25, z(4200.0)], "o212": [*o212, round(500.0 * FT * k, 1)],
        "o33": [*o33, z(4500.0)], "rwy": [0.0, 0.0, 0.0], "route": mid, "n0": [0.0, 0.0, 0.0], "n1": [0.0, 4000.0, 0.0],
    }
    i_plane = len(route) // 3
    p0, p1 = route[i_plane], route[i_plane + 1]
    return {
        "id": "oeth-17-09-route", "camera": {"at": [-26000.0, -86000.0, 56000.0], "look": [9000.0, -4000.0, 0.0], "lens": 34}, "size": [2400, 1150], "samples": 96,
        "sun": {"elevation": 48, "azimuth": 150, "energy": 3.0}, "exposure": -0.2, "look": "AgX - Medium High Contrast",
        "keep_sources": [x for x in KEEP_SOURCES if x != "srtm"], "far_ground_z": 0.0, "far_ground_size": 3000000, "clip_end": 2000000, "plan": open_plan(), "volumes": vols,
        "aircraft": [{"at": p0, "heading": round(math.degrees(math.atan2(p1[0] - p0[0], p1[1] - p0[1])) % 360.0, 1), "scale": 280.0}],
        "paths": [{"points": route, "colour": "#111827", "radius": 190.0, "arrows": 8000.0, "arrow_size": 800.0}],
        "anchors": anchors,
    }


def _bar(t0, s0, t1, s1, w):
    """A painted bar of width w (metres) from (t0, s0) to (t1, s1) of the runway frame, in the scene."""
    L = math.hypot(t1 - t0, s1 - s0) or 1.0
    nt, ns = -(s1 - s0) / L * w / 2, (t1 - t0) / L * w / 2
    return [[round(c, 2) for c in xy(s, t)] for t, s in ((t0 + nt, s0 + ns), (t1 + nt, s1 + ns), (t1 - nt, s1 - ns), (t0 - nt, s0 - ns))]


def aerodrome_18_01(scale=3.5):
    """Figure 18-1, the 3D view: the northern part of Thumamah from the north-west, low (the north end near, the aprons and the runway going away): the AIP's runway and stopway with
    their ICAO markings, the book's open ground plan (pavements, sand islands, roofs), the stopway's yellow chevrons and the runway-holding position of
    the diagonal link as figs/f_18_01_aerodrome_plan.py draws them (the paint drawn wider than it is, so that it shows), and the parked aeroplanes of the
    plan as the C172 model, `scale` times its size. Heights are not enlarged."""
    from figs import f_18_01_aerodrome_plan as A
    RW = 25.0
    marks = []
    for k in range(10):                                   # the chevrons of the stopway, pointing to the runway
        s0 = -300 + 18 + k * 29.0
        marks.append({"ring": _bar(-RW + 3, s0 - 11, 0, s0 + 5, 2.6), "colour": "#EDB92D"})
        marks.append({"ring": _bar(0, s0 + 5, RW - 3, s0 - 11, 2.6), "colour": "#EDB92D"})
    s_join, ax, ay = A.link_axis()                         # the runway-holding position: two solid and two dashed lines across the diagonal link
    ptx, pty = 25 + 34 * ax, s_join + 34 * ay
    for off, dashed in ((15.0, False), (9.4, False), (0.0, True), (-5.6, True)):
        a = (ptx + ax * off - ay * 27, pty + ay * off + ax * 27)
        b = (ptx + ax * off + ay * 27, pty + ay * off - ax * 27)
        n = 9 if dashed else 1
        for i in range(n):
            if dashed and i % 2:
                continue
            f0, f1 = i / n, (i + 1) / n
            marks.append({"ring": _bar(a[0] + (b[0] - a[0]) * f0, a[1] + (b[1] - a[1]) * f0, a[0] + (b[0] - a[0]) * f1, a[1] + (b[1] - a[1]) * f1, 1.8), "colour": "#EDB92D"})
    plan = open_plan()
    plan["marks"] = marks
    aircraft = []
    for t, s0, code in B.PLAN["parked_aeroplanes"]:
        x, y = xy(s0, t)
        aircraft.append({"at": [round(x, 1), round(y, 1), 0.3], "heading": 351.0 if code == 1 else 171.0, "scale": scale})
    hang = next(b for b in B.PLAN["buildings"] if b["id"] == "HANGAR_MAIN")
    hc = (sum(p[0] for p in hang["ring"][:-1]) / (len(hang["ring"]) - 1), sum(p[1] for p in hang["ring"][:-1]) / (len(hang["ring"]) - 1))

    def a3(t, s, z=0.0):
        x, y = xy(s, t)
        return [round(x, 1), round(y, 1), z]
    pts = {n: A.inside_point(n, *h) for n, h in (("PARALLEL TAXIWAY", (182, 600)), ("MAIN APRON", (150, 1150)), ("NORTH TURN LOOP", (76, 12)))}
    north0 = xy(300.0, 120.0)
    north1 = (north0[0], north0[1] + 300.0)
    anchors = {
        "rwy": a3(0, 1000), "des": a3(0, 78), "twy": a3(*pts["PARALLEL TAXIWAY"]), "hold": a3(ptx, pty), "apron": a3(*pts["MAIN APRON"]),
        "stopway": a3(0, -70), "loop": a3(*pts["NORTH TURN LOOP"]), "hangar": a3(hc[0], hc[1], 7.0),
        "n0": [*north0, 0.0], "n1": [*north1, 0.0],
    }
    cam, look = xy(-700.0, 640.0), xy(950.0, 130.0)       # from the north-west, low: the north end near, the aprons and the runway going away
    return {
        "id": "oeth-18-01-aerodrome", "camera": {"at": [round(cam[0], 1), round(cam[1], 1), 300.0], "look": [round(look[0], 1), round(look[1], 1), 0.0], "lens": 30},
        "size": [2400, 1150], "samples": 128, "sun": {"elevation": 38, "azimuth": 130, "energy": 3.4}, "exposure": -0.25, "look": "AgX - Medium High Contrast",
        "keep_sources": KEEP_SOURCES, "far_ground_size": 3000000, "clip_end": 2000000, "plan": plan, "aircraft": aircraft, "anchors": anchors,
    }


# ---------------------------------------------------------------------------------- the manoeuvres of Chapter 27 over farmland (no aerodrome)
GROUND_FT = 1000.0 * FT                                  # the height of the exercises above the ground: 1 000 ft
ORANGE_WIND = "#C2410C"
CROP, CROP_DARK, ROAD = "#5E9A4A", "#4C8239", "#4A505B"


def _circle(cx, cy, r, n=72, a0=0.0, a1=360.0):
    return [[round(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)), 1), round(cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n)), 1)] for i in range(n + (0 if a1 - a0 >= 360 else 1))]


def _pivot(cx, cy, r, sector=55.0):
    """A field under a centre pivot: a green disc, one sector darker (a fresh cut)."""
    return [{"ring": _circle(cx, cy, r), "colour": CROP}, {"ring": [[cx, cy]] + _circle(cx, cy, r * 0.995, 16, 10.0, 10.0 + sector), "colour": CROP_DARK}]


def _road(x0, y0, x1, y1, w=24.0):
    L = math.hypot(x1 - x0, y1 - y0)
    nx, ny = -(y1 - y0) / L * w / 2, (x1 - x0) / L * w / 2
    out = [{"ring": [[x0 + nx, y0 + ny], [x1 + nx, y1 + ny], [x1 - nx, y1 - ny], [x0 - nx, y0 - ny]], "colour": ROAD}]
    n = int(L // 40)
    for i in range(n):                                    # the centre line, dashed
        f0, f1 = i / n, (i + 0.45) / n
        a, b = (x0 + (x1 - x0) * f0, y0 + (y1 - y0) * f0), (x0 + (x1 - x0) * f1, y0 + (y1 - y0) * f1)
        ux, uy = (x1 - x0) / L * 0.0, (y1 - y0) / L * 0.0
        out.append({"ring": [[a[0] + nx * 0.08, a[1] + ny * 0.08], [b[0] + nx * 0.08, b[1] + ny * 0.08], [b[0] - nx * 0.08, b[1] - ny * 0.08], [a[0] - nx * 0.08, a[1] - ny * 0.08]],
                    "colour": "#F2EFE6"})
    return out


def _wind(x, y, z, length, heading, k=0):
    """A wind arrow: the way the wind blows (true heading), pale orange, with its head at the end."""
    a = math.radians(heading)
    ux, uy = math.sin(a), math.cos(a)
    return {"points": [[x - ux * length / 2, y - uy * length / 2, z], [x + ux * length / 2, y + uy * length / 2, z]], "colour": ORANGE_WIND, "radius": 9.0,
            "end_arrow": True, "arrow_size": 45.0}


def _farm_recipe(rid, camera, marks, aircraft, paths, anchors, blocks=None):
    return {
        "id": rid, "camera": camera, "size": [2400, 1150], "samples": 96, "exposure": -0.15,
        "sun": {"elevation": 76, "azimuth": 160, "energy": 4.2, "sky": 0.45},          # high, and the sky's own sun dimmed: one shadow, almost under what casts it (the ground track)
        "look": "AgX - Medium High Contrast", "keep_sources": [], "far_ground_z": 0.0, "far_ground_size": 3000000, "clip_end": 2000000,
        "plan": {"marks": marks, "blocks": blocks or []}, "aircraft": aircraft, "paths": paths, "anchors": anchors,
    }


def _ac(x, y, heading, bank=0.0, z=None, scale=15.0):
    return {"at": [round(x, 1), round(y, 1), round(GROUND_FT if z is None else z, 1)], "heading": round(heading % 360.0, 1), "bank": bank, "scale": scale}


def drift_27_05():
    """Figure 27-5, the 3D view: a road from south to north and a 15 kt wind from the west. Heading along the road, the aeroplane drifts east of it (red,
    its track dashed); heading about 10 degrees into the wind, it tracks along the road (green). 1 000 ft above the ground, the aeroplanes enlarged."""
    h = GROUND_FT
    marks = _road(0, -1500, 0, 1500) + _pivot(-700, 650, 260) + _pivot(650, -550, 230) + _pivot(-650, -800, 220)
    drift = [[0.0, -1100.0, h], [math.tan(math.radians(10)) * 2200.0, 1100.0, h]]
    crab = [[0.0, -1100.0, h + 40.0], [0.0, 1100.0, h + 40.0]]
    paths = [{"points": drift, "colour": "#B91C1C", "radius": 7.0, "dash": [60.0, 40.0], "end_arrow": True, "arrow_size": 40.0},
             {"points": crab, "colour": "#0F766E", "radius": 7.0, "end_arrow": True, "arrow_size": 40.0},
             _wind(-700, 200, h + 180, 420, 90), _wind(-700, -150, h + 180, 420, 90)]
    aircraft = [_ac(math.tan(math.radians(10)) * 1300.0, 200.0, 0.0), _ac(0.0, -300.0, 350.0, z=h + 40.0)]
    anchors = {"drift": [math.tan(math.radians(10)) * 1800.0, 700.0, h], "crab": [0.0, -300.0, h + 40.0], "wind": [-700, 200, h + 180], "n0": [0, 0, 0], "n1": [0, 200, 0]}
    return _farm_recipe("farm-27-05-drift", {"at": [-2100.0, -1700.0, 1500.0], "look": [150.0, 150.0, 150.0], "lens": 34}, marks, aircraft, paths, anchors)


def rectangle_27_06():
    """Figure 27-6, the 3D view: the field, the course round it at an equal distance, flown anticlockwise, the wind from the west; the aeroplane on each
    leg (on the base leg the nose towards the inside, on the crosswind leg towards the outside) and banked at the start of the turn onto base."""
    h = GROUND_FT
    D, R = 450.0, 350.0                                  # the course at an equal distance outside the field; the corners of 350 m radius (the chapter's)
    A, Bh = 450.0 + D, 260.0 + D
    field = [[-450, -260], [450, -260], [450, 260], [-450, 260]]
    marks = [{"ring": field, "colour": CROP}] + [{"ring": [[-450 + i * 60, -260], [-420 + i * 60, -260], [-420 + i * 60, 260], [-450 + i * 60, 260]], "colour": CROP_DARK} for i in range(15)]
    marks += _pivot(-1300, 900, 240) + _pivot(1350, -850, 220)
    pts = []
    corners = [(A - R, -Bh + R, 270.0), (A - R, Bh - R, 0.0), (-A + R, Bh - R, 90.0), (-A + R, -Bh + R, 180.0)]
    for cx, cy, a0 in corners:                           # anticlockwise: each corner a quarter circle
        pts += [[cx + R * math.cos(math.radians(a0 + 90 * i / 12)), cy + R * math.sin(math.radians(a0 + 90 * i / 12)), h] for i in range(13)]
    pts.append(pts[0])
    entry = [[-A - 500.0, -Bh - 500.0, h], [-A + 180.0, -Bh, h]]
    paths = [{"points": pts, "colour": "#1D4ED8", "radius": 8.0, "arrows": 900.0, "arrow_size": 42.0},
             {"points": entry, "colour": "#1D4ED8", "radius": 6.0, "dash": [50.0, 35.0], "end_arrow": True, "arrow_size": 36.0},
             _wind(-1250, 150, h + 200, 420, 90), _wind(-1250, -150, h + 200, 420, 90)]
    aircraft = [_ac(0.0, -Bh, 90.0), _ac(A, 0.0, 350.0), _ac(0.0, Bh, 270.0), _ac(-A, 0.0, 190.0),
                _ac(A - R + R * math.cos(math.radians(290)), -Bh + R + R * math.sin(math.radians(290)), 110.0, bank=-40.0)]
    anchors = {"wind": [-1250, 150, h + 200], "field": [0, 0, 0], "entry": [-A - 250.0, -Bh - 250.0, h], "down": [0.0, -Bh, h], "corner": [A - R * 0.3, -Bh + R * 0.05, h],
               "base": [A, 0.0, h], "up": [0.0, Bh, h], "cross": [-A, 0.0, h], "n0": [0, 0, 0], "n1": [0, 200, 0]}
    return _farm_recipe("farm-27-06-rectangle", {"at": [250.0, -3150.0, 2400.0], "look": [0.0, 0.0, 120.0], "lens": 34}, marks, aircraft, paths, anchors)


def s_turns_27_07():
    """Figure 27-7, the 3D view: S-turns across a road from west to east, the wind from the north: half circles south of the road (downwind, turning
    left, the bank from 40 through 32 to 23 degrees) and north of it (upwind, turning right, 23 through 32 to 40), wings level over the road."""
    h = GROUND_FT
    r = 350.0                                            # the chapter's radius
    x0 = -2 * r
    marks = _road(-2200, 0, 2200, 0) + _pivot(-950, 900, 260) + _pivot(900, -880, 240)
    pts = []
    for k in range(3):                                   # three half circles: south, north, south
        cx = x0 + r + 2 * r * k
        south = k % 2 == 0
        for i in range(25):
            a = math.radians(180 + 180 * i / 24) if south else math.radians(180 - 180 * i / 24)
            pts.append([round(cx + r * math.cos(a), 1), round(r * math.sin(a), 1), h])
    paths = [{"points": pts, "colour": "#1D4ED8", "radius": 8.0, "arrows": 700.0, "arrow_size": 42.0},
             _wind(1500, 700, h + 200, 380, 180), _wind(1750, 700, h + 200, 380, 180)]
    c1 = x0 + r

    def on1(deg):                                         # a point of the first half circle (south of the road), deg from east
        a = math.radians(deg)
        return c1 + r * math.cos(a), r * math.sin(a)
    p3, p4, p5 = on1(215.0), on1(270.0), on1(325.0)
    c2 = x0 + 3 * r
    aircraft = [_ac(x0, 0.0, 180.0), _ac(*p3, 145.0, bank=-40.0), _ac(*p4, 80.0, bank=-32.0), _ac(*p5, 25.0, bank=-23.0), _ac(x0 + 2 * r, 0.0, 0.0),
                _ac(c2, r, 80.0, bank=32.0)]
    vehicle = [[c1 + 40.0, -4.0], [c1 + 52.0, -4.0], [c1 + 52.0, 4.0], [c1 + 40.0, 4.0]]
    anchors = {"wind": [1625, 700, h + 200], "cross_dn": [x0, 0.0, h], "steep": [*p3, h], "xw": [*p4, h], "shallow": [*p5, h], "cross_up": [x0 + 2 * r, 0.0, h],
               "up_half": [c2, r, h], "vehicle": [c1 + 46.0, 0.0, 3.0], "n0": [0, 0, 0], "n1": [0, 200, 0]}
    return _farm_recipe("farm-27-07-s-turns", {"at": [-150.0, -2400.0, 1700.0], "look": [-150.0, 0.0, 120.0], "lens": 34}, marks, aircraft, paths, anchors,
                        blocks=[{"ring": vehicle, "height": 2.5, "colour": "#DC2626"}])


def point_27_08():
    """Figure 27-8, the 3D view: turns around the centre of a circular field, anticlockwise, the wind from the west: the bank steepest downwind (40),
    about 32 at the crosswind points (the nose inside the circle going north, outside going south) and shallowest upwind (23)."""
    h = GROUND_FT
    R = 350.0                                            # the chapter's radius
    marks = _pivot(0, 0, 150) + _pivot(-1300, 800, 240) + _pivot(1250, -800, 230) + _road(-2200, -1200, 2200, -1200)
    circle = [[round(R * math.cos(math.radians(270 + 360 * i / 72)), 1), round(R * math.sin(math.radians(270 + 360 * i / 72)), 1), h] for i in range(73)]
    entry = [[-1300.0, -R, h], [0.0, -R, h]]
    paths = [{"points": circle, "colour": "#1D4ED8", "radius": 8.0, "arrows": 700.0, "arrow_size": 42.0},
             {"points": entry, "colour": "#1D4ED8", "radius": 6.0, "dash": [50.0, 35.0]},
             _wind(-1250, 450, h + 200, 420, 90), _wind(-1250, 150, h + 200, 420, 90)]
    aircraft = [_ac(0.0, -R, 90.0, bank=-40.0), _ac(R, 0.0, 350.0, bank=-32.0), _ac(0.0, R, 270.0, bank=-23.0), _ac(-R, 0.0, 190.0, bank=-32.0)]
    anchors = {"point": [0, 0, 0], "wind": [-1250, 450, h + 200], "entry": [-800.0, -R, h], "down": [0.0, -R, h], "east": [R, 0.0, h], "up": [0.0, R, h], "west": [-R, 0.0, h],
               "n0": [0, 0, 0], "n1": [0, 200, 0]}
    return _farm_recipe("farm-27-08-point", {"at": [150.0, -2050.0, 1650.0], "look": [0.0, 0.0, 150.0], "lens": 34}, marks, aircraft, paths, anchors)


RECIPES = {
    "farm-27-05-drift": drift_27_05,
    "farm-27-06-rectangle": rectangle_27_06,
    "farm-27-07-s-turns": s_turns_27_07,
    "farm-27-08-point": point_27_08,
    "oeth-18-01-aerodrome": aerodrome_18_01,
    "oeth-18-08-procedures": procedures_18_08,
    "oeth-17-09-route": route_17_09,
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
