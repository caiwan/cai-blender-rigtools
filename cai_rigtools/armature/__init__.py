from typing import List, Optional, Tuple
import uuid

import bpy
import mathutils

from .utils import (
    get_armature,
    select_bones,
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


def create_tentacle_mechanism(armature, selected_bones: List[str]) -> List[str]:
    pass
