"""LOD preparation, glTF export, model index."""
import json
import os
import bpy

# detail: the highest detail level built into this quality level (see c172/detail/__init__.py):
# 0 basic model, 1 structure and mechanisms, 2 fasteners. The editable .blend always has everything;
# the web model has what lies under the skin in its high quality level only, so that the medium and
# low levels stay light enough for tablets and phones.
LODS = {
    "high":   dict(subsurf=2, tex=2048, decimate=None, detail=1),
    "medium": dict(subsurf=1, tex=1024, decimate=None, detail=0),
    "low":    dict(subsurf=1, tex=1024, decimate=0.5, detail=0),
}
BLEND_DETAIL = 2
SHOWN_DETAIL = 1             # parts above this level are hidden in the saved scene until a picture asks for them

def hide_cutters(ctx):
    for ob in ctx.cutters.objects:
        ob.hide_set(True)
        ob.hide_render = True

def apply_decimate(ctx, ratio):
    for ob in ctx.col.objects:
        if ob.type != "MESH" or ob.get("detail", 0) > 0 or ob.get("keep_faces"):      # detail parts are already drawn with few faces; a marking's texels are its picture
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
        export_draco_position_quantization=14, export_draco_normal_quantization=10, export_draco_texcoord_quantization=14,
        # the baked shade (c172/ao.py) travels as the vertex colour
        export_vertex_color="ACTIVE", export_all_vertex_colors=False, export_active_vertex_color_when_no_material=False, export_draco_color_quantization=8,
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

def parts_list(ctx):
    """Every part of the editable scene, all detail levels: what part.py and the parts index work from."""
    deps = bpy.context.evaluated_depsgraph_get()
    parts = []
    for ob in sorted(ctx.col.objects, key=lambda o: o.name):
        if "system" not in ob:
            continue
        entry = dict(id=ob.name, system=ob.get("system", ""), en=ob.get("label_en", ""), ar=ob.get("label_ar", ""), parent=ob.parent.name if ob.parent else None)
        if ob.get("group"):
            entry["group"] = True
        if ob.type == "MESH":
            mesh = ob.evaluated_get(deps).to_mesh()
            entry.update(detail=int(ob.get("detail", 0)), status=ob.get("status", ""), triangles=sum(len(p.vertices) - 2 for p in mesh.polygons))
            ob.evaluated_get(deps).to_mesh_clear()
            for key in ("assembly", "ref", "note", "count", "station_in", "optional", "kit"):
                if key in ob:
                    entry[key] = _plain(ob[key])
        parts.append(entry)
    meshes = [p for p in parts if "detail" in p]
    summary = dict(parts=len(meshes), by_detail={}, by_system={}, assemblies={})
    for p in meshes:
        summary["by_detail"][str(p["detail"])] = summary["by_detail"].get(str(p["detail"]), 0) + 1
        summary["by_system"][p["system"]] = summary["by_system"].get(p["system"], 0) + 1
        for name in str(p.get("assembly", "")).split(","):
            if name:
                summary["assemblies"][name] = summary["assemblies"].get(name, 0) + 1
    for key in summary:
        if isinstance(summary[key], dict):
            summary[key] = dict(sorted(summary[key].items()))
    return dict(summary=summary, parts=parts)

def write_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
