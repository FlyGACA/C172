"""Finer copies of the dial artwork for the plates, which look at one instrument from close by.

The model carries its dials at 2560 x 2048 px (four columns of 512 px cells), which is plenty for the web viewer
and soft in a close-up. A plate that fills the picture with an instrument needs more: this draws the same atlas
(same layout, same code) at four times the size into handbook/cache/, and the plate renderer swaps it in. Where the
book's example aeroplane differs from the model (its airspeed indicator has other V-speeds), plates.json "dials" holds
the book's values and this atlas is drawn with them.

    python3 09_book_figures/handbook/fine_textures.py [size]       (default 4096: cells of 1024 px)
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)), "08_realistic_digital_twin", "blender"))
from c172 import dials   # noqa: E402

size = int(sys.argv[1]) if len(sys.argv) > 1 else 4096
out = os.path.join(HERE, "cache")
os.makedirs(out, exist_ok=True)
with open(os.path.join(HERE, "plates.json"), encoding="utf-8") as f:
    overrides = json.load(f).get("dials", {})          # the book's example aeroplane has its own V-speeds (plates.json "dials")
dials.dials_atlas(os.path.join(out, "dials.png"), size=size, overrides=overrides)
print("wrote", os.path.join(out, "dials.png"), f"({size // dials.ROWS * dials.COLS} x {size} px)")
