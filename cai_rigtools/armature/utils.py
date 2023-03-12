from typing import List, Optional, Tuple
import uuid

import bpy
import mathutils

# TODO: Typing


def get_armature_objects():
    return [o for o in bpy.context.scene.objects if o.type == "ARMATURE"]


def get_armature(armature_name=None):
    if not armature_name and bpy.context.object.type == "ARMATURE":
        return bpy.context.object

    for obj in get_armature_objects():
        if obj.name == armature_name:
            return obj

    return None


def select_bones(armature, bone_names: List[str], clear_selection: bool = True):
    # if clear_selection:
    #     for bone in armature.data.bones:
    #         bone.select_set(state=0)

    # for bone_name in bone_names:
    #     bone = armature.data.bones[bone_name]
    #     bone.select_set(state=0)

    return


 ## TODO: add Warning if no bone found 

def find_edit_bone(armature, bone_name: str):
    return armature.data.edit_bones.get(bone_name, None)


def find_pose_bone(armature, bone_name: str):
    return armature.pose.bones.get(bone_name, None)


def new_bone(obj, bone_name: Optional[str] = None) -> str:
    """Adds a new bone to the given armature object.
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
    q: mathutils.Vector, r: mathutils.Vector, s: mathutils.Vector
) -> Tuple[mathutils.Vector, mathutils.Vector, mathutils.Vector]:
    normal = (r - q).cross(s - q).normalized()
    tangent = (s - r).normalized()
    bitangent = tangent.cross(normal)

    # TODO: Is the vector order right?
    return normal, tangent, bitangent
