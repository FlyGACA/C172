"""Use any part of the model on its own: list the parts, draw one, or export one (run inside Blender).

    blender -b 08_realistic_digital_twin/models/C172N_realistic.blend --python 09_book_figures/blender/part.py -- <command> ...

    list   [--out parts.json]
        Every part with its id, English and Arabic name, system, detail level, status and size.

    render --part ID [ID ...] [--context] [--name NAME] [--out DIR] [--size 1600x1200]
           [--azimuth 35] [--elevation 22] [--frame part|aircraft] [--tint #8DB7E2] [--quick]
        Draws the named parts in the style of the book figures, on a transparent background.
        --context draws the rest of the aircraft round them as a phantom, so the reader sees where
        the part sits; --frame aircraft then keeps the whole aircraft in the picture.

    export --part ID [ID ...] --out FILE.glb [--centre]
        Writes the named parts as a GLB, where they are in the aircraft or (--centre) at the origin.

An ID is the name of a part ("ENGINE.piston_1"), of a group ("WING_L": the group and everything in
it), a pattern ("WING_L.rib_*"), an assembly ("@aileron_control": every part of the aileron control
run, wherever it is) or a system ("system:FUEL"). Whatever is parented to a named part comes with it.
"""
import argparse
import json
import os
import sys

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import render_figure as RF          # noqa: E402


def triangles(ob, deps):
    evaluated = ob.evaluated_get(deps)
    mesh = evaluated.to_mesh()
    count = sum(len(p.vertices) - 2 for p in mesh.polygons)
    box = [evaluated.matrix_world @ Vector(c) for c in evaluated.bound_box]
    size = [round(max(c[i] for c in box) - min(c[i] for c in box), 4) for i in range(3)]
    evaluated.to_mesh_clear()
    return count, size


def command_list(args):
    deps = bpy.context.evaluated_depsgraph_get()
    parts = []
    for ob in sorted(bpy.data.objects, key=lambda o: o.name):
        if ob.name.startswith("_") or "system" not in ob:
            continue
        entry = dict(id=ob.name, group=bool(ob.get("group", False)), system=ob.get("system", ""), label_en=ob.get("label_en", ""),
                     label_ar=ob.get("label_ar", ""), parent=ob.parent.name if ob.parent else None)
        if ob.type == "MESH":
            count, size = triangles(ob, deps)
            entry.update(detail=int(ob.get("detail", 0)), status=ob.get("status", ""), triangles=count, size_m=size)
            for key in ("ref", "note", "station_in"):
                if key in ob:
                    entry[key] = ob[key]
        parts.append(entry)
    meshes = [p for p in parts if not p["group"]]
    summary = dict(model=os.path.basename(bpy.data.filepath), parts=len(meshes), by_detail={}, by_system={})
    for p in meshes:
        summary["by_detail"][str(p.get("detail", 0))] = summary["by_detail"].get(str(p.get("detail", 0)), 0) + 1
        summary["by_system"][p["system"]] = summary["by_system"].get(p["system"], 0) + 1
    payload = dict(summary=summary, parts=parts)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as stream:
            json.dump(payload, stream, ensure_ascii=False, indent=1)
            stream.write("\n")
        print(f"part: {len(meshes)} parts listed in {args.out}")
    else:
        for p in meshes:
            print(f"{p['id']:<46} {p['system']:<12} detail {p.get('detail', 0)}  {p['label_en']}")
    print("part:", json.dumps(summary))


def command_render(args):
    width, height = (int(v) for v in args.size.lower().split("x"))
    name = args.name or args.part[0].replace("*", "all").replace(".", "_").replace("/", "_")
    phantoms = RF.resolve(args.ghost, hidden=True) if args.ghost else []
    chosen = [ob for ob in RF.resolve(args.part, hidden=True) if ob not in phantoms]
    for ob in chosen + phantoms:                        # a part of the upper detail levels may be hidden in the saved scene
        ob.hide_render = False
        ob.hide_viewport = False
    chosen_names = [ob.name for ob in chosen]
    spec = dict(id=name, resolution=[width, height], samples=args.samples, ground_shadow=False, anchors=[],
                ink=dict(outer_px=4.2, part_px=2.2, fine_px=1.4), only=chosen_names,
                camera=dict(type="auto", azimuth_deg=args.azimuth, elevation_deg=args.elevation, fov=args.fov, margin=args.margin))
    if any(RF.is_picture_sheet(ob) for ob in chosen):   # a marking asked for by name is drawn
        spec["markings"] = True
    if args.tint:
        spec["highlights"] = [dict(key="part", ids=chosen_names, color=args.tint)]
    if args.grow:
        spec["grow"] = [dict(ids=chosen_names, by=args.grow)]
    if args.target:
        spec["camera"]["target"] = args.target
    if args.distance:
        spec["camera"]["distance"] = args.distance
    if phantoms:
        spec["ghost"] = [ob.name for ob in phantoms]
    if args.context:
        keep = set(chosen_names) | set(spec.get("ghost", []))
        spec["ghost"] = spec.get("ghost", []) + [
            ob.name for ob in bpy.data.objects
            if ob.type == "MESH" and not ob.hide_render and ob.name not in keep and not ob.name.startswith("_") and int(ob.get("detail", 0)) == 0
            and ob.get("system") not in ("INTERIOR", "PANEL")]
        if args.frame == "part":
            spec["camera"]["of"] = chosen_names
    else:
        spec["camera"]["of"] = chosen_names
    if args.focus:
        spec["camera"]["of"] = [ob.name for ob in RF.resolve(args.focus, hidden=True)]
    os.makedirs(args.out, exist_ok=True)
    RF.render_one(spec, argparse.Namespace(out=args.out, quick=args.quick, anchors_only=False, keep=False))
    stem = os.path.join(args.out, name + ("_quick" if args.quick else ""))
    if os.path.exists(stem + ".anchors.json"):
        os.remove(stem + ".anchors.json")
    with open(stem + ".json", "w", encoding="utf-8") as stream:
        json.dump(dict(picture=os.path.basename(stem) + ".png", parts=[dict(id=ob.name, label_en=ob.get("label_en", ""), label_ar=ob.get("label_ar", ""),
                                                                           system=ob.get("system", ""), status=ob.get("status", "")) for ob in chosen]),
                  stream, ensure_ascii=False, indent=1)
        stream.write("\n")


def command_export(args):
    chosen = RF.resolve(args.part, hidden=True)
    bpy.ops.object.select_all(action="DESELECT")
    for ob in bpy.data.objects:
        ob.hide_set(ob not in chosen)
    for ob in chosen:
        ob.hide_viewport = False
        ob.hide_render = False
        ob.hide_set(False)
        ob.select_set(True)
    if args.centre:
        centre, _radius = RF.scene_bounds(chosen)
        roots = [ob for ob in chosen if ob.parent not in chosen]
        for ob in roots:
            world = ob.matrix_world.copy()
            ob.parent = None
            ob.matrix_world = world
            ob.matrix_world.translation -= centre
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    bpy.ops.export_scene.gltf(filepath=args.out, export_format="GLB", use_selection=True, export_apply=True, export_extras=True, export_yup=True,
                              export_materials="EXPORT", export_cameras=False, export_lights=False, export_animations=False)
    print(f"part: {len(chosen)} object(s) written to {args.out} ({os.path.getsize(args.out) / 1e3:.0f} kB)")


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    parser = argparse.ArgumentParser(prog="part.py")
    sub = parser.add_subparsers(dest="command", required=True)
    listing = sub.add_parser("list")
    listing.add_argument("--out")
    render = sub.add_parser("render")
    render.add_argument("--part", nargs="+", required=True)
    render.add_argument("--context", action="store_true", help="draw the rest of the aircraft as a phantom")
    render.add_argument("--ghost", nargs="+", metavar="ID", help="draw these parts as a phantom: a case round its mechanism, a skin over its structure")
    render.add_argument("--frame", choices=("part", "aircraft"), default="part")
    render.add_argument("--name")
    render.add_argument("--out", default=os.path.join(RF.ROOT, "parts"))
    render.add_argument("--size", default="1600x1200")
    render.add_argument("--samples", type=int, default=64)
    render.add_argument("--azimuth", type=float, default=35.0)
    render.add_argument("--elevation", type=float, default=22.0)
    render.add_argument("--fov", type=float, default=24.0)
    render.add_argument("--margin", type=float, default=1.05, help="room round the parts: 1 fits their bounding sphere to the shorter side of the picture")
    render.add_argument("--tint", help="colour for the part, e.g. #8DB7E2")
    render.add_argument("--grow", type=float, help="draw the parts this much thicker (m), for cables and pipes seen from far away")
    render.add_argument("--focus", nargs="+", metavar="ID", help="fit the picture to these parts (default: to all the parts drawn)")
    render.add_argument("--target", type=float, nargs=3, metavar=("X", "Y", "Z"), help="look at this point (m) instead of the middle of the parts")
    render.add_argument("--distance", type=float, help="camera distance from the target (m) instead of fitting the parts")
    render.add_argument("--detail", type=int, choices=(0, 1, 2), help="with --context: also show the parts up to this detail level that are not named (2 = with the fasteners)")
    render.add_argument("--quick", action="store_true")
    export = sub.add_parser("export")
    export.add_argument("--part", nargs="+", required=True)
    export.add_argument("--out", required=True)
    export.add_argument("--centre", action="store_true")
    args = parser.parse_args(argv)
    {"list": command_list, "render": command_render, "export": command_export}[args.command](args)


if __name__ == "__main__":
    main()
