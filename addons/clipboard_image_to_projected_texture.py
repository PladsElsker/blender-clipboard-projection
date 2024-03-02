bl_info = {
    "name": "Project Texture from Clipboard",
    "author": "Plads Elsker",
    "blender": (2, 80, 0),
    "category": "Camera",
}


import bpy
import os
from datetime import datetime
from PIL import ImageGrab


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
    
    @classmethod
    def poll(cls, context):
        return cls._is_enabled(context)
    
    @classmethod
    def description(cls, context, properties):
        return cls._get_error_message(context)

    def execute(self, context):
        self._raise_if_invalid(context)

        obj = context.object

        image_location = self._save_image_from_clipboard(obj)
        material = self._create_shared_texture_material(obj, image_location)
        
        view_3d_settings = self._get_3d_view_settings()
        rv3d = self._get_first_region_3d()
        camera = [selected for selected in bpy.context.selected_objects if selected.type == "CAMERA"][0]
        previous_camera = bpy.data.scenes["Scene"].camera
        bpy.data.scenes["Scene"].camera = camera
        rv3d.view_perspective = 'CAMERA'

        area = self._get_first_VIEW_3D_area()
        region = self._get_first_WINDOW_region(area=area)

        override = {'area': area, 'region': region, 'edit_object': bpy.context.edit_object}
        bpy.ops.uv.project_from_view(override, camera_bounds=True, correct_aspect=True, scale_to_bounds=False)

        bpy.data.scenes["Scene"].camera = previous_camera
        self._set_3d_view_settings(view_3d_settings)

        material_index = next(index for index, slot in enumerate(obj.material_slots) if slot.material == material)
        bpy.context.object.active_material_index = material_index
        bpy.ops.object.material_slot_assign()

        # save current 3D view
        # move 3D view to selected camera
        # use "Project from view" operator
        # restore previous 3D view
        
        # assign material to selected faces
        
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
    
    def _save_image_from_clipboard(self, obj):
        pil_image = ImageGrab.grabclipboard()
        filename = f"{datetime.now().strftime('%Y%m%d%H%M%S%f')[:-3]}.png"
        image_location = os.path.join(bpy.path.abspath(obj.clipboard_projection_textures_location), filename)
        pil_image.save(image_location)
        return image_location

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
        print([node.type for node in node_tree.nodes])
        group_input_nodes = [node for node in node_tree.nodes if node.type == 'GROUP_INPUT']
        if not group_input_nodes:
            print("No Group Input node found.")
            return False

        group_input = group_input_nodes[0]
        if "Color" not in group_input.outputs or "Alpha" not in group_input.outputs:
            print("Group Input node does not have required 'Color' or 'Alpha' outputs.")
            return False

        return True
    
    def _get_first_VIEW_3D_area(self):
        return next(area for area in bpy.context.screen.areas if area.type == 'VIEW_3D')
    
    def _get_first_WINDOW_region(self, area=None):
        if not area:
            area = self._get_first_VIEW_3D_area()
        
        return next(region for region in area.regions if region.type == 'WINDOW')
    
    def _get_first_region_3d(self):
        area = self._get_first_VIEW_3D_area()
        if len(area.spaces) == 0:
            raise RuntimeError("No spaces found in VIEW_3D, cannot perform action")

        return area.spaces[0].region_3d
    
    def _get_3d_view_settings(self):
        rv3d = self._get_first_region_3d()
        return {
            'view_location': rv3d.view_location.copy(),
            'view_rotation': rv3d.view_rotation.copy(),
            'view_distance': rv3d.view_distance,
            'view_perspective': rv3d.view_perspective
        }
    
    def _set_3d_view_settings(self, view_3d_settings):
        rv3d = self._get_first_region_3d()
        rv3d.view_location = view_3d_settings['view_location']
        rv3d.view_rotation = view_3d_settings['view_rotation']
        rv3d.view_distance = view_3d_settings['view_distance']
        rv3d.view_perspective = view_3d_settings['view_perspective']


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


def unregister():
    bpy.utils.unregister_class(ClipboardProjectionPanel)
    bpy.utils.unregister_class(OBJECT_OT_ProjectClipboardOnSelected)
    del bpy.types.Object.clipboard_projection_textures_location
    del bpy.types.Object.clipboard_projection_node_group


if __name__ == "__main__":
    register()
