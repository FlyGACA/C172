"""Figure 20-1. Latitude and longitude, and why a minute of latitude is a nautical mile. Drawn again as two shaded globes on the old figure's canvas, the geometry of the old drawing exactly:
on the left a sphere seen edge-on to the equator, so that P's meridian is its blue limb, the axis stands upright, the equator and the parallels are straight chords, the parallel through P
is a green dashed chord and the latitude is the red arc at the centre; on the right the same sphere seen from above the North Pole, the equator its limb, the parallels circles, the
meridians radii, the prime meridian straight down, P's meridian 60° east of it and the longitude a red arc at the pole. A day side and a night side, thin graticule curves, glowing
arcs, the minutes (much enlarged) in amber and P a pin. Every callout of the old figure is kept (figs/h_a4.py has the parts)."""
import math

from figs import h_a4 as H
from figs import scene as S

L = (165.0, 190.0)
RT = (475.0, 190.0)
R = 135.0
PHI = 50.0           # the latitude of P in the drawing
LAM = 60.0           # its longitude east of the prime meridian


def on_circle(c, r, deg):
    """The point of a circle at `deg` degrees above the horizontal to the right (counterclockwise on the page)."""
    return c[0] + r * math.cos(math.radians(deg)), c[1] - r * math.sin(math.radians(deg))


def left_globe():
    cx, cy = L
    out = [H.globe("g1l", cx, cy, R)]
    clip = f'<g clip-path="url(#g1lc)">'
    # the graticule: parallels are chords (the sphere is seen edge-on to the equator), the other meridians ellipses
    grat = []
    for lat in (30, 70, -30, -70, -50):
        y = cy - R * math.sin(math.radians(lat))
        h = R * math.cos(math.radians(lat))
        grat.append(f'<line x1="{S.n(cx - h)}" y1="{S.n(y)}" x2="{S.n(cx + h)}" y2="{S.n(y)}" stroke="#FFFFFF" stroke-opacity="0.26" stroke-width="0.8"/>')
    for d in (30, 60):
        grat.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{S.n(R * math.sin(math.radians(d)))}" ry="{R}" fill="none" stroke="#FFFFFF" stroke-opacity="0.22" stroke-width="0.8"/>')
    out.append(clip + "".join(grat) + "</g>")
    # P's meridian: the limb, in blue with a glow
    out.append(H.glow_line_filter("g1lg", 3.0))
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="#3D7BFF" stroke-width="5" opacity="0.8" filter="url(#g1lg)"/>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="#2F66E8" stroke-width="3.4"/>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="#A9CBFF" stroke-width="1.1"/>')
    # the axis, with its arrow, and the pole
    out.append('<line x1="165" y1="33" x2="165" y2="343" stroke="#FFFFFF" stroke-opacity="0.9" stroke-width="1.6" stroke-dasharray="6 4"/>'
               '<polygon points="165,31 170.5,41 159.5,41" fill="#FFFFFF" stroke="#FFFFFF" stroke-width="0.8" stroke-linejoin="round"/>'
               '<circle cx="165" cy="55" r="4.2" fill="#FFFFFF" stroke="#2A4A8C" stroke-width="1"/>')
    # the equator, a lit line
    out.append(f'<line x1="30" y1="190" x2="300" y2="190" stroke="#FFC857" stroke-width="5" opacity="0.7" filter="url(#g1lg)"/>'
               f'<line x1="30" y1="190" x2="300" y2="190" stroke="#FFE9A6" stroke-width="2.6" stroke-linecap="round"/>')
    # the parallel through P: green, dashed, and the radius to P
    px, py = on_circle(L, R, PHI)
    out.append(f'<line x1="78.2" y1="{S.n(py)}" x2="{S.n(px)}" y2="{S.n(py)}" stroke="#2BE39A" stroke-width="5" opacity="0.7" filter="url(#g1lg)"/>'
               f'<line x1="78.2" y1="{S.n(py)}" x2="{S.n(px)}" y2="{S.n(py)}" stroke="#FFFFFF" stroke-opacity="0.8" stroke-width="4.6" stroke-dasharray="7 4"/>'
               f'<line x1="78.2" y1="{S.n(py)}" x2="{S.n(px)}" y2="{S.n(py)}" stroke="#0F9F6B" stroke-width="2.4" stroke-dasharray="7 4"/>')
    out.append(f'<line x1="{cx}" y1="{cy}" x2="{S.n(px)}" y2="{S.n(py)}" stroke="#FFFFFF" stroke-width="1.7" stroke-opacity="0.95"/>')
    # the latitude: a red arc at the centre
    out.append(f'<path d="M192.0,157.8 A42.0,42.0 0 0,1 207.0,190.0" fill="none" stroke="#FF5B4D" stroke-width="7" opacity="0.85" filter="url(#g1lg)"/>'
               f'<path d="M192.0,157.8 A42.0,42.0 0 0,1 207.0,190.0" fill="none" stroke="#FF8A7E" stroke-width="3.4" stroke-linecap="round"/>')
    out.append(H.text(216.5, 173.0, "φ", 19, "#FFB0A6", "bold", "middle", halo="#10233F"))
    # a minute of latitude (much enlarged): an amber arc on the limb
    out.append(f'<path d="M234.5,74.3 A135.0,135.0 0 0,1 251.8,86.6" fill="none" stroke="#FFB020" stroke-width="9" opacity="0.8" filter="url(#g1lg)"/>'
               f'<path d="M234.5,74.3 A135.0,135.0 0 0,1 251.8,86.6" fill="none" stroke="#FFFFFF" stroke-opacity="0.85" stroke-width="7.4" stroke-linecap="butt"/>'
               f'<path d="M234.5,74.3 A135.0,135.0 0 0,1 251.8,86.6" fill="none" stroke="#F59E0B" stroke-width="5.2" stroke-linecap="butt"/>')
    # P, a pin
    out.append(H.pin(px, py, 40.0, 1.0)[0])
    return "".join(out)


def right_globe():
    cx, cy = RT
    out = [H.globe("g1r", cx, cy, R)]
    grat = []
    for lat in (30, 70):
        grat.append(f'<circle cx="{cx}" cy="{cy}" r="{S.n(R * math.cos(math.radians(lat)))}" fill="none" stroke="#FFFFFF" stroke-opacity="0.26" stroke-width="0.8"/>')
    for k in range(12):
        a = k * 30.0
        ex, ey = cx + R * math.sin(math.radians(a)), cy + R * math.cos(math.radians(a))          # measured from straight down
        grat.append(f'<line x1="{cx}" y1="{cy}" x2="{S.n(ex)}" y2="{S.n(ey)}" stroke="#FFFFFF" stroke-opacity="0.22" stroke-width="0.8"/>')
    out.append(f'<g clip-path="url(#g1rc)">' + "".join(grat) + "</g>")
    out.append(H.glow_line_filter("g1rg", 3.0))
    # the equator: the limb
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="#FFC857" stroke-width="5" opacity="0.7" filter="url(#g1rg)"/>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="#FFE9A6" stroke-width="2.6"/>')
    # the parallel through P (radius R cos phi)
    rp = R * math.cos(math.radians(PHI))
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{S.n(rp)}" fill="none" stroke="#2BE39A" stroke-width="5" opacity="0.7" filter="url(#g1rg)"/>'
               f'<circle cx="{cx}" cy="{cy}" r="{S.n(rp)}" fill="none" stroke="#FFFFFF" stroke-opacity="0.8" stroke-width="4.6" stroke-dasharray="7 4"/>'
               f'<circle cx="{cx}" cy="{cy}" r="{S.n(rp)}" fill="none" stroke="#0F9F6B" stroke-width="2.4" stroke-dasharray="7 4"/>')
    # the prime meridian (straight down), P's meridian and the next minute's
    out.append(f'<line x1="{cx}" y1="{cy}" x2="{cx}" y2="325" stroke="#FFFFFF" stroke-width="5" opacity="0.5" filter="url(#g1rg)"/><line x1="{cx}" y1="{cy}" x2="{cx}" y2="325" stroke="#FFFFFF" stroke-width="2.4" stroke-linecap="round"/>')
    out.append(f'<line x1="{cx}" y1="{cy}" x2="591.9" y2="257.5" stroke="#FFFFFF" stroke-width="1.7" stroke-opacity="0.95"/>')
    out.append(f'<line x1="{cx}" y1="{cy}" x2="603.4" y2="231.7" stroke="#FFFFFF" stroke-width="1.2" stroke-opacity="0.85"/>')
    # the longitude: a red arc at the pole
    out.append(f'<path d="M475.0,224.0 A34.0,34.0 0 0,0 504.4,207.0" fill="none" stroke="#FF5B4D" stroke-width="7" opacity="0.85" filter="url(#g1rg)"/>'
               f'<path d="M475.0,224.0 A34.0,34.0 0 0,0 504.4,207.0" fill="none" stroke="#FF8A7E" stroke-width="3.4" stroke-linecap="round"/>')
    out.append(H.text(499.5, 238.4, "λ", 19, "#FFB0A6", "bold", "middle", halo="#10233F"))
    # a minute of longitude, much enlarged: on the equator and on the parallel
    for d in ('M591.9,257.5 A135.0,135.0 0 0,0 603.4,231.7', 'M550.2,233.4 A86.8,86.8 0 0,0 557.5,216.8'):
        out.append(f'<path d="{d}" fill="none" stroke="#FFB020" stroke-width="9" opacity="0.8" filter="url(#g1rg)"/>'
                   f'<path d="{d}" fill="none" stroke="#FFFFFF" stroke-opacity="0.85" stroke-width="7.4"/><path d="{d}" fill="none" stroke="#F59E0B" stroke-width="5.2"/>')
    # the pole, and P (a pin seen from above: its head and its shadow)
    out.append('<circle cx="475" cy="190" r="4.4" fill="#FFFFFF" stroke="#2A4A8C" stroke-width="1"/>')
    px, py = 550.2, 233.4
    out.append(f'<defs><radialGradient id="g1pp" cx="0.35" cy="0.3" r="0.8"><stop offset="0" stop-color="#FFC9C2"/><stop offset="0.4" stop-color="#FF6A5E"/><stop offset="1" stop-color="#B8241F"/></radialGradient></defs>'
               f'<ellipse cx="{px + 3}" cy="{py + 3.4}" rx="6.6" ry="3.4" fill="#050B22" opacity="0.5"/>'
               f'<circle cx="{px}" cy="{py}" r="9" fill="#FF5B4D" opacity="0.55" filter="url(#g1rg)"/>'
               f'<circle cx="{px}" cy="{py}" r="5.8" fill="url(#g1pp)" stroke="#FFFFFF" stroke-width="1.5"/><circle cx="{px - 1.8}" cy="{py - 2}" r="1.6" fill="#FFFFFF" opacity="0.85"/>')
    return "".join(out)


def plate():
    bg = (f'<defs>{S.gradient("g1bg", [(0, "#0B1633"), (0.55, "#14274F"), (1, "#22407A")])}'
          f'<radialGradient id="g1v" cx="0.5" cy="0.5" r="0.75"><stop offset="0.5" stop-color="#000000" stop-opacity="0"/><stop offset="1" stop-color="#000000" stop-opacity="0.35"/></radialGradient></defs>'
          f'<rect x="0" y="0" width="640" height="360" fill="url(#g1bg)"/>' + H.stars(20, 90, 4, 4, 636, 356) + '<rect x="0" y="0" width="640" height="360" fill="url(#g1v)"/>'
          '<line x1="320" y1="20" x2="320" y2="345" stroke="#FFFFFF" stroke-opacity="0.22" stroke-width="1" stroke-dasharray="3 4"/>')
    c = S.callout
    calls = [
        c(1, 213, 29, 169, 53), c(2, 55, 250, 75, 190), c(2, 338, 282, 346, 220), c(3, 297.8, 110.6, 256.8, 88.6), c(3, 530.2, 299.4, 547.2, 238.4),
        c(4, 257, 224, 195, 172), c(5, 61, 46.6, 105, 86.6), c(5, 375, 120, 399.8, 146.6), c(6, 273.4, 30.1, 245.4, 77.1), c(7, 429, 329, 475, 305),
        c(8, 469, 250, 495, 208), c(9, 620.3, 288.9, 601.3, 246.9), c(10, 594.3, 185.3, 556.3, 222.3),
    ]
    return {
        "id": "fig-20-01-latitude-longitude",
        "replaces": "fig-20-01-latitude-longitude.svg",
        "book_file": "plate-20-01-latitude-longitude.jpg",
        "caption": "Figure 20-1. Latitude and longitude, and why a minute of latitude is a nautical mile",
        "desc": "Figure 20-1. Latitude and longitude, and why a minute of latitude is a nautical mile",
        "legend": [
            "The North Pole and the earth's axis.",
            "The equator.",
            "A position P.",
            "Latitude φ, at the earth's centre.",
            "The parallel of latitude through P.",
            "One minute of latitude along P's meridian (blue): 1 NM anywhere.",
            "The prime meridian.",
            "Longitude λ, at the pole, here east.",
            "One minute of longitude on the equator: 1 NM.",
            "The same minute on P's parallel: cos φ NM.",
        ],
        "canvas": [640, 360],
        "background": "pale",
        "reskin": {"svg": "fig-20-01-latitude-longitude.svg", "blank": True, "layers": [bg, left_globe(), right_globe(), "".join(calls)]},
    }
