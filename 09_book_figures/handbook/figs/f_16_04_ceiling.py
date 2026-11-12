"""Figure 16-4. Cloud base and ceiling with three layers of cloud. A card with the height scale of the old figure on its left: a graded sky over a desert aerodrome (hills on the horizon,
a plain with scrub, a runway seen edge-on, a control tower), the clouds of the model of the sky (figs/clouds.py) each standing on the height of its base: two few, four scattered
(cumulus), and the broken layer, three stretches of stratocumulus whose base is the ceiling; the 1 000 ft line, the 4 500 ft dimension and the METAR groups of the old figure, with its five
numbered callouts (figs/h_a1.py and figs/scene.py make the pieces)."""
from figs import h_a1 as H
from figs import scene as S

CARD = (70, 14, 560, 360)
GY = 331.0
RED, INK = "#B91C1C", "#1F2937"


def on_base(name, cx, base, width, aspect, height=None):
    h = height or width / aspect
    return {"name": name, "at": [cx, round(base - h / 2, 1)], "width": width, **({"height": height} if height else {})}


CLOUDS = [
    on_base("cloud-cumulus-b", 185, 214, 72, 2.37), on_base("cloud-cumulus-a", 408, 214, 58, 2.53),                                   # FEW020
    on_base("cloud-cumulus-b", 140, 156, 80, 2.37), on_base("cloud-cumulus-a", 250, 156, 70, 2.53), on_base("cloud-cumulus-b", 372, 156, 84, 2.37),
    on_base("cloud-cumulus-a", 487, 156, 64, 2.53),                                                                                   # SCT030
    on_base("cloud-stratocumulus", 163, 69, 174, 7.33, 32), on_base("cloud-stratocumulus", 374, 69, 192, 7.33, 34), on_base("cloud-stratocumulus", 558, 69, 132, 7.33, 28),     # BKN045
]


def scale():
    out = [f'<line x1="70" y1="330" x2="70" y2="28.4" stroke="{INK}" stroke-width="1.5"/>']
    for ft, y in ((0, 330), (1000, 272), (2000, 214), (3000, 156), (4000, 98), (5000, 40)):
        t = "0" if ft == 0 else f"{ft // 1000} 000"
        out.append(f'<line x1="64" y1="{y}" x2="70" y2="{y}" stroke="{INK}" stroke-width="1.5"/><text x="58" y="{y + 4}" font-family="sans-serif" font-size="12" fill="{INK}" text-anchor="end">{t}</text>')
    return "".join(out)


def metar(x, y, text):
    return (f'<rect x="{x - 36}" y="{y - 16}" width="72" height="22" rx="5" fill="#FFFFFF" fill-opacity="0.9"/>'
            f'<text x="{x}" y="{y}" font-family="monospace" font-size="15" font-weight="bold" fill="{INK}" text-anchor="middle">{text}</text>')


def layers():
    x, y, w, h = CARD
    out = [H.page("a1page", 640, 380), H.defs()]
    objects = H.control_tower(594, GY - 1, 38) + H.hangar(366, GY - 4.4, 26, 13)
    out += H.profile("a1c", CARD, GY + 2, seed=121, sun=(110, 60), far=24, mid=11, base=13, sky=H.horizon_sky((GY - y) / h), scrub_count=16, grain=False,
                     runway_args={"x0": 400, "x1": 570, "half": 3.0, "threshold": False, "dash_from": 416}, clouds=[], palms=[(112, GY - 5, 0.55), (130, GY - 3, 0.45)],
                     acacias=[(250, GY - 4, 0.5)], objects=objects)
    out.append(f'<defs><clipPath id="a1cclip"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10"/></clipPath></defs>')
    out += CLOUDS
    out.append(H.foreground("a1xc", CARD, GY, seed=121, lights=(400, 570), scrub=8, scale=1.1))
    out.append(scale())
    out.append(H.line_cased(70, 272, 630, 272, RED, 2.0, dash="8 5", casing=2.4))
    out.append(H.dim_line(300, 71, 300, 328, RED, 3.0, head=10, casing=3.0))
    out.append(H.pill(333, 176.2, 50, 22, "4 500", RED, 14, border=RED))
    out.append(metar(588, 206, "FEW020") + metar(588, 144, "SCT030") + metar(588, 87, "BKN045"))
    c = S.callout
    out.append("".join([c(1, 138, 200, 158, 198), c(2, 88, 142, 106, 140), c(3, 88, 85, 96, 71), c(4, 485, 352, 485, 336), c(5, 612, 258, 612, 271)]))
    return H.flatten(out)


def plate():
    return {
        "id": "fig-16-04-ceiling",
        "replaces": "fig-16-04-ceiling.svg",
        "book_file": "plate-16-04-ceiling.jpg",
        "caption": "Figure 16-4. Cloud base and ceiling with three layers of cloud",
        "desc": "Figure 16-4. Cloud base and ceiling with three layers of cloud",
        "legend": [
            "`FEW020`: the lowest cloud base, 2 000 ft, but not a ceiling.",
            "`SCT030`: scattered, not a ceiling.",
            "`BKN045`: the lowest broken layer, so the ceiling is 4 500 ft.",
            "The aerodrome: report heights are measured from its elevation.",
            "1 000 ft: under a lower ceiling you may not fly VFR beneath it within controlled airspace designated to the surface for an aerodrome [[§91.165(d)]].",
        ],
        "canvas": [640, 380],
        "background": "pale",
        "reskin": {"svg": "fig-16-04-ceiling.svg", "blank": True, "layers": layers()},
    }
