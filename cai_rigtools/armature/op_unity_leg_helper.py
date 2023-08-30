from typing import List, Tuple

import bpy
from mathutils import Vector

from .utils import (
    find_edit_bone,
    find_pose_bone,
    create_or_update_bone,
    project_point_onto_plane,
)
from .tree_utils import find_bone_chain


def _helper_name(name: str, suffix: str = "helper") -> str:
    name_segments = name.split(".")
    return f"{name_segments[0]}.{suffix}.{'.'.join(name_segments[1:])}"


def create_unity_leg_helper(armature, selected_bones: List[str]) -> List[str]:
    """
    Create a helper for Unity's humanoid rig which support anthropomorphic digitigrade legs
    """

    # Find the bones and order them in hierarchy
    # It is only sufficient to select two bones, the first and the last
    chain = find_bone_chain(armature, selected_bones[0], selected_bones[-1])

    if not chain:
        raise RuntimeError(f"There is no direct path between the first and last bone")

    bones = list([find_edit_bone(armature, name) for name in chain])

    if len(bones) != 4 or any(bone is None for bone in bones):
        raise ValueError(f"Select exactly four bones")

    # If the armature was done right the bones should be in the correct order
    upper_leg, lower_leg, foot, toes = bones
    bpy.ops.object.mode_set(mode="EDIT")

    # Project all bone points onto the plane defined by the triangle of the upper and lower leg bones
    plane_points = (upper_leg.head, upper_leg.tail, lower_leg.tail)

    for bone in [upper_leg, lower_leg, foot, toes]:
        bone.head = project_point_onto_plane(bone.head, *plane_points)
        bone.tail = project_point_onto_plane(bone.tail, *plane_points)

    # Find the parallelogram for the helper bones
    # The upper leg bone (and its helper) has to be parallel with the foot bone

    # First we create a trapezoid from the upper leg bone and the foot bone
    upper_leg_direction = (upper_leg.tail - upper_leg.head).normalized()
    upper_helper_tail = upper_leg.tail + upper_leg_direction * foot.length

    # Adjust foot tail to be parallel with the upper leg bone
    foot.tail = foot.head + upper_leg_direction * foot.length
    
    # Crate a helper bones for upper leg, lower leg, foot and toes
    upper_helper_name = create_or_update_bone(armature, _helper_name(upper_leg.name))
    upper_helper = find_edit_bone(armature, upper_helper_name)
    upper_helper.head = upper_leg.head
    upper_helper.tail = upper_helper_tail

    lower_helper_name = create_or_update_bone(armature, _helper_name(lower_leg.name))
    lower_helper = find_edit_bone(armature, lower_helper_name)
    lower_helper.head = upper_helper_tail
    lower_helper.tail = foot.tail

    foot_helper_name = create_or_update_bone(armature, _helper_name(foot.name))
    foot_helper = find_edit_bone(armature, foot_helper_name)
    foot_helper.head = toes.head
    foot_helper.tail = toes.tail + 0.05 * (toes.tail - toes.head).normalized()

    # Parent the helper bones
    upper_helper.use_connect = upper_leg.use_connect
    upper_helper.parent = upper_leg.parent
    upper_helper.use_deform = False

    lower_helper.use_connect = False
    lower_helper.parent = upper_helper
    lower_helper.use_deform = False

    foot_helper.use_connect = True
    foot_helper.parent = lower_helper
    foot_helper.use_deform = False

    # Create constraints ---
    bpy.ops.object.mode_set(mode="POSE")

    pose_bones = list([find_pose_bone(armature, name) for name in chain])
    (
        pose_upper_leg,
        pose_lower_leg,
        pose_foot,
        pose_toes,
    ) = pose_bones

    upper_constraint = pose_upper_leg.constraints.new("COPY_ROTATION")
    upper_constraint.target = armature
    upper_constraint.subtarget = upper_helper_name

    lower_constraint = pose_lower_leg.constraints.new("COPY_ROTATION")
    lower_constraint.target = armature
    lower_constraint.subtarget = lower_helper_name

    foot_constraint = pose_foot.constraints.new("COPY_ROTATION")
    foot_constraint.target = armature
    foot_constraint.subtarget = upper_helper_name

    toe_constraint = pose_toes.constraints.new("CHILD_OF")
    toe_constraint.target = armature
    toe_constraint.subtarget = foot_helper_name

    bpy.ops.object.mode_set(mode="EDIT")

    return [
        upper_helper_name,
        lower_helper_name,
        foot_helper_name,
    ]
