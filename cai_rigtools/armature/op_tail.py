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


def create_tail_mechanism(armature, selected_bones: List[str]) -> List[str]:
    bone_pairs = []

    bone_chain = find_bone_chain(armature, selected_bones[0], selected_bones[-1])

    if not bone_chain:
        raise RuntimeError(f"There is no direct path between the first and last bone")

    for bone_name in bone_chain:
        # 1/ Disconnect (all) bones
        bone = find_edit_bone(armature, bone_name)
        bone.use_connect = False

        # 2/ Create a control bone for each target bone
        control_bone_name = create_or_update_bone(armature, f"CTRL-{bone_name}")
        bone_pairs.append(
            (bone_name, control_bone_name)
        )  # TODO: Dataclass for better maintainability?

        control_bone = find_edit_bone(armature, control_bone_name)
        control_bone.head = bone.head
        control_bone.tail = (bone.head + bone.tail) * 0.5

    # 2/b Create one extra bone at the end of the last one
    def _find_next_ctrl_pos(
        head: mathutils.Vector, tail: mathutils.Vector
    ) -> Tuple[mathutils.Vector, mathutils.Vector]:
        d = tail - head
        l = d.length
        d.normalize()
        return (tail, tail + l * d * 0.5)

    last_control_bone_name = create_or_update_bone(
        armature, f"CTRL-{bone_chain[-1]}"
    )  # Blender must increase the numbering

    last_bone = find_edit_bone(armature, bone_chain[-1])
    last_control_bone = find_edit_bone(armature, last_control_bone_name)
    last_control_bone.head, last_control_bone.tail = _find_next_ctrl_pos(
        last_bone.head, last_bone.tail
    )

    bone_pairs.append((None, last_control_bone_name))

    # 3/ reparent bones
    # 3/a Control -> Next control
    for i in range(len(bone_pairs) - 1):
        control_bone = find_edit_bone(armature, bone_pairs[i][1])
        next_control_bone = find_edit_bone(armature, bone_pairs[i + 1][1])
        next_control_bone.parent = control_bone

    # 3/b Control -> Target
    for target_bone_name, control_bone_name in bone_pairs:
        if target_bone_name is not None:
            target_bone = find_edit_bone(armature, target_bone_name)
            control_bone = find_edit_bone(armature, control_bone_name)
            target_bone.parent = control_bone

    # 4/ Add damped track from next ctrl to prev target
    bpy.ops.object.mode_set(mode="POSE")
    for i in range(len(bone_pairs) - 1):
        target_bone_name = bone_pairs[i][0]
        if target_bone_name is not None:
            target_bone = find_pose_bone(armature, target_bone_name)
            next_control_bone_name = bone_pairs[i + 1][1]

            constraint = target_bone.constraints.new("COPY_ROTATION")
            constraint.target = armature
            constraint.subtarget = next_control_bone_name

            constraint = target_bone.constraints.new("DAMPED_TRACK")
            constraint.target = armature
            constraint.subtarget = next_control_bone_name

            # There is an untold trick behind this one
            constraint = target_bone.constraints.new("STRETCH_TO")
            constraint.target = armature
            constraint.subtarget = next_control_bone_name
            constraint.enabled = False

    bpy.ops.object.mode_set(mode="EDIT")

    return [name for pairs in bone_pairs for name in pairs if name is not None]
