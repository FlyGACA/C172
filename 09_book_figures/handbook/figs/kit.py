"""Helpers shared by the figure modules (not a figure itself: plates_spec.py only loads f_*.py)."""

BEZEL_M = 0.093          # the outer diameter of an instrument's bezel in the model, metres


def dial_layer(name, inst, centre, diameter, readings=None, margin=9, px=5, samples=48, shadow=True):
    """A render of one instrument on its own (bezel, dial, pointers, no panel), as a layer of a composite plate: its bezel is `diameter`
    canvas units across and centred on `centre` = [x, y] of the canvas; `readings` is what the instrument shows (render_plate.py "pose").
    The anchors `c` (the centre) and `rim_*` (the outer edge of the bezel at the compass points of the dial) are for the plate's overlays."""
    size = diameter + 2 * margin
    anchors = {"c": {"dial": inst, "angle": 0, "radius": 0}}
    for tag, angle in (("n", 0), ("ne", 45), ("e", 90), ("se", 135), ("s", 180), ("sw", 225), ("w", 270), ("nw", 315)):
        anchors["rim_" + tag] = {"dial": inst, "angle": angle, "radius": 1.18}
    layer = {
        "name": name,
        "box": [centre[0] - size / 2, centre[1] - size / 2, size, size],
        "render": {
            "camera": {"view": "panel", "target": {"part": f"PANEL.{inst}.bezel", "at": [0.5, 0.5, 0.5]}, "width": BEZEL_M * size / diameter,
                       "azimuth": 0, "elevation": 0, "distance": 0.3},
            "size": [round(size * px), round(size * px)],
            "light": "panel",
            "show": [f"PANEL.{inst}.*"],
            "instrument_glass": "clear",
            "pose": readings or {},
            "fine_textures": True,
            "samples": samples,
            "smooth": [{"parts": [f"PANEL.{inst}.bezel"], "angle": 35}],
            "anchors": anchors,
        },
    }
    if shadow:
        layer["shadow"] = {"dx": 0, "dy": 2.6, "blur": 4.0, "opacity": 0.30}
    return layer


def ring(x, y, r, colour="#1D4ED8", width=3.2):
    """A ring round something, as markup for an "svg" overlay."""
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="none" stroke="#FFFFFF" stroke-width="{width + 3.4}" opacity=".92"/><circle cx="{x}" cy="{y}" r="{r}" fill="none" stroke="{colour}" stroke-width="{width}"/>'


def arc_arrow(cx, cy, r, a0, a1, colour="#1D4ED8", width=3.2):
    """An arrow along a circle of radius r about (cx, cy), from the angle a0 to a1 (degrees clockwise from straight up), as markup."""
    import math
    p0 = (cx + r * math.sin(math.radians(a0)), cy - r * math.cos(math.radians(a0)))
    p1 = (cx + r * math.sin(math.radians(a1)), cy - r * math.cos(math.radians(a1)))
    sign = 1 if a1 > a0 else -1
    t = (math.cos(math.radians(a1)) * sign, math.sin(math.radians(a1)) * sign)            # the way the arc is going at its end
    n = (-t[1], t[0])
    tip = (p1[0] + t[0] * 5, p1[1] + t[1] * 5)
    head = f"{tip[0] + t[0] * 9:.1f},{tip[1] + t[1] * 9:.1f} {tip[0] + n[0] * 7:.1f},{tip[1] + n[1] * 7:.1f} {tip[0] - n[0] * 7:.1f},{tip[1] - n[1] * 7:.1f}"
    sweep = 1 if sign > 0 else 0
    path = f"M{p0[0]:.1f},{p0[1]:.1f} A{r},{r} 0 0 {sweep} {p1[0]:.1f},{p1[1]:.1f}"
    return (f'<path d="{path}" fill="none" stroke="#FFFFFF" stroke-width="{width + 3.6}" stroke-linecap="round" opacity=".9"/>'
            f'<path d="{path}" fill="none" stroke="{colour}" stroke-width="{width}" stroke-linecap="round"/>'
            f'<polygon points="{head}" fill="{colour}" stroke="#FFFFFF" stroke-width="1.6" stroke-linejoin="round"/>')


def power_bar(x, y, w, h, fraction, ink="#1F2A44", fill="#8B93A3"):
    """A bar for the power set: an outline with a grey fill rising from the bottom to `fraction` of its height, as markup."""
    inner = (h - 6) * fraction
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="3" fill="#FFFFFF" stroke="{ink}" stroke-width="2.4"/>'
            + (f'<rect x="{x + 3}" y="{y + h - 3 - inner:.1f}" width="{w - 6}" height="{inner:.1f}" rx="1.5" fill="{fill}"/>' if fraction > 0 else ""))
