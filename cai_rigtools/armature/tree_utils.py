from typing import List, Optional
import bpy

# TODO: Typing

def _find_root(armature, bone_name: str) -> str:
    # TODO: data.bones are not always up to date after the prev. operation
    bone = armature.data.bones[bone_name]
    # bone = armature.pose.bones[bone_name].bone
    while bone.parent:
        bone = bone.parent
    return bone.name


def _find_path(armature, root_bone_name: str, bone_name: str) -> List[str]:
    bone_chain = []

    def _find_path(
        current_bone_name: Optional[str], bone_name: str, chain: List[str]
    ) -> bool:
        if not current_bone_name:
            return False

        chain.append(current_bone_name)
        if current_bone_name == bone_name:
            return True

        bone = armature.data.bones[current_bone_name]

        if any([_find_path(child.name, bone_name, chain) for child in bone.children]):
            return True

        chain.pop()
        return False

    _find_path(root_bone_name, bone_name, bone_chain)

    return bone_chain


def find_bone_chain(armature, first_bone_name: str, second_bone_name: str) -> List[str]:
    # The root is the armature itself but there is no such thing as a true root node in the tree.
    root_bone_name = _find_root(armature, first_bone_name)
    if root_bone_name != _find_root(armature, second_bone_name):
        raise RuntimeError(
            f"Bones {first_bone_name} and {second_bone_name} are not part of the same parent chain"
        )

    first_path = _find_path(armature, root_bone_name, first_bone_name)
    second_path = _find_path(armature, root_bone_name, second_bone_name)

    # First bone has to be higher in the tree than the second one
    if len(first_path) > len(second_path):
        first_bone_name, second_bone_name = second_bone_name, first_bone_name
        first_path, second_path = second_path, first_path

    for index, (first, second) in enumerate(zip(first_path, second_path)):
        if first == second:
            first_path[index] = None
            second_path[index] = None

    bone_chain = [name for name in first_path + second_path if name is not None]
    bone_chain.insert(0, first_bone_name)

    return bone_chain
