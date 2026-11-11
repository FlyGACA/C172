"""Detail packs: what lies under the skin and behind the panels.

The basic model (airframe.py, gear.py, powerplant.py, cockpit.py, engine.py) is what one sees from
outside and from the seats. The modules in this package add the parts a mechanic or an instructor
points at: structure, control runs, system components, the insides of the engine and of the
instruments, and the fasteners that hold it together. Every part is a separate object with its own
name, bilingual label, status and reference, so that it can be shown, exported or drawn on its own
(09_book_figures/blender/part.py) as well as in place.

Each part carries a detail level:
    0   basic model
    1   structure, mechanisms and internals
    2   fasteners (rivet rows, screws, bolts)
The build takes the highest level wanted; the lighter quality levels of the web model leave the
upper levels out (export.LODS).

A module is a file in this package with a build(ctx) function and, optionally, LEVEL (default 1).
They are built in the order of MODULES; a name without a file is skipped, so a pack can be added
without touching build.py.
"""
import importlib
import time

MODULES = [
    "structure_wing",
    "structure_fuselage",
    "structure_tail",
    "controls",
    "flap_drive",
    "fuel",
    "pneumatic",
    "brakes",
    "electrical",
    "engine_detail",
    "instruments",
    "interior",
    "cabin",
    "avionics",
    "fasteners",
    "ground",
]


def build_all(ctx, level):
    """Build every available detail module whose LEVEL is within `level`."""
    built = []
    if level <= 0:
        return built
    for name in MODULES:
        full = f"{__name__}.{name}"
        try:
            module = importlib.import_module(full)
        except ModuleNotFoundError as error:
            if error.name == full:
                continue                      # this pack has not been written yet
            raise
        if getattr(module, "LEVEL", 1) > level:
            continue
        ctx.detail_level = level
        started = time.time()
        before = len(ctx.col.objects)
        module.build(ctx)
        built.append(name)
        print(f"detail {name}: {len(ctx.col.objects) - before} parts in {time.time() - started:.1f} s")
    return built
