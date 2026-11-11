"""The clouds of the handbook's weather figures: recipes for blender/render_clouds.py (one render on a transparent ground for each, renders/<id>.png),
which a re-skinned figure lays on its scene as it lays the aeroplane (a sprite overlay naming the id, see reskin.py).

    kind      cumulus | congestus | cb | anvil | stratus | altocumulus | cirrus | lenticular | roll        the other keys are described at the top of render_clouds.py
Plain Python (no Blender, no Pillow): the plate checks read it."""


def clouds():
    return [
        {"id": "cloud-cumulus-a", "kind": "cumulus", "seed": 3, "width": 9.0, "height": 4.0, "floor": True},
        {"id": "cloud-cumulus-b", "kind": "cumulus", "seed": 8, "width": 6.0, "height": 3.2, "floor": True},
        {"id": "cloud-congestus", "kind": "congestus", "seed": 5, "width": 5.0, "height": 9.0, "floor": True},
        {"id": "cloud-cb", "kind": "cb", "seed": 11, "width": 6.0, "height": 13.0, "anvil": 12.5, "floor": True, "absorb": 0.42, "absorb_top": 8.0, "pixels": 1200},
        {"id": "cloud-cb-wide", "kind": "cb", "seed": 31, "width": 7.5, "height": 9.0, "anvil": 13.0, "floor": True, "absorb": 0.4, "absorb_top": 6.0, "pixels": 1200},
        {"id": "cloud-tcu", "kind": "congestus", "seed": 17, "width": 2.4, "height": 10.0, "girth": 0.62, "floor": True, "pixels": 480, "samples": 40},
        {"id": "cloud-cb-tall", "kind": "cb", "seed": 23, "width": 3.2, "height": 24.0, "anvil": 11.0, "girth": 0.62, "floor": True, "absorb": 0.45, "absorb_top": 14.0, "pixels": 700, "samples": 48},
        {"id": "cloud-anvil", "kind": "anvil", "seed": 4, "width": 14.0, "height": 3.0, "density": 9.0, "pixels": 1200},
        {"id": "cloud-stratus", "kind": "stratus", "seed": 6, "width": 18.0, "height": 1.4, "density": 5.0, "erode": [0.38, 0.66], "absorb": 0.18, "absorb_top": 2.5, "pixels": 1200},
        {"id": "cloud-altocumulus", "kind": "altocumulus", "seed": 2, "width": 16.0, "rows": 3, "density": 9.0, "pixels": 1200},
        {"id": "cloud-lenticular", "kind": "lenticular", "seed": 1, "width": 8.0, "layers": 3, "density": 9.0, "noise": 10.0, "erode": [0.18, 0.5], "stretch": 3.0, "pixels": 1200},
        {"id": "cloud-veil", "kind": "stratus", "seed": 12, "width": 18.0, "height": 0.9, "density": 1.6, "erode": [0.25, 0.6], "pixels": 1200},
        {"id": "cloud-nimbostratus", "kind": "stratus", "seed": 14, "width": 16.0, "height": 2.2, "density": 9.0, "absorb": 0.5, "absorb_top": 2.2, "pixels": 1200},
        {"id": "cloud-stratocumulus", "kind": "roll", "seed": 7, "width": 16.0, "height": 1.2, "density": 10.0, "floor": True, "pixels": 1200},
        {"id": "cloud-roll", "kind": "roll", "seed": 21, "width": 7.0, "height": 1.4, "density": 12.0, "floor": True, "absorb": 0.3, "absorb_top": 3.0, "pixels": 1200},
        {"id": "cloud-cirrus", "kind": "cirrus", "seed": 9, "width": 14.0, "wisps": 6, "density": 5.0, "stretch": 5.0, "pixels": 1300},
    ]
