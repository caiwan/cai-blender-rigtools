import bpy
from typing import List
from .utils import find_edit_bone, find_pose_bone, create_or_update_bone
from .tree_utils import find_bone_chain


def _helper_bone_name(bone_name: str, suffix: str = "helper") -> str:
    bone_name_segments = bone_name.split(".")
    return f"{bone_name_segments[0]}.{suffix}.{'.'.join(bone_name_segments[1:])}"


def create_unity_leg_helper(armature, selected_bones: List[str]) -> List[str]:
    """
    Create a helper for Unity's humanoid rig which support anthropomorphic digitigrade legs
    """

    bone_chain = find_bone_chain(armature, selected_bones[0], selected_bones[-1])

    if not bone_chain:
        raise RuntimeError(f"There is no direct path between the first and last bone")

    bones = list([find_edit_bone(armature, bone_name) for bone_name in bone_chain])

    if len(bones) != 4 or any(bone is None for bone in bones):
        raise ValueError("Select exactly four bones")

    bone_upper_leg, bone_lower_leg, bone_foot, bone_toes = bones

    foot_offset = bone_foot.tail - bone_foot.head
    toe_direction = (bone_toes.tail - bone_toes.head).normalized()

    # TODO: Fix Parallelogram mechanism
    # Foot and upper leg h as to be parallel to each other
    # bone_upper_leg || bone_foot
    # Lower leg and created helper bones has to be parallel to each other

    bpy.ops.object.mode_set(mode="EDIT")

    # Crate a helper bones for upper leg, lower leg, foot and toes
    bone_upper_helper_name = create_or_update_bone(
        armature, _helper_bone_name(bone_upper_leg.name)
    )
    bone_upper_helper = find_edit_bone(armature, bone_upper_helper_name)
    bone_upper_helper.head = bone_upper_leg.head
    bone_upper_helper.tail = bone_upper_leg.tail + foot_offset

    bone_lower_helper_name = create_or_update_bone(
        armature, _helper_bone_name(bone_lower_leg.name)
    )
    bone_lower_helper = find_edit_bone(armature, bone_lower_helper_name)
    bone_lower_helper.head = bone_lower_leg.head + foot_offset
    bone_lower_helper.tail = bone_lower_leg.tail + foot_offset

    bone_foot_helper_name = create_or_update_bone(
        armature, _helper_bone_name(bone_foot.name)
    )
    bone_foot_helper = find_edit_bone(armature, bone_foot_helper_name)
    bone_foot_helper.head = bone_toes.head
    bone_foot_helper.tail = bone_toes.tail + 0.05 * toe_direction

    # Parent the helper bones
    bone_upper_helper.use_connect = bone_upper_leg.use_connect
    bone_upper_helper.parent = bone_upper_leg.parent

    bone_lower_helper.use_connect = True
    bone_lower_helper.parent = bone_upper_helper

    bone_foot_helper.use_connect = True
    bone_foot_helper.parent = bone_lower_helper

    # TODO: Disable deform for these helper bones

    # TODO: Create constraints
    bpy.ops.object.mode_set(mode="POSE")

    pose_bones = list([find_pose_bone(armature, bone_name) for bone_name in bone_chain])
    pose_bone_upper_leg, pose_bone_lower_leg, pose_bone_foot, pose_bone_toes = pose_bones
        
    upper_bone_constraint = pose_bone_upper_leg.constraints.new("COPY_ROTATION")
    upper_bone_constraint.target = armature
    upper_bone_constraint.subtarget = bone_upper_helper_name

    lower_bone_constraint = pose_bone_lower_leg.constraints.new("COPY_ROTATION")
    lower_bone_constraint.target = armature
    lower_bone_constraint.subtarget = bone_lower_helper_name

    foot_bone_constraint = pose_bone_foot.constraints.new("COPY_ROTATION")
    foot_bone_constraint.target = armature
    foot_bone_constraint.subtarget = bone_upper_helper_name

    toe_bone_constraint = pose_bone_toes.constraints.new("CHILD_OF")
    toe_bone_constraint.target = armature
    toe_bone_constraint.subtarget = bone_foot_helper_name

    bpy.ops.object.mode_set(mode="EDIT")

    return [
        bone_upper_helper_name,
        bone_lower_helper_name,
        bone_foot_helper_name,
    ]
