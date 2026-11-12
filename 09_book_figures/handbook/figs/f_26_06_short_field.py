"""Figure 26-6. Short-field takeoff over an obstacle, and short-field approach and landing. Two scenes in cards: a runway of the Peninsula seen almost edge-on with a lattice mast
at the obstacle's place (a red light on its top), pale hills on the horizon, the model seen from the right at the places of the old figure, the VX climb and the VY climb as lines
with a casing, the speed boxes as small cards, the eleven numbered callouts of the old figure kept (figs/h_a1.py and figs/scene.py make the pieces)."""
from figs import h_a1 as H
from figs import scene as S

A = (8, 6, 624, 213)
B = (8, 226, 624, 208)
GYA, GYB = 193.5, 410.0
GREEN, BLUE, GREY = "#047857", "#1D4ED8", "#8391A6"
W = 84.0

# (x, y, angle, flap marks): the aeroplanes of the old figure
UPPER = [(52, 193, 0, 10), (204, 193, -8, 10), (330, 151.5, -14, 10), (560, 92.3, -10, 0)]
LOWER = [(70, 297.4, 4, 30), (262, 410, -9, 30)]


def world_a():
    land = H.mast(430, GYA + 1.5, 48, 12, 4) + H.windsock(608, GYA - 6.5, 24, wind=-1)
    return H.profile("a1a", A, GYA, seed=11, sun=(80, 70), runway_args={"x0": 14, "x1": 330, "threshold": True, "half": 4.2, "dash_from": 30},
                     clouds=[H.cloud("cloud-cumulus-b", 92, 40, 78), H.cloud("cloud-cumulus-a", 372, 34, 74), H.cloud("cloud-cumulus-b", 596, 26, 52, 0.85)],
                     palms=[(520, GYA - 6, 0.55), (538, GYA - 5, 0.45)], objects=land)


def world_b():
    land = H.mast(130, GYB + 1.5, 48, 12, 4) + H.windsock(598, GYB - 6.5, 24, wind=-1)
    return H.profile("a1b", B, GYB, seed=17, sun=(80, 70), runway_args={"x0": 190, "x1": 630, "threshold": True, "aim": 215, "half": 4.2, "dash_from": 240},
                     clouds=[H.cloud("cloud-cumulus-a", 330, 262, 84), H.cloud("cloud-cumulus-b", 520, 300, 74), H.cloud("cloud-cumulus-b", 594, 250, 52, 0.85)],
                     palms=[(60, GYB - 6, 0.55), (78, GYB - 4, 0.45)], objects=land)


def paths():
    out = [H.path_line("M 30 193 C 53.3 193 140 193 170 193 C 200 193 203.3 193 210 193", BLUE, 1.9, dash="6 5", casing=1.8)]
    out.append(H.line_cased(210, 193, 628, 122.8, GREY, 1.8, dash="5 4", casing=2.0))
    out.append(H.path_line("M 210 193 L 430 117 L 628 79.4", GREEN, 2.6, casing=2.2))
    out.append(H.line_cased(20, 301.3, 260, 394.5, GREY, 1.8, dash="5 4", casing=2.0))
    out.append(H.path_line("M 260 394.5 C 270 396.1 295 401.4 320 404 C 345 406.6 395 409 410 410", GREY, 1.8, dash="5 4", casing=2.0, glow=False))
    out.append(H.path_line("M 20 258.6 L 191 391.4 C 196 393.6 209.2 401.9 221 405 C 232.8 408.1 255.2 409.2 262 410", GREEN, 2.6, casing=2.2))
    out.append(H.line_cased(191, 391.4, 215, 410, "#7B8799", 1.2, dash="3 3", casing=1.8))
    return "".join(out)


def shadows():
    out = []
    for (tx, ty, ang, fl) in UPPER:
        height = GYA - ty
        if height < 70:
            out.append(H.drop_shadow(tx + 6 + height * 0.25, GYA + 1.6, 62, 2.4, 0.4 if height < 6 else 0.26))
    out.append(H.drop_shadow(262 + 6, GYB + 1.6, 62, 2.4, 0.4))
    return "".join(out)


def foreground():
    f = [H.foreground("a1a", A, GYA, seed=11, lights=(14, 330), scrub=10, scale=1.2),
         H.foreground("a1b", B, GYB, seed=17, lights=(190, 630), scrub=10, scale=1.2)]
    return f


def dimension():
    return (H.line_cased(262, 422, 352, 422, GREEN, 2.0, casing=2.4) + H.line_cased(262, 416, 262, 428, GREEN, 2.0, casing=2.4) + H.line_cased(352, 416, 352, 428, GREEN, 2.0, casing=2.4))


def callouts():
    c = S.callout
    return "".join([c(1, 52, 140, 52, 170), c(2, 180, 126, 204, 168), c(3, 330, 66, 332, 128), c(4, 460, 173, 433, 176), c(5, 560, 40, 560, 72), c(6, 560, 176, 560, 135),
                    c(7, 70, 250, 70, 276), c(8, 200, 372, 214, 404), c(9, 262, 340, 262, 386), c(10, 374, 422), c(11, 410, 360, 404, 407)])


def layers():
    out = [H.page("a1page", 640, 440), H.defs()]
    out += world_a() + world_b()
    out.append(paths())
    out.append(shadows())
    planes = []
    for (tx, ty, ang, fl) in UPPER + LOWER:
        o = H.plane_mid(tx, ty, ang, W)
        planes.append(o)
        out.append(o)
        if fl:
            out.append(H.flap_mark(o, fl, length=0.085, width=1.8))
    out += foreground()
    out.append(dimension())
    out.append(H.speed_card("a1c1", 217, 27.5, "VX 62"))
    out.append(H.leader(270, 52.5, 318, 142))
    out.append(H.speed_card("a1c2", 443, 19, "VY 75", 0))
    out.append(H.speed_card("a1c3", 117, 231, "60", 30, mono=False))
    out.append(callouts())
    return H.flatten(out)


def plate():
    return {
        "id": "fig-26-06-short-field",
        "replaces": "fig-26-06-short-field.svg",
        "book_file": "plate-26-06-short-field.jpg",
        "caption": "Figure 26-6. Short-field takeoff over an obstacle, and short-field approach and landing",
        "desc": "Figure 26-6. Short-field takeoff over an obstacle, and short-field approach and landing",
        "legend": [
            "Line up at the very start of the runway, flaps as the AFM gives (drawn partly extended); full power.",
            "As `VX` approaches, rotate to the `VX` attitude.",
            "Climb at `VX` 62 kt, eyes outside.",
            "The obstacle; the example takeoff table measures to 15 m (Chapter 11).",
            "Once clear, `VY` 75 kt, then flaps up in stages.",
            "`VY` from lift-off gains more height per minute but less per metre: here it would not clear the obstacle.",
            "Final at 60 kt, flaps 30°, on a steady path over the obstacle.",
            "The aiming point, just beyond the threshold.",
            "Touchdown at minimum speed, nose high, power off, with little float.",
            "Firm braking once the nosewheel is down, control wheel held back.",
            "A normal 65 kt approach over the same obstacle lands much further along.",
        ],
        "canvas": [640, 440],
        "background": "pale",
        "reskin": {"svg": "fig-26-06-short-field.svg", "blank": True, "layers": layers()},
    }
