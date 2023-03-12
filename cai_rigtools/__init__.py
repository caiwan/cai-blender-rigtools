bl_info = {
    "name": "Caiwans Rig Tools",
    "description": "Set of actions which helps building custom rigs (hopefully) faster.",
    "author": "Caiwan",
    "version": (1, 0),
    "blender": (3, 0, 0),
    "category": "Rigging",
}

from .operators import (
    CreateTargetForArmature,
    MirrorBones,
    ClearAllConstraints,
    CreateBoneChainLeverMechanism,
    CreateTailChainMechanism,
    CreateTentacleChainMechanism,
    BulkToggleDeformation,
)

# ------ Menu

import bpy


class MY_MT_RigToolArmatureMenu(bpy.types.Menu):
    bl_idname = "VIEW3D_MT_rig_tools_armature"
    bl_label = "Rig Tools"

    def draw(self, context):
        for clazz in [
            CreateTargetForArmature,
            BulkToggleDeformation,
            None,
            CreateBoneChainLeverMechanism,
            CreateTailChainMechanism,
            CreateTentacleChainMechanism,
            None,
            MirrorBones,
        ]:
            if clazz is None:
                self.layout.separator()
            else:
                self.layout.operator(clazz.bl_idname, text=clazz.bl_label)
        # self.layout.separator()


class MY_MT_RigToolPoseMenu(bpy.types.Menu):
    bl_idname = "VIEW3D_MT_rig_tools_pose"
    bl_label = "Rig Tools"

    def draw(self, context):
        for clazz in [
            ClearAllConstraints,
            BulkToggleDeformation,
        ]:
            if clazz is None:
                self.layout.separator()
            else:
                self.layout.operator(clazz.bl_idname, text=clazz.bl_label)
        # self.layout.separator()


def draw_armature_menu(self, context):
    self.layout.separator()
    self.layout.menu(MY_MT_RigToolArmatureMenu.bl_idname)


def draw_pose_menu(self, context):
    self.layout.separator()
    self.layout.menu(MY_MT_RigToolPoseMenu.bl_idname)


# ----- Bootstrap

classes = [
    MY_MT_RigToolArmatureMenu,
    MY_MT_RigToolPoseMenu,
    CreateTargetForArmature,
    ClearAllConstraints,
    MirrorBones,
    CreateBoneChainLeverMechanism,
    CreateTailChainMechanism,
    CreateTentacleChainMechanism,
    BulkToggleDeformation,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.VIEW3D_MT_edit_armature.append(draw_armature_menu)
    bpy.types.VIEW3D_MT_pose.append(draw_pose_menu)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    bpy.types.VIEW3D_MT_edit_armature.remove(draw_armature_menu)
    bpy.types.VIEW3D_MT_pose.remove(draw_pose_menu)


if __name__ == "__main__":
    register()
