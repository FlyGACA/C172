"""Figure 21-6. Primary radar, secondary radar and ADS-B. Drawn again as an illustrated picture on the old figure's canvas: a sky over the curve of the earth, the radar on its tower
(a dish with the secondary antenna on top of it, and the beam as a translucent wedge), the aeroplane of the model with its reply, the high ground and the shadow behind it, the ADS-B
ground station and a second aeroplane, and the display with its two targets. Every callout, code and altitude of the old figure is kept (figs/h_a4.py has the parts)."""
import math

from figs import h_a4 as H
from figs import scene as S

SKY = [(0.0, "#4A82C8"), (0.45, "#86B1E0"), (0.78, "#CBE0F3"), (1.0, "#F6EFD9")]
APEX, RADIUS = 292.0, 1800.0


def gy(x):
    return APEX + RADIUS - math.sqrt(RADIUS * RADIUS - (x - 320.0) ** 2)


def beam_wedge():
    """The beam of the primary radar: a translucent wedge from the dish toward the aeroplane, and two fainter ones where it was a moment ago and will be."""
    x0, y0 = 98.0, 226.0
    out = ['<defs>' + S.gradient("a6w", [(0, "#E4F0FF", 0.85), (0.5, "#9CC3F8", 0.45), (1, "#8FB8F5", 0.0)], x0, y0, x0 + 360 * math.cos(math.radians(28)), y0 - 360 * math.sin(math.radians(28)), "userSpaceOnUse")
           + S.gradient("a6x", [(0, "#DCEBFF", 0.42), (1, "#8FB8F5", 0.0)], x0, y0, x0 + 330 * math.cos(math.radians(28)), y0 - 330 * math.sin(math.radians(28)), "userSpaceOnUse") + "</defs>"]
    for centre, half, fill, ln in ((28.0, 7.0, "a6w", 380), (11.0, 6.0, "a6x", 330), (45.0, 6.0, "a6x", 330)):
        a1, a2 = math.radians(centre - half), math.radians(centre + half)
        p1 = (x0 + ln * math.cos(a1), y0 - ln * math.sin(a1))
        p2 = (x0 + ln * math.cos(a2), y0 - ln * math.sin(a2))
        out.append(f'<polygon points="{S.pts([(x0, y0), p1, p2])}" fill="url(#{fill})"/>')
    return "".join(out)


def radar_station():
    base = gy(70)
    out = ['<defs>' + S.gradient("a6t", [(0, "#FFFFFF"), (0.55, "#E2E8F1"), (1, "#9AA6BA")], 0, 0, 1, 0)
           + S.gradient("a6c", [(0, "#FFFFFF"), (1, "#C9D2E0")], 0, 0, 0, 1)
           + S.gradient("a6d", [(0, "#5E93F0"), (0.5, "#2D62C8"), (1, "#173F92")], 0, 0, 1, 1)
           + S.gradient("a6i", [(0, "#9CC0F8"), (1, "#3A70D6")], 0, 0, 0, 1)
           + S.gradient("a6o", [(0, "#FFC36B"), (0.5, "#F08A24"), (1, "#C15E0E")], 0, 0, 0, 1)
           + '<filter id="a6b" x="-30%" y="-30%" width="170%" height="170%"><feGaussianBlur stdDeviation="2.0"/></filter></defs>']
    # shadow on the ground, the cabin, the tower
    out.append(f'<ellipse cx="{S.n(86)}" cy="{S.n(base + 1.5)}" rx="44" ry="4.5" fill="#3A2E1E" opacity="0.30" filter="url(#a6b)"/>')
    out.append(f'<rect x="44" y="{S.n(base - 14)}" width="52" height="14" rx="1.5" fill="url(#a6c)" stroke="#9AA6BA" stroke-width="0.7"/>'
               f'<rect x="43" y="{S.n(base - 16.5)}" width="54" height="3.4" rx="1.2" fill="#F7F9FC" stroke="#9AA6BA" stroke-width="0.6"/>'
               f'<rect x="80" y="{S.n(base - 9.5)}" width="7" height="9.5" fill="#6F7F9A"/><rect x="50" y="{S.n(base - 10)}" width="9" height="4.6" fill="#7E9CC4"/><rect x="62" y="{S.n(base - 10)}" width="9" height="4.6" fill="#7E9CC4"/>')
    out.append(f'<polygon points="{S.pts([(62.5, base - 16), (77.5, base - 16), (73.2, 264), (66.8, 264)])}" fill="url(#a6t)" stroke="#8D9AB0" stroke-width="0.7"/>')
    for yy in (base - 32, base - 50, base - 66):
        if yy > 266:
            out.append(f'<line x1="{S.n(63.2 + (base - 16 - yy) * 0.04)}" y1="{S.n(yy)}" x2="{S.n(76.8 - (base - 16 - yy) * 0.04)}" y2="{S.n(yy)}" stroke="#C94A3C" stroke-width="2.2"/>')
    out.append('<rect x="62" y="258" width="16" height="7" rx="2" fill="#56627A" stroke="#3A4458" stroke-width="0.6"/>')
    # the feed arm, the dish (a bowl open at the top), the secondary antenna on top
    out.append('<line x1="70" y1="258" x2="70" y2="224" stroke="#3A4458" stroke-width="2.6" stroke-linecap="round"/>')
    out.append('<path d="M36,230 Q70,268 104,230 L100,242 Q70,276 40,242 Z" fill="url(#a6d)" stroke="#173F92" stroke-width="0.8" stroke-linejoin="round"/>'
               '<ellipse cx="70" cy="230" rx="34" ry="6.6" fill="url(#a6i)" stroke="#E6F0FF" stroke-width="1.1"/>'
               '<ellipse cx="70" cy="231.4" rx="25" ry="4" fill="#2B5CC0" opacity="0.5"/>'
               '<path d="M42,238 Q70,262 98,238" fill="none" stroke="#FFFFFF" stroke-opacity="0.35" stroke-width="1" stroke-linecap="round"/>')
    out.append('<ellipse cx="70" cy="226.6" rx="3.2" ry="1.8" fill="#2A3548"/>')
    out.append('<rect x="38" y="217.4" width="64" height="8.6" rx="2.2" fill="#1C2433" opacity="0.22" filter="url(#a6b)"/>'
               '<rect x="38" y="214" width="64" height="8.4" rx="2.2" fill="url(#a6o)" stroke="#8F470A" stroke-width="0.7"/>'
               '<rect x="40" y="215" width="60" height="1.8" rx="0.9" fill="#FFE9BC" opacity="0.85"/>')
    for i in range(9):
        out.append(f'<line x1="{S.n(44 + i * 6.5)}" y1="218.2" x2="{S.n(44 + i * 6.5)}" y2="221.8" stroke="#7A3A06" stroke-opacity="0.6" stroke-width="0.8"/>')
    return "".join(out)


def adsb_station():
    base = gy(560)
    out = ['<defs>' + S.gradient("a6p", [(0, "#EEF2F8"), (0.5, "#FFFFFF"), (1, "#9AA6BA")], 0, 0, 1, 0) + S.gradient("a6q", [(0, "#4B5970"), (1, "#222B3D")], 0, 0, 1, 0) + '</defs>']
    out.append(f'<ellipse cx="566" cy="{S.n(base + 1.5)}" rx="20" ry="3.4" fill="#3A2E1E" opacity="0.30" filter="url(#a6b)"/>')
    out.append(f'<line x1="548" y1="{S.n(base)}" x2="559" y2="272" stroke="#3A4458" stroke-width="2" stroke-linecap="round"/><line x1="572" y1="{S.n(base)}" x2="561" y2="272" stroke="#2B3447" stroke-width="2" stroke-linecap="round"/>'
               f'<rect x="558.6" y="236" width="2.8" height="{S.n(base - 236)}" fill="url(#a6q)"/><line x1="560" y1="{S.n(base)}" x2="560" y2="272" stroke="#3A4458" stroke-width="0.0"/>')
    out.append('<rect x="555.2" y="217" width="9.6" height="21" rx="2.4" fill="url(#a6p)" stroke="#8D9AB0" stroke-width="0.8"/><path d="M555.2,219.4 A4.8,3.6 0 0 1 564.8,219.4" fill="#2D62C8" stroke="#173F92" stroke-width="0.7"/>'
               '<rect x="556.4" y="222" width="3" height="11" rx="1.2" fill="#FFFFFF" opacity="0.7"/>')
    return "".join(out)


def scope():
    x, y, w, h = 24, 320, 176, 74
    out = [H.glass("a6s", x, y, w, h, r=7, top="#1D2A44", bottom="#0C1424", opacity=1.0)]
    cx, cy = 72, 357
    out.append(f'<defs><radialGradient id="a6r"><stop offset="0" stop-color="#274C86" stop-opacity="0.7"/><stop offset="1" stop-color="#0F1D38" stop-opacity="0.9"/></radialGradient>'
               f'{S.gradient("a6sw", [(0, "#7FB8FF", 0.0), (1, "#7FB8FF", 0.55)], cx, cy, cx + 30, cy - 18, "userSpaceOnUse")}</defs>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="34" fill="url(#a6r)" stroke="#7FA6DC" stroke-opacity="0.65" stroke-width="1"/>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="17" fill="none" stroke="#7FA6DC" stroke-opacity="0.55" stroke-width="0.9"/>')
    out.append(f'<line x1="{cx - 34}" y1="{cy}" x2="{cx + 34}" y2="{cy}" stroke="#7FA6DC" stroke-opacity="0.22" stroke-width="0.6"/><line x1="{cx}" y1="{cy - 34}" x2="{cx}" y2="{cy + 34}" stroke="#7FA6DC" stroke-opacity="0.22" stroke-width="0.6"/>')
    # the sweep trailing behind the primary target
    out.append(f'<polygon points="{cx},{cy} {S.n(cx + 31 * math.cos(math.radians(20)))},{S.n(cy - 31 * math.sin(math.radians(20)))} {S.n(cx + 31 * math.cos(math.radians(58)))},{S.n(cy - 31 * math.sin(math.radians(58)))}" fill="#7FB8FF" opacity="0.22"/>')
    out.append(f'<line x1="{cx}" y1="{cy}" x2="{S.n(cx + 31 * math.cos(math.radians(58)))}" y2="{S.n(cy - 31 * math.sin(math.radians(58)))}" stroke="#BEDBFF" stroke-opacity="0.8" stroke-width="1"/>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="2" fill="#FFFFFF"/>')
    out.append('<defs><filter id="a6bl" x="-200%" y="-200%" width="500%" height="500%"><feGaussianBlur stdDeviation="2"/></filter></defs>'
               '<circle cx="92" cy="338" r="4.2" fill="#BEDBFF" filter="url(#a6bl)"/><circle cx="92" cy="338" r="3.2" fill="#FFFFFF"/>'
               '<rect x="125" y="361" width="12" height="12" fill="#BEDBFF" opacity="0.7" filter="url(#a6bl)"/><rect x="128" y="364" width="7" height="7" fill="#FFFFFF"/>'
               '<line x1="135" y1="364" x2="141" y2="358" stroke="#FFFFFF" stroke-width="1"/>')
    out.append(H.text(143, 348, "4521", 12, "#FFFFFF", "normal", "start", mono=True) + H.text(143, 361, "045", 11, "#FFFFFF", "normal", "start", mono=True))
    return "".join(out)


def plate():
    ground, _ = H.planet("a6g", 0, 640, APEX, 400, RADIUS, seed=6)
    # the shadow behind the high ground: from the summit along the grazing line to the ground
    far_top = (440, 254 + 0.16 * 190)
    shadow_pts = [(250, 254), far_top] + [(x, gy(x)) for x in range(440, 289, -10)]
    shadow = (f'<defs>{S.gradient("a6sh", [(0, "#1B2B4A", 0.46), (0.6, "#1B2B4A", 0.22), (1, "#1B2B4A", 0.0)], 250, 0, 440, 0, "userSpaceOnUse")}</defs>'
              f'<polygon points="{S.pts(shadow_pts)}" fill="url(#a6sh)"/>'
              f'<line x1="250" y1="254" x2="{far_top[0]}" y2="{S.n(far_top[1])}" stroke="#FFFFFF" stroke-opacity="0.6" stroke-width="1" stroke-dasharray="3 3"/>')
    outline = S.jag([(204, gy(204) + 3), (214, 285), (225, 272), (238, 262), (250, 254), (259, 264), (268, 275), (279, 286), (298, gy(298) + 3)], 1.1, 4, 3)
    rock = S.rock("a6m", outline, 304, 204, 298, 6, tones=("#D6C29B", "#9A825E"), spine=[(250, 254), (248, 275), (253, 296), (255, 306)])
    # the signals: primary (blue) and secondary (orange), out and back
    blue_out = H.ribbon("a6bo", [(100, 226), (284, 128)], width=3.6, colours=H.BLUE, head=2.3, casing=1.6)
    blue_back = H.dashed_arrow([(296, 138), (109, 238.5)], "#1D4ED8", 1.7, "1.6 3.6", 6.0, casing=1.4)
    orange_out = H.ribbon("a6oo", [(98, 211), (288, 110)], width=3.6, colours=H.AMBER, head=2.3, casing=1.6)
    orange_back = H.dashed_arrow([(300, 98), (107.8, 196)], "#C2610E", 2.3, "8 4.5", 7.0, casing=1.5)
    # the reply on its tag, with a leader to the aeroplane
    tag = (H.glass("a6tg", 298, 46, 64, 40, r=5, top="#2F3F5E", bottom="#121C32")
           + '<rect x="298.7" y="46.7" width="62.6" height="38.6" rx="4.4" fill="none" stroke="#F4A340" stroke-width="1.4"/>'
           + H.text(330, 63, "4521", 14, "#FFFFFF", "bold", "middle", mono=True) + H.text(330, 79, "045", 13, "#FFD79A", "normal", "middle", mono=True)
           + '<line x1="330" y1="87" x2="330" y2="104" stroke="#FFFFFF" stroke-width="1.2" stroke-opacity="0.9"/>')
    # ADS-B: three arcs of broadcast round the aeroplane's antenna, and two dotted arrows
    arcs = "".join(f'<path d="M {S.n(336 + r)},{S.n(128.4)} A {r},{r} 0 0 1 {S.n(336 + r * math.cos(math.radians(43)))},{S.n(128.4 + r * math.sin(math.radians(43)))}" fill="none" stroke="#FFFFFF" stroke-opacity="0.8" stroke-width="4.4" stroke-linecap="round"/>'
                   f'<path d="M {S.n(336 + r)},{S.n(128.4)} A {r},{r} 0 0 1 {S.n(336 + r * math.cos(math.radians(43)))},{S.n(128.4 + r * math.sin(math.radians(43)))}" fill="none" stroke="#0B8A66" stroke-width="2.4" stroke-linecap="round"/>' for r in (16, 28, 40))
    g1 = H.dashed_arrow([(384, 151), (540.6, 216.9)], "#0B8A66", 2.6, "0.1 5.2", 7.0, casing=1.3)
    g2 = H.dashed_arrow([(372, 110), (522.2, 77.7)], "#0B8A66", 2.6, "0.1 5.2", 7.0, casing=1.3)
    layers = [
        S.sky("a6k", 0, 0, 640, 400, SKY),
        S.glow("a6u", 40, 10, 230, "#FFF2CC", 0.55),
        {"name": "cloud-cirrus", "at": [520, 36], "width": 300, "opacity": 0.5, "haze": {"colour": "#9CC0EA", "amount": 0.25}, "feather": {"x": 0.12, "y": 0.12}},
        beam_wedge(),
        rock,
        ground,
        shadow,
        radar_station(),
        adsb_station(),
        scope(),
        blue_out, blue_back, orange_out, orange_back,
        H.plane(326, 119, 68, 0, name="sprite-side"),
        tag, arcs, g1, g2,
        H.plane(566, 70, 62, 0, name="sprite-side"),
    ]
    c = S.callout
    layers.append("".join([
        c(1, 192, 236, 184, 203), c(2, 150, 140, 168, 165), c(3, 386, 66, 364, 66), c(4, 270, 236, 252, 260),
        c(5, 598, 236, 568, 238), c(6, 122, 330, 94, 340), c(7, 222, 354, 176, 352),
    ]))
    return {
        "id": "fig-21-06-radar",
        "replaces": "fig-21-06-radar.svg",
        "book_file": "plate-21-06-radar.jpg",
        "caption": "Figure 21-6. Primary radar, secondary radar and ADS-B",
        "desc": "Figure 21-6. Primary radar, secondary radar and ADS-B",
        "legend": [
            "Primary radar: a pulse out and a faint echo back, transponder or not.",
            "Secondary radar: interrogation and reply.",
            "The reply: the code, here 4521, and the pressure altitude in hundreds of feet, here 045 for 4 500 ft.",
            "High ground hides aircraft behind it.",
            "ADS-B Out: the aircraft broadcasts its own position.",
            "On the display, a primary target: position only.",
            "A secondary target with its label: code and altitude.",
        ],
        "canvas": [640, 400],
        "background": "pale",
        "reskin": {"svg": "fig-21-06-radar.svg", "blank": True, "layers": layers},
    }
