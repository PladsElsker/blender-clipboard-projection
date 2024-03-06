import bpy

from .view_3d_camera_context import VIEW_3D_CameraContext


def project_rigged_from_view_and_transfer_uvs(rigged):
    bpy.ops.object.mode_set(mode='OBJECT')

    selection_buffer = dict(
        selected=[obj for obj in bpy.context.selected_objects],
        active=bpy.context.active_object
    )

    bpy.ops.object.select_all(action='DESELECT')
    rigged.select_set(True)
    armature_modifiers = [modifier for modifier in rigged.modifiers if modifier.type == "ARMATURE" and modifier.object]
    for mods in armature_modifiers:
        mods.object.select_set(True)

    bpy.ops.object.duplicate_move()
    duplicated_objects = bpy.context.selected_objects

    for obj in duplicated_objects:
        if obj.type == 'MESH':
            for modifier in obj.modifiers:
                if modifier.type == 'ARMATURE':
                    bpy.context.view_layer.objects.active = obj
                    bpy.ops.object.modifier_apply(modifier=modifier.name)

    bpy.ops.object.mode_set(mode='EDIT')

    camera = [selected for selected in selection_buffer["selected"] if selected.type == "CAMERA"][0]
    with VIEW_3D_CameraContext(camera) as camera_context:
        override = {'area': camera_context.area, 'region': camera_context.region, 'edit_object': bpy.context.edit_object}
        bpy.ops.uv.project_from_view(override, camera_bounds=True, correct_aspect=True, scale_to_bounds=False)

    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')

    duplicated_mesh = [duplicated_mesh for duplicated_mesh in duplicated_objects if duplicated_mesh.type == "MESH"][0]
    rigged.select_set(True)
    duplicated_mesh.select_set(True)
    bpy.context.view_layer.objects.active = duplicated_mesh
    bpy.ops.object.join_uvs()

    bpy.ops.object.select_all(action='DESELECT')
    for duplicated in duplicated_objects:
        duplicated.select_set(True)
    
    bpy.ops.object.delete(use_global=False, confirm=False)

    for previous_selected in selection_buffer["selected"]:
        previous_selected.select_set(True)
    
    selection_buffer["active"].select_set(True)
    bpy.context.view_layer.objects.active = selection_buffer["active"]
    
    bpy.ops.object.mode_set(mode='EDIT')


def is_rigged_with_armature(obj):
    if obj.modifiers:
        for modifier in obj.modifiers:
            if modifier.type == 'ARMATURE' and modifier.object:
                return True

    return False
