"""Figure 9-3. A vacuum system driving the attitude and heading indicators. Cabin air drawn through the inlet filter, the two gyro instruments of the model themselves (the attitude indicator
and the heading indicator, in parallel), a suction gauge on the line, the relief valve that lets air in to hold the suction constant, and the engine-driven vacuum pump that blows the air
overboard. The instruments are the sprites of the twin, the rest is drawn by this module (figs/parts.py has the pipes, figs/scene.py the callouts); the seven numbered callouts of
the old figure are kept."""
from figs import parts as P
from figs import scene as S

n = S.n
PURPLE = ("#7C57D6", "#3A237F", "#D9CCFA")
CYAN = ("#59B8E8", "#1B5F86", "#D5F0FC")
SHADOW = {"dx": 1.5, "dy": 3, "blur": 2.6, "opacity": 0.3}


def air_filter():
    x0, y0, x1, y1 = 40, 130, 124, 206
    pleats = "".join(f'<path d="M {n(x0 + 8 + i * 7)},{n(y0 + 7)} v {n(y1 - y0 - 14)}" stroke="#B9A57A" stroke-width="1.5"/><path d="M {n(x0 + 11.5 + i * 7)},{n(y0 + 7)} v {n(y1 - y0 - 14)}" stroke="#FFFFFF" stroke-width="1.1" opacity="0.7"/>' for i in range(int((x1 - x0 - 16) / 7) + 1))
    return (f'<g filter="url(#ptsh)"><rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" rx="10" fill="url(#ptsteelv)" stroke="#5A6578" stroke-width="1.2"/></g>'
            f'<rect x="{x0 + 5}" y="{y0 + 5}" width="{x1 - x0 - 10}" height="{y1 - y0 - 10}" rx="6" fill="#E8DDBE" stroke="#B9A57A" stroke-width="1"/>' + pleats
            + f'<rect x="{x1}" y="{n((y0 + y1) / 2 - 9)}" width="14" height="18" rx="3" fill="url(#ptsteel)" stroke="#5A6578" stroke-width="0.9"/>')


def pump():
    return (f'<g filter="url(#ptsh)"><rect x="446" y="244" width="170" height="92" rx="12" fill="url(#ptblueh)" stroke="#183A74" stroke-width="1.2"/></g>'
            f'<rect x="454" y="249" width="154" height="5" rx="2.5" fill="#FFFFFF" opacity="0.35"/>'
            + "".join(f'<line x1="{n(x)}" y1="262" x2="{n(x)}" y2="326" stroke="#16356B" stroke-opacity="0.35" stroke-width="1.6"/>' for x in range(578, 608, 7))
            + f'<g filter="url(#ptsh)"><rect x="486" y="214" width="66" height="44" rx="8" fill="url(#ptsteelv)" stroke="#5A6578" stroke-width="1.1"/><circle cx="519" cy="236" r="14" fill="url(#ptblack)" stroke="#0E1422" stroke-width="1"/></g>'
              f'<circle cx="519" cy="236" r="9" fill="url(#ptsteel)" stroke="#5A6578" stroke-width="0.9"/>'
            + "".join(f'<rect x="{n(515.4 + 0 * i)}" y="{n(226)}" width="7.2" height="20" rx="1.6" fill="#3A4458" transform="rotate({a} 519 236)"/>' for i, a in enumerate((0, 90)))
            + '<circle cx="519" cy="236" r="2.4" fill="#EEF2F8"/>')


def relief_valve():
    return (f'<g filter="url(#ptsh)"><rect x="394" y="164" width="26" height="40" rx="5" fill="url(#ptbrass)" stroke="#7A5614" stroke-width="1"/></g>'
            f'<path d="M 400,172 l 14,4 l -14,4 l 14,4 l -14,4 l 14,4" fill="none" stroke="#7A5614" stroke-width="1.6" stroke-linejoin="round"/>'
            f'<rect x="398" y="204" width="18" height="10" rx="2" fill="url(#ptsteel)" stroke="#5A6578" stroke-width="0.9"/>'
            + P.tube([(407, 252), (407, 218)], *CYAN, w=4.4, shadow=False) + P.chevrons([(407, 252), (407, 220)], every=18, size=3.0))


def suction_gauge():
    return P.dial_vector(362, 62, 26, needle_deg=-8, arc=(-40, 40, "#2E9E5B"))


def lines():
    inlet = [(0, 168), (40, 168)]
    feed = [(138, 168), (176, 168), (176, 100), (206, 100)]
    feed2 = [(176, 168), (176, 266), (206, 266)]
    out_a = [(294, 100), (330, 100), (330, 168)]
    out_b = [(294, 266), (330, 266), (330, 168)]
    manifold = [(330, 168), (519, 168), (519, 214)]
    gauge = [(362, 88), (362, 168)]
    overboard = [(552, 236), (590, 236), (590, 200), (632, 200)]
    parts_ = [P.tube(inlet, *CYAN, w=7), P.tube(feed, *PURPLE, w=7), P.tube(feed2, *PURPLE, w=7), P.tube(out_a, *PURPLE, w=7), P.tube(out_b, *PURPLE, w=7), P.tube(manifold, *PURPLE, w=7), P.tube(gauge, *PURPLE, w=5.5, shadow=False),
              P.tube(overboard, *CYAN, w=7)]
    parts_ += [P.chevrons(feed, every=26), P.chevrons(feed2, every=26), P.chevrons(out_a, every=26), P.chevrons(out_b, every=26), P.chevrons(manifold, every=30), P.chevrons(overboard, every=26, colour="#1B5F86"), P.chevrons(inlet, every=18)]
    return "".join(parts_) + "".join(f'<circle cx="{n(x)}" cy="{n(y)}" r="4.2" fill="#3A237F" stroke="#FFFFFF" stroke-width="1.2"/>' for x, y in ((176, 168), (330, 168), (362, 168)))


def callouts():
    c = S.callout
    return "".join([c(1, 82, 234, 82, 208), c(2, 250, 28, 250, 54), c(3, 250, 312, 250, 286), c(4, 410, 36, 386, 52), c(5, 460, 176, 424, 184), c(6, 410, 308, 450, 296), c(7, 604, 168, 592, 198)])


def plate():
    return {
        "id": "fig-09-03-vacuum-system",
        "replaces": "fig-09-03-vacuum-system.svg",
        "book_file": "plate-09-03-vacuum-system.jpg",
        "caption": "Figure 9-3. A vacuum system driving the attitude and heading indicators",
        "desc": "Figure 9-3. A vacuum system driving the attitude and heading indicators",
        "legend": ["Inlet air filter.", "Attitude indicator.", "Heading indicator.", "Suction gauge.", "Relief valve.", "Engine-driven vacuum pump.", "Overboard outlet."],
        "canvas": [640, 360],
        "background": "pale",
        "reskin": {"svg": "fig-09-03-vacuum-system.svg", "blank": True,
                   "layers": [P.defs(), '<rect x="0" y="0" width="640" height="360" fill="url(#ptbg)"/>', lines(), air_filter(), pump(), relief_valve(), suction_gauge(),
                              {"name": "dial-31-04-ai", "at": [250, 100], "width": 92, "shadow": SHADOW}, {"name": "dial-09-03-dg", "at": [250, 266], "width": 92, "shadow": SHADOW}, callouts()]},
    }
