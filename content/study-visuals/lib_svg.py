"""Tiny deterministic SVG helpers for the study visuals (Python standard library only)."""

W = 1600
H = 1000

PALETTE = {
    "ink": "#1F2933",
    "muted": "#52606D",
    "rule": "#CBD2D9",
    "panel": "#F5F7FA",
    "track": "#E4E7EB",
    "accent": "#0E5A8A",
    "green": "#0B7A4B",
    "yellow": "#C99A06",
    "red": "#B42318",
    "white": "#FFFFFF",
}

FAMILY = "IBM Plex Sans, IBM Plex Sans Arabic, Helvetica Neue, Arial, sans-serif"


def esc(value):
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def ltr(value):
    """Isolate a left-to-right run (numbers, ranges) inside right-to-left text, the same way
    09_book_figures/js/figures/aircraft_exterior.js keeps "160 BHP" in its own order."""
    return "\u2066%s\u2069" % value


def fmt(value, digits=2):
    text = ("%." + str(digits) + "f") % float(value)
    return text.rstrip("0").rstrip(".") if "." in text else text


def _attrs(options):
    parts = []
    for key, value in options.items():
        if value is None or value is False:
            continue
        name = key.replace("_", "-")
        if isinstance(value, float):
            value = fmt(value)
        parts.append(' %s="%s"' % (name, esc(value)))
    return "".join(parts)


def rect(x, y, w, h, **options):
    return '<rect x="%s" y="%s" width="%s" height="%s"%s/>' % (fmt(x), fmt(y), fmt(w), fmt(h), _attrs(options))


def line(x1, y1, x2, y2, **options):
    return '<line x1="%s" y1="%s" x2="%s" y2="%s"%s/>' % (fmt(x1), fmt(y1), fmt(x2), fmt(y2), _attrs(options))


def circle(cx, cy, r, **options):
    return '<circle cx="%s" cy="%s" r="%s"%s/>' % (fmt(cx), fmt(cy), fmt(r), _attrs(options))


def path(d, **options):
    return '<path d="%s"%s/>' % (esc(d), _attrs(options))


def text(x, y, value, **options):
    anchor = options.pop("anchor", "start")
    size = options.pop("size", 22)
    weight = options.pop("weight", None)
    fill = options.pop("fill", PALETTE["ink"])
    return (
        '<text x="%s" y="%s" text-anchor="%s" font-family="%s" font-size="%s"%s fill="%s"%s>%s</text>'
        % (
            fmt(x),
            fmt(y),
            anchor,
            FAMILY,
            size,
            ' font-weight="%s"' % weight if weight else "",
            fill,
            _attrs(options),
            esc(value),
        )
    )


def group(body):
    return "<g>%s</g>" % body


def document(lang, direction, title, body):
    return "\n".join(
        [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" direction="%s" lang="%s" role="img" aria-labelledby="t">'
            % (W, H, W, H, direction, lang),
            '<title id="t">%s</title>' % esc(title),
            rect(0, 0, W, H, fill=PALETTE["white"]),
            body,
            "</svg>",
            "",
        ]
    )


def wrap(value, max_chars=150):
    lines = []
    current = ""
    for word in str(value).split():
        candidate = (current + " " + word) if current else word
        if len(candidate) > max_chars and current:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


def scale(value, domain, target):
    d0, d1 = domain
    r0, r1 = target
    return r0 + ((value - d0) / (d1 - d0)) * (r1 - r0)
