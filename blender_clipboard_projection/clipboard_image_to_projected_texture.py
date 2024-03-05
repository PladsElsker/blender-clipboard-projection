import bpy
import os
import asyncio

from .clipboard_ops import save_image_from_clipboard
from .async_file_ops import delete_unused_cbpr_texture_images
from .shortcuts import shortcut_manager
from .view_3d_camera_context import VIEW_3D_CameraContext
from .rigged_mesh_projection import is_rigged_with_armature, project_rigged_from_view_and_transfer_uvs


class ClipboardProjectionPanel(bpy.types.Panel):
    bl_label = "Clipboard Project"
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
    bl_label = "Project Clipboard on Faces"
    bl_idname = "wm.project_clipboard_on_selected"
    bl_options = {"REGISTER", "UNDO"}
    
    @classmethod
    def poll(cls, context):
        return cls._is_enabled(context)
    
    @classmethod
    def description(cls, context, properties):
        return cls._get_error_message(context)

    def execute(self, context):
        self._raise_if_invalid(context)

        obj = context.object

        image_location = save_image_from_clipboard(obj.clipboard_projection_textures_location)
        material = self._create_shared_texture_material(obj, image_location)
        material_index = next(index for index, slot in enumerate(obj.material_slots) if slot.material == material)
        bpy.context.object.active_material_index = material_index

        if is_rigged_with_armature(obj):
            project_rigged_from_view_and_transfer_uvs(obj)
        else:
            camera = [selected for selected in bpy.context.selected_objects if selected.type == "CAMERA"][0]
            with VIEW_3D_CameraContext(camera) as camera_context:
                override = {'area': camera_context.area, 'region': camera_context.region, 'edit_object': bpy.context.edit_object}
                bpy.ops.uv.project_from_view(override, camera_bounds=True, correct_aspect=True, scale_to_bounds=False)

        bpy.ops.object.material_slot_assign()
        
        loop = asyncio.get_event_loop()
        loop.create_task(delete_unused_cbpr_texture_images(os.path.dirname(image_location)))

        return {'FINISHED'}
    
    def _raise_if_invalid(self, context):
        if not OBJECT_OT_ProjectClipboardOnSelected._is_enabled(context):
            raise RuntimeError(OBJECT_OT_ProjectClipboardOnSelected._get_error_message(context))
    
        shared_node_tree = context.object.clipboard_projection_node_group
        if shared_node_tree:
            if not self._validate_node_tree(shared_node_tree):
                raise RuntimeError('The provided Node Tree is missing at least one input in ["Color", "Alpha"]')
    
    @classmethod
    def _is_enabled(cls, context):
        return (
            cls._is_textures_location_valid(context) and
            cls._is_edit_mode(context) and 
            cls._is_exactly_one_camera_selected(context)
        )
    
    @classmethod
    def _get_error_message(cls, context):
        if not cls._is_textures_location_valid(context):
            return "Texture Location path is invalid"
        elif not cls._is_edit_mode(context):
            return "Must be in Edit Mode to project clipboard"
        elif not cls._is_exactly_one_camera_selected(context):
            return "Exactly one camera must be selected"
        else:
            return "Project an image from the clipboard onto selected mesh faces"
    
    @classmethod
    def _is_textures_location_valid(cls, context):
        return os.path.isdir(bpy.path.abspath(context.object.clipboard_projection_textures_location))
    
    @classmethod
    def _is_edit_mode(cls, context):
        return (context.object is not None and
            context.object.type == 'MESH' and
            context.mode == 'EDIT_MESH')
    
    @classmethod
    def _is_exactly_one_camera_selected(cls, context):
        return len([obj for obj in bpy.context.selected_objects if obj.type == "CAMERA"]) == 1

    def _create_shared_texture_material(self, obj, image_location):
        material = bpy.data.materials.new(name=f"projected material {obj.name}")
        obj.data.materials.append(material)
        
        material.use_nodes = True
        nodes = material.node_tree.nodes
        links = material.node_tree.links
        nodes.clear()
        
        texture_node = nodes.new(type='ShaderNodeTexImage')
        texture_node.image = bpy.data.images.load(image_location)
        texture_node.location = (-300, 0)

        shared_node_tree = self._get_shared_node_tree(obj)

        shared_node = nodes.new('ShaderNodeGroup')
        shared_node.node_tree = shared_node_tree
        shared_node.location = (0, 0)

        links.new(texture_node.outputs['Color'], shared_node.inputs["Color"])
        links.new(texture_node.outputs['Alpha'], shared_node.inputs["Alpha"])

        return material

    def _get_shared_node_tree(self, obj):
        shared_node_tree = obj.clipboard_projection_node_group
        if shared_node_tree is not None:
            return shared_node_tree

        shared_node_tree = bpy.data.node_groups.new(f"projected shader {obj.name}", type="ShaderNodeTree")
        group_inputs = shared_node_tree.nodes.new('NodeGroupInput')
        group_inputs.location = (-400, 0)
        shared_node_tree.inputs.new('NodeSocketColor', 'Color')
        shared_node_tree.inputs.new('NodeSocketFloatFactor', 'Alpha')

        emission_node = shared_node_tree.nodes.new('ShaderNodeEmission')
        emission_node.location = (-200, 0)

        material_output_node = shared_node_tree.nodes.new('ShaderNodeOutputMaterial')
        material_output_node.location = (0, 0)

        shared_node_tree.links.new(group_inputs.outputs['Color'], emission_node.inputs['Color'])
        shared_node_tree.links.new(group_inputs.outputs['Alpha'], emission_node.inputs['Strength'])
        shared_node_tree.links.new(emission_node.outputs['Emission'], material_output_node.inputs['Surface'])

        obj.clipboard_projection_node_group = shared_node_tree
        return shared_node_tree

    def _validate_node_tree(self, node_tree):
        group_input_nodes = [node for node in node_tree.nodes if node.type == 'GROUP_INPUT']
        if not group_input_nodes:
            print("No Group Input node found.")
            return False

        group_input = group_input_nodes[0]
        if "Color" not in group_input.outputs or "Alpha" not in group_input.outputs:
            print("Group Input node does not have required 'Color' or 'Alpha' outputs.")
            return False

        return True


def register_project_clipboard_shortcut():
    shortcut_manager.register_shortcut(OBJECT_OT_ProjectClipboardOnSelected.bl_idname, type='V', value='PRESS', ctrl=True, shift=True)


def register():
    bpy.utils.register_class(ClipboardProjectionPanel)
    bpy.utils.register_class(OBJECT_OT_ProjectClipboardOnSelected)
    bpy.types.Object.clipboard_projection_textures_location = bpy.props.StringProperty(
        name="Textures Location",
        description="Saved textures location",
        default="",
        maxlen=1024,
        subtype='FILE_PATH',
    )
    bpy.types.Object.clipboard_projection_node_group = bpy.props.PointerProperty(
        name="Shared Shader Group",
        description="Select a shared shader",
        type=bpy.types.NodeTree,
    )
    register_project_clipboard_shortcut()


def unregister():
    bpy.utils.unregister_class(ClipboardProjectionPanel)
    bpy.utils.unregister_class(OBJECT_OT_ProjectClipboardOnSelected)
    del bpy.types.Object.clipboard_projection_textures_location
    del bpy.types.Object.clipboard_projection_node_group


if __name__ == "__main__":
    register()
