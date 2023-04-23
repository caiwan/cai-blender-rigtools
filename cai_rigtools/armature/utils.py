from typing import List, Optional, Tuple
import uuid

import bpy
import mathutils

# TODO: Typing


def get_armature_objects():
    return [o for o in bpy.context.scene.objects if o.type == "ARMATURE"]


# TODO: This si not an armature but the currently selected object.
def get_armature(armature_name=None):
    armature_obj = bpy.context.view_layer.objects.active
    if not armature_name and armature_obj.type == "ARMATURE":
        return armature_obj

    for obj in get_armature_objects():
        if obj.name == armature_name:
            return obj

    return None


def get_selected_bones(armature_obj) -> List[str]:
    return [bone.name for bone in armature_obj.data.bones if bone.select] or [
        bone.name for bone in armature_obj.data.edit_bones if bone.select 
    ]


def select_bones(armature, bone_names: List[str], clear_selection: bool = True):
    # bpy.ops.object.mode_set(mode='EDIT') # Should be in edit mode already

    if clear_selection:
        bpy.ops.armature.select_all(action="DESELECT")

    for bone_name in bone_names:
        bone = armature.data.bones.get(bone_name)
        if bone:
            bone.select = True

    bpy.context.view_layer.update()


## TODO: add Warning if no bone found


def find_edit_bone(armature, bone_name: str):
    return armature.data.edit_bones.get(bone_name, None)


def find_pose_bone(armature, bone_name: str):
    return armature.pose.bones.get(bone_name, None)


def new_bone(obj, bone_name: Optional[str] = None) -> str:
    """
    Adds a new bone to the given armature object.
    Returns the resulting bone's name.
    """
    bone_name = bone_name or str(uuid.uuid4())

    if obj == bpy.context.active_object and bpy.context.mode == "EDIT_ARMATURE":
        edit_bone = obj.data.edit_bones.new(bone_name)
        name = edit_bone.name
        edit_bone.head = (0, 0, 0)
        edit_bone.tail = (0, 1, 0)
        edit_bone.roll = 0
        return name
    else:
        raise RuntimeError("Can't add new bone '%s' outside of edit mode" % bone_name)


create_or_update_bone = new_bone


def find_axis_vectors(
    q: mathutils.Vector,
    r: mathutils.Vector,
    s: mathutils.Vector,
) -> Tuple[mathutils.Vector, mathutils.Vector, mathutils.Vector]:
    """
    Finds the three major axis from three arbitrary vectors
    """
    normal = (r - q).cross(s - q).normalized()
    tangent = (s - r).normalized()
    bitangent = tangent.cross(normal)

    return normal, tangent, bitangent


def move_bones_to_layer(armature, bones: List[str], layer_num: int):
    """
    Moves given bones to a specified layer
    """
    for bone_name in bones:
        # TODO: Based on the context get edit mode or pose mode bones: 
        # if context.mode == 'EDIT_ARMATURE' ... 
        bone = find_edit_bone(armature, bone_name)
        bone.layers = [i == layer_num for i in range(len(bone.layers))]

    bpy.context.view_layer.update()


def assign_bone_layer_name(armature, layer_name: str) -> int:
    """
    Finds the first available bone layer of the given armature and assigns
    the given name to it. If a layer is already activated without bones assigned,
    reuses that layer instead. Returns the index of the layer.
    """
    for i in range(len(armature.data.layers)):
        if not armature.data.layers[i]:
            armature.data.layers[i] = True
            bpy.context.view_layer.update()
            armature.data[f"layer_name_{i}"] = layer_name
            return i
        elif not any(bone.layers[i : i + 4] for bone in armature.data.bones):
            armature.data[f"layer_name_{i}"] = layer_name
            return i
    return None
