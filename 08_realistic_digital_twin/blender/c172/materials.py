"""Principled-BSDF materials wired to the generated textures (glTF-compatible)."""
import os
import bpy

_images = {}

def image(path, noncolor=False):
    key = (os.path.abspath(path), noncolor)
    if key in _images:
        return _images[key]
    img = bpy.data.images.load(os.path.abspath(path), check_existing=True)
    img.colorspace_settings.name = "Non-Color" if noncolor else "sRGB"
    _images[key] = img
    return img

def _gltf_output_group():
    g = bpy.data.node_groups.get("glTF Material Output")
    if g is None:
        g = bpy.data.node_groups.new("glTF Material Output", "ShaderNodeTree")
        g.interface.new_socket("Occlusion", in_out="INPUT", socket_type="NodeSocketFloat")
        g.nodes.new("NodeGroupInput")
    return g

def pbr(name, albedo=None, orm=None, normal=None, color=(0.8, 0.8, 0.8, 1.0), rough=0.5, metal=0.0,
        alpha=1.0, normal_strength=1.0, emission=None, emission_strength=0.0, tile=1.0, double_sided=False,
        specular=0.5, clearcoat=0.0, normal_tile=None):
    """tile repeats every texture; normal_tile, if given, repeats the normal map on its own (a painted colour
    map that covers the part once, with a fine grain tiled over it)."""
    mat = bpy.data.materials.get(name)
    if mat:
        return mat
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    bsdf.inputs["Alpha"].default_value = alpha
    bsdf.inputs["IOR"].default_value = 1.5
    if "Specular IOR Level" in bsdf.inputs:
        bsdf.inputs["Specular IOR Level"].default_value = specular
    if clearcoat and "Coat Weight" in bsdf.inputs:
        bsdf.inputs["Coat Weight"].default_value = clearcoat
    mappings = {}
    def mapped(scale):
        if scale == 1.0:
            return None
        if scale not in mappings:
            tc = nt.nodes.new("ShaderNodeTexCoord"); m = nt.nodes.new("ShaderNodeMapping")
            m.inputs["Scale"].default_value = (scale, scale, 1)
            nt.links.new(tc.outputs["UV"], m.inputs["Vector"])
            mappings[scale] = m
        return mappings[scale]
    def tex(path, nc, scale=None):
        n = nt.nodes.new("ShaderNodeTexImage"); n.image = image(path, nc)
        m = mapped(tile if scale is None else scale)
        if m is not None:
            nt.links.new(m.outputs["Vector"], n.inputs["Vector"])
        return n
    if albedo:
        t = tex(albedo, False); nt.links.new(t.outputs["Color"], bsdf.inputs["Base Color"])
        if alpha < 1.0:
            nt.links.new(t.outputs["Alpha"], bsdf.inputs["Alpha"])
    if orm:
        t = tex(orm, True)
        sep = nt.nodes.new("ShaderNodeSeparateColor")
        nt.links.new(t.outputs["Color"], sep.inputs["Color"])
        nt.links.new(sep.outputs["Green"], bsdf.inputs["Roughness"])
        nt.links.new(sep.outputs["Blue"], bsdf.inputs["Metallic"])
        grp = nt.nodes.new("ShaderNodeGroup"); grp.node_tree = _gltf_output_group()
        nt.links.new(sep.outputs["Red"], grp.inputs["Occlusion"])
    if normal:
        t = tex(normal, True, normal_tile)
        nm = nt.nodes.new("ShaderNodeNormalMap"); nm.inputs["Strength"].default_value = normal_strength
        nt.links.new(t.outputs["Color"], nm.inputs["Color"])
        nt.links.new(nm.outputs["Normal"], bsdf.inputs["Normal"])
    if emission is not None:
        bsdf.inputs["Emission Color"].default_value = emission
        bsdf.inputs["Emission Strength"].default_value = emission_strength
    if alpha < 1.0:
        mat.surface_render_method = "BLENDED"
        mat.show_transparent_back = False
    mat.use_backface_culling = not double_sided
    return mat

def build_library(tex_dir):
    _images.clear()          # a new factory scene invalidates cached Image references
    T = lambda n: os.path.join(tex_dir, n)
    M = {}
    M["fuselage"] = pbr("skin_fuselage", T("fuselage_albedo.jpg"), T("fuselage_orm.jpg"), T("fuselage_normal.png"), clearcoat=0.15)
    M["wing"] = pbr("skin_wing", T("wing_albedo.jpg"), T("wing_orm.jpg"), T("wing_normal.png"), clearcoat=0.15)
    M["fin"] = pbr("skin_fin", T("fin_albedo.jpg"), T("fin_orm.jpg"), T("fin_normal.png"), clearcoat=0.15)
    M["stab"] = pbr("skin_stab", T("stab_albedo.jpg"), T("stab_orm.jpg"), T("stab_normal.png"), clearcoat=0.15)
    M["control"] = pbr("skin_control", T("control_albedo.jpg"), T("control_orm.jpg"), T("control_normal.png"), clearcoat=0.15)
    M["cowl"] = pbr("skin_cowl", T("cowl_albedo.jpg"), T("cowl_orm.jpg"), T("cowl_normal.png"), clearcoat=0.15)
    M["rudder"] = pbr("skin_rudder", T("rudder_albedo.jpg"), T("control_orm.jpg"), T("control_normal.png"), clearcoat=0.15)      # the band of the fin carries on across it
    M["metal"] = pbr("metal_aluminium", T("metal_albedo.jpg"), T("metal_orm.jpg"), T("metal_normal.png"), tile=2.0)
    M["rubber"] = pbr("rubber_tyre", T("rubber_albedo.jpg"), T("rubber_orm.jpg"), T("rubber_normal.png"), tile=1.0)
    M["apron"] = pbr("apron_asphalt", T("apron_albedo.jpg"), T("apron_orm.jpg"), T("apron_normal.png"), tile=12.0)
    M["apron"].use_fake_user = True      # no part uses it: keep it in the saved scene for the ground of the reference renders
    M["paint_white"] = pbr("paint_white", color=(0.90, 0.90, 0.89, 1), rough=0.38, clearcoat=0.1)
    M["paint_navy"] = pbr("paint_navy", color=(0.06, 0.13, 0.32, 1), rough=0.35, clearcoat=0.2)
    M["glass"] = pbr("glass_acrylic", color=(0.35, 0.45, 0.52, 1), rough=0.03, alpha=0.22, specular=0.9, double_sided=True)
    M["instrument_glass"] = pbr("instrument_glass", color=(0.6, 0.65, 0.7, 1), rough=0.02, alpha=0.12, specular=0.9, double_sided=True)
    M["black_plastic"] = pbr("black_plastic", color=(0.03, 0.03, 0.03, 1), rough=0.55)
    M["grey_plastic"] = pbr("grey_plastic", color=(0.45, 0.45, 0.44, 1), rough=0.6)
    M["steel"] = pbr("steel_dark", color=(0.45, 0.45, 0.47, 1), rough=0.35, metal=1.0)
    M["chrome"] = pbr("chrome", color=(0.9, 0.9, 0.9, 1), rough=0.12, metal=1.0)
    M["exhaust"] = pbr("exhaust_steel", color=(0.35, 0.30, 0.27, 1), rough=0.7, metal=0.8)
    M["nav_red"] = pbr("lens_red", color=(0.9, 0.05, 0.05, 1), rough=0.1, alpha=0.8, emission=(1, 0.1, 0.1, 1), emission_strength=0.0)
    M["nav_green"] = pbr("lens_green", color=(0.05, 0.8, 0.2, 1), rough=0.1, alpha=0.8, emission=(0.1, 1, 0.2, 1), emission_strength=0.0)
    M["nav_white"] = pbr("lens_white", color=(0.95, 0.95, 0.95, 1), rough=0.1, alpha=0.8, emission=(1, 1, 1, 1), emission_strength=0.0)
    M["interior_dark"] = pbr("interior_dark", color=(0.12, 0.11, 0.10, 1), rough=0.8, double_sided=True)
    # the cabin trim: vinyl with a leather grain, woven cloth on the seat inserts, cut-pile carpet, a perforated headliner.
    # The walls carry a painted map (carpet low down, tan to the sills, cream above) with the grain tiled over it.
    M["interior_tan"] = pbr("interior_tan", T("vinyl_tan_albedo.jpg"), normal=T("vinyl_tan_normal.jpg"), rough=0.66, tile=9.0, double_sided=True)
    M["liner"] = pbr("cabin_liner", T("liner_albedo.jpg"), normal=T("vinyl_tan_normal.jpg"), rough=0.70, normal_tile=30.0, normal_strength=0.8, double_sided=True)
    M["vinyl_cream"] = pbr("vinyl_cream", T("vinyl_cream_albedo.jpg"), normal=T("vinyl_cream_normal.jpg"), rough=0.68, tile=9.0, double_sided=True)
    M["headliner"] = pbr("headliner", T("headliner_albedo.jpg"), normal=T("headliner_normal.jpg"), rough=0.78, tile=26.0, double_sided=True)
    M["cloth"] = pbr("seat_cloth", T("cloth_brown_albedo.jpg"), normal=T("cloth_brown_normal.jpg"), rough=0.92, tile=12.0)
    M["carpet"] = pbr("carpet_grey", T("carpet_albedo.jpg"), normal=T("carpet_normal.jpg"), rough=0.97, tile=28.0)
    M["cast_alu"] = pbr("cast_aluminium", color=(0.62, 0.63, 0.64, 1), rough=0.55, metal=0.9)
    M["lycoming_grey"] = pbr("engine_enamel_grey", color=(0.55, 0.57, 0.58, 1), rough=0.45, metal=0.3)
    M["bare_alu"] = pbr("bare_aluminium", color=(0.78, 0.79, 0.80, 1), rough=0.3, metal=1.0)
    M["brass"] = pbr("brass", color=(0.75, 0.6, 0.3, 1), rough=0.35, metal=1.0)
    M["hose_black"] = pbr("hose_black", color=(0.05, 0.05, 0.05, 1), rough=0.75)
    M["hose_blue"] = pbr("hose_blue", color=(0.1, 0.25, 0.7, 1), rough=0.5)
    M["hose_red"] = pbr("hose_red", color=(0.6, 0.08, 0.06, 1), rough=0.5)
    M["wire_yellow"] = pbr("wire_yellow", color=(0.85, 0.75, 0.1, 1), rough=0.5)
    M["copper"] = pbr("copper", color=(0.85, 0.5, 0.35, 1), rough=0.4, metal=1.0)
    M["leather_tan"] = pbr("leather_tan", T("vinyl_tan_albedo.jpg"), normal=T("vinyl_tan_normal.jpg"), rough=0.60, tile=8.0)
    M["vinyl_black"] = pbr("vinyl_black", T("vinyl_black_albedo.jpg"), normal=T("vinyl_black_normal.jpg"), rough=0.58, tile=9.0)
    M["panel_grey"] = pbr("panel_grey", T("panel_black_albedo.jpg"), normal=T("panel_black_normal.jpg"), rough=0.55, tile=11.0)      # the black wrinkle finish of the panel
    M["screw"] = pbr("screw_black_oxide", color=(0.10, 0.10, 0.11, 1), rough=0.35, metal=0.9)
    M["woodgrain"] = pbr("woodgrain", color=(0.30, 0.17, 0.08, 1), rough=0.45, clearcoat=0.3)
    M["bezel_black"] = pbr("bezel_black", color=(0.05, 0.05, 0.05, 1), rough=0.4)
    M["knob_red"] = pbr("knob_red", color=(0.8, 0.05, 0.05, 1), rough=0.4)
    M["prop_black"] = pbr("prop_black", color=(0.022, 0.022, 0.025, 1), rough=0.66)                       # the face toward the pilot: flat black, against glare
    M["prop_face"] = pbr("prop_face", color=(0.050, 0.052, 0.056, 1), rough=0.38)                            # the forward face: black with a sheen
    M["prop_tip"] = pbr("prop_tip_yellow", color=(0.93, 0.70, 0.05, 1), rough=0.45)
    M["belt"] = pbr("seatbelt_webbing", color=(0.25, 0.27, 0.32, 1), rough=0.9)
    M["dials"] = pbr("instrument_dials", T("dials.png"), rough=0.6)
    M["dials_alpha"] = pbr("instrument_dials_alpha", T("dials.png"), rough=0.6, alpha=0.999, double_sided=True)
    M["panel_misc"] = pbr("panel_misc", T("panel_misc.png"), rough=0.5)
    M["placards"] = pbr("panel_placards", T("panel_placards.png"), rough=0.6, alpha=0.999, double_sided=True)      # white lettering laid on the panel
    M["decals"] = pbr("markings", T("decals.png"), rough=0.34, alpha=0.999, clearcoat=0.15)                          # paint laid on the skin as separate pieces
    return M
