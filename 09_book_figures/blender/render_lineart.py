"""A line drawing of the C172 model for the blueprint-style opening picture: the model alone, every surface one flat white, its outlines and creases drawn by
Freestyle; a transparent background. openers_post.py turns the lines to gold on the cover's deep blue.

    blender -b --factory-startup --python 09_book_figures/blender/render_lineart.py -- --out <png> [--size 2200 1000] [--az 215 --el 28 --lens 60]"""
import argparse
import math
import os
import sys

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
C172 = os.path.dirname(os.path.dirname(HERE))


def main():
    a = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    p = argparse.ArgumentParser()
    p.add_argument("--out", required=True)
    p.add_argument("--size", nargs=2, type=int, default=[2200, 1000])
    p.add_argument("--az", type=float, default=215.0, help="where the camera stands, degrees clockwise from the model's tail-to-nose direction")
    p.add_argument("--el", type=float, default=28.0)
    p.add_argument("--lens", type=float, default=60.0)
    p.add_argument("--dist", type=float, default=21.0)
    p.add_argument("--thickness", type=float, default=2.0)
    a = p.parse_args(a)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    bpy.ops.import_scene.gltf(filepath=os.path.join(C172, "08_realistic_digital_twin", "models", "C172N_realistic_medium.glb"))
    mat = bpy.data.materials.new("flat")
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (1, 1, 1, 1)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(em.outputs[0], out.inputs["Surface"])
    lo, hi = Vector((1e9, 1e9, 1e9)), Vector((-1e9, -1e9, -1e9))
    for o in bpy.data.objects:
        if o.type == "MESH":
            o.data.materials.clear()
            o.data.materials.append(mat)
            for c in o.bound_box:
                w = o.matrix_world @ Vector(c)
                lo, hi = Vector(map(min, lo, w)), Vector(map(max, hi, w))
    mid = (lo + hi) / 2
    cam_d = bpy.data.cameras.new("cam")
    cam = bpy.data.objects.new("cam", cam_d)
    sc.collection.objects.link(cam)
    az, el = math.radians(a.az), math.radians(a.el)
    # the nose points along -y: azimuth 180 looks at the model from straight ahead
    cam.location = mid + Vector((math.sin(az) * math.cos(el), math.cos(az) * math.cos(el), math.sin(el))) * a.dist
    cam.rotation_euler = (mid - cam.location).to_track_quat("-Z", "Y").to_euler()
    cam_d.lens = a.lens
    sc.camera = cam
    sc.render.resolution_x, sc.render.resolution_y = a.size
    sc.render.engine = "CYCLES"
    sc.cycles.samples = 4
    sc.render.film_transparent = True
    sc.view_settings.view_transform = "Standard"
    sc.render.use_freestyle = True
    sc.render.line_thickness = a.thickness
    vl = bpy.context.view_layer
    vl.use_freestyle = True
    fs = vl.freestyle_settings
    fs.crease_angle = math.radians(138.0)
    ls = fs.linesets.new("lines") if not fs.linesets else fs.linesets[0]
    ls.select_silhouette = True
    ls.select_border = True
    ls.select_crease = True
    ls.select_material_boundary = False
    ls.select_edge_mark = False
    if ls.linestyle is None:
        ls.linestyle = bpy.data.linestyles.new("ink")
    ls.linestyle.color = (0, 0, 0)
    ls.linestyle.thickness = a.thickness
    sc.render.filepath = a.out
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGBA"
    bpy.ops.render.render(write_still=True)
    print("lineart", a.out)


main()
