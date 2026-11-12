"""Figure 16-7. VFR minimums in Classes C, D and E below 10 000 ft and at a controlled aerodrome. Two scenes in cards: on the left a cumulus of the model of the sky (figs/clouds.py) with
the aeroplane 500 ft below it, 1 000 ft above it and 2 000 ft to the side of it, the 5 km flight visibility as a dashed arrow; on the right a controlled aerodrome of the Peninsula (runway,
control tower, desert hills) under two clouds whose base is the ceiling, 1 000 ft above the ground, with the surface area of the controlled airspace as a pane of air with a dashed edge and
the 5 km ground visibility along the ground. Every distance and its dimension line is kept, with the eight numbered callouts of the old figure (figs/h_a1.py and figs/scene.py make
the pieces)."""
from figs import h_a1 as H
from figs import scene as S

A = (12, 12, 384, 356)
B = (412, 12, 216, 356)
GY = 302.0
INK, GREEN, RED, BLUE = "#1F2937", "#047857", "#B91C1C", "#1D4ED8"


def world_a():
    return H.profile("a1a", A, GY, seed=101, sun=(80, 60), far=24, mid=11, base=13, scrub_count=14, grain=False,
                     clouds=[{"name": "cloud-cumulus-c", "at": [140, 161.6], "width": 140, "haze": {"colour": "#CFE0F3", "amount": 0.06}}],
                     palms=[(34, GY - 5, 0.5)], acacias=[(366, GY - 4, 0.5)])


def world_b():
    objects = H.control_tower(599.5, GY - 1.5, 36)
    return H.profile("a1b", B, GY, seed=103, sun=(60, 60), far=22, mid=10, base=13, scrub_count=8, grain=False, radius=10,
                     runway_args={"x0": 440, "x1": 570, "half": 3.2, "threshold": False, "dash_from": 452},
                     clouds=[{"name": "cloud-cumulus-a", "at": [468, 150 - 20.5], "width": 104, "height": 41}, {"name": "cloud-cumulus-b", "at": [582, 150 - 17.5], "width": 84, "height": 35}],
                     palms=[(428, GY - 5, 0.5)], objects=objects)


def surface_area():
    """The surface area of the controlled airspace: a pane of air with a dashed edge all round."""
    x0, y0, x1, y1 = 424, 40, 616, 300
    return (f'<defs>{S.gradient("a1sar", [(0, "#BFD8F7", 0.26), (1, "#DDEBFB", 0.1)])}</defs><rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="url(#a1sar)"/>'
            f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="none" stroke="#FFFFFF" stroke-width="4.4" stroke-opacity="0.8" stroke-dasharray="8 5"/>'
            f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="none" stroke="{BLUE}" stroke-width="2" stroke-dasharray="8 5"/>')


def layers():
    out = [H.page("a1page", 640, 380), H.defs()]
    out += world_a()
    out += world_b()
    out.append(S.card_front("a1sa", *B, surface_area(), radius=10))
    # left card: the aeroplanes round the cloud, the dimensions
    out.append({"name": "sprite-side", "at": [141, 258.8], "width": 60, **H.LOOK})
    out.append({"name": "sprite-side", "at": [141, 42.6], "width": 60, **H.LOOK})
    out.append({"name": "sprite-side-left", "at": [341, 164.2], "width": 60, **H.LOOK})
    out.append(H.dim_line(110, 199, 110, 252, INK, 2.0, head=7))
    out.append(H.pill(141, 224.5, 50, 20, "500", INK, 13))
    out.append(H.dim_line(110, 56, 110, 118, INK, 2.0, head=7))
    out.append(H.pill(142, 86, 52, 20, "1 000", INK, 13))
    out.append(H.dim_line(214, 150, 312, 150, INK, 2.0, head=7))
    out.append(H.pill(274, 134, 60, 20, "2 000", INK, 13))
    out.append(H.path_line("M 168 262 L 376 262", GREEN, 2.5, dash="7 4", casing=2.4, glow=False) + H.arrow_head(386, 262, 0, 11, GREEN))
    out.append(H.pill(279, 282, 34, 20, "5", GREEN, 13))
    # right card: the ceiling, the visibility along the ground
    out.append(H.dim_line(470, 154, 470, 297, RED, 2.0, head=7))
    out.append(H.pill(502, 224, 52, 20, "1 000", RED, 13))
    out.append(H.dim_line(434, 320, 614, 320, RED, 2.5, head=9))
    out.append(H.pill(524, 320, 34, 20, "5", RED, 13))
    out.append(H.foreground("a1xb", B, GY, seed=103, scrub=5, scale=1.0, lights=(440, 570)))
    c = S.callout
    out.append("".join([c(1, 84, 229, 108, 226), c(2, 84, 87, 108, 86), c(3, 274, 186, 274, 152), c(4, 320, 282, 320, 264), c(5, 44, 172, 74, 170),
                         c(6, 450, 228, 468, 226), c(7, 524, 350, 524, 331), c(8, 604, 40)]))
    return H.flatten(out)


def plate():
    return {
        "id": "fig-16-07-vfr-minimums",
        "replaces": "fig-16-07-vfr-minimums.svg",
        "book_file": "plate-16-07-vfr-minimums.jpg",
        "caption": "Figure 16-7. VFR minimums in Classes C, D and E below 10 000 ft and at a controlled aerodrome",
        "desc": "Figure 16-7. VFR minimums in Classes C, D and E below 10 000 ft and at a controlled aerodrome",
        "legend": [
            "500 ft below cloud.",
            "1 000 ft above cloud.",
            "2 000 ft horizontally from cloud.",
            "Flight visibility 5 km.",
            "The cloud.",
            "Ceiling at least 1 000 ft to fly beneath it within controlled airspace designated to the surface for an aerodrome [[§91.165(d)]].",
            "Ground visibility at least 5 km to take off, land or enter the circuit in the surface area of Class B, C, D or E airspace; flight visibility if none is reported [[§91.165(e)]].",
            "The surface area of controlled airspace.",
        ],
        "canvas": [640, 380],
        "background": "pale",
        "reskin": {"svg": "fig-16-07-vfr-minimums.svg", "blank": True, "layers": layers()},
    }
