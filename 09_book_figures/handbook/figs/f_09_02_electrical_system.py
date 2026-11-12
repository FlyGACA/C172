"""Figure 9-2. A simple light-aeroplane electrical system. The parts drawn as the parts they are (the battery with its terminals, the master switch with its two rockers, the contactor, the
ammeter dial, the alternator with its pulley, the voltage regulator with its heat sink, the warning lamp, the bus bar, the circuit breakers and a few loads, the starter, and the magnetos
and the ignition switch in a dashed box of their own, apart from the bus), joined by wires: power in red, the alternator's output in blue, controls thin and grey. The drawing is made by
this module (figs/scene.py supplies the callouts); the eleven numbered callouts of the old figure are kept."""
import math

from figs import scene as S

n = S.n
RED, BLUE, GREY, BUS = "#D6342C", "#2B6DD6", "#6B7686", "#F29A2E"


def defs():
    g = S.gradient
    return ("<defs>"
            + g("f0902bg", [(0, "#F7FAFD"), (1, "#E1EAF4")])
            + g("f0902red", [(0, "#EE5A4F"), (1, "#B5251E")]) + g("f0902redt", [(0, "#FB9D94"), (1, "#E2564B")]) + g("f0902reds", [(0, "#A81E17"), (1, "#7A130E")])
            + g("f0902steel", [(0, "#8E9BB0"), (0.45, "#EEF2F8"), (1, "#7B8799")], 0, 0, 1, 0) + g("f0902steelv", [(0, "#EEF2F8"), (1, "#8E9BB0")])
            + g("f0902blue", [(0, "#7FB1F2"), (0.5, "#3F78D0"), (1, "#244E96")]) + g("f0902blueh", [(0, "#2A56A0"), (0.4, "#6FA3EA"), (1, "#2A56A0")], 0, 0, 1, 0)
            + g("f0902black", [(0, "#3A4458"), (1, "#151B28")]) + g("f0902grey", [(0, "#A3ADBC"), (0.5, "#E6EAF0"), (1, "#8A95A6")], 0, 0, 1, 0)
            + g("f0902bus", [(0, "#FFC568"), (0.5, "#F29A2E"), (1, "#C96A10")], 0, 0, 1, 0)
            + g("f0902face", [(0, "#FFFFFF"), (1, "#DCE3EC")])
            + f'<radialGradient id="f0902lamp" cx="0.38" cy="0.32" r="0.8"><stop offset="0" stop-color="#FFC9C2"/><stop offset="0.5" stop-color="#F0453B"/><stop offset="1" stop-color="#9E1B14"/></radialGradient>'
            + f'<radialGradient id="f0902glow"><stop offset="0" stop-color="#FF6A5E" stop-opacity="0.65"/><stop offset="1" stop-color="#FF6A5E" stop-opacity="0"/></radialGradient>'
            + f'<radialGradient id="f0902bulb" cx="0.4" cy="0.35" r="0.8"><stop offset="0" stop-color="#FFFBE0"/><stop offset="0.6" stop-color="#FFE27A"/><stop offset="1" stop-color="#E9B52E"/></radialGradient>'
            + f'<filter id="f0902sh" x="-20%" y="-20%" width="145%" height="150%"><feDropShadow dx="1.5" dy="3" stdDeviation="2.6" flood-color="#1B2B44" flood-opacity="0.28"/></filter>'
            + "</defs>")


def wire(points, colour, width=3.6, casing=True, dash=None):
    d = "M " + " L ".join(f"{n(x)},{n(y)}" for x, y in points)
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
    under = f'<path d="{d}" fill="none" stroke="#FFFFFF" stroke-width="{n(width + 2.6)}" stroke-linejoin="round" stroke-linecap="round" opacity="0.85"/>' if casing else ""
    return under + f'<path d="{d}" fill="none" stroke="{colour}" stroke-width="{n(width)}" stroke-linejoin="round" stroke-linecap="round"{dash_attr}/>'


def dot(x, y, colour):
    return f'<circle cx="{n(x)}" cy="{n(y)}" r="3.6" fill="{colour}" stroke="#FFFFFF" stroke-width="1.2"/>'


def ground(x, y, colour="#4B5563"):
    return (f'<line x1="{n(x)}" y1="{n(y)}" x2="{n(x)}" y2="{n(y + 5)}" stroke="{colour}" stroke-width="1.6"/>'
            + "".join(f'<line x1="{n(x - w)}" y1="{n(y + 5 + i * 3.4)}" x2="{n(x + w)}" y2="{n(y + 5 + i * 3.4)}" stroke="{colour}" stroke-width="1.6" stroke-linecap="round"/>' for i, w in enumerate((8, 5.5, 3)))
            )


def battery(x0, y0, x1, y1):
    d = 11
    plus = f'<path d="M {n(x1 - 20)},{n(y0 + 24)} h 9 M {n(x1 - 15.5)},{n(y0 + 19.5)} v 9" stroke="#FFFFFF" stroke-width="2.4" stroke-linecap="round"/>'
    minus = f'<path d="M {n(x0 + 11)},{n(y0 + 24)} h 9" stroke="#FFFFFF" stroke-width="2.4" stroke-linecap="round"/>'
    ribs = "".join(f'<line x1="{n(x0 + 8 + i * (x1 - x0 - 16) / 4)}" y1="{n(y0 + 34)}" x2="{n(x0 + 8 + i * (x1 - x0 - 16) / 4)}" y2="{n(y1 - 6)}" stroke="#FFFFFF" stroke-opacity="0.18" stroke-width="2"/>' for i in range(5))
    term = "".join(f'<ellipse cx="{n(tx)}" cy="{n(y0 + 3)}" rx="6.4" ry="2.8" fill="url(#f0902steel)" stroke="#5A6578" stroke-width="0.8"/><rect x="{n(tx - 6.4)}" y="{n(y0 + 3)}" width="12.8" height="7" fill="url(#f0902steel)"/><ellipse cx="{n(tx)}" cy="{n(y0 + 10)}" rx="6.4" ry="2.8" fill="#7B8799"/>' for tx in (x0 + 18, x1 - 18))
    return (f'<g filter="url(#f0902sh)"><polygon points="{S.pts([(x0, y0 + 10), (x0 + d, y0 + 1), (x1 + d, y0 + 1), (x1, y0 + 10)])}" fill="url(#f0902redt)"/>'
            f'<polygon points="{S.pts([(x1, y0 + 10), (x1 + d, y0 + 1), (x1 + d, y1 - 9), (x1, y1)])}" fill="url(#f0902reds)"/>'
            f'<rect x="{n(x0)}" y="{n(y0 + 10)}" width="{n(x1 - x0)}" height="{n(y1 - y0 - 10)}" rx="3" fill="url(#f0902red)"/></g>' + ribs + term + plus + minus)


def contactor(x0, y0, x1, y1, studs):
    w, h = x1 - x0, y1 - y0
    out = [f'<g filter="url(#f0902sh)"><rect x="{n(x0)}" y="{n(y0 + 4)}" width="{n(w)}" height="{n(h - 4)}" rx="5" fill="url(#f0902blueh)" stroke="#183A74" stroke-width="0.9"/>'
           f'<ellipse cx="{n((x0 + x1) / 2)}" cy="{n(y0 + 5)}" rx="{n(w / 2)}" ry="4.6" fill="url(#f0902grey)" stroke="#5A6578" stroke-width="0.8"/></g>',
           f'<rect x="{n(x0 + 3)}" y="{n(y0 + h * 0.45)}" width="{n(w - 6)}" height="{n(h * 0.18)}" fill="#FFFFFF" opacity="0.2"/>']
    for sx, sy in studs:
        out.append(f'<circle cx="{n(sx)}" cy="{n(sy)}" r="5.6" fill="url(#f0902steel)" stroke="#5A6578" stroke-width="0.9"/><polygon points="{S.pts([(sx + 2.8 * math.cos(math.radians(a)), sy + 2.8 * math.sin(math.radians(a))) for a in range(0, 360, 60)])}" fill="#7B8799"/>')
    return "".join(out)


def switch(x0, y0, x1, y1):
    w = (x1 - x0 - 12) / 2
    out = [f'<g filter="url(#f0902sh)"><rect x="{n(x0)}" y="{n(y0)}" width="{n(x1 - x0)}" height="{n(y1 - y0)}" rx="5" fill="url(#f0902black)" stroke="#0E1422" stroke-width="1"/></g>']
    for i in range(2):
        rx0 = x0 + 5 + i * (w + 2)
        out.append(f'<rect x="{n(rx0)}" y="{n(y0 + 5)}" width="{n(w)}" height="{n(y1 - y0 - 10)}" rx="3" fill="url(#f0902red)" stroke="#6E120D" stroke-width="0.8"/>'
                   f'<rect x="{n(rx0 + 1.5)}" y="{n(y0 + 6.5)}" width="{n(w - 3)}" height="4" rx="2" fill="#FFFFFF" opacity="0.35"/>'
                   f'<line x1="{n(rx0 + w / 2)}" y1="{n(y0 + 12)}" x2="{n(rx0 + w / 2)}" y2="{n(y0 + 20)}" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round"/>'
                   f'<circle cx="{n(rx0 + w / 2)}" cy="{n(y1 - 14)}" r="3.2" fill="none" stroke="#FFFFFF" stroke-width="1.6"/>')
    return "".join(out)


def ammeter(cx, cy, r=22):
    ticks = "".join(f'<line x1="{n(cx + (r - 7) * math.sin(math.radians(a)))}" y1="{n(cy - (r - 7) * math.cos(math.radians(a)))}" x2="{n(cx + (r - 4.5) * math.sin(math.radians(a)))}" y2="{n(cy - (r - 4.5) * math.cos(math.radians(a)))}" stroke="#374151" stroke-width="1.2"/>' for a in range(-60, 61, 20))
    ang = math.radians(22)
    return (f'<g filter="url(#f0902sh)"><circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}" fill="url(#f0902black)" stroke="#0E1422" stroke-width="1"/></g>'
            f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r - 3.4)}" fill="url(#f0902face)"/>' + ticks
            + f'<path d="M {n(cx + 8.5)},{n(cy + 5)} h 5 M {n(cx + 11)},{n(cy + 2.5)} v 5" stroke="#1F2937" stroke-width="1.5" stroke-linecap="round"/><path d="M {n(cx - 14)},{n(cy + 5)} h 5" stroke="#1F2937" stroke-width="1.5" stroke-linecap="round"/>'
            + f'<line x1="{n(cx)}" y1="{n(cy)}" x2="{n(cx + (r - 6) * math.sin(ang))}" y2="{n(cy - (r - 6) * math.cos(ang))}" stroke="#D6342C" stroke-width="1.8" stroke-linecap="round"/><circle cx="{n(cx)}" cy="{n(cy)}" r="2.6" fill="#374151"/>'
            + f'<path d="M {n(cx - r + 6)},{n(cy - 6)} A {n(r - 5)},{n(r - 5)} 0 0 1 {n(cx + 2)},{n(cy - r + 5)}" fill="none" stroke="#FFFFFF" stroke-opacity="0.55" stroke-width="1.3" stroke-linecap="round"/>')


def alternator(x0, y0, x1, y1):
    h = y1 - y0
    fins = "".join(f'<line x1="{n(x0 + 20 + i * 7)}" y1="{n(y0 + 3)}" x2="{n(x0 + 20 + i * 7)}" y2="{n(y1 - 3)}" stroke="#16356B" stroke-opacity="0.45" stroke-width="1.4"/>' for i in range(int((x1 - x0 - 44) / 7)))
    return (f'<g filter="url(#f0902sh)"><rect x="{n(x0 + 14)}" y="{n(y0)}" width="{n(x1 - x0 - 14)}" height="{n(h)}" rx="9" fill="url(#f0902blue)" stroke="#183A74" stroke-width="1"/>'
            f'<ellipse cx="{n(x1)}" cy="{n(y0 + h / 2)}" rx="7" ry="{n(h / 2)}" fill="url(#f0902blue)" stroke="#183A74" stroke-width="1"/></g>' + fins
            + f'<rect x="{n(x0 + 2)}" y="{n(y0 + h / 2 - 3)}" width="14" height="6" fill="url(#f0902steelv)" stroke="#5A6578" stroke-width="0.8"/>'
            f'<ellipse cx="{n(x0 + 8)}" cy="{n(y0 + h / 2)}" rx="6" ry="{n(h * 0.36)}" fill="url(#f0902steel)" stroke="#5A6578" stroke-width="1"/><ellipse cx="{n(x0 + 8)}" cy="{n(y0 + h / 2)}" rx="2" ry="{n(h * 0.2)}" fill="#7B8799"/>'
            f'<circle cx="{n(x1 - 1)}" cy="{n(y0 + h / 2)}" r="{n(h * 0.27)}" fill="#FFFFFF" opacity="0.92"/>'
            f'<path d="M {n(x1 - 9)},{n(y0 + h / 2)} q 2.3,-5.5 4.6,0 t 4.6,0 t 4.6,0" fill="none" stroke="#1F2937" stroke-width="1.6" stroke-linecap="round" transform="translate(-1 0)"/>')


def regulator(x0, y0, x1, y1):
    fins = "".join(f'<rect x="{n(x0 + 6 + i * 8)}" y="{n(y0 - 7)}" width="4.2" height="9" rx="1" fill="url(#f0902steelv)" stroke="#5A6578" stroke-width="0.6"/>' for i in range(int((x1 - x0 - 8) / 8)))
    pins = "".join(f'<rect x="{n(x0 + 9 + i * 14)}" y="{n(y1 - 1)}" width="4" height="6" fill="#E3B24A" stroke="#8A6A1E" stroke-width="0.6"/>' for i in range(3))
    return (f'<g filter="url(#f0902sh)"><rect x="{n(x0)}" y="{n(y0)}" width="{n(x1 - x0)}" height="{n(y1 - y0)}" rx="5" fill="url(#f0902black)" stroke="#0E1422" stroke-width="1"/></g>' + fins + pins
            + f'<rect x="{n(x0 + 5)}" y="{n(y0 + 5)}" width="{n(x1 - x0 - 10)}" height="3" rx="1.5" fill="#FFFFFF" opacity="0.2"/>'
            f'<path d="M {n(x0 + 8)},{n(y0 + 24)} l 4,-8 l 4,16 l 4,-16 l 4,16 l 4,-8 h 8" fill="none" stroke="#7FD0A6" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/>')


def lamp(cx, cy, r=14):
    return (f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r * 2.2)}" fill="url(#f0902glow)"/>'
            f'<g filter="url(#f0902sh)"><circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}" fill="url(#f0902steel)" stroke="#5A6578" stroke-width="1"/></g>'
            f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r - 3.2)}" fill="url(#f0902lamp)"/><ellipse cx="{n(cx - 3)}" cy="{n(cy - 4)}" rx="4" ry="2.6" fill="#FFFFFF" opacity="0.7"/>')


def bus(x, y0, y1, w=18):
    screws = "".join(f'<circle cx="{n(x + w / 2)}" cy="{n(yy)}" r="2.4" fill="url(#f0902steel)" stroke="#8A4A08" stroke-width="0.6"/>' for yy in range(int(y0 + 14), int(y1 - 6), 36))
    return (f'<g filter="url(#f0902sh)"><rect x="{n(x)}" y="{n(y0)}" width="{n(w)}" height="{n(y1 - y0)}" rx="4" fill="url(#f0902bus)" stroke="#9A520A" stroke-width="1"/></g>' + screws
            + f'<rect x="{n(x + 2.5)}" y="{n(y0 + 3)}" width="3" height="{n(y1 - y0 - 6)}" rx="1.5" fill="#FFFFFF" opacity="0.4"/>')


def breaker(cx, cy, r=9.5):
    return (f'<g filter="url(#f0902sh)"><circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}" fill="url(#f0902black)" stroke="#0E1422" stroke-width="1"/></g>'
            f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r - 2.8)}" fill="url(#f0902face)" stroke="#9AA5B5" stroke-width="0.8"/><circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r - 5.2)}" fill="none" stroke="#B6BFCC" stroke-width="0.8"/>')


def load_lamp(cx, cy):
    rays = "".join(f'<line x1="{n(cx + 12 * math.cos(math.radians(a)))}" y1="{n(cy - 4 + 12 * math.sin(math.radians(a)))}" x2="{n(cx + 17 * math.cos(math.radians(a)))}" y2="{n(cy - 4 + 17 * math.sin(math.radians(a)))}" stroke="#F2B21E" stroke-width="1.6" stroke-linecap="round"/>' for a in range(-180, 1, 30))
    return (rays + f'<circle cx="{n(cx)}" cy="{n(cy - 4)}" r="9.5" fill="url(#f0902bulb)" stroke="#B98A12" stroke-width="0.9"/><rect x="{n(cx - 5.5)}" y="{n(cy + 4)}" width="11" height="7" rx="1.5" fill="url(#f0902steel)" stroke="#5A6578" stroke-width="0.8"/>'
            f'<path d="M {n(cx - 3.5)},{n(cy + 3)} l 2,-7 l 2,5 l 2,-5 l 2,7" fill="none" stroke="#8A5E10" stroke-width="0.9"/>')


def load_radio(cx, cy):
    return (f'<g filter="url(#f0902sh)"><rect x="{n(cx - 19)}" y="{n(cy - 12)}" width="38" height="24" rx="3.5" fill="url(#f0902black)" stroke="#0E1422" stroke-width="1"/></g>'
            f'<rect x="{n(cx - 15)}" y="{n(cy - 8)}" width="20" height="8" rx="1.5" fill="#6FE0B0"/><rect x="{n(cx - 13)}" y="{n(cy - 6)}" width="9" height="2.4" fill="#0F5C42"/>'
            f'<circle cx="{n(cx + 11)}" cy="{n(cy - 4)}" r="3.4" fill="url(#f0902steel)" stroke="#5A6578" stroke-width="0.6"/><circle cx="{n(cx + 11)}" cy="{n(cy + 6)}" r="3.4" fill="url(#f0902steel)" stroke="#5A6578" stroke-width="0.6"/>'
            f'<rect x="{n(cx - 15)}" y="{n(cy + 3)}" width="20" height="2" fill="#A3ADBC"/>')


def load_gauge(cx, cy):
    return (f'<g filter="url(#f0902sh)"><circle cx="{n(cx)}" cy="{n(cy)}" r="13" fill="url(#f0902black)" stroke="#0E1422" stroke-width="1"/></g><circle cx="{n(cx)}" cy="{n(cy)}" r="10" fill="url(#f0902face)"/>'
            + "".join(f'<line x1="{n(cx + 6.5 * math.sin(math.radians(a)))}" y1="{n(cy - 6.5 * math.cos(math.radians(a)))}" x2="{n(cx + 8.8 * math.sin(math.radians(a)))}" y2="{n(cy - 8.8 * math.cos(math.radians(a)))}" stroke="#374151" stroke-width="1"/>' for a in range(-70, 71, 35))
            + f'<line x1="{n(cx)}" y1="{n(cy)}" x2="{n(cx + 6.5)}" y2="{n(cy - 4.2)}" stroke="#16A34A" stroke-width="1.8" stroke-linecap="round"/><circle cx="{n(cx)}" cy="{n(cy)}" r="2" fill="#374151"/>')


def load_heater(cx, cy):
    return (f'<g filter="url(#f0902sh)"><rect x="{n(cx - 19)}" y="{n(cy - 11)}" width="38" height="22" rx="4" fill="#FDE9C8" stroke="#C98A2B" stroke-width="1"/></g>'
            f'<path d="M {n(cx - 14)},{n(cy)} l 3.5,-7 l 3.5,14 l 3.5,-14 l 3.5,14 l 3.5,-14 l 3.5,14 l 3.5,-7" fill="none" stroke="#E2531E" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>')


def load_nav(cx, cy):
    return (f'<g filter="url(#f0902sh)"><circle cx="{n(cx)}" cy="{n(cy)}" r="13" fill="url(#f0902steel)" stroke="#5A6578" stroke-width="1"/></g><circle cx="{n(cx)}" cy="{n(cy)}" r="9.4" fill="#F6F8FB" stroke="#9AA5B5" stroke-width="0.8"/>'
            f'<path d="M {n(cx)},{n(cy - 7.5)} L {n(cx + 3)},{n(cy)} L {n(cx)},{n(cy + 7.5)} L {n(cx - 3)},{n(cy)} Z" fill="#D6342C"/><path d="M {n(cx)},{n(cy)} L {n(cx + 3)},{n(cy)} L {n(cx)},{n(cy + 7.5)} Z" fill="#374151"/><circle cx="{n(cx)}" cy="{n(cy)}" r="1.4" fill="#FFFFFF"/>')


def starter(x0, y0, x1, y1):
    h = y1 - y0
    teeth = f'<circle cx="{n(x0 + 8)}" cy="{n(y0 + h / 2)}" r="{n(h * 0.34)}" fill="none" stroke="#6B7686" stroke-width="{n(h * 0.12)}" stroke-dasharray="3.2 2.6"/><circle cx="{n(x0 + 8)}" cy="{n(y0 + h / 2)}" r="{n(h * 0.26)}" fill="url(#f0902steel)" stroke="#5A6578" stroke-width="0.9"/>'
    return (f'<g filter="url(#f0902sh)"><rect x="{n(x0 + 14)}" y="{n(y0)}" width="{n(x1 - x0 - 14)}" height="{n(h)}" rx="8" fill="url(#f0902grey)" stroke="#5A6578" stroke-width="1"/>'
            f'<rect x="{n(x1 - 22)}" y="{n(y0 + 1)}" width="22" height="{n(h - 2)}" rx="6" fill="url(#f0902black)" stroke="#0E1422" stroke-width="0.9"/></g>' + teeth
            + "".join(f'<line x1="{n(x0 + 28 + i * 8)}" y1="{n(y0 + 4)}" x2="{n(x0 + 28 + i * 8)}" y2="{n(y1 - 4)}" stroke="#6B7686" stroke-opacity="0.4" stroke-width="1.2"/>' for i in range(4)))


def magneto(cx, cy, r=19):
    return (f'<g filter="url(#f0902sh)"><circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}" fill="url(#f0902black)" stroke="#0E1422" stroke-width="1"/></g><circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r - 4)}" fill="url(#f0902grey)" stroke="#5A6578" stroke-width="0.8"/>'
            f'<path d="M {n(cx - 7)},{n(cy - 7)} v 9 a 7,7 0 0 0 14,0 v -9" fill="none" stroke="#B3261E" stroke-width="4.2" stroke-linecap="butt"/><path d="M {n(cx - 7)},{n(cy - 7)} v 3.6 M {n(cx + 7)},{n(cy - 7)} v 3.6" stroke="#FFFFFF" stroke-width="4.2"/>')


def ignition_switch(cx, cy, r=17):
    return (f'<g filter="url(#f0902sh)"><circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}" fill="url(#f0902steel)" stroke="#5A6578" stroke-width="1"/></g><circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r - 4)}" fill="url(#f0902steelv)" stroke="#8A95A6" stroke-width="0.8"/>'
            f'<circle cx="{n(cx)}" cy="{n(cy - 2)}" r="3.4" fill="#1F2937"/><path d="M {n(cx - 1.6)},{n(cy - 2)} h 3.2 l 1.4,9 h -6 Z" fill="#1F2937"/>'
            + "".join(f'<circle cx="{n(cx + (r + 1) * math.sin(math.radians(a)))}" cy="{n(cy - (r + 1) * math.cos(math.radians(a)))}" r="1.3" fill="#6B7686"/>' for a in (-50, -20, 20, 50)))


def scene():
    out = ['<rect x="0" y="0" width="640" height="360" fill="url(#f0902bg)"/>']
    # the box of the ignition, apart from the bus
    out.append('<rect x="14" y="10" width="206" height="96" rx="12" fill="#FFFFFF" fill-opacity="0.55" stroke="#8A95A6" stroke-width="1.3" stroke-dasharray="6 4"/>')
    # controls (thin, grey): the master switch to the contactor coil and to the regulator
    out.append(wire([(262, 62), (262, 74), (242, 74), (242, 190), (208, 190), (208, 214)], GREY, 1.8, casing=False))
    out.append(wire([(314, 62), (314, 113), (352, 113)], GREY, 1.8, casing=False))
    out.append(wire([(372, 134), (372, 258)], GREY, 1.8, casing=False))
    out.append(wire([(414, 113), (440, 113)], GREY, 1.8, casing=False))
    out.append(wire([(400, 92), (400, 60), (456, 60)], GREY, 1.8, casing=False))
    # the ignition: magnetos to the switch, and to ground
    out.append(wire([(56, 71), (56, 84), (184, 84), (184, 69)], "#4B5563", 1.8, casing=False) + wire([(184, 84), (204, 84)], "#4B5563", 1.8, casing=False))
    out.append(wire([(116, 71), (116, 84)], "#4B5563", 1.8, casing=False))
    # power: battery to the contactor, the ammeter and the bus; the alternator joins ahead of the bus; the starter on its own contactor
    out.append(wire([(96, 246), (96, 226), (190, 226)], RED, 4.2))
    out.append(wire([(226, 226), (276, 226), (400, 226), (440, 226)], RED, 4.2))
    out.append(wire([(150, 226), (150, 168)], RED, 4.2) + wire([(134, 140), (112, 140)], RED, 4.2))
    out.append(wire([(400, 262), (400, 226)], BLUE, 4.2))
    out.append(wire([(458, 118), (488, 118)], BUS, 3.0) + wire([(458, 158), (488, 158)], BUS, 3.0) + wire([(458, 198), (488, 198)], BUS, 3.0) + wire([(458, 238), (488, 238)], BUS, 3.0) + wire([(458, 278), (488, 278)], BUS, 3.0))
    for y in (118, 158, 198, 238, 278):
        out.append(wire([(498, y), (556, y)], "#4B5563", 2.0, casing=False))
    # the parts
    out.append(magneto(56, 52) + magneto(116, 52) + ignition_switch(184, 52))
    out.append(switch(246, 18, 330, 62))
    out.append(starter(26, 114, 112, 166) + contactor(134, 118, 166, 168, [(150, 168), (134, 140)]))
    out.append(battery(24, 254, 112, 314))
    out.append(contactor(190, 214, 226, 262, [(190, 226), (226, 226)]))
    out.append(ammeter(276, 226))
    out.append(alternator(318, 262, 412, 316))
    out.append(regulator(352, 92, 414, 134))
    out.append(lamp(470, 60, 14))
    out.append(bus(440, 96, 286))
    for y in (118, 158, 198, 238, 278):
        out.append(breaker(498, y))
    out.append(load_lamp(578, 118) + load_radio(578, 158) + load_gauge(578, 198) + load_heater(578, 238) + load_nav(578, 278))
    out.append(dot(150, 226, RED) + dot(400, 226, RED))
    out.append(ground(44, 318) + ground(366, 322) + ground(204, 86))
    return "".join(out)


def callouts():
    c = S.callout
    return "".join([c(1, 70, 340, 70, 318), c(2, 352, 40, 332, 40), c(3, 252, 268, 228, 254), c(4, 276, 186, 276, 204), c(5, 372, 344, 364, 318), c(6, 330, 150, 356, 128),
                    c(7, 510, 34, 482, 52), c(8, 432, 318, 447, 288), c(9, 534, 88, 504, 112), c(10, 70, 196, 70, 170), c(11, 244, 108, 218, 92)])


def plate():
    return {
        "id": "fig-09-02-electrical-system",
        "replaces": "fig-09-02-electrical-system.svg",
        "book_file": "plate-09-02-electrical-system.jpg",
        "caption": "Figure 9-2. A simple light-aeroplane electrical system",
        "desc": "Figure 9-2. A simple light-aeroplane electrical system",
        "legend": ["Battery.", "Master switch, alternator and battery halves.", "Battery contactor.", "Ammeter.", "Alternator.", "Voltage regulator.", "Low-voltage warning light.", "Bus bar.",
                   "Circuit breakers.", "Starter contactor and starter motor.", "Magnetos and ignition switch, separate from the bus."],
        "canvas": [640, 360],
        "background": "pale",
        "reskin": {"svg": "fig-09-02-electrical-system.svg", "blank": True, "layers": [defs(), scene(), callouts()]},
    }
