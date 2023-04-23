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

from .op_target import create_target_armature

from .tree_utils import (
    find_bone_chain,
)

# TODO: Separate these to individual files as well


def create_lever_mechanism(armature, selected_bones: List[str]) -> List[str]:
    bone_chain = find_bone_chain(armature, selected_bones[0], selected_bones[-1])

    if not bone_chain:
        raise RuntimeError(f"There is no direct path between the first and last bone")

    first_bone = find_edit_bone(armature, bone_chain[0])

    last_bone = find_edit_bone(armature, bone_chain[-1])

    # create lever control
    control_bone_name = create_or_update_bone(armature, f"CTRL-ROOT-{first_bone.name}")
    control_bone = find_edit_bone(armature, control_bone_name)
    control_bone.head = first_bone.tail
    # TODO: Must align this bone to a [closest] major axis of world coordinates
    axis_vectors = find_axis_vectors(first_bone.tail, first_bone.head, last_bone.tail)
    control_bone.tail = axis_vectors[2] + first_bone.tail  # TODO: Adjust length

    # create lever bottom - This controls the hips
    bottom_bone_name = create_or_update_bone(armature, f"CTRL-PIVOT-{first_bone.name}")
    bottom_bone = find_edit_bone(armature, bottom_bone_name)
    bottom_bone.head = first_bone.tail
    bottom_bone.tail = first_bone.head

    # create lever top - This controls the spine rotation
    top_bone_name = create_or_update_bone(armature, f"CTRL-PIVOT-{last_bone.name}")
    top_bone = find_edit_bone(armature, top_bone_name)
    top_bone.head = first_bone.tail
    top_bone.tail = last_bone.tail

    # parenting
    top_bone.use_connect = False
    top_bone.parent = control_bone

    bottom_bone.use_connect = False
    bottom_bone.parent = control_bone

    first_bone.use_connect = False
    first_bone.parent = bottom_bone

    second_bone = find_edit_bone(armature, bone_chain[1])
    second_bone.use_connect = False
    second_bone.parent = control_bone

    # constraints
    bpy.ops.object.mode_set(mode="POSE")

    for bone_name in bone_chain[1:]:
        bone = find_pose_bone(armature, bone_name)
        constraint = bone.constraints.new("COPY_ROTATION")
        constraint.target = armature
        constraint.subtarget = top_bone_name
        constraint.target_space = "LOCAL"
        constraint.owner_space = "LOCAL"

    bpy.ops.object.mode_set(mode="EDIT")

    return [top_bone_name, bottom_bone_name, control_bone_name]
