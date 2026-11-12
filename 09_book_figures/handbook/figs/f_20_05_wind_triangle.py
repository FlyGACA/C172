"""Figure 20-5. The wind triangle for leg 1, drawn to scale. Drawn again on a pale chart ground with a printed grid (a line every 5 kt through the point O, a stronger one every 20), the
range rings printed in dashes, the three vectors as ribbons with their arrowheads counted as before (the wind three, the heading and airspeed one, the track and groundspeed two),
the TAS arc and the angles as glowing arcs, the aeroplane of the model on the heading vector, and the scale as a steel ruler. The geometry, numbers and callouts of the old figure are
kept (figs/h_a4.py has the parts)."""
from figs import h_a4 as H
from figs import scene as S

O, W, TIP = (548.0, 292.0), (576.7, 370.9), (224.7, 105.3)


def chart():
    out = [H.paper("w5", 640, 410, origin=(O[0], O[1]))]
    for r in (84, 168, 252, 336):
        out.append(f'<circle cx="{O[0]}" cy="{O[1]}" r="{r}" fill="none" stroke="#7F93AE" stroke-opacity="0.55" stroke-width="1" stroke-dasharray="2 5"/>')
    # the triangle, lightly tinted
    out.append(f'<defs>{S.gradient("w5t", [(0, "#CFE2FB", 0.92), (1, "#9FC3F2", 0.5)], 548, 292, 224.7, 105.3, "userSpaceOnUse")}</defs><polygon points="{S.pts([O, W, TIP])}" fill="url(#w5t)"/>')
    return "".join(out)


def lines():
    out = []
    # the course line through O (300° true), dashed grey; the direction the wind comes from (340°), dotted amber; true north at O and at W
    out.append(H.halo_line(584.4, 313.0, 126.1, 48.4, "#6B7A92", 1.7, "6 4", 3.4, 0.8))
    out.append(H.halo_line(548.0, 292.0, 507.0, 179.2, "#B45309", 1.5, "3 3", 3.2, 0.8))
    for (x, y0, y1, top) in ((548.0, 292.0, 150.0, 140.0), (576.7, 370.9, 318.0, 306.0)):
        out.append(H.halo_line(x, y0, x, y1, "#27364F", 1.6, "4 3", 3.4, 0.85))
        out.append(f'<polygon points="{x},{top} {x + 6.2},{top + 12.4} {x - 6.2},{top + 12.4}" fill="#27364F" stroke="#FFFFFF" stroke-width="1.4" stroke-linejoin="round"/>')
    # the TAS arc about W, and the heading line carried on past the tip
    arc = "M194.9,150.2 A441.0,441.0 0 0,1 259.7,64.4"
    out.append(f'<defs><filter id="w5g" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="2.4"/></filter></defs>'
               f'<path d="{arc}" fill="none" stroke="#3B82F6" stroke-width="5" opacity="0.65" filter="url(#w5g)"/>'
               f'<path d="{arc}" fill="none" stroke="#FFFFFF" stroke-width="4.6" stroke-opacity="0.8" stroke-dasharray="5 3"/><path d="{arc}" fill="none" stroke="#1F5FE0" stroke-width="2" stroke-dasharray="5 3"/>')
    out.append(H.halo_line(224.7, 105.3, 128.9, 33.1, "#1F5FE0", 1.5, "4 3", 3.4, 0.85))
    return "".join(out)


def vectors():
    wind = H.vector("w5w", O, W, 5.0, H.AMBER, heads=3, head_len=13, head_w=12, gap=9.5, glow="#FFB020")
    heading = H.vector("w5h", W, TIP, 5.0, ("#1F5FE0", "#6FA3F5"), heads=1, head_len=18, head_w=17, glow="#5B96FF")
    track = H.vector("w5k", O, (225.1, 105.7), 5.0, ("#0F172A", "#475569"), heads=2, head_len=13, head_w=10.5, gap=12, glow="#334155")
    return wind, heading, track


def angles():
    out = []
    a7, a40 = "M138.1,55.3 A100.0,100.0 0 0,1 144.9,45.1", "M499.5,264.0 A56.0,56.0 0 0,1 528.8,239.4"
    for d, c, g in ((a7, "#DC2626", "#FF5B4D"), (a40, "#C2610E", "#FFB020")):
        out.append(f'<path d="{d}" fill="none" stroke="{g}" stroke-width="7" opacity="0.7" filter="url(#w5g)"/><path d="{d}" fill="none" stroke="#FFFFFF" stroke-width="6.4" stroke-opacity="0.9" stroke-linecap="round"/>'
                   f'<path d="{d}" fill="none" stroke="{c}" stroke-width="3.2" stroke-linecap="round"/>')
    out.append(H.text(130.0, 37.3, "7°", 15, "#B91C1C", "bold", "middle", halo="#FFFFFF"))
    out.append(H.text(497.7, 240.8, "40°", 13, "#B45309", "bold", "middle", halo="#FFFFFF"))
    return "".join(out)


def labels():
    return "".join([H.text(404.3, 277.4, "105", 16, "#1D4ED8", "bold", "middle", halo="#FFFFFF"), H.text(374.2, 175.3, "89", 16, "#0F172A", "bold", "middle", halo="#FFFFFF"),
                    H.text(596.0, 331.0, "20", 15, "#B45309", "bold", "middle", halo="#FFFFFF")])


def plate():
    wind, heading, track = vectors()
    dots = (f'<defs><radialGradient id="w5d" cx="0.35" cy="0.3" r="0.8"><stop offset="0" stop-color="#6B7C99"/><stop offset="1" stop-color="#0F172A"/></radialGradient></defs>'
            f'<circle cx="{O[0]}" cy="{O[1]}" r="5.4" fill="url(#w5d)" stroke="#FFFFFF" stroke-width="1.6"/><circle cx="{W[0]}" cy="{W[1]}" r="3.4" fill="#B45309" stroke="#FFFFFF" stroke-width="1.2"/>')
    layers = [
        chart(), lines(),
        wind, heading, track,
        H.plane(471.1, 291.2, 52, 307),
        angles(), labels(), dots,
        H.ruler("w5r", 26, 348, 282, 34, 40.0, 4.2, (0, 20, 40, 60), (0, 20, 40, 60), 5),
    ]
    c = S.callout
    layers.append("".join([
        c(1, 582, 146, 549, 166), c(2, 588, 304, 553, 293), c(3, 610.7, 348.9, 579.7, 357.0), c(4, 277.2, 45.7, 250.2, 73.7), c(5, 300.3, 225, 328.3, 183.6),
        c(6, 327.5, 108, 306.5, 152.5), c(7, 103.9, 26.3, 137.9, 49.3), c(8, 561.7, 206.6, 522.7, 239.6), c(9, 330, 366, 304, 366),
    ]))
    return {
        "id": "fig-20-05-wind-triangle",
        "replaces": "fig-20-05-wind-triangle.svg",
        "book_file": "plate-20-05-wind-triangle.jpg",
        "caption": "Figure 20-5. The wind triangle for leg 1, drawn to scale",
        "desc": "Figure 20-5. The wind triangle for leg 1, drawn to scale",
        "legend": [
            "True north.",
            "Point O and the course line, 300° true.",
            "Wind vector: from 340° at 20 kt, drawn downwind (three arrowheads).",
            "Arc of radius 105, the TAS.",
            "Heading and TAS: 307°, 105 kt (one arrowhead).",
            "Track and groundspeed: 300°, 89 kt (two arrowheads).",
            "Wind correction angle, 7° right, equal to the drift.",
            "Wind angle, 40° right of the course.",
            "Scale in knots.",
        ],
        "canvas": [640, 410],
        "background": "pale",
        "reskin": {"svg": "fig-20-05-wind-triangle.svg", "blank": True, "layers": layers},
    }
