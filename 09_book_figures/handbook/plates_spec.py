"""The plates of the handbook: plates.json (the first six) and one Python module per further figure in figs/ (f_NN_NN_name.py, each
with a function plate() that returns a plate in the same form as an entry of plates.json). A figure that is mostly a loop
(ticks along a scale, six aeroplanes along a path) is shorter to write as code than as JSON.

    load() -> the spec: plates.json with the figures of figs/ added to its "plates"."""
import importlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def load():
    with open(os.path.join(HERE, "plates.json"), encoding="utf-8") as f:
        spec = json.load(f)
    folder = os.path.join(HERE, "figs")
    if os.path.isdir(folder):
        if HERE not in sys.path:
            sys.path.insert(0, HERE)
        for name in sorted(os.listdir(folder)):
            if name.startswith("f_") and name.endswith(".py"):
                module = importlib.import_module("figs." + name[:-3])
                spec["plates"].append(module.plate())
        spec["sprites"] = importlib.import_module("figs.sprites").sprites()
        spec["clouds"] = importlib.import_module("figs.clouds").clouds()
    return spec
