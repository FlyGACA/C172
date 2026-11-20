"""A richer tile for the figures made of small drawings in cards: a soft vertical gradient in a tone, a pale spotlight behind the drawing, a floor band with a soft edge and a thin white rim,
in the manner of the scene panels of the weather figures. `tile(uid, x, y, w, h, tone)` returns the markup; the drawing goes on top."""
from figs import scene as S

n = S.n
TONES = {
    "blue": ("#CFE0F5", "#F1F6FC", "#B9CEE8"),
    "sand": ("#F1E3C2", "#FBF5E6", "#E2CFA2"),
    "green": ("#CDEBD6", "#F0FAF3", "#B4DBC1"),
    "red": ("#F8CFCB", "#FDF0EE", "#EDB5AF"),
    "slate": ("#D5DCE8", "#F3F5F9", "#BFC8D8"),
    "night": ("#2F4170", "#5C6FA3", "#25345C"),
}


def tile(uid, x, y, w, h, tone="slate", rx=9.0):
    top, bottom, floor = TONES[tone]
    night = tone == "night"
    return (f'<defs><linearGradient id="{uid}g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{top}"/><stop offset="1" stop-color="{bottom}"/></linearGradient>'
            f'<radialGradient id="{uid}r" cx="0.5" cy="0.46" r="0.55"><stop offset="0" stop-color="#FFFFFF" stop-opacity="{0.18 if night else 0.85}"/><stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/></radialGradient>'
            f'<clipPath id="{uid}c"><rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="{n(rx)}"/></clipPath>'
            f'<filter id="{uid}s" x="-10%" y="-10%" width="120%" height="125%"><feDropShadow dx="0" dy="1.6" stdDeviation="1.8" flood-color="#10233F" flood-opacity="0.26"/></filter></defs>'
            f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="{n(rx)}" fill="#FFFFFF" filter="url(#{uid}s)"/>'
            f'<g clip-path="url(#{uid}c)"><rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" fill="url(#{uid}g)"/>'
            f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" fill="url(#{uid}r)"/>'
            f'<rect x="{n(x)}" y="{n(y + h * 0.80)}" width="{n(w)}" height="{n(h * 0.20)}" fill="{floor}" fill-opacity="0.55"/></g>'
            f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="{n(rx)}" fill="none" stroke="#FFFFFF" stroke-width="1.6"/>')
