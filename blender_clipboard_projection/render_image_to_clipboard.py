import bpy

from .clipboard_ops import pil_to_clipboard
from .shortcuts import shortcut_manager
from .render import get_render_image


class OBJECT_OT_RenderToClipboard(bpy.types.Operator):
    bl_label = "Render Image to Clipboard"
    bl_idname = "wm.render_image_to_clipboard"

    @classmethod
    def poll(cls, context):
        return cls._is_enabled(context)
    
    @classmethod
    def description(cls, context, properties):
        if cls._is_exactly_one_camera_selected(context):
            return "Render from the selected camera to the clipboard"
        else:
            return "Exactly one camera must be selected"

    def execute(self, context):
        camera = [selected for selected in bpy.context.selected_objects if selected.type == "CAMERA"][0]
        image = get_render_image(camera_name=camera.name)
        pil_to_clipboard(image)
        return {'FINISHED'}
    
    @classmethod
    def _is_enabled(cls, context):
        return cls._is_exactly_one_camera_selected(context)
    
    @classmethod
    def _is_exactly_one_camera_selected(cls, context):
        return len([obj for obj in bpy.context.selected_objects if obj.type == "CAMERA"]) == 1


def add_operator_to_render_menu(self, context):
    self.layout.operator(OBJECT_OT_RenderToClipboard.bl_idname, icon='RENDER_STILL')


def register_render_clipboard_shortcut():
    shortcut_manager.register_shortcut(OBJECT_OT_RenderToClipboard.bl_idname, type='C', value='PRESS', ctrl=True, shift=True)


def register():
    bpy.utils.register_class(OBJECT_OT_RenderToClipboard)
    bpy.types.TOPBAR_MT_render.prepend(add_operator_to_render_menu)
    register_render_clipboard_shortcut()


def unregister():
    bpy.utils.unregister_class(OBJECT_OT_RenderToClipboard)
    bpy.types.TOPBAR_MT_render.remove(add_operator_to_render_menu)


if __name__ == "__main__":
    register()
