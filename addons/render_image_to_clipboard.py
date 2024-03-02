bl_info = {
    "name": "Render Image To Clipboard",
    "author": "Plads Elsker",
    "blender": (2, 80, 0),
    "category": "Camera",
}


import bpy
from io import BytesIO

from PIL import Image
import platform


def get_render_image(camera_name="Camera"):
    initial_render_filepath = bpy.context.scene.render.filepath
    bpy.context.scene.render.filepath = "/tmp\\tmp.png"
    
    initial_camera = bpy.context.scene.camera
    camera = bpy.data.objects[camera_name]
    bpy.context.scene.camera = camera

    bpy.ops.render.render(write_still=True)
    
    rendered_image = Image.open(bpy.context.scene.render.filepath)
    
    # clean the state
    bpy.context.scene.render.filepath = initial_render_filepath
    bpy.context.scene.camera = initial_camera
    
    return rendered_image


def pil_to_clipboard_windows(img):
    with BytesIO() as buffer:
        img.convert("RGB").save(buffer, format="BMP")
        image_bytes = buffer.getvalue()[14:]
    
    import win32clipboard
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(win32clipboard.CF_DIB, image_bytes)
    win32clipboard.CloseClipboard()


def pil_to_clipboard_linux(img):
    with BytesIO() as output:
        img.save(output, format="PNG")
        image_bytes = output.getvalue()
    
    import subprocess
    process = subprocess.Popen(['xclip', '-selection', 'clipboard', '-t', 'image/png', '-i'], stdin=subprocess.PIPE)
    process.communicate(input=image_bytes)


def pil_to_clipboard(img):
    os_name = platform.system()
    if os_name == 'Windows':
        pil_to_clipboard_windows(img)
    elif os_name == 'Linux':
        pil_to_clipboard_linux(img)
    else:
        raise "OS not supported for clipboard operation"


class ClipboardRenderPanel(bpy.types.Panel):
    bl_label = "Clipboard Render"
    bl_idname = "OBJECT_PT_render_to_clipboard"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"
    bl_options = {"HEADER_LAYOUT_EXPAND"}

    @classmethod
    def poll(cls, context):
        # Check if there is an active object and if it's a camera
        return context.active_object is not None and context.active_object.type == 'CAMERA'

    def draw(self, _):
        self.layout.use_property_split = True
        self.layout.operator("wm.render_image_to_clipboard")


class OBJECT_OT_RenderToClipboard(bpy.types.Operator):
    bl_label = "Render Image to Clipboard"
    bl_idname = "wm.render_image_to_clipboard"
    
    @classmethod
    def description(cls, context, properties):
        return "Save the rendered camera view to the clipboard"

    def execute(self, context):
        active_object = context.active_object
        if active_object.type != 'CAMERA':
            raise "The active object is not a camera."

        camera_name = active_object.name
        image = get_render_image(camera_name)
        pil_to_clipboard(image)
        return {'FINISHED'}


def register():
    bpy.utils.register_class(ClipboardRenderPanel)
    bpy.utils.register_class(OBJECT_OT_RenderToClipboard)


def unregister():
    bpy.utils.unregister_class(ClipboardRenderPanel)
    bpy.utils.unregister_class(OBJECT_OT_RenderToClipboard)


if __name__ == "__main__":
    register()
