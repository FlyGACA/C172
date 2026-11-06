Cessna 172 — Editable 3D Starter Model
====================================
Included:
- Cessna_172_Editable.glb: import into Blender, Unity, Unreal (with glTF plugin), or compatible 3D software.
- Build_Editable_Cessna172.py: fully editable Python/trimesh procedural source; change geometry, sizes, coordinates and colors, then rerun.

Model includes 141 separate named geometries: high wings, flap surfaces, ailerons, fixed horizontal stabilizers, elevators, vertical fin and rudder, wing struts, three fixed landing gear, spinner and two propeller blades, cabin windows and doors, seats, yokes, instrument panel with six gauges per side, radio stack, throttle and mixture.

IMPORTANT LIMITATIONS:
- Artistic reference model, not an accurately reverse-engineered Cessna model.
- Exterior and cabin inferred from several supplied photos. The supplied photos show more than one aircraft and panel layout; they cannot establish an exact serial-number-specific C172.
- Panel, airfoils, engine, landing gear geometry, UV/textures and fasteners are approximate; not for engineering, flight training dynamics, manufacturing or flight simulation certification.
- Individual named meshes can be selected, repositioned, scaled or recolored in Blender or other DCC tools. Geometry not rigged; to animate movable parts set pivots and keyframes in Blender.
- No automatic multipart reconstruction is done by to3D; this is an original procedural approximation. The to3D interactive upload/generation interface is available separately in chat.

Suggested editing workflow in Blender:
File -> Import -> glTF 2.0 -> select the .glb
Select an object in Outliner -> Tab to Edit Mode, or use Object Mode to move/rotate or set materials.
For animated control surfaces move each object's origin to its hinge then keyframe rotation.
Modify Build_Editable_Cessna172.py to change source dimensions, paint and geometry, and rerun (requires numpy and trimesh).
