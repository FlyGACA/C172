"""Figure 18-1. The parts of an aerodrome seen from above. An aerial picture of an aerodrome on the desert plain (figs/terrain.py): a runway of dark asphalt with worn paint and edge
lights, a parallel taxiway joined to it by three taxiways, each with its holding-position marking, an apron with the aeroplanes of the model parked on it, a control tower, a windsock
and a signal area, with the manoeuvring area and the movement area as dashed outlines on tinted ground (as the old figure had them). The ten numbered callouts of the old figure are
kept, in the same order and meaning (figs/scene.py makes the callouts, figs/h_a2.py the pavement, the lights and the buildings)."""
from figs import h_a2 as H
from figs import scene as S
from figs import terrain

W, HT = 640, 330
terrain.ensure("terrain-18-01", size=(W * 4, HT * 4), seed=181, kind="plain", features=("wadis", "tracks"), veil=0.30, soft=2.8)

U = "a181"
YEL = "#F2C230"
PAINT = "#F6F3EA"


def defs():
    return ("<defs>" + H.asphalt_filter(U + "as", seed=4, relief=0.8, tone=0.0) + H.asphalt_filter(U + "at", seed=9, relief=0.7, tone=0.35) + H.concrete_filter(U + "co", seed=8)
            + H.paint_filter(U + "pw", seed=11, wear=1.0, thickness=0.45) + H.paint_filter(U + "py", seed=21, wear=0.8, thickness=0.4)
            + H.lamp_defs(U + "l") + H.shadow_filter(U + "sh", 1.3, 1.9, 1.2, 0.32) + H.blur_filter(U + "bl", 1.0) + "</defs>")


def zones():
    """The movement area and the manoeuvring area: tinted ground and dashed outlines with a white casing, as the old figure had them (orange, blue)."""
    mov = [(46, 76), (594, 76), (594, 240), (436, 240), (436, 302), (208, 302), (208, 240), (46, 240)]
    out = [f'<polygon points="{S.pts(mov)}" fill="#E8913A" fill-opacity="0.20"/>',
           f'<rect x="58" y="88" width="524" height="144" rx="8" fill="#3B6FE0" fill-opacity="0.15"/>']
    out.append(f'<polygon points="{S.pts(mov)}" fill="none" stroke="#FFFFFF" stroke-opacity="0.85" stroke-width="3.8" stroke-linejoin="round"/>'
               f'<polygon points="{S.pts(mov)}" fill="none" stroke="#B45309" stroke-width="1.7" stroke-linejoin="round" stroke-dasharray="8 5"/>')
    out.append(f'<rect x="58" y="88" width="524" height="144" rx="8" fill="none" stroke="#FFFFFF" stroke-opacity="0.85" stroke-width="3.8"/>'
               f'<rect x="58" y="88" width="524" height="144" rx="8" fill="none" stroke="#1D4ED8" stroke-width="1.7" stroke-dasharray="8 5"/>')
    return "".join(out)


def pavement():
    """The runway, the three connecting taxiways and the parallel taxiway as one piece of asphalt (the infields are holes), on a graded shoulder; then the apron of concrete."""
    r = 5.0
    outer = (f"M 74,110 L 566,110 L 566,142 L 529.5,142 L 529.5,{228 - r} A {r},{r} 0 0 1 {529.5 - r},228 L {110.5 + r},228 A {r},{r} 0 0 1 110.5,{228 - r} L 110.5,142 L 74,142 Z")
    holes = H.rrect_path(129, 142, 182, 68, 6) + " " + H.rrect_path(329, 142, 182, 68, 6)
    d = outer + " " + holes
    out = [f'<path d="{d}" fill="#C8B78F" fill-opacity="0.55" fill-rule="evenodd" stroke="#C8B78F" stroke-opacity="0.55" stroke-width="7" stroke-linejoin="round"/>',
           f'<path d="{d}" fill="#444" fill-rule="evenodd" filter="url(#{U}as)"/>']
    # a slightly lighter, more worn surface on the taxiways (a second pass over them, soft at the edge)
    out.append(f'<rect x="110.5" y="210" width="419" height="18" fill="#444" filter="url(#{U}at)" opacity="0.55"/>')
    out.append(f'<path d="{d}" fill="none" fill-rule="evenodd" stroke="#14181F" stroke-opacity="0.35" stroke-width="0.5"/>')
    # the apron: concrete slabs
    out.append(f'<rect x="222" y="228" width="200" height="62" fill="#999" filter="url(#{U}co)"/>')
    joints = []
    for gx in range(242, 422, 20):
        joints.append(f'<line x1="{gx}" y1="228" x2="{gx}" y2="290" />')
    for gy in (248, 268):
        joints.append(f'<line x1="222" y1="{gy}" x2="422" y2="{gy}" />')
    out.append(f'<g stroke="#6F7680" stroke-opacity="0.55" stroke-width="0.45">{"".join(joints)}</g>')
    out.append(f'<rect x="222" y="228" width="200" height="62" fill="none" stroke="#7A828C" stroke-opacity="0.7" stroke-width="0.6"/>')
    # a forecourt in front of the terminal
    out.append(f'<rect x="196" y="258" width="26" height="26" fill="#999" filter="url(#{U}co)"/>')
    return "".join(out)


def road():
    """An access road to the terminal from the left edge of the picture."""
    d = "M -4,310 C 40,310 90,306 130,304 L 198,303"
    return (f'<path d="{d}" fill="none" stroke="#B9A883" stroke-opacity="0.6" stroke-width="12" stroke-linecap="round"/>'
            f'<path d="{d}" fill="none" stroke="#444" stroke-width="8" stroke-linecap="round" filter="url(#{U}at)"/>'
            f'<path d="{d}" fill="none" stroke="{PAINT}" stroke-opacity="0.85" stroke-width="0.7" stroke-dasharray="6 5"/>')


def markings():
    out = []
    # rubber of the wheels in the touchdown zones: soft dark streaks along the centreline
    for x0, x1 in ((150, 236), (404, 490)):
        for y in (121.0, 131.0):
            out.append(f'<rect x="{x0}" y="{y}" width="{x1 - x0}" height="3.2" rx="1.6" fill="#0B0F16" opacity="0.16" filter="url(#{U}bl)"/>')
    # the runway: a centreline of dashes, the threshold bars at both ends, the designators
    dash = "".join(f'<rect x="{x}" y="125.3" width="14" height="1.5"/>' for x in range(126, 506, 26))
    bars = "".join(f'<rect x="{x}" y="{y - 0.8}" width="12" height="1.6"/>' for x in (77, 551) for y in (114, 117.2, 120.4, 123.6, 128.4, 131.6, 134.8, 138))
    nums = H.glyph_text("09", 104, 126, 11, PAINT, rotate=90, spacing=1.2, stroke=PAINT, stroke_width=0.3) + H.glyph_text("27", 536, 126, 11, PAINT, rotate=-90, spacing=1.2, stroke=PAINT, stroke_width=0.3)
    out.append(f'<g fill="{PAINT}" filter="url(#{U}pw)">{dash}{bars}{nums}</g>')
    # the taxiways: yellow centrelines and the runway-holding positions (two solid lines on the taxiway side, two dashed on the runway side)
    lines = ['<line x1="110.5" y1="219" x2="529.5" y2="219" stroke-width="1.3"/>']
    for cx in (120, 320, 520):
        lines.append(f'<line x1="{cx}" y1="142" x2="{cx}" y2="219" stroke-width="1.3"/>')
        lines.append(f'<line x1="{cx - 9}" y1="174" x2="{cx + 9}" y2="174" stroke-width="1.5"/><line x1="{cx - 9}" y1="171" x2="{cx + 9}" y2="171" stroke-width="1.5"/>')
        lines.append(f'<line x1="{cx - 9}" y1="166.2" x2="{cx + 9}" y2="166.2" stroke-width="1.5" stroke-dasharray="3.4 2.6"/><line x1="{cx - 9}" y1="163.2" x2="{cx + 9}" y2="163.2" stroke-width="1.5" stroke-dasharray="3.4 2.6"/>')
    out.append(f'<g stroke="{YEL}" fill="none" filter="url(#{U}py)">{"".join(lines)}</g>')
    # the stands of the apron: a taxilane line and a lead-in line to each stand with a stop bar at its end
    stand = ['<line x1="224" y1="238" x2="420" y2="238" stroke-width="1.1"/>']
    for x in (282, 318, 354, 390):
        stand.append(f'<line x1="{x}" y1="238" x2="{x}" y2="282" stroke-width="0.9"/><line x1="{x - 4}" y1="282" x2="{x + 4}" y2="282" stroke-width="1.2"/>')
    out.append(f'<g stroke="{YEL}" stroke-opacity="0.9" fill="none" filter="url(#{U}py)">{"".join(stand)}</g>')
    # the edge of the apron: a dashed line
    out.append(f'<line x1="222" y1="228.4" x2="422" y2="228.4" stroke="#FFFFFF" stroke-opacity="0.55" stroke-width="0.7" stroke-dasharray="3 3"/>')
    return "".join(out)


def edge_lights():
    out = []
    for x in range(80, 565, 24):
        for y in (107.8, 144.2):
            out.append(H.lamp(U + "l", x, y, 0.85, "white", 3.4, 0.9))
    return "".join(out)


def terrain_bits():
    """Bushes and a few trees on the plain, away from the pavements."""
    out = []
    out.append(S.scrub(18, 6, 120, 20, 70, 7, scale=0.9) + S.scrub(19, 262, 360, 14, 66, 6, scale=0.9) + S.scrub(20, 440, 634, 10, 62, 9, scale=0.9)
               + S.scrub(21, 6, 190, 246, 328, 9, scale=0.9) + S.scrub(22, 450, 634, 308, 328, 5, scale=0.9) + S.scrub(23, 4, 40, 90, 232, 6, scale=0.9))
    return "".join(out)


def buildings():
    out = []
    # the terminal: a long low building at the apron's left end, glazed on the apron side
    out.append(H.block(138, 290, 62, 14, 16, "#E8D9B6", roof="#F4EBD2", uid=U + "tm", window="#33506F"))
    out.append(H.block(146, 272, 9, 3, 3.4, "#C9CFD6", uid=U + "r1", shadow=False) + H.block(166, 272, 7, 3, 3.0, "#C9CFD6", uid=U + "r2", shadow=False)
               + f'<polygon points="{S.pts([(156, 290), (178, 290), (181, 288.2), (159, 288.2)])}" fill="#5B6577"/>')
    # the control tower and the signal area on the right of the apron
    out.append(H.tower(U + "tw", 484, 298, 1.0))
    # the signal area: a square of concrete with a dark painted square and a white outline, white markers at the corners
    out.append(f'<rect x="518" y="268" width="28" height="28" fill="#999" filter="url(#{U}co)"/><rect x="518" y="268" width="28" height="28" fill="none" stroke="#7A828C" stroke-width="0.5"/>'
               f'<rect x="522" y="272" width="20" height="20" fill="#2A3140"/><rect x="522" y="272" width="20" height="20" fill="none" stroke="#10151F" stroke-opacity="0.5" stroke-width="0.4"/>'
               f'<g filter="url(#{U}py)"><rect x="524.5" y="274.5" width="15" height="15" fill="none" stroke="{PAINT}" stroke-width="1.2"/></g>')
    # the fuel area: three tanks inside a low wall
    out.append(f'<rect x="562" y="262" width="62" height="52" rx="3" fill="#D9CBA2" fill-opacity="0.8" stroke="#B3A37C" stroke-width="1.2"/>')
    for (x, y) in ((578, 276), (606, 276), (592, 297)):
        out.append(H.tank(U + f"k{x}", x, y, 7.2))
    return "".join(out)


def trees():
    out = []
    for i, (x, y, s) in enumerate([(124, 262, 0.55), (214, 306, 0.5), (134, 306, 0.55), (60, 284, 0.55), (36, 270, 0.5), (606, 52, 0.5), (24, 62, 0.55), (470, 52, 0.5), (14, 320, 0.5)]):
        out.append(S.palm(x, y, 26 * s, 0.1, 50 + i) if i % 2 == 0 else S.acacia(x, y, 14 * s * 1.25, 50 + i))
    return "".join(out)


def aeroplanes():
    out = []
    shadow = {"dx": 1.5, "dy": 2.3, "blur": 1.7, "opacity": 0.32}
    sprites = [{"name": "sprite-top", "at": [x, 260], "width": 28, "angle": 180, "shadow": shadow} for x in (282, 318, 354, 390)]
    sprites.append({"name": "sprite-top", "at": [320, 190], "width": 27, "angle": 0, "tint": "#2F66D6", "tint_strength": 0.62, "shadow": shadow})
    return sprites


def signs():
    out = []
    for letter, x, y in (("A", 92, 226), ("B", 140, 207), ("C", 340, 207), ("D", 540, 207)):
        out.append(H.sign(U + "s" + letter, x, y, letter, w=9.5, h=8.0, post=4.5))
    return "".join(out)


def callouts():
    c = S.callout
    return "".join([
        c(1, 372, 99, 372, 120), c(2, 34, 126, 94, 126), c(3, 200, 188, 200, 214), c(4, 160, 169, 131, 169), c(5, 322, 316, 322, 284),
        c(6, 616, 108, 582, 108), c(7, 618, 60, 594, 76), c(8, 254, 38, 227, 38), c(9, 532, 316, 532, 297), c(10, 484, 316, 484, 301)])


def layers():
    return [{"name": "terrain-18-01", "at": [W / 2, HT / 2], "width": W}, defs(), terrain_bits(), zones(), road(), pavement(), markings(), edge_lights(),
            *aeroplanes(), buildings(), H.windsock(U + "ws", 200, 72, length=31, angle=84, mouth=9, droop=0.10, pole=36), trees(), signs(), callouts()]


def plate():
    return {
        "id": "fig-18-01-aerodrome-plan",
        "replaces": "fig-18-01-aerodrome-plan.svg",
        "book_file": "plate-18-01-aerodrome-plan.jpg",
        "caption": "Figure 18-1. The parts of an aerodrome seen from above",
        "desc": "Figure 18-1. The parts of an aerodrome seen from above",
        "legend": [
            "Runway 09/27.",
            "Runway designator: `09` at the west end, `27` at the east end.",
            "Parallel taxiway `A`, joined to the runway by taxiways `B`, `C` and `D`.",
            "Runway-holding position, the holding point where an aircraft stops before entering the runway.",
            "Apron.",
            "Manoeuvring area: runway and taxiways.",
            "Movement area: the manoeuvring area and the apron.",
            "Windsock.",
            "Signal area.",
            "Aerodrome control tower.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"svg": "fig-18-01-aerodrome-plan.svg", "blank": True, "layers": layers()},
    }
