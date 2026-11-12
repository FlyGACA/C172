"""Figure 20-7. The 1-in-60 rule and two ways back to the planned track. Drawn again on a pale chart ground with a printed grid: the planned track a dark ribbon from the town (a gold
hexagon) to WADI (a dark triangle), the track flown a red ribbon to the fix and its dashed continuation, the closing-angle track a green ribbon with its arrowhead, the double-track-error
tracks an orange dashed ribbon that rejoins the planned track and goes on; the four angles (6°, 10°, 12°, 4°) as glowing arcs, the 2 NM offset dotted, and the 20 and 30 NM distances on
a steel ruler laid along the top. Distances across the track are drawn three times larger, as before. The geometry, numbers and callouts of the old figure are kept (figs/h_a4.py has the parts)."""
from figs import h_a4 as H
from figs import scene as S

TOWN, WADI, FIX = (30.0, 112.0), (610.0, 112.0), (260.7, 184.8)


def arcs():
    out = ['<defs><filter id="o7g" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="2.4"/></filter></defs>']
    spec = [("M122.0,112.0 A92,92 0 0,1 117.7,139.7", "#C4282B", "#FF5B4D"), ("M319.9,203.4 A62,62 0 0,0 321.4,172.1", "#0B8A66", "#35E6A0"),
            ("M359.9,216.0 A104,104 0 0,0 359.9,153.5", "#C2610E", "#FFB020"), ("M490.0,112.0 A120,120 0 0,0 492.5,136.5", "#0B8A66", "#35E6A0")]
    for d, c, g in spec:
        out.append(f'<path d="{d}" fill="none" stroke="{g}" stroke-width="7" opacity="0.7" filter="url(#o7g)"/><path d="{d}" fill="none" stroke="#FFFFFF" stroke-width="5.6" stroke-opacity="0.9" stroke-linecap="round"/>'
                   f'<path d="{d}" fill="none" stroke="{c}" stroke-width="2.8" stroke-linecap="round"/>')
    out.append(H.text(134.0, 134.0, "6°", 15, "#B91C1C", "bold", "start", halo="#FFFFFF"))
    out.append(H.text(482.0, 142.0, "4°", 15, "#0B7A5A", "bold", "end", halo="#FFFFFF"))
    out.append(H.text(330.7, 190.8, "10°", 15, "#0B7A5A", "bold", "start", halo="#FFFFFF"))
    out.append(H.text(370.7, 214.8, "12°", 15, "#B45309", "bold", "start", halo="#FFFFFF"))
    return "".join(out)


def markers():
    out = [f'<defs><linearGradient id="o7h" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#FFF0A6"/><stop offset="1" stop-color="#E2A92B"/></linearGradient>'
           f'<linearGradient id="o7t" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#4A5875"/><stop offset="1" stop-color="#10192B"/></linearGradient>'
           '<filter id="o7s" x="-40%" y="-40%" width="190%" height="200%"><feDropShadow dx="1" dy="2.4" stdDeviation="1.6" flood-color="#10233F" flood-opacity="0.4"/></filter></defs>']
    out.append('<polygon points="21,108 27,103 37,106 39,116 31,121 22,118" fill="url(#o7h)" stroke="#B45309" stroke-width="1.3" stroke-linejoin="round" filter="url(#o7s)"/>'
               '<polygon points="25,108.5 28,106 34,107.4" fill="#FFFFFF" opacity="0.6"/>')
    out.append('<polygon points="610,101 619.4,117.6 600.6,117.6" fill="url(#o7t)" stroke="#FFFFFF" stroke-width="1.2" stroke-linejoin="round" filter="url(#o7s)"/>')
    return "".join(out)


def plate():
    ground = H.paper("o7", 640, 330, origin=(30.0, 112.0), minor=29.0, major=116.0)
    ruler = H.ruler("o7r", 22, 40, 596, 32, 30.0, 11.6, (0, 20, 50), (), 5) + H.text(145.4, 63.5, "20", 15, "#1F2937", "bold", "middle") + H.text(435.4, 63.5, "30", 15, "#1F2937", "bold", "middle")
    planned = H.ribbon("o7p", [TOWN, (602.0, 112.0)], width=3.8, colours=("#111B30", "#2E3C58"), arrow=False, casing=1.4)
    flown = H.ribbon("o7f", [TOWN, FIX], width=4.8, colours=("#B3181C", "#E0524A"), arrow=False, casing=1.6, glow="#FF5B4D")
    cont = H.halo_line(FIX[0], FIX[1], 610.0, 294.9, "#C4282B", 1.5, "6 4", 3.4, 0.8)
    offset = H.halo_line(260.7, 112.0, 260.7, 184.8, "#1F2937", 1.5, "3 3", 3.2, 0.85)
    closing = H.ribbon("o7c", [FIX, (594.0, 115.4)], width=4.6, colours=("#07745A", "#22B684"), head=2.3, casing=1.6, glow="#35E6A0")
    double = H.dashed_arrow([FIX, (491.5, 112.0), (549.5, 112.0)], "#C2610E", 2.8, "9 4", 11.0, casing=1.6)
    rings = ('<defs><radialGradient id="o7q" cx="0.4" cy="0.35" r="0.8"><stop offset="0" stop-color="#FFFFFF"/><stop offset="1" stop-color="#C9D3E2"/></radialGradient></defs>'
             f'<circle cx="{FIX[0]}" cy="{FIX[1]}" r="9" fill="#FF5B4D" opacity="0.45" filter="url(#o7g)"/><circle cx="{FIX[0]}" cy="{FIX[1]}" r="5.5" fill="url(#o7q)" stroke="#16233D" stroke-width="2.2"/>'
             '<circle cx="491.5" cy="112" r="4.5" fill="url(#o7q)" stroke="#C2610E" stroke-width="2"/>')
    layers = [
        ground, ruler,
        planned, offset, cont, flown, double, closing,
        arcs(), H.text(252.7, 154.4, "2", 15, "#1F2937", "bold", "end", halo="#FFFFFF"),
        rings, markers(),
    ]
    c = S.callout
    layers.append("".join([
        c(1, 42, 182, 31, 121), c(2, 168, 90, 160, 112), c(3, 104, 201.5, 126, 142.3), c(4, 238.7, 236.8, 257.7, 189.8), c(5, 491.3, 199.6, 478.3, 142.6),
        c(6, 407.8, 90, 403.8, 139.7), c(7, 588, 90, 607, 105),
    ]))
    return {
        "id": "fig-20-07-one-in-sixty",
        "replaces": "fig-20-07-one-in-sixty.svg",
        "book_file": "plate-20-07-one-in-sixty.jpg",
        "caption": "Figure 20-7. The 1-in-60 rule and two ways back to the planned track",
        "desc": "Figure 20-7. The 1-in-60 rule and two ways back to the planned track",
        "legend": [
            "The town: the last fix, on track.",
            "The planned track to WADI, 300°.",
            "The track flown, 6° right of the planned track.",
            "Fix at the road crossing: 2 NM right of track after 20 NM.",
            "Closing-angle method: turn 10° left and fly straight to WADI, closing at 4°.",
            "Double-track-error method: turn 12° left, rejoin the track after another 20 NM, then turn 6° right.",
            "Point WADI, 30 NM ahead.",
        ],
        "canvas": [640, 330],
        "background": "pale",
        "reskin": {"svg": "fig-20-07-one-in-sixty.svg", "blank": True, "layers": layers},
    }
