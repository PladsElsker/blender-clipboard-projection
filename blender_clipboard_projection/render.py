import bpy

from PIL import Image


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
