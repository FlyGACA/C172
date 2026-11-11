"""Instrument faces and panel placards drawn from data/instruments.json (POH-referenced scales).
Atlas layout (dials.png, four columns of four square cells): see CELLS. Angles: clockwise from 12 o'clock as the pilot sees them."""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(os.path.dirname(os.path.dirname(HERE)), "data", "instruments.json")
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
CELLS = ["ASI", "AI_BALL", "AI_MASK", "ALT", "TC", "DG_CARD", "DG_MASK", "VSI", "TACH", "SUCTION", "CLOCK", "VOR", "ADF"]
COLS, ROWS = 4, 4
COLORS = {"white": (235, 235, 235), "green": (40, 170, 70), "yellow": (240, 200, 40), "red": (220, 30, 30)}

def cell_uv(name):
    i = CELLS.index(name); c, r = i % COLS, i // COLS
    return (c / COLS, 1 - (r + 1) / ROWS, (c + 1) / COLS, 1 - r / ROWS)     # u0, v0, u1, v1 (v up)

def value_to_angle(spec, v):
    m = spec["map"]
    if v <= m[0][0]: return m[0][1]
    if v >= m[-1][0]: return m[-1][1]
    for (v0, a0), (v1, a1) in zip(m, m[1:]):
        if v0 <= v <= v1:
            return a0 + (a1 - a0) * (v - v0) / (v1 - v0)
    return m[-1][1]

def _pol(cx, cy, r, ang_deg):
    a = math.radians(ang_deg - 90)
    return (cx + r * math.cos(a), cy + r * math.sin(a))

def draw_dial(img, box, spec, title=None, subtitle=None, font_scale=1.0):
    from PIL import Image, ImageDraw, ImageFont
    x0, y0, x1, y1 = box
    S = x1 - x0
    cx, cy, R = (x0 + x1) / 2, (y0 + y1) / 2, S * 0.47
    d = ImageDraw.Draw(img, "RGBA")
    d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=(12, 12, 13, 255))
    # arcs
    for arc in spec.get("arcs", []):
        a0 = value_to_angle(spec, arc["from"]); a1 = value_to_angle(spec, arc["to"])
        ro = R * (0.97 if arc.get("band") == "outer" else 0.84); ri = R * (0.90 if arc.get("band") == "outer" else 0.78)
        d.pieslice([cx - ro, cy - ro, cx + ro, cy + ro], a0 - 90, a1 - 90, fill=COLORS[arc["color"]])
        d.pieslice([cx - ri, cy - ri, cx + ri, cy + ri], a0 - 91, a1 - 89, fill=(12, 12, 13, 255))
    # ticks
    t = spec.get("ticks", {})
    minor = []
    if "minor_step" in t:
        v = t.get("minor_from", spec["min"])
        while v <= spec["max"] + 1e-9:
            minor.append(v); v += t["minor_step"]
    for v in minor:
        a = value_to_angle(spec, v)
        d.line([_pol(cx, cy, R * 0.90, a), _pol(cx, cy, R * 0.84, a)], fill=(230, 230, 230), width=max(1, int(S * 0.006)))
    for v in t.get("major", []):
        a = value_to_angle(spec, v)
        d.line([_pol(cx, cy, R * 0.92, a), _pol(cx, cy, R * 0.78, a)], fill=(245, 245, 245), width=max(2, int(S * 0.012)))
    for rl in spec.get("redlines", []):
        a = value_to_angle(spec, rl["value"])
        d.line([_pol(cx, cy, R * 0.98, a), _pol(cx, cy, R * 0.80, a)], fill=COLORS["red"], width=max(2, int(S * 0.018)))
    f = ImageFont.truetype(FONT_BOLD, int(S * 0.085 * font_scale))
    for v in spec.get("labels", []):
        a = value_to_angle(spec, v)
        txt = spec.get("label_text", {}).get(str(v)) or spec.get("label_text", {}).get(str(int(v)) if float(v).is_integer() else str(v))
        if txt is None:
            val = abs(v) if spec.get("label_abs") else v
            val = val / spec["label_divisor"] if spec.get("label_divisor") else val
            txt = str(int(val)) if float(val).is_integer() else str(val)
        px, py = _pol(cx, cy, R * 0.64, a)
        d.text((px, py), txt, fill=(240, 240, 240), font=f, anchor="mm")
    fs = ImageFont.truetype(FONT, int(S * 0.055 * font_scale))
    if title:
        d.text((cx, cy - R * 0.33), title, fill=(220, 220, 220), font=fs, anchor="mm")
    if subtitle:
        d.text((cx, cy + R * 0.36), subtitle, fill=(200, 200, 200), font=fs, anchor="mm")

def dials_atlas(path, size=2048):
    from PIL import Image, ImageDraw, ImageFont
    with open(DATA, encoding="utf-8") as f:
        INSTR = json.load(f)["instruments"]
    cs = size // ROWS
    img = Image.new("RGBA", (cs * COLS, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img, "RGBA")
    def box(name):
        i = CELLS.index(name); c, r = i % COLS, i // COLS
        return (c * cs, r * cs, (c + 1) * cs, (r + 1) * cs)
    draw_dial(img, box("ASI"), INSTR["ASI"], "AIRSPEED", "KNOTS")
    alt = dict(INSTR["ALT"]); draw_dial(img, box("ALT"), alt, "ALTITUDE", "")
    # Kollsman window on the altimeter (3 o'clock)
    x0, y0, x1, y1 = box("ALT"); cx, cy = (x0 + x1) / 2, (y0 + y1) / 2; R = cs * 0.47
    d.rectangle([cx + R * 0.42, cy - R * 0.1, cx + R * 0.74, cy + R * 0.1], fill=(30, 30, 30), outline=(120, 120, 120))
    d.text((cx + R * 0.58, cy), "29.92", fill=(230, 230, 230), font=ImageFont.truetype(FONT, int(cs * 0.06)), anchor="mm")
    draw_dial(img, box("VSI"), INSTR["VSI"], "VERTICAL SPEED", "100 FEET PER MINUTE")
    draw_dial(img, box("TACH"), INSTR["TACH"], "RPM", "X 100")
    x0, y0, x1, y1 = box("TACH"); cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    d.rectangle([cx - R * 0.28, cy + R * 0.45, cx + R * 0.28, cy + R * 0.62], fill=(240, 240, 240))
    d.text((cx, cy + R * 0.535), "0 4 2 3 1 . 6", fill=(20, 20, 20), font=ImageFont.truetype(FONT_BOLD, int(cs * 0.05)), anchor="mm")
    draw_dial(img, box("SUCTION"), INSTR["SUCTION"], "SUCTION", "IN. HG", font_scale=1.25)
    clock = {"map": [[0, 0], [12, 360]], "min": 0, "max": 12, "ticks": {"major": list(range(0, 12)), "minor_step": 0.2, "minor_from": 0}, "labels": list(range(1, 13)), "label_text": {}}
    draw_dial(img, box("CLOCK"), clock, "", "")
    # ---- turn coordinator: face with L/R marks, wings symbol drawn by the needle mesh
    tc = {"map": [[-1, -20], [1, 20]], "min": -1, "max": 1, "ticks": {"major": [-1, 1]}, "labels": [], "arcs": []}
    draw_dial(img, box("TC"), tc, "TURN COORDINATOR", "2 MIN")
    x0, y0, x1, y1 = box("TC"); cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    f = ImageFont.truetype(FONT_BOLD, int(cs * 0.08))
    d.text((cx - R * 0.78, cy + R * 0.25), "L", fill=(240, 240, 240), font=f, anchor="mm"); d.text((cx + R * 0.78, cy + R * 0.25), "R", fill=(240, 240, 240), font=f, anchor="mm")
    d.text((cx, cy + R * 0.62), "NO PITCH INFORMATION", fill=(200, 200, 200), font=ImageFont.truetype(FONT, int(cs * 0.04)), anchor="mm")
    # inclinometer tube
    d.arc([cx - R * 0.5, cy + R * 0.25, cx + R * 0.5, cy + R * 0.75], 200, 340, fill=(200, 200, 200), width=max(2, cs // 60))
    # ---- attitude indicator ball (sky/ground with pitch ladder) and mask
    x0, y0, x1, y1 = box("AI_BALL"); cx, cy = (x0 + x1) / 2, (y0 + y1) / 2; Rb = cs * 0.49
    d.ellipse([cx - Rb, cy - Rb, cx + Rb, cy + Rb], fill=(120, 80, 40, 255))
    d.pieslice([cx - Rb, cy - Rb, cx + Rb, cy + Rb], 180, 360, fill=(70, 140, 220, 255))
    d.line([cx - Rb, cy, cx + Rb, cy], fill=(250, 250, 250), width=max(2, cs // 120))
    for i, deg in enumerate((5, 10, 15, 20)):
        w = Rb * (0.18 if deg % 10 else 0.32); yoff = Rb * 0.065 * deg / 5
        for sgn in (-1, 1):
            d.line([cx - w, cy + sgn * yoff, cx + w, cy + sgn * yoff], fill=(250, 250, 250), width=max(1, cs // 200))
            if deg % 10 == 0:
                d.text((cx + w + cs * 0.03, cy + sgn * yoff), str(deg), fill=(250, 250, 250), font=ImageFont.truetype(FONT, int(cs * 0.045)), anchor="lm")
    # bank scale on the ball
    for b in (-60, -45, -30, -20, -10, 0, 10, 20, 30, 45, 60):
        d.line([_pol(cx, cy, Rb * 0.98, b), _pol(cx, cy, Rb * (0.86 if b % 30 == 0 else 0.92), b)], fill=(250, 250, 250), width=max(2, cs // 100))
    x0, y0, x1, y1 = box("AI_MASK"); cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    # transparent centre, black ring, orange aeroplane symbol and bank pointer
    d.ellipse([cx - Rb, cy - Rb, cx + Rb, cy + Rb], fill=(12, 12, 13, 255))
    d.ellipse([cx - Rb * 0.86, cy - Rb * 0.86, cx + Rb * 0.86, cy + Rb * 0.86], fill=(0, 0, 0, 0))
    d.polygon([_pol(cx, cy, Rb * 0.86, 0), (cx - cs * 0.02, cy - Rb * 0.98), (cx + cs * 0.02, cy - Rb * 0.98)], fill=(255, 140, 0, 255))
    d.rectangle([cx - Rb * 0.45, cy - cs * 0.008, cx - Rb * 0.12, cy + cs * 0.008], fill=(255, 140, 0, 255))
    d.rectangle([cx + Rb * 0.12, cy - cs * 0.008, cx + Rb * 0.45, cy + cs * 0.008], fill=(255, 140, 0, 255))
    d.ellipse([cx - cs * 0.02, cy - cs * 0.02, cx + cs * 0.02, cy + cs * 0.02], fill=(255, 140, 0, 255))
    # ---- directional gyro card and mask
    x0, y0, x1, y1 = box("DG_CARD"); cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    d.ellipse([cx - Rb, cy - Rb, cx + Rb, cy + Rb], fill=(12, 12, 13, 255))
    fcard = ImageFont.truetype(FONT_BOLD, int(cs * 0.09))
    for deg in range(0, 360, 5):
        ln = Rb * (0.80 if deg % 30 == 0 else 0.86 if deg % 10 == 0 else 0.90)
        d.line([_pol(cx, cy, Rb * 0.96, deg), _pol(cx, cy, ln, deg)], fill=(240, 240, 240), width=max(1, cs // 150))
        if deg % 30 == 0:
            lbl = {0: "N", 90: "E", 180: "S", 270: "W"}.get(deg, str(deg // 10))
            px, py = _pol(cx, cy, Rb * 0.66, deg)
            tmp = Image.new("RGBA", (cs // 5, cs // 5), (0, 0, 0, 0))
            ImageDraw.Draw(tmp).text((cs // 10, cs // 10), lbl, fill=(240, 240, 240), font=fcard, anchor="mm")
            tmp = tmp.rotate(-deg, Image.BICUBIC)
            img.alpha_composite(tmp, (int(px - cs // 10), int(py - cs // 10)))
    x0, y0, x1, y1 = box("DG_MASK"); cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    d.ellipse([cx - Rb, cy - Rb, cx + Rb, cy + Rb], fill=(12, 12, 13, 255))
    d.ellipse([cx - Rb * 0.97, cy - Rb * 0.97, cx + Rb * 0.97, cy + Rb * 0.97], fill=(0, 0, 0, 0))
    d.polygon([(cx, cy - Rb * 0.95), (cx - cs * 0.02, cy - Rb * 0.80), (cx + cs * 0.02, cy - Rb * 0.80)], fill=(255, 140, 0, 255))
    # aeroplane silhouette
    d.rectangle([cx - cs * 0.012, cy - Rb * 0.3, cx + cs * 0.012, cy + Rb * 0.3], fill=(255, 140, 0, 255))
    d.rectangle([cx - Rb * 0.32, cy - cs * 0.012, cx + Rb * 0.32, cy + cs * 0.012], fill=(255, 140, 0, 255))
    d.rectangle([cx - Rb * 0.12, cy + Rb * 0.22, cx + Rb * 0.12, cy + Rb * 0.26], fill=(255, 140, 0, 255))
    # ---- omni course indicator and ADF bearing indicator (POH Figure 7-2 shows both). A plain face of each kind:
    # an azimuth card, a pointer or a deviation bar. They are not driven by the simulation, which has no radio aids.
    def azimuth_card(cx, cy, r_out, r_num, font):
        for deg in range(0, 360, 5):
            inner = r_out * (0.84 if deg % 30 == 0 else 0.89 if deg % 10 == 0 else 0.93)
            d.line([_pol(cx, cy, r_out, deg), _pol(cx, cy, inner, deg)], fill=(235, 235, 235), width=max(1, cs // (130 if deg % 10 == 0 else 200)))
            if deg % 30 == 0:
                lbl = {0: "N", 90: "E", 180: "S", 270: "W"}.get(deg, str(deg // 10))
                px, py = _pol(cx, cy, r_num, deg)
                tmp = Image.new("RGBA", (cs // 5, cs // 5), (0, 0, 0, 0))
                ImageDraw.Draw(tmp).text((cs // 10, cs // 10), lbl, fill=(235, 235, 235), font=font, anchor="mm")
                img.alpha_composite(tmp.rotate(-deg, Image.BICUBIC), (int(px - cs // 10), int(py - cs // 10)))
    fnav = ImageFont.truetype(FONT_BOLD, int(cs * 0.062)); fsm = ImageFont.truetype(FONT, int(cs * 0.042))
    x0, y0, x1, y1 = box("VOR"); cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=(12, 12, 13, 255))
    azimuth_card(cx, cy, R * 0.98, R * 0.74, fnav)
    d.ellipse([cx - R * 0.60, cy - R * 0.60, cx + R * 0.60, cy + R * 0.60], fill=(18, 18, 19, 255), outline=(70, 70, 72), width=max(1, cs // 250))
    for k in range(-5, 6):                                   # the row of dots the deviation bar is read against
        if k:
            rr = cs * 0.009
            d.ellipse([cx + k * R * 0.095 - rr, cy - rr, cx + k * R * 0.095 + rr, cy + rr], fill=(235, 235, 235))
    d.ellipse([cx - R * 0.05, cy - R * 0.05, cx + R * 0.05, cy + R * 0.05], outline=(235, 235, 235), width=max(1, cs // 200))
    d.line([cx, cy - R * 0.52, cx, cy + R * 0.52], fill=(250, 250, 250), width=max(2, cs // 110))      # the deviation bar, centred
    d.polygon([(cx + R * 0.30, cy - R * 0.36), (cx + R * 0.44, cy - R * 0.36), (cx + R * 0.37, cy - R * 0.47)], fill=(235, 235, 235))      # TO
    d.text((cx + R * 0.37, cy - R * 0.27), "TO", fill=(235, 235, 235), font=fsm, anchor="mm")
    d.text((cx - R * 0.36, cy + R * 0.40), "NAV", fill=(200, 200, 200), font=fsm, anchor="mm")
    d.polygon([(cx, cy - R * 0.60), (cx - cs * 0.022, cy - R * 0.50), (cx + cs * 0.022, cy - R * 0.50)], fill=(240, 200, 40))            # the course index
    x0, y0, x1, y1 = box("ADF"); cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=(12, 12, 13, 255))
    azimuth_card(cx, cy, R * 0.98, R * 0.74, fnav)
    bearing = 38.0                                           # the pointer: a bar with an arrowhead, through the centre
    d.line([_pol(cx, cy, R * 0.56, bearing + 180), _pol(cx, cy, R * 0.46, bearing)], fill=(240, 200, 40), width=max(3, cs // 70))
    tip, la, lb = _pol(cx, cy, R * 0.60, bearing), _pol(cx, cy, R * 0.44, bearing - 9), _pol(cx, cy, R * 0.44, bearing + 9)
    d.polygon([tip, la, lb], fill=(240, 200, 40))
    d.rectangle([cx - cs * 0.008, cy - R * 0.16, cx + cs * 0.008, cy + R * 0.16], fill=(235, 235, 235))      # a small aeroplane at the centre
    d.rectangle([cx - R * 0.16, cy - cs * 0.008, cx + R * 0.16, cy + cs * 0.008], fill=(235, 235, 235))
    d.text((cx, cy + R * 0.34), "ADF", fill=(200, 200, 200), font=fsm, anchor="mm")
    d.polygon([(cx, cy - R * 0.985), (cx - cs * 0.02, cy - R * 0.90), (cx + cs * 0.02, cy - R * 0.90)], fill=(240, 240, 240))
    img.save(path)

# ---------------------------------------------------------------------------------------------- radios and small plates
# panel_misc.png, 2048 px square. Left half: the faces of the avionics stack, one under the other, drawn with square
# texels (1024 px across the 165 mm of the stack). Right half: the small plates and the small indicators.
RADIO_W = 0.165                       # width of the avionics stack (m)
RADIO_ROWS = [("COMNAV1", 384), ("COMNAV2", 384), ("XPDR", 288), ("ADF", 288), ("AUDIO", 192), ("MARKER", 160)]      # height in texels

def radio_height(region):
    """Height of a radio's face (m)."""
    return dict(RADIO_ROWS)[region] * RADIO_W / 1024.0

# Knobs that stand on the faces: (u, v, radius m, kind). u, v: fractions of the face from its top left corner as the
# pilot sees it. kind: "dual" two knobs one on the other (frequency), "knob" a plain knob, "bat" the lever of a small switch.
_NAVCOM_KNOBS = [(0.095, 0.74, 0.0060, "knob"), (0.385, 0.60, 0.0100, "dual"), (0.595, 0.74, 0.0060, "knob"), (0.885, 0.60, 0.0100, "dual")]
RADIO_KNOBS = {
    "COMNAV1": _NAVCOM_KNOBS, "COMNAV2": _NAVCOM_KNOBS,
    "XPDR": [(0.115, 0.54, 0.0085, "knob")] + [(0.361 + 0.085 * i, 0.76, 0.0046, "knob") for i in range(4)],
    "ADF": [(0.800, 0.54, 0.0100, "dual"), (0.420, 0.58, 0.0072, "knob"), (0.150, 0.77, 0.0050, "knob")],
    "AUDIO": [(0.09 + 0.117 * i, 0.40, 0.0021, "bat") for i in range(8)],
    "MARKER": [(0.80, 0.56, 0.0021, "bat")],
}

# The small indicators near the left edge of the panel (oil temperature and pressure, fuel quantity, ammeter): a
# rectangular face each, the pointer pivoted below the middle and sweeping a scale across the top.
RECT_W, RECT_H = 0.030, 0.038         # face of one indicator (m)
RECT_PIVOT = 0.0115                   # the pointer's pivot lies this far below the middle of the face
RECT_COVER = 0.0072                   # the lower part of the face, from this far below the middle down, lies behind a cover

def rect_radius(key):
    """Radius of the scale of a small indicator, from the pointer's pivot (m): shorter where the sweep is wider."""
    return 0.0150 if key == "AMMETER" else 0.0172

_MISC_PX = {   # x, y, width, height in texels (y down)
    "FLAP_IND": (1032, 8, 160, 500), "LOW_VOLT": (1208, 8, 256, 136), "HOURMETER": (1208, 160, 320, 154), "IGNITION": (1544, 8, 320, 320),
    "PLACARD_SPEED": (1208, 336, 832, 208), "COMPASS": (1032, 820, 512, 200),
    "G_FUEL_L": (1032, 560, 190, 240), "G_FUEL_R": (1236, 560, 190, 240), "G_OIL_T": (1440, 560, 190, 240), "G_OIL_P": (1644, 560, 190, 240),
    "G_AMMETER": (1848, 560, 190, 240),
}
MISC = {}      # name -> (u0, v0, u1, v1) regions of panel_misc.png (v up)
_row = 0
for _name, _h in RADIO_ROWS:
    MISC[_name] = (0.0, 1 - (_row + _h) / 2048.0, 0.5, 1 - _row / 2048.0); _row += _h
for _name, (_x, _y, _w, _h) in _MISC_PX.items():
    MISC[_name] = (_x / 2048.0, 1 - (_y + _h) / 2048.0, (_x + _w) / 2048.0, 1 - _y / 2048.0)

def panel_misc_atlas(path, size=2048):
    """The faces of the radios, the small indicators and the small plates of the panel. The radios are plain faces of
    their kind, with the small readouts, legends and buttons such sets have; they copy no maker's set."""
    from PIL import Image, ImageDraw, ImageFont
    with open(DATA, encoding="utf-8") as f:
        INSTR = json.load(f)["instruments"]
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    k = size / 2048.0                       # texels to a texel of the layout above
    m = 1024.0 * k / RADIO_W                # texels to the metre on the radio faces
    FACE, EDGE, LEG, DIGIT = (25, 25, 27), (66, 66, 68), (214, 214, 210), (240, 226, 190)
    def px(region):
        u0, v0, u1, v1 = MISC[region]
        return (int(round(u0 * size)), int(round((1 - v1) * size)), int(round(u1 * size)), int(round((1 - v0) * size)))
    def font(h, bold=False):
        return ImageFont.truetype(FONT_BOLD if bold else FONT, max(6, int(h)))
    def face(region):
        x0, y0, x1, y1 = px(region)
        d.rectangle([x0, y0, x1, y1], fill=FACE)
        d.rectangle([x0 + 4 * k, y0 + 4 * k, x1 - 4 * k, y1 - 4 * k], outline=EDGE, width=max(1, int(2 * k)))
        for sx, sy in ((x0 + 16 * k, y0 + 16 * k), (x1 - 16 * k, y0 + 16 * k), (x0 + 16 * k, y1 - 16 * k), (x1 - 16 * k, y1 - 16 * k)):      # the screws of the face
            d.ellipse([sx - 6.5 * k, sy - 6.5 * k, sx + 6.5 * k, sy + 6.5 * k], fill=(56, 56, 58), outline=(94, 94, 96))
            d.line([sx - 4.5 * k, sy, sx + 4.5 * k, sy], fill=(18, 18, 18), width=max(1, int(2 * k)))
        return x0, y0, x1 - x0, y1 - y0
    def window(x, y, w, h, text, colour=DIGIT):
        d.rectangle([x, y, x + w, y + h], fill=(5, 5, 6), outline=(88, 88, 90), width=max(1, int(2 * k)))
        d.text((x + w / 2, y + h / 2), text, fill=colour, font=font(min(h * 0.70, w / (0.68 * len(text) + 0.4)), True), anchor="mm")
    def legend(x, y, text, h=17.0, colour=LEG):
        d.text((x, y), text, fill=colour, font=font(h * k), anchor="mm")
    def seats(region, x0, y0, w, h):
        """A dark seat under each knob of the face, a little larger than the knob."""
        for u, v, r, kind in RADIO_KNOBS[region]:
            rr = r * m + (5 if kind != "bat" else 9) * k
            d.ellipse([x0 + u * w - rr, y0 + v * h - rr, x0 + u * w + rr, y0 + v * h + rr], fill=(12, 12, 13), outline=(72, 72, 74), width=max(1, int(2 * k)))
    def navcom(region, com, nav):
        x0, y0, w, h = face(region)
        for half, (text, name) in enumerate(((com, "COMM"), (nav, "NAV"))):
            hx = x0 + w * 0.5 * half
            window(hx + w * 0.045, y0 + h * 0.16, w * 0.245, h * 0.27, text)
            legend(hx + w * 0.167, y0 + h * 0.085, name, 18)
            legend(hx + w * 0.095, y0 + h * 0.925, "OFF   VOL" if half == 0 else "VOL   ID", 14)
            legend(hx + w * 0.385, y0 + h * 0.925, "MHz      kHz", 14)
            d.rounded_rectangle([hx + w * 0.205, y0 + h * 0.66, hx + w * 0.225, y0 + h * 0.82], radius=3 * k, fill=(198, 196, 188), outline=(90, 90, 90))      # a small switch
            legend(hx + w * 0.215, y0 + h * 0.585, "SQ" if half == 0 else "TO", 13); legend(hx + w * 0.215, y0 + h * 0.895, "TEST" if half == 0 else "FR", 12)
        d.line([x0 + w * 0.5, y0 + h * 0.08, x0 + w * 0.5, y0 + h * 0.92], fill=EDGE, width=max(1, int(2 * k)))
        seats(region, x0, y0, w, h)
    navcom("COMNAV1", "118.30", "110.50"); navcom("COMNAV2", "121.50", "113.90")
    x0, y0, w, h = face("XPDR")
    for i, digit in enumerate("1200"):
        window(x0 + w * (0.330 + 0.085 * i), y0 + h * 0.15, w * 0.062, h * 0.34, digit)
    legend(x0 + w * 0.488, y0 + h * 0.075, "CODE", 14)
    for t, du, dv in (("OFF", -0.078, 0.36), ("SBY", -0.040, -0.36), ("ON", 0.022, -0.40), ("ALT", 0.074, -0.20), ("TST", 0.082, 0.36)):
        legend(x0 + w * (0.115 + du), y0 + h * (0.54 + dv), t, 13)
    d.ellipse([x0 + w * 0.745, y0 + h * 0.22, x0 + w * 0.745 + h * 0.26, y0 + h * 0.48], fill=(124, 98, 30), outline=(176, 154, 84), width=max(1, int(2 * k))); legend(x0 + w * 0.745 + h * 0.13, y0 + h * 0.66, "REPLY", 13)
    d.rounded_rectangle([x0 + w * 0.865, y0 + h * 0.20, x0 + w * 0.935, y0 + h * 0.50], radius=5 * k, fill=(50, 50, 52), outline=(112, 112, 114), width=max(1, int(2 * k))); legend(x0 + w * 0.90, y0 + h * 0.66, "IDENT", 13)
    legend(x0 + w * 0.85, y0 + h * 0.87, "TRANSPONDER", 13, (150, 150, 146))
    seats("XPDR", x0, y0, w, h)
    x0, y0, w, h = face("ADF")
    window(x0 + w * 0.05, y0 + h * 0.16, w * 0.22, h * 0.34, "0 3 4 5"); legend(x0 + w * 0.16, y0 + h * 0.085, "ADF   kHz", 14)
    for t, du, dv in (("OFF", -0.070, 0.10), ("ADF", -0.034, -0.36), ("ANT", 0.034, -0.36), ("BFO", 0.072, 0.10)):
        legend(x0 + w * (0.42 + du), y0 + h * (0.58 + dv), t, 13)
    legend(x0 + w * 0.255, y0 + h * 0.77, "VOL", 13); legend(x0 + w * 0.80, y0 + h * 0.90, "TUNE", 13); legend(x0 + w * 0.61, y0 + h * 0.20, "ADF", 15, (150, 150, 146))
    seats("ADF", x0, y0, w, h)
    x0, y0, w, h = face("AUDIO")
    for i, t in enumerate(("COM 1", "COM 2", "NAV 1", "NAV 2", "ADF", "MKR", "SPKR", "PHONE")):
        legend(x0 + w * (0.09 + 0.117 * i), y0 + h * 0.80, t, 13)
    seats("AUDIO", x0, y0, w, h)
    x0, y0, w, h = face("MARKER")
    for i, (t, c) in enumerate((("O", (70, 110, 235)), ("M", (236, 176, 44)), ("A", (238, 238, 232)))):
        cx = x0 + w * (0.34 + 0.13 * i); cy = y0 + h * 0.50; r = h * 0.27
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=tuple(int(v * 0.42) for v in c), outline=(124, 124, 126), width=max(1, int(2 * k)))
        d.text((cx, cy), t, fill=c, font=font(r * 1.15, True), anchor="mm")
    legend(x0 + w * 0.15, y0 + h * 0.50, "MARKER", 15); legend(x0 + w * 0.80, y0 + h * 0.20, "HI  LO  TEST", 12)
    seats("MARKER", x0, y0, w, h)
    # ---- the small indicators: scale across the top, read against a pointer pivoted below (the pointer is a part)
    def rect_gauge(region, key, title):
        x0, y0, x1, y1 = px(region); w, h = x1 - x0, y1 - y0
        spec = INSTR[key]; s = w / RECT_W
        cx, cy = x0 + w / 2, y0 + h / 2
        py_ = cy + RECT_PIVOT * s; R = rect_radius(key) * s
        d.rectangle([x0, y0, x1, y1], fill=(12, 12, 13))
        for arc in spec.get("arcs", []):
            a0, a1 = value_to_angle(spec, arc["from"]), value_to_angle(spec, arc["to"])
            d.pieslice([cx - R, py_ - R, cx + R, py_ + R], a0 - 90, a1 - 90, fill=COLORS[arc["color"]])
            d.pieslice([cx - R * 0.87, py_ - R * 0.87, cx + R * 0.87, py_ + R * 0.87], a0 - 92, a1 - 88, fill=(12, 12, 13))
        t = spec.get("ticks", {})
        if "minor_step" in t:
            v = t.get("minor_from", spec["min"])
            while v <= spec["max"] + 1e-9:
                a = value_to_angle(spec, v)
                d.line([_pol(cx, py_, R * 0.90, a), _pol(cx, py_, R, a)], fill=(228, 228, 228), width=max(1, int(2 * k)))
                v += t["minor_step"]
        for v in t.get("major", []):
            a = value_to_angle(spec, v)
            d.line([_pol(cx, py_, R * 0.80, a), _pol(cx, py_, R * 1.01, a)], fill=(245, 245, 245), width=max(2, int(4 * k)))
        for rl in spec.get("redlines", []):
            a = value_to_angle(spec, rl["value"])
            d.line([_pol(cx, py_, R * 0.76, a), _pol(cx, py_, R * 1.04, a)], fill=COLORS["red"], width=max(2, int(6 * k)))
        fl = font(19 * k, True)
        for v in spec.get("labels", []):                       # the figures stand inside the scale, under their marks
            a = value_to_angle(spec, v)
            txt = spec.get("label_text", {}).get(str(v)) or spec.get("label_text", {}).get(str(int(v)) if float(v).is_integer() else str(v))
            if txt is None:
                txt = ("+" if v > 0 and key == "AMMETER" else "") + (str(int(v)) if float(v).is_integer() else str(v))
            d.text(_pol(cx, py_, R * 0.60, a), txt, fill=(240, 240, 240), font=fl, anchor="mm")
        d.text((cx, y0 + 21 * k), title, fill=(214, 214, 210), font=font(19 * k, True), anchor="mm")
    rect_gauge("G_FUEL_L", "FUEL_L", "LEFT"); rect_gauge("G_FUEL_R", "FUEL_R", "RIGHT")
    rect_gauge("G_OIL_T", "OIL_T", "TEMP"); rect_gauge("G_OIL_P", "OIL_P", "PRESS"); rect_gauge("G_AMMETER", "AMMETER", "AMP")
    # ---- flap position indicator: a scale down the side of the lever's slot, the pointer at UP
    x0, y0, x1, y1 = px("FLAP_IND"); d.rectangle([x0, y0, x1, y1], fill=(16, 16, 17)); w, h = x1 - x0, y1 - y0
    d.rectangle([x0 + 4 * k, y0 + 4 * k, x1 - 4 * k, y1 - 4 * k], outline=EDGE, width=max(1, int(2 * k)))
    for i, t in enumerate(("UP", "10°", "20°", "30°", "40°")):
        cy = y0 + h * (0.16 + 0.175 * i)
        d.line([x0 + w * 0.58, cy, x0 + w * 0.90, cy], fill=LEG, width=max(1, int(4 * k)))
        d.text((x0 + w * 0.30, cy), t, fill=LEG, font=font(w * 0.20, True), anchor="mm")
    d.polygon([(x0 + w * 0.60, y0 + h * 0.16), (x0 + w * 0.96, y0 + h * 0.135), (x0 + w * 0.96, y0 + h * 0.185)], fill=(245, 245, 240))
    x0, y0, x1, y1 = px("LOW_VOLT"); d.rectangle([x0, y0, x1, y1], fill=(26, 26, 27))
    d.rounded_rectangle([x0 + 12 * k, y0 + 12 * k, x1 - 12 * k, y1 - 12 * k], radius=14 * k, fill=(132, 22, 20), outline=(60, 12, 12), width=max(1, int(4 * k)))
    d.text(((x0 + x1) / 2, (y0 + y1) / 2), "LOW VOLTAGE", fill=(252, 224, 220), font=font((y1 - y0) * 0.20, True), anchor="mm")
    x0, y0, x1, y1 = px("HOURMETER"); d.rectangle([x0, y0, x1, y1], fill=(26, 26, 27))
    d.rectangle([x0 + 22 * k, y0 + 22 * k, x1 - 22 * k, y1 - 50 * k], fill=(8, 8, 9), outline=(94, 94, 96), width=max(1, int(2 * k)))
    d.text(((x0 + x1) / 2, (y0 + y1) / 2 - 14 * k), "0 4 2 3 1", fill=DIGIT, font=font((y1 - y0) * 0.36, True), anchor="mm")
    d.text(((x0 + x1) / 2, y1 - 26 * k), "HOURS  1/10", fill=LEG, font=font((y1 - y0) * 0.14), anchor="mm")
    x0, y0, x1, y1 = px("PLACARD_SPEED"); d.rectangle([x0, y0, x1, y1], fill=(14, 14, 15))
    d.rectangle([x0 + 5 * k, y0 + 5 * k, x1 - 5 * k, y1 - 5 * k], outline=(150, 150, 146), width=max(1, int(2 * k)))
    lines = ["MANEUVERING SPEED 97 KIAS AT 2300 LBS", "THIS AIRPLANE MUST BE OPERATED IN COMPLIANCE", "WITH THE OPERATING LIMITATIONS — POH SECTION 2"]
    f = font((y1 - y0) / 4 * 0.50, True)
    for i, ln in enumerate(lines):
        d.text(((x0 + x1) / 2, y0 + (y1 - y0) * (i + 1) / 4), ln, fill=(232, 232, 228), font=f, anchor="mm")
    # the plate behind the ignition key: the five positions round the switch
    x0, y0, x1, y1 = px("IGNITION"); d.rectangle([x0, y0, x1, y1], fill=(20, 20, 21))
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2 + (y1 - y0) * 0.06; R = (x1 - x0) * 0.375
    d.rounded_rectangle([x0 + 5 * k, y0 + 5 * k, x1 - 5 * k, y1 - 5 * k], radius=22 * k, outline=(150, 150, 146), width=max(1, int(2 * k)))
    f = font((y1 - y0) * 0.072, True)
    for a, t in ((-66, "OFF"), (-33, "R"), (0, "L"), (33, "BOTH"), (66, "START")):
        d.text(_pol(cx, cy, R, a), t, fill=(232, 232, 228), font=f, anchor="mm")
        d.line([_pol(cx, cy, R * 0.66, a), _pol(cx, cy, R * 0.80, a)], fill=(232, 232, 228), width=max(1, int(3 * k)))
    # the window of the magnetic compass: a stretch of its card behind the lubber line
    x0, y0, x1, y1 = px("COMPASS"); d.rectangle([x0, y0, x1, y1], fill=(9, 9, 10)); w, h = x1 - x0, y1 - y0
    f = font(h * 0.40, True)
    for deg in range(-45, 50, 5):
        cx = x0 + w * (0.5 + deg / 90.0)
        d.line([cx, y1 - h * (0.40 if deg % 30 == 0 else 0.30 if deg % 10 == 0 else 0.20), cx, y1 - h * 0.04], fill=(240, 240, 240), width=max(1, int(4 * k)))
        if deg % 30 == 0:
            d.text((cx, y0 + h * 0.30), {0: "N", 30: "3", -30: "33"}[deg], fill=(240, 240, 240), font=f, anchor="mm")
    d.line([x0 + w / 2, y0, x0 + w / 2, y1], fill=(236, 236, 230), width=max(1, int(3 * k)))
    img.save(path)


def wood_panel(path, size=(1536, 256)):
    """The printed walnut laminate of the lower panel of a 1970s Cessna: fine grain that drifts together, a few darker
    figure lines, softened. One piece for the whole width of the panel (it does not tile)."""
    import random
    from PIL import Image, ImageDraw, ImageFilter
    W, H = size
    rnd = random.Random(3)
    img = Image.new("RGB", (W, H), (74, 42, 21))
    d = ImageDraw.Draw(img)
    drift = [rnd.random() * 6.28 for _ in range(3)]
    for i in range(int(H * 3.4)):
        yy = rnd.random() * H; amp = 1.5 + rnd.random() * 4.5; dark = rnd.random() < 0.13
        pts = [(kx * W / 120, yy + math.sin(kx / 13.0 + drift[0] + yy / 31.0) * amp + math.sin(kx / 37.0 + drift[1]) * 3.5 + math.sin(kx / 5.0 + drift[2] + yy / 9.0) * 0.8) for kx in range(121)]
        c = (48 + rnd.randint(-8, 8), 26 + rnd.randint(-5, 5), 13 + rnd.randint(-3, 3)) if dark else (98 + rnd.randint(-18, 22), 57 + rnd.randint(-10, 14), 28 + rnd.randint(-6, 8))
        d.line(pts, fill=c, width=1)
    img.filter(ImageFilter.GaussianBlur(0.6)).save(path, quality=90)

# ---------------------------------------------------------------------------------------------- panel lettering
def placard_atlas(path):
    """White lettering on a transparent sheet: the names of the switches and controls (layout: atlas.measure_lettering)."""
    from PIL import Image, ImageDraw, ImageFont
    from .atlas import measure_lettering, LETTER_PX, LETTER_SIZE
    size = LETTER_SIZE
    img = Image.new("RGBA", (size, size), (238, 238, 232, 0))      # the colour of the letters everywhere, so no dark fringe shows when filtered
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(FONT_BOLD, int(LETTER_PX * 0.74))
    for word, ((u0, v0, u1, v1), _aspect) in measure_lettering(FONT_BOLD).items():
        x0, y0, x1, y1 = u0 * size, (1 - v1) * size, u1 * size, (1 - v0) * size
        d.text(((x0 + x1) / 2, (y0 + y1) / 2), word, fill=(238, 238, 232, 255), font=f, anchor="mm")
    img.save(path)

if __name__ == "__main__":
    import sys
    dials_atlas(sys.argv[1] if len(sys.argv) > 1 else "dials.png")
    panel_misc_atlas(sys.argv[2] if len(sys.argv) > 2 else "panel_misc.png")
