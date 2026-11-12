"""Figure 26-7. Soft-field takeoff and soft-field landing. Two scenes in cards: a strip of grass and loose sand in the desert seen almost edge-on (two faint wheel tracks, tufts), pale hills
on the horizon, the ground effect zone as a veil of air with a dashed top, the model seen from the right at the places of the old figure, the paths as lines with a casing, the speed
boxes as small cards; the ten numbered callouts of the old figure kept (figs/h_a1.py and figs/scene.py make the pieces)."""
from figs import h_a1 as H
from figs import scene as S

A = (8, 6, 624, 213)
B = (8, 226, 624, 208)
GYA, GYB = 193.0, 410.0
BLUE = "#1D4ED8"
W = 84.0

UPPER = [(56, 193, 0, 10), (175, 193, -11, 10), (300, 186, -11, 10), (430, 177, -3, 0), (585, 103, -10, 0)]
LOWER = [(90, 296, 2, 30), (330, 401, -7, 30), (470, 410, -11, 30), (590, 410, 0, 30)]

PATH_UP = ("M 24 193 C 28.3 193 24.8 193 50 193 C 75.2 193 141.7 193 175 193 C 208.3 193 229.2 194.2 250 193 C 270.8 191.8 280 188.5 300 186 C 320 183.5 348.3 179.5 370 178 "
           "C 391.7 176.5 407.5 178.5 430 177 C 452.5 175.5 479.2 181.3 505 169 C 530.8 156.7 564.5 120 585 103 C 605.5 86 620.8 73 628 67")
PATH_DOWN = ("M 20 262 C 31.7 267.7 60 281.3 90 296 C 120 310.7 170 334.7 200 350 C 230 365.3 248.3 379.5 270 388 C 291.7 396.5 305 397.7 330 401 C 355 404.3 396.7 406.5 420 408 "
             "C 443.3 409.5 461.7 409.7 470 410")


def world_a():
    objects = H.grass_strip("a1sa", 8, 632, GYA, 4.6, seed=3) + H.air_block("a1za", 290, 143, 632, GYA + 4.6, colour="#B9D5F5", opacity=0.62)
    return H.profile("a1a", A, GYA, seed=23, sun=(80, 70), clouds=[H.cloud("cloud-cumulus-b", 96, 40, 78), H.cloud("cloud-cumulus-a", 268, 40, 78), H.cloud("cloud-cumulus-b", 560, 24, 48, 0.85)],
                     palms=[(30, GYA - 6, 0.5), (246, GYA - 5, 0.45)], acacias=[(122, GYA - 5, 0.5), (260, GYA - 5, 0.4)], objects=objects)


def world_b():
    objects = H.grass_strip("a1sb", 8, 632, GYB, 4.6, seed=7)
    return H.profile("a1b", B, GYB, seed=29, sun=(80, 70), clouds=[H.cloud("cloud-cumulus-a", 300, 270, 88), H.cloud("cloud-cumulus-b", 520, 258, 70)],
                     palms=[(214, GYB - 6, 0.5), (232, GYB - 4, 0.4)], acacias=[(52, GYB - 5, 0.5)], objects=objects)


def paths():
    return (H.path_line(PATH_UP, BLUE, 1.9, dash="6 5", casing=1.9) + H.path_line(PATH_DOWN, BLUE, 2.4, casing=2.2))


def shadows():
    out = []
    for (tx, ty, ang, fl) in UPPER:
        height = GYA - ty
        if height < 40:
            out.append(H.drop_shadow(tx + 6 + max(0, height) * 0.25, GYA + 1.6, 62, 2.4, 0.4 if height < 6 else 0.28))
    for (tx, ty, ang, fl) in LOWER:
        height = GYB - ty
        if height < 40:
            out.append(H.drop_shadow(tx + 6 + max(0, height) * 0.25, GYB + 1.6, 62, 2.4, 0.4 if height < 6 else 0.28))
    return "".join(out)


def callouts():
    c = S.callout
    return "".join([c(1, 56, 130, 56, 168), c(2, 175, 118, 177, 168), c(3, 300, 108, 304, 160), c(4, 430, 104, 430, 153), c(5, 612, 169, 612, 148), c(6, 612, 52, 593, 82),
                    c(7, 90, 250, 90, 274), c(8, 330, 330, 332, 378), c(9, 470, 330, 470, 385), c(10, 530, 346, 570, 392)])


def layers():
    out = [H.page("a1page", 640, 440), H.defs()]
    out += world_a() + world_b()
    out.append(paths())
    out.append(shadows())
    for (tx, ty, ang, fl) in UPPER + LOWER:
        o = H.plane_mid(tx, ty, ang, W)
        out.append(o)
        if fl:
            out.append(H.flap_mark(o, fl, length=0.085, width=1.8))
    out.append(H.foreground("a1a", A, GYA, seed=23, scrub=10, scale=1.2))
    out.append(H.foreground("a1b", B, GYB, seed=29, scrub=10, scale=1.2))
    out.append(S.ribbon("a1ar1", [(80, 165), (92, 165), (104, 165)], 5.5, "#1F2937", "#667489", opacity=0.95, head=2.2))
    out.append(S.ribbon("a1ar2", [(560, 374), (572, 374), (584, 374)], 5.5, "#1F2937", "#667489", opacity=0.95, head=2.2))
    out.append(H.speed_card("a1c1", 437, 33.5, "VX 62"))
    out.append(H.leader(503, 58.5, 566, 89))
    out.append(H.speed_card("a1c2", 137, 231, "60", 30, mono=False))
    out.append(callouts())
    return H.flatten(out)


def plate():
    return {
        "id": "fig-26-07-soft-field",
        "replaces": "fig-26-07-soft-field.svg",
        "book_file": "plate-26-07-soft-field.jpg",
        "caption": "Figure 26-7. Soft-field takeoff and soft-field landing",
        "desc": "Figure 26-7. Soft-field takeoff and soft-field landing",
        "legend": [
            "Rolling onto the runway without stopping, control wheel fully back, flaps as the AFM recommends.",
            "Full power; once the nosewheel lifts, a nose-high attitude held.",
            "Lift-off at a low speed.",
            "Nose lowered at once: level just above the surface, accelerating.",
            "The ground effect zone, within about one wingspan of the surface.",
            "Climb only at `VX` 62 kt with an obstacle, or at `VY` 75 kt.",
            "Final at 60 kt, flaps 30°.",
            "Flare with some power on.",
            "Touchdown at the lowest possible speed, nose high, nosewheel held off.",
            "Nosewheel lowered gently, no brakes, power to keep moving.",
        ],
        "canvas": [640, 440],
        "background": "pale",
        "reskin": {"svg": "fig-26-07-soft-field.svg", "blank": True, "layers": layers()},
    }
