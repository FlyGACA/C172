# Run in Blender 4.x: blender --background --python FlyGACA_Blender_Enhance.py
import bpy, math, os
from mathutils import Vector
ROOT=os.path.dirname(os.path.abspath(__file__))
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=os.path.join(ROOT,"FlyGACA_C172_Classic_Analog_Phase2.glb"))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
def mat(name,rgba,metal,rough,transmission=0):
 m=bpy.data.materials.new(name);m.diffuse_color=rgba;m.use_nodes=True
 bs=m.node_tree.nodes.get("Principled BSDF")
 bs.inputs["Base Color"].default_value=rgba
 bs.inputs["Metallic"].default_value=metal
 bs.inputs["Roughness"].default_value=rough
 bs.inputs["Transmission Weight"].default_value=transmission
 return m
paint=mat("PBR • aircraft white enamel",(0.85,.89,.91,1),.38,.24)
metal=mat("PBR • brushed aluminum",(.53,.58,.62,1),.78,.28)
glass=mat("PBR • cockpit glass",(.15,.36,.48,1),.08,.12,.58)
rubber=mat("PBR • black rubber",(.025,.028,.03,1),0,.84)
dark=mat("PBR • dark instrument finish",(.035,.047,.058,1),.12,.62)
cream=mat("PBR • control surface paint",(.79,.82,.84,1),.25,.31)
red=mat("PBR • burgundy livery",(.55,.055,.075,1),.32,.24)
for o in meshes:
 n=o.name.lower()
 if any(w in n for w in ["glass","window","windscreen"]):m=glass
 elif any(w in n for w in ["wheel","tire","tyre"]):m=rubber
 elif any(w in n for w in ["metal","strut","hinge","fastener","spring","axle","cap","pitot","antenna","knob"]):m=metal
 elif any(w in n for w in ["stripe","burgundy"]):m=red
 elif any(w in n for w in ["instrument","radio","panel","breaker","switch","propeller blade"]):m=dark
 elif any(w in n for w in ["flap","aileron","elevator","rudder"]):m=cream
 else:m=paint
 o.data.materials.clear();o.data.materials.append(m)
 for poly in o.data.polygons:poly.use_smooth=True
 if hasattr(o.data,"set_sharp_from_angle"):pass
# mark control-surface pivots using a hierarchy of empties for interactive animation
controls=[("Flaps", "flap"),("Ailerons","aileron"),("Elevator","elevator"),("Rudder","rudder"),("Propeller","propeller blade")]
root=bpy.data.collections.new("FlyGACA • Animation Controls");bpy.context.scene.collection.children.link(root)
for label,key in controls:
 for side in ["left","right"] if key not in ("rudder","propeller blade") else ["all"]:
  members=[o for o in meshes if key in o.name.lower() and (side=="all" or side in o.name.lower())]
  if not members:continue
  pivot=bpy.data.objects.new(label+" • "+side+" • pivot",None);root.objects.link(pivot)
  bounds=[o.matrix_world @ Vector(corner) for o in members for corner in o.bound_box]
  centroid=sum(bounds,Vector())/len(bounds)
  pivot.location=centroid
  for o in members:
   world=o.matrix_world.copy();o.parent=pivot;o.matrix_world=world
# lighting and camera
world=bpy.context.scene.world
if world:world.color=(.23,.32,.42)
def area(name,loc,power,size):
 data=bpy.data.lights.new(name,'AREA');data.energy=power;data.shape='DISK';data.size=size
 obj=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(obj);obj.location=loc
 obj.rotation_euler=(Vector((0,0,0))-obj.location).to_track_quat('-Z','Y').to_euler()
area("Studio softbox", (4,-7,9),1700,8)
area("Rim light",(-7,4,6),1100,6)
cam_data=bpy.data.cameras.new("FlyGACA camera");cam=bpy.data.objects.new("FlyGACA camera",cam_data);bpy.context.collection.objects.link(cam)
cam.location=(10,-13,7);cam.rotation_euler=(Vector((0,0,.2))-cam.location).to_track_quat('-Z','Y').to_euler()
bpy.context.scene.camera=cam;cam_data.type='ORTHO';cam_data.ortho_scale=14
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=48
scene.render.resolution_x=1600;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
scene.render.filepath=os.path.join(ROOT,"FlyGACA_C172_Preview.png")
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT,"FlyGACA_C172_Editable.blend"))
bpy.ops.render.render(write_still=True)
print("Saved .blend and render")
