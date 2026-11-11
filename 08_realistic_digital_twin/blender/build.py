"""FlyGACA Cessna 172N — Phase 8 model build (run inside Blender).

    blender -b --python blender/build.py -- --out models --assets assets --lod all

Builds the scene procedurally with the c172 package, saves the editable .blend (high LOD,
modifiers live) and exports Draco-compressed GLBs per quality level.
"""
import argparse
import math
import os
import sys
import time

import bpy
from mathutils import Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.dirname(HERE)

from c172 import units as U                       # noqa: E402
from c172 import materials, airframe, gear, powerplant, export, atlas  # noqa: E402
from c172.shapes import empty                      # noqa: E402

AXIS_MAP = {"x": ("x", 1), "y": ("z", -1), "z": ("y", 1)}   # Blender local axis -> glTF local axis, sign
GROUPS = [("AIRFRAME", "Airframe", "هيكل الطائرة"), ("WING_R", "Right wing", "الجناح الأيمن"), ("WING_L", "Left wing", "الجناح الأيسر"),
          ("EMPENNAGE", "Empennage", "الذيل"), ("GEAR", "Landing gear", "عجلات الهبوط"), ("POWERPLANT", "Powerplant", "مجموعة القدرة"),
          ("ENGINE", "Engine", "المحرك"), ("INTERIOR", "Interior", "المقصورة الداخلية"), ("PANEL", "Instrument panel", "لوحة العدادات"),
          ("SYSTEMS", "Aircraft systems", "أنظمة الطائرة")]


class Ctx:
    def __init__(self, subsurf):
        self.subsurf = subsurf
        self.col = bpy.data.collections.new("C172N")
        self.cutters = bpy.data.collections.new("_cutters")
        bpy.context.scene.collection.children.link(self.col)
        bpy.context.scene.collection.children.link(self.cutters)
        self.groups = {}
        self.mats = None

    def group(self, name, label_en, label_ar):
        g = empty(name, self.col)
        g["system"] = name; g["label_en"] = label_en; g["label_ar"] = label_ar; g["group"] = True
        self.groups[name] = g
        return g

    def tag(self, ob, system, label_en, label_ar, status="estimated", **kw):
        if status == "measured" and not kw.get("measurement_id"):
            raise ValueError(f"{ob.name}: measured geometry requires measurement_id")
        ob["system"] = system; ob["label_en"] = label_en; ob["label_ar"] = label_ar; ob["status"] = status
        for k, v in kw.items():
            if k in ("hinge_axis", "spin_axis"):
                ax, sgn = AXIS_MAP[v]
                ob[k] = ax
                sk = "hinge_sign" if k == "hinge_axis" else "spin_sign"
                ob[sk] = int(kw.get(sk, 1)) * sgn
            elif k in ("hinge_sign", "spin_sign"):
                continue
            else:
                ob[k] = v


def build_scene(subsurf, assets, detail=0):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.unit_settings.system = "METRIC"; sc.unit_settings.length_unit = "METERS"
    ctx = Ctx(subsurf)
    ctx.detail_level = detail            # the basic builders may fit themselves to the detail packs (seat frames on their rails)
    ctx.assets = assets                  # where the position maps of the painted skins are (c172/posmap.py)
    atlas.use_cells(os.path.join(assets, "textures", "atlas_cells.json"))      # where the texture generator laid out the lettering
    ctx.mats = materials.build_library(os.path.join(assets, "textures"))
    for name, en, ar in GROUPS:
        ctx.group(name, en, ar)
    t = time.time()
    airframe.build_fuselage(ctx); print("fuselage", round(time.time() - t, 1)); t = time.time()
    airframe.build_wing(ctx, 1); airframe.build_wing(ctx, -1); print("wings", round(time.time() - t, 1)); t = time.time()
    airframe.build_empennage(ctx); print("empennage", round(time.time() - t, 1)); t = time.time()
    airframe.build_details(ctx); print("details", round(time.time() - t, 1)); t = time.time()
    gear.build_main_gear(ctx, 1); gear.build_main_gear(ctx, -1); gear.build_nose_gear(ctx); print("gear", round(time.time() - t, 1)); t = time.time()
    powerplant.build_cowl(ctx); powerplant.build_spinner_prop(ctx); print("powerplant", round(time.time() - t, 1)); t = time.time()
    from c172 import cockpit, engine
    cockpit.build(ctx); print("cockpit", round(time.time() - t, 1)); t = time.time()
    engine.build(ctx); print("engine", round(time.time() - t, 1)); t = time.time()
    from c172 import detail as detail_packs
    detail_packs.build_all(ctx, detail); print("detail packs", round(time.time() - t, 1)); t = time.time()
    from c172 import decals
    decals.build(ctx); print("markings", round(time.time() - t, 1)); t = time.time()
    # helper meshes created without an explicit tag inherit their parent's system/label
    for ob in ctx.col.objects:
        if ob.type == "MESH" and "system" not in ob:
            par = ob.parent
            while par is not None and "system" not in par:
                par = par.parent
            sysname = par["system"] if par is not None else ob.name.split(".")[0]
            ob["system"] = sysname
            ob["label_en"] = (par["label_en"] + " (fitting)") if par is not None and "label_en" in par else ob.name
            ob["label_ar"] = (par["label_ar"] + " (تجهيز)") if par is not None and "label_ar" in par else ob.name
            ob["status"] = "estimated"
    # three.js' GLTFLoader strips '.' from node names, so keep the canonical id in the extras
    for ob in ctx.col.objects:
        ob["id"] = ob.name
        if ob.type == "MESH" and "detail" not in ob:
            ob["detail"] = 0
    export.hide_cutters(ctx)
    # The parts above are laid out in the build frame (see units.py). Turn the finished aircraft into
    # its attitude at rest, with the tyres on z = 0 and the main wheels at their station: every root
    # object, cutters included so the booleans stay valid. units.to_ground() is the same transform.
    bpy.context.view_layer.update()
    pivot_y, pivot_z = U.fs(U.GROUND_PIVOT_FS), U.wl(-U.GROUND_DROP_IN)
    at_rest = (Matrix.Translation((0, pivot_y, 0)) @ Matrix.Rotation(-math.radians(U.GROUND_PITCH_DEG), 4, "X")
               @ Matrix.Translation((0, -pivot_y, -pivot_z)))
    for ob in bpy.data.objects:
        if ob.parent is None:
            ob.matrix_world = at_rest @ ob.matrix_world
    bpy.context.view_layer.update()
    bpy.context.scene["ground_pitch_deg"] = U.GROUND_PITCH_DEG
    return ctx


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "models"))
    ap.add_argument("--assets", default=os.path.join(ROOT, "assets"))
    ap.add_argument("--lod", default="all")
    ap.add_argument("--no-draco", action="store_true")
    ap.add_argument("--skip-textures", action="store_true")
    ap.add_argument("--blend", default=None, help="path for the editable .blend (default <out>/C172N_realistic.blend)")
    ap.add_argument("--detail", type=int, default=None, help="highest detail level to build (0 basic, 1 structure and mechanisms, 2 fasteners); "
                                                             "default: what each quality level carries, everything in the .blend")
    args = ap.parse_args(argv)
    os.makedirs(args.out, exist_ok=True)
    tex_dir = os.path.join(args.assets, "textures")
    if not args.skip_textures or not os.path.exists(os.path.join(tex_dir, "fuselage_albedo.jpg")):
        # needs Pillow and the position maps: run blender/posmaps.py, then `python3 -m c172.textures assets` with the
        # system Python (npm run build:model8 does all three in order)
        from c172 import textures
        textures.generate_all(tex_dir, os.path.join(args.assets, "hdri"), size=2048)
        textures.downscale_sets(tex_dir, (1024,))
    lods = list(export.LODS) if args.lod == "all" else [args.lod]
    for lod in lods:
        spec = export.LODS[lod]
        t0 = time.time()
        if lod == "high":
            # the editable scene carries every detail level; the exported model may carry fewer
            top = export.BLEND_DETAIL if args.detail is None else args.detail
            ctx = build_scene(spec["subsurf"], args.assets, top)
            # fasteners stay in the editable scene but are left out of renders until a picture asks for them
            # (render_figure "detail"). They stay enabled in the viewport: Blender does not work out where a
            # disabled object stands, and the validator has to check them like everything else.
            for ob in ctx.col.objects:
                if ob.get("detail", 0) > export.SHOWN_DETAIL:
                    ob.hide_render = True
            blend = args.blend or os.path.join(args.out, "C172N_realistic.blend")
            bpy.ops.wm.save_as_mainfile(filepath=blend, compress=True)
            bpy.ops.file.make_paths_relative()
            bpy.ops.wm.save_as_mainfile(filepath=blend, compress=True)
            print("saved", blend)
            export.write_json(os.path.join(args.out, "parts_all.json"), export.parts_list(ctx))      # every part, all detail levels
            keep = min(top, spec["detail"])
            if keep < top:
                for ob in list(ctx.col.objects):
                    if ob.get("detail", 0) > keep:
                        bpy.data.objects.remove(ob, do_unlink=True)
        else:
            ctx = build_scene(spec["subsurf"], args.assets, spec["detail"] if args.detail is None else min(args.detail, spec["detail"]))
        if spec["decimate"]:
            export.apply_decimate(ctx, spec["decimate"])
        # shade the cabin and the outside (after the editable scene is saved: it does not carry the baked shade)
        from c172 import ao
        t1 = time.time(); n = ao.bake(list(ctx.col.objects)); print(f"baked shade on {n} vertices in {time.time() - t1:.1f} s")
        export.retarget_textures(tex_dir, spec["tex"])
        glb = os.path.join(args.out, f"C172N_realistic_{lod}.glb")
        export.export_glb(glb, draco=not args.no_draco)
        idx = export.model_index(ctx, lod)
        idx["file"] = os.path.basename(glb); idx["bytes"] = os.path.getsize(glb); idx["build_seconds"] = round(time.time() - t0, 1)
        export.write_json(os.path.join(args.out, f"model_index_{lod}.json"), idx)
        print(f"[{lod}] {idx['objects']} objects, {idx['triangles']} tris, {idx['bytes']/1e6:.1f} MB in {idx['build_seconds']} s")


if __name__ == "__main__":
    main()
