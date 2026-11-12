"""Figure 17-6. The air traffic services a VFR flight meets from departure to arrival. Above: the route in profile on a slice of desert ground (a front of sand and rock, the ground seen
from above along its back edge with the two runways, a control tower), the control zone (CTR) and the terminal control area (TMA) as translucent blocks of glass with depth, the route as a
dashed line with a casing and the model on it; below: the services as glass capsules on a pale card (tower, approach control dashed, flight information, TIBA, the alerting service with its
bell), with the dashed guides that tie the five places of the flight to the services and the numbered discs under them. Every place, bar and label of the old figure is kept, with its seven
numbered callouts (figs/h_a1.py and figs/scene.py make the pieces)."""
from figs import h_a1 as H
from figs import scene as S

U = (10, 6, 620, 160)
L = (10, 172, 620, 226)
GREEN, BLUE, AMBER = "#047857", "#1D4ED8", "#B45309"
DX, DY = 12.0, 9.0
CTR = [(20, 96), (130, 96), (130, 150), (20, 150)]
TMA = [(130, 30), (290, 30), (290, 70), (210, 70), (210, 96), (130, 96)]
ROUTE = "M 70 146 L 130 112 L 210 112 L 290 88 L 480 88 L 560 130 L 596 146"


def ground():
    top = [(14, 150), (614, 150), (614 + DX, 150 - DY), (14 + DX, 150 - DY)]
    g = S.gradient
    out = [S.land_layer("a1hl", S.ridge(131, 24, 626, 141, 20, peaks=0.55), 142, ("#8391B3", "#BDC8DD"), rim=True, haze=0.3),
           f'<defs>{g("a1gt", [(0, "#EFE0B8"), (1, "#DCC592")])}{g("a1gf", [(0, "#E3CD9C"), (1, "#A98B5E")])}{g("a1gr", [(0, "#C9B287"), (1, "#8F7752")], 0, 0, 1, 0)}</defs>',
           f'<polygon points="{S.pts(top)}" fill="url(#a1gt)"/>',
           S.scrub(7, 30, 620, 142, 149, 12, scale=0.5),
           f'<polygon points="{S.pts([(614, 150), (614 + DX, 150 - DY), (614 + DX, 160 - DY), (614, 160)])}" fill="url(#a1gr)"/>',
           S.rock("a1gk", S.jag([(14, 150), (614, 150)], 0.5, 4, parts=60), 160, 14, 614, 15, tones=("#EAD8A9", "#B99A68")),
           f'<rect x="14" y="150" width="600" height="1.4" fill="#FFF6DA" opacity="0.8"/>']
    # the two runways on the ground seen from above (along the back edge)
    for x0, x1 in ((50, 92), (568, 612)):
        out.append(f'<polygon points="{S.pts([(x0, 148.2), (x1, 148.2), (x1 + 8, 142), (x0 + 8, 142)])}" fill="#3E4756"/>'
                   f'<line x1="{x0 + 4}" y1="145.1" x2="{x1 + 4}" y2="145.1" stroke="#F4F6FA" stroke-width="0.9" stroke-dasharray="4 3"/>')
    return "".join(out)


def bar(x, y, w, kind):
    fills = {"blue": ("#EEF3FE", "#CAD8F7", BLUE), "green": ("#EAF7F1", "#C7E9DA", GREEN), "amber": ("#FFF4E6", "#FBDDB6", AMBER)}
    a, b, stroke = fills[kind]
    uid = f"a1bar{int(x)}{int(y)}"
    return (f'<defs>{S.gradient(uid, [(0, a), (1, b)])}</defs>'
            f'<rect x="{x}" y="{y}" width="{w}" height="20" rx="10" fill="url(#{uid})" filter="url(#a1ds)"/>'
            f'<rect x="{x + 6}" y="{y + 2.2}" width="{w - 12}" height="5" rx="2.5" fill="#FFFFFF" opacity="0.55"/>')


def bar_edge(x, y, w, colour, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<rect x="{x}" y="{y}" width="{w}" height="20" rx="10" fill="none" stroke="{colour}" stroke-width="2"{d}/>'


def bell(cx, cy):
    return (f'<path d="M {cx - 9},{cy + 8} L {cx - 7.2},{cy + 4.4} L {cx - 7.2},{cy - 1.9} Q {cx - 7.2},{cy - 8.2} {cx},{cy - 8.2} Q {cx + 7.2},{cy - 8.2} {cx + 7.2},{cy - 1.9} L {cx + 7.2},{cy + 4.4} L {cx + 9},{cy + 8} Z" '
            f'fill="{AMBER}" stroke="#FFFFFF" stroke-width="1.2" paint-order="stroke"/><circle cx="{cx}" cy="{cy + 10.6}" r="2.5" fill="{AMBER}" stroke="#FFFFFF" stroke-width="1"/>'
            f'<rect x="{cx - 1}" y="{cy - 11}" width="2" height="3" fill="{AMBER}"/>')


def lower():
    x, y, w, h = L
    out = [S.card("a1lc", x, y, w, h, [(0, "#F7FAFE"), (1, "#E4ECF6")], "", radius=10)]
    for k, xg in enumerate((80, 130, 290, 520, 604)):
        out.append(H.line_cased(xg, 164, xg, 372, "#7B8799", 1.2, dash="3 3", casing=2.0, opacity=0.95))
    out.append(bar(66, 186, 74, "blue") + bar_edge(66, 186, 74, BLUE))
    out.append(bar(120, 222, 180, "blue") + bar_edge(120, 222, 180, BLUE, "6 4"))
    out.append(bar(280, 258, 250, "blue") + bar_edge(280, 258, 250, BLUE))
    out.append(bar(510, 294, 110, "green") + bar_edge(510, 294, 110, GREEN))
    out.append(bar(66, 336, 554, "amber") + bar_edge(66, 336, 554, AMBER))
    for t, yy, col in (("TWR", 201, BLUE), ("APP", 237, BLUE), ("FIS", 273, BLUE), ("TIBA", 309, GREEN)):
        out.append(f'<text x="14" y="{yy}" font-family="monospace" font-size="12" font-weight="bold" fill="{col}" text-anchor="start">{t}</text>')
    out.append(bell(36, 343))
    return out


def layers():
    out = [H.page("a1page", 640, 400), H.defs()]
    out.append(S.card("a1uc", *U, H.horizon_sky((141 - U[1]) / U[3]), S.glow("a1ug", 90, 40, 150, "#FFF1CC", 0.5), radius=10))
    out.append(S.card_front("a1ug2", *U, ground() + H.control_tower(44, 148, 30), radius=10))
    out.append(S.card_front("a1uglass", *U, H.glass_prism("a1ctr", CTR, DX, DY, "#5E8CEB", 0.42, BLUE) + H.glass_prism("a1tma", TMA, DX, DY, "#8DB0F5", 0.34, BLUE), radius=10))
    out.append(f'<text x="75" y="116" font-family="monospace" font-size="12" font-weight="bold" fill="{BLUE}" text-anchor="middle" stroke="#FFFFFF" stroke-width="3.2" stroke-linejoin="round" paint-order="stroke">CTR</text>')
    out.append(f'<text x="250" y="52" font-family="monospace" font-size="12" font-weight="bold" fill="{BLUE}" text-anchor="middle" stroke="#FFFFFF" stroke-width="3.2" stroke-linejoin="round" paint-order="stroke">TMA</text>')
    out += lower()
    out.append(H.path_line(ROUTE, GREEN, 2.5, dash="7 4", casing=2.4))
    out.append({"name": "sprite-side", "at": [379, 84.8], "width": 54, **H.LOOK, "tint": "#0E9F6E", "tint_strength": 0.5})
    c = S.callout
    out.append("".join(c(k + 1, xg, 386, r=10) for k, xg in enumerate((80, 130, 290, 520, 604))))
    out.append(c(6, 318, 232, r=10) + c(7, 440, 324, 440, 338, r=10))
    return H.flatten(out)


def plate():
    return {
        "id": "fig-17-06-ats-along-a-flight",
        "replaces": "fig-17-06-ats-along-a-flight.svg",
        "book_file": "plate-17-06-ats-along-a-flight.jpg",
        "caption": "Figure 17-6. The air traffic services a VFR flight meets from departure to arrival",
        "desc": "Figure 17-6. The air traffic services a VFR flight meets from departure to arrival",
        "legend": [
            "Aerodrome A: the tower (`TWR`) clears you to taxi and take off [[§91.99(f)]] [[§91.127(i)]].",
            "Leaving the control zone: the tower transfers you, or you report that you are leaving ATC service [[§91.99(g)]].",
            "En route: flight information service (`FIS`).",
            "Approaching aerodrome B, without a tower: TIBA broadcasts [[§91.121(d)]].",
            "After landing: the arrival report [[§91.73(h)]].",
            "Approach control (`APP`), dashed: only if the route enters the TMA or ATC transfers you.",
            "Alerting service, from departure to the arrival report.",
        ],
        "canvas": [640, 400],
        "background": "pale",
        "reskin": {"svg": "fig-17-06-ats-along-a-flight.svg", "blank": True, "layers": layers()},
    }
