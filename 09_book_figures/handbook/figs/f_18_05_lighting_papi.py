"""Figure 18-5. Runway and taxiway lights, and the four lights of the PAPI. The lights are best seen after dark, so both halves are drawn at dusk. Above, an aerial view of a
lit runway on the plain at night (figs/terrain.py): the approach lights with a crossbar, the green threshold lights, the white edge lights, the red end lights, the PAPI units with
their beams, a taxiway with blue edge lights, green centreline lights and a red stop bar; every lamp is a bulb with a halo. Below, the PAPI seen from the side at dusk: its beam
spreading to the approach in the five sectors, the five panels the pilot sees (four lit lamps each, white or red), and the aeroplane of the model on the glide path. The eight
callouts of the old figure (the PAPI one twice, as it had it) are kept, in the same order and meaning (figs/scene.py makes the callouts, figs/h_a2.py the lamps and the pavement)."""
from figs import h_a2 as H
from figs import scene as S
from figs import terrain

W, HT = 640, 450
TOP = 214                                    # the plan view is above this line, the side view below it
terrain.ensure("terrain-18-05", size=(W * 4, TOP * 4), seed=185, kind="night", features=("wadis", "tracks"), veil=0.14, soft=2.8)

U = "a185"
PAINT = "#E9E7DE"


def defs():
    return ("<defs>" + H.asphalt_filter(U + "as", seed=6, relief=0.8, tone=0.0) + H.lamp_defs(U + "l") + H.blur_filter(U + "bl", 1.6) + H.blur_filter(U + "bg", 3.2) + H.blur_filter(U + "bs", 0.7)
            + S.gradient(U + "sky", [(0, "#141C38"), (0.45, "#222E5E"), (0.8, "#34467F"), (1.0, "#4C5F98")])
            + S.gradient(U + "gr", [(0, "#4B3F3A"), (1, "#1E1A1F")])
            + S.gradient(U + "wash", [(0, "#07102A", 0.55), (1, "#07102A", 0.55)])
            + H.shadow_filter(U + "ps", 0.8, 1.4, 1.0, 0.45, "#050912")
            + f'<linearGradient id="{U}hs" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#6A7385"/><stop offset="0.5" stop-color="#3A4252"/><stop offset="1" stop-color="#1D222D"/></linearGradient>'
            + f'<linearGradient id="{U}rg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFE9B8" stop-opacity="0.34"/><stop offset="0.3" stop-color="#FFE9B8" stop-opacity="0"/><stop offset="0.7" stop-color="#FFE9B8" stop-opacity="0"/><stop offset="1" stop-color="#FFE9B8" stop-opacity="0.34"/></linearGradient>'
            + "</defs>")


# ------------------------------------------------------------------------------------------------------------------ the plan
def plan():
    out = []
    # the runway and the taxiway: asphalt in the dark (a blue wash over it), with a soft pool of light along the runway edges
    out.append(f'<rect x="150" y="76" width="450" height="60" fill="#444" filter="url(#{U}as)"/>')
    out.append(f'<rect x="404" y="136" width="36" height="64" fill="#444" filter="url(#{U}as)"/>')
    out.append(f'<rect x="150" y="76" width="450" height="60" fill="#06102A" opacity="0.26"/><rect x="404" y="136" width="36" height="64" fill="#06102A" opacity="0.26"/>')
    out.append(f'<rect x="150" y="76" width="450" height="60" fill="url(#{U}rg)"/>')
    # worn paint: the centreline, the threshold bars, quietly visible in the glow
    dash = "".join(f'<rect x="{x}" y="105" width="14" height="2"/>' for x in range(176, 590, 26))
    bars = "".join(f'<rect x="{x}" y="{y}" width="10" height="1.8"/>' for x in (156,) for y in (82, 86, 90, 94, 112, 116, 120, 124))
    out.append(f'<g fill="{PAINT}" opacity="0.30">{dash}{bars}</g>')
    out.append(f'<rect x="150" y="76" width="450" height="60" fill="none" stroke="#9FB0D6" stroke-opacity="0.28" stroke-width="0.6"/><rect x="404" y="136" width="36" height="64" fill="none" stroke="#9FB0D6" stroke-opacity="0.28" stroke-width="0.6"/>')
    return "".join(out)


def plan_lights():
    out = []
    L = U + "l"
    # approach lights: a row on the extended centreline and a crossbar
    for x in range(44, 141, 12):
        out.append(H.lamp(L, x, 106, 2.0, "white", 4.6))
    for y in (82, 90, 98, 114, 122, 130):
        out.append(H.lamp(L, 86, y, 2.0, "white", 4.6))
    # threshold lights (green) and runway end lights (red)
    for y in range(79, 129, 7):
        out.append(H.lamp(L, 150, y, 1.9, "green", 4.6))
        out.append(H.lamp(L, 600, y, 1.9, "red", 4.6))
    # runway edge lights (white), with a gap where the taxiway leaves
    for x in range(172, 563, 30):
        out.append(H.lamp(L, x, 76, 1.8, "white", 4.4))
    for x in list(range(172, 383, 30)) + list(range(472, 563, 30)):
        out.append(H.lamp(L, x, 136, 1.8, "white", 4.4))
    # the taxiway: blue edge lights, green centreline lights, a red stop bar across it
    for y in range(148, 197, 12):
        out.append(H.lamp(L, 403, y, 1.7, "blue", 4.6) + H.lamp(L, 441, y, 1.7, "blue", 4.6))
    for y in range(142, 197, 9):
        out.append(H.lamp(L, 422, y, 1.4, "green", 4.4))
    for x in range(408, 437, 7):
        out.append(H.lamp(L, x, 166, 1.6, "red", 4.6))
    return "".join(out)


def papi_plan():
    """The four PAPI units on the left of the runway near the touchdown point, each a dark box with a lens facing the approach and a soft beam running out to the left."""
    out = []
    L = U + "l"
    for y in (29, 40, 51, 62):
        out.append(f'<polygon points="{S.pts([(222, y + 4), (150, y - 8), (150, y + 16)])}" fill="url(#{U}cone)" />')
    for i, y in enumerate((29, 40, 51, 62)):
        out.append(f'<rect x="222" y="{y}" width="14" height="8" rx="1.4" fill="url(#{U}hs)" stroke="#0C1018" stroke-width="0.5" filter="url(#{U}ps)"/>'
                   f'<rect x="223" y="{y + 0.8}" width="12" height="1.8" rx="0.8" fill="#FFFFFF" opacity="0.22"/>')
        colour = "white" if i < 2 else "red"
        out.append(H.lamp(L, 221.4, y + 4, 2.1, colour if False else "white", 4.8))
    return "".join(out)


def cones_defs():
    return (f'<defs><linearGradient id="{U}cone" x1="1" y1="0" x2="0" y2="0"><stop offset="0" stop-color="#FFF2CC" stop-opacity="0.55"/><stop offset="0.5" stop-color="#FFF2CC" stop-opacity="0.16"/>'
            f'<stop offset="1" stop-color="#FFF2CC" stop-opacity="0"/></linearGradient></defs>')


def beams_plan_fix():
    return ""


def plane_plan():
    plane = {"name": "sprite-top-night", "at": [26, 106], "width": 42, "angle": 90, "tint": "#9FB0D2", "tint_strength": 0.55}
    L = U + "l"
    lights = (H.lamp(L, 26, 85.6, 1.5, "red", 4.6) + H.lamp(L, 26, 126.4, 1.5, "green", 4.6) + H.lamp(L, 7, 106, 1.3, "white", 4.0))
    return plane, lights


# ------------------------------------------------------------------------------------------------------------------ the side view
GX = 176                                         # where the sectors are cut off on the left
APEX = (598, 429)
LINES = [385.4, 355.2, 324.3, 292.2]            # their heights at GX (the boundaries of the sectors: 2.5, 2.8, 3.2, 3.5 degrees)


def at_x(y_at_gx, x):
    """The height of a line from the apex that is at y_at_gx on the left edge, at x."""
    return APEX[1] + (y_at_gx - APEX[1]) * (APEX[0] - x) / (APEX[0] - GX)


def side():
    out = []
    top = TOP
    out.append(f'<rect x="0" y="{top}" width="{W}" height="{HT - top}" fill="url(#{U}sky)"/>')
    # distant hills against the afterglow, then the ground
    ridge = S.ridge(5, 0, W, 424, 12, step=4.0, peaks=0.5)
    out.append(S.land_layer(U + "h1", ridge, 440, ("#1E2547", "#2B3258"), rim=False, haze=0.25, haze_colour="#6C7DB5"))
    out.append(f'<rect x="0" y="429" width="{W}" height="{HT - 429}" fill="url(#{U}gr)"/><line x1="0" y1="429.5" x2="{W}" y2="429.5" stroke="#8C6E5A" stroke-opacity="0.6" stroke-width="0.8"/>')
    # the runway edge-on at the right, with its lights
    out.append(f'<rect x="560" y="427" width="80" height="6" fill="#333B49"/><rect x="560" y="427" width="80" height="1.4" fill="#7A8497" opacity="0.8"/>')
    return "".join(out)


def sectors():
    """The beam of the PAPI in its five sectors: each a wedge from the unit to the left edge, brightest at the unit and fading with distance, with soft edges."""
    out = []
    bounds = [248.0] + LINES[::-1] + [429.0]            # from the top: above 3.5, 3.5-3.2, 3.2-2.8, 2.8-2.5, below 2.5 (all at GX)
    cols = [("#FFF6DA", 0.62), ("#FFF1DE", 0.60), ("#FFD6CE", 0.68), ("#FF8272", 0.70), ("#FF2D22", 0.74)]
    defs = [f'<linearGradient id="{U}f{i}" x1="1" y1="0" x2="0" y2="0"><stop offset="0" stop-color="{c}" stop-opacity="{o}"/><stop offset="0.55" stop-color="{c}" stop-opacity="{o * 0.42}"/><stop offset="1" stop-color="{c}" stop-opacity="0"/></linearGradient>'
            for i, (c, o) in enumerate(cols)]
    out.append("<defs>" + "".join(defs) + "</defs>")
    out.append(f'<g filter="url(#{U}bs)">')
    for i in range(5):
        a, b = bounds[i], bounds[i + 1]
        poly = [APEX, (GX, a), (GX, b)]
        out.append(f'<polygon points="{S.pts(poly)}" fill="url(#{U}f{i})"/>')
    out.append("</g>")
    # the on-slope sector is the one the pilot is meant to fly in: a light rim along it
    for y in LINES:
        out.append(f'<line x1="{APEX[0]}" y1="{APEX[1]}" x2="{GX}" y2="{y}" stroke="#FFFFFF" stroke-opacity="0.85" stroke-width="1.0" stroke-dasharray="5 4"/>')
    return "".join(out)


def papi_side():
    """The PAPI unit at the foot of the beam: a low housing on the ground with its lens glowing towards the approach."""
    x, y = 593, 421
    out = [f'<defs>{H.shadow_filter(U + "pu", 1.0, 1.2, 1.0, 0.5, "#05070E")}</defs>',
           f'<rect x="{x}" y="{y}" width="14" height="8" rx="1.6" fill="url(#{U}hs)" stroke="#0C1018" stroke-width="0.5" filter="url(#{U}pu)"/>',
           f'<rect x="{x + 0.8}" y="{y + 0.6}" width="12.4" height="1.8" rx="0.8" fill="#FFFFFF" opacity="0.22"/>',
           H.lamp(U + "l", x - 0.6, y + 4, 2.2, "white", 5.5)]
    return "".join(out)


def panel(y, lamps, bold=False, label=""):
    """One panel of the pilot's view: a housing with four lamps (True white, False red), and its angle at the left."""
    x, w, h = 96, 64, 20
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="url(#{U}hs)" stroke="#0C1018" stroke-width="0.8" filter="url(#{U}ps)"/>',
           f'<rect x="{x + 1.5}" y="{y + 1}" width="{w - 3}" height="3" rx="1.5" fill="#FFFFFF" opacity="0.18"/>']
    for i, white in enumerate(lamps):
        cx, cy = x + 11 + 14 * i, y + h / 2
        out.append(H.lamp(U + "l", cx, cy, 4.6, "white" if white else "red", 2.8))
    out.append(H.glyph_text(label, 62, y + h / 2, 10.0 if not bold else 11.0, "#EEF1F8", anchor="end", stroke="#EEF1F8" if bold else None, stroke_width=0.5 if bold else 0))
    return "".join(out)


def panels():
    out = []
    for y, lamps, label, bold in ((260.2, (1, 1, 1, 1), "3.5°", False), (298.3, (1, 1, 1, 0), "3.2°", False), (329.8, (1, 1, 0, 0), "3°", True), (360.3, (1, 0, 0, 0), "2.8°", False), (401.7, (0, 0, 0, 0), "2.5°", False)):
        out.append(panel(y, lamps, bold, label))
    return "".join(out)


def aeroplane_side():
    return {"name": "sprite-side", "at": [380, 379.2], "width": 46, "angle": 4, "tint": "#B8C4E0", "tint_strength": 0.45}


def callouts():
    c = S.callout
    return "".join([
        c(1, 86, 54, 86, 80), c(2, 150, 154, 150, 130), c(3, 320, 158, 322, 138), c(4, 600, 154, 600, 130),
        c(5, 262, 46, 238, 46), c(6, 470, 190, 443, 184), c(7, 376, 176, 421, 178), c(8, 470, 154, 438, 166),
        c(5, 598, 396, 598, 420)])


def layers():
    plane, plane_lights = plane_plan()
    return [{"name": "terrain-18-05", "at": [W / 2, TOP / 2], "width": W}, defs(), cones_defs(), plan(), papi_plan(), plan_lights(), plane, plane_lights,
            f'<line x1="0" y1="{TOP}" x2="{W}" y2="{TOP}" stroke="#FFFFFF" stroke-opacity="0.35" stroke-width="1"/>',
            side(), sectors(), H.grain(U + "gn", 0, TOP, W, HT - TOP, 0.045, 1.1, 5), papi_side(), aeroplane_side(), panels(), callouts()]


def plate():
    return {
        "id": "fig-18-05-lighting-papi",
        "replaces": "fig-18-05-lighting-papi.svg",
        "book_file": "plate-18-05-lighting-papi.jpg",
        "caption": "Figure 18-5. Runway and taxiway lights, and the four lights of the PAPI",
        "desc": "Figure 18-5. Runway and taxiway lights, and the four lights of the PAPI",
        "legend": [
            "Approach lights, white, along the extended centreline, here with one crossbar.",
            "Threshold lights, green.",
            "Runway edge lights, white.",
            "Runway end lights, red.",
            "PAPI: four units in a row on the left of the runway, near the touchdown point.",
            "Taxiway edge lights, blue.",
            "Taxiway centreline lights, green.",
            "Stop bar, red, across the taxiway at the runway-holding position.",
        ],
        "canvas": [W, HT],
        "background": "pale",
        "reskin": {"svg": "fig-18-05-lighting-papi.svg", "blank": True, "layers": layers()},
    }
