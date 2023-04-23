import bpy

from .armature import (
    get_armature,
    get_selected_bones,
    find_pose_bone,
    find_edit_bone,
    select_bones,
    assign_bone_layer_name,
    move_bones_to_layer,
    create_lever_mechanism,
    create_target_armature,
    create_tail_mechanism,
    create_tentacle_mechanism,
    create_unity_leg_helper,
)


class BaseOperator(bpy.types.Operator):
    def _find_armature(self):
        self.armature = get_armature()

        if self.armature is None:
            self.report({"ERROR_INVALID_INPUT"}, "Selected object is not an armature.")
            return False
        return True

    def _find_selected_bones(self):
        if not self._find_armature():
            return False

        self.selected_bones = get_selected_bones(self.armature)
        # self.selected_bone_names = [b.name for b in self.selected_bones]

        if not self.selected_bones:
            self.report({"ERROR_INVALID_INPUT"}, "No bones are selected.")
            return False

        return True


class ClearAllConstraints(BaseOperator):
    """
    Clear all constraints from selected bones
    """

    bl_idname = "rigtools.clear_constraints"
    bl_label = "Clear all constraints"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        if not self._find_selected_bones():
            return {"CANCELLED"}

        fail = 0

        for bone_name in self.selected_bones:
            pose_bone = find_pose_bone(self.armature, bone_name)
            if pose_bone:
                for constraint in pose_bone.constraints:
                    pose_bone.constraints.remove(constraint)
            else:
                fail += 1

        if not fail:
            self.report({"INFO"}, f"{len(self.selected_bones)} had been cleared.")
        else:
            self.report(
                {"WARNING"},
                f"{len(self.selected_bones - fail)} had been cleared. {fail} Bones could not be cleared",
            )

        return {"FINISHED"}


class BulkToggleDeformation(BaseOperator):
    """
    Toggle deformation of selected bones
    """

    bl_idname = "rigtools.bulk_set_deformation_bone"
    bl_label = "Toggle deformation of selected bones"
    bl_options = {"REGISTER", "UNDO"}

    use_deform: bpy.props.BoolProperty(
        name="Use Deform",
        default=True,
    )

    def execute(self, context):
        if not self._find_selected_bones():
            return {"CANCELLED"}

        for bone_name in self.selected_bones:
            bone = find_edit_bone(self.armature, bone_name)
            if bone:
                bone.use_deform = self.use_deform

        return {"FINISHED"}


class MirrorBones(BaseOperator):
    """
    Mirrors selected bones
    """

    bl_idname = "rigtools.mirror_bones"
    bl_label = "Mirror selected bones"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        if not self._find_selected_bones():
            return {"CANCELLED"}

        fail = 0

        _mirror_map = []

        for bone_name in self.selected_bones:
            bone = find_edit_bone(self.armature, bone_name)
            if bone:
                # Avoid modifying the same bone twice if mirroring is turned on
                # selection duplicates if any mirroring option was turned on
                bone_name_stripped = bone_name.replace(".L", "").replace(".R", "")
                if bone_name_stripped not in _mirror_map:
                    bone.tail = bone.head + (bone.tail - bone.head) * -1
                    _mirror_map.append(bone_name_stripped)
            else:
                fail += 1

        if not fail:
            self.report({"INFO"}, f"{len(self.selected_bones)} had been mirrored.")
        else:
            self.report(
                {"WARNING"},
                f"{len(self.selected_bones - fail)} had been mirrored. {fail} Bones failed.",
            )

        return {"FINISHED"}


class CreateTargetForArmature(BaseOperator):
    """
    Create a target armature for selected bones.
    """

    bl_idname = "rigtools.create_target"
    bl_label = "Create target rig"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        if not self._find_selected_bones():
            return {"CANCELLED"}

        # TODO: Prefix as property
        prefix = "TGT"

        try:
            created_bones = create_target_armature(
                self.armature, self.selected_bones, prefix
            )
            target_layer_id = assign_bone_layer_name(self.armature, prefix)
            move_bones_to_layer(self.armature, created_bones, target_layer_id)
            select_bones(self.armature, created_bones)
        except Exception as e:
            self.report({"ERROR"}, f"Failed to create target rig: {e}")
            return {"CANCELLED"}

        self.report(
            {"INFO"}, f"{len(created_bones)} bones had been created or updated."
        )

        return {"FINISHED"}


class CreateBoneChainLeverMechanism(BaseOperator):
    """
    Create a lever mechanism for manipulation bone chains (spine)
    """

    bl_idname = "rigtools.create_chain_lever"
    bl_label = "Create bone lever rig"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        if not self._find_selected_bones():
            return {"CANCELLED"}

        try:
            created_bones = create_lever_mechanism(self.armature, self.selected_bones)
            select_bones(self.armature, created_bones)
        except Exception as e:
            self.report({"ERROR"}, f"Failed to create bone lever rig: {e}")
            return {"CANCELLED"}

        self.report(
            {"INFO"}, f"{len(created_bones)} bones had been created or updated."
        )

        return {"FINISHED"}


class CreateTailChainMechanism(BaseOperator):
    """
    Create a lever mechanism for manipulating simple tails
    """

    bl_idname = "rigtools.create_tail"
    bl_label = "Create tail rig"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        if not self._find_selected_bones():
            return {"CANCELLED"}

        try:
            created_bones = create_tail_mechanism(self.armature, self.selected_bones)
            select_bones(self.armature, created_bones)
        except Exception as e:
            self.report({"ERROR"}, f"Failed to create tail rig: {e}")
            return {"CANCELLED"}

        self.report({"INFO"}, f"{len(created_bones)} bones had been created or updated")

        return {"FINISHED"}


class CreateTentacleChainMechanism(BaseOperator):
    """
    Create a lever mechanism for manipulating simple tails
    """

    bl_idname = "rigtools.create_tentacle"
    bl_label = "Create tentacle rig"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        if not self._find_selected_bones():
            return {"CANCELLED"}

        try:
            created_bones = create_tentacle_mechanism(
                self.armature, self.selected_bones
            )
            select_bones(self.armature, created_bones)
        except Exception as e:
            self.report({"ERROR"}, f"Failed to create tentacle rig: {e}")
            return {"CANCELLED"}

        self.report({"INFO"}, f"{len(created_bones)} bones had been created or updated")

        return {"FINISHED"}


class CreateUnityLegHelper(BaseOperator):
    """
    Create a helper for Unity's humanoid rig
    """

    bl_idname = "rigtools.create_unity_leg_helper"
    bl_label = "Create Unity leg helper"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        if not self._find_selected_bones():
            return {"CANCELLED"}

        try:
            created_bones = create_unity_leg_helper(self.armature, self.selected_bones)
            select_bones(self.armature, created_bones)
        except Exception as e:
            self.report({"ERROR"}, f"Failed to create Unity leg helper: {e}")
            return {"CANCELLED"}

        self.report({"INFO"}, f"{len(created_bones)} bones had been created or updated")

        return {"FINISHED"}
