"""Cover pictures for the handbook, upright (1792 x 2400, the size of the book's cover art): the C172 model and Thumamah (OETH) from the 3D scene.

`python3 -m figs.covers <name>` writes cache/covers/<name>.json, a recipe for blender/render_oeth.py; covers_post.py finishes the picture. Proposals for the
owner to choose from; nothing here is in the book.

What is real in them: the model and its paint; the runway (4 000 x 50 m, 171/351), its stopways, markings and lights (AD 2 OETH 2.12 and 2.14: white edge
lights every 60 m, green threshold, red end; on 35 a simple approach lighting system and PAPI on both sides); the book's open ground plan (pavements, roofs,
parked aeroplanes) on the SRTM relief. What is drawn for the look: the hour, the sky, the compass rose and the dashed track; in the remake of the present cover,
its painted sky and mesas are kept and only the aeroplane and the aerodrome are ours."""
import json
import math
import os
import sys

from figs import oeth3d as O
from figs.openers import rp, unit, runway_lights, L, HALF

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SIZE = [1792, 2400]
HD35 = O.heading(O.T35, O.T17)                              # the runway's direction for runway 35 (north-north-west); 17 is the opposite
BLUE_HOUR = {"horizon": "#DC8A45", "low": "#3C4A7A", "zenith": "#060E22", "strength": 0.6, "moon": 0.9, "moon_colour": "#FFB070", "moon_elevation": 4,
             "moon_azimuth": 262, "star_bright": 0.0}
DUSK = {"horizon": "#F2A64C", "low": "#5B5A78", "zenith": "#0A1730", "strength": 0.9, "moon": 3.0, "moon_colour": "#FFB870", "moon_elevation": 6,
        "moon_azimuth": 200, "star_bright": 0.0}


def norm(v):
    d = math.sqrt(sum(c * c for c in v))
    return [c / d for c in v]


def frame(azimuth, pitch):
    """The camera's own axes for a view along `azimuth` (degrees true) raised by `pitch` degrees: forward, right, up."""
    ax, ay = unit(azimuth)
    rx, ry = unit(azimuth + 90.0)
    c, s = math.cos(math.radians(pitch)), math.sin(math.radians(pitch))
    return [ax * c, ay * c, s], [rx, ry, 0.0], [-ax * s, -ay * s, c]


def along(p, *steps):
    q = list(p)
    for v, d in steps:
        q = [q[i] + v[i] * d for i in range(3)]
    return [round(c, 3) for c in q]


def plan(marks=True):
    return O.aerodrome_18_01()["plan"] if marks else O.open_plan()


def parked(model="low", only=None):
    out = []
    for k, a in enumerate(O.aerodrome_18_01(scale=1.0)["aircraft"]):
        if only is None or k in only:
            out.append(dict(a, model=model))
    return out


def base(rid, camera, **kw):
    r = {"id": rid, "camera": camera, "size": list(SIZE), "samples": 128, "exposure": 0.25, "look": "AgX - Medium High Contrast", "transparent": True,
         "keep_sources": O.KEEP_SOURCES, "plan": plan(), "far_ground_size": 3000000, "clip_end": 2000000}
    r.update(kw)
    return r


def approach_lights(size, strength):
    """The simple approach lighting system of runway 35: lights on the extended centreline every 60 m for 420 m and a crossbar at 300 m."""
    return [{"points": [rp(L + 60.0 * k, 0.0) for k in range(1, 8)], "colour": "#FFF3D6", "size": size, "strength": strength, "power": 260.0, "light_every": 2, "lift": 0.8},
            {"points": [rp(L + 300.0, t) for t in (-13.5, -9.0, -4.5, 4.5, 9.0, 13.5)], "colour": "#FFF3D6", "size": size, "strength": strength, "lift": 0.8}]


def remake():
    """The present cover with our aeroplane and our aerodrome: its painted sky and mesas are kept (covers_post.py); this render gives the valley floor (Thumamah
    seen from the north, runway 17 running away, the aprons on the right) and the model above it, from a camera worked out from the painted runway: the horizon
    at 0.774 of the height, the runway's vanishing point at 0.776 of the width, its near end 50 m wide over 370 pixels."""
    az, pitch, lens = 171.0 - 15.9, 22.32, 24.0
    f, rt, up = frame(az, pitch)
    fh = [f[0] / math.cos(math.radians(pitch)), f[1] / math.cos(math.radians(pitch)), 0.0]
    n = rp(0.0, 0.0, 0.0)
    cam = along(n, (fh, -242.8), (rt, -16.74))
    cam[2] = 22.6
    r = base("cover-remake", {"at": cam, "look": along(cam, (f, 100.0)), "lens": lens}, night=dict(DUSK),
             haze={"start": 500.0, "depth": 7000.0, "colour": "#E7A24F", "strength": 0.9})
    # seen low and against the light: the ground at one level (the runway's) for 600 m round the pavements, in place of the two levels the scene was graded
    # to; and no shadows from the pavements and the paint, which lie a little above the ground (each edge threw a long black line across the valley)
    r["plan"] = dict(r["plan"], flatten={"inner": 600.0, "outer": 1800.0, "z": -0.01}, flat_shadows=False)
    r["lights"] = runway_lights(size=0.5, strength=16.0)
    r["lights"][1]["colour"], r["lights"][2]["colour"] = "#FF3A2A", "#49FF86"     # seen from the north: the threshold of 17 green before us, the far end red
    # the model where the painted aeroplane is (its nose, tail and wingtips fitted to the painting's, 24 pixels rms): 11.5 m from the camera, heading north,
    # as after a takeoff from runway 35 toward the viewer
    ac = along(cam, (f, 11.474), (rt, -1.861), (up, 0.314))
    r["aircraft"] = [{"at": ac, "heading": 0.6, "pitch": -6.9, "bank": -7.0, "attitude": "body", "model": "high", "prop": {"alpha": 0.1},
                      "lights": {"nav": 26.0, "beacon": 30.0},
                      "anchors": {"tail": [0.0, 5.7, 1.5], "nose": [0.0, -2.1, 1.38], "tipL": [5.45, 0.2, 1.98], "tipR": [-5.45, 0.2, 1.98], "hub": [0.0, -1.93, 1.385]}}] + parked()
    # the light of the painting: warm from the glow at the horizon, below and ahead of the viewer (the undersides lit gold), cool and faint from the sky above
    r["spots"] = [{"at": along(cam, (rt, -7.0), (up, -6.0), (f, 2.0)), "look": ac, "power": 3800.0, "size": 6.0, "colour": "#FFC98A"},
                  {"at": along(ac, (fh, 22.0), (up, -9.0), (rt, 6.0)), "look": ac, "power": 9000.0, "size": 10.0, "colour": "#FFA646"},
                  {"at": along(ac, (up, 20.0), (rt, -12.0)), "look": ac, "power": 1700.0, "size": 18.0, "colour": "#7F9CFF"}]
    r["anchors"] = {"t17": n, "t17l": rp(0.0, -HALF, 0.0), "t17r": rp(0.0, HALF, 0.0), "mid": rp(900.0, 0.0, 0.0), "far": rp(L, 0.0, 0.0),
                    "hz": along(cam, (fh, 600000.0))[:2] + [0.0]}
    return r


def sunrise():
    """Over the field at sunrise: the model banking above the northern aprons, the low sun behind the viewer's right shoulder, long shadows, the runway
    running away to the north-west of the picture."""
    g = rp(650.0, 200.0, 0.0)
    cam = rp(1561.0, -507.0, 560.0)
    d = norm([g[0] - cam[0], g[1] - cam[1], 0.0])
    az = math.degrees(math.atan2(d[0], d[1])) % 360.0
    f, rt, up = frame(az, -8.8)
    r = base("cover-sunrise", {"at": cam, "look": along(cam, (f, 1000.0)), "lens": 28}, exposure=-0.1,
             sun={"elevation": 8.0, "azimuth": 104.0, "energy": 5.4, "colour": "#FFC08A", "sky": 0.5, "angle": 2.5},
             ground_image=O.ground_texture(), haze={"start": 6000.0, "depth": 28000.0, "colour": "#F4D8B6", "strength": 0.93})
    ac = along(cam, (norm([f[i] + 0.01 * rt[i] - 0.07 * up[i] for i in range(3)]), 15.5))
    r["aircraft"] = [{"at": ac, "heading": (az + 180.0 + 55.0) % 360.0, "pitch": 3.0, "bank": -12.0, "attitude": "body", "model": "high", "prop": {"alpha": 0.1},
                      "lights": {"nav": 14.0, "beacon": 18.0}, "anchors": {"tail": [0.0, 5.7, 1.5], "nose": [0.0, -2.1, 1.38], "mid": [0.0, 1.2, 1.4]}}] + parked()
    r["anchors"] = {"g": g, "t17": rp(0.0, 0.0, 0.0), "rmid": rp(1400.0, 0.0, 0.0), "t35": rp(L, 0.0, 0.0), "hz": along(cam, ([f[0], f[1], 0.0], 600000.0))[:2] + [0.0]}
    return r


def papi(size, strength):
    """The PAPI of runway 35, on both sides (AD 2 OETH 2.14: 3 degrees): four units each side abeam the aiming point; on the path the two nearer the
    runway show red and the two outer ones white."""
    s0 = L - 390.0
    red = [rp(s0, sg * (HALF + 15.0 + 9.0 * k)) for sg in (-1, 1) for k in (0, 1)]
    white = [rp(s0, sg * (HALF + 15.0 + 9.0 * k)) for sg in (-1, 1) for k in (2, 3)]
    return [{"points": red, "colour": "#FF2A1F", "size": size, "strength": strength, "lift": 0.6}, {"points": white, "colour": "#FFF6E0", "size": size, "strength": strength, "lift": 0.6}]


def touchdown():
    """Short final for runway 35 at the blue hour, from behind and above the model: its landing light on the approach lights, the green threshold, the PAPI
    and the edge lights running to one point, the red end lights 4 km off."""
    ac = rp(L + 470.0, 0.0, 25.5)                          # beyond the first approach light, on a 3 degree path
    r = base("cover-touchdown", {"aircraft": 0, "at": [0.8, 13.2, 4.3], "look": [0.0, -70.0, -2.6], "lens": 26}, exposure=1.0,
             night=dict(BLUE_HOUR, strength=0.85, moon=0.7, moon_colour="#9FB4FF", moon_elevation=38, moon_azimuth=115), ground_image=O.ground_texture(),
             haze={"start": 900.0, "depth": 9000.0, "colour": "#3B4268", "strength": 0.85, "glare": {"threshold": 2.6, "strength": 0.7, "size": 0.5, "size_steps": 7}})
    r["aircraft"] = [{"at": ac, "heading": HD35, "pitch": 2.5, "bank": 0.0, "attitude": "body", "model": "high", "prop": {"alpha": 0.06},
                      "lights": {"nav": 60.0, "beacon": 80.0, "strobe": 16.0, "landing": {"power": 30000.0, "angle": 34.0, "down": 4.5, "strength": 300.0}},
                      "anchors": {"tail": [0.0, 5.7, 1.5], "tipL": [5.45, 0.2, 1.98], "tipR": [-5.45, 0.2, 1.98]}}]
    edge = runway_lights(size=0.6, strength=34.0)
    edge[0]["power"] = 1500.0
    r["lights"] = edge + approach_lights(0.42, 20.0) + papi(0.55, 34.0)
    r["lights"][3]["power"] = 420.0
    fx, fy = unit(HD35)
    lx, ly = -fy, fx
    r["spots"] = [{"at": [ac[0] - fx * 14.0 + lx * 9.0, ac[1] - fy * 14.0 + ly * 9.0, ac[2] + 10.0], "look": [ac[0], ac[1], ac[2] + 1.4], "power": 1500.0, "size": 8.0, "colour": "#AFC0FF"},
                  {"at": [ac[0] + fx * 16.0 + lx * 12.0, ac[1] + fy * 16.0 + ly * 12.0, ac[2] - 1.0], "look": [ac[0], ac[1], ac[2] + 1.4], "power": 1100.0, "size": 10.0, "colour": "#FFB070"}]
    r["anchors"] = {"thr": rp(L, 0.0, 0.0), "end": rp(0.0, 0.0, 0.0), "hz": [round(ac[0] + fx * 600000.0, 1), round(ac[1] + fy * 600000.0, 1), 0.0]}
    return r


def cockpit():
    """From the pilot's seat, lined up on runway 35 at the blue hour: the model's own panel (the six instruments, the radios, the compass) lit softly,
    the landing light on the centreline, the edge lights running away."""
    ac = rp(L - 60.0, 0.0, 0.0)
    r = base("cover-cockpit", {"aircraft": 0, "at": [0.21, -0.02, 1.655], "look": [0.17, -3.0, 1.06], "lens": 19, "clip_start": 0.02}, exposure=1.0,
             night=dict(BLUE_HOUR, strength=1.5, moon=1.5, moon_colour="#9FB4FF", moon_elevation=38, moon_azimuth=115),
             haze={"start": 900.0, "depth": 9000.0, "colour": "#3B4268", "strength": 0.85, "glare": {"threshold": 3.0, "strength": 0.55, "size": 0.45, "size_steps": 7}})
    r["aircraft"] = [{"at": ac, "heading": HD35, "pitch": 0.0, "bank": 0.0, "attitude": "body", "on_ground": True, "model": "high",
                      "hide": ["AIRFRAME.windshield", "POWERPLANT.propeller"],
                      "lights": {"landing": {"power": 260000.0, "angle": 46.0, "down": 4.5, "strength": 40.0}},
                      "emit": {"instrument_dials": 1.5, "panel_misc": 0.9, "panel_placards": 0.8},
                      # the panel as it would read there: the aerodrome's elevation (1 870 ft; the threshold of 35 is at 1 868 ft: AD 2 OETH 2.2 and 2.12), at rest on the
                      # ground, the engine idling, the heading of runway 35 (351 degrees true, about 347 magnetic with the AIP's 3 degrees east of 2015: shown as 350)
                      "pose": {"ALT": 1870.0, "ASI": 0.0, "VSI": 0.0, "TACH": 1000.0, "SUCTION": 4.8, "heading": 350.0},
                      "lamps": [{"at": [0.05, -0.02, 1.70], "power": 3.6, "colour": "#FFD3A0", "size": 0.05}, {"at": [0.22, -0.38, 1.50], "power": 0.6, "colour": "#FFC890", "size": 0.03},
                                {"at": [0.24, 0.10, 1.18], "power": 1.6, "colour": "#FFCFA0", "size": 0.06}]}]
    edge = runway_lights(size=0.5, strength=30.0)
    edge[0]["power"] = 1500.0
    r["lights"] = edge
    fx, fy = unit(HD35)
    r["anchors"] = {"end": rp(0.0, 0.0, 0.0), "hz": [round(ac[0] + fx * 600000.0, 1), round(ac[1] + fy * 600000.0, 1), 0.0]}
    return r


def topdown():
    """Straight down on the threshold of runway 17 at sunrise, south at the top so that the 17 reads: the numbers, the stopway's chevrons, the turn loop and
    the aprons with their long shadows, and the model crossing close under the viewer."""
    # the view is laid out for the cover page: its title and facts cover the top quarter and its foot the last quarter, so the designator and the model lie between
    cam = rp(86.0, 100.0, 430.0)
    r = base("cover-topdown", {"at": cam, "look": rp(86.0, 100.0, 0.0), "lens": 35, "roll": 180.0 - (360.0 - HD35)}, exposure=-0.2,
             sun={"elevation": 15.0, "azimuth": 100.0, "energy": 5.4, "colour": "#FFC790", "sky": 0.55, "angle": 2.0})
    ac = rp(88.1, 101.0, 404.0)
    r["aircraft"] = [{"at": ac, "heading": 218.0, "pitch": 0.0, "bank": 14.0, "attitude": "body", "model": "high", "prop": {"alpha": 0.1},
                      "anchors": {"tail": [0.0, 5.7, 1.5], "nose": [0.0, -2.1, 1.38]}}] + parked()
    r["anchors"] = {"t17": rp(0.0, 0.0, 0.0), "s300": rp(300.0, 0.0, 0.0), "west": rp(0.0, 200.0, 0.0)}
    return r


RECIPES = {"cover-remake": remake, "cover-sunrise": sunrise, "cover-touchdown": touchdown, "cover-cockpit": cockpit, "cover-topdown": topdown}


if __name__ == "__main__":
    name = sys.argv[1]
    os.makedirs(os.path.join(HERE, "cache", "covers"), exist_ok=True)
    out = os.path.join(HERE, "cache", "covers", name + ".json")
    with open(out, "w") as f:
        json.dump(RECIPES[name](), f)
    print(out)
