# Character Studio - procedural humanoid base + armature
# Run in Blender 3.6+ / 4.x: Scripting > New > paste > Run Script.
import bpy
import math
from mathutils import Vector

# -------------------- SETTINGS --------------------
CHARACTER_NAME = "CharacterStudio_Humanoid"
CHARACTER_KIND = "monster"  # "human" or "monster"
HEIGHT = 2.4
# ---------------------------------------------------

def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (bpy.data.meshes, bpy.data.curves, bpy.data.armatures, bpy.data.materials):
        for block in list(datablocks):
            if block.users == 0:
                datablocks.remove(block)

def make_material(name, color, roughness=0.72, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*color, 1.0)
        bsdf.inputs["Roughness"].default_value = roughness
        bsdf.inputs["Metallic"].default_value = metallic
    return mat

def add_sphere(name, location, scale, material, segments=24, rings=16):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=rings, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(material)
    for poly in obj.data.polygons:
        poly.use_smooth = True
    return obj

def point_segment_distance(point, start, end):
    segment = end - start
    length_sq = segment.length_squared
    if length_sq < 1e-8:
        return (point - start).length
    t = max(0.0, min(1.0, (point - start).dot(segment) / length_sq))
    closest = start + t * segment
    return (point - closest).length

def build_character():
    clear_scene()
    scale = HEIGHT / 2.4
    skin = make_material("Skin_Worn", (0.34, 0.39, 0.32) if CHARACTER_KIND == "monster" else (0.62, 0.39, 0.29))
    dark = make_material("Clothing_Dark", (0.075, 0.085, 0.09))
    eyes = make_material("Eyes", (0.012, 0.009, 0.008), roughness=0.22)

    parts = []
    def part(name, loc, size, mat=skin):
        loc = (loc[0], loc[1], loc[2] * scale)
        size = (size[0] * scale, size[1] * scale, size[2] * scale)
        parts.append(add_sphere(name, loc, size, mat))

    # Core body
    part("Pelvis", (0, 0, 0.98), (0.22, 0.14, 0.20), dark)
    part("Abdomen", (0, 0, 1.28), (0.20, 0.13, 0.28))
    part("Chest", (0, 0, 1.62), (0.31, 0.17, 0.30), dark)
    part("Neck", (0, 0, 1.91), (0.085, 0.085, 0.13))
    part("Head", (0, 0, 2.14), (0.16, 0.15, 0.22))
    part("Jaw", (0, -0.045, 2.02), (0.115, 0.12, 0.075))

    # Arms and hands
    for side, sign in (("L", 1), ("R", -1)):
        part("Shoulder_" + side, (0.34*sign, 0, 1.70), (0.15, 0.15, 0.16))
        part("UpperArm_" + side, (0.49*sign, 0, 1.53), (0.105, 0.105, 0.24))
        part("Elbow_" + side, (0.63*sign, 0, 1.40), (0.09, 0.09, 0.10))
        part("Forearm_" + side, (0.75*sign, 0, 1.27), (0.085, 0.09, 0.19))
        part("Hand_" + side, (0.88*sign, -0.015, 1.12), (0.09, 0.055, 0.12))

    # Legs and feet
    for side, sign in (("L", 1), ("R", -1)):
        part("Thigh_" + side, (0.13*sign, 0, 0.72), (0.13, 0.13, 0.30), dark)
        part("Knee_" + side, (0.13*sign, 0, 0.48), (0.105, 0.11, 0.11))
        part("Shin_" + side, (0.13*sign, 0, 0.25), (0.085, 0.095, 0.24), dark)
        part("Foot_" + side, (0.13*sign, -0.09, 0.075), (0.105, 0.19, 0.075), dark)

    # Monster silhouette additions
    if CHARACTER_KIND == "monster":
        for side, sign in (("L", 1), ("R", -1)):
            part("Monster_Hip_" + side, (0.23*sign, 0, 1.0), (0.13, 0.14, 0.20), skin)
            part("Monster_Spine_" + side, (0.0, 0.15, 1.58), (0.045, 0.07, 0.22), skin)

    # Eyes face toward -Y
    part("Eye_L", (-0.065, -0.135, 2.18), (0.025, 0.018, 0.025), eyes)
    part("Eye_R", (0.065, -0.135, 2.18), (0.025, 0.018, 0.025), eyes)

    # Join all geometry into one mesh and place origin at world zero.
    bpy.ops.object.select_all(action="DESELECT")
    for obj in parts:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    mesh = bpy.context.object
    mesh.name = CHARACTER_NAME + "_Mesh"
    bpy.context.scene.cursor.location = (0, 0, 0)
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    # Create a standard humanoid armature.
    arm_data = bpy.data.armatures.new(CHARACTER_NAME + "_Rig")
    rig = bpy.data.objects.new(CHARACTER_NAME + "_Rig", arm_data)
    bpy.context.collection.objects.link(rig)
    bpy.context.view_layer.objects.active = rig
    rig.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")

    bone_defs = {
        "root": ((0,0,0.05), (0,0,0.98), None),
        "pelvis": ((0,0,0.98), (0,0,1.18), "root"),
        "spine": ((0,0,1.18), (0,0,1.52), "pelvis"),
        "chest": ((0,0,1.52), (0,0,1.78), "spine"),
        "neck": ((0,0,1.78), (0,0,1.98), "chest"),
        "head": ((0,0,1.98), (0,0,2.34), "neck"),
    }
    for side, sign in (("L",1), ("R",-1)):
        bone_defs["upper_arm."+side] = ((0.28*sign,0,1.72), (0.63*sign,0,1.40), "chest")
        bone_defs["forearm."+side] = ((0.63*sign,0,1.40), (0.86*sign,0,1.16), "upper_arm."+side)
        bone_defs["hand."+side] = ((0.86*sign,0,1.16), (0.94*sign,-0.02,1.08), "forearm."+side)
        bone_defs["thigh."+side] = ((0.13*sign,0,0.98), (0.13*sign,0,0.49), "pelvis")
        bone_defs["shin."+side] = ((0.13*sign,0,0.49), (0.13*sign,0,0.12), "thigh."+side)
        bone_defs["foot."+side] = ((0.13*sign,0,0.12), (0.13*sign,-0.20,0.06), "shin."+side)

    edit_bones = {}
    for name, (head, tail, parent) in bone_defs.items():
        bone = arm_data.edit_bones.new(name)
        bone.head = Vector(head) * scale
        bone.tail = Vector(tail) * scale
        edit_bones[name] = bone
    for name, (_, _, parent_name) in bone_defs.items():
        if parent_name:
            edit_bones[name].parent = edit_bones[parent_name]
    bpy.ops.object.mode_set(mode="OBJECT")
    rig.show_in_front = True
    arm_data.display_type = "OCTAHEDRAL"

    # Smooth proximity-based weights: nearest two bones share influence.
    groups = {name: mesh.vertex_groups.new(name=name) for name in bone_defs.keys()}
    segments = []
    for name, (head, tail, _) in bone_defs.items():
        segments.append((name, Vector(head)*scale, Vector(tail)*scale))
    for vertex in mesh.data.vertices:
        point = vertex.co
        distances = sorted(
            ((point_segment_distance(point, a, b), name) for name, a, b in segments),
            key=lambda item: item[0]
        )[:2]
        raw = [1.0 / max(d, 0.035)**2 for d, _ in distances]
        total = sum(raw)
        for (distance, name), weight in zip(distances, raw):
            groups[name].add([vertex.index], weight/total, "REPLACE")

    modifier = mesh.modifiers.new("Character_Rig", "ARMATURE")
    modifier.object = rig
    mesh.parent = rig

    # Organize objects and set a useful camera-free viewport.
    collection = bpy.data.collections.new("CHARACTER_STUDIO")
    bpy.context.scene.collection.children.link(collection)
    for obj in (mesh, rig):
        for old_collection in list(obj.users_collection):
            old_collection.objects.unlink(obj)
        collection.objects.link(obj)

    bpy.ops.object.select_all(action="DESELECT")
    mesh.select_set(True)
    rig.select_set(True)
    bpy.context.view_layer.objects.active = rig
    bpy.context.scene.unit_settings.system = "METRIC"
    print("Character Studio: base character and humanoid rig created.")
    print("Next: refine topology, sculpt details, UV unwrap, texture, and test deformations.")

if __name__ == "__main__":
    build_character()
