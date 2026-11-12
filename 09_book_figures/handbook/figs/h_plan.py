"""Plan views laid on the ground: what the figures of manoeuvres and patterns seen from above share. `layer(cfg, name, ...)` takes a figure's "reskin" configuration (the old drawing and what
the figure already changes in it) and adds to it an aerial picture of the country under the diagram (figs/terrain.py), solid stand-ins for the flat grey and tinted shapes of the old
drawing (asphalt with its shoulder and edge lines for the runways, a tarred road, a taxiway, a slab of concrete, a crop, a farm plot, gravel, a flat roof) and a white casing under its lines
and words (reskin.py "halo"). The old drawing is the spec: nothing of it is taken out except its flat fills."""
import os
import re

from figs import terrain

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# the flat colours of the old drawings, and what each one stands for in a plan view (a style of STYLES); a figure can say otherwise with `fills=`
DEFAULT_FILLS = {"#6b7280": "asphalt", "#d1d5db": "road", "#9ca3af": "taxi", "#e3f1ec": "crop", "#fdf0e1": "plot"}

STYLES = {"asphalt": "url(#hpAsphalt)", "road": "url(#hpRoad)", "taxi": "url(#hpTaxi)", "concrete": "url(#hpConcrete)", "crop": "url(#hpCrop)", "plot": "url(#hpPlot)",
          "gravel": "url(#hpGravel)", "grass": "url(#hpGrass)", "roof": "#E6DAC0"}


def defs():
    return ('<defs>'
            '<linearGradient id="hpAsphalt" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#5A6272"/><stop offset="0.5" stop-color="#4B5363"/><stop offset="1" stop-color="#3E4553"/></linearGradient>'
            '<linearGradient id="hpRoad" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#6A717D"/><stop offset="0.5" stop-color="#5B626E"/><stop offset="1" stop-color="#515866"/></linearGradient>'
            '<linearGradient id="hpTaxi" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#8A919E"/><stop offset="0.5" stop-color="#78808D"/><stop offset="1" stop-color="#6D7482"/></linearGradient>'
            '<pattern id="hpConcrete" width="46" height="46" patternUnits="userSpaceOnUse"><rect width="46" height="46" fill="#D2D5D8"/><rect x="0" y="0" width="23" height="46" fill="#CBCED2"/>'
            '<path d="M0 0.4H46M0.4 0V46" stroke="#AEB3BA" stroke-width="0.9" fill="none"/></pattern>'
            '<pattern id="hpCrop" width="5" height="5" patternUnits="userSpaceOnUse" patternTransform="rotate(18)"><rect width="5" height="5" fill="#6FA45B"/><rect width="5" height="2.2" fill="#5C9249"/></pattern>'
            '<pattern id="hpPlot" width="6.4" height="6.4" patternUnits="userSpaceOnUse" patternTransform="rotate(-12)"><rect width="6.4" height="6.4" fill="#BBA372"/><rect width="6.4" height="2.3" fill="#A58B5A"/><rect y="2.3" width="6.4" height="0.7" fill="#CDB888" fill-opacity="0.8"/></pattern>'
            '<pattern id="hpGravel" width="13" height="13" patternUnits="userSpaceOnUse"><rect width="13" height="13" fill="#D2BE98"/><circle cx="2.4" cy="3" r="0.9" fill="#B79E72"/>'
            '<circle cx="8.6" cy="2" r="0.7" fill="#E7D8B6"/><circle cx="5.4" cy="8.2" r="1.0" fill="#AD9466"/><circle cx="11" cy="10" r="0.7" fill="#E7D8B6"/><circle cx="1.6" cy="10.6" r="0.6" fill="#C2AA7D"/><circle cx="10.6" cy="5.4" r="0.6" fill="#BBA276"/></pattern>'
            '<pattern id="hpGrass" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(8)"><rect width="6" height="6" fill="#8DAA5B"/><rect width="6" height="2" fill="#7F9D50"/></pattern>'
            '</defs>')


def _num(tag, key):
    m = re.search(rf'\b{key}="(-?[\d.]+)"', tag)
    return float(m.group(1)) if m else None


def swaps(svg_text, fills=None):
    """[old tag, new text] for every rectangle of the old drawing that has one of the flat fills (only rectangles, so that the symbols of the aeroplanes, which are not rectangles, keep the
    colours that the re-skin reads their tints from). A runway or a road gets a pale shoulder under it and a thin edge line along each long side; a small grey square is a flat roof."""
    table = {k.lower(): v for k, v in (DEFAULT_FILLS if fills is None else {**DEFAULT_FILLS, **fills}).items()}
    out = {}
    for tag in re.findall(r"<rect\b[^>]*/>", svg_text):
        m = re.search(r'fill="(#[0-9a-fA-F]{6})"', tag)
        if not m or 'width="100%"' in tag:
            continue
        style = table.get(m.group(1).lower())
        if not style:
            continue
        x, y, w, h = _num(tag, "x") or 0.0, _num(tag, "y") or 0.0, _num(tag, "width"), _num(tag, "height")
        if w is None or h is None or (x == 0 and w >= 600):                              # the whole page: leave it
            continue
        if style == "asphalt" and max(w, h) < 40:
            style = "roof"
        new = tag.replace(f'fill="{m.group(1)}"', f'fill="{STYLES[style]}"', 1)
        if style in ("asphalt", "road", "taxi") and max(w, h) >= 90 and min(w, h) >= 5:
            pad = 3.4 if style == "asphalt" else 2.4
            shoulder = f'<rect x="{x - pad:g}" y="{y - pad:g}" width="{w + 2 * pad:g}" height="{h + 2 * pad:g}" fill="#B3A688" fill-opacity="0.55"/>'
            if w >= h:
                edge = "".join(f'<line x1="{x + 3:g}" y1="{yy:g}" x2="{x + w - 3:g}" y2="{yy:g}" stroke="#F4F1E6" stroke-opacity="0.8" stroke-width="0.8"/>' for yy in (y + 1.7, y + h - 1.7))
            else:
                edge = "".join(f'<line x1="{xx:g}" y1="{y + 3:g}" x2="{xx:g}" y2="{y + h - 3:g}" stroke="#F4F1E6" stroke-opacity="0.8" stroke-width="0.8"/>' for xx in (x + 1.7, x + w - 1.7))
            new = shoulder + new + edge
        elif style == "roof":
            new = f'<rect x="{x + 2.2:g}" y="{y + 2.2:g}" width="{w:g}" height="{h:g}" fill="#2B2A25" fill-opacity="0.32"/>' + new.replace("/>", ' stroke="#A69A7E" stroke-width="0.9"/>', 1)
        out[tag] = new
    return [[a, b] for a, b in out.items()]


def canvas_of(svg_file):
    with open(os.path.join(HERE, "old", svg_file), encoding="utf-8") as f:
        text = f.read()
    vb = re.search(r'viewBox="[-\d.]+ [-\d.]+ ([\d.]+) ([\d.]+)"', text)
    return float(vb.group(1)), float(vb.group(2)), text


def layer(cfg, name, seed=1, kind="plain", features=("scrub", "wadis", "tracks"), veil=0.28, soft=2.8, fills=None, flat_fills=True, extra_sprites=(), markup="", halo=True, ground=True, area=None, **terrain_kw):
    """The figure's reskin configuration with a terrain under it: `name` is the picture's name (renders/<name>.png, made now if it is not there), `kind`, `features`, `veil` and `soft` are
    figs/terrain.py's, `terrain_kw` its road=, village=, fields=. `fills` says what an old flat colour stands for in this figure ({"#6b7280": "roof"}; styles in STYLES, None leaves it).
    `extra_sprites` are laid over the ground and under the diagram, `markup` likewise (after the gradients). `ground=False` leaves the page without a terrain (the ground is `markup`);
    `area=(x0, y0, x1, y1)` lays the terrain on that part of the canvas only."""
    w, h, text = canvas_of(cfg["svg"])
    out = dict(cfg)
    sprites = list(cfg.get("sprites", []))
    if ground:
        x0, y0, x1, y1 = area or (0.0, 0.0, w, h)
        terrain.ensure(name, size=(int((x1 - x0) * 4), int((y1 - y0) * 4)), seed=seed, kind=kind, features=features, veil=veil, soft=soft, **terrain_kw)
        sprites = [{"name": name, "at": [(x0 + x1) / 2, (y0 + y1) / 2], "width": x1 - x0}, *extra_sprites, *sprites]
    else:
        sprites = [*extra_sprites, *sprites]
    out["sprites"] = sprites
    out["markup"] = defs() + markup + cfg.get("markup", "")
    gone = [re.compile(rx) for rx in cfg.get("remove", [])]                           # what the figure takes out is not given a new fill
    swapped = [pair for pair in (swaps(text, fills) if flat_fills else []) if not any(rx.search(pair[0]) for rx in gone)]
    out["replace"] = list(cfg.get("replace", [])) + swapped
    if halo:
        out["halo"] = halo
    return out


def panel(uid, x, y, w, h, sky=("#BFD9F2", "#E9F1F7", "#F6EFD9"), ground_y=None, ground=("#DCC99D", "#C2A870"), radius=14.0, border="#FFFFFF"):
    """A card with a sky in it, for the side view of a figure whose other half is a plan view: a vertical gradient, a strip of ground from `ground_y` to the foot of the card, a white
    border and a soft shadow. Returns markup to put under the diagram (`markup=`)."""
    stops = "".join(f'<stop offset="{o:g}" stop-color="{c}"/>' for o, c in zip((0.0, 0.62, 1.0), sky))
    gstops = f'<stop offset="0" stop-color="{ground[0]}"/><stop offset="1" stop-color="{ground[1]}"/>'
    g = ""
    if ground_y is not None:
        g = (f'<rect x="{x:g}" y="{ground_y:g}" width="{w:g}" height="{y + h - ground_y:g}" fill="url(#{uid}g)"/>'
             f'<rect x="{x:g}" y="{ground_y:g}" width="{w:g}" height="1.6" fill="#FFF6DA" fill-opacity="0.7"/>')
    return (f'<defs><linearGradient id="{uid}s" x1="0" y1="0" x2="0" y2="1">{stops}</linearGradient><linearGradient id="{uid}g" x1="0" y1="0" x2="0" y2="1">{gstops}</linearGradient>'
            f'<clipPath id="{uid}c"><rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" rx="{radius:g}"/></clipPath>'
            f'<filter id="{uid}f" x="-5%" y="-5%" width="110%" height="115%"><feDropShadow dx="0" dy="1.6" stdDeviation="2.4" flood-color="#3B2F1A" flood-opacity="0.3"/></filter></defs>'
            f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" rx="{radius:g}" fill="#FFFFFF" filter="url(#{uid}f)"/>'
            f'<g clip-path="url(#{uid}c)"><rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" fill="url(#{uid}s)"/>{g}</g>'
            f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" rx="{radius:g}" fill="none" stroke="{border}" stroke-width="2.2" stroke-opacity="0.9"/>')


def path_points(d, per=10):
    """The points along an old drawing's path (M, L, C and Z only, each command written out): its curves sampled `per` times each, to cut a picture to the shape of a region of the drawing."""
    tokens = re.findall(r"[MLCZ]|-?\d*\.?\d+", d)
    pts, i, cur = [], 0, (0.0, 0.0)
    while i < len(tokens):
        t = tokens[i]
        if t in "ML":
            cur = (float(tokens[i + 1]), float(tokens[i + 2]))
            pts.append(cur)
            i += 3
        elif t == "C":
            x1, y1, x2, y2, x, y = (float(v) for v in tokens[i + 1:i + 7])
            x0, y0 = cur
            for k in range(1, per + 1):
                u = k / per
                a, b, c, e = (1 - u) ** 3, 3 * u * (1 - u) ** 2, 3 * u * u * (1 - u), u ** 3
                pts.append((a * x0 + b * x1 + c * x2 + e * x, a * y0 + b * y1 + c * y2 + e * y))
            cur = (x, y)
            i += 7
        else:
            i += 1
    return pts
