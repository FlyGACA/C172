"""Old figures of the handbook given the aeroplane of the model. A plate with a "reskin" key keeps the diagram of the figure it replaces (the SVG
in old/, the drawing the book had) and swaps its flat aeroplane symbols for pictures of the model (figs/sprites.py), in the same place, heading and
size (a little larger, so the picture can be read), tinted where the symbol was coloured; the fonts are the book's (Inter, JetBrains Mono).

    "reskin": {"svg": "fig-18-06-circuit.svg", "grow": 1.7, "grow_side": 1.4, "remove": [regex, ...],
               "drop": [[from text, up to text]], "sprites": [sprite overlays with "at"], "markup": "svg markup"}  (the last three: a stretch of the old drawing replaced)

build_plates.py writes the result to cache/flat-src/<id>.svg like any plate; rasterize.mjs and book_plates.py do the rest."""
import math
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))

# the first generation of the book's aeroplane symbols
TOP = re.compile(r'<g transform="rotate\((-?[\d.]+) (-?[\d.]+) (-?[\d.]+)\)">((?:<polygon[^>]*/>){3})</g>')
SIDE = re.compile(r'((?:<path d="M[^"]+Z" fill="#[0-9a-fA-F]{6}"/>){3}<line [^>]*/><circle [^>]*/>)')

# the same symbol drawn turned (its points worked out, no group): the fuselage (7 to 9 points), the wing and the tailplane (4 points each), one colour
POLY = r'<polygon points="([^"]+)" fill="(#[0-9a-fA-F]{6})"/>'
TURNED = re.compile(POLY + POLY + POLY)

# the second drawing of the same symbol: one outline path (wingspan 36.4, nose toward -y) with the place, heading and size in its transform
SILHOUETTE = re.compile(r'<path d="M17\.7 -6\.6[^"]*"([^>]*)/>')

# a large version in a group (nose toward +x, wingspan 80), used by the compass figure
BIG = re.compile(r'<g transform="translate\(([-\d.]+),([-\d.]+)\) rotate\(([-\d.]+)\)">\s*<polygon points="-36,-4 26,-4 38,0 26,4 -36,4" fill="(#[0-9a-fA-F]{6})"/>.*?</g>', re.S)

# the same, from the side (nose toward +x, wheels on y = 0), inside a group that puts it in place: the picture goes in the group, whatever else is in it stays
SIDE_SILHOUETTE = re.compile(r'<path d="(M-30\.2 -17\.7[^"]*)"([^>]*)/>(?:<line x1="1\.2" y1="-13\.3" x2="[-\d.]+" y2="[-\d.]+"[^>]*/>)?')       # (and its blue flap mark, which the picture shows itself)

# a line-drawn side view (fuselage outline, wing and gear lines, two wheels, a strut) in whatever attitude: the stall sequences
LINE_SIDE = re.compile(r'<path d="(M [^"]+)" fill="#e8eefc" stroke="#1f2937" stroke-width="1\.4"/>\s*(?:<line[^>]*/>\s*){1,2}'
                       r'<circle cx="([-\d.]+)" cy="([-\d.]+)" r="3"[^>]*/>\s*<circle cx="([-\d.]+)" cy="([-\d.]+)" r="3"[^>]*/>\s*<line[^>]*/>')

DARK = "#1f2937"
LOOK = {"outline": {"width": 0.5, "colour": "#2B3648", "opacity": 0.9}, "shadow": {"dx": 1.2, "dy": 2.0, "blur": 1.5, "opacity": 0.26}}


def look(fill, cfg=None):
    """The sprite's tint for the colour of the symbol it replaces: a dark or grey symbol is an ordinary aeroplane, a coloured one an aeroplane in colour."""
    r, g, b = (int(fill.lstrip("#")[i:i + 2], 16) / 255.0 for i in (0, 2, 4))
    top, bottom = max(r, g, b), min(r, g, b)
    saturation = 0.0 if top == 0 else (top - bottom) / top
    result = dict(LOOK) if saturation < 0.3 or top < 0.4 else {**LOOK, "tint": fill, "tint_strength": 0.62}      # (a very dark colour is a dark grey, not a hue)
    if cfg and cfg.get("outline") is False:                                                                       # on a dark ground an outline would only be noise
        result.pop("outline", None)
    return result


def reskin(plate, sprite_markup, sprite_aspect):
    cfg = plate["reskin"]
    with open(os.path.join(HERE, "old", cfg["svg"]), encoding="utf-8") as f:
        svg = f.read()
    for pattern in cfg.get("remove", []):
        svg = re.sub(pattern, "", svg, flags=re.S)
    for old, new in cfg.get("replace", []):                  # a few words of the old drawing changed (a colour, a ground)
        if old not in svg:
            raise ValueError(f"{plate['id']}: {old[:60]!r} is not in the old drawing")
        svg = svg.replace(old, new)
    for spec in cfg.get("drop", []):                         # a stretch of the old drawing taken out (from the first text up to the second) and the new things put there
        start, end = spec[0], spec[1]
        a = svg.index(start)
        b = svg.index(end, a)
        extra = spec[2] if len(spec) > 2 else None           # {"sprites": [...], "markup": "..."} for this stretch alone; otherwise the figure's own, at the first
        piece = "".join(sprite_markup(o, o["at"][0], o["at"][1]) for o in extra.get("sprites", [])) + extra.get("markup", "") if extra else "@@INSERT@@"
        svg = svg[:a] + piece + svg[b:]
    insert = "".join(sprite_markup(o, o["at"][0], o["at"][1]) for o in cfg.get("sprites", [])) + cfg.get("markup", "")
    if "@@INSERT@@" in svg:
        svg = svg.replace("@@INSERT@@", insert, 1)
    else:                                                    # (under everything else of the old drawing, as its own symbols were: after the white ground)
        ground = re.search(r'<rect x="0" y="0" width="[\d.]+" height="[\d.]+" fill="#ffffff"/>', svg)
        svg = svg[:ground.end()] + insert + svg[ground.end():] if ground and insert else svg.replace("</svg>", insert + "</svg>", 1)

    def top(m):
        angle, cx, cy = float(m.group(1)), float(m.group(2)), float(m.group(3))
        fill = re.search(r'fill="(#[0-9a-fA-F]{6})"', m.group(4)).group(1)
        return sprite_markup({"name": cfg.get("sprite_top", "sprite-top"), "width": 24.0 * cfg.get("grow", 1.7), "angle": angle, **look(fill, cfg)}, cx, cy)

    def side(m):
        xs, ys = [], []
        for tag in re.findall(r"<(?:path|line|circle)[^>]*>", m.group(1)):
            if tag.startswith("<path"):
                for x, y in re.findall(r"(-?\d+\.?\d*),(-?\d+\.?\d*)", re.search(r'd="([^"]+)"', tag).group(1)):
                    xs.append(float(x)); ys.append(float(y))
            elif tag.startswith("<line"):
                v = {k: float(x) for k, x in re.findall(r'(x1|y1|x2|y2)="(-?[\d.]+)"', tag)}
                xs += [v["x1"], v["x2"]]; ys += [v["y1"], v["y2"]]
            else:
                v = {k: float(x) for k, x in re.findall(r'\b(cx|cy|r)="(-?[\d.]+)"', tag)}
                xs += [v["cx"] - v["r"], v["cx"] + v["r"]]; ys += [v["cy"] - v["r"], v["cy"] + v["r"]]
        fill = re.search(r'fill="(#[0-9a-fA-F]{6})"', m.group(1)).group(1)
        return sprite_markup({"name": "sprite-side", "width": (max(xs) - min(xs)) * cfg.get("grow_side", 1.4), **look(fill, cfg)}, (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2)

    def turned(m):
        shapes = [[tuple(float(v) for v in pt.split(",")) for pt in m.group(i).split()] for i in (1, 3, 5)]
        fills = {m.group(2).lower(), m.group(4).lower(), m.group(6).lower()}
        if len(fills) != 1 or not (7 <= len(shapes[0]) <= 10 and len(shapes[1]) == 4 and len(shapes[2]) == 4):
            return m.group(0)
        mid = lambda pts: (sum(x for x, _ in pts) / len(pts), sum(y for _, y in pts) / len(pts))
        wing, tail = mid(shapes[1]), mid(shapes[2])
        side = max(math.hypot(shapes[1][i][0] - shapes[1][(i + 1) % 4][0], shapes[1][i][1] - shapes[1][(i + 1) % 4][1]) for i in range(4))
        if not (18.0 <= side <= 40.0):
            return m.group(0)
        heading = math.degrees(math.atan2(wing[0] - tail[0], -(wing[1] - tail[1])))
        every = [pt for shape in shapes for pt in shape]
        cx, cy = (min(x for x, _ in every) + max(x for x, _ in every)) / 2, (min(y for _, y in every) + max(y for _, y in every)) / 2
        return sprite_markup({"name": cfg.get("sprite_top", "sprite-top"), "width": side * cfg.get("grow", 1.7), "angle": heading, **look(fills.pop(), cfg)}, cx, cy)

    def silhouette(m):
        attrs = m.group(1)
        t = re.search(r'transform="translate\(([-\d.]+)[ ,]+([-\d.]+)\)(?: rotate\(([-\d.]+)\))?(?: scale\(([-\d.]+)\))?"', attrs)
        if not t:
            return m.group(0)
        tx, ty, a, k = float(t.group(1)), float(t.group(2)), float(t.group(3) or 0), float(t.group(4) or 1)
        fill = (re.search(r'fill="(#[0-9a-fA-F]{6})"', attrs) or re.search(r"(#1f2937)", DARK)).group(1)
        opacity = re.search(r'\bopacity="([\d.]+)"', attrs)
        rad = math.radians(a)
        cx, cy = tx - 1.6 * k * math.sin(rad), ty + 1.6 * k * math.cos(rad)             # the middle of the outline is 1.6 behind its origin
        o = {"name": cfg.get("sprite_top", "sprite-top"), "width": 36.4 * k * cfg.get("grow_silhouette", 1.15), "angle": a, **look(fill, cfg)}
        if opacity:
            o["opacity"] = float(opacity.group(1))
        return sprite_markup(o, cx, cy)

    def big(m):
        o = {"name": cfg.get("sprite_top", "sprite-top"), "width": 80.0 * cfg.get("grow_big", 1.0), "angle": float(m.group(3)) + 90.0, **look(m.group(4), cfg)}
        return sprite_markup(o, float(m.group(1)), float(m.group(2)))

    svg = BIG.sub(big, svg)
    def side_silhouette(m):
        nums = [float(v) for v in re.findall(r"-?\d+\.?\d*", m.group(1))]
        xs, ys = nums[0::2], nums[1::2]
        fill = (re.search(r'fill="(#[0-9a-fA-F]{6})"', m.group(2)) or re.search(r"(#1f2937)", DARK)).group(1)
        width = (max(xs) - min(xs)) * cfg.get("grow_side_silhouette", 1.12)
        # the picture's wheels stand on the symbol's lowest line, its middle on the symbol's middle
        o = {"name": "sprite-side", "width": width, "px": 7.0, **look(fill, cfg)}
        h_units = width * sprite_aspect("sprite-side")
        return sprite_markup(o, (min(xs) + max(xs)) / 2, max(ys) - h_units / 2 + 0.6)

    def line_side(m):
        nums = [float(v) for v in re.findall(r"-?\d+\.?\d*", m.group(1))]
        xs, ys = nums[0::2], nums[1::2]
        x1, y1, x2, y2 = (float(m.group(i)) for i in (2, 3, 4, 5))
        pitch_down = math.degrees(math.atan2(y2 - y1, x2 - x1))                         # the line through the wheels, nose wheel on the right
        left, right = min(xs), max(xs)
        top, bottom = min(ys), max(y2, y1) + 3
        return sprite_markup({"name": "sprite-side", "width": (right - left) * cfg.get("grow_line_side", 1.18), "angle": pitch_down, **look(DARK, cfg)},
                             (left + right) / 2 + 2, (top + bottom) / 2)

    svg = LINE_SIDE.sub(line_side, svg)
    svg = SIDE_SILHOUETTE.sub(side_silhouette, svg)
    svg = SILHOUETTE.sub(silhouette, svg)
    svg = TOP.sub(top, svg)
    svg = TURNED.sub(turned, svg)
    svg = SIDE.sub(side, svg)
    svg = svg.replace('font-family="sans-serif"', 'font-family="Inter, sans-serif"').replace('font-family="monospace"', 'font-family="JetBrains Mono, monospace"')
    root = re.search(r"<svg[^>]*>", svg).group(0)
    new_root = root.replace("<svg ", '<svg xmlns:xlink="http://www.w3.org/1999/xlink" data-px-per-unit="3" ', 1) if "data-px-per-unit" not in root else root
    return svg.replace(root, new_root, 1)
