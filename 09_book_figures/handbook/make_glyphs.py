"""One-off: outlines of the glyphs the plates use (the digits of the callouts, the alpha of the angle of attack) as
SVG path data, so that a plate looks the same wherever it is drawn, with no font installed.
Needs fontTools; the result, glyphs.json, is kept in the repository.   python3 make_glyphs.py"""
import json
import os
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

FONT = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
font = TTFont(FONT)
glyphs = font.getGlyphSet()
cmap = font.getBestCmap()
upm = font["head"].unitsPerEm
cap = font["OS/2"].sCapHeight
out = {"font": "Inter Bold (SIL Open Font License 1.1)", "units": upm, "cap_height": cap, "glyphs": {}}
for ch in "0123456789α":
    name = cmap[ord(ch)]
    pen = SVGPathPen(glyphs)
    glyphs[name].draw(TransformPen(pen, (1, 0, 0, -1, 0, 0)))          # font units are y up, SVG is y down
    out["glyphs"][ch] = {"d": pen.getCommands(), "advance": glyphs[name].width}
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "glyphs.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, indent=1)
print("wrote glyphs.json:", {k: v["advance"] for k, v in out["glyphs"].items()}, "cap height", cap, "upm", upm)
