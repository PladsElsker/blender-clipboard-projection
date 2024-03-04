import bpy


class VIEW_3D_CameraContext:
    def __init__(self, camera):
        self.camera = camera
        self.previous_camera = bpy.data.scenes["Scene"].camera
        self.area = self._get_first_VIEW_3D_area()
        self.view_3d_settings = self._get_3d_view_settings(self.area)
        self.region = self._get_first_WINDOW_region(self.area)
        self.rv3d = self._get_first_region_3d(self.area)

    def __enter__(self):
        bpy.data.scenes["Scene"].camera = self.camera
        self.rv3d.view_perspective = 'CAMERA'
        return self

    def __exit__(self, *args, **kwargs):
        bpy.data.scenes["Scene"].camera = self.previous_camera
        self._set_3d_view_settings(self.area, self.view_3d_settings)
    
    def _get_first_VIEW_3D_area(self):
        return next(area for area in bpy.context.screen.areas if area.type == 'VIEW_3D')
    
    def _get_first_WINDOW_region(self, area):
        return next(region for region in area.regions if region.type == 'WINDOW')
    
    def _get_first_region_3d(self, area):
        if len(area.spaces) == 0:
            raise RuntimeError("No spaces found in VIEW_3D, cannot perform action")

        return area.spaces[0].region_3d
    
    def _get_3d_view_settings(self, area):
        rv3d = self._get_first_region_3d(area)
        return {
            'view_location': rv3d.view_location.copy(),
            'view_rotation': rv3d.view_rotation.copy(),
            'view_distance': rv3d.view_distance,
            'view_perspective': rv3d.view_perspective
        }
    
    def _set_3d_view_settings(self, area, view_3d_settings):
        rv3d = self._get_first_region_3d(area)
        rv3d.view_location = view_3d_settings['view_location']
        rv3d.view_rotation = view_3d_settings['view_rotation']
        rv3d.view_distance = view_3d_settings['view_distance']
        rv3d.view_perspective = view_3d_settings['view_perspective']