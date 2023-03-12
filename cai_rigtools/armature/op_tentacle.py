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


def create_tentacle_mechanism(armature, selected_bones: List[str]) -> List[str]:
    # TODO: ... 
    pass
