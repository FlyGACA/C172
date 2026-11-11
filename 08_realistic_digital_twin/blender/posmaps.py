"""Write the position maps of the painted skins: where each texel of their textures lies on the aircraft.

    blender -b --python blender/posmaps.py -- [--assets <dir>]

The texture generator (python3 -m c172.textures) reads them to lay the paint scheme on the fuselage, the cowl,
the fin and the rudder, and the trim on the cabin liner; see c172/posmap.py. Only the airframe is built here,
without its materials.
"""
import argparse
import collections
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import bpy                                          # noqa: E402
from build import Ctx, GROUPS, ROOT                 # noqa: E402
from c172 import airframe, powerplant, posmap       # noqa: E402

SKINS = {
    "fuselage": ["AIRFRAME.fuselage"],
    "cowl": ["POWERPLANT.cowl_upper", "POWERPLANT.cowl_lower"],
    "fin": ["EMPENNAGE.fin"],
    "rudder": ["EMPENNAGE.rudder"],
    "liner": ["INTERIOR.cabin_liner"],
}


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--assets", default=os.path.join(ROOT, "assets"))
    args = ap.parse_args(argv)
    t = time.time()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    ctx = Ctx(posmap.LEVELS)
    ctx.detail_level = 0
    ctx.mats = collections.defaultdict(lambda: None)        # the shapes only: no textures are needed to say where they lie
    for name, en, ar in GROUPS:
        ctx.group(name, en, ar)
    airframe.build_fuselage(ctx); airframe.build_wing(ctx, 1); airframe.build_wing(ctx, -1); airframe.build_empennage(ctx); airframe.build_details(ctx)
    powerplant.build_cowl(ctx)
    posmap.write(os.path.join(args.assets, "posmaps"), SKINS)
    print(f"position maps written in {time.time() - t:.1f} s")


if __name__ == "__main__":
    main()
