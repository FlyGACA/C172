"""Figure 14-3. Sea and land breezes, valley and mountain winds. Four scenes in cards: a coast of the Gulf by day, with the land hot and the cumulus building over it, and by night; a
valley of the hills by day, the heated slopes sending air up under cumulus, and by night, the cold air draining down into a pool of fog. The ribbon arrows are the arrows of the old
figure (the wind at the surface, the air rising, the return flow aloft, the air sinking) and its nine numbered callouts are kept (figs/scene.py makes the scenes, reskin.py lays them
with the clouds of figs/clouds.py)."""
from figs import scene as S

CARDS = {"A": (8, 6, 304, 196), "B": (328, 6, 304, 196), "C": (8, 214, 304, 196), "D": (328, 214, 304, 196)}
DAY = [(0.0, "#3F78C2"), (0.55, "#86B4E6"), (0.95, "#DCEBF8"), (1.0, "#F4F1DF")]
NIGHT = [(0.0, "#1B2748"), (0.6, "#34497D"), (1.0, "#6A7FAE")]
BLUE = ("#2F63C8", "#8DB3F2")
ORANGE = ("#E8782E", "#F8BE73")
INK = ("#1F2937", "#667489")
NIGHT_BLUE = ("#6E92E0", "#B9CFF8")


def stars(x, y, w, h, seed=3, count=22):
    import random
    rnd = random.Random(seed)
    return "".join(f'<circle cx="{S.n(x + rnd.uniform(4, w - 4))}" cy="{S.n(y + rnd.uniform(4, h * 0.5))}" r="{S.n(rnd.uniform(0.5, 1.1))}" fill="#FFFFFF" opacity="{S.n(rnd.uniform(0.5, 1.0))}"/>' for _ in range(count))


def moon(cx, cy):
    return S.glow(f"f1403m{int(cx)}", cx, cy, 28, "#FFF1C8", 0.55) + f'<circle cx="{S.n(cx)}" cy="{S.n(cy)}" r="9" fill="#F7EBC2"/><circle cx="{S.n(cx + 4.8)}" cy="{S.n(cy - 2.6)}" r="8.2" fill="#3D5286"/>'


def tapered(points, x_from, span, base):
    """A ridge line that starts at nothing (at the line `base`) at x_from and reaches its full height over `span`."""
    out = []
    for x, y in points:
        t = max(0.0, min(1.0, (x - x_from) / span))
        t = t * t * (3 - 2 * t)
        out.append((x, base - (base - y) * t))
    return out


def coast(key, night):
    x, y, w, h = CARDS[key]
    hz = y + 112
    shore = x + 150
    land_top = ("#9C8E78", "#B9AB92") if night else ("#D2B880", "#E9D6A8")
    land = f'<defs>{S.gradient("f1403l" + key, [(0, land_top[1]), (1, "#CDB382" if not night else "#8A7F6C")])}</defs>'
    shore_path = f"M {shore},{hz - 2} C {shore + 6},{hz + 30} {shore - 10},{hz + 60} {shore + 4},{y + h} L {x + w},{y + h} L {x + w},{hz - 2} Z"
    land += f'<path d="{shore_path}" fill="url(#f1403l{key})"/>' + f'<path d="M {shore},{hz - 2} C {shore + 6},{hz + 30} {shore - 10},{hz + 60} {shore + 4},{y + h}" fill="none" stroke="#FFFFFF" stroke-width="1.6" stroke-opacity="0.8"/>'
    far = S.land_layer(f"f1403f{key}", tapered(S.ridge(7 if key == "A" else 9, shore - 4, x + w, hz + 1, 52, peaks=0.6), shore - 4, 80, hz + 1), hz + 4, ("#586A97", "#93A3C4") if not night else ("#243257", "#3D4D78"), rim=not night, haze=0.06 if not night else 0.0)
    far += S.land_layer(f"f1403g{key}", tapered(S.ridge(13 if key == "A" else 15, shore - 4, x + w, hz + 2, 26, peaks=0.25), shore - 4, 60, hz + 2), hz + 4, ("#8693B6", "#BCC7DC") if not night else ("#2F3F68", "#4A5B86"), rim=not night, haze=0.06 if not night else 0.0)
    sea_ = S.sea(f"f1403s{key}", x, shore + 4, hz, y + h, seed=5 if key == "A" else 8, light="#3D8CC6" if not night else "#1E3A68", dark="#2C6FAE" if not night else "#101D3B")
    if not night:
        land += S.glow(f"f1403w{key}", x + 250, hz + 20, 70, "#FF9A4A", 0.38)
    land += S.scrub(11, shore + 14, x + w - 4, hz + 6, y + h - 4, 12, colour=("#8A8A55", "#5E603E") if not night else ("#4A4D40", "#33362F"), scale=0.55)
    houses = S.house(x + 224, y + 150, 13, 8, 3) + S.house(x + 246, y + 156, 11, 7, 4) + S.palm(x + 208, y + 166, 24, 0.1, 6) + S.palm(x + 270, y + 160, 21, -0.1, 7) + S.acacia(x + 190, y + 172, 11, 8)
    if night:
        houses += f'<rect x="{S.n(x + 228)}" y="{S.n(y + 145)}" width="1.8" height="2.4" fill="#FFE08A"/><rect x="{S.n(x + 250)}" y="{S.n(y + 152)}" width="1.6" height="2.2" fill="#FFE08A"/>'
    boats = S.dhow(x + 60, y + 150, 0.95) + S.dhow(x + 104, y + 128, 0.6)
    return far + sea_ + land + (houses if True else "") + boats


def valley(key, night, fog_level=None):
    x, y, w, h = CARDS[key]
    top = y + 78
    colours = (("#AFA38E", "#7E7059"), ()) if night else (("#DCCBA6", "#A8916A"), ())
    far = ("#2C3B63", "#46577F") if night else ("#586A97", "#9BAAC8")
    return S.slope_valley(f"f1403v{key}", x, x + w, top, y + h, colours=(colours[0], colours[0]), far=far, fog_level=fog_level, seed=4 if key == "C" else 9, night=night)


def cards():
    out = []
    # A: the coast by day
    ax, ay, aw, ah = CARDS["A"]
    out.append(S.card("f1403A", ax, ay, aw, ah, DAY, S.sun("f1403sa", ax + 40, ay + 30, 9) + coast("A", False)))
    bx, by, bw, bh = CARDS["B"]
    out.append(S.card("f1403B", bx, by, bw, bh, NIGHT, stars(bx, by, bw, bh) + moon(bx + 250, by + 30) + coast("B", True)))
    cx, cy, cw, ch = CARDS["C"]
    out.append(S.card("f1403C", cx, cy, cw, ch, DAY, S.sun("f1403sc", cx + 152, cy + 26, 9) + valley("C", False)))
    dx, dy, dw, dh = CARDS["D"]
    out.append(S.card("f1403D", dx, dy, dw, dh, NIGHT, stars(dx, dy, dw, dh, 5) + moon(dx + 152, dy + 30) + valley("D", True, fog_level=74)))
    return out


def arrows():
    r = S.ribbon
    a = []
    # A: sea breeze at the surface, the air rising over the land, the return flow aloft, the air sinking over the sea
    a.append(r("f1403a1", [(34, 168), (90, 160), (150, 156), (224, 158)], 7.5, *BLUE))
    a.append(r("f1403a2", [(262, 150), (264, 120), (262, 90), (258, 64)], 7.5, *ORANGE))
    a.append(r("f1403a3", [(236, 34), (180, 28), (126, 28), (84, 36)], 6.5, *INK, opacity=0.95))
    a.append(r("f1403a4", [(48, 52), (50, 80), (50, 104), (48, 124)], 6.5, *BLUE))
    # B: the land breeze, weaker
    a.append(r("f1403b1", [(560, 164), (500, 158), (440, 158), (380, 164)], 5.2, *NIGHT_BLUE, opacity=0.95))
    # C: air up the heated slopes
    a.append(r("f1403c1", [(124, 380), (96, 354), (72, 330), (56, 312)], 7.0, *ORANGE))
    a.append(r("f1403c2", [(196, 380), (224, 354), (248, 330), (264, 312)], 7.0, *ORANGE))
    a.append(r("f1403c3", [(158, 340), (158, 300), (158, 268)], 6.0, *BLUE))
    # D: cold air draining down the slopes
    a.append(r("f1403d1", [(366, 322), (392, 346), (420, 370), (442, 386)], 7.0, *NIGHT_BLUE))
    a.append(r("f1403d2", [(594, 322), (568, 346), (540, 370), (518, 386)], 7.0, *NIGHT_BLUE))
    return "".join(a)


def callouts():
    c = S.callout
    return "".join([c(1, 292, 188, 276, 172), c(2, 112, 180, 112, 160), c(3, 292, 82, 264, 100), c(4, 152, 22, 152, 34), c(5, 22, 88, 48, 90),
                    c(6, 612, 188, 596, 172), c(7, 460, 184, 460, 160), c(8, 24, 372, 74, 336), c(9, 456, 308, 408, 350)])


CLOUDS = [{"name": "cloud-cumulus-a", "at": [262, 52], "width": 104}, {"name": "cloud-cumulus-b", "at": [104, 84], "width": 44, "opacity": 0.9},
          {"name": "cloud-cumulus-b", "at": [64, 272], "width": 74}, {"name": "cloud-cumulus-a", "at": [262, 268], "width": 84}]


def plate():
    return {
        "id": "fig-14-03-local-winds",
        "replaces": "fig-14-03-local-winds.svg",
        "book_file": "plate-14-03-local-winds.jpg",
        "caption": "Figure 14-3. Sea and land breezes, valley and mountain winds",
        "desc": "Figure 14-3. Sea and land breezes, valley and mountain winds",
        "legend": [
            "By day the land heats faster than the sea.",
            "Sea breeze at the surface.",
            "Air rising over the land, building cumulus.",
            "Return flow aloft.",
            "Air sinking over the sea.",
            "At night the land cools faster than the sea.",
            "Land breeze, usually weaker.",
            "Valley wind: air rises up the heated slopes and builds cumulus over the ridges.",
            "Mountain wind: cold air drains down and pools in the valley, where fog can form.",
        ],
        "canvas": [640, 420],
        "background": "pale",
        "reskin": {"svg": "fig-14-03-local-winds.svg", "blank": True, "layers": ['<rect x="0" y="0" width="640" height="420" fill="#ffffff"/>', *cards(), *CLOUDS, arrows(), callouts()]},
    }
