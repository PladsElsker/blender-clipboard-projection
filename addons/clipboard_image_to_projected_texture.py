bl_info = {
    "name": "Project Texture from Clipboard",
    "author": "Plads Elsker",
    "blender": (2, 80, 0),
    "category": "Camera",
}


import bpy


class ClipboardProjectionPanel(bpy.types.Panel):
    bl_label = "Clipboard Projection"
    bl_idname = "OBJECT_PT_project_clipboard_on_object"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "material"
    bl_options = {"HEADER_LAYOUT_EXPAND"}

    def draw(self, context):
        obj = context.object
        self.layout.use_property_split = True
        self.layout.prop(obj, "clipboard_projection_textures_location", text="Textures Location")
        self.layout.prop(obj, "clipboard_projection_node_group", text="Node Group")
        self.layout.operator("wm.project_clipboard_on_selected")


class OBJECT_OT_ProjectClipboardOnSelected(bpy.types.Operator):
    bl_label = "Project Clipboard on Selected"
    bl_idname = "wm.project_clipboard_on_selected"
    
    @classmethod
    def _is_edit_mode(cls, context):
        return (context.object is not None and
            context.object.type == 'MESH' and
            context.mode == 'EDIT_MESH')
    
    @classmethod
    def _is_exactly_one_camera_selected(cls, context):
        return len([obj for obj in bpy.context.selected_objects if obj.type == "CAMERA"]) == 1
    
    @classmethod
    def _is_enabled(cls, context):
        return cls._is_edit_mode(context) and cls._is_exactly_one_camera_selected(context)
    
    @classmethod
    def poll(cls, context):
        return cls._is_enabled(context)
    
    @classmethod
    def description(cls, context, properties):
        if not cls._is_edit_mode(context):
            return "Must be in Edit Mode to project clipboard"
        elif not cls._is_exactly_one_camera_selected(context):
            return "Exactly one camera must be selected"
        else:
            return "Project an image from the clipboard onto selected mesh faces"

    def execute(self, context):
        # validate that only one camera is selected
        # get selected vertices
        # create material
        # setup uvs
        # etc.
        return {'FINISHED'}

def update_node_group(self, context):
    print("Node group changed to:", self.my_node_group)

def update_file_path(self, context):
    print("File path changed to:", self.my_file_path)


def register():
    bpy.utils.register_class(ClipboardProjectionPanel)
    bpy.utils.register_class(OBJECT_OT_ProjectClipboardOnSelected)
    bpy.types.Object.clipboard_projection_textures_location = bpy.props.StringProperty(
        name="Textures Location",
        description="Saved textures location",
        default="",
        maxlen=1024,
        subtype='FILE_PATH',
        update=update_file_path
    )
    bpy.types.Object.clipboard_projection_node_group = bpy.props.PointerProperty(
        name="Node Group",
        description="Select a node group",
        type=bpy.types.NodeTree,
        update=update_node_group
    )


def unregister():
    bpy.utils.unregister_class(ClipboardProjectionPanel)
    bpy.utils.unregister_class(OBJECT_OT_ProjectClipboardOnSelected)
    del bpy.types.Object.clipboard_projection_textures_location
    del bpy.types.Object.clipboard_projection_node_group


if __name__ == "__main__":
    register()
