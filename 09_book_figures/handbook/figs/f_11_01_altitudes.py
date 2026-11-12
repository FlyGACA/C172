"""Figure 11-1. Elevation, pressure altitude and density altitude on a hot afternoon. A cut through the country in a card: a sea at its mean level with a coast, a plateau of desert rock
rising to the aerodrome at 1 700 ft (a runway seen edge-on, a hangar, a windsock, the model standing on it), the 1 013 hPa level as an amber dashed line 300 ft below the sea level,
the heights as dimension lines (1 700, 2 000 and 5 000 ft) with their numbers, a thermometer on a plaque (36 and 11 degrees), the model's ghost at 5 000 ft for the density altitude,
the scale in feet on the left. Every number and level of the old figure kept, with its six numbered callouts (figs/h_a1.py and figs/scene.py make the pieces)."""
from figs import h_a1 as H
from figs import scene as S

CARD = (62, 14, 568, 322)
BLUE, AMBER, INK = "#1E40AF", "#C86A08", "#1F2937"


def y_of(ft):
    return 286.0 - 0.044 * ft


def sea():
    x, y, w, h = CARD
    out = [f'<defs>{S.gradient("a1sg", [(0, "#8CCDF0"), (0.12, "#4F9ED8"), (1, "#173F73")])}</defs><rect x="{x}" y="286" width="{w}" height="{y + h - 286}" fill="url(#a1sg)"/>']
    out.append(S.sea("a1sea", x, x + w, 286, 304, seed=4, light="#4A98D4", dark="#7CC4EE"))
    # light slanting down into the water
    for k in range(7):
        x0 = 90 + k * 82
        out.append(f'<polygon points="{x0},286 {x0 + 20},286 {x0 + 8},334 {x0 - 18},334" fill="#FFFFFF" fill-opacity="0.07"/>')
    return "".join(out)


def plateau():
    outline = [(175, 286)] + S.jag([(175, 286), (225, 211.2)], 2.0, 3, parts=7)[1:-1] + S.jag([(225, 211.2), (380, 211.2)], 0.35, 5, parts=10) + S.jag([(380, 211.2), (400, 228.8)], 1.2, 7, parts=3)[1:]
    rock = S.rock("a1pl", outline, 334, 175, 400, 5, tones=("#E3CFA2", "#8F7048"))
    strata = []
    for k, off in enumerate((16, 34, 54, 78, 104)):
        strata.append(f'<path d="M 175,{286 + off * 0.2} L 225,{211.2 + off} L 380,{211.2 + off} L 400,{228.8 + off}" fill="none" stroke="#3B2C1B" stroke-opacity="{0.10 + 0.012 * k}" stroke-width="{0.9 + 0.2 * k}"/>')
    cap = '<rect x="225" y="209.8" width="155" height="2.4" fill="#F3E6BF"/>'
    return rock + f'<g clip-path="url(#a1plc)">{"".join(strata)}</g>' + cap


def aerodrome():
    out = [H.hangar(231, 208.6, 22, 12), H.windsock(374, 208.6, 17, wind=-1)]
    out.append(H.runway("a1rw", 245, 366, 209.2, half=2.2, centre=True, threshold=True, lights=True, dash_from=262))
    out.append(S.acacia(381, 211.2, 9, 3))
    return "".join(out)


def levels():
    out = [H.line_cased(62, 66, 630, 66, "#FFFFFF", 1.2, dash="3 3", casing=1.8, opacity=0.85),
           H.line_cased(140, 211.2, 225, 211.2, "#5B6578", 1.2, dash="3 3", casing=2.0), H.line_cased(380, 211.2, 462, 211.2, "#5B6578", 1.2, dash="3 3", casing=2.0)]
    out.append(f'<line x1="62" y1="286" x2="630" y2="286" stroke="#FFFFFF" stroke-width="5.4" stroke-opacity="0.7"/><line x1="62" y1="286" x2="630" y2="286" stroke="{BLUE}" stroke-width="2.5"/>')
    out.append(H.line_cased(62, 299.2, 630, 299.2, "#F59E0B", 2.0, dash="7 4", casing=2.2))
    return "".join(out)


def thermometer():
    x, y, w, h = 502, 94, 68, 138
    out = [H.card("a1th", x, y, w, h, 8)]
    out.append(f'<defs>{S.gradient("a1tube", [(0, "#DCE4EF"), (0.5, "#FFFFFF"), (1, "#C5D0E0")], 0, 0, 1, 0)}{S.gradient("a1hg", [(0, "#FF9A3C"), (1, "#C94F00")], 0, 0, 1, 0)}</defs>')
    out.append('<rect x="514.4" y="104" width="11.2" height="104" rx="5.6" fill="url(#a1tube)" stroke="#334155" stroke-width="1.4"/>')
    out.append('<circle cx="520" cy="212" r="10.4" fill="url(#a1tube)" stroke="#334155" stroke-width="1.4"/>')
    out.append('<rect x="517.5" y="118" width="5" height="92" fill="url(#a1hg)"/><circle cx="520" cy="212" r="8" fill="url(#a1hg)"/><circle cx="517" cy="209" r="2.4" fill="#FFFFFF" opacity="0.55"/><rect x="518" y="120" width="1.4" height="84" fill="#FFFFFF" opacity="0.45"/>')
    for yy in range(112, 204, 10):
        out.append(f'<line x1="528" y1="{yy}" x2="531" y2="{yy}" stroke="#94A3B8" stroke-width="0.8"/>')
    out.append('<line x1="526" y1="118" x2="534" y2="118" stroke="#C86A08" stroke-width="2.2"/><line x1="526" y1="168" x2="534" y2="168" stroke="#1E40AF" stroke-width="2.2"/>')
    out.append('<text x="537" y="122" font-family="sans-serif" font-size="12" font-weight="bold" fill="#C86A08" text-anchor="start">36°</text>'
               '<text x="537" y="172" font-family="sans-serif" font-size="12" font-weight="bold" fill="#1E40AF" text-anchor="start">11°</text>')
    return "".join(out)


def scale():
    out = ['<line x1="62" y1="330" x2="62" y2="22" stroke="#334155" stroke-width="2"/>']
    labels = [(-1000, "−1 000"), (0, "0"), (1000, "1 000"), (2000, "2 000"), (3000, "3 000"), (4000, "4 000"), (5000, "5 000"), (6000, "6 000")]
    for ft, t in labels:
        yy = y_of(ft)
        out.append(f'<line x1="58" y1="{S.n(yy)}" x2="66" y2="{S.n(yy)}" stroke="#334155" stroke-width="1.4"/>'
                   f'<text x="54" y="{S.n(yy + 4)}" font-family="sans-serif" font-size="11" fill="#475569" text-anchor="end">{t}</text>')
    return "".join(out)


def layers():
    x, y, w, h = CARD
    out = [H.page("a1page", 640, 360), H.defs()]
    out.append(S.card("a1ca", x, y, w, h, H.horizon_sky((286 - y) / h), S.glow("a1cg", 130, 60, 200, "#FFF1CC", 0.5), radius=10))
    out += [H.cloud("cloud-cumulus-b", 150, 70, 54), H.cloud("cloud-cumulus-a", 330, 52, 64, 0.9), H.cloud("cloud-cumulus-b", 440, 140, 38, 0.8)]
    out.append(f'<defs><clipPath id="a1plc"><polygon points="175,286 225,211.2 380,211.2 400,228.8 400,334 175,334"/></clipPath></defs>')
    world = sea() + plateau() + aerodrome()
    out.append(S.card_front("a1cw", x, y, w, h, world, radius=10))
    out.append(S.card_front("a1cl", x, y, w, h, levels(), radius=10))
    out.append(H.dim_line(150, 285, 150, 212.2, INK, 1.8, head=6.5))
    out.append(H.pill(120, 250, 48, 18, "1 700", INK, 12, border="#8793A8"))
    out.append(H.dim_line(450, 298.2, 450, 212.2, AMBER, 2.0, head=6.5))
    out.append(H.pill(482, 258, 48, 18, "2 000", AMBER, 12, border="#E5B06A"))
    out.append(H.dim_line(598, 285, 598, 67, BLUE, 2.5, head=7))
    out.append(H.pill(570, 262, 48, 18, "5 000", BLUE, 12, border="#8FA7E6"))
    out.append(thermometer())
    out.append({"name": "sprite-side", "at": [300, 201.2], "width": 62, **H.LOOK})
    out.append(H.drop_shadow(306, 211.8, 54, 1.8, 0.4))
    out.append({"name": "sprite-side", "at": [557, 51.5], "width": 64, "opacity": 0.55, "tint": "#7FA2F0", "tint_strength": 0.5, **H.LOOK})
    out.append('<ellipse cx="557" cy="50" rx="36" ry="13" fill="none" stroke="#1E40AF" stroke-width="1.3" stroke-dasharray="3 2.4" opacity="0.8"/>')
    out.append(scale())
    c = S.callout
    out.append("".join([c(1, 100, 266, 112, 285), c(2, 300, 164, 300, 184), c(3, 100, 320, 112, 300.5), c(4, 426, 244, 448, 252), c(5, 494, 132, 515, 138), c(6, 618, 128, 600, 128)]))
    return H.flatten(out)


def plate():
    return {
        "id": "fig-11-01-altitudes",
        "replaces": "fig-11-01-altitudes.svg",
        "book_file": "plate-11-01-altitudes.jpg",
        "caption": "Figure 11-1. Elevation, pressure altitude and density altitude on a hot afternoon",
        "desc": "Figure 11-1. Elevation, pressure altitude and density altitude on a hot afternoon",
        "legend": [
            "Mean sea level.",
            "The aerodrome, elevation 1 700 ft.",
            "The level where the pressure is 1 013 hPa; with QNH 1 003 hPa it lies about 300 ft below sea level.",
            "Pressure altitude: the aerodrome is 2 000 ft above the 1 013 hPa level.",
            "Outside air temperature 36 °C, against the ISA temperature of 11 °C at that pressure altitude.",
            "Density altitude: the aeroplane performs as it would 5 000 ft above sea level in the standard atmosphere.",
        ],
        "canvas": [640, 360],
        "background": "pale",
        "reskin": {"svg": "fig-11-01-altitudes.svg", "blank": True, "layers": layers()},
    }
