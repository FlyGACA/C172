"""Opening pictures for the parts of the handbook: the C172 model and Thumamah (OETH) from the 3D scene, in the manner of the book's cover (a deep blue sky that
turns amber at the horizon, a warm low light, a fine compass rose in the sky and a dashed golden track). Decorative: no callouts, no numbers, no claim.

Not figures. `python3 -m figs.openers <name>` writes cache/openers/<name>.json, a recipe for blender/render_oeth.py; openers_post.py then lays the sky, the
compass rose and the track, and gives the render its painted finish.

What is real in them: the runway, its lights (AD 2 OETH 2.14: white edge lights every 60 m, green threshold, red end; width 50 m) and the ground (the book's open
plan on the SRTM relief, under the open picture of the ground). What is not: the hour, the weather and the track, which are drawn for the look."""
import json
import math
import os
import sys

from figs import oeth3d as O

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
L = O._L                                                 # the runway's length, threshold to threshold
HALF = 25.0                                              # half its width (50 m)
DUSK = {"horizon": "#F2A64C", "low": "#5B5A78", "zenith": "#0A1730", "strength": 0.9, "moon": 3.2, "moon_colour": "#FFB870", "moon_elevation": 7,
        "moon_azimuth": 252, "star_bright": 0.0}
HAZE = {"start": 600.0, "depth": 9000.0, "colour": "#E19A52", "strength": 0.92, "glare": {"threshold": 2.2, "strength": 0.9, "size": 0.55, "size_steps": 7}}


def rp(s, t, z=None):
    x, y = O.runway_point(s, t)
    return [round(x, 1), round(y, 1)] + ([z] if z is not None else [])


def runway_lights(size=2.6, strength=70.0):
    """The runway's lights as the AIP gives them, drawn large so that they read from the air: white along both edges every 60 m, green across the
    threshold of 35 (the south end), red across the far end."""
    n = int(L // 60.0)
    edges = [rp(60.0 * k, t) for k in range(n + 1) for t in (-HALF - 1.5, HALF + 1.5)]
    across = [-HALF + 3.0 + (2 * HALF - 6.0) * k / 10.0 for k in range(11)]
    return [{"points": edges, "colour": "#FFE9B8", "size": size, "strength": strength, "power": 900.0, "light_every": 3, "lift": 0.8},
            {"points": [rp(L + 4.0, t) for t in across], "colour": "#49FF86", "size": size, "strength": strength, "lift": 0.8},
            {"points": [rp(-4.0, t) for t in across], "colour": "#FF3A2A", "size": size, "strength": strength, "lift": 0.8}]


def unit(bearing):
    a = math.radians(bearing)
    return math.sin(a), math.cos(a)


def bezier(p0, p1, p2, p3, n):
    out = []
    for i in range(n + 1):
        t = i / n
        a, b, c, d = (1 - t) ** 3, 3 * t * (1 - t) ** 2, 3 * t * t * (1 - t), t ** 3
        out.append([round(a * p0[k] + b * p1[k] + c * p2[k] + d * p3[k], 2) for k in range(3)])
    return out


def base(rid, camera, size=(2200, 1000)):
    return {"id": rid, "camera": camera, "size": list(size), "samples": 128, "exposure": 0.25, "look": "AgX - Medium High Contrast", "transparent": True,
            "keep_sources": O.KEEP_SOURCES, "plan": O.open_plan(), "ground_image": O.ground_texture(), "far_ground_size": 3000000, "clip_end": 2000000,
            "night": dict(DUSK), "haze": dict(HAZE), "lights": runway_lights()}


def departure():
    """Part 1 (and the pattern of the set): just after takeoff from runway 35, the model in a climbing turn toward the viewer, the lit runway going away to
    the south behind it, the dashed track from the runway up to its tail."""
    hd35 = O.heading(O.T35, O.T17)                        # the runway's direction for a takeoff on 35
    ac = rp(-1250.0, 420.0, 165.0)                        # 1 250 m past the far end, 420 m west of the centreline, about 540 ft above the field
    ahd = (hd35 + 32.0) % 360.0
    fx, fy = unit(ahd)
    cx, cy = unit((hd35 + 8.0) % 360.0)                   # the camera ahead of the aeroplane and to its left, a little below it
    cam = [round(ac[0] + cx * 17.5, 2), round(ac[1] + cy * 17.5, 2), ac[2] - 2.0]
    look = [round(ac[0] - cx * 60.0, 2), round(ac[1] - cy * 60.0, 2), ac[2] + 4.4]
    r = base("opener-departure", {"at": cam, "look": look, "lens": 25})
    r["aircraft"] = [{"at": ac, "heading": ahd, "pitch": 6.0, "bank": 10.0}]
    r["spots"] = [{"at": [cam[0], cam[1], cam[2] + 3.0], "look": ac, "power": 5200.0, "size": 5.0, "colour": "#FFE2B8"},
                  {"at": [ac[0] + 30.0, ac[1] - 10.0, ac[2] + 40.0], "look": ac, "power": 2600.0, "size": 20.0, "colour": "#9FB6FF"}]
    tail = [round(ac[0] - fx * 5.6, 2), round(ac[1] - fy * 5.6, 2), ac[2] + 2.0]
    # the track is drawn on the picture (openers_post.py), as on the cover: from the middle of the runway, on toward its far end and round up to the tail
    r["anchors"] = {"ac": ac, "tail": tail, "rwy_mid": rp(0.5 * L, 0.0, 1.0), "rwy_end": rp(0.0, 0.0, 1.0),
                    "hz": [round(ac[0] - cx * 600000.0, 1), round(ac[1] - cy * 600000.0, 1), 0.0]}
    r["track"] = {"from": "rwy_mid", "through": "rwy_end", "to": "tail", "swing": [0.20, 0.30]}
    return r


def final():
    """Part 7 (the flight training manual): short final for runway 35, seen from behind and a little above the model: the runway ahead with its white edge
    lights, the green threshold, the simple approach lights and the PAPI of 35 (AD 2 OETH 2.14)."""
    hd35 = O.heading(O.T35, O.T17)
    fx, fy = unit(hd35)
    lx, ly = -fy, fx                                       # to the left of the track
    d, zh = 330.0, 18.5                                    # 330 m short of the threshold, on a 3 degree path
    ac = rp(L + d, 0.0, zh)
    cam = [round(ac[0] - fx * 11.5 + lx * 1.6, 2), round(ac[1] - fy * 11.5 + ly * 1.6, 2), zh + 4.3]
    aim = [round(ac[0] + fx * 150.0, 2), round(ac[1] + fy * 150.0, 2), zh - 25.0]
    r = base("opener-final", {"at": cam, "look": aim, "lens": 24})
    r["aircraft"] = [{"at": ac, "heading": hd35, "pitch": -1.5, "bank": 0.0}]
    r["spots"] = [{"at": [cam[0], cam[1], cam[2] + 2.0], "look": ac, "power": 3200.0, "size": 5.0, "colour": "#FFE2B8"}]
    r["lights"] = runway_lights(size=1.1, strength=26.0) + [
        {"points": [rp(L + 60.0 * k, 0.0) for k in range(1, 8)], "colour": "#FFF3D6", "size": 0.9, "strength": 22.0, "power": 300.0, "light_every": 2, "lift": 0.8},
        {"points": [rp(L + 300.0, t) for t in (-13.5, -9.0, -4.5, 4.5, 9.0, 13.5)], "colour": "#FFF3D6", "size": 0.9, "strength": 22.0, "lift": 0.8}]
    r["emit"] = {"Light": 12.0}
    r["haze"] = dict(HAZE, start=900.0, depth=11000.0, strength=0.9, glare={"threshold": 3.0, "strength": 0.45, "size": 0.4, "size_steps": 6})
    r["anchors"] = {"ac": ac, "hz": [round(ac[0] + fx * 600000.0, 1), round(ac[1] + fy * 600000.0, 1), 0.0]}
    r["rose"] = {"at": [0.5, 0.2], "r": 0.5}
    return r


def circuit():
    """Part 5 (airspace, radio and navigation): Thumamah from the south-east at dusk, its runway lit, the left-hand circuit of runway 35 (west of the runway, at
    2 900 ft: AD 2 OETH 2.22) as the dashed track, the model on the downwind leg, enlarged so that it reads."""
    hd35 = O.heading(O.T35, O.T17)
    H = 314.0                                              # 1 030 ft above the aerodrome
    D = 1700.0                                             # the downwind leg's distance from the runway, for the picture
    legs = [(L, 0.0, 0.0), (L * 0.55, 0.0, 15.0), (-1200.0, 0.0, 180.0), (-1200.0, D, H), (L + 1500.0, D, H), (L + 1500.0, 0.0, 130.0), (L, 0.0, 15.0)]
    track = []
    for (s0, t0, z0), (s1, t1, z1) in zip(legs, legs[1:]):
        n = max(2, int(math.hypot(s1 - s0, t1 - t0) / 55.0))
        track += [rp(s0 + (s1 - s0) * i / n, t0 + (t1 - t0) * i / n, round(z0 + (z1 - z0) * i / n, 1)) for i in range(n)]
    cam = rp(L + 4300.0, -3300.0, 1500.0)
    r = base("opener-circuit", {"at": cam, "look": rp(L * 0.42, 700.0, 0.0), "lens": 30})
    ac = rp(L * 0.5, D, H)
    r["aircraft"] = [{"at": ac, "heading": (hd35 + 180.0) % 360.0, "scale": 14.0}]
    r["lights"] = runway_lights(size=7.0, strength=60.0)
    r["haze"] = dict(HAZE, start=3500.0, depth=26000.0, strength=0.9)
    r["anchors"] = {f"t{i:03d}": p for i, p in enumerate(track)}
    r["anchors"].update({"ac": ac, "hz": [round(cam[0] + (ac[0] - cam[0]) * 400.0, 1), round(cam[1] + (ac[1] - cam[1]) * 400.0, 1), 0.0]})
    r["track_depths"] = [round(math.dist(p, cam), 1) for p in track]
    r["rose"] = {"at": [0.72, 0.02], "r": 0.42}
    return r


RECIPES = {"opener-departure": departure, "opener-final": final, "opener-circuit": circuit}


if __name__ == "__main__":
    name = sys.argv[1]
    os.makedirs(os.path.join(HERE, "cache", "openers"), exist_ok=True)
    out = os.path.join(HERE, "cache", "openers", name + ".json")
    with open(out, "w") as f:
        json.dump(RECIPES[name](), f)
    print(out)
