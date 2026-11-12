"""The clouds of the handbook's weather figures: recipes for blender/render_clouds.py (one render on a transparent ground for each, renders/<id>.png),
which a re-skinned figure lays on its scene as it lays the aeroplane (a sprite overlay naming the id, see reskin.py).

    kind      cumulus | congestus | cb | anvil | stratus | nimbostratus | veil | altocumulus | stratocumulus | cirrus | lenticular | roll       the other keys are described at the top of render_clouds.py
Plain Python (no Blender, no Pillow): the plate checks read it."""


def clouds():
    """Each cloud: its kind and shape (see render_clouds.py), and its picture: `pixels` wide, `samples` path tracing samples (the widest a figure lays it, times four, is what it needs)."""
    return [
        {"id": "cloud-cumulus-a", "kind": "cumulus", "seed": 3, "width": 9.0, "height": 4.0, "floor": True, "voxel": 0.0065, "pixels": 700, "samples": 128},
        {"id": "cloud-cumulus-b", "kind": "cumulus", "seed": 8, "width": 6.0, "height": 3.2, "floor": True, "voxel": 0.0065, "pixels": 520, "samples": 128},
        {"id": "cloud-congestus", "kind": "congestus", "seed": 5, "width": 5.0, "height": 9.0, "floor": True, "pixels": 720, "samples": 96},
        {"id": "cloud-cb", "kind": "cb", "seed": 11, "width": 8.0, "height": 13.5, "anvil": 15.5, "lean": 0.06, "floor": True, "absorb": 0.30, "absorb_top": 9.0, "band": 0.012, "voxel": 0.004, "pixels": 1300, "samples": 72},
        {"id": "cloud-cb-wide", "kind": "cb", "seed": 31, "width": 9.0, "height": 10.0, "anvil": 15.0, "lean": 0.12, "floor": True, "absorb": 0.28, "absorb_top": 7.0, "band": 0.012, "voxel": 0.004, "pixels": 800, "samples": 80},
        {"id": "cloud-stormbase", "kind": "cumulus", "seed": 41, "width": 14.0, "height": 5.0, "floor": True, "absorb": 0.50, "absorb_top": 5.0, "absorb_white": 0.66, "ambient": 0.40, "fill": 0.4, "voxel": 0.0065, "pixels": 900, "samples": 96},
        {"id": "cloud-tcu", "kind": "congestus", "seed": 17, "width": 2.4, "height": 10.0, "girth": 0.62, "floor": True, "pixels": 360, "samples": 112},
        {"id": "cloud-cb-tall", "kind": "cb", "seed": 23, "width": 5.2, "height": 24.0, "anvil": 13.5, "lean": 0.1, "girth": 0.85, "floor": True, "absorb": 0.32, "absorb_top": 15.0, "band": 0.012, "voxel": 0.004, "pixels": 700, "samples": 72},
        {"id": "cloud-anvil", "kind": "anvil", "seed": 4, "width": 14.0, "height": 3.0, "band": 0.012, "voxel": 0.004, "pixels": 900, "samples": 96},
        {"id": "cloud-stratus", "kind": "stratus", "seed": 6, "width": 18.0, "height": 2.4, "depth": 4.0, "density": 12.0, "erode": [0.32, 0.6], "ragged": 0.5, "gaps": [0.30, 0.55], "gap_floor": 0.30, "taper": 8.0, "end_fade": 0.35, "absorb": 0.40, "absorb_white": 0.88, "pixels": 900, "samples": 200},
        {"id": "cloud-altocumulus", "kind": "altocumulus", "seed": 2, "width": 16.0, "depth": 2.2, "rows": 2, "per_row": 6, "elevation": 6.0, "noise": 70.0, "ambient": 0.42, "fill": 0.35, "absorb": 0.18, "absorb_top": 1.3, "pixels": 900, "samples": 128},
        {"id": "cloud-lenticular", "kind": "lenticular", "seed": 1, "width": 8.0, "layers": 3, "lens_density": 25.0, "lens_erode": [0.22, 0.5], "band": 0.012, "voxel": 0.004, "pixels": 800, "samples": 128},
        {"id": "cloud-veil", "kind": "veil", "seed": 12, "width": 18.0, "height": 1.7, "depth": 1.2, "density": 3.0, "erode": [0.28, 0.5], "fibre": 0.22, "haze": 0.55, "gaps": [0.22, 0.5], "gap_floor": 0.25, "taper": 8.0, "end_fade": 0.4, "pixels": 1400, "samples": 200},
        {"id": "cloud-nimbostratus", "kind": "nimbostratus", "seed": 14, "width": 16.0, "height": 3.6, "depth": 4.0, "density": 22.0, "erode": [0.30, 0.55], "ragged": 0.7, "gaps": [0.15, 0.4], "gap_floor": 0.6, "taper": 8.0, "end_fade": 0.35, "lens": 0.8, "absorb": 0.62, "absorb_white": 0.72, "noise": 14.0, "detail": 6.0, "roughness": 0.55, "pixels": 1000, "samples": 200},
        {"id": "cloud-stratocumulus", "kind": "stratocumulus", "seed": 7, "width": 16.0, "depth": 2.0, "rows": 2, "per_row": 5, "elevation": 6.0, "noise": 60.0, "ambient": 0.40, "fill": 0.30, "absorb": 0.22, "absorb_top": 1.4, "pixels": 800, "samples": 128},
        {"id": "cloud-roll", "kind": "roll", "seed": 21, "width": 7.0, "height": 0.9, "floor": True, "absorb": 0.25, "absorb_top": 3.0, "pixels": 600, "samples": 128},
        {"id": "cloud-cirrus", "kind": "cirrus", "seed": 9, "width": 14.0, "height": 3.5, "depth": 0.8, "density": 16.0, "erode": [0.25, 0.5], "stretch": 6.0, "fibre": 0.12, "gaps": [0.40, 0.62], "taper": 6.0, "end_fade": 0.4, "curl": 0.9, "pixels": 900, "samples": 240},
    ]
