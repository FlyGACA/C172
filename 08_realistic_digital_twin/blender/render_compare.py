"""Render a previous-phase GLB with the Phase 8 camera presets for before/after comparisons.
    blender -b --python blender/render_compare.py -- --glb 07_kinematic_twin/C172N_Phase7_Kinematic_Twin.glb --out docs/renders --prefix phase7_ --views front_quarter,engine
"""
import os, sys, runpy
import bpy
argv = sys.argv[sys.argv.index("--") + 1:]
glb = argv[argv.index("--glb") + 1]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=os.path.abspath(glb))
# drop the --glb pair so render_preview's parser does not see it
i = argv.index("--glb"); del argv[i:i + 2]
sys.argv = [sys.argv[0], "--"] + argv
runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), "render_preview.py"), run_name="__main__")
