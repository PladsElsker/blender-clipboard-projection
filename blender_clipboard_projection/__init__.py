bl_info = {
    "name": "Clipboard Rendering",
    "author": "Plads Elsker",
    "blender": (2, 80, 0),
    "category": "Camera",
}


from .asyncio_adapter import asyncio_adapter
from .shortcuts import shortcut_manager

from . import clipboard_image_to_projected_texture
from . import render_image_to_clipboard


def register():
    asyncio_adapter.start()
    clipboard_image_to_projected_texture.register()
    render_image_to_clipboard.register()


def unregister():
    asyncio_adapter.stop()
    shortcut_manager.unregister_shortcuts()
    clipboard_image_to_projected_texture.unregister()
    render_image_to_clipboard.unregister()


if __name__ == "__main__":
    register()
