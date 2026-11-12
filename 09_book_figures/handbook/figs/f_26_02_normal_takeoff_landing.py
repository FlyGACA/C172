"""Figure 26-2. Normal takeoff and normal landing seen from the side. Two scenes in cards: a runway of the Peninsula seen almost edge-on (dark asphalt, white markings, edge lights), pale
hills on the horizon, a desert plain with scrub, a windsock; the model seen from the right at each of the nine places of the old figure (the same points, the same attitudes), the
paths as lines with a casing, the speed boxes as small cards, the ten numbered callouts of the old figure kept in their places (figs/h_a1.py and figs/scene.py make the pieces)."""
import math

from figs import h_a1 as H
from figs import scene as S

CX = -6.8              # the middle of an old aeroplane lies this far behind the point of its group where its main wheels touch (canvas units)
W = 88.0
ASPECT = 0.2922
A = (8, 6, 624, 204)
B = (8, 220, 624, 204)
GYA, GYB = 178.5, 395.0


def plane(tx, ty, angle, lowered=False):
    """The model where the old aeroplane stood: turned about the old one's ground point (the group's origin; 14.4 lower when the group was translated 18)."""
    h = W * ASPECT
    lx, ly = CX, (14.4 if lowered else 0.0) - h / 2
    a = math.radians(angle)
    o = {"name": "sprite-side", "at": [round(tx + lx * math.cos(a) - ly * math.sin(a), 1), round(ty + lx * math.sin(a) + ly * math.cos(a), 1)], "width": W, **H.LOOK}
    if angle:
        o["angle"] = angle
    return o


UPPER = [(70, 178, 0, False), (215, 178, -8, False), (330, 168, -9, True), (480, 94, -11, True)]
LOWER = [(110, 292.1, 2, True), (248, 359.6, -3, True), (372, 389, -6, False), (470, 395, -8, False), (590, 395, 0, False)]

PATH1 = ("M 40 178 C 45 178 40.8 178 70 178 C 99.2 178 179.2 178.3 215 178 C 250.8 177.7 265.8 177.7 285 176 C 304.2 174.3 310.8 174 330 168 C 349.2 162 375 152.3 400 140 "
         "C 425 127.7 443.3 112.3 480 94 C 516.7 75.7 596.7 40.7 620 30")
PATH2 = ("M 20 250 C 35 257 79.7 277.9 110 292.1 C 140.3 306.3 181.7 325.6 202 335.1 C 222.3 344.6 215.7 341.8 232 349.2 C 248.3 356.5 276.7 372.4 300 379 "
         "C 323.3 385.6 350.3 386.7 372 389 C 393.7 391.3 413.7 392 430 393 C 446.3 394 463.3 394.7 470 395 L 612 395")


def gradients():
    return ('<defs><linearGradient id="a1pth1" gradientUnits="userSpaceOnUse" x1="240" y1="0" x2="320" y2="0"><stop offset="0" stop-color="#E0761A"/><stop offset="1" stop-color="#1D4ED8"/></linearGradient>'
            '<linearGradient id="a1pth2" gradientUnits="userSpaceOnUse" x1="170" y1="0" x2="520" y2="0"><stop offset="0" stop-color="#1D4ED8"/><stop offset="0.5" stop-color="#1D4ED8"/>'
            '<stop offset="0.8" stop-color="#079669"/><stop offset="1" stop-color="#E0761A"/></linearGradient></defs>')


def world_a():
    x, y, w, h = A
    land = H.backdrop("a1a", x, x + w, GYA, y + h, seed=5, far=24, mid=11, base=13, palms=[(588, GYA - 6, 0.55)], acacias=[(24, GYA - 5, 0.55)])
    land += H.hangar(598, GYA - 6, 30, 16)
    land += H.runway("a1ra", x, x + w, GYA, half=4.2, centre=True, threshold=False)
    land += H.windsock(436, GYA - 6.5, 24, wind=-1)
    for tx in (150, 235):                                              # the points of the old figure where the aeroplane rotates and lifts off
        land += H.line_cased(tx, GYA - 14, tx, GYA - 1, "#3B4A63", 1.0, dash="2.4 2.4", casing=1.8, opacity=0.9)
    return S.card_front("a1aw", x, y, w, h, land, radius=10)


def world_b():
    x, y, w, h = B
    land = H.backdrop("a1b", x, x + w, GYB, y + h, seed=9, far=24, mid=11, base=13, palms=[(86, GYB - 6, 0.55), (104, GYB - 4, 0.45)], acacias=[(600, GYB - 5, 0.5)])
    land += H.hangar(24, GYB - 6, 40, 20)
    land += H.runway("a1rb", 240, x + w, GYB, half=4.2, centre=True, threshold=True, aim=330, dash_from=270)
    land += H.windsock(206, GYB - 6.5, 24, wind=-1)
    return S.card_front("a1bw", x, y, w, h, land, radius=10)


def clouds():
    c = lambda name, cx, cy, w, op=0.95: {"name": name, "at": [cx, cy], "width": w, "opacity": op, "haze": {"colour": "#CFE0F3", "amount": 0.18}}
    return [c("cloud-cumulus-b", 60, 40, 74), c("cloud-cumulus-a", 262, 34, 92), c("cloud-cumulus-b", 560, 28, 60, 0.85),
            c("cloud-cumulus-a", 372, 256, 96), c("cloud-cumulus-b", 586, 262, 70)]


def foreground():
    out = []
    for (box, gy, seed) in ((A, GYA, 5), (B, GYB, 9)):
        x, y, w, h = box
        inner = H.edge_lights(x, x + w, gy, 4.2) if box is A else H.edge_lights(240, x + w, gy, 4.2)
        inner += S.scrub(seed + 40, x + 6, x + w - 6, gy + 12, y + h - 3, 11, scale=1.25)
        out.append(S.card_front(f"a1f{seed}", x, y, w, h, inner, radius=10))
    return out


def shadows():
    out = []
    for (tx, ty, ang, low) in UPPER + LOWER:
        gy = GYA if ty < 215 else GYB
        height = (gy - ty) - (0 if not low else -14.4)
        if height > 60:
            continue
        out.append(H.drop_shadow(tx + 12 + max(0, height) * 0.25, gy + 1.5, 64, 2.4, 0.42 if height < 6 else 0.28))
    return "".join(out)


def callouts():
    c = S.callout
    return "".join([c(1, 70, 120, 70, 152), c(2, 215, 112, 214, 151), c(3, 330, 100, 331, 149), c(4, 560, 150, 502, 108),
                    c(5, 110, 252, 110, 276), c(6, 330, 412, 330, 402), c(7, 232, 306, 244, 334.6), c(8, 392, 318, 378, 361), c(9, 470, 330, 470, 365), c(10, 590, 340, 590, 369)])


def arrow_dir():
    return S.ribbon("a1dir", [(14, 120), (30, 120), (47, 120)], 6.5, "#1E3A8A", "#93B4EF", opacity=0.95, head=2.2)


def paths():
    out = [H.path_line(PATH1, "url(#a1pth1)", 2.1, dash="7 5", casing=1.8)]
    out.append(H.path_line(PATH2, "url(#a1pth2)", 2.6, casing=2.2))
    out.append(H.line_cased(232, 349.2, 330, 395, "#7B8799", 1.3, dash="4 4", casing=2.0))
    return "".join(out)


def layers():
    out = [f'<defs>{S.gradient("a1page", [(0, "#F1F5FA"), (1, "#E6EDF5")])}</defs><rect x="0" y="0" width="640" height="430" fill="url(#a1page)"/>', H.defs(), gradients()]
    for (box, k, key) in ((A, "A", "a1ca"), (B, "B", "a1cb")):
        x, y, w, h = box
        out.append(S.card(key, x, y, w, h, H.SKY, S.glow(key + "g", x + 80, y + 70, 190, "#FFF1CC", 0.5), radius=10))
    out.extend(clouds())
    out.append(world_a())
    out.append(world_b())
    # the aiming point, as the old figure had it: a block on the runway at the foot of the path's dashed extension
    out.append(paths())
    out.append(shadows())
    out.append(H.puff(464, 394.5, 7, 4, 3, 0.9))
    for (tx, ty, ang, low) in UPPER + LOWER:
        out.append(plane(tx, ty, ang, low))
    out.extend(foreground())
    out.append(arrow_dir())
    out.append(H.speed_card("a1c1", 107, 59, "VR 55", 0))
    out.append(H.leader(160, 101, 205, 150))
    out.append(H.speed_card("a1c2", 367, 33, "VY 75", 0))
    out.append(H.leader(433, 62, 478, 82))
    out.append(H.speed_card("a1c3", 163, 231, "65", 30, flap_colour="#F59E0B", mono=False))
    out.append(callouts())
    return H.flatten(out)


def plate():
    return {
        "id": "fig-26-02-normal-takeoff-landing",
        "replaces": "fig-26-02-normal-takeoff-landing.svg",
        "book_file": "plate-26-02-normal-takeoff-landing.jpg",
        "caption": "Figure 26-2. Normal takeoff and normal landing seen from the side",
        "desc": "Figure 26-2. Normal takeoff and normal landing seen from the side",
        "legend": [
            "Takeoff roll at full power, rudder keeping the nose on the centreline.",
            "Rotation at `VR` 55 kt to the takeoff attitude.",
            "Lift-off, wings level, attitude held.",
            "Climb at `VY` 75 kt.",
            "Final at 65 kt, flaps 30°.",
            "The aiming point.",
            "Round out (flare): throttle closed, nose raised progressively.",
            "Hold-off just above the runway as the speed decays.",
            "Touchdown on the main wheels, nose high, near the stall speed.",
            "Nosewheel lowered; rollout on the centreline.",
        ],
        "canvas": [640, 430],
        "background": "pale",
        "reskin": {"svg": "fig-26-02-normal-takeoff-landing.svg", "blank": True, "layers": layers()},
    }
