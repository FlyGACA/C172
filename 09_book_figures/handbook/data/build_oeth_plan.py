"""Build data/oeth_plan.json, the ground plan of Thumamah (OETH) that Figure 18-1 and the other Thumamah pictures draw from, out of open data.

The runway, its stopways and its thresholds are the AIP's (AD 2.12, AMDT 11/26; data/saudi_airspace.json). Everything else is read off open satellite imagery: a median of
cloud-free Copernicus Sentinel-2 scenes (10 m; data/open/oeth_s2_composite.npz, fetched by data/open/fetch_oeth_open.py), resampled into the runway frame. Pavement is what is
neutral in colour where the desert is red: a cell counts as paved when its redness (B04 - B02) / (B04 + B02) is below 0.29 (sand is about 0.35, concrete and dusty asphalt about
0.25, clean asphalt about 0.17, so the edge of clean asphalt lands some 5 m outside its true place). The outline of that surface inside an airside window is vectorised,
simplified to 5 m, and its edges that run along or across the runway are made straight; the sand islands beside the runway are taken up to the runway's edge; roofs are the very
bright patches; the road is the dark line west of the aerodrome. Nothing is traced from imagery under a closed licence, and no OpenStreetMap geometry is used
(data/open/oeth_osm_check.json is only compared with: see the printed report). Accuracy: about 10 m (one pixel).

Attribution that goes with every use: "Contains modified Copernicus Sentinel data 2026".
Coordinates are metres in the runway frame: s from the threshold of runway 17 towards the threshold of runway 35 (southwards), t to the west of the centreline.
Needs numpy, pillow, scikit-image and shapely.    python build_oeth_plan.py [--check-picture]     Not for navigation.
"""
import json
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw
from shapely.geometry import MultiPolygon, Point, Polygon, box
from shapely.ops import unary_union
from skimage import measure

HERE = os.path.dirname(os.path.abspath(__file__))
OPEN = os.path.join(HERE, "open")
OUT = os.path.join(HERE, "oeth_plan.json")
FACTS = json.load(open(os.path.join(HERE, "saudi_airspace.json"), encoding="utf-8"))["oeth"]
META = json.load(open(os.path.join(OPEN, "oeth_s2_composite.json"), encoding="utf-8"))
RES = 2.5                                            # metres to a cell of the runway-frame grid (the imagery itself is 10 m)
S_MIN, S_MAX, T_MIN, T_MAX = -900.0, 4900.0, -300.0, 400.0
RW = 25.0                                            # half the runway width (AIP: 50 m)
RED_PAVED = 0.29                                     # redness below this is pavement (or a roof); see the docstring
ROOF_SEED, GROUND_BRIGHT = 4100.0, 2800.0            # a roof is a patch brighter than ROOF_SEED; its outline is taken half-way between its peak and the ground
# the airside window in (t, s): open ground to the east, the public road and the plots to the west
WINDOW = [(-45, -330), (-45, 4090), (60, 4090), (175, 4040), (175, 3740), (262, 2900), (262, 290), (240, 290), (240, 95), (172, 95), (172, 30), (150, 30), (150, -15), (45, -15), (45, -330)]
# the parts of the paved surface, by where they lie: (name, zone, boxes of (t0, s0, t1, s1)); a part is what is paved inside its boxes
ZONES = [                                            # the cuts between parts run through the sand islands or across open pavement, never along an island's edge
    ("NORTH TURN LOOP", "taxiway", [(RW, -20, 150, 266)]),
    ("HANGAR APRON", "apron", [(150, -20, 262, 266)]),
    ("PARALLEL TAXIWAY", "taxiway", [(RW, 266, 194, 880)]),
    ("NORTH APRON", "apron", [(194, 266, 262, 880)]),
    ("LINK TO THE MAIN APRON", "taxiway", [(RW, 880, 112, 940)]),
    ("MAIN APRON", "apron", [(112, 880, 262, 1343)]),
    ("DIAGONAL LINK", "taxiway", [(RW, 940, 112, 1343), (RW, 1343, 88, 1420)]),
    ("SOUTH APRON", "apron", [(88, 1343, 262, 2920)]),
    ("MID LINK", "taxiway", [(RW, 1420, 88, 2420)]),
    ("SOUTH DIAGONAL LINK", "taxiway", [(RW, 2420, 88, 2920)]),
    ("SOUTH TURN LOOP", "taxiway", [(RW, 3700, 180, 4090)]),
]
# parked aeroplanes for the pictures (t, s, heading 1 = nose north, 2 = nose south): the three on the south apron stand where the composite shows aeroplanes on every date;
# the others are placed on the aprons for the picture
PARKED = [[228, 340, 1], [228, 364, 1], [228, 388, 1], [228, 412, 1], [228, 436, 1], [222, 1040, 1], [222, 1075, 1], [165, 1912, 2], [165, 1946, 2], [165, 2006, 2]]


def utm38(lat, lon):
    """WGS 84 to UTM zone 38 N (EPSG:32638), Krueger series to n^3; millimetres are not needed here."""
    a, f, k0, lon0 = 6378137.0, 1 / 298.257223563, 0.9996, math.radians(45.0)
    n = f / (2 - f)
    A = a / (1 + n) * (1 + n * n / 4 + n ** 4 / 64)
    al = (n / 2 - 2 * n * n / 3 + 5 * n ** 3 / 16, 13 * n * n / 48 - 3 * n ** 3 / 5, 61 * n ** 3 / 240)
    phi, lam = math.radians(lat), math.radians(lon) - lon0
    e = 2 * math.sqrt(n) / (1 + n)
    t = math.sinh(math.atanh(math.sin(phi)) - e * math.atanh(e * math.sin(phi)))
    xi, eta = math.atan2(t, math.cos(lam)), math.atanh(math.sin(lam) / math.sqrt(1 + t * t))
    E = 500000 + k0 * A * (eta + sum(al[j] * math.cos(2 * (j + 1) * xi) * math.sinh(2 * (j + 1) * eta) for j in range(3)))
    N = k0 * A * (xi + sum(al[j] * math.sin(2 * (j + 1) * xi) * math.cosh(2 * (j + 1) * eta) for j in range(3)))
    return E, N


THR = {r["id"]: r["threshold"] for r in FACTS["runways"]}
E0, N0 = utm38(THR["17"]["lat"], THR["17"]["lon"])
E1, N1 = utm38(THR["35"]["lat"], THR["35"]["lon"])
LEN = math.hypot(E1 - E0, N1 - N0)
UX, UY = (E1 - E0) / LEN, (N1 - N0) / LEN            # along the runway, in the grid
WX, WY = UY, -UX                                     # to the west of it


def to_frame(band):
    """A north-up 10 m band of the composite, resampled (bicubic) into the runway frame: rows are t, columns are s."""
    emin, nmin, emax, nmax = META["bounds_e_n_min_e_n_max"]
    w, h = int((S_MAX - S_MIN) / RES), int((T_MAX - T_MIN) / RES)
    a, b, c = RES * UX / 10, RES * WX / 10, (E0 + S_MIN * UX + T_MIN * WX - emin) / 10
    d, e, f = -RES * UY / 10, -RES * WY / 10, (nmax - N0 - S_MIN * UY - T_MIN * WY) / 10
    return np.asarray(Image.fromarray(band.astype(np.float32), mode="F").transform((w, h), Image.AFFINE, (a, b, c, d, e, f), resample=Image.BICUBIC))


def cell(t, s):
    return int((t - T_MIN) / RES), int((s - S_MIN) / RES)


def ts_of(row, col):
    return T_MIN + (row + 0.5) * RES, S_MIN + (col + 0.5) * RES


def rings_of(field, level):
    """Closed contours of `field` at `level` as shapely polygons in (t, s), each with the value of the field inside it."""
    out = []
    for cn in measure.find_contours(field, level):
        if len(cn) < 6 or not np.allclose(cn[0], cn[-1]):
            continue
        p = Polygon([ts_of(y, x) for y, x in cn])
        if not p.is_valid:
            p = p.buffer(0)
        for g in (p.geoms if isinstance(p, MultiPolygon) else [p]):
            if g.is_empty or g.area < 150:
                continue
            rp = g.representative_point()
            out.append((g, float(field[cell(rp.x, rp.y)])))
    return out


def straighten(ring, min_len=22.0, max_dev=12.0):
    """Make the edges of a ring that run along or across the runway exactly so (the aerodrome is laid out on the runway's axes)."""
    pts = [list(p) for p in ring[:-1]]
    n = len(pts)
    for _ in range(3):
        for i in range(n):
            a, b = pts[i], pts[(i + 1) % n]
            dt, ds = b[0] - a[0], b[1] - a[1]
            if math.hypot(dt, ds) < min_len:
                continue
            ang = abs(math.degrees(math.atan2(dt, ds))) % 180
            if ang < max_dev or ang > 180 - max_dev:
                a[0] = b[0] = (a[0] + b[0]) / 2
            elif abs(ang - 90) < max_dev:
                a[1] = b[1] = (a[1] + b[1]) / 2
    return pts + [pts[0]]


def tidy(poly, tol=5.0):
    """Simplify a polygon, straighten its edges, and return its largest piece."""
    g = poly.simplify(tol, preserve_topology=True)
    q = Polygon(straighten(list(g.exterior.coords)), [straighten(list(h.coords)) for h in g.interiors])
    if not q.is_valid:
        q = q.buffer(0)
    q = q.simplify(2.0, preserve_topology=True)
    if isinstance(q, MultiPolygon):
        q = max(q.geoms, key=lambda x: x.area)
    return q


def r05(ring):
    return [[round(t * 2) / 2, round(s * 2) / 2] for t, s in ring]


def main():
    z = np.load(os.path.join(OPEN, "oeth_s2_composite.npz"))
    B, G, R = to_frame(z["B02"]), to_frame(z["B03"]), to_frame(z["B04"])
    with np.errstate(invalid="ignore", divide="ignore"):
        red, bri = (R - B) / (R + B), (R + G + B) / 3                     # the corners of the grid lie outside the composite
    h, w = red.shape
    report = {}

    # how well the imagery sits on the AIP's runway: the middle of the dark band, where sand lies on both sides
    ts = T_MIN + (np.arange(h) + 0.5) * RES
    prof = red[:, cell(0, 1450)[1]:cell(0, 2050)[1]].mean(axis=1)
    seg = (ts > -90) & (ts < 60)
    half = (prof[seg].min() + np.median(prof[(ts > -110) & (ts < -70)])) / 2
    idx = np.where(seg & (prof < half))[0]
    edge = lambda i0, i1: ts[i0] + (half - prof[i0]) * (ts[i1] - ts[i0]) / (prof[i1] - prof[i0])
    e_east, e_west = edge(idx[0] - 1, idx[0]), edge(idx[-1], idx[-1] + 1)
    report["runway_band_in_imagery_t_m"] = [round(float(e_east), 1), round(float(e_west), 1)]
    report["runway_centre_offset_m"] = round(float(e_east + e_west) / 2, 1)
    report["threshold_to_threshold_m"] = round(LEN, 1)

    # the paved surface inside the airside window
    paved_field = np.nan_to_num(red, nan=0.5) - RED_PAVED
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).polygon([((s - S_MIN) / RES - 0.5, (t - T_MIN) / RES - 0.5) for t, s in WINDOW], fill=1)
    field = np.where(np.asarray(m, dtype=bool), paved_field, 0.2)
    rings = rings_of(field, 0.0)
    surface = unary_union([g for g, v in rings if v < 0]).buffer(-3).buffer(3)                 # drop spurs thinner than 6 m
    surface = max(surface.geoms, key=lambda g: g.area) if isinstance(surface, MultiPolygon) else surface
    # the sand islands: holes of the surface; an island that is joined to its neighbour across a taxiway by a neck of sand is cut there
    islands = []
    for g, v in rings:
        if v >= 0 and g.area >= 700 and Polygon(surface.exterior).contains(g.representative_point()):
            opened = g.buffer(-7).buffer(7)
            islands += [p for p in (opened.geoms if isinstance(opened, MultiPolygon) else [opened]) if p.area >= 700]
    # islands beside the runway reach its edge: the paved margin that the imagery shows there is narrower than a pixel
    grown = []
    for isl in islands:
        t0, s0, t1, s1 = isl.bounds
        if t0 < RW + 15:
            top = isl.intersection(box(t0, s0, t0 + 4, s1))
            isl = unary_union([isl, box(RW, top.bounds[1], t0 + 4, top.bounds[3])])
        grown.append(isl)
    islands = [tidy(i) for i in grown]
    west = Polygon(surface.exterior).intersection(box(RW, S_MIN, T_MAX, S_MAX)).difference(unary_union(islands))

    def mean_in(poly, arr):
        t0, s0, t1, s1 = poly.bounds
        vals = []
        for tt in np.arange(t0 + 5, t1 - 4, 7.5):
            for ss in np.arange(s0 + 5, s1 - 4, 7.5):
                if poly.contains(Point(tt, ss)):
                    vals.append(arr[cell(tt, ss)])
        return float(np.mean(vals)) if vals else float("nan")

    pavements = []
    for name, zone, boxes in ZONES:
        part = west.intersection(unary_union([box(t0, s0, t1, s1) for t0, s0, t1, s1 in boxes]))
        if zone == "apron":                                                                # an apron has no spurs or notches narrower than 16 m
            part = part.buffer(-8, join_style=2).buffer(8, join_style=2).buffer(8, join_style=2).buffer(-8, join_style=2)
        pieces = [p for p in (part.geoms if hasattr(part, "geoms") else [part]) if not p.is_empty and p.area >= 600]
        for k, p in enumerate(sorted(pieces, key=lambda p: -p.area)):
            q = tidy(p, tol=4.0)
            brightness = mean_in(q, bri)
            pavements.append({"name": name if k == 0 else f"{name} ({k + 1})", "zone": zone, "surface": "concrete" if brightness > 2750 else "asphalt", "status": "sentinel2_derived",
                              "area_m2": round(q.area), "ring": r05(q.exterior.coords), "holes": [r05(hh.coords) for hh in q.interiors if Polygon(hh).area >= 300]})

    # roofs: very bright, neutral patches on the west side
    buildings = []
    bright = np.nan_to_num(bri)
    for seed, v in rings_of(bright, ROOF_SEED):
        t0, s0, t1, s1 = seed.bounds
        if v < ROOF_SEED or seed.area < 200 or not (-320 < s0 and s1 < 4100 and 100 < t0 and t1 < 290):
            continue
        rp = seed.representative_point()
        if red[cell(rp.x, rp.y)] > 0.3:
            continue
        r0, c0 = cell(t0, s0)
        r1, c1 = cell(t1, s1)
        peak = float(bright[r0:r1 + 1, c0:c1 + 1].max())
        level = min(max((peak + GROUND_BRIGHT) / 2, 3700.0), 5200.0)
        shapes = [g for g, vv in rings_of(bright, level) if vv >= level and g.intersects(seed)]
        if not shapes:
            continue
        for g in shapes:                                                                    # one bright patch can hold two roofs side by side
            if g.area < 200:
                continue
            q = box(*g.bounds)                                                              # the buildings stand square to the runway; at 10 m a roof is no more than its box
            if any(Polygon(b["ring"]).intersects(q) for b in buildings):                   # two seeds of one roof
                continue
            buildings.append({"id": "", "roof": "white", "height_m_estimated": 9 if q.area > 2000 else 6, "area_m2": round(q.area), "ring": r05(q.exterior.coords)})
    buildings.sort(key=lambda b: (min(p[1] for p in b["ring"])))
    for k, b in enumerate(buildings):
        b["id"] = f"ROOF_{k + 1}"
    biggest = max((b for b in buildings if max(p[1] for p in b["ring"]) < 400), key=lambda b: b["area_m2"])
    biggest["id"] = "HANGAR_MAIN"

    # the road west of the aerodrome: the darkest line, followed from the middle both ways
    def track(s_from, s_to, step, t_start):
        pts, t_prev = [], t_start
        for s in np.arange(s_from, s_to, step):
            cands = np.arange(t_prev - 14, t_prev + 14.1, RES)
            vals = [bri[cell(tt, s)[0], cell(tt, s)[1] - 4:cell(tt, s)[1] + 5].mean() if T_MIN + 5 < tt < T_MAX - 5 else 9e9 for tt in cands]
            t_prev = float(cands[int(np.argmin(vals))])
            pts.append([t_prev, float(s)])
        return pts
    south = track(3000, S_MAX - 40, 40, 280)
    north = track(2960, S_MIN + 40, -40, south[0][0])
    road = list(reversed(north)) + south
    # smooth it a little (the road is straighter than a pixel-wide track)
    sm = [[round(float(np.mean([p[0] for p in road[max(0, i - 2):i + 3]])), 1), round(p[1], 1)] for i, p in enumerate(road)]
    road = sm[::2]

    # true north in the frame: the true bearing from threshold to threshold (170.8 degrees; the AIP rounds the runway's to 171)
    la0, lo0, la1, lo1 = (math.radians(v) for v in (THR["17"]["lat"], THR["17"]["lon"], THR["35"]["lat"], THR["35"]["lon"]))
    b = math.atan2(math.sin(lo1 - lo0) * math.cos(la1), math.cos(la0) * math.sin(la1) - math.sin(la0) * math.cos(la1) * math.cos(lo1 - lo0))
    report["true_bearing_thr17_to_thr35_deg"] = round(math.degrees(b) % 360, 2)
    north_ts = [round(-math.sin(b), 4), round(math.cos(b), 4)]                                # north, in (t, s) per metre: to the east of the axis a little, and back along it
    out = {
        "provenance": {
            "runway": "AIP AD 2.12 (AMDT 11/26): 4000 x 50 m, true bearing 171/351; stopways 300 m (north of THR 17) and 60 m (south of THR 35)",
            "outlines": "pavements, sand islands, roofs and the road: derived from open satellite imagery, a median of 14 cloud-free Copernicus Sentinel-2 L2A scenes (10 m), "
                        + META["scenes"][-1]["datetime"][:10] + " to " + META["scenes"][0]["datetime"][:10] + ", by data/build_oeth_plan.py; accurate to about 10 m; outlines only",
            "attribution": META["attribution"],
            "zones": "which paved part is a taxiway and which an apron is read from the layout (links and loops between the runway and the aprons are taxiways); the AIP names taxiways A to F and T and "
                     "two aprons without giving their positions",
            "parked": "the three aeroplanes on the south apron stand where the composite shows aeroplanes on every date; the others are placed for the picture (t, s, heading 1 = nose north, 2 = nose south)",
            "frame": "metres in the runway frame: s from THR 17 towards THR 35 (south), t to the west of the centreline",
            "check": report,
        },
        "runway": {"length_m": 4000, "width_m": 50, "true_deg_17": 171.0, "stopway_north_m": 300, "stopway_south_m": 60, "north_in_ts_per_m": north_ts},
        "pavements": pavements, "islands": [r05(i.exterior.coords) for i in islands], "buildings": buildings, "lines": {"ACCESS_ROAD": road}, "parked_aeroplanes": PARKED,
    }
    json.dump(out, open(OUT, "w", encoding="utf-8"), separators=(",", ":"))
    print("wrote", OUT, os.path.getsize(OUT), "bytes;", len(pavements), "paved parts,", len(islands), "islands,", len(buildings), "roofs")
    print("imagery against the AIP runway:", report)
    for p in pavements:
        tt = [q[0] for q in p["ring"]]
        ss = [q[1] for q in p["ring"]]
        print(f"  {p['name']:26s} {p['zone']:8s} {p['surface']:8s} {p['area_m2']:7d} m2  t {min(tt):5.0f}..{max(tt):5.0f}  s {min(ss):6.0f}..{max(ss):6.0f}  {len(p['ring'])} vertices, {len(p['holes'])} holes")
    for bd in buildings:
        tt = [q[0] for q in bd["ring"]]
        ss = [q[1] for q in bd["ring"]]
        print(f"  {bd['id']:12s} {bd['area_m2']:6d} m2  t {min(tt):5.0f}..{max(tt):5.0f}  s {min(ss):6.0f}..{max(ss):6.0f}")
    compare_osm(buildings, pavements)
    if "--check-picture" in sys.argv:
        picture(R, G, B, out)


def compare_osm(buildings, pavements):
    """Print how the OpenStreetMap ways of the aerodrome compare (their geometry is not used)."""
    path = os.path.join(OPEN, "oeth_osm_check.json")
    if not os.path.exists(path):
        return
    for wy in json.load(open(path, encoding="utf-8"))["ways"]:
        pts = []
        for la, lo in wy["lat_lon"]:
            e, n = utm38(la, lo)
            pts.append(((e - E0) * WX + (n - N0) * WY, (e - E0) * UX + (n - N0) * UY))
        tt, ss = [p[0] for p in pts], [p[1] for p in pts]
        kind = wy["tags"].get("aeroway") or ("building" if "building" in wy["tags"] else "?")
        print(f"  OpenStreetMap way {wy['way']} ({kind}, {wy['timestamp'][:10]}): t {min(tt):5.0f}..{max(tt):5.0f}  s {min(ss):6.0f}..{max(ss):6.0f}")


def picture(R, G, B, plan):
    """data/open/oeth_plan_check.png: the outlines over the composite, for the eye (contains modified Copernicus Sentinel data)."""
    def stretch(x, lo, hi):
        return np.clip((x - lo) / (hi - lo), 0, 1)
    rgb = (np.dstack([stretch(R, 1500, 6500), stretch(G, 1200, 5200), stretch(B, 800, 3800)]) ** 0.8 * 255).astype(np.uint8)
    r0, c0 = cell(-80, -400)
    r1, c1 = cell(330, 4200)
    im = Image.fromarray(rgb[r0:r1, c0:c1])
    dr = ImageDraw.Draw(im)
    P = lambda t, s: ((s + 400) / RES, (t + 80) / RES)
    for p in plan["pavements"]:
        col = (60, 140, 255) if p["zone"] == "taxiway" else (255, 150, 30)
        dr.line([P(t, s) for t, s in p["ring"]], fill=col, width=1)
        for hh in p["holes"]:
            dr.line([P(t, s) for t, s in hh], fill=col, width=1)
    for bd in plan["buildings"]:
        dr.line([P(t, s) for t, s in bd["ring"]], fill=(0, 255, 0), width=1)
    dr.line([P(t, s) for t, s in plan["lines"]["ACCESS_ROAD"]], fill=(255, 255, 255), width=1)
    dr.rectangle([P(-RW, -300), P(RW, 4060)], outline=(255, 0, 255))
    im.save(os.path.join(OPEN, "oeth_plan_check.png"), optimize=True)
    print("wrote", os.path.join(OPEN, "oeth_plan_check.png"), im.size)


if __name__ == "__main__":
    main()
