"""Figure 18-4. Taxiway markings, the runway-holding position and the four kinds of sign. An aerial picture on the desert plain (figs/terrain.py): a runway, the taxiway that
leaves it with its yellow centreline curving on to the runway centreline, the runway-holding position marking, the intermediate holding position, the aeroplane of the model on the
centreline and the signs standing beside the taxiway, with the four kinds of sign shown large on a card at the right: solid boards on posts, lit, with a shadow. The nine callouts of
the old figure are kept, in the same order and meaning (figs/scene.py makes the callouts, figs/h_a2.py the asphalt, the paint and the signs)."""
from figs import h_a2 as H
from figs import scene as S
from figs import terrain

W, HT = 640, 400
terrain.ensure("terrain-18-04", size=(W * 4, HT * 4), seed=184, kind="plain", features=("wadis", "tracks"), veil=0.34, soft=2.8)

U = "a184"
PAINT = "#F6F3EA"
YEL = "#F2BE1A"
R = 9.0


def defs():
    return ("<defs>" + H.asphalt_filter(U + "as", seed=6, relief=0.9, tone=0.0) + H.asphalt_filter(U + "at", seed=16, relief=0.8, tone=0.35)
            + H.paint_filter(U + "pw", seed=12, wear=0.35, thickness=0.5) + H.paint_filter(U + "py", seed=22, wear=0.3, thickness=0.5)
            + H.blur_filter(U + "bl", 1.4) + H.blur_filter(U + "bs", 0.8) + H.blur_filter(U + "bc", 3.0) + "</defs>")


def pavement():
    r = R
    d = (f"M 0,18 L 400,18 L 400,98 L {215 + r},98 A {r},{r} 0 0 0 215,{98 + r} L 215,{296 - r} A {r},{r} 0 0 0 {215 + r},296 L 400,296 L 400,338 L {215 + r},338 "
         f"A {r},{r} 0 0 0 215,{338 + r} L 215,400 L 165,400 L 165,{338 + r} A {r},{r} 0 0 0 {165 - r},338 L 0,338 L 0,296 L {165 - r},296 A {r},{r} 0 0 0 165,{296 - r} "
         f"L 165,{98 + r} A {r},{r} 0 0 0 {165 - r},98 L 0,98 Z")
    out = [f'<path d="{d}" fill="#C2B089" fill-opacity="0.5" stroke="#C2B089" stroke-opacity="0.5" stroke-width="9" stroke-linejoin="round" filter="url(#{U}bl)"/>',
           f'<path d="{d}" fill="#444" filter="url(#{U}at)"/>',
           f'<rect x="0" y="18" width="400" height="80" fill="#444" filter="url(#{U}as)"/>',
           f'<path d="{d}" fill="none" stroke="#10151D" stroke-opacity="0.4" stroke-width="0.5"/>']
    # rubber and a few cracks on the runway, a patched joint on the taxiway
    out.append(f'<rect x="20" y="40" width="300" height="5" rx="2.5" fill="#0A0E15" opacity="0.10" filter="url(#{U}bl)"/><rect x="20" y="70" width="300" height="5" rx="2.5" fill="#0A0E15" opacity="0.10" filter="url(#{U}bl)"/>')
    out.append(f'<polyline points="60,100 63,112 59,124 64,136" fill="none" stroke="#0A0D13" stroke-opacity="0.3" stroke-width="0.45"/>'
               f'<polyline points="196,18 193,30 198,42 195,54" fill="none" stroke="#0A0D13" stroke-opacity="0.3" stroke-width="0.45"/>'
               f'<polyline points="170,230 176,236 184,234 194,240" fill="none" stroke="#0A0D13" stroke-opacity="0.3" stroke-width="0.45"/>')
    return "".join(out)


def markings():
    out = []
    # the runway: side stripes and a centreline of dashes
    white = ['<rect x="0" y="20.5" width="400" height="3"/><rect x="0" y="92.5" width="400" height="3"/>']
    white.append("".join(f'<rect x="{x}" y="56" width="{min(26, 400 - x)}" height="4"/>' for x in range(10, 400, 46)))
    out.append(f'<g fill="{PAINT}" filter="url(#{U}pw)">{"".join(white)}</g>')
    # the taxiway centreline, curving on to the runway centreline; the centreline of the crossing taxiway; the holding positions
    yel = [f'<path d="M 190,400 V120 Q 190,58 252,58" fill="none" stroke-width="2.6" stroke-linecap="butt"/>', '<line x1="0" y1="317" x2="400" y2="317" stroke-width="2.6"/>']
    yel.append('<line x1="165" y1="150" x2="215" y2="150" stroke-width="2.4"/><line x1="165" y1="145" x2="215" y2="145" stroke-width="2.4"/>')
    yel.append('<line x1="165" y1="137" x2="215" y2="137" stroke-width="2.4" stroke-dasharray="5 4"/><line x1="165" y1="132" x2="215" y2="132" stroke-width="2.4" stroke-dasharray="5 4"/>')
    yel.append('<line x1="165" y1="354" x2="215" y2="354" stroke-width="2.6" stroke-dasharray="7 5"/>')
    out.append(f'<g stroke="{YEL}" fill="none" filter="url(#{U}py)">{"".join(yel)}</g>')
    return "".join(out)


def signs_left():
    out = []
    out.append(H.sign(U + "sb", 84, 182, "B", w=24, h=26, post=10, kind="location", glow=0.25))
    out.append(H.sign(U + "sr", 128, 182, "09–27", w=60, h=26, post=10, kind="mandatory", glow=0.3))
    out.append(H.sign(U + "sl", 60, 392, "A", w=48, h=24, post=8, kind="direction", arrow=-1, glow=0.25))
    out.append(H.sign(U + "sm", 98, 392, "B", w=24, h=24, post=8, kind="location", glow=0.25, shadow=False))
    out.append(H.sign(U + "sn", 136, 392, "A", w=48, h=24, post=8, kind="direction", arrow=1, glow=0.25, shadow=False))
    return "".join(out)


def card():
    x, y, w, h = 418, 20, 210, 364
    out = [f'<defs><clipPath id="{U}cc"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10"/></clipPath>{H.shadow_filter(U + "cs", 0, 2.2, 3.2, 0.30, "#10233F")}'
           f'<linearGradient id="{U}cg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FBF8F0" stop-opacity="0.80"/><stop offset="1" stop-color="#EFE8D6" stop-opacity="0.70"/></linearGradient></defs>',
           f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="#FFFFFF" filter="url(#{U}cs)"/>',
           f'<g clip-path="url(#{U}cc)"><rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#E9DDBC"/>'
           f'<image x="0" y="0" width="{W}" height="{HT}" href="@@TERRAIN@@" opacity="0.0"/><rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#{U}cg)"/></g>',
           f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="none" stroke="#FFFFFF" stroke-width="1.6"/>']
    # ground under each sign: a soft contact shadow and a low kerb strip
    for foot, cx, rx in ((106, 515, 64), (192, 483, 36), (278, 515, 64), (364, 515, 64)):
        out.append(f'<ellipse cx="{cx}" cy="{foot + 1.5}" rx="{rx}" ry="5.5" fill="#B9A67A" opacity="0.55" filter="url(#{U}bc)"/>'
                   f'<ellipse cx="{cx + 2}" cy="{foot + 2.6}" rx="{rx * 0.8}" ry="2.6" fill="{H.SHADOW}" opacity="0.30" filter="url(#{U}bc)"/>')
    return "".join(out)


def signs_card():
    out = []
    out.append(H.sign(U + "c1", 515, 106, "09–27", w=110, h=40, post=14, kind="mandatory", glow=0.45, cap=17, shadow=0.55))
    out.append(H.sign(U + "c2", 483, 192, "B", w=46, h=40, post=14, kind="location", glow=0.40, cap=20, shadow=0.55))
    out.append(H.sign(U + "c3", 515, 278, "A", w=110, h=40, post=14, kind="direction", arrow=-1, glow=0.45, cap=17, shadow=0.55))
    out.append(H.sign(U + "c4", 515, 364, "09", w=110, h=40, post=14, kind="destination", arrow=1, glow=0.45, cap=17, shadow=0.55))
    return "".join(out)


def callouts():
    c = S.callout
    return "".join([
        c(1, 244, 141, 209, 141), c(2, 116, 118, 116, 149), c(3, 242, 232, 192, 247), c(4, 244, 354, 214, 354), c(5, 18, 372, 38, 372),
        c(6, 436, 72, 462, 72), c(7, 436, 158, 462, 158), c(8, 436, 244, 462, 244), c(9, 436, 330, 462, 330)])


def aeroplane():
    return {"name": "sprite-top", "at": [190, 190], "width": 40, "angle": 0, "tint": "#2F66D6", "tint_strength": 0.62, "shadow": {"dx": 1.6, "dy": 2.6, "blur": 1.8, "opacity": 0.34}}


def scenery():
    return S.scrub(41, 230, 400, 104, 290, 6, scale=0.85) + S.scrub(42, 6, 160, 178, 290, 4, scale=0.85) + S.scrub(43, 220, 400, 344, 394, 3, scale=0.85) + S.scrub(44, 6, 80, 340, 356, 1, scale=0.8)


def layers():
    return [{"name": "terrain-18-04", "at": [W / 2, HT / 2], "width": W}, defs(), scenery(), pavement(), markings(), aeroplane(), signs_left(), card().replace('<image x="0" y="0" width="640" height="400" href="@@TERRAIN@@" opacity="0.0"/>', ""), signs_card(), callouts()]


def plate():
    return {
        "id": "fig-18-04-taxiway-signs",
        "replaces": "fig-18-04-taxiway-signs.svg",
        "book_file": "plate-18-04-taxiway-signs.jpg",
        "caption": "Figure 18-4. Taxiway markings, the runway-holding position and the four kinds of sign",
        "desc": "Figure 18-4. Taxiway markings, the runway-holding position and the four kinds of sign",
        "legend": [
            "Runway-holding position marking: solid lines on your side, dashed lines on the runway side.",
            "Runway-holding position sign `09-27`, with the location sign `B` outboard of it.",
            "Taxiway centreline, curving on to the runway centreline.",
            "Intermediate holding position before taxiway `A`.",
            "Direction signs either side of the location sign `B`: taxiway `A` goes both left and right.",
            "Mandatory instruction sign.",
            "Location sign.",
            "Direction sign.",
            "Destination sign: this way to runway 09.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"svg": "fig-18-04-taxiway-signs.svg", "blank": True, "layers": layers()},
    }
