from typing import List, Optional, Tuple
import uuid

import bpy
import mathutils

from .utils import (
    get_armature,
    select_bones,
    get_selected_bones,
    find_pose_bone,
    find_edit_bone,
    create_or_update_bone,
    find_axis_vectors,
)

from .tree_utils import (
    find_bone_chain,
)

# TODO: Separate these to individual files as well


# TODO: Add typing
def _check_target_bones(armature, selected_bones: List[str]) -> List[str]:
    # TODO: check already created bones
    # Check target name
    # check parent
    # Check parenting type
    # 1/ IF all checks -> OK
    # 2/ If bone exists -> Remove bone

    return selected_bones


# def _assign_all_properties(target, source):
#     # TODO: This does not work
#     for key, value in source.items():
#         print(target, source, key, value)
#         setattr(target, key, value)


# TODO: Add typing
def create_target_armature(armature, selected_bones: List[str]) -> List[str]:
    selected_bones = _check_target_bones(armature, selected_bones)

    bpy.ops.object.mode_set(mode="EDIT")

    bone_map = {}
    # TODO:  Use names for selected bones
    for bone_name in selected_bones:
        bone = find_edit_bone(armature, bone_name)
        target_bone_name = create_or_update_bone(armature, f"TGT-{bone_name}")
        target_bone = find_edit_bone(armature, target_bone_name)

        # TODO: proper copy bone
        # _assign_all_properties(target_bone, bone)

        target_bone.head = bone.head
        target_bone.tail = bone.tail
        target_bone.roll = bone.roll
        # TODO: Rest of the properties

        bone.use_deform = False

        bone_map[bone.name] = target_bone_name

    for bone_name, target_bone_name in bone_map.items():
        bone = find_edit_bone(armature, bone_name)
        target_bone = find_edit_bone(armature, target_bone_name)

        # Connect parents
        if bone.parent and bone.parent.name in bone_map:
            print(f"Parenting {target_bone_name}: {bone.name} -> {bone.parent.name}")
            target_bone_parent = find_edit_bone(armature, bone_map[bone.parent.name])
            target_bone.parent = target_bone_parent

            # Copy connection type
            target_bone.use_connect = bone.use_connect
            target_bone.use_deform = bone.use_deform

    bpy.ops.object.mode_set(mode="POSE")

    for bone_name, target_bone_name in bone_map.items():
        # TODO: Find updates here

        bone = find_pose_bone(armature, bone_name)
        constraint = bone.constraints.new("COPY_TRANSFORMS")
        constraint.target = armature
        constraint.subtarget = target_bone_name

    bpy.ops.object.mode_set(mode="EDIT")

    return [n for n in bone_map.keys()]