"""LOD preparation, glTF export, model index."""
import json
import os
import bpy

# detail: the highest detail level built into this quality level (see c172/detail/__init__.py):
# 0 basic model, 1 structure and mechanisms, 2 fasteners. The editable .blend always has everything.
LODS = {
    "high":   dict(subsurf=2, tex=2048, decimate=None, detail=1),
    "medium": dict(subsurf=1, tex=1024, decimate=None, detail=1),
    "low":    dict(subsurf=1, tex=512, decimate=0.5, detail=0),
}
BLEND_DETAIL = 2
SHOWN_DETAIL = 1             # parts above this level are hidden in the saved scene until a picture asks for them

def hide_cutters(ctx):
    for ob in ctx.cutters.objects:
        ob.hide_set(True)
        ob.hide_render = True

def apply_decimate(ctx, ratio):
    for ob in ctx.col.objects:
        if ob.type != "MESH" or ob.get("detail", 0) > 0:      # detail parts are already drawn with few faces
            continue
        m = ob.modifiers.new("decimate", "DECIMATE")
        m.ratio = ratio
        m.use_collapse_triangulate = False

def retarget_textures(tex_dir, size):
    """Point every image datablock at the <tex_dir>/<size>/ copy if it exists."""
    for img in bpy.data.images:
        if not img.filepath:
            continue
        base = os.path.basename(img.filepath)
        cand = os.path.join(tex_dir, str(size), base)
        if os.path.exists(cand):
            img.filepath = cand
            img.reload()

def export_glb(path, draco=True):
    bpy.ops.export_scene.gltf(
        filepath=path, export_format="GLB", export_apply=True, export_extras=True, export_yup=True,
        use_visible=True, export_materials="EXPORT", export_image_format="AUTO", export_jpeg_quality=85,
        export_texcoords=True, export_normals=True, export_tangents=False, export_animations=False,
        export_lights=False, export_cameras=False, export_skins=False, export_morph=False,
        export_draco_mesh_compression_enable=draco, export_draco_mesh_compression_level=6,
        export_draco_position_quantization=14, export_draco_normal_quantization=10, export_draco_texcoord_quantization=12,
    )

def _plain(v):
    if hasattr(v, "to_dict"):
        return v.to_dict()
    if hasattr(v, "to_list"):
        return v.to_list()
    return v

def model_index(ctx, lod):
    deps = bpy.context.evaluated_depsgraph_get()
    entries = []
    tris = 0
    for ob in ctx.col.objects:
        if ob.type != "MESH" or ob.hide_get():
            continue
        ev = ob.evaluated_get(deps)
        me = ev.to_mesh()
        t = sum(len(p.vertices) - 2 for p in me.polygons)
        tris += t
        e = {k: _plain(ob[k]) for k in ob.keys() if not k.startswith("_")}
        e.update(name=ob.name, triangles=t, parent=ob.parent.name if ob.parent else None)
        entries.append(e)
        ev.to_mesh_clear()
    systems = {}
    for e in entries:
        systems.setdefault(e.get("system", "?"), 0)
        systems[e.get("system", "?")] += 1
    return {"lod": lod, "objects": len(entries), "triangles": tris, "systems": systems, "parts": entries}

def write_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
