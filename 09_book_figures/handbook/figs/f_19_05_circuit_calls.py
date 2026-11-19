"""Figure 19-5. The calls of a training circuit, from the apron and back. Drawn again on an aerial view of the country (figs/terrain.py, plain with scrub; the pieces
are in figs/mapkit.py); the layout of the old flat figure is kept exactly (the apron, the two taxiways, runway 09/27, the holding point, the left-hand circuit for runway 27, the wind,
the taxi back, and the strip of calls and frequencies below), and its eight callouts keep their colours: blue for calls to Ground, green for calls to Tower, grey for the wind.

The aerodrome as it looks from above: a concrete apron with parked aeroplanes, taxiways with their yellow centre lines and the holding-point bars, an asphalt runway with its
threshold bars, numbers and dashed centre line; the circuit a dark ribbon with heads; the model on downwind and on final; the strip below as two coloured bands with the numbered
calls on them."""
from figs import h_a4 as A
from figs import h_b2 as G
from figs import mapkit as K
from figs import scene as S
from figs import terrain

terrain.ensure("terrain-19-05", size=(2560, 1480), seed=195, kind="plain", features=("scrub",), veil=0.3, soft=2.6)

n = S.n
W, HT = 640, 410
BLUE, GREEN, GREY = "#1D4ED8", "#047857", "#6B7280"
CIRCUIT = "M236,122 L150,122 Q120,122 120,152 L120,300 Q120,330 150,330 L550,330 Q580,330 580,300 L580,152 Q580,122 550,122 L436,122"


def aerodrome():
    out = ['<defs>' + S.gradient("c195a", [(0, "#DAD6CC"), (1, "#C4BFB3")]) + S.gradient("c195r", [(0, "#4B5563"), (1, "#374151")]) + '</defs>']
    # the apron and the two taxiways, with their shadows
    out.append('<rect x="282" y="21" width="290" height="34" rx="4" fill="#2C2216" opacity="0.25"/>'
               '<rect x="280" y="18" width="290" height="34" rx="4" fill="url(#c195a)" stroke="#A8A294" stroke-width="1"/>')
    for x in (293.0, 405.0):
        out.append(f'<rect x="{n(x)}" y="52" width="14" height="59" fill="url(#c195r)"/>'
                   f'<line x1="{n(x + 7)}" y1="52" x2="{n(x + 7)}" y2="111" stroke="#FACC15" stroke-width="1.4"/>')
    out.append('<rect x="403" y="86" width="18" height="2" fill="#FACC15"/><rect x="403" y="90" width="18" height="2" fill="#FACC15"/>'
               '<rect x="403" y="94" width="18" height="1.2" fill="#FACC15" opacity="0.8"/>')
    # the runway: asphalt, threshold bars, numbers, centre line
    out.append('<rect x="238" y="113.5" width="200" height="22" fill="#2C2216" opacity="0.25"/>'
               '<rect x="236" y="111" width="200" height="22" fill="url(#c195r)" stroke="#E5E7EB" stroke-width="0.6"/>')
    for i in range(4):
        out.append(f'<rect x="239" y="{n(113.5 + i * 4.6)}" width="7" height="2.6" fill="#FFFFFF"/><rect x="426" y="{n(113.5 + i * 4.6)}" width="7" height="2.6" fill="#FFFFFF"/>')
    for x in range(266, 404, 18):
        out.append(f'<line x1="{x}" y1="122" x2="{x + 9}" y2="122" stroke="#FFFFFF" stroke-width="1.6"/>')
    out.append(G.glyph_text("27", 418, 122, 8.5, "#FFFFFF", rotate=-90) + G.glyph_text("09", 254, 122, 8.5, "#FFFFFF", rotate=90))
    return "".join(out)


def parked():
    return [A.plane(x, 35, 24, 180) for x in (330.0, 358.0, 452.0, 480.0, 548.0)]


def circuit():
    out = [f'<path d="{CIRCUIT}" fill="none" stroke="#FFFFFF" stroke-width="6" stroke-opacity="0.85"/>',
           f'<path d="{CIRCUIT}" fill="none" stroke="#1E293B" stroke-width="2.8"/>',
           '<line x1="432" y1="122" x2="236" y2="122" stroke="#FFFFFF" stroke-width="5" stroke-opacity="0.6"/>'
           '<line x1="432" y1="122" x2="236" y2="122" stroke="#1E293B" stroke-width="2.4" stroke-dasharray="6 4"/>']
    for pts in ("190,122 202,115.4 202,128.6", "120,225 113.4,213 126.6,213", "350,330 338,336.6 338,323.4", "580,225 586.6,237 573.4,237",
                "500,122 512,115.4 512,128.6", "340,122 352,115.4 352,128.6"):
        out.append(f'<polygon points="{pts}" fill="#1E293B" stroke="#FFFFFF" stroke-width="1.2"/>')
    # off the runway and back to the apron: dashed blue
    out.append('<line x1="300" y1="116" x2="300" y2="73.2" stroke="#FFFFFF" stroke-width="4.5" stroke-opacity="0.8"/>'
               f'<line x1="300" y1="116" x2="300" y2="73.2" stroke="{BLUE}" stroke-width="2.2" stroke-dasharray="4 3"/>'
               f'<polygon points="300,66 304.9,75 295.1,75" fill="{BLUE}" stroke="#FFFFFF" stroke-width="1"/>')
    # the wind, from the west
    out.append(A.ribbon("w195", [(230, 230), (300, 230)], width=6.0, colours=("#566377", "#A8B3C4"), head=2.2, casing=1.8))
    return "".join(out)


def disc(k, x, y, col, r=12.0, size=13.0):
    return (f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(r + 1.6)}" fill="#FFFFFF"/><circle cx="{n(x)}" cy="{n(y)}" r="{n(r)}" fill="{col}"/>'
            f'<text x="{n(x)}" y="{n(y + size * 0.36)}" font-family="sans-serif" font-size="{n(size)}" font-weight="bold" fill="#ffffff" text-anchor="middle">{k}</text>')


def strip():
    out = ['<rect x="34" y="376" width="596" height="24" rx="8" fill="#F1F5F9" stroke="#CBD5E1" stroke-width="1"/>',
           f'<rect x="40" y="383" width="90" height="10" rx="5" fill="{BLUE}"/><rect x="130" y="383" width="390" height="10" fill="{GREEN}"/>'
           f'<rect x="520" y="383" width="90" height="10" rx="5" fill="{BLUE}"/>',
           '<rect x="128" y="383" width="4" height="10" fill="#FFFFFF"/><rect x="518" y="383" width="4" height="10" fill="#FFFFFF"/>']
    for k, x, col in ((1, 85, BLUE), (2, 195, GREEN), (3, 260, GREEN), (4, 325, GREEN), (5, 390, GREEN), (6, 455, GREEN), (7, 565, BLUE)):
        out.append(disc(k, x, 388, col, r=9, size=11))
    out.append('<polygon points="626,388 614,394.6 614,381.4" fill="#1F2937"/>')
    return "".join(out)


def layers():
    out = [f'<rect x="0" y="0" width="{W}" height="{HT}" fill="#ffffff"/>', {"name": "terrain-19-05", "at": [320, 189], "width": 640}, aerodrome()]
    out += parked()
    out.append(circuit())
    out.append(A.plane(270, 330, 40, 90))
    out.append(A.plane(530, 122, 40, 270))
    out.append(K.north(40, 20, 50))
    out.append(K.frame(W, HT, (8.0, 8.0, 632.0, 368.0)))
    out.append(disc(1, 520, 35, BLUE) + disc(2, 440, 90, GREEN) + disc(3, 424, 150, GREEN) + disc(4, 230, 354, GREEN) + disc(5, 604, 225, GREEN)
               + disc(6, 560, 98, GREEN) + disc(7, 280, 90, BLUE) + disc(8, 214, 230, GREY, r=11))
    out.append(strip())
    return out


def plate():
    return {
        "id": "fig-19-05-circuit-calls",
        "replaces": "fig-19-05-circuit-calls.svg",
        "book_file": "plate-19-05-circuit-calls.jpg",
        "caption": "Figure 19-5. The calls of a training circuit, from the apron and back",
        "desc": "Figure 19-5. The calls of a training circuit, from the apron and back",
        "legend": [
            "Apron: start-up and taxi, to Ground.",
            "Holding point: ready for departure, to Tower.",
            "Runway: line-up and take-off clearances, read back.",
            "Early on downwind: the downwind report.",
            "Base: a report if the tower asks for one.",
            "Final: the final report; the landing or touch-and-go clearance, read back.",
            "Off the runway: taxi instructions, to Ground.",
            "The wind, from the west, so runway 27 is in use.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"svg": "fig-19-05-circuit-calls.svg", "blank": True, "layers": layers()},
    }
