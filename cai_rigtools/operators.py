import bpy

from .armature import (
    get_armature,
    get_selected_bones,
    find_pose_bone,
    find_edit_bone,
    select_bones,
    create_lever_mechanism,
    create_target_armature,
    create_tail_mechanism,
    create_tentacle_mechanism,
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
        if not all(
            [
                self._find_selected_bones(),
            ]
        ):
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
    Clear all constraints from selected bones
    """

    bl_idname = "rigtools.bulk_set_deformation_bone"
    bl_label = "Turn all deformations on or off"
    bl_options = {"REGISTER", "UNDO"}

    use_deform: bpy.props.BoolProperty(
        name="Use Deform",
        default=True,
    )

    def execute(self, context):
        if not all(
            [
                self._find_selected_bones(),
            ]
        ):
            return {"CANCELLED"}

        for bone_name in self.selected_bones:
            bone = find_edit_bone(self.armature, bone_name)
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
        if not all(
            [
                self._find_selected_bones(),
            ]
        ):
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
        if not all(
            [
                self._find_armature(),
                self._find_selected_bones(),
            ]
        ):
            return {"CANCELLED"}

        created_bones = create_target_armature(self.armature, self.selected_bones)
        select_bones(self.armature, created_bones)
        self.report({"INFO"}, f"{len(created_bones)} bones had been or updated.")

        return {"FINISHED"}


class CreateBoneChainLeverMechanism(BaseOperator):
    """
    Create a lever mechanism for manipulation bone chains (spine)
    """

    bl_idname = "rigtools.create_chain_lever"
    bl_label = "Create bone lever rig"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        # TODO: Use Names only
        selected_bones = [o.name for o in bpy.context.selected_bones if o.select]

        if not selected_bones:
            self.report({"ERROR"}, "Cannot preform operation, no bones selected")
            return {"FINISHED"}

        armature = get_armature()
        created_bones = create_lever_mechanism(armature, selected_bones)
        select_bones(armature, created_bones)

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
        # TODO: Use Names only
        selected_bones = [o.name for o in bpy.context.selected_bones if o.select]

        if not selected_bones:
            self.report({"ERROR"}, "Cannot preform operation, no bones selected")
            return {"FINISHED"}

        armature = get_armature()
        created_bones = create_tail_mechanism(armature, selected_bones)
        select_bones(armature, created_bones)

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
        # TODO: Use Names only
        selected_bones = [o.name for o in bpy.context.selected_bones if o.select]

        if not selected_bones:
            self.report({"ERROR"}, "Cannot preform operation, no bones selected")
            return {"FINISHED"}

        armature = get_armature()
        created_bones = create_tentacle_mechanism(armature, selected_bones)
        select_bones(armature, created_bones)

        self.report({"INFO"}, f"{len(created_bones)} bones had been created or updated")

        return {"FINISHED"}
