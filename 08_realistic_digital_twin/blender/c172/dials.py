"""Instrument faces and panel placards drawn from data/instruments.json (POH-referenced scales).
Atlas layout (dials.png, 4x4 cells): see CELLS. Angles: clockwise from 12 o'clock as the pilot sees them."""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(os.path.dirname(os.path.dirname(HERE)), "data", "instruments.json")
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
CELLS = ["ASI", "AI_BALL", "AI_MASK", "ALT", "TC", "DG_CARD", "DG_MASK", "VSI", "TACH", "SUCTION", "AMMETER", "OIL_P", "OIL_T", "FUEL_L", "FUEL_R", "CLOCK"]
COLORS = {"white": (235, 235, 235), "green": (40, 170, 70), "yellow": (240, 200, 40), "red": (220, 30, 30)}

def cell_uv(name):
    i = CELLS.index(name); c, r = i % 4, i // 4
    return (c / 4, 1 - (r + 1) / 4, (c + 1) / 4, 1 - r / 4)     # u0, v0, u1, v1 (v up)

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
    # hub
    d.ellipse([cx - S * 0.03, cy - S * 0.03, cx + S * 0.03, cy + S * 0.03], fill=(40, 40, 40))

def dials_atlas(path, size=2048):
    from PIL import Image, ImageDraw, ImageFont
    with open(DATA, encoding="utf-8") as f:
        INSTR = json.load(f)["instruments"]
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img, "RGBA")
    cs = size // 4
    def box(name):
        i = CELLS.index(name); c, r = i % 4, i // 4
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
    draw_dial(img, box("SUCTION"), INSTR["SUCTION"], "SUCTION", "IN. HG")
    draw_dial(img, box("AMMETER"), INSTR["AMMETER"], "AMP", "")
    draw_dial(img, box("OIL_P"), INSTR["OIL_P"], "OIL PRESS", "PSI")
    draw_dial(img, box("OIL_T"), INSTR["OIL_T"], "OIL TEMP", "°F")
    draw_dial(img, box("FUEL_L"), INSTR["FUEL_L"], "FUEL QTY", "LEFT GAL", font_scale=1.3)
    draw_dial(img, box("FUEL_R"), INSTR["FUEL_R"], "FUEL QTY", "RIGHT GAL", font_scale=1.3)
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
    img.save(path)

MISC = {   # name -> (u0, v0, u1, v1) regions of panel_misc.png (v up)
    "COMNAV1": (0.0, 0.875, 0.5, 1.0), "COMNAV2": (0.0, 0.75, 0.5, 0.875), "ADF": (0.0, 0.625, 0.5, 0.75), "XPDR": (0.0, 0.5, 0.5, 0.625),
    "AUDIO": (0.0, 0.4375, 0.5, 0.5), "MARKER": (0.0, 0.375, 0.5, 0.4375),
    "FLAP_IND": (0.5, 0.875, 0.75, 1.0), "LOW_VOLT": (0.75, 0.875, 1.0, 1.0), "HOURMETER": (0.5, 0.75, 0.75, 0.875),
    "PLACARD_SPEED": (0.5, 0.625, 1.0, 0.75), "PLACARD_FUEL": (0.5, 0.5, 1.0, 0.625), "SWITCHES": (0.0, 0.25, 1.0, 0.375),
    "IGNITION": (0.75, 0.75, 1.0, 0.875), "WOOD": (0.0, 0.0, 0.5, 0.25), "COMPASS": (0.5, 0.0, 1.0, 0.25),
}

def panel_misc_atlas(path, size=1024):
    from PIL import Image, ImageDraw, ImageFont
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    def px(region):
        u0, v0, u1, v1 = MISC[region]
        return (int(u0 * size), int((1 - v1) * size), int(u1 * size), int((1 - v0) * size))
    def radio(region, left, right, label1, label2, color=(255, 150, 40)):
        x0, y0, x1, y1 = px(region); h = y1 - y0
        d.rectangle([x0, y0, x1, y1], fill=(28, 28, 30))
        d.rectangle([x0 + 4, y0 + 4, x1 - 4, y1 - 4], outline=(70, 70, 72), width=2)
        f = ImageFont.truetype(FONT_BOLD, int(h * 0.42)); fl = ImageFont.truetype(FONT, int(h * 0.2))
        for cx, txt in ((x0 + (x1 - x0) * 0.28, left), (x0 + (x1 - x0) * 0.72, right)):
            d.rectangle([cx - (x1 - x0) * 0.17, y0 + h * 0.2, cx + (x1 - x0) * 0.17, y0 + h * 0.75], fill=(8, 8, 8))
            d.text((cx, y0 + h * 0.47), txt, fill=color, font=f, anchor="mm")
        d.text((x0 + (x1 - x0) * 0.28, y0 + h * 0.88), label1, fill=(210, 210, 210), font=fl, anchor="mm")
        d.text((x0 + (x1 - x0) * 0.72, y0 + h * 0.88), label2, fill=(210, 210, 210), font=fl, anchor="mm")
        for cx in (x0 + (x1 - x0) * 0.07, x0 + (x1 - x0) * 0.5, x0 + (x1 - x0) * 0.93):
            d.ellipse([cx - h * 0.18, y0 + h * 0.3, cx + h * 0.18, y0 + h * 0.66], fill=(60, 60, 60), outline=(110, 110, 110))
    radio("COMNAV1", "118.30", "110.50", "COMM", "NAV"); radio("COMNAV2", "121.50", "113.90", "COMM", "NAV")
    radio("ADF", "0 3 4 5", "ADF", "FREQ kHz", "ADF", color=(255, 90, 60))
    radio("XPDR", "1 2 0 0", "ALT", "CODE", "MODE", color=(255, 150, 40))
    x0, y0, x1, y1 = px("AUDIO"); d.rectangle([x0, y0, x1, y1], fill=(28, 28, 30))
    f = ImageFont.truetype(FONT, int((y1 - y0) * 0.28))
    for i, t in enumerate(("COM1", "COM2", "NAV1", "NAV2", "ADF", "MKR", "SPKR", "PHONE")):
        cx = x0 + (x1 - x0) * (i + 0.5) / 8
        d.rectangle([cx - 10, y0 + (y1 - y0) * 0.25, cx + 10, y0 + (y1 - y0) * 0.6], fill=(200, 200, 200))
        d.text((cx, y0 + (y1 - y0) * 0.82), t, fill=(210, 210, 210), font=f, anchor="mm")
    x0, y0, x1, y1 = px("MARKER"); d.rectangle([x0, y0, x1, y1], fill=(28, 28, 30))
    for i, (t, c) in enumerate((("O", (60, 90, 220)), ("M", (230, 180, 40)), ("A", (240, 240, 240)))):
        cx = x0 + (x1 - x0) * (i + 1) / 4
        d.ellipse([cx - 12, (y0 + y1) / 2 - 12, cx + 12, (y0 + y1) / 2 + 12], fill=c)
    x0, y0, x1, y1 = px("FLAP_IND"); d.rectangle([x0, y0, x1, y1], fill=(20, 20, 20))
    f = ImageFont.truetype(FONT_BOLD, int((y1 - y0) * 0.22))
    d.text(((x0 + x1) / 2, y0 + (y1 - y0) * 0.18), "WING FLAPS", fill=(230, 230, 230), font=f, anchor="mm")
    for i, t in enumerate(("0", "10", "20", "30")):
        d.text((x0 + (x1 - x0) * (i + 0.5) / 4, y0 + (y1 - y0) * 0.6), t, fill=(230, 230, 230), font=f, anchor="mm")
    x0, y0, x1, y1 = px("LOW_VOLT"); d.rectangle([x0, y0, x1, y1], fill=(35, 35, 35))
    d.rectangle([x0 + 10, y0 + 10, x1 - 10, y1 - 10], fill=(140, 20, 20))
    d.text(((x0 + x1) / 2, (y0 + y1) / 2), "LOW VOLTAGE", fill=(250, 220, 220), font=ImageFont.truetype(FONT_BOLD, int((y1 - y0) * 0.2)), anchor="mm")
    x0, y0, x1, y1 = px("HOURMETER"); d.rectangle([x0, y0, x1, y1], fill=(35, 35, 35))
    d.rectangle([x0 + 10, y0 + 15, x1 - 10, y1 - 15], fill=(240, 240, 240))
    d.text(((x0 + x1) / 2, (y0 + y1) / 2), "4 2 3 1 . 6", fill=(20, 20, 20), font=ImageFont.truetype(FONT_BOLD, int((y1 - y0) * 0.4)), anchor="mm")
    def placard(region, lines, bg=(235, 235, 235), fg=(20, 20, 20)):
        x0, y0, x1, y1 = px(region); d.rectangle([x0, y0, x1, y1], fill=bg)
        f = ImageFont.truetype(FONT_BOLD, int((y1 - y0) / (len(lines) + 1) * 0.45))
        for i, ln in enumerate(lines):
            d.text(((x0 + x1) / 2, y0 + (y1 - y0) * (i + 1) / (len(lines) + 1)), ln, fill=fg, font=f, anchor="mm")
    placard("PLACARD_SPEED", ["MANEUVERING SPEED 97 KIAS AT 2300 LBS", "THIS AIRPLANE MUST BE OPERATED IN COMPLIANCE", "WITH THE OPERATING LIMITATIONS — POH SECTION 2"])
    placard("PLACARD_FUEL", ["FUEL SELECTOR", "LEFT · BOTH · RIGHT · OFF", "TAKEOFF AND LANDING ON BOTH — 40.0 GAL USABLE"])
    # switch labels row
    x0, y0, x1, y1 = px("SWITCHES"); d.rectangle([x0, y0, x1, y1], fill=(30, 30, 30))
    f = ImageFont.truetype(FONT, int((y1 - y0) * 0.09))
    for i, t in enumerate(("MASTER", "BCN", "NAV", "STROBE", "TAXI", "LDG", "PITOT HT", "AVN MASTER", "CARB HEAT", "THROTTLE", "MIXTURE", "FLAPS")):
        d.text((x0 + (x1 - x0) * (i + 0.5) / 12, (y0 + y1) / 2), t, fill=(220, 220, 220), font=f, anchor="mm")
    x0, y0, x1, y1 = px("IGNITION"); d.rectangle([x0, y0, x1, y1], fill=(30, 30, 30))
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2 + (y1 - y0) * 0.1; R = (x1 - x0) * 0.4
    f = ImageFont.truetype(FONT_BOLD, int((y1 - y0) * 0.11))
    for a, t in ((-70, "OFF"), (-35, "R"), (0, "L"), (35, "BOTH"), (70, "START")):
        d.text(_pol(cx, cy, R, a), t, fill=(230, 230, 230), font=f, anchor="mm")
    # woodgrain lower panel (1970s Cessna 'Royalite' laminate look)
    x0, y0, x1, y1 = px("WOOD")
    import random
    rnd = random.Random(3)
    d.rectangle([x0, y0, x1, y1], fill=(92, 52, 24))
    for i in range(140):
        yy = y0 + rnd.random() * (y1 - y0); amp = rnd.random() * 8
        pts = [(x0 + k * (x1 - x0) / 40, yy + math.sin(k / 3.0 + i) * amp) for k in range(41)]
        d.line(pts, fill=(120 + rnd.randint(-30, 30), 70 + rnd.randint(-20, 20), 30 + rnd.randint(-10, 15)), width=rnd.randint(1, 3))
    # magnetic compass card strip
    x0, y0, x1, y1 = px("COMPASS"); d.rectangle([x0, y0, x1, y1], fill=(15, 15, 15))
    f = ImageFont.truetype(FONT_BOLD, int((y1 - y0) * 0.12))
    for deg in range(0, 360, 5):
        cx = x0 + (x1 - x0) * deg / 360
        d.line([cx, y1 - (y1 - y0) * (0.35 if deg % 30 == 0 else 0.2), cx, y1], fill=(240, 240, 240), width=2)
        if deg % 30 == 0:
            d.text((cx, y0 + (y1 - y0) * 0.35), {0: "N", 90: "E", 180: "S", 270: "W"}.get(deg, str(deg // 10)), fill=(240, 240, 240), font=f, anchor="mm")
    img.save(path)

if __name__ == "__main__":
    import sys
    dials_atlas(sys.argv[1] if len(sys.argv) > 1 else "dials.png")
    panel_misc_atlas(sys.argv[2] if len(sys.argv) > 2 else "panel_misc.png")
