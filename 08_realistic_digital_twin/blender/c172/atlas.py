"""Where things lie in the texture atlases: markings (decals) and panel lettering.

The texture generator runs under the system Python, which has Pillow; the builders run inside Blender, which does
not. The widths of the words of the lettering depend on the typeface, so the generator measures them and writes
the layout beside the textures (atlas_cells.json), and the builders read it from there.
"""
import json
import os

# ---- markings laid on the skin as separate pieces: name, lines, pixel box (x, y, w, h), colour, style
NAVY = (0.09, 0.19, 0.40)
DECAL_SIZE = (2048, 512)
DECAL_LAYOUT = [
    ("WORDMARK", ["FlyGACA"], (16, 16, 1500, 330), NAVY, "wordmark"),
    ("NO_STEP", ["NO STEP"], (1540, 16, 480, 150), (0.05, 0.05, 0.05), "stencil"),
    ("FUEL", ["FUEL  100LL", "21.5 US GAL"], (1540, 190, 480, 230), (0.75, 0.05, 0.05), "placard"),
]

def decal_cells():
    """name -> ((u0, v0, u1, v1), width over height) in the decal atlas, v up."""
    W, H = DECAL_SIZE
    return {name: ((x / W, 1 - (y + h) / H, (x + w) / W, 1 - y / H), w / h) for name, _t, (x, y, w, h), _c, _s in DECAL_LAYOUT}

# ---- white lettering laid on the panel beside each switch and control: the plain names of the controls
LETTERING = ["MASTER", "ALT", "BAT", "BCN", "NAV", "STROBE", "TAXI", "LAND", "PITOT HT", "AVN PWR", "PRIMER", "CARB HEAT", "PULL ON", "THROTTLE",
             "PUSH OPEN", "MIXTURE", "PULL LEAN", "CABIN HT", "CABIN AIR", "PARK BRAKE", "WING FLAPS", "UP", "10", "20", "FULL", "ELEV TRIM", "NOSE DN", "NOSE UP",
             "TAKE OFF", "FUEL", "LEFT", "BOTH", "RIGHT", "OFF", "CIRCUIT BREAKERS", "PUSH TO RESET", "MIC", "PHONE", "IGNITION", "LIGHTS", "PANEL LT", "RADIO LT", "OIL"]
LETTER_PX = 46          # height of a line of lettering in the atlas
LETTER_SIZE = 1024
_cells_file = None

def measure_lettering(font_path, size=LETTER_SIZE):
    """Lay the words out in rows (needs Pillow): word -> ((u0, v0, u1, v1), width over height)."""
    from PIL import ImageFont
    f = ImageFont.truetype(font_path, int(LETTER_PX * 0.74))
    cells = {}; x = 6; y = 6
    for word in LETTERING:
        w = int(f.getlength(word)) + 14
        if x + w > size - 6:
            x = 6; y += LETTER_PX + 6
        cells[word] = ((x / size, 1 - (y + LETTER_PX) / size, (x + w) / size, 1 - y / size), w / LETTER_PX)
        x += w + 8
    return cells

def write_cells(path, font_path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"lettering": {k: [list(v[0]), v[1]] for k, v in measure_lettering(font_path).items()}}, f, indent=1)

def use_cells(path):
    """Tell the builders where the generator wrote the layout."""
    global _cells_file
    _cells_file = path

def lettering_cells():
    if _cells_file is None or not os.path.exists(_cells_file):
        raise RuntimeError("atlas_cells.json is missing: generate the textures first (python3 -m c172.textures <assets>)")
    with open(_cells_file, encoding="utf-8") as f:
        return {k: (tuple(v[0]), v[1]) for k, v in json.load(f)["lettering"].items()}
