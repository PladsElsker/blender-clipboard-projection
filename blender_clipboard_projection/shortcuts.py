import bpy


class BlenderShortcut:
    def __init__(self):
        self.added_keymaps = []

    def register_shortcut(self, bl_idname, **kwargs):
        wm = bpy.context.window_manager
        kc = wm.keyconfigs.addon
        if kc:
            km = kc.keymaps.get('Window')
            if not km:
                km = kc.keymaps.new(name='Window', space_type='EMPTY')
            
            kmi = km.keymap_items.new(bl_idname, **kwargs)
            self.added_keymaps.append((km, kmi))

    def unregister_shortcuts(self):
        for km, kmi in self.added_keymaps:
            km.keymap_items.remove(kmi)
        
        self.added_keymaps.clear()


shortcut_manager = BlenderShortcut()
