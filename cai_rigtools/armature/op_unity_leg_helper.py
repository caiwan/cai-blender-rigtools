from typing import List
from .utils import find_edit_bone, create_or_update_bone


def _helper_bone_name(bone_name: str, suffix: str = "helper") -> str:
    bone_name_segments = bone_name.split(".")
    return f"{bone_name_segments[0]}.{suffix}.{'.'.join(bone_name_segments[1:])}"


def create_unity_leg_helper(armature, selected_bones: List[str]) -> List[str]:
    """
    Create a helper for Unity's humanoid rig which support anthropomorphic digitigrade legs
    """

    bones = list(
        [find_edit_bone(armature, bone_name) for bone_name in selected_bones[:4]]
    )

    if len(bones) != 4 or any(bone is None for bone in bones):
        raise ValueError("Select exactly four bones")

    bone_upper_leg, bone_lower_leg, bone_foot, bone_toes = bones

    foot_direction = bone_foot.tail - bone_foot.head

    # TODO: Fix Parallelogram mechanism
    # Foot and upper leg h as to be parallel to each other
    # bone_upper_leg || bone_foot
    # Lower leg and created helper bones has to be parallel to each other

    # Crate a helper bones for upper leg, lower leg, foot and toes
    bone_upper_helper_name = create_or_update_bone(
        armature, _helper_bone_name(bone_upper_leg.name)
    )
    bone_upper_helper = find_edit_bone(armature, bone_upper_helper_name)
    bone_upper_helper.head = bone_upper_leg.head
    bone_upper_helper.tail = bone_upper_leg.tail + foot_direction

    bone_lower_helper_name = create_or_update_bone(
        armature, _helper_bone_name(bone_lower_leg.name)
    )
    bone_lower_helper = find_edit_bone(armature, bone_lower_helper_name)
    bone_lower_helper.head = bone_lower_leg.head + foot_direction
    bone_lower_helper.tail = bone_lower_leg.tail + foot_direction

    bone_foot_helper_name = create_or_update_bone(
        armature, _helper_bone_name(bone_foot.name)
    )
    bone_foot_helper = find_edit_bone(armature, bone_foot_helper_name)
    bone_foot_helper.head = bone_toes.head
    bone_foot_helper.tail = bone_toes.tail

    # Parent the helper bones
    bone_upper_helper.use_connect = bone_upper_leg.use_connect
    bone_upper_helper.parent = bone_upper_leg.parent

    bone_lower_helper.use_connect = True
    bone_lower_helper.parent = bone_upper_helper

    bone_foot_helper.use_connect = True
    bone_foot_helper.parent = bone_lower_helper

    return [bone_upper_helper_name, bone_lower_helper_name, bone_foot_helper_name]
