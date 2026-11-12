"""Figure 22-8. Landing and taking off behind a heavy aeroplane. Two scenes in cards: a runway of the Peninsula seen almost edge-on, pale hills, cumulus; the heavy aeroplane, which the
model does not have, drawn as a vector aeroplane (white, a fin in colour) on the runway after landing and climbing out; its path as a line, its wake as a band of air below and behind
the path with a few swirls; the model seen from the right on the paths of the old figure (green on the right path, red in the wake), the touchdown and rotation points as posts across
the runway; the nine numbered callouts of the old figure kept (figs/h_a1.py and figs/scene.py make the pieces)."""
from figs import h_a1 as H
from figs import scene as S
from figs.kit import side_plane

A = (8, 6, 624, 196)
B = (8, 210, 624, 192)
GYA, GYB = 176.0, 382.0
GREEN, RED, INK = "#047857", "#B91C1C", "#1F2937"
SILHOUETTE = (-24.8, 17.9, -9.4, 5.3)         # the extent of the old flat aeroplane in its own units; it stood on its wheels at y = 5.3

WAKE_A = ("18,30 44,42 70,54 96,66 122,78 148,90 174,102 200,114 226,126 252,138 278,150 304,162 330,174 330,174 330,174 330,174 304,165.5 278,157 252,148.5 226,140 200,131.5 "
          "174,123 148,114.5 122,106 96,97.5 70,89 44,80.5 18,72")
WAKE_B = ("330,380 356,369.1 382,358.2 408,347.3 434,336.4 460,325.5 486,314.6 512,303.7 538,292.8 564,281.9 590,271 616,260.1 640,250 640,284 616,294.1 590,305 564,315.9 538,326.8 "
          "512,337.7 486,348.6 460,359.5 434,370.4 408,380 382,380 356,380 330,380")


def wake(uid, points, flip=False):
    """A band of disturbed air: a pale blue veil, deeper along the path that makes it, with a few swirls inside (clipped to the band)."""
    pl = [tuple(float(v) for v in p.split(",")) for p in points.split()]
    out = [f'<defs>{S.gradient(uid, [(0, "#7FA6E6", 0.62), (1, "#BCD4F6", 0.18)])}<clipPath id="{uid}c"><polygon points="{S.pts(pl)}"/></clipPath></defs>',
           f'<polygon points="{S.pts(pl)}" fill="url(#{uid})"/>']
    xs = [p[0] for p in pl]
    sw = []
    x = min(xs) + 30
    while x < max(xs) - 14:
        # y on the band's centre line at x: halfway between the two edges
        ups = [p for p in pl if abs(p[0] - x) < 14]
        if ups:
            ymid = sum(p[1] for p in ups) / len(ups)
            sw.append(f'<path d="M {S.n(x - 9)},{S.n(ymid + 1)} q 6,-9 13,-2 q 5,7 -3,10 q -8,2 -9,-5" fill="none" stroke="#FFFFFF" stroke-width="1.1" stroke-opacity="0.55" stroke-linecap="round"/>')
        x += 40
    out.append(f'<g clip-path="url(#{uid}c)">{"".join(sw)}</g>')
    out.append(f'<polygon points="{S.pts(pl)}" fill="none" stroke="#FFFFFF" stroke-width="0.9" stroke-opacity="0.6"/>')
    return "".join(out)


def post(x, y0, y1, colour):
    return H.line_cased(x, y0, x, y1, colour, 2.4, casing=2.2)


def world_a():
    return H.profile("a1a", A, GYA, seed=81, sun=(80, 60), runway_args={"x0": 170, "x1": 632, "threshold": True, "half": 4.2, "dash_from": 196},
                     clouds=[H.cloud("cloud-cumulus-a", 540, 46, 84), H.cloud("cloud-cumulus-b", 604, 108, 50, 0.85)],
                     palms=[(40, GYA - 6, 0.5), (58, GYA - 4, 0.42)], acacias=[(130, GYA - 5, 0.5)])


def world_b():
    return H.profile("a1b", B, GYB, seed=83, sun=(80, 60), runway_args={"x0": 8, "x1": 632, "threshold": True, "half": 4.2, "dash_from": 30},
                     clouds=[H.cloud("cloud-cumulus-a", 214, 246, 80), H.cloud("cloud-cumulus-b", 110, 236, 44, 0.85)],
                     palms=[(600, GYB - 6, 0.5)])


def layers():
    out = [H.page("a1page", 640, 410), H.defs()]
    out += world_a() + world_b()
    # the wakes, then the paths and the posts
    out.append(wake("a1wa", WAKE_A))
    out.append(wake("a1wb", WAKE_B))
    out.append(H.line_cased(18, 30, 330, 174, INK, 2.0, casing=2.2))
    out.append(H.line_cased(18, 10, 420, 174, GREEN, 2.4, casing=2.2))
    out.append(H.line_cased(18, 66, 262, 174, RED, 2.2, dash="7 5", casing=2.2))
    out.append(post(330, 164, 186, INK) + post(420, 164, 186, GREEN))
    out.append(H.line_cased(110, 380, 330, 380, "#DDE3EC", 2.0, dash="5 4", casing=0.0, opacity=0.95))
    out.append(H.line_cased(330, 380, 640, 250, INK, 2.0, casing=2.2))
    out.append(H.line_cased(238, 380, 520, 228, GREEN, 2.4, casing=2.2))
    out.append(H.arrow_head(520, 228, -28.3, 10, GREEN))
    out.append(H.line_cased(18, 262, 170, 380, GREEN, 2.2, dash="7 5", casing=2.2))
    out.append(post(330, 370, 392, INK) + post(238, 370, 392, GREEN) + post(170, 370, 392, GREEN))
    # the heavy aeroplane, landed (its gear on the runway) and climbing out
    out.append(H.drop_shadow(560, GYA + 2, 140, 3.4, 0.4))
    out.append(H.airliner("a1h1", 556, GYA - 14.5, 140, 0, True))
    out.append(H.airliner("a1h2", 548, 281, 140, -22.8, False))
    # the model: green on the right path, red in the wake, green on its takeoff
    out.append(side_plane(150, 61.9, 22.2, 0.85, SILHOUETTE, grow=1.5, look={**H.LOOK, "tint": "#0E9F6E", "tint_strength": 0.55}))
    out.append(side_plane(150, 122.4, 23.9, 0.85, SILHOUETTE, grow=1.5, look={**H.LOOK, "tint": "#D33A32", "tint_strength": 0.6}))
    out.append(side_plane(430, 274.5, -28.3, 0.85, SILHOUETTE, grow=1.5, look={**H.LOOK, "tint": "#0E9F6E", "tint_strength": 0.55}))
    out.append(H.foreground("a1a", A, GYA, seed=81, lights=(170, 632), scrub=9, scale=1.1))
    out.append(H.foreground("a1b", B, GYB, seed=83, lights=(8, 632), scrub=9, scale=1.1))
    c = S.callout
    out.append("".join([c(1, 214, 40, 186, 107.5), c(2, 330, 150, 330, 162), c(3, 100, 140, 118, 98.2), c(4, 448, 132, 420, 163), c(5, 222, 164, 236, 159),
                         c(6, 366, 364, 334, 374), c(7, 586, 370, 540, 316), c(8, 372, 238, 422, 272), c(9, 62, 330, 84, 316)]))
    return H.flatten(out)


def plate():
    return {
        "id": "fig-22-08-behind-heavy",
        "replaces": "fig-22-08-behind-heavy.svg",
        "book_file": "plate-22-08-behind-heavy.jpg",
        "caption": "Figure 22-8. Landing and taking off behind a heavy aeroplane",
        "desc": "Figure 22-8. Landing and taking off behind a heavy aeroplane",
        "legend": [
            "The heavy aeroplane's approach path.",
            "Its touchdown point: the wake ends there.",
            "The wake, below and behind its path.",
            "Your approach: at or above its path, touching down beyond its touchdown point.",
            "Below its path and landing short: into the wake.",
            "A departing heavy aeroplane's rotation point: the wake begins there.",
            "The wake below its climb path.",
            "Your takeoff: rotate before its rotation point and climb above its path until you can turn clear.",
            "Landing behind a departing heavy aeroplane: touch down before its rotation point.",
        ],
        "canvas": [640, 410],
        "background": "pale",
        "reskin": {"svg": "fig-22-08-behind-heavy.svg", "blank": True, "layers": layers()},
    }
